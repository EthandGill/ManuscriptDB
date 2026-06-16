#!/usr/bin/env python3
"""
epigraphy_translate.py — add faithful English translations to the EDH/LIST
inscriptions in static/epigraphy_data.js.  NO Firecrawl credits, fully offline.

This is the epigraphy analogue of build_from_sweep.py: a two-phase
scaffold/assemble loop with a safety-checked write, so the model never edits the
2.1 MB data file by hand. The data already lives on disk (edh_ingest.py produced
it); this script only adds a `translation` field per record.

  1) SCAFFOLD — pull the next batch of UN-translated inscriptions:
       python epigraphy_translate.py scaffold --batch 150
     Writes _epi_translate_<NNN>.txt with one block per inscription: the original
     Latin (readable) under [LATIN] and a blank [ENGLISH] section to fill.
     Resumable: records that already have a non-empty `translation` are skipped,
     so re-running just hands you the next un-done batch.

  2) (Claude fills the scaffold) — under each [ENGLISH], type a faithful English
     translation of the Latin shown (expand the standard epigraphic abbreviations
     — D(is) M(anibus) -> "To the Spirits of the Dead", v(ixit) a(nnos) -> "lived
     N years", etc.). Free prose, one or more lines. Leave [ENGLISH] blank to skip
     a record (it stays un-done and reappears in the next scaffold).

  3) ASSEMBLE — safety-checked merge back into the data file:
       python epigraphy_translate.py assemble _epi_translate_<NNN>.txt
     For every block it requires (a) the id still exists in epigraphy_data.js and
     (b) the English is non-empty, then sets record["translation"]. It backs up
     epigraphy_data.js -> .bak first and prints built/skipped/error counts. Any
     unknown id or empty translation is reported and that record is left untouched.

Schema-tolerant: works whether `text` is a string (current edh_ingest output) or
a list of lines (post Phase-1), and whether the title field is `title` or `name`.
"""

import os, re, sys, json, argparse, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "static", "epigraphy_data.js")
REC_SEP = "=== "
PREFIX = "window.EPIGRAPHY_DATA = "


# ── data file I/O ───────────────────────────────────────────────────────────
def load_data():
    """Return (records, header). Strips the `window.EPIGRAPHY_DATA = ` wrapper and
    parses the whole remainder — robust to `]` inside array-valued fields like
    `text`. Raises a clear error if the file is mid-write (e.g. the ingester is
    regenerating it in another terminal)."""
    raw = open(DATA, encoding="utf-8").read()
    if PREFIX not in raw:
        raise SystemExit(f"{DATA}: no '{PREFIX.strip()}' wrapper found.")
    cut = raw.index(PREFIX)
    header = raw[:cut]
    payload = raw[cut + len(PREFIX):].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    try:
        return json.loads(payload), header
    except json.JSONDecodeError as e:
        raise SystemExit(
            f"{DATA} did not parse ({e}). It may be mid-write by edh_ingest.py "
            "in another terminal — wait for that to finish and re-run.")


def write_data(records, header):
    shutil.copyfile(DATA, DATA + ".bak")
    body = json.dumps(records, ensure_ascii=False)
    open(DATA, "w", encoding="utf-8").write(f"{header}{PREFIX}{body};\n")


def text_lines(rec):
    t = rec.get("text")
    if isinstance(t, list):
        return [str(x) for x in t if str(x).strip()]
    return [ln for ln in re.split(r"\r?\n", str(t or "")) if ln.strip()]


def has_translation(rec):
    tr = rec.get("translation")
    if isinstance(tr, list):
        return any(str(x).strip() for x in tr)
    return bool(str(tr or "").strip())


def title_of(rec):
    return rec.get("title") or rec.get("name") or rec.get("id") or "?"


# ── SCAFFOLD ────────────────────────────────────────────────────────────────
def do_scaffold(batch, start):
    records, _ = load_data()
    todo = [r for r in records if text_lines(r) and not has_translation(r)]
    chunk = todo[start:start + batch]
    if not chunk:
        print(f"Nothing to do: {len(todo)} untranslated remain, "
              f"start={start} is past the end.")
        return

    # number the output file after how many are already done
    done = sum(1 for r in records if has_translation(r))
    tag = f"{done + start:05d}"
    out_path = os.path.join(HERE, f"_epi_translate_{tag}.txt")

    blocks = []
    for r in chunk:
        b = [f"{REC_SEP}{r['id']}",
             f"# {title_of(r)} | {r.get('date', '?')} | {r.get('genre', '?')}",
             "[LATIN]"]
        b += text_lines(r)
        b += ["[ENGLISH]", ""]   # <- type the English under this line
        blocks.append("\n".join(b))

    header = [
        f"# Epigraphy translation scaffold — {len(chunk)} inscriptions",
        "# Under each [ENGLISH], type a faithful English translation of the Latin",
        "# above it. Expand standard abbreviations (D(is) M(anibus), v(ixit) a(nnos),",
        "# H(ic) s(itus) e(st), etc.). Free prose, one or more lines. Leave blank to skip.",
        f"# Then: python epigraphy_translate.py assemble {os.path.basename(out_path)}",
        "", "",
    ]
    open(out_path, "w", encoding="utf-8").write("\n".join(header) + "\n".join(blocks) + "\n")
    print(f"{len(todo)} untranslated total. Wrote {len(chunk)} to {out_path}")


# ── ASSEMBLE ────────────────────────────────────────────────────────────────
def parse_scaffold(path):
    """Return {id: [english lines]} for every block with non-empty English."""
    raw = open(path, encoding="utf-8").read()
    out = {}
    for chunk in raw.split(REC_SEP)[1:]:
        lines = chunk.splitlines()
        ident = lines[0].strip()
        eng, section = [], None
        for ln in lines[1:]:
            s = ln.rstrip()
            if s.strip() == "[LATIN]":
                section = "latin"; continue
            if s.strip() == "[ENGLISH]":
                section = "eng"; continue
            if s.startswith("#"):
                continue
            if section == "eng":
                eng.append(s)
        eng = [e for e in eng if e.strip()]
        if eng:
            out[ident] = eng
    return out


def do_assemble(path):
    trans = parse_scaffold(path)
    records, header = load_data()
    by_id = {r["id"]: r for r in records}

    built = errors = skipped = 0
    for ident, eng in trans.items():
        if ident not in by_id:
            print(f"[ERR ] {ident}: not found in epigraphy_data.js — skipped.")
            errors += 1
            continue
        by_id[ident]["translation"] = eng
        built += 1

    empty = sum(1 for r in records if not has_translation(r) and text_lines(r))
    if built:
        write_data(records, header)
        print(f"[ OK ] merged {built} translations (backup -> epigraphy_data.js.bak)")
    print(f"\nBuilt {built}, errors {errors}. {empty} inscriptions still untranslated.")
    if errors:
        sys.exit(1)


# ── selftest ────────────────────────────────────────────────────────────────
def selftest():
    sample = "=== HD1\n# Test | 100 CE | funerary\n[LATIN]\nD M\nv a XXX\n[ENGLISH]\nTo the Spirits of the Dead.\nHe lived 30 years.\n\n=== HD2\n[LATIN]\nfoo\n[ENGLISH]\n\n"
    import tempfile
    p = os.path.join(tempfile.gettempdir(), "_epi_selftest.txt")
    open(p, "w", encoding="utf-8").write(sample)
    got = parse_scaffold(p)
    assert set(got) == {"HD1"}, got
    assert got["HD1"] == ["To the Spirits of the Dead.", "He lived 30 years."], got
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scaffold")
    s.add_argument("--batch", type=int, default=150)
    s.add_argument("--start", type=int, default=0)
    a = sub.add_parser("assemble")
    a.add_argument("file")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "scaffold":
        do_scaffold(args.batch, args.start)
    elif args.cmd == "assemble":
        do_assemble(args.file)
    else:
        selftest()


if __name__ == "__main__":
    main()

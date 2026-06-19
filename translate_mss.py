#!/usr/bin/env python3
"""
translate_mss.py — add faithful, LINE-ALIGNED English translations to the
documentary papyri in manuscripts/*.txt.  NO Firecrawl / NTVMR, fully offline.

This is the manuscripts twin of epigraphy_translate.py, reusing the
#greek == #translation safety assertion from build_from_sweep.py.  The papyri
already live on disk (import/scrape produced them); this script only fills the
blank [TRANSLATION] slots, one English line per Greek r.N line so the diglot
reader lines up line-for-line.

  1) SCAFFOLD — pull the next batch of UN-translated papyri:
       python translate_mss.py scaffold --batch 12
     Finds manuscripts/*.txt whose [TRANSLATION] slots are ALL empty (resumable:
     any file with even one filled slot is skipped) and writes
     _mss_translate_<NNN>.txt with, per manuscript: its id, the numbered Greek
     r.N lines, any "# HGV-EN:" reference translation, and one blank English slot
     per Greek line.

  2) (Claude fills the scaffold) — one faithful English line per Greek r.N line,
     line-aligned.  Where a "# HGV-EN:" reference is shown, lay THAT translation
     out line-by-line instead of translating cold; otherwise translate from the
     Greek.  Expand standard abbreviations, keep [restorations], gaps as "…".
     Leave a record's slots blank to skip it (it reappears in the next scaffold).

  3) ASSEMBLE — safety-checked merge back into each .txt:
       python translate_mss.py assemble _mss_translate_<NNN>.txt
     For every record it asserts (# Greek r.N lines) == (# filled English lines),
     aborting THAT record on any mismatch, and refuses to overwrite a file that
     has since been translated.  Backs up nothing-global: it edits only the
     [TRANSLATION] section of each target file in place.

  python translate_mss.py selftest   # offline parser/alignment check
"""

import os, re, sys, glob, argparse, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MSS = os.path.join(HERE, "manuscripts")
REC_SEP = "=== "


# ── flat-section + line parsing ───────────────────────────────────────────────
def flat_section(raw, tag):
    """Text of a FLAT [TAG] section, or None if absent.  Named sections like
    [GREEK:Romans] do NOT match \\[GREEK\\], so multi-book NT manuscripts are
    automatically excluded — this tool only touches flat documentary papyri."""
    m = re.search(rf"\[{tag}\](.*?)(?=\n\[|\Z)", raw, re.S)
    return m.group(1) if m else None


def greek_lines(gtext):
    """[(ref, text)] for each r.N / v.N Greek line with real text (no GAP/FOLIO)."""
    out = []
    for ln in gtext.splitlines():
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("FOLIO"):
            continue
        m = re.match(r"^([rv]\.\d+)\s+(.*)", s)
        if m and m.group(2).strip() and not m.group(2).strip().upper().startswith("GAP:"):
            out.append((m.group(1), m.group(2).strip()))
    return out


def trans_slots(ttext):
    """[(num, text)] for each numbered translation slot, in order, # comments
    skipped.  text is '' for an empty slot."""
    out = []
    for ln in ttext.splitlines():
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("FOLIO"):
            continue
        m = re.match(r"^([\d:]+)\s*(.*)$", s)
        if m:
            out.append((m.group(1), m.group(2).strip()))
    return out


def trans_comments(ttext):
    """Reference comment lines worth carrying through (the HGV-EN prose)."""
    return [ln.rstrip() for ln in ttext.splitlines()
            if ln.strip().startswith("# HGV-EN:")]


def meta_brief(raw):
    name = date = genre = "?"
    sec = flat_section(raw, "META") or ""
    for ln in sec.splitlines():
        s = ln.strip()
        if s.startswith("name:"):
            name = s.split(":", 1)[1].strip()
        elif s.startswith("date:"):
            date = s.split(":", 1)[1].strip()
        elif s.startswith("genre:"):
            genre = s.split(":", 1)[1].strip()
    return name, date, genre


def is_untranslated(raw):
    """True iff this is a flat papyrus with Greek r.N lines and ALL its
    translation slots empty."""
    g = flat_section(raw, "GREEK")
    t = flat_section(raw, "TRANSLATION")
    if g is None or t is None:
        return False
    gl = greek_lines(g)
    slots = trans_slots(t)
    if not gl or not slots:
        return False
    return not any(txt for _, txt in slots)


# ── SCAFFOLD ──────────────────────────────────────────────────────────────────
def do_scaffold(batch):
    files = sorted(glob.glob(os.path.join(MSS, "*.txt")))
    todo, done = [], 0
    for p in files:
        raw = open(p, encoding="utf-8").read()
        t = flat_section(raw, "TRANSLATION")
        if t is not None and any(txt for _, txt in trans_slots(t)):
            done += 1
            continue
        if is_untranslated(raw):
            todo.append((p, raw))

    if not todo:
        print("Nothing to do: every flat papyrus is translated.")
        return

    chunk = todo[:batch]
    tag = f"{done:05d}"
    out_path = os.path.join(HERE, f"_mss_translate_{tag}.txt")

    blocks = []
    for p, raw in chunk:
        stem = os.path.splitext(os.path.basename(p))[0]
        name, date, genre = meta_brief(raw)
        gl = greek_lines(flat_section(raw, "GREEK"))
        b = [f"{REC_SEP}{stem}", f"# {name} | {date} | {genre}"]
        b += trans_comments(flat_section(raw, "TRANSLATION"))
        b.append("[GREEK]")
        b += [f"{ref:<6} {txt}" for ref, txt in gl]
        b.append("[TRANSLATION]")
        b += [f"{i:<5} " for i in range(1, len(gl) + 1)]   # <- type English after the number
        blocks.append("\n".join(b))

    header = [
        f"# Manuscript translation scaffold — {len(chunk)} papyri "
        f"({len(todo)} untranslated total).",
        "# Under each [TRANSLATION], type ONE faithful English line per Greek r.N",
        "# line (line-aligned). Where a '# HGV-EN:' reference is shown, lay THAT",
        "# translation out line-by-line; otherwise translate the Greek. Expand",
        "# standard abbreviations, keep [restorations], render gaps as '…'.",
        "# Leave a record's slots blank to skip it.",
        f"# Then: python translate_mss.py assemble {os.path.basename(out_path)}",
        "", "",
    ]
    open(out_path, "w", encoding="utf-8").write("\n".join(header) + "\n".join(blocks) + "\n")
    print(f"{len(todo)} untranslated total. Wrote {len(chunk)} to {out_path}")


# ── ASSEMBLE ──────────────────────────────────────────────────────────────────
def parse_scaffold(path):
    """{stem: [slot texts in order]} for every block (blank slots kept as '')."""
    raw = open(path, encoding="utf-8").read()
    out = {}
    for chunk in raw.split(REC_SEP)[1:]:
        lines = chunk.splitlines()
        stem = lines[0].strip()
        section, slots = None, []
        for ln in lines[1:]:
            s = ln.strip()
            if s == "[GREEK]":
                section = "greek"; continue
            if s == "[TRANSLATION]":
                section = "trans"; continue
            if s.startswith("#"):
                continue
            if section == "trans":
                m = re.match(r"^([\d:]+)\s*(.*)$", s)
                if m:
                    slots.append(m.group(2).strip())
        out[stem] = slots
    return out


def write_translation(path, eng):
    """Replace the [TRANSLATION] section of `path` in place, filling slots 1..N
    with `eng`. Keeps the # HGV-EN: reference comment for provenance."""
    raw = open(path, encoding="utf-8").read()
    i = raw.index("[TRANSLATION]")
    head = raw[:i].rstrip("\n")
    comments = trans_comments(flat_section(raw, "TRANSLATION"))
    body = [head, "", "[TRANSLATION]"]
    body += comments
    body += [f"{n:<5} {t}" for n, t in enumerate(eng, 1)]
    open(path, "w", encoding="utf-8").write("\n".join(body) + "\n")


def do_assemble(path):
    trans = parse_scaffold(path)
    built = errors = skipped = 0
    for stem, slots in trans.items():
        filled = [t for t in slots if t]
        if not filled:
            skipped += 1
            continue
        target = os.path.join(MSS, stem + ".txt")
        if not os.path.exists(target):
            print(f"[ERR ] {stem}: manuscripts/{stem}.txt not found — skipped.")
            errors += 1; continue
        raw = open(target, encoding="utf-8").read()
        if not is_untranslated(raw):
            print(f"[SKIP] {stem}: already translated on disk — not overwriting.")
            skipped += 1; continue
        ng = len(greek_lines(flat_section(raw, "GREEK")))
        # reuse build_from_sweep's assertion: one English line per Greek line
        if len(slots) != ng or len(filled) != ng:
            print(f"[ERR ] {stem}: {ng} Greek lines but {len(filled)} filled "
                  f"({len(slots)} slots) — must match 1:1. Record aborted.")
            errors += 1; continue
        write_translation(target, slots)
        built += 1
        print(f"[ OK ] {stem} -> {ng} lines")
    print(f"\nBuilt {built}, errors {errors}, skipped(empty/done) {skipped}.")
    if errors:
        print("Fix the [ERR ] records and re-run assemble (built ones stay translated).")
        sys.exit(1)


# ── SPLIT (fan-out helper) ────────────────────────────────────────────────────
def split_records(raw):
    """[(header, [record_text, ...])] — a scaffold's leading comment header and
    its '=== ' records, each record kept whole (META/GREEK/TRANSLATION)."""
    marker = "\n" + REC_SEP
    head, sep, rest = raw.partition(marker)
    if not sep:
        return head, []
    records = [REC_SEP + r for r in (marker + rest).split(marker)[1:]]
    return head, records


def do_split(path, parts):
    """Split one big scaffold into `parts` smaller scaffolds that each carry a
    disjoint set of whole records, so subagents can fill them in parallel with
    no file conflicts (different records -> different manuscripts/*.txt). Prints
    the part filenames, one per line."""
    raw = open(path, encoding="utf-8").read()
    head, records = split_records(raw)
    if not records:
        print("Nothing to split.")
        return
    parts = max(1, min(parts, len(records)))
    base = os.path.splitext(os.path.basename(path))[0]
    buckets = [[] for _ in range(parts)]
    for i, rec in enumerate(records):        # contiguous-ish round-robin keeps
        buckets[i % parts].append(rec)        # parts balanced in record count
    written = []
    for k, bucket in enumerate(buckets):
        if not bucket:
            continue
        out_path = os.path.join(HERE, f"{base}_part{k:02d}.txt")
        body = (f"# Part {k} of {parts} of {os.path.basename(path)} — "
                f"{len(bucket)} records.\n\n" + "\n".join(bucket) + "\n")
        open(out_path, "w", encoding="utf-8").write(body)
        written.append(out_path)
    for p in written:
        print(p)


# ── selftest ──────────────────────────────────────────────────────────────────
def selftest():
    # a fake untranslated papyrus
    fake = ("[META]\nid:       X.1\nname:     Test\ndate:     1 CE\ngenre:    letters\n\n"
            "[GREEK]\nr.1    αλφα\nr.2    GAP: not preserved\nr.3    γαμμα\n\n"
            "[TRANSLATION]\n# HGV-EN: ref prose\n1     \n2     \n3     \n")
    d = tempfile.mkdtemp()
    fp = os.path.join(d, "x_1.txt")
    open(fp, "w", encoding="utf-8").write(fake)

    # parser checks
    assert is_untranslated(fake), "should be untranslated"
    assert len(greek_lines(flat_section(fake, "GREEK"))) == 2, "GAP line excluded -> 2 Greek"
    assert trans_comments(flat_section(fake, "TRANSLATION")) == ["# HGV-EN: ref prose"]

    # scaffold-parse + alignment
    scaf = ("# header\n\n\n" + REC_SEP + "x_1\n# Test | 1 CE | letters\n"
            "# HGV-EN: ref prose\n[GREEK]\nr.1    αλφα\nr.2    γαμμα\n"
            "[TRANSLATION]\n1     alpha\n2     gamma\n")
    sp = os.path.join(d, "_mss_translate_00000.txt")
    open(sp, "w", encoding="utf-8").write(scaf)
    parsed = parse_scaffold(sp)
    assert parsed == {"x_1": ["alpha", "gamma"]}, parsed

    # write-back + idempotent overwrite guard
    write_translation(fp, ["alpha", "gamma"])
    out = open(fp, encoding="utf-8").read()
    assert "1     alpha" in out and "2     gamma" in out, out
    assert "# HGV-EN: ref prose" in out, "reference comment kept"
    assert not is_untranslated(out), "now translated"

    # split: 3 records -> 2 parts, disjoint and whole
    multi = ("# header\n\n" + REC_SEP + "a\n[GREEK]\nr.1 x\n[TRANSLATION]\n1     \n"
             + REC_SEP + "b\n[GREEK]\nr.1 y\n[TRANSLATION]\n1     \n"
             + REC_SEP + "c\n[GREEK]\nr.1 z\n[TRANSLATION]\n1     \n")
    _, recs = split_records(multi)
    assert len(recs) == 3 and recs[0].startswith("=== a") and recs[2].startswith("=== c"), recs
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scaffold")
    s.add_argument("--batch", type=int, default=12)
    a = sub.add_parser("assemble")
    a.add_argument("file")
    sp = sub.add_parser("split")
    sp.add_argument("file")
    sp.add_argument("--parts", type=int, default=10)
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "scaffold":
        do_scaffold(args.batch)
    elif args.cmd == "assemble":
        do_assemble(args.file)
    elif args.cmd == "split":
        do_split(args.file, args.parts)
    else:
        selftest()


if __name__ == "__main__":
    main()

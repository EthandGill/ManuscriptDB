#!/usr/bin/env python3
"""
build_from_sweep.py — turn a _sweep_<range>.json into finished manuscripts/*.txt

Runs in Terminal B (Claude Code) and spends ZERO Firecrawl credits — it only
reads the JSON that Terminal A already paid for. Two phases:

  1) SCAFFOLD — mechanical prep (no judgement):
       python build_from_sweep.py scaffold _sweep_o.wilck_561-610.json
     Classifies each record by its Subjects keyword, cleans the Greek, numbers it
     r.1..r.N, pre-fills the metadata it can derive, and writes
     _translate_<range>.txt with a blank [TRANSLATION] line per Greek line.
     Sparse / unclassifiable records are listed as "# SKIPPED ..." comments.

  2) (Claude fills the scaffold) — for each record, replace TODO in name:/content:
     and type one English line per Greek line. Translate the ACTUAL Greek shown,
     line-aligned. Leave a record's translation blank to drop it.

  3) ASSEMBLE — safety-checked write:
       python build_from_sweep.py assemble _translate_o.wilck_561-610.txt
     For every record it asserts (# Greek lines) == (# filled translation lines)
     and that name:/content: are filled, then writes manuscripts/<slug>.txt.
     ANY mismatch aborts that record with a clear message (this is the check that
     caught every alignment bug). Records with an empty translation are skipped.

Format produced matches the documentary .txt the app already parses (flat r.N
Greek, integer-keyed line-aligned translation).
"""

import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
MSS = os.path.join(HERE, "manuscripts")
GREEK = "Ͱ-Ͽἀ-῿"   # Greek + Greek Extended

# ── classification: HGV German "Subjects" keyword -> app genre ────────────────
GENRE_RULES = [
    ("receipts",  ["quittung"]),
    ("contracts", ["vertrag", "kauf", "darlehen", "pacht", "ehe", "miete"]),
    ("letters",   ["brief"]),
    ("petitions", ["eingabe", "petition"]),
    ("documents", ["abrechnung", "liste", "deklaration", "register", "deklar"]),
]

# ── find-site -> (lat, lon). Add rows as you meet new origins. ────────────────
COORDS = {
    "oxyrhynchus": (28.5383, 30.6765),
    "soknopaiou":  (29.5377, 30.6856),
    "karanis":     (29.5186, 30.9036),
    "arsino":      (29.3084, 30.8428),   # Arsinoite / Arsinoe
    "syene":       (24.0889, 32.8997),
    "elephantine": (24.0889, 32.8997),
    "alexandria":  (31.2001, 29.9187),
    "rome":        (41.8931, 12.4828),
    "bostra":      (32.5185, 36.4817),
    "herakleop":   (29.0667, 30.9333),
    "memphis":     (29.8440, 31.2550),
    "tebtynis":    (29.1117, 30.7450),
    "hermopolis":  (27.7820, 30.8020),
    "theb":        (25.7188, 32.6573),   # Thebes / Thebais / "Theben" (Luxor)
    "hermonthis":  (25.6167, 32.5500),
    "edfu":        (24.9780, 32.8730),
    "apollonopolis": (24.9780, 32.8730),
    "ombos":       (24.4667, 32.9333),
    "diospolis":   (25.7188, 32.6573),
    "pselkis":     (23.1925, 32.7472),   # Pselchis / Dakka, Nubia
    "koptos":      (25.9967, 32.8167),   # Coptos / Qift
    "mendes":      (30.9626, 31.5046),   # Mendes / Tell el-Ruba (Delta)
    "pathyr":      (25.4833, 32.4833),   # Pathyris / Krokodilopolis (Gebelein)
    "sakkara":     (29.8711, 31.2165),   # Saqqara (Memphites)
    "myra":        (36.2589, 29.9853),   # Myra, Lycia (Demre)
    "latopol":     (25.2933, 32.5547),   # Latopolis / Esna
    "eileithy":    (25.1197, 32.7958),   # Eileithyiaspolis / El-Kab
}

SERIES_DISPLAY = {
    "o.wilck": "O.Wilck.", "o.fay": "O.Fay.", "bgu": "BGU", "p.oxy": "P.Oxy.",
    "p.tebt": "P.Tebt.", "p.fay": "P.Fay.", "p.mich": "P.Mich.", "cpr": "CPR",
    "p.cair.zen": "P.Cair.Zen.", "psi": "PSI",
}

REC_SEP = "=== "   # scaffold record delimiter


# ── helpers ───────────────────────────────────────────────────────────────────
def citation(ident):
    parts = ident.split(";")
    series = parts[0]
    rest = [p for p in parts[1:] if p != ""]
    disp = SERIES_DISPLAY.get(series, series.upper())
    return f"{disp} {'.'.join(rest)}".strip()


def slug(ident):
    s = ident.replace(";", "_").replace(".", "_")
    return re.sub(r"_+", "_", s).strip("_")


def classify(subjects):
    s = (subjects or "").lower()
    for genre, keys in GENRE_RULES:
        if any(k in s for k in keys):
            return genre
    return None


_DE_MONTHS = {"Jan.": "Jan", "Feb.": "Feb", "März": "Mar", "Apr.": "Apr",
              "Mai": "May", "Juni": "Jun", "Juli": "Jul", "Aug.": "Aug",
              "Sept.": "Sep", "Okt.": "Oct", "Nov.": "Nov", "Dez.": "Dec"}

def clean_date(date):
    """Normalise an HGV German date: drop markdown escapes, English months, notes."""
    d = (date or "unknown").replace("\\", "").strip()
    for de, en in _DE_MONTHS.items():
        d = d.replace(de, en)
    d = d.replace("Tag unsicher", "day uncertain").replace("Jahr unsicher", "year uncertain")
    d = re.sub(r"\s+", " ", d).strip()
    return d


def coords_for(origin):
    o = (origin or "").lower()
    for key, (la, lo) in COORDS.items():
        if key in o:
            return la, lo
    return None, None


def clean_line(line):
    line = re.sub(r"^\s*\d+(?=[(\[\s%s])" % GREEK, "", line)  # every-5 counter glued at line start (5(ἔτους), 10(hand 1))
    line = re.sub(r"⁦[^⁩]*⁩", "…", line)     # ⁦ -ca.?- ⁩ isolate length-markers -> …
    line = re.sub(r"[⁦⁧⁨⁩]", "", line)        # any stray directional-isolate marks
    line = line.replace("\\[", "[").replace("\\]", "]")     # unescape markdown brackets
    line = re.sub(r"[\\/]", "", line)                       # \\..// above-line marks, stray escapes
    line = re.sub(r"_\([^)]*\)_", "", line)                 # _(Reprinted from O.Wilck NNNN)_ markdown notes
    line = re.sub(r"⟦[^⟧]*⟧", "", line)      # ⟦deletions⟧
    line = re.sub(r"\(\([^)]*\)\)", "", line)               # ((editorial notes))
    line = re.sub(r"~+", "", line)                          # ~~~ markers
    line = re.sub(r"-?\bca\.\??-?", "…", line)              # leftover -ca.?- length markers
    line = re.sub(r"\bvac\.?\b", "", line, flags=re.I)
    line = re.sub(r"(?<![%s\w])\d+(?=[%s])" % (GREEK, GREEK), "", line)  # 5Ταμείων -> Ταμείων
    line = re.sub(r"…(\s*…)+", "…", line)                   # collapse repeated …
    line = re.sub(r"\s+", " ", line).strip(" |")
    return line


_APPARATUS = re.compile(
    r"(^\s*[.\-])|(^\s*\d+\.\s)|(\blin\d)|(=>)|(\|ed\|)|(\bl\.\s)|(\bBL\b)|"
    r"(prev\.\s*ed)|(corr\.)|\bZPE\b|\bAPF\b|\bcf\.\b|Traces|(p\.\s*\d+)|(,\s*n\.\s*\d)|"
    r"(\bpapyrus\b)|(\bostrac)|(\s\|\s)|(^\s*(Title|Subjects|Inv|Date|Material|Origin|Provenance|Language)\b)",
    re.I)

def clean_greek(greek):
    out = []
    for raw in greek or []:
        # strip directional-isolate marks + leading space so the ^-anchored
        # apparatus patterns still fire on lines like "⁧3. ϊερασ papyrus"
        probe = re.sub(r"[⁦⁧⁨⁩]", "", raw).lstrip()
        if _APPARATUS.search(probe):
            continue
        c = clean_line(raw)
        if c and re.search("[" + GREEK + "]", c):
            out.append(c)
    return out


# ── SCAFFOLD ──────────────────────────────────────────────────────────────────
def do_scaffold(json_path):
    data = json.load(open(json_path, encoding="utf-8"))
    rng = os.path.basename(json_path).replace("_sweep_", "").replace(".json", "")
    out_path = os.path.join(HERE, f"_translate_{rng}.txt")

    blocks, skipped = [], []
    for ident, rec in data.items():
        genre = classify(rec.get("subjects"))
        gk = clean_greek(rec.get("greek"))
        if not gk:
            skipped.append(f"# SKIPPED {ident}: no Greek preserved")
            continue
        if genre is None:
            # Never skip a record that has preserved Greek: default an
            # unrecognised Subjects keyword to the generic "documents" genre.
            genre = "documents"
        la, lo = coords_for(rec.get("origin"))
        cite = citation(ident)
        lines = [f"{REC_SEP}{ident}"]
        lines.append("[META]")
        lines.append(f"id:       {cite}")
        lines.append(f"label:    {cite}")
        lines.append("name:     TODO short title (e.g. 'Tax receipt — poll-tax')")
        lines.append(f"genre:    {genre}")
        lines.append(f"date:     {clean_date(rec.get('date'))}")
        lines.append("language: Greek (Koiné)")
        lines.append(f"found:    {rec.get('origin') or 'unknown'}")
        lines.append("held:     (see shelf)")
        lines.append(f"shelf:    {rec.get('shelf') or 'unknown'}")
        lines.append("content:  TODO one-line content summary")
        lines.append(f"tm:       {rec.get('tm') or ''}")
        lines.append(f"source:   https://papyri.info/ddbdp/{ident}")
        lines.append(f"lat:      {la if la is not None else ''}")
        lines.append(f"lon:      {lo if lo is not None else ''}")
        lines.append("")
        lines.append("[GREEK]")
        for i, g in enumerate(gk, 1):
            lines.append(f"r.{i:<4} {g}")
        lines.append("")
        lines.append("[TRANSLATION]")
        for i in range(1, len(gk) + 1):
            lines.append(f"{i:<5} ")   # <- type the English after the number
        blocks.append("\n".join(lines))

    header = [
        f"# Translation scaffold for {rng} — generated by build_from_sweep.py",
        "# Fill each record: replace the TODO in name:/content:, and type one",
        "# English line per Greek line (translate the ACTUAL Greek shown, line-",
        "# aligned). Leave a record's TRANSLATION lines blank to drop it.",
        "# Then: python build_from_sweep.py assemble " + os.path.basename(out_path),
        "#",
        f"# {len([b for b in blocks])} buildable, {len(skipped)} skipped.",
    ] + skipped + ["", ""]

    open(out_path, "w", encoding="utf-8").write("\n".join(header) + "\n".join(blocks) + "\n")
    print(f"Scaffold: {len(blocks)} records to translate, {len(skipped)} skipped.")
    print(f"Wrote {out_path}")


# ── ASSEMBLE ──────────────────────────────────────────────────────────────────
def _parse_record(text):
    """Return (ident, meta_lines, greek_lines, trans_texts)."""
    ident = text.splitlines()[0].strip()
    meta, greek, trans = [], [], []
    section = None
    for ln in text.splitlines()[1:]:
        s = ln.rstrip("\n")
        if s.strip() == "[META]":
            section = "meta"; continue
        if s.strip() == "[GREEK]":
            section = "greek"; continue
        if s.strip() == "[TRANSLATION]":
            section = "trans"; continue
        if section == "meta" and s.strip():
            meta.append(s)
        elif section == "greek":
            if re.match(r"\s*r\.\d+", s):
                greek.append(s)
        elif section == "trans":
            m = re.match(r"\s*(\d+)\s?(.*)$", s)
            if m:
                trans.append(m.group(2).strip())
    return ident, meta, greek, trans


def do_assemble(scaffold_path):
    raw = open(scaffold_path, encoding="utf-8").read()
    chunks = raw.split("\n" + REC_SEP)
    # first chunk holds the header; re-attach delimiter to the rest
    records = []
    for i, c in enumerate(chunks):
        c = c if c.startswith(REC_SEP) else (REC_SEP + c if i else c)
        if REC_SEP in c:
            records.append(c[c.index(REC_SEP) + len(REC_SEP):])
    os.makedirs(MSS, exist_ok=True)
    built = errors = skipped = 0
    for rectext in records:
        ident, meta, greek, trans = _parse_record(rectext)
        filled = [t for t in trans if t]
        if not filled:
            skipped += 1
            continue
        # checks
        metablob = "\n".join(meta)
        if "TODO" in metablob:
            print(f"[ERR ] {ident}: name:/content: still has TODO — fill it.")
            errors += 1; continue
        if len(greek) != len(trans) or any(t == "" for t in trans):
            print(f"[ERR ] {ident}: {len(greek)} Greek lines but "
                  f"{len(filled)} translation lines — must match 1:1.")
            errors += 1; continue
        # write (normalise the date meta line at write time)
        meta = [(f"date:     {clean_date(m.split(':',1)[1])}" if m.startswith("date:") else m)
                for m in meta]
        body = ["[META]"] + meta + ["", "[GREEK]"]
        body += greek
        body += ["", "[TRANSLATION]"]
        body += [f"{i:<5} {t}" for i, t in enumerate(trans, 1)]
        path = os.path.join(MSS, slug(ident) + ".txt")
        open(path, "w", encoding="utf-8").write("\n".join(body) + "\n")
        built += 1
        print(f"[ OK ] {ident} -> manuscripts/{slug(ident)}.txt ({len(greek)} lines)")
    print(f"\nBuilt {built}, errors {errors}, skipped(empty) {skipped}.")
    if errors:
        print("Fix the [ERR ] records and re-run assemble (built ones are overwritten harmlessly).")
        sys.exit(1)


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("scaffold", "assemble"):
        sys.exit("usage: build_from_sweep.py scaffold <_sweep_*.json>\n"
                 "       build_from_sweep.py assemble <_translate_*.txt>")
    if sys.argv[1] == "scaffold":
        do_scaffold(sys.argv[2])
    else:
        do_assemble(sys.argv[2])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
clean_inscriptions.py - strip EDH "#" multi-reading artifacts from the inscription
`text` in static/epigraphy_data.js.

EDH's EpiDoc edition stored some words as several `#`-separated readings, and the
edh_ingest renderer copied them all into the displayed Greek/Latin:

    <merged-blob>#<interpretive>#<DIPLOMATIC-CAPS>      e.g. SilIvinius#Si[l]vinius#SIIVINIUS

Only the MIDDLE form (the scholarly interpretive reading - lowercase, with
[restorations]/(expansions)) is meant to display. The merged blob, the ALL-CAPS
diplomatic, and the `#` separators are noise.

The rule (per INSCRIPTIONS-text-cleanup.md):
  - 3 segments -> keep the middle (interpretive) one.
  - 2 segments -> keep the bracketed/lowercase one, drop the ALL-CAPS / merge blob.
  - Remove the `#` separators. Tokens/lines with no `#` are left byte-for-byte
    unchanged.
  - Groups can span a space AND a list-entry (line) break, because EDH splits a
    word across physical lines; we therefore operate on the whole joined text of
    each record's `text` list, not naively on space-tokens.

Only `text` is changed; translation/genre/title/coordinates/etc. are preserved.
This is token-free (pure string surgery, no model).

    python clean_inscriptions.py            # clean the data file in place (.bak first)
    python clean_inscriptions.py --selftest # offline parser check, no file writes
"""

import os, re, sys, json, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "static", "epigraphy_data.js")
PREFIX = "window.EPIGRAPHY_DATA = "

# A 3-reading group: <blob>#<interp>#<DIPL>. The blob (S0) and the interpretive
# segment (S1) may each continue after ONE line break (\n) because EDH split the
# carved word across physical lines; the diplomatic (S2) is a single whitespace-
# free run. We keep S1 (the text between the two `#`).
#   - S0  : either  <blob-head with '=' merge marker>\n<continuation>  (cross-line),
#           or       [^\s#]*                                           (within-line)
#     The cross-line branch fires ONLY when the head carries a merge marker ('='),
#     which is the signature of a word split across EDH lines; this avoids eating a
#     clean preceding line that merely ends a word fragment (e.g. a rasura prefix).
#   - S1  : ([^#]*?)                  everything between the two `#` (may contain \n)
#   - S2  : [^\s#]*                   the ALL-CAPS diplomatic reading (may be empty,
#                                     e.g. within a rasura where it was erased)
THREE = re.compile(
    r'(?<!\S)(?:[^\s#]*=[^\s#]*\n[^#\n]*|[^\s#]*)#([^#]*?)#[^\s#]*(?!\S)')

# A leftover 2-reading group (single `#`), whitespace-bounded.
TWO = re.compile(r'(?<!\S)[^\s#]+#[^\s#]+(?!\S)')


def _is_diplomatic(seg):
    """All-caps carved reading: has letters and every letter is uppercase."""
    letters = [c for c in seg if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def _is_blob(seg):
    """Merged blob: carries the `[interp=DIPL]` / `<interp=DIPL>` merge marker."""
    return "=" in seg


def _pick_two(match):
    a, b = match.group(0).split("#", 1)
    cand = [s for s in (a, b) if not _is_diplomatic(s) and not _is_blob(s)]
    if len(cand) == 1:
        return cand[0]
    pool = cand if cand else [a, b]
    for s in pool:                       # prefer the bracketed/expansion reading
        if "[" in s or "(" in s:
            return s
    return pool[0]


def clean_text(lines):
    """Apply the rule to a record's `text` list. Returns a (possibly shorter) list.
    If there is no `#`, the original list is returned unchanged (byte-identical)."""
    if not any("#" in ln for ln in lines):
        return lines
    joined = "\n".join(lines)
    joined = THREE.sub(lambda m: m.group(1), joined)   # 3-reading groups
    joined = TWO.sub(_pick_two, joined)                # any leftover 2-reading
    return joined.split("\n")


# -- data file I/O (mirrors epigraphy_translate.py so the file format is identical) --
def load_data():
    raw = open(DATA, encoding="utf-8").read()
    if PREFIX not in raw:
        raise SystemExit(f"{DATA}: no '{PREFIX.strip()}' wrapper found.")
    cut = raw.index(PREFIX)
    header = raw[:cut]
    payload = raw[cut + len(PREFIX):].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    return json.loads(payload), header


def write_data(records, header):
    shutil.copyfile(DATA, DATA + ".bak")
    body = json.dumps(records, ensure_ascii=False)
    open(DATA, "w", encoding="utf-8").write(f"{header}{PREFIX}{body};\n")


def run():
    records, header = load_data()
    changed = lines_before = lines_after = 0
    for r in records:
        t = r.get("text")
        if not isinstance(t, list):
            continue
        cleaned = clean_text(t)
        if cleaned != t:
            changed += 1
            lines_before += len(t)
            lines_after += len(cleaned)
            r["text"] = cleaned
    write_data(records, header)
    leftover = sum(s.count("#") for r in records
                   for s in (r.get("text") or []) if isinstance(s, str))
    print(f"records changed: {changed}")
    print(f"text lines in changed records: {lines_before} -> {lines_after}")
    print(f"remaining '#' in any text: {leftover}")
    print(f"backup -> {os.path.basename(DATA)}.bak")
    if leftover:
        sys.exit("ERROR: '#' artifacts remain - inspect before committing.")


def selftest():
    cases = [
        # 3-segment, within one line
        (["SilIvinius#Si[l]vinius#SIIVINIUS Aurelius"], ["Si[l]vinius Aurelius"]),
        (["aderuInt#ader[u]nt#ADERINT"], ["ader[u]nt"]),
        (["x colonor[um=I]#colonor[um]#COLONORI y"], ["x colonor[um] y"]),
        (["a redem<p=I>tori#redem[p]tori#REDEMITORI b"], ["a redem[p]tori b"]),
        (["Tre(verorum) dePv(o)ta#d[e]v(o)ta#DPVTA ac dicat[a m]ai[esta]ti eius"],
         ["Tre(verorum) d[e]v(o)ta ac dicat[a m]ai[esta]ti eius"]),
        # no '#': untouched, byte identical (incl. multiple lines)
        (["plain line one", "second [restored] line"],
         ["plain line one", "second [restored] line"]),
        # cross-line blob (word split across list entries) -> 3 lines collapse to 2
        (["si partem IIII anni a[ppar=RRIP]", "uissent#a[ppar]",
          "uissent#ARRIPUISSENT ut pro portione"],
         ["si partem IIII anni a[ppar]", "uissent ut pro portione"]),
        (["mater [qu=C]o", "d#[qu]o", "d#COD petierat"],
         ["mater [qu]o", "d petierat"]),
        (["liceto i[t=IS]", "que sic#i[t]", "que sic#IISQUE eis facere"],
         ["liceto i[t]", "que sic eis facere"]),
        # 3-segment with EMPTY diplomatic (rasura), clean [[g(arum) prefix kept
        (["coh(orti) I Sept(imiae) Bel",
          "[[g(arum) AleDxandrian(ae)]]#Al[e]xandrian(ae)]]#", "sub c(ura)"],
         ["coh(orti) I Sept(imiae) Bel", "[[g(arum) Al[e]xandrian(ae)]]", "sub c(ura)"]),
    ]
    ok = True
    for src, exp in cases:
        got = clean_text(list(src))
        status = "ok " if got == exp else "FAIL"
        if got != exp:
            ok = False
            print(f"[{status}] {src}\n        got={got}\n        exp={exp}")
        else:
            print(f"[{status}] {src} -> {got}")
    print("selftest OK" if ok else "selftest FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    run()

#!/usr/bin/env python3
"""
extract_verses.py  —  ManuscriptDB verse-aligned Greek extractor
=================================================================

Companion to import_manuscript.py. Where the importer lays the Greek out by
*physical line* (r.1, r.2, ...) with no verse markers, this script uses the
NTVMR TEI <ab n="B07K7V10"> verse anchors to reassemble the manuscript's actual
text grouped *by verse*, cleaned for reading:

  * words split across a line break ("word—" + continuation) are re-joined
  * reconstruction brackets [..] and nomina sacra {..} are KEPT, so you can see
    exactly what this manuscript reads (variants included) versus the standard text
  * physical gaps (lacuna / illegible) are marked with …

It then prints a ready-to-fill [TRANSLATION] scaffold: one commented GK: line
showing the real Greek of each verse, followed by a blank line for the English.
Fill the blanks in with a faithful translation of THAT Greek — not the ESV
boilerplate for the verse number.

Usage (run inside the ManuscriptDB project, where NTVMR is reachable):

    python extract_verses.py --docID 10015 --pages 10 20

    # write straight to a scaffold file instead of stdout
    python extract_verses.py --docID 10015 --id P15 --pages 10 20 \
        --out manuscripts\P15.translation.txt

The page IDs are the same ones you passed to import_manuscript.py (use
.claude\skills\grab-manuscript\scripts\probe_pages.py to discover them).
"""

import argparse, re, ssl, sys, urllib.request
import xml.etree.ElementTree as ET

# Windows often lacks root certs for urllib — bypass verification for NTVMR
# (identical to import_manuscript.py)
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


# ── FETCH ───────────────────────────────────────────────────────────────────

def fetch_xml(doc_id, page_id, retries=4):
    import time as _time
    url = (f"https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           f"?docID={doc_id}&pageID={page_id}&format=xml")
    print(f"  Fetching pageID={page_id} … ", end="", file=sys.stderr, flush=True)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=25, context=_SSL_CTX) as r:
                data = r.read().decode("utf-8")
            print("OK", file=sys.stderr)
            return data
        except Exception as e:
            if attempt < retries - 1:
                print(f"retry({attempt+1}) … ", end="", file=sys.stderr, flush=True)
                _time.sleep(3)
            else:
                print(f"FAILED ({e})", file=sys.stderr)
    return None


# ── XML HELPERS (kept in sync with import_manuscript.py) ─────────────────────

def strip_ns(xml_text):
    """Remove TEI namespace so tag names are plain strings."""
    return re.sub(r'\s*xmlns(?::[^=]*)?\s*=\s*"[^"]*"', "", xml_text)


def all_text(node):
    """All text inside a node, joined and stripped."""
    return "".join(node.itertext()).strip()


def localname(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def word_to_token(w):
    """
    Convert a <w> element to a single clean Greek token.

    Mirrors import_manuscript.word_to_str but RE-JOINS words that are split
    across a <lb break="no"/> (the importer keeps them on separate lines with a
    trailing —; for continuous verse text we want the whole word).

      * <abbr type="nomSac"|"num">  -> {text}      (nomen sacrum kept marked)
      * <supplied> wrapping a nomSac -> {text}
      * <supplied> otherwise        -> [text]      (reconstruction kept marked)
      * <unclear>/<hi>/other        -> text
    """
    parts = []

    if w.text and w.text.strip():
        parts.append(w.text.strip())

    for child in w:
        tag = localname(child.tag)

        if tag == "lb" and child.get("break") == "no":
            # word continues — keep concatenating, no hyphen, no space
            if child.tail and child.tail.strip():
                parts.append(child.tail.strip())
            continue

        if tag == "abbr":
            atype = child.get("type", "")
            t = all_text(child)
            chunk = "{" + t + "}" if atype in ("nomSac", "num") else t

        elif tag == "supplied":
            nom = child.find(".//abbr[@type='nomSac']")
            if nom is not None:
                chunk = "{" + all_text(nom) + "}"
            else:
                chunk = "[" + all_text(child) + "]"

        elif tag in ("unclear", "hi"):
            chunk = all_text(child)

        else:
            chunk = all_text(child)

        parts.append(chunk)
        if child.tail and child.tail.strip():
            parts.append(child.tail.strip())

    return "".join(parts).strip()


# ── VERSE DECODING (kept in sync with import_manuscript.py) ──────────────────

BOOK_MAP = {
    'B01':'Matthew','B02':'Mark','B03':'Luke','B04':'John','B05':'Acts',
    'B06':'Romans','B07':'1 Corinthians','B08':'2 Corinthians',
    'B09':'Galatians','B10':'Ephesians','B11':'Philippians',
    'B12':'Colossians','B13':'1 Thessalonians','B14':'2 Thessalonians',
    'B15':'1 Timothy','B16':'2 Timothy','B17':'Titus','B18':'Philemon',
    'B19':'Hebrews','B20':'James','B21':'1 Peter','B22':'2 Peter',
    'B23':'1 John','B24':'2 John','B25':'3 John','B26':'Jude',
    'B27':'Revelation',
}

def decode_ab_ref(n):
    """'B07K7V10' -> ('1 Corinthians', 7, 10)"""
    m = re.match(r'(B\d+)K(\d+)V(\d+)', n or "")
    if not m:
        return None
    book = BOOK_MAP.get(m.group(1), m.group(1))
    return (book, int(m.group(2)), int(m.group(3)))


# ── PAGE PARSER (verse-grouped) ──────────────────────────────────────────────

def parse_page_verses(xml_text):
    """
    Return an ordered list of (ref, token_list) where ref = (book, chap, verse).

    Words are bucketed under whichever <ab n="..."> verse anchor encloses them.
    Anything before the first decodable anchor falls under ('?', 0, 0).
    """
    xml_text = re.sub(
        r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', xml_text)
    xml_text = strip_ns(xml_text)
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"    (skipped — malformed XML: {e})", file=sys.stderr)
        return []

    body = root.find(".//body")
    if body is None:
        return []

    order = []          # verse refs in first-seen order
    buckets = {}        # ref -> [tokens]
    state = {"cur": ("?", 0, 0)}

    def add(tok):
        if not tok:
            return
        ref = state["cur"]
        if ref not in buckets:
            buckets[ref] = []
            order.append(ref)
        buckets[ref].append(tok)

    def walk(elem):
        for child in elem:
            ctag = localname(child.tag)

            if ctag == "ab":
                # Set the current verse and let it stay "sticky": this works
                # whether <ab> is a container wrapping the verse's words OR an
                # empty milestone anchor followed by sibling words.
                ref = decode_ab_ref(child.get("n", ""))
                if ref:
                    state["cur"] = ref
                walk(child)          # words inside this verse anchor (if any)

            elif ctag == "w":
                add(word_to_token(child))
                # do NOT recurse — word_to_token consumed the children

            elif ctag == "gap":
                reason = child.get("reason", "")
                if reason in ("lacuna", "illegible", ""):
                    add("…")

            elif ctag in ("note", "pb", "cb", "teiHeader", "lb"):
                pass                  # metadata / handled inline

            else:
                walk(child)           # div, unclear, hi, etc.

    walk(body)
    return [(ref, buckets[ref]) for ref in order]


# ── COLLATION ACROSS PAGES ───────────────────────────────────────────────────

def collate(pages_verse_lists):
    """
    Merge per-page verse buckets into one ordered structure:
        book -> [(chap, verse, "greek text"), ...]
    A verse appearing on more than one page is concatenated in page order.
    """
    merged = {}          # ref -> [tokens]
    order = []           # ref order across all pages
    for verse_list in pages_verse_lists:
        for ref, tokens in verse_list:
            if ref == ("?", 0, 0):
                continue  # skip unanchored scraps
            if ref not in merged:
                merged[ref] = []
                order.append(ref)
            merged[ref].extend(tokens)

    # group by book, preserving order of first appearance
    by_book = {}
    book_order = []
    for ref in order:
        book, chap, verse = ref
        if book not in by_book:
            by_book[book] = []
            book_order.append(book)
        text = " ".join(merged[ref]).strip()
        # tidy up spacing around the gap marker
        text = re.sub(r"\s*…\s*", " … ", text).strip()
        by_book[book].append((chap, verse, text))

    # sort verses within each book by (chap, verse)
    for book in by_book:
        by_book[book].sort(key=lambda t: (t[0], t[1]))

    return book_order, by_book


# ── SCAFFOLD BUILDER ─────────────────────────────────────────────────────────

def build_scaffold(doc_id, manuscript_id, book_order, by_book):
    out = []
    out.append("# " + "─" * 70)
    out.append(f"# Verse-aligned Greek scaffold"
               + (f" for {manuscript_id}" if manuscript_id else "")
               + f"  (NTVMR docID={doc_id})")
    out.append("# Generated by extract_verses.py")
    out.append("#")
    out.append("# Each verse below shows the manuscript's ACTUAL reconstructed Greek:")
    out.append("#   [..] = editorially supplied / reconstructed   {..} = nomen sacrum")
    out.append("#   …    = physical gap (not preserved)")
    out.append("#")
    out.append("# Translate each verse FROM THIS GREEK. Reflect this manuscript's own")
    out.append("# readings where they differ from the standard text — do not paste the")
    out.append("# generic ESV wording for the verse number. Then put the finished verse")
    out.append("# lines into the .txt file's [TRANSLATION] section and delete the GK: lines.")
    out.append("# " + "─" * 70)
    out.append("")

    multi_book = len(book_order) > 1
    for book in book_order:
        if multi_book:
            out.append(f"[TRANSLATION:{book}]")
        else:
            out.append("[TRANSLATION]")
        out.append("")
        for chap, verse, greek in by_book[book]:
            ref = f"{chap}:{verse}"
            out.append(f"# {ref:<7} GK: {greek}")
            out.append(f"{ref:<7}")
            out.append("")
        out.append("")

    return "\n".join(out)


# ── SELF TEST (offline, no network) ──────────────────────────────────────────

_SELFTEST_XML = """<?xml version="1.0" encoding="utf-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
 <text><body>
  <ab n="B07K7V18">
   <w>τις</w>
   <lb n="1"/>
   <w>κε<supplied reason="lost">κλη</supplied><lb break="no"/>ται</w>
   <w>μη</w>
   <w><abbr type="nomSac">θυ</abbr></w>
   <gap reason="lacuna" extent="2"/>
  </ab>
  <ab n="B07K7V19">
   <w>ουδεν</w>
   <w>εστιν</w>
  </ab>
 </body></text>
</TEI>"""

def selftest():
    verse_list = parse_page_verses(_SELFTEST_XML)
    book_order, by_book = collate([verse_list])
    got = {(c, v): t for (c, v, t) in by_book.get("1 Corinthians", [])}

    expected = {
        (7, 18): "τις κε[κλη]ται μη {θυ} …",   # split word re-joined, [..]/{..} kept, gap = …
        (7, 19): "ουδεν εστιν",
    }
    ok = True
    for ref, exp in expected.items():
        actual = got.get(ref)
        status = "PASS" if actual == exp else "FAIL"
        if actual != exp:
            ok = False
        print(f"  [{status}] {ref[0]}:{ref[1]}")
        print(f"         expected: {exp!r}")
        print(f"         actual:   {actual!r}")
    print()
    print("SELFTEST:", "ALL PASS ✅" if ok else "FAILURE ❌")
    print("\n--- sample scaffold ---")
    print(build_scaffold("TEST", "Pxx", book_order, by_book))
    sys.exit(0 if ok else 2)


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    if "--selftest" in sys.argv:
        selftest()

    p = argparse.ArgumentParser(
        description="Extract verse-aligned Greek from NTVMR and emit a "
                    "[TRANSLATION] scaffold for faithful, manuscript-accurate translation.")
    p.add_argument("--selftest", action="store_true",
                   help="Run an offline parser self-test (no network) and exit.")
    p.add_argument("--docID", required=True, help="NTVMR document ID  e.g. 10015")
    p.add_argument("--id", default="", help="Manuscript label for the header  e.g. P15")
    p.add_argument("--pages", nargs="+", type=int, default=[10, 20],
                   help="NTVMR page IDs (same ones used for import). Default: 10 20")
    p.add_argument("--out", default="", help="Optional output file. Default: stdout.")
    args = p.parse_args()

    pages_verse_lists = []
    for pid in args.pages:
        xml = fetch_xml(args.docID, pid)
        if xml:
            verse_list = parse_page_verses(xml)
            if verse_list:
                n = sum(1 for ref, _ in verse_list if ref != ("?", 0, 0))
                print(f"    >> pageID={pid}: {n} verse anchors", file=sys.stderr)
                pages_verse_lists.append(verse_list)

    if not pages_verse_lists:
        print("\nNo verse-anchored content found. Check --docID and --pages.",
              file=sys.stderr)
        sys.exit(1)

    book_order, by_book = collate(pages_verse_lists)
    if not book_order:
        print("\nFound pages but no decodable <ab> verse anchors. The transcription "
              "may lack verse markup; fall back to manual segmentation.", file=sys.stderr)
        sys.exit(1)

    scaffold = build_scaffold(args.docID, args.id, book_order, by_book)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(scaffold)
        nverses = sum(len(v) for v in by_book.values())
        print(f"\nWrote scaffold ({nverses} verses across {len(book_order)} book(s)) "
              f"to {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(scaffold)


if __name__ == "__main__":
    main()

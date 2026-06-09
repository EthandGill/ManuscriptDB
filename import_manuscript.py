#!/usr/bin/env python3
"""
import_manuscript.py  —  ManuscriptDB importer
Fetches TEI XML from NTVMR and writes a manuscripts/<ID>.txt file.

Usage:
    python import_manuscript.py ^
        --docID 10001 --id P1 --name "Papyrus 1" ^
        --genre new-testament --date "c. 250 CE" ^
        --found "Oxyrhynchus, Egypt" --held "Penn Museum (E 2746)" ^
        --content "Matthew 1:1-9, 1:12-20" ^
        --lat 28.5383 --lon 30.6765 ^
        --pages 10 20
"""

import argparse, os, re, ssl, urllib.request
import xml.etree.ElementTree as ET

# Windows often lacks root certs for urllib — bypass verification for NTVMR
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

MANUSCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "manuscripts")


# ── FETCH ─────────────────────────────────────────────────────────────────────

def fetch_xml(doc_id, page_id, retries=4):
    import time as _time
    url = (f"https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           f"?docID={doc_id}&pageID={page_id}&format=xml")
    print(f"  Fetching pageID={page_id} … ", end="", flush=True)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=25, context=_SSL_CTX) as r:
                data = r.read().decode("utf-8")
            print("OK")
            return data
        except Exception as e:
            if attempt < retries - 1:
                print(f"retry({attempt+1}) … ", end="", flush=True)
                _time.sleep(3)
            else:
                print(f"FAILED ({e})")
    return None


# ── XML HELPERS ───────────────────────────────────────────────────────────────

def strip_ns(xml_text):
    """Remove TEI namespace so tag names are plain strings."""
    return re.sub(r'\s*xmlns(?::[^=]*)?\s*=\s*"[^"]*"', "", xml_text)


def all_text(node):
    """All text inside a node, joined and stripped."""
    return "".join(node.itertext()).strip()


def word_to_str(w):
    """
    Convert a <w> element to (before, after) strings.
    'after' is non-empty when the word crosses a <lb break="no"/>,
    meaning the word is split across two manuscript lines.
    before gets a trailing — in the caller.
    """
    before, after = [], []
    past_split = False

    # Leading text of <w> itself
    if w.text and w.text.strip():
        before.append(w.text.strip())

    for child in w:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

        # ── line-break marker inside a word ──────────────────────────────
        if tag == "lb" and child.get("break") == "no":
            past_split = True
            if child.tail and child.tail.strip():
                after.append(child.tail.strip())
            continue

        # ── derive the text representation of this child ─────────────────
        if tag == "abbr":
            atype = child.get("type", "")
            t = all_text(child)
            chunk = "{" + t + "}" if atype in ("nomSac", "num") else t

        elif tag == "supplied":
            # supplied may wrap a nomSac — render as {x} not [x]
            nom = child.find(".//abbr[@type='nomSac']")
            if nom is not None:
                chunk = "{" + all_text(nom) + "}"
            else:
                chunk = "[" + all_text(child) + "]"

        elif tag in ("unclear", "hi"):
            chunk = all_text(child)

        else:
            # unknown child — just grab text
            chunk = all_text(child)

        target = after if past_split else before
        target.append(chunk)

        # tail text after the child tag
        if child.tail and child.tail.strip():
            target.append(child.tail.strip())

    return "".join(before).strip(), "".join(after).strip()


# ── PAGE PARSER ───────────────────────────────────────────────────────────────

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
    m = re.match(r'(B\d+)K(\d+)V(\d+)', n)
    if not m:
        return None
    book = BOOK_MAP.get(m.group(1), m.group(1))
    return (book, int(m.group(2)), int(m.group(3)))

def extract_folio_label_and_verses(root):
    """
    Returns (folio_label_p75, is_recto) from editorial notes and ab verse refs.
    P75 format: 'NR' or 'NV' e.g. '17V', '4R'.
    Falls back to content-based label if no note found.
    """
    # Try editorial note first: "F19v = frg. XVI" -> "19V"
    folio_code = None
    for note in root.iter('note'):
        if note.get('type') == 'editorial':
            t = ''.join(note.itertext()).strip()
            m = re.search(r'\bF(\d+)(r|v)\b', t, re.I)
            if m:
                folio_code = m.group(1) + m.group(2).upper()
                break

    # Gather verse range from <ab n="B07K7V10"> elements
    verse_refs = []
    for ab in root.iter('ab'):
        n = ab.get('n', '')
        ref = decode_ab_ref(n)
        if ref:
            verse_refs.append(ref)

    # Build verse range string (e.g. "1 Corinthians 4:9-10")
    verse_label = ''
    if verse_refs:
        book = verse_refs[0][0]
        chap_start, v_start = verse_refs[0][1], verse_refs[0][2]
        chap_end,   v_end   = verse_refs[-1][1], verse_refs[-1][2]
        if chap_start == chap_end:
            verse_label = f"{book} {chap_start}:{v_start}-{v_end}"
        else:
            verse_label = f"{book} {chap_start}:{v_start}-{chap_end}:{v_end}"

    # Determine is_recto from folio_code
    is_recto = True
    if folio_code:
        is_recto = folio_code.endswith('R')

    # Build P75-style FOLIO label
    if folio_code and verse_label:
        folio_label = f"{folio_code} — {verse_label}"
    elif folio_code:
        folio_label = folio_code
    elif verse_label:
        # Unknown folio number
        is_recto = True  # default; will be overridden by existing pb label
        folio_label = f"? — {verse_label}"
    else:
        folio_label = "?"

    return folio_label, is_recto

def normalise_folio(raw):
    """Convert any NTVMR page label to a clean Recto/Verso string."""
    s = raw.lower().strip().lstrip("0")   # "001r" → "1r"
    if s.endswith("r"):
        n = s[:-1]
        return "Recto" if n in ("", "1") else f"Recto {n}"
    if s.endswith("v"):
        n = s[:-1]
        return "Verso" if n in ("", "1") else f"Verso {n}"
    return raw   # fallback: return as-is

def parse_page(xml_text):
    """Return (folio_label, lines) where lines = [{'num': int, 'text': str}]."""
    # Sanitize bare & that aren't already part of an XML entity
    import re as _re
    xml_text = _re.sub(r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', xml_text)
    xml_text = strip_ns(xml_text)
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"    (skipped — malformed XML: {e})")
        return "?", []

    # Try new P75-format label extraction first (editorial note + verse refs)
    p75_label, is_recto = extract_folio_label_and_verses(root)
    if p75_label and p75_label != "?":
        folio_label = "FOLIO " + p75_label
    else:
        # Fall back to pb n attribute
        pb = root.find(".//pb")
        raw_n = pb.get("n", "?") if pb is not None else "?"
        folio_label = normalise_folio(raw_n)
        is_recto = "Recto" in folio_label

    lines = []
    current = []
    line_num = [0]

    def flush(allow_empty=False):
        if current:
            line_num[0] += 1
            lines.append({"num": line_num[0],
                           "text": " ".join(p for p in current if p)})
            current.clear()
        elif allow_empty:
            line_num[0] += 1
            lines.append({"num": line_num[0], "text": "GAP:"})

    body = root.find(".//body")
    if body is None:
        return folio_label, lines

    # Recursive walker — processes elements in document order.
    # Handles any nesting depth. Skips inside <w> (word_to_str covers it)
    # and skips inside <note> / <pb> / <cb> (non-text metadata).
    _SKIP_SUBTREE = {"w", "note", "pb", "cb", "teiHeader"}
    _SKIP_CONTENT = {"lb", "gap"}  # handled inline, no recursion needed

    def walk(elem):
        for child in elem:
            ctag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

            if ctag == "w":
                before, after = word_to_str(child)
                if after:
                    if before:
                        current.append(before + "—")
                    flush(allow_empty=False)
                    if after:
                        current.append(after)
                else:
                    if before:
                        current.append(before)
                # Do NOT recurse into <w> — word_to_str already handled children

            elif ctag == "lb":
                if child.get("break") != "no":
                    flush(allow_empty=True)
                # No recursion into lb

            elif ctag == "gap":
                flush(allow_empty=False)
                reason = child.get("reason", "")
                extent = child.get("extent", "")
                if reason == "lacuna" and extent:
                    try:
                        for _ in range(int(extent)):
                            line_num[0] += 1
                            lines.append({"num": line_num[0], "text": "GAP:"})
                    except ValueError:
                        line_num[0] += 1
                        lines.append({"num": line_num[0],
                                      "text": f"GAP: {extent} lines"})
                elif reason == "illegible":
                    line_num[0] += 1
                    lines.append({"num": line_num[0], "text": "GAP:"})
                # No recursion into gap

            elif ctag in ("note", "pb", "cb", "teiHeader"):
                pass  # Skip metadata subtrees entirely

            else:
                # div, ab, unclear, hi, etc. — recurse
                walk(child)

    walk(body)
    flush(allow_empty=False)
    return folio_label, lines


# ── TXT BUILDER ───────────────────────────────────────────────────────────────

def build_txt(args, pages_data):
    out = []
    out.append(f"# {'─' * 47}")
    out.append(f"# {args.name}  ({args.id})")
    out.append(f"# Source: NTVMR docID={args.docID}")
    out.append(f"# {'─' * 47}")
    out.append("")
    out.append("[META]")
    out.append(f"id:       {args.id}")
    out.append(f"name:     {args.name}")
    out.append(f"genre:    {args.genre}")
    out.append(f"date:     {args.date}")
    out.append(f"language: {args.language}")
    out.append(f"found:    {args.found}")
    out.append(f"held:     {args.held}")
    out.append(f"content:  {args.content}")
    out.append(f"lat:      {args.lat}")
    out.append(f"lon:      {args.lon}")
    if args.book:
        out.append(f"book:     {args.book}")
    out.append("")
    out.append("# Notation:")
    out.append("#   {word}  = nomen sacrum (rendered with overline)")
    out.append("#   [word]  = supplied / reconstructed lacuna")
    out.append("#   word—   = word continues on next line")
    out.append("#   GAP:    = line not preserved")
    out.append("")
    out.append("[GREEK]")
    out.append("")

    for folio_label, page_lines in pages_data:
        # folio_label already has "FOLIO " prefix from parse_page when using new extractor
        if folio_label.startswith("FOLIO "):
            out.append(folio_label)
        else:
            out.append(f"FOLIO {folio_label}")
        out.append("")
        # Determine r/v prefix from label: NR = recto, NV = verso
        if re.search(r'\d+R\b', folio_label):
            prefix = "r"
        elif re.search(r'\d+V\b', folio_label):
            prefix = "v"
        else:
            prefix = "r" if "Recto" in folio_label else "v"
        for ln in page_lines:
            ref = f"{prefix}.{ln['num']}"
            out.append(f"{ref:<8} {ln['text']}")
        out.append("")

    out.append("# ── TRANSLATION (optional) ──────────────────────────────────")
    out.append("# Uncomment and fill in to show an English translation in the popup.")
    out.append("# Format:  verse_ref   English text")
    out.append("#")
    out.append("# [TRANSLATION]")
    out.append("# 1:1   The book of the genealogy of ...")
    out.append("")

    return "\n".join(out)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Import a manuscript from NTVMR into ManuscriptDB"
    )
    p.add_argument("--docID",    required=True,  help="NTVMR document ID  e.g. 10001")
    p.add_argument("--id",       required=True,  help="Short label  e.g. P1")
    p.add_argument("--name",     required=True,  help="Full name  e.g. 'Papyrus 1'")
    p.add_argument("--genre",    default="new-testament",
                   help="Genre ID: new-testament | old-testament | apocrypha | …")
    p.add_argument("--date",     default="unknown", help="Estimated date  e.g. 'c. 250 CE'")
    p.add_argument("--language", default="Greek (Koiné)")
    p.add_argument("--found",    default="unknown", help="Find-site")
    p.add_argument("--held",     default="unknown", help="Current holding institution")
    p.add_argument("--content",  default="unknown", help="Text contents  e.g. 'Matt 1:1-9'")
    p.add_argument("--book",     default="",        help="Biblical book  e.g. Matthew, Mark, John")
    p.add_argument("--lat",      required=True, type=float, help="Find-site latitude")
    p.add_argument("--lon",      required=True, type=float, help="Find-site longitude")
    p.add_argument("--pages",    nargs="+", type=int, default=[10, 20],
                   help="NTVMR page IDs to fetch  (default: 10 20  = recto + verso)")
    args = p.parse_args()

    os.makedirs(MANUSCRIPTS_DIR, exist_ok=True)

    print(f"\nImporting {args.id}  (docID={args.docID})")
    pages_data = []
    for pid in args.pages:
        xml = fetch_xml(args.docID, pid)
        if xml:
            label, lns = parse_page(xml)
            if lns:
                pages_data.append((label, lns))
                print(f"    >> {label}: {len(lns)} lines parsed")

    if not pages_data:
        print("\nNo data found. Check --docID and --pages.")
        return

    content = build_txt(args, pages_data)
    out_path = os.path.join(MANUSCRIPTS_DIR, f"{args.id}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\nDone. Written to {out_path}")


if __name__ == "__main__":
    main()

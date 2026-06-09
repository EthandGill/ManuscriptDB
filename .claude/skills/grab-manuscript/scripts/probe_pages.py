"""
probe_pages.py — Discover all valid NTVMR page IDs for a manuscript.

Usage:
    python probe_pages.py <docID> [--max 400] [--skip 230]

Outputs one line per valid page:
    pageID=10  folio=F1R  words=46  verses=1 Corinthians 1:17,1 Corinthians 1:18
"""
import ssl, urllib.request, re, sys, time, argparse
import xml.etree.ElementTree as ET

_SSL = ssl.create_default_context()
_SSL.check_hostname = False
_SSL.verify_mode = ssl.CERT_NONE

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

def strip_ns(t):
    return re.sub(r'\s*xmlns(?::[^=]*)?\s*=\s*"[^"]*"', '', t)

def probe(doc_id, pid, retries=3):
    url = ("https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           "?docID={}&pageID={}&format=xml".format(doc_id, pid))
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=20, context=_SSL) as r:
                data = r.read().decode('utf-8')
            if '<error' in data:
                return None
            if not re.search(r'<w[ >]', data):
                return None
            # Parse for folio note and verse refs
            clean = re.sub(r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#[0-9]+|#x[0-9a-fA-F]+);)',
                           '&amp;', strip_ns(data))
            root = ET.fromstring(clean)
            folio = '-'
            for note in root.iter('note'):
                if note.get('type') == 'editorial':
                    t = ''.join(note.itertext()).strip()
                    m = re.search(r'F(\d+[rv])', t, re.I)
                    if m:
                        folio = 'F' + m.group(1).upper()
                        break
            verses = []
            for ab in root.iter('ab'):
                n = ab.get('n', '')
                m = re.match(r'(B\d+)K(\d+)V(\d+)', n)
                if m:
                    ref = "{} {}:{}".format(
                        BOOK_MAP.get(m.group(1), m.group(1)),
                        m.group(2), m.group(3))
                    if ref not in verses:
                        verses.append(ref)
            wcount = len(re.findall(r'<w[ >]', data))
            return {'pid': pid, 'folio': folio, 'words': wcount, 'verses': verses}
        except Exception:
            if i < retries - 1:
                time.sleep(2)
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('docID', type=int)
    ap.add_argument('--max', type=int, default=400)
    ap.add_argument('--skip', type=int, nargs='*', default=[])
    args = ap.parse_args()

    found = []
    for pid in range(1, args.max + 1):
        if pid in args.skip:
            continue
        result = probe(args.docID, pid)
        if result:
            found.append(result)
            verse_str = ','.join(result['verses'][:3])
            print("pageID={:<4} folio={:<6} words={:<3} verses={}".format(
                result['pid'], result['folio'], result['words'], verse_str))
            sys.stdout.flush()

    # Print summary line for easy parsing
    page_ids = [r['pid'] for r in found]
    print("FOUND_PAGES:" + ','.join(str(p) for p in page_ids))

if __name__ == '__main__':
    main()

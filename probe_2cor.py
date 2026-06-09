"""Probe NTVMR for P117 (docID=10117) and P124 (docID=10124) page IDs and content."""
import ssl, urllib.request, re, sys, time
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

BOOK_MAP = {
    'B01':'Matthew','B02':'Mark','B03':'Luke','B04':'John','B05':'Acts',
    'B06':'Romans','B07':'1 Corinthians','B08':'2 Corinthians',
    'B09':'Galatians','B10':'Ephesians','B11':'Philippians',
    'B12':'Colossians','B13':'1 Thessalonians','B14':'2 Thessalonians',
    'B15':'1 Timothy','B16':'2 Timothy','B17':'Titus','B18':'Philemon',
    'B19':'Hebrews','B20':'James','B21':'1 Peter','B22':'2 Peter',
    'B23':'1 John','B24':'2 John','B25':'3 John','B26':'Jude','B27':'Revelation',
}

def decode_ab(n):
    m = re.match(r'(B\d+)K(\d+)V(\d+)', n)
    if not m: return None
    return "{} {}:{}".format(BOOK_MAP.get(m.group(1), m.group(1)), m.group(2), m.group(3))

def strip_ns(t):
    return re.sub(r'\s*xmlns(?::[^=]*)?\s*=\s*"[^"]*"', '', t)

def probe(doc_id, pid, retries=3):
    url = ("https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           "?docID={}&pageID={}&format=xml".format(doc_id, pid))
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=20, context=_SSL_CTX) as r:
                data = r.read().decode('utf-8')
            if re.search(r'<error', data): return False, '', [], 0
            has_w = bool(re.search(r'<w[ >]', data))
            if not has_w: return False, '', [], 0
            # Extract folio note and verses
            clean = strip_ns(data)
            root = ET.fromstring(re.sub(r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', clean))
            folio = '-'
            for note in root.iter('note'):
                if note.get('type') == 'editorial':
                    t = ''.join(note.itertext()).strip()
                    m = re.search(r'F(\d+[rv])', t, re.I)
                    if m: folio = 'F{}'.format(m.group(1).upper()); break
            verses = []
            for ab in root.iter('ab'):
                ref = decode_ab(ab.get('n',''))
                if ref and ref not in verses: verses.append(ref)
            wcount = len(re.findall(r'<w[ >]', data))
            return True, folio, verses, wcount
        except:
            if i < retries-1: time.sleep(2)
    return False, '', [], 0

for doc_id, label in [(10117, 'P117'), (10124, 'P124')]:
    print("=== {} (docID={}) ===".format(label, doc_id))
    found = []
    for pid in range(1, 401):
        ok, folio, verses, wcount = probe(doc_id, pid)
        if ok:
            found.append(pid)
            verse_str = ', '.join(verses[:3])
            print("  pageID={:<4} folio={:<6} words={:<3} {}".format(
                pid, folio, wcount, verse_str[:60]))
            sys.stdout.flush()
    print("  FOUND: {}\n".format(found))

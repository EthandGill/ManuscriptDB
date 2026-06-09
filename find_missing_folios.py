"""
Targeted probe for missing P11 folios: 1R, 3V, 7R, 8R, 10V, 12V, 15V, 18V.
Also inspects why some pages parse 0 lines.
"""
import ssl, urllib.request, re, sys, time
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

BOOK_MAP = {
    'B01':'Matthew','B02':'Mark','B03':'Luke','B04':'John','B05':'Acts',
    'B06':'Romans','B07':'1 Corinthians','B08':'2 Corinthians',
}

def decode_ab(n):
    m = re.match(r'(B\d+)K(\d+)V(\d+)', n)
    if not m: return None
    return "{} {}:{}".format(BOOK_MAP.get(m.group(1), m.group(1)), m.group(2), m.group(3))

def fetch(pid, retries=3):
    url = ("https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           "?docID=10011&pageID={}&format=xml".format(pid))
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=20, context=_SSL_CTX) as r:
                return r.read().decode('utf-8')
        except Exception as e:
            if i < retries-1: time.sleep(2)
    return None

def analyse(pid, data):
    data = re.sub(r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', data)
    clean = re.sub(r'\s*xmlns(?::[^=]*)?\s*=\s*"[^"]*"', '', data)
    try:
        root = ET.fromstring(clean)
    except ET.ParseError as e:
        print("  pageID={} PARSE ERROR: {}".format(pid, e))
        return

    # Error element?
    err = root.find('.//error')
    if err is not None:
        print("  pageID={} NO TRANSCRIPTION".format(pid))
        return

    # Folio note
    folio = '-'
    for note in root.iter('note'):
        if note.get('type') == 'editorial':
            t = ''.join(note.itertext()).strip()
            m = re.search(r'F(\d+)(r|v)', t, re.I)
            if m:
                folio = 'F{}{}'.format(m.group(1), m.group(2).upper())
                break

    # Verses
    verses = []
    for ab in root.iter('ab'):
        ref = decode_ab(ab.get('n',''))
        if ref and ref not in verses:
            verses.append(ref)

    # Words
    words = [(''.join(w.itertext()).strip()) for w in root.iter('w')]
    words = [w for w in words if w]

    verse_str = ', '.join(verses[:3]) if verses else '-'
    snippet = ' '.join(words[:6])
    print("  pageID={:<4} folio={:<6} words={:<3} verses={:<40} text={}".format(
        pid, folio, len(words), verse_str[:39], snippet[:40]))

# ── Ranges to probe ────────────────────────────────────────────────────────────
# F1r  → around pageID 1-19 (F1v=20)
# F3v  → between pageID 21 (F2r) and 31 (F4r)
# F7r,F8r,F8v → between 81 (F6v) and 90 (F9r): IDs 82-89
# F10v → pageID 120 (known but 0 lines — inspect body)
# F12v → between 150 (F12r) and 170 (F13r): IDs 151-169
# F15v → between 210 (F15r) and 240 (F16v): IDs 211-239
# F18v → pageID 300 (already in file — confirm)

ranges = (
    list(range(1, 20)) +          # F1r search
    list(range(22, 31)) +          # F3v search (between F2r=21 and F4r=31)
    list(range(82, 90)) +          # F7r/F8r search
    [120] +                        # F10v re-inspect
    list(range(151, 170)) +        # F12v search
    list(range(211, 240)) +        # F15v search
    [300]                          # F18v confirm
)

print("Probing {} page IDs for missing P11 folios...\n".format(len(ranges)))

for pid in ranges:
    data = fetch(pid)
    if data is None:
        print("  pageID={:<4} FAILED (no response)".format(pid))
    else:
        analyse(pid, data)
    sys.stdout.flush()

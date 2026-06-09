"""
Fetch all P11 pages, extract:
  - editorial-note folio label (e.g. "F19v = frg. XVI")
  - verse range from <ab n="B07K7V10"> etc.
  - word count / text snippet
"""
import ssl, urllib.request, re, sys, time
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

PAGE_IDS = [10,20,21,22,30,31,40,41,50,60,70,80,81,82,83,90,100,110,120,130,
            140,150,160,170,180,192,200,210,230,240,270,290,300,310,320]

# NT book number -> name (NTVMR uses B01=Matt, B02=Mark, ... B07=1Cor, B08=2Cor)
BOOK_MAP = {
    'B01':'Matthew','B02':'Mark','B03':'Luke','B04':'John','B05':'Acts',
    'B06':'Romans','B07':'1 Corinthians','B08':'2 Corinthians',
    'B09':'Galatians','B10':'Ephesians','B11':'Philippians',
    'B12':'Colossians','B13':'1 Thessalonians','B14':'2 Thessalonians',
    'B15':'1 Timothy','B16':'2 Timothy','B17':'Titus','B18':'Philemon',
    'B19':'Hebrews','B20':'James','B21':'1 Peter','B22':'2 Peter',
    'B23':'1 John','B24':'2 John','B25':'3 John','B26':'Jude','B27':'Revelation',
}

def strip_ns(xml_text):
    return re.sub(r'\s*xmlns(?::[^=]*)?\s*=\s*"[^"]*"', '', xml_text)

def decode_ab_n(n):
    """'B07K7V10' -> '1 Corinthians 7:10'"""
    m = re.match(r'(B\d+)K(\d+)V(\d+)', n)
    if not m:
        return n
    book = BOOK_MAP.get(m.group(1), m.group(1))
    return "{} {}:{}".format(book, m.group(2), m.group(3))

def fetch_page(page_id, retries=3):
    url = ("https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           "?docID=10011&pageID={}&format=xml".format(page_id))
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=20, context=_SSL_CTX) as r:
                return r.read().decode('utf-8')
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
    return None

def parse_page(data):
    data = re.sub(r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', data)
    data = strip_ns(data)
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return None

    # Check for error element
    err = root.find('.//error')
    if err is not None:
        return None

    # Editorial note folio label
    notes = []
    for note in root.iter('note'):
        if note.get('type') == 'editorial':
            t = ''.join(note.itertext()).strip()
            if t:
                notes.append(t)

    # Verse refs from <ab n="B07K7V10">
    verses = []
    for ab in root.iter('ab'):
        n = ab.get('n', '')
        if re.match(r'B\d+K\d+V\d+', n):
            verses.append(decode_ab_n(n))

    # Words
    words = []
    for w in root.iter('w'):
        t = ''.join(w.itertext()).strip()
        if t:
            words.append(t)

    return {
        'notes': notes,
        'verses': verses,
        'words': words,
    }

print("{:<8} {:<25} {:<45} {:>5}  {}".format(
    "pageID", "folio note", "verse range", "wds", "first words"))
print("-" * 130)

for pid in PAGE_IDS:
    data = fetch_page(pid)
    if data is None:
        print("{:<8} FAILED (no response)".format(pid))
        sys.stdout.flush()
        continue

    result = parse_page(data)
    if result is None:
        print("{:<8} NO TRANSCRIPTION".format(pid))
        sys.stdout.flush()
        continue

    note_str = '; '.join(result['notes']) if result['notes'] else '-'
    verse_str = ', '.join(result['verses']) if result['verses'] else '-'
    snippet = ' '.join(result['words'][:8])
    print("{:<8} {:<25} {:<45} {:>5}  {}".format(
        pid, note_str[:24], verse_str[:44], len(result['words']), snippet[:50]))
    sys.stdout.flush()

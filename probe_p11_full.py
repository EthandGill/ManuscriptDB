"""
Fetch every valid page for P11 (docID=10011) and show:
  - the actual <pb n="..."> folio label
  - first few words of text content
  - line count
"""
import ssl, urllib.request, re, sys
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

PAGE_IDS = [10,20,21,22,30,31,40,41,50,60,70,80,81,82,83,90,100,110,120,130,
            140,150,160,170,180,192,200,210,230,240,270,290,300,310,320]

def strip_ns(xml_text):
    return re.sub(r'\s*xmlns(?::[^=]*)?\s*=\s*"[^"]*"', '', xml_text)

def get_page_info(page_id):
    url = ("https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           "?docID=10011&pageID={}&format=xml".format(page_id))
    try:
        with urllib.request.urlopen(url, timeout=20, context=_SSL_CTX) as r:
            raw = r.read().decode('utf-8')
    except Exception as e:
        return None, None, None

    raw = re.sub(r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', raw)
    clean = strip_ns(raw)

    try:
        root = ET.fromstring(clean)
    except ET.ParseError as e:
        return '(parse error)', str(e)[:60], 0

    # Find pb element and its n attribute
    pb = root.find('.//pb')
    folio_n = pb.get('n', '?') if pb is not None else '?'

    # Collect all word text
    words = []
    for w in root.iter('w'):
        t = ''.join(w.itertext()).strip()
        if t:
            words.append(t)

    snippet = ' '.join(words[:12])
    return folio_n, snippet, len(words)

print("{:<8} {:<15} {:>6}  {}".format("pageID", "folio_n", "words", "first words"))
print("-" * 100)
for pid in PAGE_IDS:
    folio_n, snippet, wcount = get_page_info(pid)
    if folio_n is not None:
        print("{:<8} {:<15} {:>6}  {}".format(pid, folio_n, wcount, snippet))
    sys.stdout.flush()

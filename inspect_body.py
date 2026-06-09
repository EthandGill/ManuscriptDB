"""Inspect the body XML of pages that have words but parse 0 lines."""
import ssl, urllib.request, re, sys, time
sys.stdout.reconfigure(encoding='utf-8')

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

def fetch(pid, retries=3):
    url = ("https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           "?docID=10011&pageID={}&format=xml".format(pid))
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=20, context=_SSL_CTX) as r:
                return r.read().decode('utf-8')
        except:
            if i < retries-1: time.sleep(2)
    return None

# Inspect body of pages that have words but produce 0 parse lines
for pid in [10, 22, 82, 83, 120, 160]:
    data = fetch(pid)
    if not data:
        print("pageID={} FAILED".format(pid)); continue
    # Extract body section
    body_m = re.search(r'<body>(.*?)</body>', data, re.DOTALL)
    if body_m:
        body = body_m.group(0)
        print("=== pageID={} BODY (first 1200 chars) ===".format(pid))
        print(body[:1200])
    else:
        print("=== pageID={} NO <body> TAG ===".format(pid))
        print(data[500:1200])
    print()

# Also probe 401-600 for F15V
print("\n=== Probing 401-600 for F15V ===")
for pid in range(401, 601, 5):
    data = fetch(pid)
    if data:
        has_w = bool(re.search(r'<w[ >]', data))
        if has_w:
            # Get verses
            verses = re.findall(r'<ab[^>]+n="(B\d+K\d+V\d+)"', data)
            notes = re.findall(r'F(\d+[rv])', data, re.I)
            print("  pageID={} words=YES  folio_hints={}  verse_hints={}".format(
                pid, notes[:3], verses[:3]))
            sys.stdout.flush()

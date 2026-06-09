"""Dense retry probe for F15V — every integer 211-260 with multiple retries."""
import ssl, urllib.request, re, sys, time
sys.stdout.reconfigure(encoding='utf-8')

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

def probe(pid, retries=4):
    url = ("https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           "?docID=10011&pageID={}&format=xml".format(pid))
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=20, context=_SSL_CTX) as r:
                data = r.read().decode('utf-8')
            has_w = bool(re.search(r'<w[ >]', data))
            has_err = bool(re.search(r'<error', data))
            if has_w and not has_err:
                verses = re.findall(r'<ab[^>]+n="(B\d+K\d+V\d+)"', data)
                notes = re.findall(r'F(\d+[rv])', data, re.I)
                wcount = len(re.findall(r'<w[ >]', data))
                return True, notes, verses, wcount
            return False, [], [], 0
        except Exception as e:
            if i < retries-1:
                time.sleep(2)
    return False, [], [], 0

print("Dense probe 211-260 with retries for P11 F15V...")
found = []
for pid in range(211, 261):
    ok, notes, verses, wcount = probe(pid)
    status = "FOUND words={} folio={} verses={}".format(wcount, notes, verses[:2]) if ok else "."
    if ok:
        print("  pageID={} {}".format(pid, status))
        found.append(pid)
    sys.stdout.flush()

print()
if found:
    print("Found pages: {}".format(found))
else:
    print("F15V not found in 211-260. It may not have a transcription in NTVMR API.")

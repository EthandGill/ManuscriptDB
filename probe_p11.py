import ssl, urllib.request, re, sys, time
sys.stdout.reconfigure(encoding='utf-8')

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

def probe(page_id):
    url = ("https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           "?docID=10011&pageID={}&format=xml".format(page_id))
    try:
        with urllib.request.urlopen(url, timeout=15, context=_SSL_CTX) as r:
            data = r.read().decode('utf-8')
        has_w = bool(re.search(r'<w[ >]', data))
        has_ab = bool(re.search(r'<ab[ >]', data))
        if has_w or has_ab:
            pb = re.search(r'n="([^"]+)"', data)
            label = pb.group(1) if pb else '?'
            words = len(re.findall(r'<w[ >]', data))
            return True, label, words, data
        return False, '', 0, ''
    except Exception as e:
        return False, '', 0, ''

found = []
for pid in range(1, 401):
    ok, label, words, data = probe(pid)
    if ok:
        found.append((pid, label, words))
        print("  pageID={:4d}  label={:<12}  words={}".format(pid, label, words))
        sys.stdout.flush()

print()
print("Total pages found: {}".format(len(found)))
print("Page IDs: {}".format([p for p,l,w in found]))

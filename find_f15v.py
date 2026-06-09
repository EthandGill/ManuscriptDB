"""Probe page IDs 400-1200 for P11 F15V."""
import ssl, urllib.request, re, sys, time
sys.stdout.reconfigure(encoding='utf-8')

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

def probe(pid):
    url = ("https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           "?docID=10011&pageID={}&format=xml".format(pid))
    try:
        with urllib.request.urlopen(url, timeout=15, context=_SSL_CTX) as r:
            data = r.read().decode('utf-8')
        has_w = bool(re.search(r'<w[ >]', data))
        if has_w:
            verses = re.findall(r'<ab[^>]+n="(B\d+K\d+V\d+)"', data)
            notes = re.findall(r'F(\d+[rv])', data, re.I)
            wcount = len(re.findall(r'<w[ >]', data))
            return True, notes, verses, wcount
        return False, [], [], 0
    except:
        return False, [], [], 0

print("Probing 400-1200 for P11 F15V...")
for pid in range(400, 1201, 10):
    ok, notes, verses, wcount = probe(pid)
    if ok:
        print("  pageID={} folio_hints={} verse_hints={} words={}".format(
            pid, notes[:3], verses[:3], wcount))
        sys.stdout.flush()
print("Done.")

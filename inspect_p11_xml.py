"""Show raw XML snippet for a few P11 pages to understand label structure."""
import ssl, urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

def fetch(page_id):
    url = ("https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/"
           "?docID=10011&pageID={}&format=xml".format(page_id))
    try:
        with urllib.request.urlopen(url, timeout=20, context=_SSL_CTX) as r:
            return r.read().decode('utf-8')
    except Exception as e:
        return "(failed: {})".format(e)

# Sample a few pages that previously had different labels
for pid in [10, 240, 250, 270, 290, 310, 320]:
    data = fetch(pid)
    # Print first 600 chars to see structure
    print("=== pageID={} ===".format(pid))
    print(data[:800])
    print()

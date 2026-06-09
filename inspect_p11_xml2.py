"""Show full XML for page 240 to find the pb/folio label."""
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

for pid in [240, 270, 310]:
    data = fetch(pid)
    if not data.startswith('(failed'):
        # Print the body section which should contain pb and text
        body_match = re.search(r'<body>.*?</body>', data, re.DOTALL)
        if body_match:
            print("=== pageID={} BODY ===".format(pid))
            print(body_match.group(0)[:2000])
        else:
            # Print from teiHeader end onwards
            print("=== pageID={} (no body tag found) ===".format(pid))
            # Find any tag with type=folio or containing recto/verso
            for m in re.finditer(r'<[^>]+(recto|verso|folio|leaf|page)[^>]*>', data, re.I):
                print("TAG:", m.group(0))
            # Print all n= attributes
            for m in re.finditer(r'<(\w+)[^>]+n="([^"]+)"', data):
                print("  <{}> n={}".format(m.group(1), m.group(2)))
            print(data[400:1500])
    print()

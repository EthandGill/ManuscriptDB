"""Fetch F1V (pg20), F4V (pg41), F6R (pg70) with heavy retries and print parsed lines."""
import ssl, urllib.request, re, sys, time
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

def strip_ns(t):
    return re.sub(r'\s*xmlns(?::[^=]*)?\s*=\s*"[^"]*"', '', t)

def all_text(node):
    return ''.join(node.itertext()).strip()

def word_to_str(w):
    before, after, past = [], [], False
    if w.text and w.text.strip():
        before.append(w.text.strip())
    for child in w:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag == 'lb' and child.get('break') == 'no':
            past = True
            if child.tail and child.tail.strip():
                after.append(child.tail.strip())
            continue
        if tag == 'abbr':
            chunk = '{' + all_text(child) + '}'
        elif tag == 'supplied':
            nom = child.find(".//abbr[@type='nomSac']")
            chunk = '{' + all_text(nom) + '}' if nom else '[' + all_text(child) + ']'
        else:
            chunk = all_text(child)
        (after if past else before).append(chunk)
        if child.tail and child.tail.strip():
            (after if past else before).append(child.tail.strip())
    return ''.join(before).strip(), ''.join(after).strip()

def parse(xml_text):
    xml_text = re.sub(r'&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', xml_text)
    root = ET.fromstring(strip_ns(xml_text))
    body = root.find('.//body')
    if body is None:
        return []
    lines, current, lnum = [], [], [0]
    def flush(empty=False):
        if current:
            lnum[0] += 1
            lines.append({'num': lnum[0], 'text': ' '.join(p for p in current if p)})
            current.clear()
        elif empty:
            lnum[0] += 1
            lines.append({'num': lnum[0], 'text': 'GAP:'})
    def walk(e):
        for c in e:
            t = c.tag.split('}')[-1] if '}' in c.tag else c.tag
            if t == 'w':
                b, a = word_to_str(c)
                if a:
                    if b: current.append(b + '—')
                    flush(False)
                    if a: current.append(a)
                elif b:
                    current.append(b)
            elif t == 'lb':
                if c.get('break') != 'no': flush(True)
            elif t == 'gap':
                flush(False)
                r, ex = c.get('reason',''), c.get('extent','')
                if r == 'lacuna' and ex:
                    try:
                        for _ in range(int(ex)):
                            lnum[0] += 1; lines.append({'num': lnum[0], 'text': 'GAP:'})
                    except: pass
                elif r == 'illegible':
                    lnum[0] += 1; lines.append({'num': lnum[0], 'text': 'GAP:'})
            elif t not in ('note', 'pb', 'cb', 'teiHeader'):
                walk(c)
    walk(body)
    flush(False)
    return lines

def fetch(pid, retries=6):
    url = 'https://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/?docID=10011&pageID={}&format=xml'.format(pid)
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=20, context=_SSL_CTX) as r:
                return r.read().decode('utf-8')
        except:
            if i < retries-1: time.sleep(3)
    return None

TARGETS = [
    (20, '1V', '1 Corinthians 1:20-22', 'v'),
    (41, '4V', '1 Corinthians 2:11-12', 'v'),
    (70, '6R', '1 Corinthians 3:2-3',   'r'),
]

for pid, folio, verses, prefix in TARGETS:
    print('=== Fetching page {} ({}) ==='.format(pid, folio))
    data = fetch(pid)
    if not data:
        print('FAILED'); continue
    lines = parse(data)
    if not lines:
        print('0 lines parsed'); continue
    print('FOLIO {} — {}'.format(folio, verses))
    print()
    for ln in lines:
        ref = '{}.{}'.format(prefix, ln['num'])
        print('{:<8} {}'.format(ref, ln['text']))
    print()

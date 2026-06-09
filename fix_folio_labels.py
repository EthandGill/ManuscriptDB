"""
Fix all invented NR/NV folio numbers across every manuscript imported this session.
Rule: if NTVMR gave no real folio label (pb n="0"), use Recto/Verso/Recto 2/Verso 2...
      not invented "1R", "2V" etc.
"""
import re, sys, os
sys.stdout.reconfigure(encoding='utf-8')
DIR = r'C:\ManuscriptDB\manuscripts'

def fix(name):
    path = os.path.join(DIR, name + '.txt')
    with open(path, encoding='utf-8') as f:
        txt = f.read()

    # Build a sequential Recto/Verso sequence for replacing NR/NV labels
    # Pattern: "FOLIO 1R — ...", "FOLIO 2V — ..." etc.
    def seq_label(n, is_r):
        if n == 1:
            return 'Recto' if is_r else 'Verso'
        return f'Recto {n}' if is_r else f'Verso {n}'

    # Find all invented NR/NV headers in order
    pattern = re.compile(r'^FOLIO (\d+)([RV]) — (.+)$', re.MULTILINE)
    matches = list(pattern.finditer(txt))
    if not matches:
        return  # nothing to fix

    # Replace each one with the correct Recto/Verso label
    # Process in reverse order so positions don't shift
    for m in reversed(matches):
        n = int(m.group(1))
        is_r = m.group(2) == 'R'
        verse = m.group(3)
        new_label = f'FOLIO {seq_label(n, is_r)} — {verse}'
        txt = txt[:m.start()] + new_label + txt[m.end():]

    # Fix line prefixes: Recto blocks get r., Verso blocks get v.
    def fix_recto(m):
        return re.sub(r'^v\.(\d+)', r'r.\1', m.group(0), flags=re.MULTILINE)
    def fix_verso(m):
        return re.sub(r'^r\.(\d+)', r'v.\1', m.group(0), flags=re.MULTILINE)

    txt = re.sub(r'^(FOLIO Recto(?: \d+)? — .+?)(?=^FOLIO |\Z)',
                 fix_recto, txt, flags=re.MULTILINE | re.DOTALL)
    txt = re.sub(r'^(FOLIO Verso(?: \d+)? — .+?)(?=^FOLIO |\Z)',
                 fix_verso, txt, flags=re.MULTILINE | re.DOTALL)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(txt)

    # Report new folio headers
    headers = [l.rstrip() for l in txt.splitlines() if l.startswith('FOLIO')]
    print(f'{name}: {headers}')

# All manuscripts imported this session with invented numbers
for ms in [
    # Hebrews batch
    'P12', 'P13', 'P17', 'P79', 'P89', 'P114', 'P116', 'P126',
    # Pauline batch
    'P51', 'P49', 'P92', 'P132', 'P16', 'P30', 'P65', 'P133',
    'P32', 'P87', 'P139',
    # 2 Corinthians
    'P117', 'P124',
    # 1 Corinthians (from earlier — these used old format, skip if already clean)
    'P15', 'P34', 'P68', 'P123',
]:
    try:
        fix(ms)
    except FileNotFoundError:
        print(f'{ms}: not found, skipping')

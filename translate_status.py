#!/usr/bin/env python3
"""
translate_status.py — how many manuscripts still need translating?

Scans manuscripts/*.txt and reports translated vs untranslated, how many of the
untranslated ones have a free HGV-English head-start, and roughly how many Greek
lines are left (a proxy for remaining token cost). Offline, instant, no tokens.

  py translate_status.py
"""
import os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
MSS = os.path.join(HERE, "manuscripts")

content_re = re.compile(r"^\s*\S+\s+\S")      # "<ref>  <text>"  -> a filled slot
empty_re   = re.compile(r"^\s*\d+\s*$")        # "5     "          -> an empty slot

total = translated = untranslated = with_hgv = lines_left = 0

for f in glob.glob(os.path.join(MSS, "*.txt")):
    in_tr = has_tr = has_hgv = False
    empties = 0
    for ln in open(f, encoding="utf-8"):
        st = ln.strip()
        if st.startswith("[TRANSLATION"):
            in_tr = True
            continue
        if st.startswith("[") and st.endswith("]"):
            in_tr = False
        if "# hgv-en" in st.lower():
            has_hgv = True
        if in_tr:
            if st.startswith("#"):
                continue
            if content_re.match(ln):
                has_tr = True
            elif empty_re.match(ln):
                empties += 1
    total += 1
    if has_tr:
        translated += 1
    else:
        untranslated += 1
        lines_left += empties
        if has_hgv:
            with_hgv += 1

print(f"Total manuscripts:        {total}")
print(f"Translated:               {translated}")
print(f"Left to translate:        {untranslated}")
print(f"  ...with free HGV-EN:     {with_hgv}  (cheap — reformat, not translate)")
print(f"  ...need full translation:{untranslated - with_hgv}")
print(f"Approx Greek lines left:  {lines_left}  (rough proxy for remaining cost)")

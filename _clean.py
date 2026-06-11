"""Shared cleaner for the o.wilck sweep JSON — used by _dump.py and _build.py."""
import re
GREEK = r'Ͱ-Ͽἀ-῿'

def clean(lines):
    out = []
    for l in lines:
        if '|' in l:                          # metadata table row (Title | …, Subjects | …)
            continue
        s = l.strip()
        if re.match(r'^\d+\\?\.', s):          # numbered apparatus "2. l. …" / "5\. corr. …"
            continue
        if s[:1] in '.-':                      # dot/dash-led apparatus
            continue
        if ('prev. ed' in s or 'papyrus' in s or ' l. ' in s or s.startswith('l.')
                or 'BL ' in s or 'corr.' in s):
            continue
        # English editorial commentary that happens to contain Greek glyphs
        if re.match(r'^[A-Za-z]', s) or 'stigma' in s or 'construed' in s or 'the image' in s:
            continue
        if ('www.' in s or 'trismegistos' in s or 'ghostname' in s or 'paroxytone' in s
                or 'appears now' in s or 'prev.' in s):
            continue
        if s.startswith('=>') or '<#' in s or '#>' in s or 'monogr' in s:
            continue
        if 'gratia' in s or 'serves as' in s or 'variation' in s or 'KorrTyche' in s:
            continue
        c = re.sub(r'⟦[^⟧]*⟧', '', l)          # scribal deletions
        c = c.replace('⟦', '').replace('⟧', '')
        c = c.replace('\\', '').replace('/', '')   # interlinear markers
        c = re.sub(r'\(\([^)]*\)\)', '', c)    # ((editorial notes))
        c = re.sub(r'^\s*\d+', '', c)          # leading every-5 line number merged onto text
        c = c.replace('Traces', '…')           # illegible traces
        c = re.sub(r'\s+', ' ', c).strip()
        if re.search('[' + GREEK + ']', c):
            out.append(c)
    return out

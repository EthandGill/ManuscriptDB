"""Fix FOLIO labels, line prefixes, and add translations for P117 and P124."""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

def fix_file(path, folio1_label, folio2_label, translation_block):
    with open(path, encoding='utf-8') as f:
        txt = f.read()

    # Split into sections around the two FOLIO blocks
    # Fix folio 1 label (recto)
    txt = txt.replace('FOLIO ? — ' + folio1_label.split(' — ')[1],
                      folio1_label, 1)
    # Fix folio 2 label (verso)
    txt = txt.replace('FOLIO ? — ' + folio2_label.split(' — ')[1],
                      folio2_label, 1)

    # Fix v. → r. for lines that belong to the recto folio only
    # The recto block is between the first FOLIO header and the second FOLIO header
    parts = re.split(r'(?=^FOLIO \d+[RV])', txt, flags=re.MULTILINE)
    fixed_parts = []
    for part in parts:
        # If this part starts with the recto folio header, fix v. to r.
        if part.startswith(folio1_label):
            part = re.sub(r'^v\.(\d+)', r'r.\1', part, flags=re.MULTILINE)
        fixed_parts.append(part)
    txt = ''.join(fixed_parts)

    # Replace translation placeholder
    old = ('# ── TRANSLATION (optional) ──────────────────────────────────\n'
           '# Uncomment and fill in to show an English translation in the popup.\n'
           '# Format:  verse_ref   English text\n'
           '#\n'
           '# [TRANSLATION]\n'
           '# 1:1   The book of the genealogy of ...')
    txt = txt.replace(old, translation_block.strip())

    with open(path, 'w', encoding='utf-8') as f:
        f.write(txt)
    print('Done: {}'.format(path))


# ── P117 ─────────────────────────────────────────────────────────────────────
fix_file(
    r'C:\ManuscriptDB\manuscripts\P117.txt',
    folio1_label='FOLIO 1R — 2 Corinthians 7:6-8',
    folio2_label='FOLIO 1V — 2 Corinthians 7:9-11',
    translation_block="""[TRANSLATION]
7:6    But God, who comforts the downcast, comforted us by the coming of Titus,
7:7    and not only by his coming but also by the comfort with which he was comforted by you, as he told us of your longing, your mourning, your zeal for me, so that I rejoiced still more.
7:8    For even if I made you grieve with my letter, I do not regret it — though I did regret it, for I see that that letter grieved you, though only for a while.
7:9    As it is, I rejoice, not because you were grieved, but because you were grieved into repenting. For you felt a godly grief, so that you suffered no loss through us.
7:10   For godly grief produces a repentance that leads to salvation without regret, whereas worldly grief produces death.
7:11   For see what earnestness this godly grief has produced in you, but also what eagerness to clear yourselves, what indignation, what fear, what longing, what zeal, what punishment!
"""
)

# ── P124 ─────────────────────────────────────────────────────────────────────
fix_file(
    r'C:\ManuscriptDB\manuscripts\P124.txt',
    folio1_label='FOLIO 1R — 2 Corinthians 11:1-4',
    folio2_label='FOLIO 1V — 2 Corinthians 11:6-9',
    translation_block="""[TRANSLATION]
11:1   I wish you would bear with me in a little foolishness. Do bear with me!
11:2   For I feel a divine jealousy for you, since I betrothed you to one husband, to present you as a pure virgin to Christ.
11:3   But I am afraid that as the serpent deceived Eve by his cunning, your thoughts will be led astray from a sincere and pure devotion to Christ.
11:4   For if someone comes and proclaims another Jesus than the one we proclaimed, or if you receive a different spirit from the one you received, or if you accept a different gospel from the one you accepted, you put up with it readily enough.
11:6   Even if I am unskilled in speaking, I am not so in knowledge; indeed, in every way we have made this plain to you in all things.
11:7   Or did I commit a sin in humbling myself so that you might be exalted, because I preached God's gospel to you free of charge?
11:8   I robbed other churches by accepting support from them in order to serve you.
11:9   And when I was with you and was in need, I did not burden anyone, for the brothers who came from Macedonia supplied my need. So I refrained and will refrain from burdening you in any way.
"""
)

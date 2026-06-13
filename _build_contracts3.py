#!/usr/bin/env python3
"""Build clean loan contracts: BGU 3.800, BGU 4.1133, BGU 4.1152."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    # remove the whole directional-isolate filler span (vac./ca.? markers) as a unit
    l = re.sub(r'⁦[^⁩]*⁩', ' ', l)
    l = re.sub(r'[⁦⁧⁨⁩]', '', l)          # any stray isolate marks
    l = re.sub(r'\bvac\.?\b', ' ', l)
    return re.sub(r'\s+', ' ', l).strip()

SRC = {'bgu;3;800': '_PENDING_bgu3_800-849.json',
       'bgu;4;1133': '_PENDING_bgu4_1100-1150.json',
       'bgu;4;1152': '_PENDING_bgu4_1151-1200.json'}

ITEMS = [
 dict(key='bgu;3;800', nlines=25, slug='bgu_3_800',
      name='Loan note - 100 drachmas and five artabas of wheat (double copy)',
      date='30 Jan 158 CE', found='Arsinoite nome, Fayum, Egypt', lat=29.3084, lon=30.8428,
      content='Sotas son of Papeis and Sotas alias Tryphon acknowledge a loan of 100 drachmas and 5 artabas of wheat from Onnophris, repayable in Pauni; written twice',
      trans=[
        "Sotas son of Papeis and Sotas also called",
        "Tryphon, to Onnophris son of Pakysis,",
        "gree(ting). We acknowledge by this",
        "written bond that we have from",
        "you [a hund]red [si]l[ve]r drachmas",
        "[an]d fiv[e] artab[a]s of whe[a]t, total 100 dr.",
        "(and) 5 (art. of wheat), which we will also repay in the month",
        "Pauni of the present twenty-",
        "first [an]d year",
        "of [Antoni]nus Caesar t[he lord],",
        "Mecheir 5. I, So[ta]s also called T[r]yphon, will jointly",
        "repay as aforesaid.",
        "Sotas son of Papei[s] and Sotas also called",
        "Tryphon, to Onnophris son of Pakysis,",
        "gree(ting). We acknowledge by",
        "this written bond that we have",
        "from you a hundr[ed] silver drachmas",
        "and five artabas of wheat - five,",
        "total 100 dr. (and) 5 (art. of wheat), which we will also re-",
        "pay in the month Pauni of the",
        "present twenty-fir[s]t",
        "ye[a]r of [A]ntoninus Cae-",
        "sar the lo[r]d, Mecheir 5.",
        "I, Sotas also called Tryphon, will jointly repay",
        "as aforesaid.",
      ]),
 dict(key='bgu;4;1133', nlines=25, slug='bgu_4_1133',
      name='Agreement - Chairemon as front-man in an eranos loan',
      date='14 Dec 19 BCE', found='Alexandria, Egypt', lat=31.2, lon=29.9,
      content='Chairemon, having lent his name for two shares of a 23-talent eranos loan from Artemidoros the eranarch, is indemnified by Artemidoros and Hermione, who took the money for themselves',
      trans=[
        "[From] Chairemon son of Zopyrion, and fr(om) Artemidoros son of Pathres,",
        "P[ers]ian",
        "[of the e]pigone, an[d] his wife Hermione daughter of Chairemon, Persian,",
        "[wit]h as guardian her (husband) Artemidoros. Since Cha[i]remon, being asked",
        "[by] Artemidoros himself and Hermione, has joined them in taking up",
        "two [n]ames(?) ... from Artemidoros son of Herakleides, the eranarch,",
        "[to] complete 23 talents 1000(?) bronze, [accord]ing to the agreement made",
        "on the same day through the same tribunal - they agree:",
        "[Art]emidoros and Hermione, that Chairemon has received nothing at all",
        "[fr]om the aforesaid principal, but that they have used it entirely",
        "[for] their own (purposes), which they will also repay to Artemidoros son of Herakleides",
        "in certain fixed installments according to the",
        "[...] agreement, and will release him from the agreement, and",
        "from now on will keep him undisturbed and free from exaction in",
        "[ev]ery way concerning these matters; and that they will do this without",
        "[a]ny dispute; or else that they shall be liable to seizure and held until",
        "they pay",
        "[wh]atever they may come to owe on the two names, with half again, at once,",
        "[and] the proper inte[r]est and the damages, the right of execution belonging to",
        "Chairemon",
        "[b]oth from the two, being mutual sureties for payment, and from one and from whichever of",
        "[t]hem he chooses, and from all their belongings, as if by judg(ment),",
        "[v]oid being <whatever pleas they bring forward, every shelter,>",
        "Year 12 of Caesar, Choiak 18.",
        "To be corrected(?).",
      ]),
 dict(key='bgu;4;1152', nlines=26, slug='bgu_4_1152',
      name='Repayment release - two loans repaid through Helenos’ bank',
      date='11-10 BCE', found='Alexandria, Egypt', lat=31.2, lon=29.9,
      content='Stephanos, freedman of Caesar, acknowledges repayment by Diodoros, through Helenos money-changing bank, of two loans (300 + 200 dr.) with overdue interest; the loan-agreements and a slave-deed are returned',
      trans=[
        "To Protarchos,",
        "from Stephanos (freedman) of Caesar and from Diodoros",
        "son of Diodoros. Stephanos concedes that he has re-",
        "ceived from Diodor[o]s, through the money-changing",
        "bank of Helenos, the loans he lent him",
        "according to the agreements made through the same tribunal,",
        "two, in the 8th (year) of Caesar: one in Pha-",
        "ophi, 300 silver dr., the other in Phamen[oth],",
        "200 silver dr.; and, of both loans, the",
        "interest of the overdue time; and that",
        "the said agreements are void, together with the",
        "bank-payments made toward each of them",
        "through Tet... his own ... and Demetrios’ money-changing",
        "bank; and that Stepha-",
        "nos will not proceed, nor any other on his behalf, against Diodo-",
        "ros, neither about the same nor about any-",
        "thing else at all, written or unwritten, fr[om] times",
        "[pa]st up to the present",
        "day; or - the agreed terms not being valid -",
        "he is liable both for the damages an[d the] ap-",
        "pointed fine. And D[io]do[ros] too concedes",
        "that he has recovered from Stephanos what he [ga]ve",
        "him according to the agreement of the month Phaophi -",
        "the documents ..., all of them, [and a co]-",
        "py of the agreement concerning the sl[ave,]",
        "such (documents) as he handed over.",
      ]),
]

HDR = """# ---------------------------------------------------------
# {label} - {name}
# Source: papyri.info DDbDP {key}  (Trismegistos {tm})
# Scraped via Firecrawl; apparatus & editorial markup trimmed.
# ---------------------------------------------------------

[META]
id:       {label}
label:    {label}
name:     {name}
genre:    contracts
date:     {date}
language: Greek (Koine)
found:    {found}
held:     (see shelf)
shelf:    {shelf}
content:  {content}
tm:       {tm}
source:   https://papyri.info/ddbdp/{key}
lat:      {lat}
lon:      {lon}

[GREEK]
"""

for it in ITEMS:
    r = json.load(open(SRC[it['key']], encoding='utf-8'))[it['key']]
    gk = [polish(l) for l in clean(r['greek'])][:it['nlines']]
    gk = [l for l in gk if l]
    tr = it['trans']
    assert len(gk) == len(tr), f"{it['key']}: greek {len(gk)} != trans {len(tr)}"
    num = it['key'].split(';')[2]
    series = it['key'].split(';')[1]
    label = f"BGU {series}.{num}"
    body = HDR.format(label=label, name=it['name'], key=it['key'], tm=r.get('tm', '?'),
                      date=it['date'], found=it['found'], shelf=r.get('shelf', '?'),
                      content=it['content'], lat=it['lat'], lon=it['lon'])
    body += "".join(f"r.{i}   {l}\n" for i, l in enumerate(gk, 1))
    body += "\n[TRANSLATION]\n"
    body += "".join(f"{i}   {l}\n" for i, l in enumerate(tr, 1))
    with open(f"manuscripts/{it['slug']}.txt", 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"built manuscripts/{it['slug']}.txt  ({len(gk)} lines)")
print("ALL OK")

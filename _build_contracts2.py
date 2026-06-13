#!/usr/bin/env python3
"""Build contracts tranche 2: the BGU 4 nurse-contract trio (1106, 1107, 1108)."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\(inverse\)\s*', '', l)
    l = re.sub(r'\d*,m(s(up)?|inf)\d*\b', '', l)
    l = re.sub(r'\br,m\b|\bv,ctr\b|\bv,msup\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

SRC = '_PENDING_bgu4_1100-1150.json'

ITEMS = [
 dict(key='bgu;4;1106', nlines=53, slug='bgu_4_1106',
      name='Nurse contract — Theodote to suckle the foundling Tyche',
      date='c. 13 BCE',
      content='Theodote, with her husband as surety, nurses Marcus Aemilius’ foundling slave-girl for 18 months; nine months’ wages paid up front',
      trans=[
        "(1st hand) [To Protarcho]s, president of the tribunal,",
        "(2nd hand) [from] Marcus Aemilius, son of Marcus, of the tribe Callidia(?), a[nd from]",
        "Th[eod]ote daughter of Dositheos, Persian, wi[th as guardian]",
        "a[nd s]urety for what is set out in this agree[ment]",
        "her husband Sophron, [son of]",
        "[…]…archos, Per[s]ian of the [epi-]",
        "[gone.] Concerning the matters agreed, [Theo-]",
        "dote [consents,] for a period of [eighteen] months [from Pha-]",
        "menoth of the current 17th <year> of Cae[sar, to]",
        "[nurse and suckle, outside,] at her own home [in the city,]",
        "[with her own milk, pure and unspoiled,]",
        "[the foundling slave infant at the breast of his, Tyche,]",
        "[that Marcus has entrusted to her,]",
        "[receiving from] him each m[onth as]",
        "[wage for the milk and the nursing, with]",
        "[oil, 8 silver drachmas. And Theo-]",
        "[dote] has received, through her surety S[o]phron, from M[arcus,]",
        "[from hand to hand ou]t of the house, for the aforesaid [eighteen] mon[ths,]",
        "the nursing-wages of nine months gathered to[gether —]",
        "seventy-two [drachma]s; and if it happen within [these]",
        "that the child suffer the human lot, [Theo-]",
        "[dote,] taking up another child, [shall nurse]",
        "[and suck]le it and present it to Marc[us for]",
        "[the] same nine months, taking nothing at",
        "[all,] because she has undertaken to nurse a-",
        "gainst death; and, being kept in good order with the re[maining]",
        "monthly nursing-wages, she is to exercise the proper care",
        "both of herself [and of the] child, not",
        "[spoili]ng her milk, nor sleeping with a man, nor con-",
        "ceiving, nor suckling another child be-",
        "sides; and whatever she receives or is entrusted with, to keep safe",
        "and return whenever demanded, or to pay the",
        "value of each item, except manifest loss, on which, hav-",
        "ing also been made evident, she shall be released; and not to qu[it]",
        "the nursing within the period. And [i]f she trans-",
        "gresses anything, she and Sophron are to be liable to seizure",
        "and held until they pay back both the nursing-wages she has re-",
        "ceived and whatever she may receive, with half again, and the",
        "damages and expenses and a further 300 silver drachmas, the",
        "right of execution belonging <to Marcus> upon both — being",
        "mutual sureties for the payment — and upon one, and upon whichever",
        "of them he chooses, and upon all their belong-",
        "ings, as if by legal judgment; void being also",
        "whatever pleas they may bring forward, every shel-",
        "ter; and, she performing each thing, that [Mar-]",
        "[cu]s Aemilius furnish her the monthly",
        "nursing-wages for the remaining nine months, and not [take]",
        "the child away within the period, or him-",
        "self pay the same penalty. And Theodote shall come over",
        "to Marcus … of the month …",
        "willingly, with the child too, for it to be inspected",
        "by him.",
        "(inverted) guarantee[…]",
      ]),
 dict(key='bgu;4;1107', nlines=38, slug='bgu_4_1107',
      name='Nurse contract — Didyme to suckle Isidora’s foundling',
      date='c. 13 BCE',
      content='Didyme nurses Isidora’s foundling slave infant for 16 months at 10 drachmas and two kotylai of oil a month; both women sign by their brothers',
      trans=[
        "Sheet (kollema).",
        "To Protarchos,",
        "from Isidora daughter of Kom[…], with as guardian her [brother Eutychides]",
        "son of Kom[…], and from Didyme daughter of Apol[lonios, Per]sian, [with as guardian]",
        "her brother Ischyrion son of Apollon[ios. Concerning the matters agreed,]",
        "[Didy]me [consents] to nurse and suckle, outside, at her own home [in the city, with her own]",
        "milk, pure and unspoiled, for a per[iod of sixteen mon]ths from Phar-",
        "mouthi of the current seventeenth <year> [of Caesar,] the slave",
        "infant of hers, a foundling at the br[east, … whose name is …,] that [Isidora has gi]ven over to her,",
        "receiving from Isidora herself as wa[ge for the milk and the nursing, for each]",
        "month, ten silver drachmas and two kotylai of oil; with which, kept",
        "in good [or]der, she is to exercise the care both of herself and of the child,",
        "not spoiling her milk, nor sleeping with a man, nor conceiving, [nor]",
        "suckling [another] child besides; and whatever she receives or is entrusted with of its things, to keep",
        "these safe and return them whenever demanded, or to pay the [value of each, except]",
        "manifest loss, on which, having also been made evident, [she shall be re]leased. [And forthwith]",
        "Didyme has received from Isidora, from hand to hand out of the house, <30 drachmas and> the oil of the first",
        "three months, Pharmouthi and Pachon and Pauni; and (she is) not to quit t[he nursing within]",
        "the period; and if she transgresses anything, she is to pay back both what [she has received of the nursing-wages and]",
        "whatever she may receive in addition, with half again, and the damages and ex[pen]ses, and to pay further",
        "[drachmas]",
        "five hundred and the appointed [fine], the right of execution belonging to Isidora",
        "both from Didyme herself and [from] all her belongings, as if by legal judg[ment;]",
        "void being also whatever pleas she may bring forward, every [shelter;]",
        "and, she performing each thing, that Isidora shall furnish her",
        "the monthly nursing-wages as aforesaid for the remaining [months,]",
        "thirteen, and not take the child away within the period, [or herself]",
        "pay the same penalty. And Didyme shall come over to [Isidora]",
        "each month, always every four days, bringing [the child too, for it to be]",
        "inspected by her. We request (registration).",
        "(2nd hand) I, Isidora, agree according to what is written above.",
        "I, Eutychides, am registered as guardian of my sister <and have written>",
        "on her behalf, as she does not know letters.",
        "(3rd hand) I, Didyme, agree according to what is wr[itten above.]",
        "I, Ischyrion, am registered as my sis-",
        "ter’s guardian and have writ[ten on her be-]",
        "half, as she does not know letters.",
        "(1st hand) Of Isido(ra). Year 17 of Caesar.",
      ]),
 dict(key='bgu;4;1108', nlines=38, slug='bgu_4_1108',
      name='Nurse contract — Erotarion to suckle the soldier’s slave-boy Primus',
      date='5 Oct 5 BCE',
      content='Erotarion nurses Primus, slave child of the legionary Marcus Sempronius, for 15 months at 10 drachmas and two kotylai of oil; monthly inspections',
      trans=[
        "To Artemidoros, archidikastes and superintendent of the chrematistai and the other tribunals,",
        "from Marcus Sempronius, son of [Marcus], of the tribe Aemilia, soldier of the",
        "twen[ty-]second legion, of the coh[ort …] … [… and] from",
        "E[rotarion daughter of …]komei…, [with as guardian and su]rety her kinsman [L]ucius …omysius,",
        "son of Lucius. Erotarion consents, for fifteen months from",
        "Phaophi of the current twenty-sixth year of Caesar, to nurse and suckle,",
        "outside, at her own home in the city,",
        "(inserted:) with her own milk, pure and unspoiled,",
        "the slave child that Marcus has entrusted to her already since Epeiph of the past year,",
        "whose name is Primus, at a wage for the milk and the nursing of ten drachmas a month",
        "and two kotylai of oil; and forthwith Erotarion has received from Marcus",
        "the nursing-wages [and] the oil for Epeiph and Mesore and Thoth …, and further for the sixteen months from [Pha]ophi",
        "(inserted:) likewise the nursing-wages and the oil of six months; and if — may it not happen —",
        "it befall the child to suffer the human lot",
        "…",
        "(inserted:) within the six months, Erotarion is bound, taking up another child, to nurse and suckle it for the",
        "6 months, not",
        "(inserted:) taking more than the aforesaid ten … months […]",
        "Erotarion, kept in good order with the nursing-wages and oil, is to exercise",
        "the care both of herself and of the child, not spoiling her milk, nor sleep-",
        "ing with a man, nor conceiving, nor suckling another child besides, for the months —",
        "and whatever she receives —",
        "(inserted:) six from Phaophi; and if after the six months Erotarion wishes another child …",
        "(inserted:) to suckle besides, it shall be permitted her; and whatever she receives or is entrusted with of the child’s belongings, (to return) whenever demanded, or to pay",
        "the value of each item, except manifest loss, on which, having also been made evi-",
        "dent, she shall be released; and not to quit the nursing within <the> period. And if she transgresses anything,",
        "she is to pay back the nursing-wages she has received and whatever she may receive in addition, with half again,",
        "and the damages and expenses, and a further two hundred silver drachmas, the right of execution being",
        "from Erotarion and from either and from each and from whichever of them",
        "[Ma]rcus chooses, and",
        "from all her belongings, as if by legal judgment; and (she is) not to bring forward pleas, or they are void.",
        "And Erotarion performing each thing, Marcus is to furnish her the remaining monthly",
        "nursing-wages as aforesaid, and not to take the child away within <the> period …, or himself be li-",
        "able to the same penalty. And Erotarion shall come over to Marcus with the",
        "child always three times a month, for it to be inspected by hi[m.] And Lucius is to be regis-",
        "tered in the right of approach against Erotarion for what she owes him together with her",
        "mother Kleopatra, according to an agreement. We request (registration). Farewell.",
        "(1st hand) Year 26 of Caesar, Phaophi 8.",
      ]),
]

HDR = """# ───────────────────────────────────────────────
# {label} — {name}
# Source: papyri.info DDbDP {key}  (Trismegistos {tm})
# Scraped via Firecrawl; apparatus & editorial markup trimmed.
# ───────────────────────────────────────────────

[META]
id:       {label}
label:    {label}
name:     {name}
genre:    contracts
date:     {date}
language: Greek (Koiné)
found:    Alexandria, Egypt
held:     (see shelf)
shelf:    {shelf}
content:  {content}
tm:       {tm}
source:   https://papyri.info/ddbdp/{key}
lat:      31.2
lon:      29.9

[GREEK]
"""

data = json.load(open(SRC, encoding='utf-8'))
for it in ITEMS:
    r = data[it['key']]
    gk = [polish(l) for l in clean(r['greek'])][:it['nlines']]
    gk = [l for l in gk if l]
    tr = it['trans']
    assert len(gk) == len(tr), f"{it['key']}: greek {len(gk)} != trans {len(tr)}"
    parts = it['key'].split(';')
    label = f"BGU {parts[1]}.{parts[2]}"
    body = HDR.format(label=label, name=it['name'], key=it['key'], tm=r.get('tm', '?'),
                      date=it['date'], shelf=r.get('shelf', '?'), content=it['content'])
    body += "".join(f"r.{i}   {l}\n" for i, l in enumerate(gk, 1))
    body += "\n[TRANSLATION]\n"
    body += "".join(f"{i}   {l}\n" for i, l in enumerate(tr, 1))
    with open(f"manuscripts/{it['slug']}.txt", 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"built manuscripts/{it['slug']}.txt  ({len(gk)} lines)")
print("ALL OK")

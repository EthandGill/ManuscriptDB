#!/usr/bin/env python3
"""Build contracts tranche 1: BGU 3.854 house sale, BGU 4.1058 nurse contract,
P.Oxy 2.318 loan (Tryphon archive)."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = re.sub(r'\br,m\b|\bv,ctr\b|\bv,msup\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

SRC = {
    'bgu;3;854': '_PENDING_bgu3_850-900.json',
    'bgu;4;1058': '_PENDING_bgu4_1050-1100.json',
    'p.oxy;2;318': '_PENDING_p.oxy2_286-320.json',
}

ITEMS = [
 dict(key='bgu;3;854', nlines=13, slug='bgu_3_854',
      name='Deed of sale — a two-storey house at Soknopaiou Nesos',
      date='18 May 45 CE', found='Soknopaiou Nesos (Arsinoite nome / Fayum), Egypt',
      lat=29.5377, lon=30.6856,
      content='Thases sells Herieus her two-storey house; price received hand-to-hand; both women sign by proxy',
      trans=[
        "[Thases, daughter of Panephremmis, my mother being] Thermouthis: I acknowledge [that I have sold] to Herieus, daughter of Sambathion, her mother being Thases, the two-storey house belonging to me with all its appurtenances,",
        "[all of them, at Soknopaiou Neso]s in the Herak[leides division of the Arsinoite no]me,",
        "the neighbors of the whole house being: on the south and west the royal road, on the north the house of Tesenouphis,",
        "[over which his children hold control,] on the east the [house] of Herieus daughter of Sambathion;",
        "and I have received at once, from hand to hand out of the house, the whole agreed price",
        "[in full, and I will guarantee it] with every guarantee from the present day for all time, and I will do the rest as written above, and I have in-",
        "[structed the witnesses to wri]te, and that the deed be drawn up by the clerk at the record-office. Papais son of Pa..ses wrote on her behalf because she does not know",
        "[letters. I, Herieus daughter of Samba]tion, my mother being Thases, have bought as aforesaid. Leontas son of Eirenaios wrote on her behalf because she does not",
        "[know letters. Sale and ces]sion of a two-storey house [and] all its appurtenances at Soknopaiou Nesos in the Herakleides division, the neighbors of the whole",
        "[house being: on the south and west the roy]al [road], on the north [the house of Tesenouphis, over which] his children hold control, on the east the house of Herieus daughter of Sambathion; and she has the price and gives guarantee — done by Thases",
        "[daughter of Panephremmis, mother Thermo]uthis, aged about 3(?), a mole on the left of her forehead; and Herieus daughter of Sambathion, mother Thases, aged about 38, likewise a mole on the left of her forehead. Subscriber:",
        "[…] … and the other (signatory): Leontas son of Eirenaios, aged about 20, without distinguishing mark. In the fifth year of Tiberius Claudius",
        "[Caesar Augustus Germanicus Imperator, Pa]chon 20. Registered through the record-office at Soknopaiou Nesos.",
      ]),
 dict(key='bgu;4;1058', nlines=51, slug='bgu_4_1058',
      name='Nurse contract — the slave Zosime to suckle the foundling Agalmation',
      date='30 Mar 13 BCE', found='Alexandria, Egypt',
      lat=31.2, lon=29.9,
      content='Philotera hires out her slave to nurse a foundling slave-girl for two years at 12 drachmas a month, with strict conditions',
      trans=[
        "(1st hand) To Protarchos,",
        "(2nd hand) from Sillis son of [Pto]lemaios, of the Philometorian",
        "deme, and from his mother Philotera daughter of",
        "Theodoros, Persian, with as guardian her hus-",
        "band P[tolemaios] son of Sillis, of the Philometo-",
        "rian deme. Concerning the matters agreed, Philo-",
        "tera consents to furnish her own slave-",
        "woman Zosime for a period of two years from Phar-",
        "mouthi of the current 17th year of Caesar, nurs-",
        "ing and suckling, in Philotera's own keeping,",
        "the child Sillis has handed over to her — a foundling",
        "slave infant at the breast, a girl",
        "whose name is Agalmation — at the wage fixed",
        "for the milk and the nursing, for each",
        "month, with oil and bread-rations, 12 silver drachmas;",
        "and the assembled principal of the two years' nurs-",
        "ing-wages, the 288 silver drachmas, forthwith",
        "has Philotera received from Sillis,",
        "from hand to hand out of the house. And if it happen that the said",
        "child Agalmation suffer the human lot (die)",
        "within the two years, Philotera is bound,",
        "taking up another child, to fur-",
        "nish her slave nursing it and to present",
        "it in full for whatever child she takes up, for the whole two",
        "years, receiving nothing at all more, since she has under-",
        "taken to nurse against death; and from",
        "now on to furnish the slave-woman exer-",
        "cising the proper care both of herself and of the",
        "child, not spoiling her milk,",
        "nor sleeping with a man, nor conceiving,",
        "nor taking on yet another child to suckle; and what-",
        "ever she receives or is entrusted with of his belongings, to",
        "keep safe and to return whenever it is de-",
        "manded, or to pay the value of each item — except mani-",
        "fest loss, on which, if it be also made evident,",
        "she shall be released; and not to quit the",
        "nursing within the period. And if she trans-",
        "gresses any of this, she is to pay back what she has received",
        "of the principal of the nursing-wages, with half again,",
        "and the damages and expenses, and a fur-",
        "ther penalty of 500 silver drachmas, and the appointed",
        "fine, the right of execution belonging to Sil-",
        "lis both upon Philotera herself and upon",
        "all her property, as if by legal",
        "judgment; void being also whatever",
        "pleas she may bring forward, every shel-",
        "ter; and the concession that Philotera has brought",
        "up to Sillis concerning the foster",
        "slave-child is to remain valid and as-",
        "sured. We request (registration).",
        "Year 17 of Caesar, Pharmouthi 4.",
      ]),
 dict(key='p.oxy;2;318', nlines=35, slug='p_oxy_2_318',
      name='Loan of 160 drachmas — Antiphanes to Tryphon, with house transfer',
      date='58–59 CE', found='Oxyrhynchus, Egypt',
      lat=28.54, lon=30.658,
      content='Antiphanes lends Tryphon 160 drachmas; on repayment his minor son is released from two mortgaged houses by the Sarapeion',
      trans=[
        "[In the fifth year of Nero] Claud[ius Caesa]r Augustus Germanicus",
        "[Imperator, …] on dies Augusta, in the city of the [Oxyrhyn]chi in the [The]baid.",
        "[Antiphanes son of] Herakl[as, of the] city of the [Oxyrhyn]chi,",
        "has lent to [Tryphon son of Dionysio]s, of [the same city],",
        "Persian of the epigone, in the street, one hundred and six-",
        "ty drachmas of Imperial and Ptolemaic",
        "silver coin as principal, to which nothing at all has been added. And let the bor-",
        "rower repay to Antiphanes the one hundred and",
        "sixty drachmas of silver on the thirtieth of the month Sebastos of the coming",
        "sixth year of Nero Claudius Caesar Augustus Germanicus",
        "Imperator, without any postponement; on the condition, binding",
        "upon the repayment of the money, that Antiphanes shall have",
        "his minor son Antiphanes released from the two",
        "[hous]es which the lender Antiphanes has sold to [Tr]yphon",
        "at the Sarap[e]ion by the city of the Oxyrhynchi, in the",
        "quarter called \"of the Shepherds\", and have him regis-",
        "tered at another place, the costs of the transfer and regis-",
        "tration falling upon the lender Antiph[a]nes.",
        "And if, the tra[nsfer] having been made, the bor[rower]",
        "does not repay [as written], let him for[f]eit to Antiphan[es]",
        "[the aforesaid principal] with half again, and for whatever",
        "time [Tryphon de]lays, the proper inter(est),",
        "[the right of execution belonging] to the lender Antiphanes both from the",
        "[borrower and fr]om all his property,",
        "[as if by legal judgment; it being open] to the lender Antiphanes",
        "[to effect before the sta]ted term the trans-",
        "[fer] of his son; on the same day let the borrow[er] pay",
        "[to Antiphanes, upon the] transfer then to be made, the aforesaid",
        "[principal —] Tryphon being [in no way dimin]ished in the en-",
        "[suing] guaran[tee] to be given [by Anti]phanes of the [two houses]",
        "he bought [from] him, in accordance with the conveyance made [to him.]",
        "[The deed is valid.] Year (…) of Nero Claudius",
        "[Caesar Augustu]s Germ[anicus Im]perator,",
        "[… through] Apolloni-",
        "[os, formerly styled Se]koundos(?) …",
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
    parts = it['key'].split(';')
    label = (parts[0].upper().replace('P.OXY', 'P.Oxy') + ' '
             + (parts[1] + '.' if parts[1] else '') + parts[2])
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

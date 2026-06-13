#!/usr/bin/env python3
"""Build final tranche: P.Oxy 1.103 lease, 1.94 slave-sale agency, BGU 3.837 reed-sale, P.Fay 96 oil-mill rent receipt."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'⁦[^⁩]*⁩', ' ', line)
    l = re.sub(r'[⁦⁧⁨⁩]', '', l)
    l = re.sub(r'\(perpendicular\)\s*', '', l)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = re.sub(r'\bvac\.?\b', ' ', l)
    return re.sub(r'\s+', ' ', l).strip()

SRC = {'p.oxy;1;103': '_PENDING_p.oxy1_91-140.json',
       'p.oxy;1;94': '_PENDING_p.oxy1_91-140.json',
       'bgu;3;837': '_PENDING_bgu3_800-849.json',
       'p.fay;;96': '_PENDING_p.fay_91-140.json'}

ITEMS = [
 dict(key='p.oxy;1;103', nlines=28, slug='p_oxy_1_103', genre='contracts',
      name='Lease of land - one aroura for flax, rent in half the crop',
      date='13 Oct 316 CE', found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658,
      content='Two Aurelii lease one aroura near Ision Panga from the gymnasiarch Themistokles to sow flax, paying half the retted flax-stalk as rent',
      trans=[
        "To Aurelius [Th]emistokles also called Dioskouri[des, gym]nasiarch,",
        "former prytanis, council(lor) of the [il]lus(trious) and most ill[ustrious city of the Oxyrhynch]ite[s],",
        "through Ko[rm]ilios, assistant,",
        "from the Aurelii Leonides son of Theon and Di[os]k[o]ros son of Ammonios,",
        "both of the same city. Of our own free will we undertake",
        "to lease, for the present 11th and ninth year only,",
        "of the (land) belonging to you near Ision Panga, in the embankment-district of",
        "Nesla, held in common with your brother Leukadios, one aroura",
        "for sowing flax-stalk; and, in lieu of rent, to furnish you the land-",
        "owner half the share of the flax-stalk arising from",
        "the land; and we the lessees, in return for the farming we do",
        "and the seed and all the expenses we provide,",
        "(to keep) the remaining half share and the whole of the linseed,",
        "all free of every risk, the public dues of the land being",
        "your charge as landowner, you being master of the crops until you recover",
        "what is owing. The undertaking being guaranteed to us, of necessity",
        "we shall deliver the half share of the flax-stalk arising,",
        "retted at the pool, without delay,",
        "at the proper season, you having the right of execution against us,",
        "we being mutual sureties for payment as is fitting. The undertaking is",
        "valid, and on being questioned we acknowledged it.",
        "In the consulship of Caecinius Sabinus and Vettius Rufinus the",
        "most illustrious, Phaophi 16.",
        "(2nd hand) I, Aurelius Themistokles also called Dioskourides,",
        "through me Kormilios assistant, have a copy of this",
        "deed. If a higher bid is offered,",
        "it shall be accepted.",
        "(Lease) of Leonides and Diskoros, flax-stalk-valuers(?).",
      ]),
 dict(key='p.oxy;1;94', nlines=23, slug='p_oxy_1_94', genre='contracts',
      name='Deed of agency - authorizing the sale of two slaves',
      date='26 Oct 83 CE', found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658,
      content='Marcus Antonius Ptolemaios appoints Dionysios his agent to sell two inherited slaves, Diogas alias Nilos and another Diogas, at whatever price he finds',
      trans=[
        "In the third year of Imperator Caesar Domitian Augustus,",
        "Phaophi (2nd hand) 28, (1st hand) in the city of the Oxyrhynchi in the Thebaid.",
        "Marcus Antonius Ptolemaios, son of Ptolemaios, of the Sergian tribe,",
        "and however he is styled, acknowledges to Dionysios the el-",
        "der, son of Theon son of Dionysios, of the city of the Oxyrhynchi,",
        "in the street, that he has appointed him, by this",
        "acknowledgment, as agent to carry off, for alienation,",
        "the slave bodies belonging to him, Antonius Ptolemaios, by paternal",
        "inheritance - Diogas also called Nilos, about 40 years old,",
        "and another Diogas, about 30 years old - these such, not to be re-",
        "turned, except for (legal) claim and the sacred disease, to those who come forward",
        "for the purchase, whether all together or one by one,",
        "at whatever price he finds, and (2nd hand) about them to manage all else",
        "(1st hand) just as it was open to Marcus Ptolemaios himself",
        "[w]hen present; for he approves of these",
        "thing[s], on condition that the price to be given (2nd hand) him for these",
        "(1st hand) - or for what shall be sold of them - he shall re-",
        "store to Antonius Ptolemaios, the trust",
        "resting upon Dionys[i]os, and the guarantee",
        "of owner[ship] falling to Anto-",
        "nius Ptolemaios on the aforesaid terms.",
        "The deed of agency is valid.",
        "Deed of agency of Anto(nius) Ptol(emaios).",
      ]),
 dict(key='bgu;3;837', nlines=40, slug='bgu_3_837', genre='contracts',
      name='Sale of reeds - 42 bundles of male reed (Byzantine)',
      date='29 May 609 CE', found='Arsinoe / Ptolemais Euergetis (Fayum), Egypt',
      lat=29.3084, lon=30.8428,
      content='Three villagers acknowledge receiving payment in full from Menas the public weigher for 42 bundles of male reed, to be delivered the following Mecheir',
      trans=[
        "[… and of our la]dy",
        "[the h]oly Mother of God",
        "[and all] the saints,",
        "in the reign [of] our lord",
        "Fl(avius) [Pho]cas the",
        "eternal Augustus, [ye]ar",
        "7, Pauni 4, tax-period 12 of the ind(iction),",
        "in Ar(sinoe).",
        "The Aurelii: apa Ol son of",
        "Pousi, and Agammon",
        "son of Pamoun, and Ouena-",
        "phrios son of Anoup, from",
        "the hamlet of …iolios(?)",
        "of the Arsinoite nome,",
        "to the most admirable",
        "Menas, public weigh-",
        "er, son of the blessed",
        "Paul, from the city of the Arsinoi-",
        "tes, greeting. We acknowl-",
        "edge, by mutual surety-",
        "ship, that we have had",
        "from you, from hand to hand, and",
        "have been paid in full the",
        "price of male reeds,",
        "of bundles, forty-",
        "two, reed bundles 42,",
        "I apa Ol bundles",
        "twenty-four, and I",
        "Agammon bundles",
        "nine, and Ouenaphrios the",
        "other nine bundles,",
        "each bundle",
        "being, of palms,",
        "nine, and the delivery",
        "of them we will make to you",
        "[in] the month Mecheir of the coming",
        "thirteenth",
        "[indiction] and …",
        "[…] jointly: by apa Ol son of Pousi (and) Agamm(on) son of Pamoun (and) Ouenaphrios son of Anoup, ree[ds]",
        "for the most admir(able) Menas, public w[eigher].",
      ]),
 dict(key='p.fay;;96', nlines=20, slug='p_fay_96', genre='receipts',
      name='Receipt - rent of an oil-mill paid in oil',
      date='26 Nov 143 CE', found='Theadelphia (Arsinoite nome / Fayum), Egypt',
      lat=29.4333, lon=30.5333,
      content='Through Sarapion’s bank: Nemesas acknowledges from Syros the oil-maker the rent of the oil-mill - five metretes of oil, half olive and half radish',
      trans=[
        "In the seventh year of Imperator",
        "Caesar Titus Aelius Hadrianus Antoninus",
        "Augustus Pius, Hathyr 29, through the bank of Sara-",
        "pion (son of) Pterouit…kos:",
        "Syros son of Alexandros son of Alexandros,",
        "oil-make[r], to Nemesas son of Heli[od]oros son of",
        "Eudaimon, of the quarter of …kon, aged about",
        "forty, without distinguishing mark - that",
        "Nemesas has received from Syr[o]s the rent",
        "of the past sixth year of Antoninus",
        "Caesar the lord, which Syros holds",
        "in lease, of the oil-mill belonging",
        "to the one in his charge,",
        "Pompeius Ptolemaios, prytanizing gymna-",
        "siarch: of oil, five metretes,",
        "namely two and a half metretes of olive oil",
        "and the remaining two and a half metretes",
        "of radish oil; and that he makes no claim against him",
        "about these things, the lease remaining",
        "valid on the terms it contains.",
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
genre:    {genre}
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
    parts = it['key'].split(';')
    if parts[0] == 'p.fay':
        label = f"P.Fay. {parts[2]}"
    elif parts[0] == 'p.oxy':
        label = f"P.Oxy {parts[1]}.{parts[2]}"
    else:
        label = f"BGU {parts[1]}.{parts[2]}"
    body = HDR.format(label=label, name=it['name'], key=it['key'], tm=r.get('tm', '?'),
                      genre=it['genre'], date=it['date'], found=it['found'],
                      shelf=r.get('shelf', '?'), content=it['content'],
                      lat=it['lat'], lon=it['lon'])
    body += "".join(f"r.{i}   {l}\n" for i, l in enumerate(gk, 1))
    body += "\n[TRANSLATION]\n"
    body += "".join(f"{i}   {l}\n" for i, l in enumerate(tr, 1))
    with open(f"manuscripts/{it['slug']}.txt", 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"built manuscripts/{it['slug']}.txt  ({len(gk)} lines)")
print("ALL OK")

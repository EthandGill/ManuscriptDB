#!/usr/bin/env python3
"""Build documents batch C."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'⁦[^⁩]*⁩', ' ', line)
    l = re.sub(r'[⁦⁧⁨⁩]', '', l)
    l = re.sub(r'\(perpendicular\)\s*', '', l)
    l = re.sub(r'\bcolumn [rv]\b', '', l)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = re.sub(r'\bvac\.?\b', ' ', l)
    return re.sub(r'\s+', ' ', l).strip()

SRC = {'bgu;3;833':'_PENDING_bgu3_800-849.json','p.oxy;2;255':'_PENDING_p.oxy2_234-285.json',
       'p.oxy;2;249':'_PENDING_p.oxy2_234-285.json','p.fay;;100':'_PENDING_p.fay_91-140.json',
       'bgu;4;1064':'_PENDING_bgu4_1050-1100.json','p.oxy;2;254':'_PENDING_p.oxy2_234-285.json'}
OXY = dict(found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658)

ITEMS = [
 dict(key='bgu;3;833', nlines=36, slug='bgu_3_833', label='BGU 3.833',
      name='Census declaration - Melas of Memphis and his children',
      date='1 Oct 174 CE', found='Memphis, Egypt', lat=29.8489, lon=31.2503,
      content='Melas, a tradeless man of Memphis, registers himself (aged 51) and his children by two different women in a lodging-house, with the owner standing surety for the poll-taxes, under oath',
      trans=[
        "To Heron, royal scribe",
        "of the Memphite (nome),",
        "from Melas son of Areios, his mother",
        "being Kaleis, of those from Memph-",
        "is without a trade, registered in the 2nd",
        "quarter. I register myself",
        "and my people, as lodgers,",
        "in (the house) I dwell in at Memphis",
        "in the same 2nd quarter,",
        "the house of Isidoros son of Anou-",
        "bion also called Pankrates,",
        "for the house-by-house",
        "census of the past 14th year of Aurelius",
        "Antoninus Caesar",
        "the lord —",
        "(this) registration:",
        "myself, Melas, for the sa-",
        "me 14th year, aged 51,",
        "and the (children) born of",
        "different women,",
        "(my) sons: from Tesagris,",
        "a Memphite woman, Melas,",
        "aged 1;",
        "and from Herieus a [dau]ghter, Tne-",
        "phremphis, aged 16.",
        "And the aforesaid house-owner, present,",
        "Isidoros, goes surety for us",
        "for the poll-taxes.",
        "And I swear by the",
        "Fortune of the lord Aurelius Antoninus Caesar",
        "that the foregoing is true.",
        "Year 15 of Imperator Caesar",
        "Marcus Aurelius Antoninus",
        "Augustus Armeniacus Medicus",
        "Parthicus Germanicus Greatest,",
        "Phaophi 4.",
      ]),
 dict(key='p.oxy;2;255', nlines=27, slug='p_oxy_2_255', label='P.Oxy 2.255', **OXY,
      name='Census declaration with oath - no privileged lodgers',
      date='Sept-Oct 48 CE',
      content='Thermoutharion declares the inmates of her house (only herself, a freedwoman aged 65) and swears by Tiberius Claudius that no stranger, Alexandrian, freedman, Roman or Egyptian lodges with her beyond those listed',
      trans=[
        "To Dor[ion, s]trategos, an[d A]po[l]lo(nios),",
        "ro[y]al scr[ibe], and Didymos [and A]pol[lo(nios)],",
        "topogrammateis and komogrammateis, from Ther[mou-]",
        "tharion daughter of Thoonis, with as guardian",
        "Apollonios son of Sotades. The",
        "[persons] dwelling in the house belong-",
        "[ing to me, of the south]ern [quart]er […]",
        "are: Thermou[tharion, freedwoman of the afore-]",
        "writ(ten) Sotad[es], aged about 65,",
        "of middle height, honey-skinned, long-faced, a scar on the ri[gh]t knee;",
        "total: women 2(?).",
        "I, Thermouthari[on] the aforewritten, w[ith]",
        "as guardian the s[am]e Apollonios, swear",
        "by [T]iberius Claudius Caesar Aug[ustus]",
        "Germanicus Imperator that",
        "soundly and truthfully I have sub-",
        "mitted the foregoing reg-",
        "istration of those dwelling with me,",
        "and that no one else dwells with me,",
        "neither a stra[nger n]or an Alexandrian",
        "nor a freedman nor a Roman",
        "nor an Egyp[tian b]eyond those a-",
        "forewritten. If I keep my [oath], may it",
        "go w[ell] with me; if I [for]swear, the [con]trary.",
        "Year nine of Tiberius Claud[ius]",
        "Caesar Augustus Germanicus",
        "[Imper]ator, Phaophi [..].",
      ]),
 dict(key='p.oxy;2;249', nlines=27, slug='p_oxy_2_249', label='P.Oxy 2.249', **OXY,
      name='Property declaration - a share inherited from a childless brother',
      date='10 Oct 80 CE',
      content='Diogas registers, beyond his earlier returns, a one-third of a one-sixth share of a jointly-held house in the garden of Pammenes, come to him by the will of his brother Poplios who died childless under Vespasian',
      trans=[
        "To Epimachos and Theon, archive-keepers,",
        "from Diogas son of Teos",
        "son of Kentauros, his mother being Api-",
        "a daughter of Protas, of those from Oxy-",
        "rhynchus city. I regis-",
        "ter, according to the regula-",
        "tions, apart from what I previously regis-",
        "tered, also now the (property) that has come",
        "down to me from the name",
        "of my full bro-",
        "ther Poplios, of those of the",
        "same city, who di-",
        "ed childless in the 10th year",
        "of the god Vespasian, in th[e]",
        "same city, in the (garden) called",
        "of Pammenes — a gar-",
        "den: a third part of a sixth",
        "part of a house held in common with",
        "me and (my) brothers and",
        "others, in accordance with",
        "the will made through the",
        "record-office in the same city",
        "in the month Tybi of the 10th year,",
        "as it contains.",
        "Year 3 of Imperator Titus",
        "Caesar Vespasian Augustus,",
        "Phaophi 13.",
      ]),
 dict(key='p.fay;;100', nlines=29, slug='p_fay_100', label='P.Fay. 100',
      name='Bank order - pay out the price of a half house-share',
      date='23 Jan 99 CE', found='Theadelphia (Arsinoite nome / Fayum), Egypt',
      lat=29.4333, lon=30.5333,
      content='Aphrodous instructs the banker to pay two women (each with husband-guardian) 300 drachmas apiece — 600 on deposit — as the price of a half share of a house and court at Theadelphia; both women sign by their husbands',
      trans=[
        "Aphrodous daughter of Sat[y]r[o]s, w[ith] as guardian her kins-",
        "man Ammonios son of Her[a]kleides, to Sambas",
        "also called Didymos, banker, gr[ee]ting. Pay",
        "out to Charition also called Tasoucharion,",
        "daughter of Charidemos, and to Char[i]tion daughter of Didymos,",
        "each with her husband as guardian — t[o]",
        "Charition also called Ta[s]oucharion (the guardian) being Apollo-",
        "n[i]os son of Apollo[ni]os, and to the other Cha-",
        "rition (the guardian) Heron son of Didymos — the price",
        "of a half share of a house and cour[t] and plots",
        "[a]nd all the appurtenances, in the vil-",
        "[lage of] Theadelphia in the Themistes division,",
        "[in acc]ordance with the old conveyances made to th[em],",
        "which you hold of mine on",
        "deposit: six hundred silver drach-",
        "[mas], total 600 dr. Year 2 of Imperator Caesar",
        "Nerva Trajan Augustus Germanicus, Tyb[i]",
        "28. I, Charition daughter of Didymos, with as guardian my husband",
        "Heron son of Didymos: register it; and I have received",
        "the 300 silver drachmas falling to me, total 300 dr.",
        "I, Heron, wrote also for my wife, she not knowing",
        "letters. Year two of Imperator Caesar",
        "Nerva Trajan Augustus Germanicus, Tybi 28.",
        "I, Charition also called Tasouchion, daughter of Charidemos,",
        "with as guardian my husband Apollonios",
        "son of Apion, have received the three",
        "hundred drachmas, total 300 dr. I, Apollonios,",
        "wrote also for my wife,",
        "she not knowing letters.",
      ]),
 dict(key='bgu;4;1064', nlines=19, slug='bgu_4_1064', label='BGU 4.1064', **OXY,
      name='Bank order - transfer ten talents to the exegetes',
      date='Dec 277 - Jan 278 CE',
      content='An order to the banker Sarapion to transfer ten talents of new silver coin to Aurelius Ofellius, exegetes of the Oxyrhynchites, in return for money received at Hermopolis; a single-copy autograph draft',
      trans=[
        "[(N.N.) to Aurelius Sa]r[a-]",
        "pion, banker, greeting.",
        "You will do w[ell] to t[r]ansfer",
        "to (the man) with you in the Oxy[rhy]nchite, Au-",
        "relius Ofellius, exegetes of the Oxy-",
        "rhynchites, in return for what I had from",
        "him at Hermo[u]polis, of new sil-",
        "ver coin, ten talents,",
        "10 tal., the equal ten silver talents,",
        "full in number, and do not de-",
        "tain them; and this draft",
        "I have issued you in single copy,",
        "in my own hand, and let it be valid, and",
        "on being questioned I acknowledged it.",
        "Year 3 of our lord Marcus",
        "Aurelius Probus Augustus,",
        "Tybi …",
        "(Notice) in the Oxyrhynchite:",
        "… Sarapion the distributing-clerk.",
      ]),
 dict(key='p.oxy;2;254', nlines=10, slug='p_oxy_2_254', label='P.Oxy 2.254', **OXY,
      name='Census declaration of a priest of Isis',
      date='c. 13-26 CE',
      content='Horion, priest of Isis at the temple of the Two Brothers by the Sarapeion, declares the persons dwelling in the house he shares with his wife Tasis and others',
      trans=[
        "To Eutychides and Theon, topo- and komo-grammateis,",
        "from Horion son of Petosiris, priest of Isis",
        "greatest goddess, of the temple called of the Two Brothers,",
        "which is at the Sara-",
        "peion by the city of the Oxyrhynchi, in the Myrobalanos quarter.",
        "The persons dwelling in the house belonging",
        "to me and (my) wife Tasis, and to Tauris son of Harbichis(?)",
        "and to Panpontos son of Nechthesoris and Thaechme-",
        "re — a house in the aforesaid (place) called of the Two Brothers —",
        "of whom there are:",
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
genre:    documents
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
    body = HDR.format(label=it['label'], name=it['name'], key=it['key'], tm=r.get('tm', '?'),
                      date=it['date'], found=it['found'], shelf=r.get('shelf', '?'),
                      content=it['content'], lat=it['lat'], lon=it['lon'])
    body += "".join(f"r.{i}   {l}\n" for i, l in enumerate(gk, 1))
    body += "\n[TRANSLATION]\n"
    body += "".join(f"{i}   {l}\n" for i, l in enumerate(tr, 1))
    with open(f"manuscripts/{it['slug']}.txt", 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"built manuscripts/{it['slug']}.txt  ({len(gk)} lines)")
print("ALL OK")

#!/usr/bin/env python3
"""Build P.Oxy 1 legal tranche: wills 104 & 105, house sale 99."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

DATA = json.load(open('_PENDING_p.oxy1_91-140.json', encoding='utf-8'))
OXY = dict(found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658)

ITEMS = [
 dict(key='p.oxy;1;104', nlines=38, slug='p_oxy_1_104', **OXY,
      name='Will of Soeris — house to her son, life-tenancy to her husband',
      date='26 Dec 96 CE',
      content='Soeris, sane and of sound mind, leaves her house by the Sarapeion to her son Areotes; her husband keeps rent-free dwelling for life; forty drachmas to her daughter',
      trans=[
        "In the sixteenth year of Imperator Caesar Domitian",
        "Augustus Germanicus, Choiak 30, in the city of the Oxyrhynchi in the Thebaid,",
        "for good fortune.",
        "Thus has Soeris, daughter of Harpochras, freedman",
        "of Sarapion son of Chairemon, her mother being Tnepheros daughter of Annios,",
        "of the city of the Oxyrhynchi, made her will, being sane and of sound mind, with as guardian her husband Hatres, his mother being Teraus",
        "also called Thaubastis, daughter of Phatres, both of the same city, in the",
        "street. So long as I live in health, may I have power over my own property, to use and ad-",
        "minister it in whatever way I choose. But after my coming",
        "death, I concede that there belong to my son Areotes, styled",
        "as of me, Soeris, as mother — if he lives, and if not, to his issue — the house",
        "and court belonging to me at the Sarapeion by the city of the Oxyrhynchi, in the quarter",
        "formerly of the Cavalry Camp, with entrances",
        "and exits and appurtenances, on condition that my designated husband Hatres shall have",
        "the right of dwelling, and the accruing rents, of the designated",
        "house and court for the span of his life, free of rent,",
        "cast out by no one; to whom the same son Areotes shall furnish",
        "yearly forty-eight drachmas of silver until there be paid in",
        "full three hundred drachmas of silver — the sum settled between them",
        "in settlement and agreement concerning what is owed by me to the",
        "same husband Hatres on a bank security for the tenancy-pledge of the",
        "same house and court, six hundred drachmas of silver. And the same son",
        "shall give to the daughter born to me of my husband Hatres, Tnepheros,",
        "after my husband’s death, within thirty days, what I be-",
        "queath her: forty drachmas of silver. And she shall dwell in one room",
        "on the ground floor, at the gate-house, whenever she be separated from her husband, until",
        "she be once for all reconciled, free of rent. And in general it shall not be lawful for anyone",
        "[…] to make demand of anything else from the son or his assigns",
        "[after] my husband’s death — nothing of what passed through the bank se-",
        "curity of the tenancy-pledge, in any [way]; rather he is re-",
        "leased from payment of what is owed through it […]. And to no one else",
        "[at all] do I leave any of my property. All the fore-",
        "[writt]en has the approval of [my] designated [husband Hatre]s, of the same",
        "[city], in the same street […] Artemidor[os …]",
        "[…] … [… fo]ur …[…]",
        "[…] …",
        "[…] …",
        "[…] …",
      ]),
 dict(key='p.oxy;1;105', nlines=38, slug='p_oxy_1_105', **OXY,
      name='Will of Pekysis — daughter as heir, seven sealing witnesses',
      date='118–138 CE',
      content='Pekysis leaves his house-shares to his daughter Ammonous and the furniture to his wife; seven witnesses each describe their scar and their seal',
      trans=[
        "[In the ..th year of Imperator Caesar Trajan Hadria]n Augustus, Tybi 13, in the city of the Oxyrhynchi in the Thebaid, for good fortune.",
        "[Thus has Pekysis son of Hermes son of P]ekysis, his mother being Didyme daughter of Philotas,",
        "of the city of the Oxyrhynchi, [made his will, being sane and of sound mind,] in the street: for the time I survive, I am to have power over my",
        "own property",
        "[… a]nd to alter my will. But if I die with this will in force, I leave as heir",
        "my daughter Ammonous, her mother being Ptolema, if she lives — and [if]",
        "[not, her issue —] of the shares belonging to me, in the Cretan quarter, of a house held in common, and court and vaults. And the gear and furniture that I shall leave, and",
        "household stock and whatever el[se]",
        "[I may have, I leave all to the] mother of my children and my wife Ptolema, freedwoman",
        "of Demetrios son of Hermippos, on condition she have for the span of her life the use and",
        "dwelling-right and the",
        "[rent-income of the shares of the house and court and va]ults. And if it happen that Ammonous die childless and intestate,",
        "the shares of the immovables shall belong to her half-brother on the mother’s side, Antas, if he lives — and if not,",
        "[…. And it shall not be lawful for anyone else to] interfere with what I have ordained, or whoever transgresses any of it shall pay to my daughter and",
        "heir Ammonous a fine of a thousand drachmas, and",
        "[…] (2nd hand) I, Pekysis son of Hermes son of Pekysis, leave after my death as heir my daughter",
        "[Ammonous, of the shares in the Creta]n [quarter] of the house and court and vaults; and to my",
        "wife Ptolema I leave all",
        "[my gear and furniture and house]hold stock and whatever else I may have, and for as long as she lives the dwelling-right of the shares of the hou-",
        "[se and court and vaults. And i]f Ammonous die childless and intestate, let",
        "the shares of the immovables belong to",
        "[her half-brother on the mother’s side, A]ntas, as stated above. I am forty-four years old,",
        "a scar on the neck on the left,",
        "[and my seal is of Am]mon. (3rd hand) I, Sarapion son of Sarapion son of Dionysios, of the same city, witness the will of Pekysis, and",
        "[I am .. years old, a scar …, and] my [se]al is of Dionysos. (4th hand) I, Hekaton son of Sarapion son of Hekaton, of the",
        "same city, witness the will of Pekysis, and I am",
        "[.. years old, a scar …, and] my seal is of Sarapis. (5th hand) I, Papontos son of Diogenes son of Papontos, of",
        "the same city, witness the will of Pekysis,",
        "[and I am .. years old, …, and] my seal is Zeus on an eagle. (6th hand) I, Zoilos son of Zoilos son of Panechotes, of the sa-",
        "[me city, witness the will of P]ekysis, and I am forty-eight years old, a scar on the left forearm, and",
        "[my seal is … of Ha]rpokrates on a lotus. (7th hand) I, Heras also called Saios, son of Zenas son of Heras, of the same",
        "city, witness the will of Pekysis,",
        "[and I am … years old, a scar on the] right [shi]n, and my seal is a bust of a philosopher. (8th hand) I, Dionysios son of Dionysios son of Diogenes, of the same city,",
        "witness",
        "[the will of Pekysis, and I am] forty-six years old, a scar by the right temple,",
        "and my seal is of Dionysoplaton. (9th hand) (Registered at the) record-office of the city of Oxyr(hynchi).",
        "[Year .. of Imperator Cae]sar Trajan Hadrian Augustus, Tybi 13.",
        "[… Will of Pekysis son of Her]mes son of Pekysis, mother Didyme daughter of Philotas, of the city of Ox(yrhynchi).",
      ]),
 dict(key='p.oxy;1;99', nlines=30, slug='p_oxy_1_99', **OXY,
      name='Sale of a half-share of a three-storey house — the weaver Tryphon buys',
      date='4 Sept 55 CE',
      content='Tryphon, “honey-skinned, long-faced, somewhat squinting”, buys half a three-storey house from his mother’s cousin for 32 bronze talents; tax receipt appended',
      trans=[
        "Copy. In the second year of Nero Claudius Caesar Augustus Germanicus Imperator,",
        "month Audnaios-S[e]basto[s 6, in the city of the Oxyrhynchi]",
        "in the Thebaid, before the agoranomoi Andromachos and Diogenes. Tryphon son of Dionysios,",
        "[of the city of the Oxyrhynchi],",
        "of middle height, honey-skinned, long-faced, somewhat squinting, a scar on his right wrist, has bought from his mother Thamounis’ cou[sin Pnepheros]",
        "son of Pap[o]ntos, of the same city, aged [about] 65, of middle height, honey-skinned, long-faced, a scar above his [eye]brow [… and]",
        "another on his right knee, in the street: the half share of the three-storey house belonging to him from his mother,",
        "with [all] its en[trances]",
        "and exits [and] appurtenances, situated at the Sarapeion by the city of the Oxyrhynchi,",
        "in the southern [parts of the quarter]",
        "Temgemou[thi]s, west of the street leading to the quarter called “of the Shepherds”. Neighbors of the whole [house: on the south]",
        "and east, public streets; on the north, that of the aforesaid buyer Tryphon’s",
        "mother Thamounis; [on the west, the house of the]",
        "seller Pnepheros’ sister Tausiris, a blind alley lying between. (Price:) 32 talents",
        "of bronze. And [the seller] will gua[rantee the]",
        "half share of the house under disposition, for ever, against all comers, with every guarantee, in the",
        "sa[me] street.",
        "In the second year of Nero Claudius Caesar Augustus Germanicus Imperator, month",
        "Sebastos 6, executed through And[romachos and Diogenes]",
        "the agoranomoi.",
        "Payment of the conveyance-tax, year 2 of Nero Claudius Caesar Augustus Ger[manicu]s Imperator, month [Sebastos 6. Paid through the]",
        "bank in the city of the Oxyrhynchi headed by Sara[pi]on and partners …[…] Tryphon son of Dionysios […]",
        "tax on the half share of the three-storey house belonging from his mother to the [se]ller,",
        "with [all its entrances]",
        "and exits and appurtenances, situated at the Sarapeion by the city of the Oxyrhynchi in the [southern parts]",
        "of the quarter Temgenouthis, in the parts west of the street leading to the quarter called",
        "[“of the Shepherds”,]",
        "which he bought from his mother Thamounis’ cousin Pnephe[ros] son of Papontos",
        "[of the same]",
        "city by agoranomic deed, for 32 bronze talents — bronze reckoned in silver, 3 talents 1200 dr. — the one-tenth tax with transport charge, […] drachmas.",
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
    r = DATA[it['key']]
    gk = [polish(l) for l in clean(r['greek'])][:it['nlines']]
    gk = [l for l in gk if l]
    tr = it['trans']
    assert len(gk) == len(tr), f"{it['key']}: greek {len(gk)} != trans {len(tr)}"
    num = it['key'].split(';')[2]
    label = f"P.Oxy 1.{num}"
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

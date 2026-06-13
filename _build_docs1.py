#!/usr/bin/env python3
"""Build documents + petitions batch A."""
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

SRC = {'bgu;4;1061':'_PENDING_bgu4_1050-1100.json','bgu;4;1189':'_PENDING_bgu4_1151-1200.json',
       'p.oxy;1;108':'_PENDING_p.oxy1_91-140.json','p.oxy;1;109':'_PENDING_p.oxy1_91-140.json',
       'bgu;3;852':'_PENDING_bgu3_850-900.json','bgu;3;869':'_PENDING_bgu3_850-900.json',
       'p.oxy;2;253':'_PENDING_p.oxy2_234-285.json'}
OXY = dict(found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658)
SOKN = dict(found='Soknopaiou Nesos (Arsinoite nome / Fayum), Egypt', lat=29.5377, lon=30.6856)
HERA = dict(found='Busiris (Herakleopolite nome), Egypt', lat=29.0667, lon=30.9333)

ITEMS = [
 dict(key='bgu;4;1061', nlines=20, slug='bgu_4_1061', genre='petitions', label='BGU 4.1061', **HERA,
      name='Petition - a temple doorkeeper murdered, a merchant robbed',
      date='25 Jan 14 BCE',
      content='Pnephoros reports to the deputy-strategos how Patellis with 15 others murdered the woman doorkeeper of the chapel at Busiris, then in brigand fashion stripped a merchant of 150 fleeces and 1500 drachmas',
      trans=[
        "(…, year 16, Tybi 30.)",
        "To Nearchos, deputy-strategos,",
        "from Pnephoros son of Herakleios, of those from Sinaru on the",
        "far side. I report to you how, in the",
        "past <year>, Patellis, of those from Sinaru,",
        "son of Mesthasys, attacking together with others, and taking up",
        "a tool — other men, 15, of those from the same (village) —",
        "the doorkeeper assigned to the watch at the chap-",
        "el of Hellanikos in the temple at Busiris,",
        "the wife of Malephis,",
        "they murdered on the spot. And further, this man's",
        "younger brother Ambesis, together",
        "with Pnephoros son of Petesouchos, who was traveling in the",
        "settlement — setting upon, in brigand fashion,",
        "a certain merchant of those from the Oxyrhynchite —",
        "they stripped and stole from him fleeces",
        "of wool, 150, and 1500 silver drachmas; concerning which, even in",
        "Sinaru itself they were handed over, and, so",
        "that the matter not be paraded in public, were re-",
        "leased.",
      ]),
 dict(key='bgu;4;1189', nlines=14, slug='bgu_4_1189', genre='petitions', label='BGU 4.1189', **HERA,
      name='Petition - Antaios seeks recovery of money he paid as surety',
      date='1 BCE - 1 CE',
      content='Antaios, gymnasiarch of Busiris, having stood surety for two defaulting embankment-decani and been forced to pay 421 drachmas into the treasury, asks the strategos to make the toparch help him recover it from their property',
      trans=[
        "To Theon, strategos and in charge of the revenues,",
        "from Antaios son of Onnophris, gymnasiarch of the vil-",
        "lage of Busiris in the 30th year of Caesar. I became surety",
        "for Theoxenos son of Lykos and Panetbeuis son of Pete-",
        "chon, of the same village, decani",
        "of the embankment near Koma; and, the aforesaid",
        "men having defaulted on (their) appearance, I was com-",
        "pelled by Apollonios, the toparch of the (parts)",
        "around Busi[ris, to p]ay into the treasury on their",
        "behalf 421 silver [d]rachmas and the additional charges",
        "on them. Si[nce], then, the said men have means —",
        "[hous]es and allotments and cattle and",
        "crops — I ask, if it seem good, to instruct the sa(me)",
        "toparch to assist me as I exact (it).",
      ]),
 dict(key='p.oxy;1;108', nlines=40, slug='p_oxy_1_108', genre='documents', label='P.Oxy 1.108', **OXY,
      name='A cook’s meat account - daily deliveries',
      date='28 Sept 215 CE (?)',
      content='A running ledger of a cook’s daily meat deliveries by date: minai of meat, tongues, trotters, kidneys, breast, tripe, snout, ears, over Thoth and the preceding Mesore',
      trans=[
        "Thoth 4, year 24:",
        "of meat, 4 minai,",
        "2 trotters,",
        "one tongue,",
        "one snout.",
        "(Thoth) 6: a tongue-and-jowl.",
        "11: of meat, 2 minai,",
        "one tongue,",
        "2 kidneys.",
        "12: of meat, 1 mina,",
        "one breast.",
        "14: of meat, 2 minai,",
        "1 breast.",
        "16: of meat, 3 minai.",
        "17: of meat, 2 minai,",
        "one tongue.",
        "18: one tongue.",
        "21: tripe.",
        "22:",
        "tripe,",
        "2 kidneys.",
        "23:",
        "of meat, 2 minai,",
        "1 tripe,",
        "2 trotters.",
        "26:",
        "one tongue.",
        "30: one breast.",
        "And before these, Mesore",
        "18: of meat 2 minai, 1 tripe,",
        "2 kidneys. 21: 1 breast.",
        "23: 1 tongue-and-jowl, kid-",
        "neys 2. 24: 2 minai, kid-",
        "neys 2. 25: for Tryphon 2 minai,",
        "1 ear, 1 trotter, 2 kidneys.",
        "29: 2 minai, 2 trotters, a tong-",
        "ue. On the 2nd intercalary day,",
        "a tongue. 3rd: 1 breast.",
        "Account",
        "of a cook.",
      ]),
 dict(key='p.oxy;1;109', nlines=28, slug='p_oxy_1_109', genre='documents', label='P.Oxy 1.109', **OXY,
      name='Inventory of clothing and household goods',
      date='late 3rd-4th century CE',
      content='A list of articles: tunics white and purple, mantles, Tarsian linens, girdles, cloaks, mattresses, pillows, bronze vessels, a Dalmatian tunic, women’s tunics, and 20 minai of silver',
      trans=[
        "Account of articles.",
        "1 white single-nap (cloak).",
        "2 white sleeveless tunics.",
        "2 natural-colored ones.",
        "1 purple sleeveless tunic.",
        "2 white mantles.",
        "1 natural-colored mantle.",
        "2 Tarsian linens.",
        "2 wraps.",
        "2 broad-striped (garments).",
        "2 girdles.",
        "2 cloaks.",
        "2 tunics.",
        "3 mattresses.",
        "3 pillows.",
        "2 coverlets.",
        "a woollen(?) tunic",
        "and a mantle.",
        "1 white tunic.",
        "1 new wrapper.",
        "3 bronze pints.",
        "1 cooler.",
        "2 bronze vessels.",
        "1 Dalmatian (tunic).",
        "Into the Oxyrhynchite:",
        "1 swathe.",
        "2 women's tunics.",
        "20 minai of silver.",
      ]),
 dict(key='bgu;3;852', nlines=20, slug='bgu_3_852', genre='documents', label='BGU 3.852', **SOKN,
      name='Census declaration - four camels',
      date='28 Jan 167 CE',
      content='Tesenouphis and Pakysis of Soknopaiou Nesos register, through a manager, the same four camels for the present 7th year as in the past 6th; countersigned by strategos and royal scribe, counted in agreement',
      trans=[
        "(Soknopaiou Nesos: camels [4].)",
        "[To So-and-so,] to Herminos [...,]",
        "through Pappos, former gymnasiarch, depu[ty],",
        "and to Serenos, royal scribe of the same (division),",
        "through Eudaimon, deputy,",
        "from Tesenouphis son of Teseno-",
        "uphis, elder, called",
        "Seiphon, and Pakysis son",
        "of Tesenouphis, younger, called",
        "Kiales, both from the village",
        "of Soknopaiou Nesos, through the manager",
        "Tesenouphis son of Tesenouphis.",
        "The camels I registered in the past 6th year,",
        "4, I register also for the pres[ent]",
        "7th year. Wherefore I submit (this).",
        "Registered before the strategos: camels 4.",
        "Mecheir 2. Registered before the royal (scribe):",
        "camels 4. Mecheir 3.",
        "Counted, in agreement.",
        "Counted, in agreement.",
      ]),
 dict(key='bgu;3;869', nlines=15, slug='bgu_3_869', genre='documents', label='BGU 3.869', **SOKN,
      name='Census declaration - five camels of a minor',
      date='Jan-Feb 135 CE',
      content='Taouetis, a minor, through her kinsman-manager Satabous, registers the same five full-grown camels at Soknopaiou Nesos for the 19th year of Hadrian as in the past 18th',
      trans=[
        "To [Ar]chias, strategos, an[d]",
        "to Hermeinos, royal scribe,",
        "of the Arsinoite, Herakleides division,",
        "from Taouetis daughter of Har-",
        "pagathos, a minor, with",
        "as manager her kinsman",
        "Satabous son of Satab(ous). The (camels) which",
        "I registered in the past",
        "18th year at the village of [Sokno-]",
        "paiou Nesos, ca[mels]",
        "full-grown, five, the",
        "same — I register (them)",
        "[al]so for the registration of the present",
        "19th year of Hadrian Caesar",
        "[the l]ord.",
      ]),
 dict(key='p.oxy;2;253', nlines=24, slug='p_oxy_2_253', genre='documents', label='P.Oxy 2.253', **OXY,
      name='Notice of anachoresis - tenants fled, leaving no means',
      date='July-Aug 19 CE',
      content='A declaration (with sworn oath by Tiberius Caesar) that certain persons, owning only shares of a house, have withdrawn abroad leaving no other means, asking they be registered among the destitute fugitives',
      trans=[
        "[…]…, regis-",
        "[tered upon t]he previously exist[in]g",
        "[shares belonging to them] of a house in the quarter of Teumenou[this],",
        "[bought fro]m Deesotes, wife",
        "[of M…, son of] Sarapion, in accord-",
        "[ance with the] securities (made out) to her — have with-",
        "[drawn to] foreign parts, no",
        "[o]ther [means belonging to them] existing.",
        "Wherefore [I submit thi]s memorandum, asking",
        "that these be regis[tered] among those who have with-",
        "drawn [and] have no [m]eans,",
        "[fr]om the present 5th year of Tiberius Caesar",
        "Augustus, and the like.",
        "Farewell.",
        "[I, Thoonis son of Ammonio]s, have submitted the memoran-",
        "[dum, and I swear by Tiberius] Caesar Augustus",
        "Imperator, son of the god Zeus Eleutherios",
        "Augustus, that the fore-",
        "[w]ritten things are true, and that no me[a]ns belong",
        "[t]o Ammon[i]os and to the younger",
        "Theon, up to the present",
        "day. If I keep my oath, may it be well with me;",
        "if I [for]swear, the contrary.",
        "Year 5 of Tiberius Caesar Augustus, Mesor[e ..].",
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
    body = HDR.format(label=it['label'], name=it['name'], key=it['key'], tm=r.get('tm', '?'),
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

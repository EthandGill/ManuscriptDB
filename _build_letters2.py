#!/usr/bin/env python3
"""Build letters tranche 2: BGU 3.892/874, BGU 4.1082/1073/1096, P.Oxy 2.291/292."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

SRC = {
    'bgu;3': '_PENDING_bgu3_850-900.json',
    'bgu;4': '_PENDING_bgu4_1050-1100.json',
    'p.oxy;2': '_PENDING_p.oxy2_286-320.json',
}
def load(key):
    for pref, f in SRC.items():
        if key.startswith(pref):
            return json.load(open(f, encoding='utf-8'))[key]
    raise KeyError(key)

ITEMS = [
 dict(key='bgu;3;892', nlines=30, slug='bgu_3_892',
      name='Letter — Perousis to his landlord: the wedding and the pigeons',
      date='2nd century CE', found='Hermopolite nome, Egypt', lat=27.7803, lon=30.8016,
      content='Perousis waited two days at Pake; asks when the wedding is, reports sending forty half-jars and sixty pigeons',
      trans=[
        "To my lord the landholder: Perousis,",
        "very many greetings. …",
        "I heard from Onnophris and",
        "[Th]eon of Pake about your",
        "visit to Pake, and I",
        "sat waiting for two days expect-",
        "ing you, and because of this I could",
        "not come to Toou Pa-",
        "sko. Now, if you are busy with the",
        "wedding — since you could not return",
        "to me — let me know through the",
        "[…]… about the day",
        "on which the wedding takes place, that I may come",
        "up to you; and write to Kollouthos",
        "[…] the fishermen of Kirka, that",
        "[…] to them before I go",
        "up. (I sent?) you forty half-",
        "kadia by Pachymis the archepho-",
        "dos from […], and sixty little",
        "pigeons, safe and sound; and send",
        "me quickly the half-kadia",
        "of Eu…tos the oil-maker, the one from Thallou;",
        "and about whatever you wish done with me out here,",
        "let me know, that I may do it",
        "quickly before I go up.",
        "I pray for your health,",
        "my lord, for many years,",
        "in good spirits and pros-",
        "pering.",
        "To my brother: Perousis.",
      ]),
 dict(key='bgu;3;874', nlines=12, slug='bgu_3_874',
      name='Letter — gold pieces from the deacon, grain from Phoibammon',
      date='4th–7th century CE', found='Arsinoite nome, Fayum, Egypt (?)', lat=29.3084, lon=30.8428,
      content='A Byzantine Christian letter: collect two gold pieces at Narmouthis, get grain from Phoibammon, greetings to the household',
      trans=[
        "⳨ Also at another time I wrote to you to send to Narmouthis and receive",
        "the two gold pieces from the deacon. If you have done this, write me",
        "here. So please send to Phoibammon",
        "and receive grain from him, and learn what is received from him.",
        "And inform the lord Elias my brother, as I informed Petros,",
        "about the matter of which he spoke to me; and he has informed me —",
        "he has reviewed the expenses of the petition. Write me and",
        "I act. Greet warmly your lady mother",
        "and Elias and Romanos my brothers and all those in your",
        "bountiful house, and the lord Euphrantios and his sweetest",
        "children. Do not neglect it, then; we trust in the Master of",
        "all that with the new governor we are coming out there.",
      ]),
 dict(key='bgu;4;1082', nlines=12, slug='bgu_4_1082',
      name='Letter — Petysis orders payment of half a gold solidus',
      date='4th century CE', found='Hermopolis (?), Egypt', lat=27.7803, lon=30.8016,
      content='Petysis instructs Apphynchios and Didymos the carpet-weaver to pay the scribe Pettirios another half nomismation for the ninth indiction',
      trans=[
        "To my lord brother Apphynchios",
        "and Didymos the carpet-weaver:",
        "Petysis son of Pantebes.",
        "Just as I received from you in",
        "the village the half holokottinos,",
        "so now provide to my brother",
        "Pettirios the scribe, for the security-receipt",
        "of the ninth indiction, another half",
        "gold nomismation. Do not neg-",
        "lect it, lord brothers. (2nd hand) We pray for your",
        "health for many years, lord",
        "brothers.",
      ]),
 dict(key='bgu;4;1073', nlines=22, slug='bgu_4_1073',
      name='Letter — the council of Oxyrhynchus confirms an athlete’s immunity',
      date='Jan–Feb 274 CE', found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658,
      content='The city council notifies the property-archive keepers that Aurelius Apollodidymos, enrolled in the sacred synod, holds tax immunity',
      trans=[
        "Copy(?).",
        "The most excellent council of the illustrious and most illustrious city of the Oxyrhynchites,",
        "through Aurelius Euporos also called Agathos Dai-",
        "mon, former kosmetes, exegetes, hypomnemato-",
        "graph of the most illustrious city of the Alexandrians, former prytanis,",
        "and however he is styled, councillor, prytanis in office,",
        "to the keepers of the property-archives, their dearest, greeting:",
        "Aurelius Apollodidy-",
        "mos son of Ploution presented to us his rights, depending",
        "on universal laws, concerning his having been enrolled",
        "in the assembly of the sacred synod,",
        "and, having according to custom done reverence to",
        "the divine, we have all the more confirmed",
        "these to him. Since, then, we judged it conse-",
        "quent to report this openly to you, that you may",
        "know the immunity belonging to him by the",
        "laws and may make the due an-",
        "notation against his name,",
        "this is sent to you, dearest friends.",
        "I pray for your health, dearest friends.",
        "Year 5 of our lord Aurelian",
        "Augustus, Mecheir.",
      ]),
 dict(key='bgu;4;1096', nlines=14, slug='bgu_4_1096',
      name='Letter — Isidoros to Hierax: hand the office books to Sarapion',
      date='c. 38 CE (year uncertain)', found='Arsinoite nome, Fayum, Egypt (?)', lat=29.3084, lon=30.8428,
      content='Isidoros has re-engaged Sarapion as his scribe and orders the account books handed over at once; Doras is dismissed',
      trans=[
        "Isidoros to Hierax his dear-",
        "est, greeting. Since Sarapion",
        "I have got as scribe — whom",
        "I had before, about whom too",
        "I wrote you at another time — you will do",
        "well to hand over to him",
        "the books of the office",
        "at once, and not to make fur-",
        "ther use of Doras, be-",
        "cause I have de-",
        "cided to have Sarapion as my",
        "scribe. So do not do other-",
        "wise. Farewell. Year 2 of G[aius Caesar]",
        "the [lord], month […]",
      ]),
 dict(key='p.oxy;2;291', nlines=15, slug='p_oxy_2_291',
      name='Letter — the strategos Chaireas orders the tax statements ready',
      date='25–26 CE', found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658,
      content='Chaireas tells the dioiketes Tyrannos to write up the grain and money statements of year 12 at once — “act the man and collect”',
      trans=[
        "Chaireas to Tyrannos his dearest,",
        "very many greetings.",
        "[The] statement of the 12th year of Tiberius",
        "Caesar Augustus, in grain and",
        "in silver, write up at once,",
        "since Severus has charged me",
        "with the collection; and I have already writ-",
        "ten [you] to act the man and to collect",
        "until I arrive in good health.",
        "Do [not] neglect it, then, and make ready",
        "also those from the [.. year] up to the 11th year",
        "[for th]e collection, in grain and",
        "[in silver].",
        "Farewell.",
        "To Tyrannos, dioiketes.",
      ]),
 dict(key='p.oxy;2;292', nlines=14, slug='p_oxy_2_292',
      name='Letter of recommendation — Theon commends his brother Herakleides',
      date='c. 25 CE', found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658,
      content='Theon asks the dioiketes Tyrannos to receive his brother Herakleides as recommended — “unharmed by the evil eye”',
      trans=[
        "Theon to Tyrannos the most honored,",
        "very many greetings.",
        "Herakleides, who delivers this",
        "letter to you, is my brother;",
        "wherefore I entreat you with all your pow-",
        "er to hold him as one recommend-",
        "ed. And I have asked also Hermias",
        "my brother in writing to tell [you]",
        "about him. And you will do me the greatest favor",
        "if he wins your notice.",
        "Before all I pray that you have health,",
        "unharmed by the evil eye, faring",
        "excellently. Farewell.",
        "To Tyrannos, dioiketes.",
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
genre:    letters
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
    r = load(it['key'])
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

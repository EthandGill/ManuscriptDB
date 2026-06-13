#!/usr/bin/env python3
"""Build the first petitions: P.Oxy 1.130/131, 2.281/282, P.Tebt 2.439, P.Fay 107."""
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

SRC = {'p.oxy;1;130':'_PENDING_p.oxy1_91-140.json','p.oxy;2;281':'_PENDING_p.oxy2_234-285.json',
       'p.oxy;1;131':'_PENDING_p.oxy1_91-140.json','p.tebt;2;439':'_PENDING_p.tebt2_408-445.json',
       'p.oxy;2;282':'_PENDING_p.oxy2_234-285.json','p.fay;;107':'_PENDING_p.fay_91-140.json'}
OXY = dict(found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658)

ITEMS = [
 dict(key='p.oxy;2;281', nlines=30, slug='p_oxy_2_281', **OXY,
      name='Petition - Syra: her husband squandered the dowry and abandoned her',
      date='20-50 CE',
      content='Syra petitions the archidikastes to compel her husband Sarapion, who beat her, deprived her of necessities and then left her destitute, to return her 200-drachma dowry with half again',
      trans=[
        "To Herakleides, priest and archidi-",
        "kastes and superintendent of the",
        "chrematistai and of the",
        "other tribunals,",
        "from Syra daughter of Theon.",
        "I lived with Sarapion, having given him a dowry",
        "by agreement, on",
        "account of two hundred",
        "silver drachmas. So I, having taken him",
        "into my parents’",
        "dwelling, though he was utterly",
        "penniless, kept myself blameless",
        "toward him in all",
        "things. But Sarapion, having",
        "spent the dowry on whatever",
        "purpose he wished, did not cease",
        "ill-treating me and insult-",
        "[in]g me and laying",
        "his hands (on me), and reducing me to want",
        "of the necessar-",
        "ies, and later",
        "abandoned me, leav-",
        "ing me destitute. Therefore I ask you to order",
        "that he be brought before you",
        "so that he may be compelled,",
        "being held, to repay",
        "me the [d]owry with half",
        "again. For of the",
        "other things [I have against him]",
        "I lay claim [and will lay claim].",
      ]),
 dict(key='p.oxy;2;282', nlines=23, slug='p_oxy_2_282', **OXY,
      name='Petition - Tryphon: his wife left and carried off his property',
      date='29-37 CE',
      content='Tryphon the weaver petitions the strategos Alexandros: he provided for his wife Demetrous beyond his means, but she became estranged, left, and took his belongings; he asks she be made to return them',
      trans=[
        "To A[le]xandros, strategos,",
        "from Tryphon son of Dio-",
        "nysios, of the city of the Oxyrhyn-",
        "[ch]i. I lived",
        "[with] Dem[e]trous daughter of Hera-",
        "kleides, an[d] I for my part",
        "supplied her with what",
        "followed and beyond my means.",
        "But she, becoming estranged",
        "from our common life,",
        "[in the] e[n]d went",
        "[out] and they carried off",
        "our belongings, of which the",
        "itemized list is appended. Therefore I ask",
        "that she be br[o]ught [be]fore you",
        "so that she may meet with what is",
        "[fit], and return to me",
        "our property. For of the",
        "other things which I have",
        "agai[ns]t her I will lay",
        "cla[im a]nd will lay claim. Farewell.",
        "[There ar]e, of the things taken away:",
        "[…]…ion worth 40 (drachmas) …",
      ]),
 dict(key='p.oxy;1;130', nlines=23, slug='p_oxy_1_130', **OXY,
      name='Petition - Anup begs the patrician Apion for relief',
      date='c. 548 CE',
      content='A Byzantine tenant on the Apion estate at Phakra petitions his lord, the dux and patrician Apion, for mercy: his beasts died, he borrowed 15 solidi, and the estate agents will not heed the lord’s order to relieve him',
      trans=[
        "† To my good lord, lover of Christ, lover of the poor, all-",
        "praiseworthy, most magnificent patrician and dux of the Thebaid,",
        "Apion, fr(om) Anup, your pitiable slave, from the property belonging to",
        "it called Phakra.",
        "Nothing unjust or impious does the glorious house of my good",
        "lord possess; rather it is ever full of mercy, pouring out upon the needy",
        "their necessities. Wherefore I too, the pitiable slave of my good lord,",
        "through this my present petition wish to be shown mercy,",
        "(and) that your lordship know how, from fathers and forefathers, I have served",
        "my good lord (and) paid yearly the public dues; and, by God’s",
        "will, in the past eleventh indiction and the past",
        "tenth my beasts died, and I borrowed no little gold,",
        "15 sol(idi), until I could buy the same beasts. But when I came",
        "to my good lord and (when) he came here to have mercy on me, the agents",
        "of my lord would not act according to the command of my good",
        "lord. For if, master, your mercy does not reach me, I cannot stand",
        "on my property and be of use for the landlord’s affairs. And",
        "I beg and entreat your lordship to order that I be shown mercy,",
        "since I have come to great ruin. For I have no other ref-",
        "uge except that of the Master Christ and of your eminence.",
        "And I will send up undying hymns to the Master Christ for the",
        "life of your lordship and of her most magnificent son",
        "Strategios the lord. †",
      ]),
 dict(key='p.oxy;1;131', nlines=27, slug='p_oxy_1_131', **OXY,
      name='Petition - Susneus: a disputed paternal inheritance',
      date='6th-7th century CE',
      content='Susneus of Patani petitions his lord over his father’s estate: his brother David got the mother’s property plus a half-aroura, but now demands a re-division of the whole inheritance',
      trans=[
        "† To my good lord, (next) after God, a petition (and) supplication † from me,",
        "Susneus, your pitiable slave, from Patani. I inform",
        "my good lord of the matter concerning me, which is in this",
        "way. While my father lived he called me and",
        "my brothers, saying that one of you shall hold",
        "the property of your mother Io[..]raphe, and the others are maintained from my property;",
        "and he raised up David my younger",
        "brother, and gave (him) into the holding of my mother.",
        "And as he was about to die, my father ordered that there be given",
        "to that David from his own [pr]operty a half-aroura, saying",
        "that the half-aroura suffices him, since he also has the holding of",
        "his mother. And behold, it is three years today since he died;",
        "and as soon as he died I went to Abraamios the",
        "headman of Klaudianos, and he brought forward the witnesses",
        "who had been present over my father — that is, Julius the elder",
        "and Apollon — and he caused it to be done according to the word of my father;",
        "and year by year I sow my property, and",
        "David my brother sows the property of my mother and",
        "his half-aroura. And today Abraamios, suborned",
        "by the same David, has warned me, saying that unless",
        "my brother takes the property of the mother — save one (aroura) — and the half-aroura",
        "which my father gave him, then again there be re-divided between me and",
        "him whatever my father left me; for my father gave to my mother",
        "110 sol(idi) to divide between me and m[y] brothers,",
        "and these she gave to Elisabet my elder sister. And I beg",
        "my good lord to make provision that, according to what my father said,",
        "the right be safeguarded for me. †",
      ]),
 dict(key='p.tebt;2;439', nlines=15, slug='p_tebt_2_439',
      name='Petition - Zoilos seeks release lest he flee his village',
      date='15 June 151 CE', found='Tebtunis (Arsinoite nome / Fayum), Egypt',
      lat=29.108, lon=30.937,
      content='Zoilos, aged 42, takes refuge with the (epi)strategos asking him to write to the divisional strategos for his release, lest he become a fugitive from his own land; with the official’s endorsement',
      trans=[
        "(1st hand) …[… lest]",
        "I become a fugitive [from my]",
        "own (land), I have taken refuge with you, beg-",
        "ging, if it seem good to you, to order",
        "a letter written to the strategos of the Themistes and",
        "Polemon divisions",
        "to release me, that I may be helped",
        "by you. Prosper.",
        "Zoilos, 42 (years old), (a scar) on a finger of the left hand.",
        "Year 14 of Imperator Caesar Titus",
        "Aelius Hadrianus Antoninus Augustus",
        "Pius, Pauni 21.",
        "(2nd hand) Year 14, Pauni 21.",
        "(3rd hand) No one objecting,",
        "petition the strategos.",
      ]),
 dict(key='p.fay;;107', nlines=17, slug='p_fay_107',
      name='Petition - Papontos reports the theft of hides',
      date='24 Nov 133 CE', found='Theadelphia (Arsinoite nome / Fayum), Egypt',
      lat=29.4333, lon=30.5333,
      content='Papontos, aged about 55, reports that four goatskins and four sheep-fleeces were stolen, asking the village patrol to make the due search and hold the guilty',
      trans=[
        "…[…]…",
        "they stole away",
        "four goat-",
        "skins",
        "and four sheep-fleeces.",
        "On account of which",
        "I ask that order be given to the",
        "patrolman of the village",
        "to make the",
        "due",
        "search and to keep those",
        "found guilty in",
        "custody for the",
        "due",
        "prosecution. Prosper.",
        "Papontos, aged about 55, a scar",
        "on the right eyebrow.",
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
genre:    petitions
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
    elif parts[0] == 'p.tebt':
        label = f"P.Tebt {parts[1]}.{parts[2]}"
    else:
        label = f"P.Oxy {parts[1]}.{parts[2]}"
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

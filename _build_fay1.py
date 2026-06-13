#!/usr/bin/env python3
"""Build P.Fay tranche 1: six Gemellus estate letters (110-114, 120)."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

DATA = json.load(open('_sweep_p.fay_91-140.json', encoding='utf-8'))

COMMON = dict(found='Euhemeria (Arsinoite nome / Fayum), Egypt', lat=29.4333, lon=30.4)

ITEMS = [
 dict(key='p.fay;;110', nlines=35, slug='p_fay_110', **COMMON,
      name='Letter — Gemellus to Epagathos: manure, oil-press, debts to collect',
      date='11 Sept 94 CE',
      content='Estate orders: cart out the manure, dig round the oil-press, flood the allotments, water the olives twice, collect debts with interest',
      trans=[
        "Lucius Bellienus Gemellus",
        "to Epagathos his own, greeting.",
        "You will do well, on receiving my",
        "letter, to have",
        "the manure in it carted out,",
        "so that what you call a store-chamber",
        "be made a depot; and dig deep round the oil-",
        "press on the outside,",
        "so that the oil-press is not",
        "easy to climb into; and sort the manure",
        "off to the dung-heap; and let them",
        "flood all our allot-",
        "ments, that the sheep may bed there,",
        "and let them give the olive-groves their second",
        "watering; and cross over to",
        "Diony[s]ias and find out whether the olive-",
        "grove has been watered twice and forked",
        "over; and if at all not, let it be watered",
        "and … safely forked",
        "over, lest … them fall through; and",
        "having paid(?) … [an]d Psellos, the sitologoi,",
        "…[… and] Chairas the scribe of the",
        "farmers, and Heraklas 90 dr. and interest,",
        "and Cha[ira]s the former tax-collector 24 dr.,",
        "and Didas …, the price of barley, 240 dr. and interest,",
        "and Heron the former foreman two years’ interest,",
        "120 dr. And let the carpenters hang",
        "the doors; and I am sending you the",
        "ropes. Make the arms of the oil-press",
        "double, and those of the de-",
        "pots single. Farewell.",
        "Year 14 of Imperator Caesar Domitian",
        "Augustus Germanicus, month Germanikos 14.",
        "So do not do otherwise.",
        "Deliver to Epagathos from Lucius Bellienus Gemellus.",
      ]),
 dict(key='p.fay;;111', nlines=32, slug='p_fay_111', **COMMON,
      name='Letter — Gemellus scolds Epagathos: two piglets lost on the road',
      date='13 Sept 95 CE',
      content='“I blame you greatly” — two piglets dead from the jolting of the road; buy 20 artabas of lotus at Dionysias whatever the price',
      trans=[
        "Lucius Bellenus Gemellus",
        "to Epagathos his own, greeting.",
        "I blame you greatly: you",
        "lost two piglets from the",
        "jolting of the road, though you have",
        "ten working beasts",
        "in the village. Heraklidas the don-",
        "key-driver spread the blame a-",
        "round, saying that you told him",
        "to drive the piglets on foot.",
        "Moreover, I ordered you",
        "to stay at Dio[nys]ias two",
        "days, until you bought",
        "20 artabas of lotus. They say the",
        "lotus is to be had at Diony-",
        "sia[s] at 18 dr. At whatever",
        "price you find it, by all",
        "means buy the 20 artabas of lotus —",
        "count it urgent.",
        "Push on the flooding",
        "of all the olive-",
        "groves, [and] assign at Sen-",
        "[theus’] a workman for the green-",
        "stuff, to flood; and water",
        "the row of plants",
        "at the prophet’s.",
        "So do not do otherwise.",
        "Farewell. Year 15 of Imperator",
        "Caesar Domitian Augus[tus]",
        "Germanicus, month Germanik(os).",
        "[To Epagathos] his own,",
        "[from Lucius Bellen]us Gemellus.",
      ]),
 dict(key='p.fay;;112', nlines=26, slug='p_fay_112', **COMMON,
      name='Letter — Gemellus to Epagathos: dig the olives, reap Apias — “I blame you greatly”',
      date='21 May 99 CE',
      content='Push the digging and double-hoeing; the strip at Apias still half-reaped; check the Dionysias grove; don’t thresh till I write',
      trans=[
        "Lucius Bellenus Gemellus to Epagathos",
        "his own, greeting. You will do well to push on the dig-",
        "ging of the olive-groves and the loosening-round",
        "and double-hoeing of the olive-groves, and [the] fal-",
        "lows hoe round and double-hoe, press-",
        "ing the ox-driver",
        "so that each",
        "day he renders his work; and do not glue the tally",
        "of the ox-teams to the …(?). The strip at",
        "Apias to this day you have not reaped but have ne-",
        "glected, and so far you have reaped the half",
        "of it, waiting on the meas-",
        "urer Zoilos — and do not let him put",
        "you to shame: you have left it unreaped to this day.",
        "Therefore I blame you greatly. Find",
        "out whether the olive-grove of Dionysias has been dug;",
        "if not, push on its digging",
        "in two days; for it pays that it",
        "be dug …(?). Let them not hurry",
        "to thresh …(?) and the Sentheus plot",
        "until I write. Do not crush all the threshing-floors",
        "for the present. So do not do otherwise.",
        "Farewell. Greet Heron and Orsenouphis",
        "and all those at home. Year 2 of Imperator",
        "Caesar Nerva Trajan Augustus Germanicus,",
        "Pachon 26.",
      ]),
 dict(key='p.fay;;113', nlines=15, slug='p_fay_113', **COMMON,
      name='Letter — Gemellus to his son Sabinus: send Pindaros to thin the olives',
      date='c. 100 CE',
      content='Hermonax wants the field-guard Pindaros to mark which trees to cut at Kerkesoucha; fish for 12 dr. for the feast',
      trans=[
        "Lucius Bellenus Gemellus",
        "to Sabinus his son, greeting.",
        "By all means send Pin-",
        "daros the field-guard of",
        "Dionys[i]as, or his father,",
        "since Hermonax asked me that",
        "he might look over his olive-",
        "grove at Kerkesoucha, since",
        "it is thick with trees, and out of them",
        "he wants to cut some trees. So you",
        "will do well to send him",
        "at once; and on the 18th or 19th",
        "send fish to the city for 12 dr.",
        "for the fortieth-day feast of the little",
        "[…] son(?) of Gemella.",
      ]),
 dict(key='p.fay;;114', nlines=27, slug='p_fay_114', **COMMON,
      name='Letter — Gemellus to Sabinus: Pindaros again, and fish for the birthday',
      date='14 Dec 100 CE',
      content='Repeat order: send Pindaros to inspect Hermonax’ thick olive-grove; fish on the 24th or 25th for Gemella’s birthday — “don’t fool away your olive-shaking”',
      trans=[
        "Lucius Bellenus Gemellus",
        "to Sabinus his son, greeting.",
        "Do well then: on receiv-",
        "ing my letter,",
        "send me Pindaros",
        "to the city, the field-",
        "guard of Dionysias,",
        "since Hermo-",
        "nax asked me that he might",
        "take him to Kerkesoucha",
        "to look over his",
        "olive-grove, since",
        "it is thick, and",
        "he wants to cut",
        "trees out of it, so that",
        "what is to be cut",
        "be cut with skill; and",
        "send the fish",
        "on the 24th or 25th for",
        "the birthday of Gemella.",
        "So do not fool away",
        "your olive-shaking.",
        "Farewell. Year 4 of Imperator",
        "Caesar Nerva",
        "Trajan Augustus",
        "Germanicus, Choiak",
        "18.",
      ]),
 dict(key='p.fay;;120', nlines=14, slug='p_fay_120', **COMMON,
      name='Letter — Gemellus to Epagathos: send pitch-forks and winnowing-shovels',
      date='c. 100 CE',
      content='Send two pitch-forks, two winnowing-shovels and a scoop — “I am stuck without them at Aphroditopolis”; reap Apias',
      trans=[
        "Lucius Bellenus Gemell[us]",
        "to Epagathos his [own], gr[eeting].",
        "Do well to s[e]nd me two",
        "pitch-[f]orks and two winnowing-",
        "shovels and one scoop, since I",
        "am stuck without them at Aphro-",
        "dites Polis; and reap the",
        "s[t]rip at Apias, and re-",
        "lease the sheaves at once to A…,",
        "and dig the olive-groves",
        "at Apias. If",
        "[…] the ox-team from the",
        "[…]… you will",
        "send […]",
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
    r = DATA[it['key']]
    gk = [polish(l) for l in clean(r['greek'])][:it['nlines']]
    gk = [l for l in gk if l]
    tr = it['trans']
    assert len(gk) == len(tr), f"{it['key']}: greek {len(gk)} != trans {len(tr)}"
    num = it['key'].split(';')[2]
    label = f"P.Fay. {num}"
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

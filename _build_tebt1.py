#!/usr/bin/env python3
"""Build P.Tebt 2 letters: 411-421."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

DATA = json.load(open('_PENDING_p.tebt2_408-445.json', encoding='utf-8'))
TEB = dict(found='Tebtunis (Arsinoite nome / Fayum), Egypt', lat=29.108, lon=30.937)

ITEMS = [
 dict(key='p.tebt;2;411', nlines=16, slug='p_tebt_2_411', **TEB,
      name='Letter — Paulinos: “the epistrategos is asking for you”',
      date='2nd century CE',
      content='Come up that very hour — he was ready to post a proclamation; “do not be alarmed: when you arrive you will know what it is about”',
      trans=[
        "Pauleinos to Heron his",
        "son, greeting.",
        "The moment you receive my",
        "letter, that very hour",
        "come up, for his excellency the",
        "epistrategos has been asking for",
        "you insistently. He was even ready",
        "to post a proclamation, had I not",
        "promised that today",
        "you would present yourself. So do not",
        "do otherwise — yet do not",
        "be at all alarmed:",
        "when you arrive you will know",
        "what it is about.",
        "I pray for your health.",
        "Pach(on) 3.",
      ]),
 dict(key='p.tebt;2;413', nlines=20, slug='p_tebt_2_413', **TEB,
      name='Letter — Aphrodite to her lady: errands done, parcels sent',
      date='2nd–3rd century CE',
      content='A servant reports: the sealed roll delivered, the leather garment cut, Puteolan vessels and warp-reeds on the way — “do not think I have neglected your orders”',
      trans=[
        "Aphodite to Arsinoes her lady, many greetings.",
        "I make obeisance for you before the gods here",
        "each day, praying for your health.",
        "I at once restored to Mamertinus’ (wife)",
        "what you sent over, and Sere-",
        "nion received the little roll, sealed. Do not think, lad[y,]",
        "that I have neglected your orders. Euphrosyne,",
        "after cutting out the little leather garment,",
        "pressed it on Isidoros. And you will receive by Arteus",
        "both the hand-cloth and … wraps and fo[ur(?)]",
        "Puteolan (vessels) and one fig-basket and 5 reeds",
        "of warp-thread — it was agreed that these be sent you",
        "out of her wages. I have received the",
        "little cage from Didymos. We are slow in",
        "sending you letters because we have no one",
        "… (to carry them). Anbrosia greets you and […]",
        "…[. a]nd Athenodoros and Thermouthis and her house-",
        "hold, and all your friends greet",
        "those who love you.",
        "Deliver — from Apodite, to the lady.",
      ]),
 dict(key='p.tebt;2;414', nlines=39, slug='p_tebt_2_414', **TEB,
      name='Letter — Thenpetsokis: fifty figs and a household inventory',
      date='2nd century CE',
      content='Sent: 50 dried figs; to hand over: the loom, weaver’s reeds, mortar, kneading-troughs, lamp-stand, the child’s feeder and the big case',
      trans=[
        "Receive from Tephersais fifty",
        "dried figs.",
        "Thenpetsokis to Thenapynchis",
        "her sister, very many greet[ings].",
        "Before all I pray that you are in",
        "health, and your children an[d]",
        "Pasis the little chief. I sent you",
        "by Protas 50 dried figs;",
        "had I not long been ill, I would have sent",
        "to you (before); and if I do nicely, I will",
        "send your daughter a kotyle of iris-perfume.",
        "You will gi[ve] Tephersais the loom",
        "and the …(?) and the [……]",
        "of the weaver’s reeds",
        "and the …(?) and the mortar",
        "and the two kneading-troughs and the bas-",
        "kets of the papers and the little",
        "…(?) and the cup and the",
        "lamp-stand and the little basket with what",
        "is in it at the bottom, and the child’s feed-",
        "er and the big case.",
        "Kotos shall give Tephersais the",
        "box that I lent him,",
        "for it does not belong to the brother of",
        "your mother. I greet you",
        "and your brothers. And let the daugh-",
        "ter of Kephalas give the measure",
        "to Tephersais; let her sell it and send",
        "me the money, since I am coming.",
        "I greet Aphrodite",
        "our mother. The wine-press is",
        "Agathangelos’, so let it be given to the",
        "children. You will speak to the wife of the",
        "tinsmith Ameimon about",
        "your son. You will give the wooden",
        "stool and the little door and the little",
        "lamp.",
        "Del[ive]r to Thenapynchis",
        "the wife of the potter.",
      ]),
 dict(key='p.tebt;2;416', nlines=24, slug='p_tebt_2_416',
      name='Letter — Kalleas, from Alexandria: “I came to worship”',
      date='3rd century CE', found='Alexandria, Egypt (found at Tebtunis)',
      lat=31.2, lon=29.9,
      content='Two notes on one sheet: don’t believe people saying I’ll stay in Alexandria; and — look after my wife until I come, let her want for nothing',
      trans=[
        "Kallea(s) to Sarapias his sis-",
        "ter, greeting.",
        "I want you to know that I have",
        "arrived in Alexandria.",
        "So do not be faint-hearted that I",
        "mean to stay at Antinoou. I",
        "came to Alexandria to wor-",
        "[s]hip. So do not listen to peo-",
        "ple (saying) that I mean to stay",
        "here: I am coming to you",
        "quickly, to the country.",
        "Kallea(s) to Protous his sister,",
        "greeting.",
        "Do everything to look after",
        "my wife until I ar-",
        "rive; and tell Akoutas",
        "my brother too that, if my wife",
        "has need of anything, he should",
        "supply her need",
        "until I come — let her go seek-",
        "ing nothing. Greet the children of",
        "my sister.",
        "I pray for your health.",
        "Deli(ver) to Sarap[i]as f(rom) Kallea(s).",
      ]),
 dict(key='p.tebt;2;420', nlines=30, slug='p_tebt_2_420', **TEB,
      name='Letter — Aurelius Sarapion: “I am out of pocket — send my 52 drachmas”',
      date='3rd century CE',
      content='Shut up in the account-bureau, he bought two rolls for the grain person-lists; demands his money back and barley besides',
      trans=[
        "Aure[liu]s Sarapion to Polion",
        "his brother and Diogenes",
        "his father, very many greetings.",
        "You know that I am out of pocket, and",
        "without reason you went off from me with-",
        "out giving me coppers. I bought",
        "2 rolls for the person-",
        "lists of the grain-dues of the royal",
        "(scribe), and 28 dr. for the agreement",
        "of the …, again for the royal",
        "(scribe). So do everything — as",
        "there is necessity — send me",
        "my 52 dr.; and collect for me too,",
        "on my account, another 60 dr., for I have",
        "need: the … is half done.",
        "Without fail then, my lord brother",
        "Polion, remember me — what I too",
        "have done for you from beginning to",
        "end, and I serve you still. They have urged",
        "my brother to",
        "come to you about the bar-",
        "ley; and tell Diogenes that he too",
        "should give an artaba of barley on the ac-",
        "count of supplies. So give your con-",
        "sent, that it be fetched up without fail,",
        "for I am shut up till",
        "today in the account-bureau;",
        "and let me know without fail",
        "what you have done about me. I pray for your health.",
        "[To …]on my brother — Sarapi(on).",
      ]),
 dict(key='p.tebt;2;421', nlines=14, slug='p_tebt_2_421', **TEB,
      name='Letter — Apion: “come at once, your sister is ailing”',
      date='3rd century CE',
      content='Drop everything and come; bring her white tunic, but the turquoise one sell or leave to your daughter as you please',
      trans=[
        "Apion to Didymos, greeting. Putting off",
        "everything, at once, the moment",
        "you receive this letter of mine,",
        "come to me, since your sister",
        "is ailing. And her white",
        "tunic, the one you have — bring",
        "it when you come; but the turquoise one",
        "do n[ot] bring — rather, if you want to sell",
        "it, sell it; if you want to leave it",
        "to yo[ur] daughter, leave it. But do not neg-",
        "lect her at all, and do not trouble your",
        "w[if]e or the children; and when you come,",
        "come to Theogenis.",
        "I pray for your health.",
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
    label = f"P.Tebt 2.{num}"
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

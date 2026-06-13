#!/usr/bin/env python3
"""Build P.Oxy 3 letters: 526-533."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

DATA = json.load(open('_PENDING_p.oxy3_485-534.json', encoding='utf-8'))
OXY = dict(found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658)

ITEMS = [
 dict(key='p.oxy;3;528', nlines=26, slug='p_oxy_3_528', **OXY,
      name='Letter — Serenos to Isidora: “weeping by night, lamenting by day”',
      date='2nd century CE',
      content='“Since you went out from me I have kept mourning… you sent me letters that could move a stone.” Serenos begs Isidora to say whether she is coming',
      trans=[
        "Serenos to Isidora [his sis-]",
        "ter and lady, very many [greetings].",
        "Before all I pray [for your heal-]",
        "th, and each [day] and",
        "evening I make obeisance for you",
        "before Thoeris who loves you. I want you",
        "to know that since you went out from me",
        "I have kept mourning, weeping by night",
        "and lamenting by day. Since the 12th of Phaophi, when",
        "I bathed with you, I did not bathe",
        "nor anoint myself until the 12th of Hathyr; and you sent",
        "me letters that could move a",
        "stone — so much have your words stir-",
        "red me. That very hour I wrote",
        "back to you, and gave it on the 12th, sealed up",
        "together with your letters.",
        "But apart from your words and let-",
        "ters — “Kolobos has made me a whore!” —",
        "he said: “Your wife sent me word",
        "that he himself sold the little",
        "chain and himself set me on the",
        "boat.” You say these words so that",
        "I be no longer trusted for my lading.",
        "See how many times I have sent to you! Whether you come",
        "or do not come, let me know.",
        "Deliver to Isidora f(rom) Serenos.",
      ]),
 dict(key='p.oxy;3;531', nlines=30, slug='p_oxy_3_531', **OXY,
      name='Letter — Cornelius to his son Hierax: “attend only to your books”',
      date='2nd century CE',
      content='A father’s advice to his student son: quarrel with no one, study, white clothes with the purple cloaks, allowances listed by name',
      trans=[
        "Cornelius to Hierax his sweetest son,",
        "greeting.",
        "We all greet you warmly, all those at home, and",
        "(we greet) all those with you. About the man you write",
        "me of so often: take no notice of him",
        "until I come to you, with good fortune, with Ves-",
        "tinus and the donkeys. For if the gods will,",
        "I shall come to you quickly after the month Mecheir,",
        "since I have pressing business in hand. See that you",
        "quarrel with none of the people in the house, but",
        "attend only to your books, studying,",
        "and from them you will have profit. Receive by On-",
        "nophras the white clothes that can",
        "be worn with the purple cloaks,",
        "the others you will wear with the myrtle-colored ones.",
        "By Anoubas I will send you both money and",
        "monthly supplies and the other pair, the scarlet ones.",
        "You won us over with the little fish; their",
        "price too I will send you by Anoubas — still,",
        "until Anoubas comes to you, pay out from your own",
        "bronze your allowance and your people’s,",
        "until I send it. For the month Tybi there is:",
        "for you, what you like; for Phronimos 16 dr.; for Abask(antos’) people",
        "and for Myron 9 dr.; for Sekoundos 12 dr. Send",
        "Phronimos to Asklepiades in my",
        "name, and let him take from him the an-",
        "swer to the letter I wrote him, and send it.",
        "Tell me what you want. Farewell, my child.",
        "Tybi 16.",
        "To Hierax my [s]on, from Cornelius his father.",
      ]),
 dict(key='p.oxy;3;532', nlines=24, slug='p_oxy_3_532', **OXY,
      name='Letter — Herakleides demands his twenty drachmas',
      date='2nd century CE',
      content='Pay the bearer at once, “or you will make me come and have it out with you… you did not stay, held fast by a bad conscience”',
      trans=[
        "Herakleides to Hatres",
        "his dear(est), greeting.",
        "You ought, even without my",
        "having written you by Saetos,",
        "to have sent up the 20 dr., knowing",
        "that I transferred them on the spot",
        "to my partners;",
        "but you have waited all",
        "this time without pay-",
        "ing. So, of necessity, to the man",
        "who hands you this let-",
        "ter, at once",
        "pay it, so that you make",
        "me too untroubled.",
        "See then that you do not do otherwise",
        "and make me come",
        "to you to have it out",
        "with you. For in Pao-",
        "mis that time I found you, and",
        "though I wished to treat you",
        "kindly, you did not",
        "stay — by a bad",
        "conscience held",
        "fast.",
      ]),
 dict(key='p.oxy;3;533', nlines=34, slug='p_oxy_3_533', **OXY,
      name='Letter — Apion to his sons: claims, leases, wheat and wine',
      date='late 2nd–early 3rd century CE',
      content='A landowner’s long instruction list: publish the claim-notices before Phaophi, don’t lease the house to young men, collect the wheat, greet everyone by name',
      trans=[
        "Apion to Apion his son and Horion his dearest, very many greetings.",
        "Before all I pray that you are in health, with your children and wives. All that",
        "I wrote in the other letter — so as not to write the same again — I write to Horion too. I sent",
        "to you",
        "by Eutyches of Ision Tryphonos 3 notices-of-claim, 2 against the farmers of Maxi-",
        "mus, the other against Diogenes the (son) of Belee.; publish them at once before",
        "Phaoph[i, s]o they do not run past their term. Others were sent up to Panechotes the lawyer, from whom",
        "you will fetch them — and give him 64 dr. Sell the hay-seed, and ask",
        "O.ph.les whether he has need of that from Tampitei. My revenues collected",
        "through the farmers: either let them be reckoned at the treasury on deposit, or let them be in safe keeping",
        "with the farmers, so that, the gods willing, if they are released we have no entangle-",
        "ment with our adversary — or let the risk of them rest on the farmers. The",
        "house of T..bios do not lease to anyone, except perhaps to a woman meaning to live",
        "in it; … for it is […] to expose such a house to young",
        "men — so we get no vexations and no ill-will. Tell Zoilos the farmer from Sento:",
        "“See to the bronze according to the agreements.” Tell the twins too:",
        "“See",
        "to the cash,” and likewise Apollonios and Dionysios; if you are able, send",
        "to Pa[ke]rke-East, to Pausiris the donkey-driver: “Just as you arranged with",
        "me, give the jars of wine — and let them keep their pledged word.” Take over from",
        "Harthonis the priest the 20 artabas of wheat, and from Zoilos the farmer of Sento the 5 artabas of wheat he has",
        "borrowed from me. Look up in the strategos’ account-office the letter of the dioiketes",
        "written in the month Thoth about names being sent in, in my stead, for the allotment of the",
        "collector-",
        "ship. Tell Serenos at the camel-yard: “See to the bronze.” Tell Hermias",
        "the scribe of the money-collectors of Ision Panga: “Transfer the wheat you owe me, or",
        "whatever",
        "you approve.” Let Herakleides son of Hermaiskos repay the 6 artabas of wheat on deposit. Tell Dio-",
        "nysios son of Epimachos, former chief priest, that I petitioned the dioiketes about the revenue,",
        "that it be credited against the debt of Sarapion son of Phanias. Greet Statia my daughter",
        "and Herakleides and Apion my sons. Greet little Serenos and Kopreus",
        "and all ours by name. Amarantos and Zmaragdos greet you.",
        "I pray for your health.",
        "Deliver to Apion my son and Horion.",
      ]),
 dict(key='p.oxy;3;526', nlines=14, slug='p_oxy_3_526', **OXY,
      name='Letter — Kyrillos: “I was not unfeeling to leave you”',
      date='first half of 2nd century CE',
      content='An apology for sudden departure, with a proverb about tenfold interest; “I am going up with the dancer — I would not break my word”',
      trans=[
        "Greetings, Kalokairos —",
        "I, Kyrillos, address",
        "you. I was not un-",
        "feeling, to leave you",
        "without reason; for no one,",
        "collecting in Tybi his",
        "interest tenfold, re-",
        "ceives the principal. [But]",
        "I am going up with [the dan-]",
        "cer; even if he were not go-",
        "ing up, I would not break",
        "my word.",
        "Good fortune.",
        "Deli(ver) to Kalokairos.",
      ]),
 dict(key='p.oxy;3;527', nlines=10, slug='p_oxy_3_527', **OXY,
      name='Letter — Hatres offers the fuller Serenus for a day’s work',
      date='2nd–early 3rd century CE',
      content='“If you need him, send an attendant for him today, the 19th — see you don’t neglect it, for I am holding him”',
      trans=[
        "Hatres to Heras his brother, greeting.",
        "As you instructed me about Serenus",
        "the fuller, the one working with",
        "Phileas: if you have need of him, send",
        "an attendant for him today, that",
        "is the 19th. {For I am holding him} But",
        "see that you do not neglect it, for I am hold-",
        "ing him.",
        "I pray that you fare well and prosper.",
        "Deli(ver) to [He]ras.",
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
    label = f"P.Oxy 3.{num}"
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

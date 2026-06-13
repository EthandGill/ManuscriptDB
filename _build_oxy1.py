#!/usr/bin/env python3
"""Build P.Oxy 1 letters: 113-121 incl. Eirene's consolation and the boy Theon."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

DATA = json.load(open('_sweep_p.oxy_1_91-140.json', encoding='utf-8'))
OXY = dict(found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658)

ITEMS = [
 dict(key='p.oxy;1;115', nlines=13, slug='p_oxy_1_115', **OXY,
      name='Letter of consolation — Eirene to Taonnophris and Philon',
      date='2nd century CE',
      content='“I wept over the blessed one as I wept for Didymas… but there is nothing anyone can do in the face of such things. Comfort one another.”',
      trans=[
        "Eirene to Taonnophris and Philon,",
        "take heart.",
        "I was as grieved and wept over",
        "the blessed one as I wept",
        "for Didymas, and everything that was fit-",
        "ting I did, and so did all",
        "my people — Epaphrodeitos and Thermou-",
        "thion and Philion and Apollonios",
        "and Plantas. But still, there is no-",
        "thing anyone can do in the face of such things.",
        "So comfort one another.",
        "Fare well. Hathyr 30.",
        "To Taonnophris and Philon.",
      ]),
 dict(key='p.oxy;1;119', nlines=18, slug='p_oxy_1_119', **OXY,
      name='Letter — the boy Theon’s tantrum: “take me to Alexandria!”',
      date='2nd–3rd century CE',
      content='“If you won’t take me with you to Alexandria, I won’t write you, I won’t speak to you… If you don’t send for me, I won’t eat, I won’t drink. There!”',
      trans=[
        "Theon to Theon his father, greeting.",
        "A fine thing you did: you didn’t take me with",
        "you to the city! If you won’t take <me> with",
        "you to Alexandria, I won’t write you a",
        "letter, I won’t speak to you, I won’t wish you health,",
        "and then, if you go to Alexandria, I will",
        "not take your hand, nor greet you a-",
        "gain after that. If you won’t take m[e],",
        "that’s what happens. And my mother said to Ar-",
        "chelaos: “He drives me mad — take him away!”",
        "And a fine thing you did: you sent me gifts —",
        "big ones! — husks!(?) They fooled us there",
        "on the 12th, the day you sailed. Well then, send for",
        "me, I beg you. If you don’t send, I won’t",
        "eat, I won’t drink. There!",
        "I pray for your health.",
        "Tybi 18.",
        "Deliver to Theon [fr]om Theonas his son.",
      ]),
 dict(key='p.oxy;1;116', nlines=22, slug='p_oxy_1_116', **OXY,
      name='Letter — Eirene: 340 drachmas paid, dates and pomegranates sent',
      date='2nd century CE',
      content='Money given to Kalokairos on Dionysios’ account; Ombite dates and twenty-five pomegranates sent sealed in the clothes-basket',
      trans=[
        "Eirene to Taonnophris and Philon.",
        "I have given Kalokairos, on the account",
        "of Dionysios, 340 dr., since he wrote me",
        "to give him as much as he",
        "should want. So, being so good,",
        "give them to Parammon our work-",
        "man, and if he still has",
        "need, supply him with as much as he",
        "wants, and quickly send him",
        "off. I sent you in my clothes-",
        "basket a measure of Ombite",
        "date(s) and twenty-five pomegranates,",
        "by Kalokairos, seal(ed). Be so",
        "good as to send me back in",
        "it cleaned stuff worth two drachmas, since",
        "I have urgent need of it.",
        "I sent you by the same Kalo-",
        "kairo(s) a b[o]x of smooth fine",
        "grapes and a basket of fine",
        "dates, seal(ed).",
        "Farewell. Hathyr 30.",
        "To Taonnophris and Philon.",
      ]),
 dict(key='p.oxy;1;113', nlines=33, slug='p_oxy_1_113', **OXY,
      name='Letter — Korbolon: the key, a color pattern, and big cheeses',
      date='2nd century CE',
      content='A key and press-lid sent by camel-man; buy violet-white dye to match the pattern before the tunic is woven; “I wanted little cheeses, not big ones”',
      trans=[
        "Korbolon to [Herakleid(es)] his l[o]rd,",
        "g[reeting].",
        "I sent you by Hor[ion] the key and",
        "by Onnophris, camel-man of Apol(lonios), the press-lid. I folded up",
        "with that letter a pattern of white-violet;",
        "so, prithee, you will do",
        "well to buy me 2 drachmas’ worth, and send it",
        "to me quickly by whomever you find, since the tu-",
        "nic is about to be woven. I received",
        "everything you wrote that I would receive,",
        "from Onnophris, intact. I sent you",
        "by the same Onnophris six choinikes of fine",
        "apples. I give thanks to all the gods, knowing",
        "that I learned Ploution had turned up",
        "in the Oxyrhynchite nome.",
        "Do not think I have been careless of the key;",
        "the reason is rather this: that the",
        "smith is far from us.",
        "As for the things I had written you to send",
        "me by Korbolon, I wonder how",
        "you did not see fit to send them — and",
        "that when I needed them for a feast.",
        "Prithee, buy me a silver",
        "seal-ring, and send it to me quickly. See to it,",
        "until Onnophris buys",
        "for me what Eirene’s mother told him. I told him that Syntrophos said to give nothing",
        "more",
        "to Amarantos on my account from now on. Let me know what you gave him, that I may settle",
        "accounts with him; and if not, I am coming out with my son on this very account.",
        "I had from Korbolon the big cheeses — but I did not want big ones;",
        "little ones I wanted. And whatever you want, let me know — I’ll gladly do it. Farewell.",
        "Pauni 1. Send me one obol’s worth of cakes for my sister’s boy.",
        "To Herakleid(es) son of Ammo(nios), my lord.",
      ]),
 dict(key='p.oxy;1;114', nlines=20, slug='p_oxy_1_114', **OXY,
      name='Letter — Eunoia: redeem my pledged capes, bracelets and Aphrodite',
      date='2nd–3rd century CE',
      content='An inventory in pawn at Sarapion’s for two minas — leather hooded capes, true-purple cloth, bracelets, a tin flask, an Aphrodite figure',
      trans=[
        "the …(?) …[…]… Now",
        "let it be your care to redeem my things from Sara-",
        "pion. They lie pledged for 2 minas; I have paid the",
        "interest up to Epeiph, at a stater per mina:",
        "a frankincense-colored leather hooded cape, an onyx-colored",
        "leather hooded cape, a tunic and a white hooded cape",
        "of true purple, a kerchief with Laconian stripe,",
        "a purple-bordered linen cloth, 2 bracelets, a necklace,",
        "a coverlet, an Aphrodite, a bowl, a tin",
        "flask, a big one, and a jar. From Onetor",
        "fetch the 2 armlets. They lie pledged for eight “hands”",
        "since Tybi of last year, at a stater per mina. If",
        "the cash does not suffice — through the negligence of our lady",
        "Theagenis — if then the cash does not suf-",
        "fice, sell the bracelets to make up the",
        "sum. Greet warmly Aia and Eutychia",
        "— I pray for [y]our health — and Alexandra. Xanthilla greets",
        "Aia and all",
        "hers.",
        "[…] ✗ from Eunoi[a].",
      ]),
 dict(key='p.oxy;1;121', nlines=28, slug='p_oxy_1_121', **OXY,
      name='Letter — Isidoros: dig up the acacias, keep the bulls working',
      date='3rd century CE',
      content='The two acacias must be dug round today; the bulls and the carpenters must not stand idle — “keep at them”',
      trans=[
        "Isidoros to Aurelius his",
        "brother, very many greetings.",
        "As I told you about the",
        "two acacias, that they should",
        "give them to us: this very",
        "day let them be dug",
        "round. Let Phaneias himself",
        "make them be dug up.",
        "If he won’t, write me",
        "so I know. For perhaps",
        "tomorrow we are coming",
        "to seal. So hurry",
        "this, that I may know. As for",
        "the bulls — let them",
        "work; do not let them",
        "be idle at all.",
        "The branches — bring them",
        "all into the road, so that",
        "he may tie them three by three and",
        "drag them off. Do it so —",
        "it pays. Take no notice",
        "of their owners;",
        "perhaps I’ll give him nothing —",
        "(though) I’m doing a great thing",
        "for them. The carpenters —",
        "do not let them be idle at all;",
        "keep at them. I pray",
        "for your health.",
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

#!/usr/bin/env python3
"""Build P.Fay tranche 2: Gemellus/Sabinus archive letters 115-124."""
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
 dict(key='p.fay;;115', nlines=23, slug='p_fay_115', **COMMON,
      name='Letter — Gemellus: buy two well-bred piglets for Sabinus’ birthday',
      date='21 Aug 101 CE',
      content='Buy two well-bred piglets to raise at home for sacrifice at Sabinus’ birthday; send a solid broad strap for the ox-team at once',
      trans=[
        "[…]… [… ex-]",
        "pense and […]…",
        "guard. Buy us",
        "two well-bred piglets",
        "for raising at home,",
        "since we intend …",
        "to sacrifice piglets at",
        "the birthday of Sabinus.",
        "So do not do otherwise.",
        "Farewell. Greet Orse-",
        "nouphis and Heron",
        "and all those at home.",
        "Year 4 of Trajan the lord,",
        "month Kaisareios 28.",
        "Send me a …(?) for the",
        "ox-team to Aphrodites",
        "Polis, solid and broad,",
        "since the one it has is cut",
        "and the ox-driver",
        "is stuck — at once.",
        "✗ Del[i]ver to Epagath(os)",
        "from [L]ucius Bellenus",
        "Gemellus.",
      ]),
 dict(key='p.fay;;116', nlines=24, slug='p_fay_116', **COMMON,
      name='Letter — Gemellus: pickle thirty fish and send olives to the city',
      date='2 Dec 104 CE',
      content='Look out thirty phagroi or korakinoi, pickle and send them; Gemellus is going to the city for the little one until the 15th of Choiak',
      trans=[
        "[Luci]us Bellenus Gemellus",
        "to [Epag]athos his own, greeting.",
        "[So] do well: look out thir-",
        "ty pha[g]roi or thirty kora-",
        "kinoi, and",
        "[pick]ling them, send them to me",
        "[at t]he city, and get",
        "forty fine […],",
        "since I am planning",
        "to go off [to the] city for the sake",
        "[of] the little one and for the sake of that",
        "pending matter, until",
        "the fifteenth",
        "of the present month",
        "[Choia]k; and if you can, send",
        "an ar[taba] of olives …",
        "[…] you send, so that",
        "we may send to my [bro]ther. So do",
        "[not] do otherwise. If",
        "I [go a]way I will send for",
        "[you, th]at I may greet you.",
        "[Fare]well. Year 8 of Trajan",
        "[Caes]ar the lord, Choiak",
        "6.",
      ]),
 dict(key='p.fay;;118', nlines=19, slug='p_fay_118', **COMMON,
      name='Letter — Gemellus: water the grove, buy birds for the feast',
      date='6 Nov 110 CE',
      content='Go to the sowing-overseer at Dionysias; buy the customary gifts — especially for the strategoi — and the little birds for the feast',
      trans=[
        "[…] go to Diony-",
        "sias, to Psiathas the sowing-overseer,",
        "until you water the olive-grove there; and buy",
        "for us, for the sending to those at the fes-",
        "tival to whom we are accustomed to send, espe-",
        "cially the strategoi. Two days ahead buy",
        "the little birds for the feast, and",
        "send them; and the rest send",
        "to the city with one carrying the sacks, since",
        "the beasts are about to cart dung at Psennoph-",
        "ris — with him bringing the slings(?) and little sie-",
        "ves(?), as if for wood-cutting. I am putting six arouras",
        "into Psennophris. If the beasts come up,",
        "load them with cabbage and wood.",
        "So do not do otherwise. Stay there until you water",
        "the seven-aroura piece of the olive-grov[e]. Greet",
        "all who love you in truth.",
        "Farewell. Year 14 of Tra[j]an Caesar the lord,",
        "Hathyr 10.",
      ]),
 dict(key='p.fay;;119', nlines=37, slug='p_fay_119', **COMMON,
      name='Letter — Gemellus to Sabinus: rotten hay at twelve drachmas',
      date='c. 103 CE',
      content='The donkey-driver bought a rotten bundle of hay; where are the bank-receipt and the loan document? Cocks for the Saturnalia, fish for Gemella’s birthday',
      trans=[
        "Lucius Bell[e]nus Gemellus",
        "to [Sa]binus his son, greeting.",
        "Aunes the donkey-driver has bought",
        "a rotten bundle of hay",
        "at 12 dr. — a little bundle,",
        "rotten hay, the whole of it",
        "broken up, like refuse.",
        "Sabinus, the (son) of Psellos, the",
        "one from Psinachis who was with you,",
        "has brought to the city a let-",
        "ter of the prefect to Diony-",
        "sios the strategos, to hear",
        "his case … violence done me(?)",
        "… him … until he",
        "writes the …(?) of the hay",
        "for the sowing. The bank-receipt",
        "of the hay — where have you put it?",
        "And its loan of the",
        "mina — where is the document? Send",
        "the key and tell me",
        "where it lies, that I may fetch them out,",
        "so that if I am going to reckon with him",
        "I have them. So do not do",
        "otherwise. Take care of yourself.",
        "Greet Epagathos and",
        "those who love us in",
        "truth. Farewell. Choiak 12.",
        "For the Saturnalia send",
        "ten cocks from the market,",
        "and for the birthday of Gemell[a]",
        "send fish and …",
        "and bread, 1 (artaba of wheat).",
        "Send the beasts to cart dung at the vegetable-plot of Psinachis, and the dung-carts, since Pasis is bawling",
        "lest it turn to crumbs because of the water; and let them bring hay for it. At once send the",
        "beasts.",
        "Deliver to Sabinus my son, f(rom) L[ucius]",
        "Be[l]lenus Geme[ll]us.",
      ]),
 dict(key='p.fay;;121', nlines=16, slug='p_fay_121', **COMMON,
      name='Letter — Bellenus Sabinus: a new yoke-band for Vestinus',
      date='after 110 CE (?)',
      content='Give Vestinus a strong new yoke-band, well greased, from the skins in the chest; ask the hunch-backed tanner for the calf’s hide',
      trans=[
        "Bellenus Sabinus to Gemi-",
        "nus his own, greeting.",
        "You will do well to give Vesti-",
        "nus, for his yoke,",
        "a new yoke-band,",
        "a strong one, which you will also",
        "grease carefully, from the",
        "skins in the chest",
        "that you have by you,",
        "so that when he comes up he may",
        "carry it [back], since [his]",
        "own is cut. And the h[id]e",
        "of the calf that we sacri-",
        "[f]iced, ask for fr[om the]",
        "hunch-backed tanner. [Farewell.]",
        "Given Pauni 6.",
      ]),
 dict(key='p.fay;;122', nlines=26, slug='p_fay_122', **COMMON,
      name='Letter — Bellenus Sabinus: release twenty-eight artabas of mustard',
      date='c. 100 CE',
      content='Hand over 28 artabas of the mustard in Sochotes’ granary to the bearer, seal the rest until the balance of the price is paid',
      trans=[
        "Bellienus Sabinus to Epagathos his",
        "own, greeting.",
        "You will do well to transfer the mus-",
        "tard that is with you in the granary of So-",
        "chotes to the man who brings you this let-",
        "ter, letting him carry off",
        "twenty-eight artabas, and the",
        "rest leaving under the seal of",
        "both, until, on receiving the bal-",
        "ance of the price, I write you again",
        "to let him carry it off; and meas-",
        "ure the mustard with the four-choi-",
        "nix measure …(?) subscription …(?),",
        "and let me know how many",
        "came out, that I may know. I sent you",
        "patterns of the forty large ones",
        "for the water-wheel of",
        "Chalothis. Compel Siso-",
        "is the car[p]enter to pay up,",
        "and send to Chalothis, if you",
        "find anyone among those present having",
        "much credit; and send the things for",
        "the …(?) three days ahead",
        "…[…] at 8 dr.",
        "Farewell.",
        "Given Phamenoth 6.",
      ]),
 dict(key='p.fay;;123', nlines=30, slug='p_fay_123', **COMMON,
      name='Letter — Harpokration: an apology, and Teuphilos wants out',
      date='c. 100 CE (?)',
      content='Harpokration was harassed and could not come down; the field-hand Teuphilos suddenly announces he wants to leave for Sabinus',
      trans=[
        "Harpokration to Bellenus",
        "Sabinus his bro-",
        "ther, greeting. Yester-",
        "day too I wrote you by",
        "Mardon your man, want-",
        "ing you to know",
        "that, because I was harassed,",
        "I could not come",
        "down; and that I shall be",
        "here a few days.",
        "If it seem good to you, send",
        "the receipt of Isas, and",
        "let us take over the little",
        "oil then, if you think fit.",
        "For Teuphi-",
        "los the Jew has come, saying",
        "“I was pressed into farm-work",
        "and I want to go off",
        "to Sabi-",
        "nus.” For he did not",
        "tell us, when he was taken on,",
        "that he should be released, but sud-",
        "denly he has told us",
        "today. For I shall find out",
        "whether he speaks truly.",
        "Farewell. Greet",
        "the brothers, Lykos",
        "a[nd ……].",
        "[Me]cheir 12.",
        "Del[i]ver ✗ to Bellenus Sabinus.",
      ]),
 dict(key='p.fay;;124', nlines=27, slug='p_fay_124', **COMMON,
      name='Letter — Theogiton rebukes Apollonios over their mother’s allowance',
      date='2nd century CE',
      content='“You seem to me to be quite senseless” — pay mother her maintenance fairly, or your greed will bring you regret',
      trans=[
        "[Th]eogi[ton to Ap]ollonios,",
        "[greet]ing.",
        "Again […] to write to you …",
        "… […] your doings …",
        "…, though I am not practiced",
        "in letters; and now, then,",
        "I have tried again to write to you",
        "before I take in hand to do",
        "anything more drastic — if only you",
        "will deal fairly in what concerns your mo-",
        "ther. For you seem to me",
        "to be quite senseless, in the present",
        "month(?), not keeping your pledged",
        "hand — for even if there were no",
        "documents, yet thanks be to the g[od]s",
        "that no presump-",
        "tion has arisen on our part,",
        "that you should think, without legal forms,",
        "to put us aside. And now,",
        "then, if you do not comply and ren-",
        "der the allowance to mother",
        "fairly, the consequence of",
        "this will follow, and your greed",
        "will bring you regret",
        "yet again. For do not suppose",
        "that your mother keeps quiet",
        "about these things. Farewell.",
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

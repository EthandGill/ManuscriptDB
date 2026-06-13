#!/usr/bin/env python3
"""Build P.Oxy 3 marriage contracts 496 & 497."""
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
 dict(key='p.oxy;3;496', nlines=39, slug='p_oxy_3_496', **OXY,
      name='Marriage contract — Thaïs and Sarapion, with dowry of 4,100 drachmas',
      date='19 Apr 127 CE',
      content='Gold jewelry weighed to the quarter, two sets of clothing, the slave Kallityche from grandmother — with full divorce, guardianship and inheritance clauses',
      trans=[
        "In the eleventh year of Imperator Caesar Trajan Hadrian Augustus, Ph[a]rm[ou]thi 24, in the city of the Oxyrhynchi in the Thebaid, with good fortune, in the priesthood of [Ju]lia A[ugu]sta.",
        "Sarapion son of Sarapion son of Sarapion son of Sarapion, his mother being Tha[ï]s daughter of Sarapion,",
        "of the city of the [O]xyrhynchi, has given his own daughter Thaïs, her mother being […], in marriage to Sarap[i]on son of [Eud]aimon son of Theon, [his mother bei]ng Heras daughter of […, her mo]ther being D[ido]us; [and the bridegroom acknowledges receipt from Sarapion the father]",
        "[an]d giver: a pair of … of three minaiai and fourteen and a half quarters, a brooch of eight quarters, a clasp of six quarters, a little chain with green … stones — the gold weighing […] and a half [quart]ers — so that in all there is, by the Oxyrhynchite stan[dard, gold of five minaiai and … quarters,]",
        "[an]d two sets of clothing, two girdles, one flame-colored, one rose-colored, a … mantle — all at a joint valuation of five hundred and sixty silver drachmas — and one thousand eight hundred and sixty silver drachmas, so that the whole dowry together is [four thousand one hundred drachmas of] Imperial [silver] coin; [and the]",
        "grandmother [of the] bride, Thaïs daughter of Sarapion, her mother being Heraklou[s], of the same c[ity], with as guardian her own",
        "other son — full brother of the giver — Sarapion son of [Sa]rapi[o]n, acknowledges, in",
        "the same stree[t], that she has given the Thaï[s] in marriage, and gives to the [sa]me Thaïs [… the slave Kal-]",
        "[lit]yche and the offspring to be born of her; <but> her service and earnings",
        "the bridegroom shall hold together … with the bride so long as they live with one another, it not being lawful for the [bridegr]oo[m]",
        "to […] the slav[e] with[out the …] nor anything brought in [… Also a house]",
        "[and] light-well a[nd] court and its fixtures, and the slave bodies Sarapous [and]",
        "Nikarous and the offspring of N[ika]rous — Sarapous and Kerdon and [Epich]armos — and",
        "what offspring shall be born of them or of others, and whatever she may acquire [besides these] or …[… — these he may not sell nor pledge nor otherwise dis-]",
        "[po]se of without the consent of the bride. So let the married pair live together with one another blamelessly,",
        "and let the bridegroom furnish the bride with necessaries according to his means; and if",
        "they differ with one another a[nd] the bride [wishes to separate from",
        "the bridegroom …, then,]",
        "[when] the separation has taken place, let the bride take away the s[l]ave Kallityche",
        "and the offspring born of her, and let the bridegroom repay — to the giver if he survives, otherwise to the bride — the four thou[sand] one hundred drachmas of the dowry within [… days from demand, or let him pay it with half again;]",
        "[…] each … and … be done. And if the bride is pregnant when she separates, the bridegroom shall give her another sixty drachmas toward",
        "the expenses of her confinement. While they live together, may there be health; but if it happen that one of the married pair [die …, let the bride-]",
        "[groom] have power over his own property, to bestow whatever he chooses and to share out to whom he",
        "will; and if he bestow nothing, these things too shall after his death belong to the children born of them",
        "both. And if [the] bridegroom have died first, let the bride have […]",
        "[…] let the bride be (guardian) as to the ha[lf], or the next-of-kin, and the man to be appointed by the bridegroo[m]",
        "as to the other half — both guardians — the children being maintained with their mother until they come of age. And if the bridegroom appoint no one [as guardian] of the half [guardianship, let the bride alone, or]",
        "the [n]ext-of-kin, (be guardian), it being lawful for no one to ca[st] her out of the guardianship or any part of it. And if the bride",
        "die first, there being no children of them both, or those born having passed away",
        "childless, let the bridegroom give back what is [in the dowry …: the four thou-]",
        "sand one hundred [silver drachmas] within six[t]y days, and let all her other property be remitted to the same kin of the bride. And if likewise",
        "the bridegroom die first, there being no children of them both, or those born having",
        "after[wards passed away childless,]",
        "(the bride shall recover it,) taking away the slave Kallityche and the offspring to be born of her — and until she recover it,",
        "let her be mistress of everything; and in all the stipulations the choice rests with the bride, if",
        "she choose, to have the gold objects named in the dowry [at the same weight, or their equal valuation,]",
        "the right of execution belonging to the bride and hers both upon the bridegroom and upon all his",
        "property, according as they agreed with one another. Identifier of both parties: (2nd hand) D[i]ogenes",
        "son of Hierax, scri[be, o]f the same city, in [the same street].",
      ]),
 dict(key='p.oxy;3;497', nlines=34, slug='p_oxy_3_497', **OXY,
      name='Marriage contract — Ammonous and Theon (fragmentary)',
      date='early 2nd century CE',
      content='Surviving clauses: the wife may not stay away a night or shame her husband; dowry repayment within sixty days; mutual guardianship of children',
      trans=[
        "[…] …",
        "[… he may not sell nor pledg]e nor [otherwise] dispose of",
        "[without the consent of Ammonous …] …; likewise let it not be lawful for A[mm]onous to stay a-",
        "[way for a night or a day from Theon’s house, nor to be with another man, nor to shame",
        "Theon in whatever brings sha]me on a husband, nor to ruin their common home. And",
        "[if they differ with one another and Ammonous wishes to separate from Theon and",
        "… to make] demand [of the dow]ry, leaving Theon,",
        "[… let Theon repay her the … hun]dred [drachmas] within sixty days from demand. And i[f]",
        "[… Ammonous wishes to make] de[m]and of the d[o]wry, let there be, instead of it, only the six",
        "hun-",
        "[dred drachmas …] …, let the same Theon furnish the children with their maintenance",
        "[…; and if, after their] separation from one another, it happen that the children of them both pass away,",
        "[… let Theon repay to Chai]r[emo]n, if he lives, otherwise to her nearest of kin, the dowry",
        "[and …, or let him pay it with half] again. While they live together, may there be health; but if it happen that one of them",
        "die,",
        "[…, of the] children [to be born to them of one ano]ther, or any of them being under age, let Ammonous,",
        "and the man",
        "[to be appointed] by Theon, [each as to the half — both guardians …, the children] being maintained with their [m]other until coming of age. And if no one",
        "besides the",
        "[… be appointed …,] (she shall be) accountant of these things and of what shall be left to them. And if Ammonous die",
        "first, [there being no children of them both, or … having] failed, let Theon repay to her father and giver",
        "Chairemon, if he survive, [otherwise to her nearest] of kin, the dowry [… within … days fr]om demand, or let him pay it with half again. And if [The]on die fir[s]t,",
        "[there being no children of them both …,] let Ammonous, first recover[i]ng the dowry and all else of hers, out of the …",
        "[… and in all] the stipulations about the demand and recovery of the dowry, the right of execution",
        "[shall belong]",
        "[to Ammonous and hers, upon Theon and upon all his property, as if",
        "by judgme]nt, according as they agreed with one an[o]ther, the choice of the ring be-",
        "[ing with Ammonous, if she choose. (2nd hand) I, Theon …] son of [A]chill[es], of the Propapposebastian tribe, also Althaian, my mother being Demetria,",
        "[have the dowry … (3rd hand) I, Chairemon …]os, also Altheian, have given my daughter in marriage.",
        "[(4th hand) I, …] son of Sarapion son of Artemidoros, of the Auximetrian tribe and al[so …,]",
        "[… drachm]as of principal, before you, in full, on al[l]",
        "[the aforesaid terms …]; I, …, wrote on his behalf as he writes slowly.",
        "[…] …",
        "[…] 22. Marriage-contract of Ammonou(s) wi(th) Theon.",
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

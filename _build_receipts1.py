#!/usr/bin/env python3
"""Build BGU 3 receipts: annona report, harvest-tax, penthemeros corvee, poll-tax."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

SRC = {'bgu;3;807': '_PENDING_bgu3_800-849.json'}
def load(k):
    f = SRC.get(k, '_PENDING_bgu3_850-900.json')
    return json.load(open(f, encoding='utf-8'))[k]

SOKN = dict(found='Soknopaiou Nesos (Arsinoite nome / Fayum), Egypt', lat=29.5377, lon=30.6856)

ITEMS = [
 dict(key='bgu;3;807', nlines=22, slug='bgu_3_807',
      name='Receipt — military requisition of barley for the Heraklian cavalry-wing',
      date='Oct–Nov 185 CE', found='Hermopolite nome, Egypt', lat=27.7803, lon=30.8016,
      content='A duplicarius of the Heraklian ala at Koptos certifies receipt of 15 artabas of barley levied on the village of Magdola toward 20,000 artabas for the wing',
      trans=[
        "To Ploutogenes, royal scribe acting in the matters of",
        "the strategia,",
        "Antonius Vestinus, duplicarius, dispatched",
        "by Valerius Frontinus, prefect of the",
        "Heraklian cavalry-wing at Koptos. I have had measured out",
        "to me from Asies son of Phibis son of Asies, and Inaro-",
        "ous son of Kollouthos son of Cornelius, elders of Magdo-",
        "la of Petechon the Kousseite, Upper, the",
        "(barley) levied on their village out of what was order-",
        "ed by the former prefect Longaeus",
        "Rufus to be requisitioned from the produce of the 24th (year)",
        "for the use of the aforesaid wing — of barley, two",
        "myriads of artabas, by the public receiving-measure,",
        "by the ordered measurement, of barley fifteen artabas,",
        "in accordance with the apportionment made",
        "by the procurators of the nome.",
        "And I have issued this receipt in quadruplicate.",
        "Year 26 of Imperator Caesar Marc[u]s [Au]rel[ius]",
        "[Comm]od[us Antoni]nus [Au]gustus [Pius]",
        "[Felix Armeniacus Medic]us Par[th]icus [Sarmaticus]",
        "[Ge]rmanicus B[retann]icus Greate[s]t, Hathy[r ..]",
        "[… (2nd hand) …]ou[…]",
      ]),
 dict(key='bgu;3;851', nlines=10, slug='bgu_3_851',
      name='Receipt — purchase of confiscated olive-bearing property',
      date='10 Aug 163 CE', found='Arsinoite nome, Fayum, Egypt', lat=29.3084, lon=30.8428,
      content='A note of a payment to Isidoros and the overseers of confiscated property of the estate of Heliodoros son of Maron, for olive-land',
      trans=[
        "Year 2 of the Aurelii",
        "Anton[i]nus and Verus",
        "the lords Augusti,",
        "Mesor[e] 17. Paid to Isidoros",
        "and partners, overseers",
        "of confiscated property of the administration of Helio-",
        "doros son of Maron, through",
        "Horos son of Ambro…s, over-",
        "seer(?) of confiscated 3rd-(year) olive-",
        "lands …, he bought …",
      ]),
 dict(key='bgu;3;875', nlines=8, slug='bgu_3_875',
      name='Penthemeros receipt — dyke-work at the Boubastos canal of Karanis',
      date='27 July 146 CE', found='Karanis (Arsinoite nome / Fayum), Egypt',
      lat=29.5186, lon=30.9036,
      content='Herodes son of Petheus has worked his five-day embankment corvée at the Boubastos canal of Karanis; countersigned by Longinus',
      trans=[
        "Year nine of Imperator Caesar",
        "Titus Aelius Hadrianus Antoninus",
        "Augustus Pius. Has worked for the embankment-works",
        "of the same 9th (year), Epeiph 29 to",
        "Meso(re) 3, in the Boub(astos) canal of Kara(nis):",
        "(2nd hand?) Herodes son of Petheus son of",
        "Herodes, (mother) Serap(…).",
        "(3rd hand) I, Longi(nus), have signed.",
      ]),
 dict(key='bgu;3;876', nlines=9, slug='bgu_3_876', **SOKN,
      name='Penthemeros receipt — dyke-work in the Epagathian canal',
      date='17 June 152 CE',
      content='Stotoetis son of Apynchis has worked his five-day embankment corvée in the Epagathian canal of Soknopaiou Nesos; signed by Antonis Zerion',
      trans=[
        "Year 15 of Imperat(or) C[a]e[s]a[r]",
        "Titus Aelius Hadrianus Antoninus",
        "Augustu(s) Pius. [Ha]s worked for the",
        "embankment-works of the s(ame) 15th (year), from Pauni",
        "19 to 23, in the Epagath(ian) canal",
        "of Soknop(aiou Nesos): Stotoe(tis) son of Apynchis",
        "son of St(o)t(o)e(tis), (mother) Tekiasis.",
        "(2nd hand) I, Antonis Zerion,",
        "have signed.",
      ]),
 dict(key='bgu;3;877', nlines=8, slug='bgu_3_877', **SOKN,
      name='Penthemeros receipt — the ordered five-day stint',
      date='6 Nov 159 CE',
      content='Stotoetis son of Apynchis has done the ordered five days’ embankment work in the Epagathian canal of Soknopaiou Nesos; signed by Phanias',
      trans=[
        "Year 23 of Imperator Caesar",
        "Titus Aelius Hadrian[us An]toninus",
        "Augustus P[i]us. Has worked for the embankment(-dues)",
        "of the past 22nd (year), Hathyr 5–9, in th(e) Epag(athian canal),",
        "the ordered 5 day(s’) five-day stint, of Soknop(aiou Nesos):",
        "Stotoe(tis) son of Apynch(is) son of Stot(oetis),",
        "(mother) Tekiasis.",
        "(2nd hand) I, Phanias, have signed.",
      ]),
 dict(key='bgu;3;878', nlines=8, slug='bgu_3_878', **SOKN,
      name='Penthemeros receipt — under the joint reign',
      date='11 Sept 162 CE',
      content='Stotoetis son of Apynchis has worked the ordered five-day embankment stint in the first year of Marcus Aurelius and Lucius Verus',
      trans=[
        "Year 3 of Imperator Caesar",
        "Marcus Aurelius Antoninus",
        "Augustus and Imperator Caesar",
        "Lucius Aurelius Ver[u]s Augustus.",
        "Has worked for the embankment(-dues) of the past 2nd (year), Thoth 10 to",
        "14, the ordered 5 day(s’) five-day stint, in the … canal,",
        "of Soknopaiou Nesos: Stotoe(tis) son of Apynch(is)",
        "son of Stotoe(tis), (mother) Tekiasis.",
      ]),
 dict(key='bgu;3;881', nlines=13, slug='bgu_3_881', **SOKN,
      name='Tax account — money-taxes of Stotoetis over a year',
      date='23 Dec 154 CE',
      content='A running account of payments by Stotoetis son of Apynchis to the collectors of money-taxes at Soknopaiou Nesos: syntaximon, guard-pay, river- and prison-guard dues, and apportionments on the destitute',
      trans=[
        "Seventeenth year of Imperator Caesar Titus Aelius Hadrianus",
        "Antoninus S[eb]astos Pius, Phaophi 25. Paid to Theogi(ton) and partners,",
        "collec(tors) of money(-taxes) of Soknop(aiou Nesos): Stotoe(tis) son of Apynch(is) son of Stot(oetis),",
        "(mother) Tekiasis, syntaximon-tax of the same (year),",
        "12 silver drachmas, total 12 dr.; on Hadrianos 29, another 4 silver dr., total 4 dr.; on Tybi 26, another 4 silver dr., total 4 dr.;",
        "Phamenoth 29, another 4 silver dr., total 4 dr.; Pharmo(uthi) 30, another 4 silver dr., total 4 dr.; Pacho(n) 29,",
        "guard-pay, 2 silver dr. 5 ob., total 2 dr. 5 ob.; mag(dola-tax) 5½ ob.; Pauni 26, another 8 silver dr., total 8 dr.; Epeiph 28, river-guard(-dues) 3 ob.,",
        "prison-guard(-dues) 1½ ob., dou(ble-tax) 2½ ob., wild-beast(-tax) 1 ob. 1½ ob. ¼-ob.; for the 18th (year), Thoth 27, of the 17th (year) apportion(ment) on the destitute, 4 silver dr., total 4 dr.,",
        "and 18th (year), Phaoph(i) 15, through Harp(…) of the additional-levy of the seventeenth (year), 12 dr., total 12 dr.; Hathyr 27, additional-levy of the 17th (year), 12 dr., total [1]2 dr.,",
        "on Hadrianos 27, guard-tax of the destitute of the 17th (year), 3 dr. 5 ob., total 3 dr. 5 ob.",
        "17th (year), Mecheir 30, paid to Theogi(ton) for the past sixteenth (year), apportion(ment) on the destitute, 8 silver dr., total 8 dr.,",
        "Pauni 26, for the past sixteenth (year), 4 silver dr., total 4 dr.; Mesore, Epagomenai 1, for the past",
        "sixteenth (year), 8 silver dr., total 8 dr.",
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
genre:    receipts
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
    num = it['key'].split(';')[2]
    label = f"BGU 3.{num}"
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

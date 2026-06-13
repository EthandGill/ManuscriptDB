#!/usr/bin/env python3
"""Build mixed contracts: P.Oxy 1.95 slave sale + P.Tebt 2.442/440/445."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

SRC = {
    'p.oxy;1;95': '_PENDING_p.oxy1_91-140.json',
    'p.tebt;2;442': '_PENDING_p.tebt2_408-445.json',
    'p.tebt;2;440': '_PENDING_p.tebt2_408-445.json',
    'p.tebt;2;445': '_PENDING_p.tebt2_408-445.json',
}
TEB = dict(found='Tebtunis (Arsinoite nome / Fayum), Egypt', lat=29.108, lon=30.937)

ITEMS = [
 dict(key='p.oxy;1;95', nlines=38, slug='p_oxy_1_95', label='P.Oxy 1.95',
      found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658,
      name='Attested sale of the slave Dioskorous — 1,200 drachmas',
      date='23 June 129 CE',
      content='Agathos Daimon attests his holograph deed selling the 25-year-old slave Dioskorous, “not to be returned, except for the sacred disease”',
      trans=[
        "In the thirteenth year of Imperator",
        "Caesar Trajan Hadrian Augustus, Pauni",
        "(2nd hand) 29, (1st hand) in the city of the Oxyrhynchi in the Thebaid.",
        "Agathos Daimon also called Dionysio[s],",
        "son of Dionysios son of Dionys[i]os, his mother being Hermione,",
        "of the city of the Oxyrhynchi, acknowledges to [G]aius [Ju]lius Germa-",
        "nus, son of Gaius Julius Dome[tianu]s, in the s[tr]eet,",
        "that there is attested, th[r]ough [this] acknowledg-",
        "ment, the holograph deed of sale which the acknowledging party, Agathos Dai-",
        "mo[n] also called Dionysios, made to Julius Germanus",
        "on the twenty-fifth of the month Tybi of the",
        "present thirteenth year,",
        "of the slave belonging to him",
        "by purchase — formerly of Herakleides also",
        "called Theon, son of Machon, of the Sosikosmian tribe",
        "and Althaian deme — Dioskorous,",
        "about 25 (years old), without distinguishing mark, whom from that time",
        "Julius Germanus has had over from him — this",
        "very one, not to be returned, except for the sacred",
        "disease and (legal) claim — at a price of one thousand",
        "two hundred silver drachmas, which",
        "from that time Agathos Daimo[n]",
        "also called Dionysios has received fro[m] Julius Germa-",
        "nus in full, together with the holograph deed of sa[le];",
        "upon which Julius Germanus paid",
        "the sale-tax dues on the same slav[e]",
        "Dioskorous on the third of the mon[th]",
        "Phamenoth of the same year, in accord-",
        "ance with the receipt issued to him —",
        "the guarantee of the same slave",
        "Dioskorous with every guarantee",
        "falling upon Agathos Daimo[n]",
        "also called Dionysios, as the holograph",
        "deed of sale also contains. And should it happen that this (deed)",
        "be lost or otherwise destro[y]ed, [Ju-]",
        "lius [Germanus] shall n[ot] further need",
        "[… pur]chase(?) […]",
        "[…] … […]",
      ]),
 dict(key='p.tebt;2;442', nlines=13, slug='p_tebt_2_442', label='P.Tebt 2.442', **TEB,
      name='Apprenticeship — Harphaesis bound to the weaver Heron',
      date='9 Nov 113 CE',
      content='Protas apprentices his son to learn the weaver’s craft “entire and complete, as Heron himself knows it”',
      trans=[
        "In the seventeenth year of Imperator Ca[esar]",
        "Nerva Trajan Augustus Germanic[us]",
        "Dacicus, Hathyr 13, at Tebtunis in the P[ole-]",
        "mon division of the Arsino[ite nome.]",
        "Protas son of Petesou[chos, aged about]",
        "forty (years), with a scar on his right wri[st],",
        "has apprenticed his own son Harphaesis to Heron",
        "son of Orseus, weaver, aged about twenty-f[ive],",
        "with a scar in the middle of his forehead, [so] that",
        "Harphaesis may le[arn] the wea[ver’s]",
        "craft, entire and complete, [as] Heron",
        "himself knows it, for [… ye]ars [from]",
        "[the new moo]n of the [month] Choiak […]",
      ]),
 dict(key='p.tebt;2;440', nlines=18, slug='p_tebt_2_440', label='P.Tebt 2.440', **TEB,
      name='Repayment release — four thousand drachmas on a mortgage (fragmentary)',
      date='198–210 CE',
      content='Sarapias, fatherless, acknowledges receiving the four thousand drachmas remaining from a mortgage loan registered at the property-archive',
      trans=[
        "[……]…[……] in the month Mes[ore …]",
        "[……] Sarapias, fatherless, her mother being [……, acknowledges]",
        "[… aged about …]-seven, a scar on her right knee, with as g[uardian …]",
        "[… aged …]-five [years], a scar on the left shin, to Achill[es …]",
        "[… of the city of the Arsinoit]es, of the Gymnasium quarter, [and …]",
        "[……]…ios son of Apollonios, aged about fif[ty …]",
        "[… that] Sa[rapias] has received from them, the two, [……]",
        "[… the] four thousand [silver drach]mas remaining …[…]",
        "[……] of what Achilles owed, and [……]",
        "[…… of] the Treasuries quarter …[…]",
        "[… by an acknowledgment of l]oan made thr[ough …]",
        "[… by mort]gage and through the [property-]ar[chive …]",
        "[……]…ammon, from which mortg[age …]",
        "[… ar]chive certain belongin[gs …]",
        "[……] and the (deed) through the …[…]",
        "[… to the] one producing (it), according to …[…]",
        "[……]…, nor …[…]",
        "[……]…, nor against [their] assi[gns …]",
      ]),
 dict(key='p.tebt;2;445', nlines=21, slug='p_tebt_2_445', label='P.Tebt 2.445', **TEB,
      name='Lease — five arouras of royal land for one year',
      date='92 CE (?)',
      content='Pakebkis leases Orseus five arouras in two parcels at 37½ artabas of wheat by the four-choinix measure of the god’s granary; both sign by proxy',
      trans=[
        "[… a scar on the right] eyebr[ow; and for Orseus, Didymos son of Kronion,]",
        "ag(ed) 34 […]",
        "(2nd hand) I, Pakebkis son of P[……, have leased, for only the]",
        "twelfth ye[ar, the five arouras of royal land]",
        "in two [parcels, of which the first parcel is four] arouras",
        "in the field [called] of [Laar]chos, and of the second",
        "parcel the remaining [o]ne arour[a] in the Sixth fie[ld],",
        "at a total rent, apart from seed, of thirty-",
        "seven and a half artabas of wheat by the four-choi[n]ix measure",
        "of the god’s granary, as aforesaid. His son Psenkebkis wrote",
        "on his behalf because he does not know letters.",
        "(3rd hand) I, Orseus son of Kronio(n), Persian of the epigone, have taken on lease the",
        "five arouras of royal land for only the twelf-",
        "th year, at a total rent of thirty-sev-",
        "en and a half artabas of wheat, the carriage-charges of the",
        "delivery falling on me, as afore(said). Didym(os) son of",
        "Kronio(n) wrote on his beh(alf), as he does not know letters.",
        "Registered through the record-office at",
        "Tebtunis.",
        "Lease, of Pa[kebki]s",
        "to Or[s]eus, of 5 (arouras).",
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
    r = json.load(open(SRC[it['key']], encoding='utf-8'))[it['key']]
    gk = [polish(l) for l in clean(r['greek'])][:it['nlines']]
    gk = [l for l in gk if l]
    tr = it['trans']
    assert len(gk) == len(tr), f"{it['key']}: greek {len(gk)} != trans {len(tr)}"
    body = HDR.format(label=it['label'], name=it['name'], key=it['key'], tm=r.get('tm', '?'),
                      date=it['date'], found=it['found'], shelf=r.get('shelf', '?'),
                      content=it['content'], lat=it['lat'], lon=it['lon'])
    body += "".join(f"r.{i}   {l}\n" for i, l in enumerate(gk, 1))
    body += "\n[TRANSLATION]\n"
    body += "".join(f"{i}   {l}\n" for i, l in enumerate(tr, 1))
    with open(f"manuscripts/{it['slug']}.txt", 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"built manuscripts/{it['slug']}.txt  ({len(gk)} lines)")
print("ALL OK")

#!/usr/bin/env python3
"""Build petitions tranche 2: P.Oxy 2.285, BGU 4.1070, P.Fay 108, BGU 4.1187."""
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

SRC = {'p.oxy;2;285':'_PENDING_p.oxy2_234-285.json','bgu;4;1070':'_PENDING_bgu4_1050-1100.json',
       'p.fay;;108':'_PENDING_p.fay_91-140.json','bgu;4;1187':'_PENDING_bgu4_1151-1200.json'}

ITEMS = [
 dict(key='p.oxy;2;285', nlines=21, slug='p_oxy_2_285',
      name='Petition - a weaver extorted by the trade-tax collector',
      date='c. 50 CE', found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658,
      content='Sarapion the weaver petitions the strategos Tiberius Claudius Pasion: the tax-collector Apollophanes seized the linen tunic off his back, extorted four drachmas more, and exacted two a month for six months',
      trans=[
        "To Tiberius Claudius Pasion, strate(gos),",
        "from Sarapion son of Theon,",
        "of the city of the Oxyrhynchi,",
        "weaver, of the quarter of the Gymna-",
        "sium street. Apollophanes, having been",
        "collector of the trade-tax of the weav-",
        "ers in the 1st year of Tiberius Claud[ius]",
        "Caesar Augustus Germanicus",
        "Imperator, using much force,",
        "snatched away the (tunic) I was",
        "wearing, a linen tunic",
        "worth eight drachmas, and ex-",
        "torted from me another four",
        "drachmas, and from the month Neos Sebas-",
        "tos of the ninth year of Tiberius",
        "Claudius Caesar Augustus",
        "Germanicus Imperator until",
        "Pharmouthi, six months, each month",
        "two drachmas, which come to 24 dr.",
        "Therefore I ask that proceedings be taken against him",
        "as may seem good to you. Farewell.",
      ]),
 dict(key='bgu;4;1070', nlines=14, slug='bgu_4_1070',
      name='Petition - Aurelia Techosarion requests a guardian for her children',
      date='Sept-Oct 218 CE', found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658,
      content='Aurelia Techosarion asks the priest-exegetes of Oxyrhynchus to appoint the children’s well-off paternal uncle Aurelius Achilles as guardian over their inheritance, so their rights are not lost',
      trans=[
        "[To So-and-so,] priest, prytanis in office, exeg(etes), council(lor) of the city of the Ox(yrhynchites),",
        "[from Aurel(ia) Techosarion] also called Isidora, daughter of Panaretos also called Theon, of the same city.",
        "[I request,] at my own risk, as guardian of my under-age children",
        "[over] their paternal inheritance, Aurelius Achilles",
        "[son of Theon ...], their paternal uncle, who is well-off,",
        "[... being present] and consenting to the choice of the guardianship, on condition that he",
        "[...] to mine, since I too must necessarily be a co-",
        "[overseer ...] this petition, so that what follows for them may come about and",
        "[their rights not be l]ost. Year 2 of Imperator Caesar Marcus Aurelius",
        "[Antoninus Piou]s Felix Augustus, Phaophi. I, Aurelia Techosarion",
        "[also called Isidora, have submitted it.] I, Aurelius Serenos, am registered as her guardian, having been asked,",
        "[and wrote on her behalf,] as she does [not] know letters. I, Aurelius Achilles son of Theon, consent.",
        "[...]…, assistant, through Aurelius Origenes (his) son, I delivered (it).",
        "[...], assistant, I delivered (it). Hathyr 3.",
      ]),
 dict(key='p.fay;;108', nlines=17, slug='p_fay_108',
      name='Petition - two pig-dealers ambushed and robbed at dawn',
      date='17 Sept 169 CE (?)', found='Theadelphia (Arsinoite nome / Fayum), Egypt',
      lat=29.4333, lon=30.5333,
      content='Pasion and Onesimos, pig-dealers of the metropolis, report that on the road from Theadelphia at dawn malefactors bound them and the watchtower-guard, beat them bloody, and carried off a piglet and Pasion’s tunic',
      trans=[
        "To Megalonymos, strate(gos) of the Arsi(noite), of the Themist[e]s and Po-",
        "lemon divisions,",
        "from Pasion son of Herakleides, of",
        "the Hellenion quarter, and Onesimos son of",
        "Amerimnos, of the Gymnasium quarter,",
        "the two pig-dealers of the metropo-",
        "lis. Yesterday, which was the 19th of the present mo-",
        "nth Thoth, as we were coming up from",
        "the village of Theadelphia in the Themistes",
        "division, at dawn there came upon",
        "us certain malefactors, between Poly-",
        "deukia and Theadelphia, and they bound",
        "us, together with the watchtower-guard, and with",
        "very many blows ill-treated us a[nd]",
        "made [Pasio]n wounded, and",
        "carried off one piglet [of u]s and lif-",
        "[ted Pasio]n’s tunic",
      ]),
 dict(key='bgu;4;1187', nlines=36, slug='bgu_4_1187',
      name='Petition - Kastor: his inherited land seized by force',
      date='c. 49-48 BCE', found='Herakleopolite nome, Egypt', lat=29.0667, lon=30.9333,
      content='Kastor petitions the strategos Andromachos: bare plots he inherited from his mother have been alienated by two women acting with violence; he asks they be summoned and his ownership upheld',
      trans=[
        "To Andromachos, (royal) kinsman and strategos and",
        "in charge of the revenues,",
        "from Kastor son of Polydeukes, of",
        "the village of Tokoeos. There belonging to me",
        "in the same village, by maternal (inheritance),",
        "bare plots of one and a half bikos,",
        "of which the possession and ownership",
        "belonged to my mother, and",
        "for the time she lived holding and own-",
        "ing (them) unhindered, with no one",
        "at al[l h]in[dering, she continued;]",
        "and [... after her]",
        "death, lord, [... the]",
        "aforesaid …[...]",
        "it has befallen me (that) Sen[...]",
        "daughter of Semtheus, and Stotoe daughter of Pne[...]",
        "(son) of …ion, of the sam[e village,]",
        "have alienated the desig-",
        "nated plots, with no",
        "right to lay claim, but",
        "using the violence and willfulness that is theirs,",
        "thinking",
        "to get away with it and not to render",
        "the account concerning these things. Being in dan-",
        "ger, then, of being deprived of my own,",
        "if I do not obtain your",
        "assistance, I ask, if it seem good,",
        "to order them brought before you",
        "and that I obtain my rights;",
        "and (that) they, for what is fitting, with regard to",
        "the attention of others — there remaining to me",
        "the ownership and lordship",
        "of the said plots,",
        "inasmuch as they are indeed ours, that I may be",
        "[a]ssisted.",
        "Farewell.",
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
    elif parts[0] == 'p.oxy':
        label = f"P.Oxy {parts[1]}.{parts[2]}"
    else:
        label = f"BGU {parts[1]}.{parts[2]}"
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

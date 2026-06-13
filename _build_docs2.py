#!/usr/bin/env python3
"""Build documents batch B."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'⁦[^⁩]*⁩', ' ', line)
    l = re.sub(r'[⁦⁧⁨⁩]', '', l)
    l = re.sub(r'\(perpendicular\)\s*', '', l)
    l = re.sub(r'\bcolumn [rv]\b', '', l)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = re.sub(r'\bvac\.?\b', ' ', l)
    return re.sub(r'\s+', ' ', l).strip()

SRC = {'p.oxy;3;516':'_PENDING_p.oxy3_485-534.json','bgu;4;1065':'_PENDING_bgu4_1050-1100.json',
       'p.oxy;1;137':'_PENDING_p.oxy1_91-140.json','p.oxy;1;139':'_PENDING_p.oxy1_91-140.json',
       'p.oxy;2;245':'_PENDING_p.oxy2_234-285.json','p.oxy;2;239':'_PENDING_p.oxy2_234-285.json'}
OXY = dict(found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658)

ITEMS = [
 dict(key='p.oxy;3;516', nlines=14, slug='p_oxy_3_516', label='P.Oxy 3.516', **OXY,
      name='Order to the sitologoi - pay out wheat from deposit',
      date='17 Nov 160 CE',
      content='Dionysios, sacred victor and former exegetes, instructs the granary-keepers of the Kerkeurosis district to pay Apion 25½ artabas 9 choinikes of wheat from his deposit',
      trans=[
        "Dionysios son of Faustus also called",
        "Amphion, of the sacred victors",
        "and former exegetes of the city of the Oxy(rhynchites),",
        "through Horion (his) secretary,",
        "to the sitologoi of the middle toparchy, district of Kerkeurosis,",
        "greeting. Pay out",
        "from what you hold on deposit of mine,",
        "of wheat of the produce of the past 23rd year",
        "of Antoninus Caesar the lord,",
        "to Apion son of Apion, artabas",
        "twenty-five and a half, nine choin(ikes),",
        "total 25 1/2 art., 9 choin. Year 24 of Antoninus",
        "Caesar the lord, Hathyr 21.",
        "I, Apion son of Apion, presented (it).",
      ]),
 dict(key='bgu;4;1065', nlines=30, slug='bgu_4_1065', label='BGU 4.1065',
      name='Bank-remittance - the price of two gold serpent-bracelets',
      date='25 Aug 98 CE', found='Arsinoite nome, Fayum, Egypt', lat=29.3084, lon=30.8428,
      content='A bank copy: the goldsmith Mystharion acknowledges receiving 2,816 drachmas for a pair of serpent-headed “Magian” bracelets of 8 minaiai of assayed gold, with terms for remaking',
      trans=[
        "Copy of a bank-payment through the",
        "bank of Pappion of the Macedonians.",
        "Year one of Imperator Caesar Nerva Trajan",
        "Augustus Germanicus, month Kaisareios, 2nd intercalary day.",
        "Herodes son of Leon, to Mysthas son of Menelaos, goldsmith,",
        "(acknowledges) that he has received the price of assayed gold,",
        "of eight minaiai, which he made for him",
        "into a pair of Magian bracelets, double-curved,",
        "serpent-headed, by the Arsinoite standard,",
        "which Hero[des] also received — of the agreed",
        "charge: two thousand silver [d]rachmas",
        "eight hundred and sixteen, total 2816 dr. And if",
        "Herodes wishes to remake the afore-",
        "said articles, he shall give, for each minaion,",
        "for wastage one quarter. And if also",
        "he should dispose (of them), likewise he shall give, for each minaion,",
        "one quarter, Mysthas repaying the price current at the time …",
        "I, Mystharion son of Menelaos, gold-",
        "smith, have received from [He]rodes",
        "the price of assayed gold, of",
        "eight minaiai, which I made",
        "for him into a pair of Magian",
        "bracelets: silver drachmas",
        "two thousand eight hundred sixteen,",
        "[total 2]816 dr. And if he wishes to",
        "remake them or dispose (of them), I will re-",
        "pay the price current at the time,",
        "taking back the articles, and",
        "for each minaion one quar-",
        "ter, as aforesaid.",
      ]),
 dict(key='p.oxy;1;137', nlines=29, slug='p_oxy_1_137', label='P.Oxy 1.137', **OXY,
      name='Receipt for a new water-wheel axle (Apion estate)',
      date='11 Jan 584 CE',
      content='The tenant Ptollion of Ambious acknowledges to the Apion estate that he received a new pumping-axle for the landlord’s water-wheel, to serve seven years, the old one given to the doorkeeper',
      trans=[
        "† In the reign of our most divine and most pious lord Fl(avius) Tib[er]ius",
        "Maurice, the eternal Augustus and Imperator, year 3, after the",
        "consulship of our lord of divine memory, Tiberius",
        "Constantine, year 6, Tybi 15, indiction 2.",
        "To the most magnificent heirs of him of glorious memory,",
        "Apion, former chief patrician, landholders also here",
        "in the illustrious city of the Oxyrhynchites, through Menas the servant,",
        "who puts the question and secures for his own masters, the",
        "same all-praiseworthy men, the right of action and obligation —",
        "Aurelius Ptollion, son of Anouthios, his mother being Nonna, hailing",
        "from the hamlet of Ambious of the Oxyrhynchite nome, belonging",
        "to your magnificence, a registered tenant-farmer of it, gr[ee]ting.",
        "A need having now arisen for the landlord’s water-wheel under my charge,",
        "called (the wheel) of the plot of Anianos, drawing water onto arable land,",
        "for one axle, going up to the city I asked",
        "your magnificence to order the said axle",
        "to be furnished me; and at once your magnificence, taking",
        "thought for the maintenance of its own affairs,",
        "credited me its price in my accounts — a new, serviceable,",
        "satisfactory pumping-axle. I received (it) toward the completion of all",
        "the machine’s parts on this present day, which is Tybi",
        "the fifteenth of the present second indiction, for the water-supply of the crops of the",
        "(by God’s help) third tax-period, the said axle to serve the irrigations",
        "for a seven-year period; and the old one having been given to the doorkeeper. The bond is valid,",
        "written in single copy, and on question I acknowledged it. I, Ptollion son of Anouthios — this bond is agreeable to me",
        "as aforesaid. I, Papnouthios, wrote on behalf of (him) being illiterate. † Total:",
        "one axle only. † † †",
        "† Bond of Ptollion son of Anouthios, from the hamlet of Ambious,",
        "for receipt of one axle. †",
      ]),
 dict(key='p.oxy;1;139', nlines=33, slug='p_oxy_1_139', label='P.Oxy 1.139', **OXY,
      name='Sworn bond of an estate chief-guard against theft',
      date='26 Oct 612 CE',
      content='Aurelius Menas, chief-guard on the Apion estate, binds himself to pay 24 solidi per offense if he or his men are ever found stealing machine-parts or oxen, or harboring brigands',
      trans=[
        "[† In the name of the Lord and Master Jesus]",
        "[Christ our God and Savior,]",
        "[(in the reign of) our greatest lord and benefactor Fl(avius) Heraclius,]",
        "[the eternal Augustus] and Imperator,",
        "ye[ar 3], Ph[ao]phi 29, indiction 1.",
        "To Fl(avius) Apion, the all-praiseworthy and most magnificent,",
        "ex-consul and patrician, landholder also",
        "here in the illustrious city of the Oxyr(hynchites), through Menas",
        "the servant, who puts the question and secures",
        "for his own master, the same all-praiseworthy",
        "man, the right of action and obligation —",
        "Aurelius Menas, chief-guard, son",
        "of Hor, his mother being Herais, from the village",
        "of Adaios in the Oxyr(hynchite) nome, governed as a pagarchy",
        "by your magnificence. I acknowledge",
        "to your magnificence, through those belonging to it,",
        "that if ever, at any season",
        "or time, we be found to have stolen",
        "machine-parts or oxen,",
        "or to have committed any theft whatever,",
        "or to have harbored",
        "brigands — on condition that I furnish",
        "to your magnificence, for",
        "each offense, of gold",
        "twenty-four solidi, in deed and",
        "in effect exacted, at my own risk and",
        "(that) of my property. Valid is",
        "the acknowledgment, written in single copy, and on question I acknowledged it. †",
        "I, Menas son of Hor — it is agreeable to me,",
        "this acknowledgment, as aforesaid. I, Joh[n],",
        "wrote on his behalf, (he) being illiterate.",
        "(Bond) of Menas chief-guard, son of Hor, from the village of Adaios of the Oxyrhynch(ite)",
        "nome. †",
      ]),
 dict(key='p.oxy;2;245', nlines=27, slug='p_oxy_2_245', label='P.Oxy 2.245', **OXY,
      name='Declaration of sheep and lambs',
      date='30 Jan 26 CE',
      content='Herakleios and Naris register 12 sheep (six each) with following lambs, to graze around Pela and through the nome, mixed with another’s flock; countersigned by the toparch',
      trans=[
        "68",
        "To Chaireas, strategos,",
        "from Herakleios son of",
        "Apion, and Naris son",
        "of Kollouthos, eld-",
        "er. We register",
        "for the present 12th year",
        "of Tiberius Caesar Augustus",
        "the sheep belonging to us,",
        "six each,",
        "sheep 12, which will graze",
        "together with the follow-",
        "ing lambs, around Pela in the",
        "western toparchy",
        "and throughout the whole nome,",
        "mixed in with those",
        "of Dionysios son of Hippalos,",
        "through the shepherd of this man,",
        "(his) son Straton the youn-",
        "ger, registered for the poll-tax",
        "in the same Pela;",
        "for which we will also pay the prop-",
        "er tax. Fare[w]ell.",
        "I, Sara(pion) toparch, have signed: sheep",
        "twelve, total 12.",
        "Year 12 of Tiberius Caesar",
        "Augustus, Mech(eir) 5.",
      ]),
 dict(key='p.oxy;2;239', nlines=15, slug='p_oxy_2_239', label='P.Oxy 2.239', **OXY,
      name='Sworn declaration of no tax-collection',
      date='19 Sept 66 CE',
      content='Epimachos of Psobthis swears by Nero that he has made no collection in his village on any account and will not be set over it henceforth, on pain of the oath',
      trans=[
        "To the registrar of the Oxyrhynchit[e nome],",
        "Epimachos son of Pausiris son [of P]tole[mai(os)],",
        "his mother being Herakleia daughter of Epimach[os],",
        "of the village of Psobthis",
        "of the lower toparchy. I swear",
        "by Nero Claudius Caesar Aug[ustus]",
        "Germanicus Imperator that no",
        "collection has been made",
        "by me in the same village",
        "on any account whatsoever,",
        "nor indeed that from now on I will be set over",
        "the village; or may I be liable to the oath.",
        "Year 13 of Nero Claudius Caesar",
        "Augustus Germanicus Imperator,",
        "month Sebastos 22.",
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
genre:    documents
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

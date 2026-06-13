#!/usr/bin/env python3
"""Build tranche 1: 8 private letters from the pending BGU 4 / P.Oxy 2 sweeps."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

FILES = {
    'bgu;4': '_PENDING_bgu4_1050-1100.json',
    'p.oxy;2;269': '_PENDING_p.oxy2_234-285.json',
    'p.oxy;2;29': '_PENDING_p.oxy2_286-320.json',
}

def load(key):
    for pref, f in FILES.items():
        if key.startswith(pref):
            return json.load(open(f, encoding='utf-8'))[key]
    raise KeyError(key)

def polish(line):
    """Strip positional/typesetting junk papyri.info leaves inline."""
    l = line
    l = re.sub(r'\(perpendicular\)\s*', '', l)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = re.sub(r'\br,m\b|\bv,ctr\b|\bv,msup\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    l = re.sub(r'\s+', ' ', l).strip()
    return l

ITEMS = [
 dict(key='bgu;4;1079', nlines=41, slug='bgu_4_1079',
      name='Letter — Sarapion to Herakleides: debts, a patron, and a warning',
      date='4 Aug 41 CE', found='Philadelphia (Arsinoite nome / Fayum), Egypt',
      lat=29.4544, lon=31.0539,
      content='Sarapion urges Herakleides to court the patron Ptollarion daily over a crushing debt',
      trans=[
        "Sarapion to Herakleides our",
        "own, greeting. I sent you",
        "two other letters,",
        "one by Nedymos, one by",
        "Kronios the sword-bearer.",
        "Well then, I re-",
        "ceived from the Arab the",
        "letter, and I read it",
        "and was grieved.",
        "Stick close to Ptoll-",
        "arion at every hour; per-",
        "haps he can set you",
        "free. Tell him: “I am",
        "one thing, everyone else another;",
        "I am a mere boy. I have sold you",
        "my wares for a talent too",
        "little; I do not know",
        "what my patron will do to me;",
        "many creditors we",
        "have. Do not ruin",
        "us.” Ask him",
        "every day; perhaps he can",
        "take pity on you. If not, then like",
        "everyone else, you too watch",
        "yourself against the Jews(?).",
        "Rather, by sticking close to",
        "him you may become his friend.",
        "See whether the tablet can",
        "be signed through Diodoros,",
        "through the wife of the Pre-",
        "fect. If you do your",
        "part, you are not to blame.",
        "Greet Diodoros warmly.",
        "Farewell. Greet Harpochration.",
        "Year 1 of Tiberius Claudius Caesar",
        "Augustus Germanicus Imperator, month",
        "Kaisareios 11.",
        "[Deliver at] Alexandria,",
        "at the Augustan Market, at the …",
        "…storehouse, for Herakleides from Sarapion",
        "…on, son of Sosipatros.",
      ]),
 dict(key='bgu;4;1080', nlines=26, slug='bgu_4_1080',
      name='Letter — a father congratulates his son Heras on his wedding',
      date='3rd century CE (?)', found='Provenance unknown (Egypt); Berlin collection',
      lat=29.3084, lon=30.8428,
      content='Herakleides rejoices over his son’s marriage, quotes Homer’s “double feast”, asks for ten pounds of soft tow',
      trans=[
        "Herakleides to Heras his son, greeting.",
        "Before all else I embrace you, rejoicing with you",
        "over the good, pious and",
        "fortunate married life granted you, in accord with our common",
        "vows and prayers, which the gods, hearing",
        "in full, have brought to pass. And we, though",
        "absent, were gladdened in spirit at the news as if present,",
        "praying blessings over what is to come, and that",
        "coming to you we may share together a",
        "double feast in full bloom. So, just as",
        "your brother Ammonas has discussed with me",
        "concerning you and your af-",
        "fairs, so, as is right, it shall be done. And about",
        "this be confident and untroubled. And you, be eager",
        "to honor us with let-",
        "ters in equal measure. And about whatever you wish, write to me —",
        "it gives me pleasure. And if it is no burden to you",
        "and possible, send along to me ten",
        "pounds of soft tow, total 10 lb., well",
        "prepared, at the price current where you are,",
        "yourself taking no loss in",
        "this. Give many greetings from me to",
        "your dearest consort, with whom",
        "I pray that you fare well and flourish,",
        "my lord son.",
        "Oxypogon to Heras his son.",
      ]),
 dict(key='bgu;4;1078', nlines=18, slug='bgu_4_1078',
      name='Letter — Sarapion to his sister Sarapias: anxious for news',
      date='20 Oct 38 CE', found='Philadelphia (Arsinoite nome / Fayum), Egypt',
      lat=29.4544, lon=31.0539,
      content='Sarapion has sold his goods, complains nobody sent word by departing friends, will not sit idle',
      trans=[
        "Sarapion to Sarapias his sister, very many greetings",
        "and continual good health. Know that I have sold",
        "at the right moment; but you did not do well —",
        "though many friends were setting out — to send",
        "me not one word, though you knew that I am anxious",
        "about you. Well then, if I get the bits of money",
        "I shall see what I must do; for I must not",
        "sit idle. And I could wish you had given me word about the works,",
        "whether they have gone cheap or not.",
        "And know that Hegemon came in",
        "on the twenty-third. For the rest, take care of",
        "yourselves, that you stay well. Greet the children",
        "and all those in the house, and Panechotes.",
        "Farewell.",
        "Year 3 of Gaius Caesar Augustus Germanicus,",
        "month Soter 23.",
        "Deliver — from Sarapion the merchant",
        "to Sarapion his younger son, at the house.",
      ]),
 dict(key='bgu;4;1097', nlines=27, slug='bgu_4_1097',
      name='Letter — a wife to her husband: their son has gone for a soldier',
      date='41–67 CE', found='Provenance unknown (Egypt); Berlin collection',
      lat=29.3084, lon=30.8428,
      content='A wife scolds her husband for advising their son Sarapas to enlist, asks for lentils and radish oil, gives farm orders',
      trans=[
        "[…] … month … therefore I write to you,",
        "so you may know. As yet we have done nothing.",
        "And if the adversary comes up, keep watch on him;",
        "for I fear he may slip away, for he has grown sick of it.",
        "About Sarapas our son: he has not lodged",
        "with me at all, but went off to the camp",
        "to enlist. You did not do well",
        "to advise him to enlist;",
        "for when I tell him not to enlist, he says to me:",
        "“My father told me to enlist.”",
        "About Epaphroditos: he is here with me.",
        "Now please — I have, in the middle room,",
        "lentils; send them to me, and a chous of radish",
        "oil, so that I have my month’s provisions here; for I",
        "am not downhearted, but keep my courage and stay on.",
        "And if the allotment is flooded, be quick … and",
        "sow it well. I gave you word about the",
        "produce … once …",
        "… a letter to the prefect … us, so that",
        "it be measured into the public granary and given",
        "for seed …",
        "[Year … of Clau]dius Caesar Augustus Germanicus Imperator, Mesore 22.",
        "[…] so greet his mother and Demetris and his children",
        "[…] and Aparosi… …",
        "[… and] his mother and Dionyseia and her children and […]",
        "[…] her … and the mother …",
        "[N.N., daughter of Dem]etrios, to Sarapion her father.",
      ]),
 dict(key='bgu;4;1095', nlines=26, slug='bgu_4_1095',
      name='Letter — provisioning a former strategos: dates, pigeons, fish',
      date='6 Jul 57 CE', found='Peri Thebas (Thebaid), Egypt',
      lat=25.7188, lon=32.6573,
      content='Report after an inspection: no old dates anywhere; bread, pigeons, pickled fish and a phagros sent on',
      trans=[
        "[…] provide what there is […]",
        "We have come out from the inspection.",
        "And we sent to you by the sword-",
        "bearer Daphnos, who has a …",
        "… and letters, and by an-",
        "other sword-bearer, Hermon,",
        "to the temple of Leto one let-",
        "ter. So do not be negligent",
        "about anything. As for the date-",
        "palm: old fruit we found none, neither",
        "in the Diopolite nor in the Ombite nome,",
        "and the new is still in hand. For I am per-",
        "suaded that meanwhile Ptolemaios, having sent word,",
        "will be charged to convey two artabas",
        "of loaves",
        "and a half-basket of pigeons",
        "and a flagon of pickled fish",
        "and a phagros-fish kept whole; in",
        "the flagon, number 40 — total 40; in the half-",
        "basket, pigeons, number 35, and one",
        "basket-phagros.",
        "And wash yourself, that you keep healthy. So I urge you, carefully, regarding the …",
        "… and toward Ptolemaios. Year 3 of Nero Claudius Caesar Augustus Germanicus Imperator,",
        "Epeiph 12.",
        "[To N.N.,] former strategos of Peri Thebas.",
        "…",
      ]),
 dict(key='p.oxy;2;269', nlines=36, slug='p_oxy_2_269',
      name='Letter with loan copy — Tryphon asks Ammonas to collect a debt',
      date='after 13 May 57 CE', found='Oxyrhynchus, Egypt',
      lat=28.54, lon=30.658,
      content='Copy of Dioskoros’ 52-drachma bank loan, with Tryphon’s cover note: press him and exact the bond',
      trans=[
        "Copy. Dioskoros son of Zenodoros, Persian of the epigone, to Tryphon",
        "son of Dionysios, greeting. I acknowledge that I have from you, at the Sarapeion near the city of",
        "the Oxyrhynchi, through the bank of Archibios son of Archibios, fifty-two",
        "drachmas of Imperial silver coin as principal,",
        "to which nothing at all has been added; which I will also repay you on the thirtieth",
        "of the month Kaisareios of the present 3rd year of Nero Claudius",
        "Caesar Augustus Germanicus Imperator, without any",
        "postponement. And if I do not repay as written, I will forfeit to you",
        "the aforesaid principal increased by half, and for the time",
        "overdue the proper interest, you having the right of execution",
        "upon me and upon all my property,",
        "as if by legal judgment. This bond is valid wherever produced",
        "and for whoever produces it. Year 3 of Nero Claudius Caesar",
        "Augustus Germanicus Imperator, month Germanikeios 18, dies Augusta.",
        "Copy of the subscription. I, Dioskoros son of Zenodoros, have the fifty-two",
        "drachmas of silver as principal, and I will repay",
        "as stated above. I, Zoilos son of Horos, wrote for him since he does not know",
        "letters. Year 3 of Nero Claudius Caesar Augustus Germanicus",
        "Imperator, month Germanikeios 18, dies Augusta.",
        "Copy of the bank-note. Year 3 of Nero Claudius Caesar Augustus",
        "Germanicus Imperator, month Germanikeios 18, dies Augusta.",
        "Through Theon son of Syros, agent of Archibios the banker, the payment was made.",
        "(2nd hand) Tryphon to Ammonas",
        "the tall, his dearest,",
        "greeting. If you can,",
        "— I beg you — press",
        "Dioskoros and exact from",
        "him the",
        "bond; and",
        "if he gives you the money,",
        "give him a receipt,",
        "and if you find someone trust-",
        "worthy, give him the money",
        "to bring to me.",
        "Greet all your",
        "people. Farewell.",
      ]),
 dict(key='p.oxy;2;294', nlines=34, slug='p_oxy_2_294',
      name='Letter — Sarapion to Dorion: houses searched, awaiting the inquiry',
      date='11 Dec 22 CE', found='Alexandria, Egypt (found at Oxyrhynchus)',
      lat=31.2, lon=29.9,
      content='Sarapion, in Alexandria, hears the houses were searched; men in custody until the prefect’s inquiry',
      trans=[
        "The inquiry […]",
        "Sarapion to Dorion [his brother, greet-]",
        "ing and continual good health. [Since I ar-]",
        "rived in Alexandria on the [… of the under-]",
        "written month, I learned [from certain]",
        "fishermen … to Alexandria […] that",
        "Sa…illa(?) … […]",
        "from me in the court, and the house [of]",
        "Sekonda has been searched, and […]",
        "my house has been searched, and […]",
        "and … whether these things are really so.",
        "You will do well, then, to write me a reply",
        "about this, so that I myself may present a pe-",
        "tition to the prefect. Do not do otherwise. I",
        "myself have not even anointed myself until I hear",
        "word from you about everything. And I am being",
        "pressed by friends to become a household-man of the chief",
        "usher Apollonios, so that I may come with him to the in-",
        "quiry. The deputy of the stra-",
        "tegos and Justus the sword-bearer are in cus-",
        "tody, as the prefect ordered, until",
        "the inquiry — unless they persuade the chief",
        "usher to give security for them until the in-",
        "quiry. About Phalakros, write me how",
        "he is again being coddled up there. Do not do other-",
        "wise. And I told Diogenes your friend not to wrong",
        "me … regarding the expense of what he has of mine;",
        "for … with the chief usher. And I ask you",
        "and entreat you, write me a reply about",
        "what has happened. Before all, take care of",
        "yourself, that you stay well. Look after Demetrous",
        "and Dorion our father. Farewell.",
        "Year 9 of Tiberius Caesar [Augustus, Cho]iak 15.",
        "Deliver to Dorion my brother.",
      ]),
 dict(key='p.oxy;2;295', nlines=17, slug='p_oxy_2_295',
      name='Letter — Thaeisous to her mother Syras: Seleukos has fled',
      date='c. 35 CE', found='Oxyrhynchus, Egypt',
      lat=28.54, lon=30.658,
      content='A daughter reports that Seleukos came and fled; tells her mother not to worry and to write',
      trans=[
        "Thaeisous to Syras her",
        "mother. Know that",
        "Seleukos came",
        "here and has fled.",
        "Do not wear your-",
        "self out with worry.",
        "Expect Lou-",
        "kia for the",
        "new year. Write me",
        "the day (you come).",
        "Greet — you —",
        "Ammonas",
        "my brother",
        "and …rap… and",
        "[my] sis-",
        "ter […]",
        "and Theonas my father.",
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
    r = load(it['key'])
    gk = [polish(l) for l in clean(r['greek'])][:it['nlines']]
    gk = [l for l in gk if l]
    tr = it['trans']
    assert len(gk) == len(tr), f"{it['key']}: greek {len(gk)} != trans {len(tr)}"
    parts = it['key'].split(';')
    label = (parts[0].upper().replace('P.OXY', 'P.Oxy') + ' '
             + (parts[1] + '.' if parts[1] else '') + parts[2])
    body = HDR.format(label=label, name=it['name'], key=it['key'], tm=r.get('tm', '?'),
                      date=it['date'], found=it['found'], shelf=r.get('shelf', '?'),
                      content=it['content'], lat=it['lat'], lon=it['lon'])
    body += "".join(f"r.{i}   {l}\n" for i, l in enumerate(gk, 1))
    body += "\n[TRANSLATION]\n"
    body += "".join(f"{i}   {l}\n" for i, l in enumerate(tr, 1))
    out = f"manuscripts/{it['slug']}.txt"
    with open(out, 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"built {out}  ({len(gk)} lines)")
print("ALL OK")

#!/usr/bin/env python3
"""Build letters tranche 4: P.Oxy 1.118/120/123, P.Tebt 2.419, P.Fay 109/133."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\(seal\)', '', l)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

SRC = {'p.oxy;1': '_PENDING_p.oxy1_91-140.json', 'p.tebt;2': '_PENDING_p.tebt2_408-445.json',
       'p.fay': '_PENDING_p.fay_91-140.json'}
def load(k):
    for pref, f in SRC.items():
        if k.startswith(pref):
            return json.load(open(f, encoding='utf-8'))[k]

ITEMS = [
 dict(key='p.oxy;1;118', nlines=43, slug='p_oxy_1_118',
      name='Letter — Saras and Eudaimon to Diogenes: an urgent ferry and provisions',
      date='late 3rd century CE', found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658,
      content='Detain the ferry, or notify the strategos and the peace-officers; bring incense and good frankincense; hurry the cooks Ammonas and Dioskoros',
      trans=[
        "Saras and Eudaimon",
        "to Diogenes their son, greeting.",
        "Advised by",
        "the most estimable Ammo-",
        "nion, because of the uncertainty of the",
        "journey, to send for a",
        "ferry-boat, we sent",
        "you a dispatch so that,",
        "if, persuaded by you, they",
        "se[n]d (it) while you are [p]res-",
        "ent, you may [de]tain what is needed; but if",
        "not, you may notify",
        "both the strategos a[n]d",
        "the peace-officers, for",
        "our security,",
        "to be put on",
        "record. And knowing what",
        "the hospitality is like, having got",
        "from the priests a little",
        "…(?) and some frankincense,",
        "[and] buying up some good",
        "[stuff,] coming,",
        "[brin]g it. We hear",
        "[that] two days in",
        "[the He]rakleopo-",
        "lite (nome) he is, so, with the",
        "care that is yours,",
        "make haste, having",
        "(those) for whose sake you put in to harbor;",
        "for there is no profit if the",
        "needful things fall",
        "short at his arrival.",
        "Ammonas and Dioskoros",
        "the cooks have gone up to",
        "the O[x]yrhynchite (nome), meaning",
        "to come out at once. Since, then,",
        "they are slow, lest at some point",
        "there be need of them, at",
        "once drive them out.",
        "Farewell, for my good fortune.",
        "(2nd hand) Farewell, both for me and for you,",
        "good [fortune].",
        "To Diogenes.",
      ]),
 dict(key='p.oxy;1;120', nlines=38, slug='p_oxy_1_120',
      name='Letter — Hermias to his sister, in misfortune: “a man must withdraw”',
      date='3rd century CE', found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658,
      content='A despairing letter (in vulgar spelling) — “a man seeing himself in misfortune ought to withdraw and not simply fight fate” — with a note to his son Gunthos',
      trans=[
        "To his sister, Hermias greeting.",
        "For the rest, what to write you I do not know, for I have worn my-",
        "self out telling you each thing, and",
        "you do not listen. For a man seeing",
        "himself in misfortune ought even to with-",
        "draw, and not simply to fight",
        "what is fated. For though we have a birth of moderate",
        "and unlucky lot, not even",
        "so do we attend to ourselves. So far, then,",
        "nothing at all has yet been done;",
        "still, even so, if you care, send",
        "me someone — either Gunthos or Ammonios —",
        "to stay with me until I know",
        "how my affairs are settled. Am I being",
        "dragged along, or even shut out, until",
        "God takes pity on us? For Hermei[as]",
        "is in haste to come to you, but, though I",
        "asked him to stay, he was not willing,",
        "saying that he has some necessary business",
        "and must go up; and my son Genna-",
        "dios is not able to attend to the",
        "property, especially since he is in a foreign place and",
        "with the (military) corps. Manage your own affairs",
        "as is fitting, lest we be utterly over-",
        "turned. For we have not resolved to have",
        "anything (more), being in misfortune. Farewell to me, ever",
        "faring well.",
        "Hermeias to Gunthos his son, gree(ting).",
        "If Ammonios does not come at once",
        "to me, you yourself,",
        "putting all aside,",
        "come in his stead, doing your own work.",
        "But see that you do not",
        "leave me afflicted.",
        "And let me know how",
        "Didymos fares; do the",
        "days bring all things to completion?",
        "I pray for your health.",
      ]),
 dict(key='p.oxy;1;123', nlines=26, slug='p_oxy_1_123',
      name='Letter — Ischyrion the tabularius to his son: enrolment and robes',
      date='3rd–4th century CE', found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658,
      content='A worried father, distressed at hearing nothing; have Theodoros press Timotheos; the others have already entered with their colleagues — enter “with the chlamys”',
      trans=[
        "To my lord son Dionysotheon,",
        "his father, greeting.",
        "There is opportunity now too, with the man going up to you.",
        "It became necessary for me to address you.",
        "I greatly wonder, my son, that to this day I have not received",
        "letters from you informing me about your",
        "well-being. Even so, my master, write",
        "me back quickly; for I am much distressed because",
        "I did not receive letters from you. Go to my brother",
        "Theodoros and make him take the trouble",
        "to go to Timotheos and pass on to him",
        "to get his (affairs) ready, so that he may enter to take up his post. For already",
        "those of the other cities have brought in their attestation",
        "to their colleagues — they have entered. So, on entering",
        "with the robe, let the one coming know it, so that ready",
        "he may enter. So let them not be willing, without attestation,",
        "to set us against one another, as knowing that the same",
        "thing befalls us all. For we have been ordered",
        "to enter with the cloaks; whence let the one coming",
        "come ready, as meaning to take up his post.",
        "I greet my sweetest daughter Makkaria",
        "and my mistress your mother and all",
        "ours by name. I pray for your health for many",
        "years, lord son.",
        "Epeiph 22.",
        "To my lord son Dionysotheon, Ischyrion the tabularius.",
      ]),
 dict(key='p.tebt;2;419', nlines=25, slug='p_tebt_2_419',
      name='Letter — Heron: send the she-donkey to be branded',
      date='3rd century CE', found='Tebtunis (Arsinoite nome / Fayum), Egypt',
      lat=29.108, lon=30.937,
      content='Send the she-donkey tomorrow to be branded — a tribune was here for this; instructions on the daughter, hay, and watering the colophonia',
      trans=[
        "Heron to Heron the most hon(ored), greeting.",
        "By all means tomorrow,",
        "which is the 25th, send",
        "the she-donkey so that",
        "it be branded. See you do not",
        "neglect it, since",
        "a tribune was here",
        "today",
        "for this. If",
        "my daughter is ready,",
        "let her come",
        "up on the she-donkey,",
        "but the other donkey let it",
        "not come up until",
        "I tell you. And if",
        "my daughter does not come",
        "up, load it with",
        "hay and by night",
        "send it. Let it be your care",
        "about the water-",
        "ing of the colophonia",
        "and the simiais(?) and about",
        "the hay.",
        "I pr[a]y for your health.",
        "To Heron the manager.",
      ]),
 dict(key='p.fay;;109', nlines=15, slug='p_fay_109',
      name='Letter — Pisais to Herakles: pay the three staters to Kleon',
      date='19 June 10 BCE (?)', found='Euhemeria (Arsinoite nome / Fayum), Egypt',
      lat=29.4333, lon=30.4,
      content='Pay Kleon the three staters Seleukos said to give me — treat it as a loan to me; I have settled accounts with father and want a receipt',
      trans=[
        "Pisais to Herakles, greeting. Whenever in need you wish",
        "to use anything of mine, I do not at once hold you back; and now,",
        "I beg you, the three staters that Seleukos told",
        "you to give me — give them now to Kleon, reck-",
        "oning that you are lending them to me, even if you must put your cloak",
        "in pledge, because I have settled the account with",
        "(my) father and he has struck me off the books, and I want to take",
        "a receipt. For Seleukos has knocked them out of my hands here,",
        "saying that you have entrusted them to himself.",
        "And now, I beg you, reckoning that you are lending me",
        "[them], do not hold Kleon up, and join",
        "[wi]th [K]leon and ask Saras for the 12 dr.",
        "[So do not do oth]erwise.",
        "Year 20, Pa(uni) 25.",
        "To Herakleros(?)",
      ]),
 dict(key='p.fay;;133', nlines=18, slug='p_fay_133',
      name='Letter — Alypios to Heroninos: hold off the vintage two or three days',
      date='2 Feb 260 CE', found='Theadelphia (Arsinoite nome / Fayum), Egypt',
      lat=29.4333, lon=30.5333,
      content='From the Heroninos estate archive: the steward Herakleides sent to arrange the vintage; wait two or three days so the empty jars catch up and the wine turns out good',
      trans=[
        "Fr(om) Alypios [to Heroninos(?)]",
        "I have sent the stew[ar]d [Hera-]",
        "kleides to you, as you ask[ed],",
        "to make the arrangement for the vintage.",
        "Put it off two",
        "or three days, so that both the empty (jars) may",
        "[c]atch up with you, and also the wine",
        "may turn out good — for you know that",
        "the season is now rather late,",
        "as I did also in the other",
        "little estates. So, by your own inspection,",
        "not trusting the fruit-buyers, make the vint-",
        "age, and write me back accordingly.",
        "I have sent you also a little release-note of wine",
        "for the vintage, for you alone […]",
        "I pray for your health.",
        "To Heroninos, ma(nager of) Thraso.",
        "Year 7, Mesore 18.",
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
    if parts[0] == 'p.fay':
        label = f"P.Fay. {parts[2]}"
    elif parts[0] == 'p.tebt':
        label = f"P.Tebt {parts[1]}.{parts[2]}"
    else:
        label = f"P.Oxy {parts[1]}.{parts[2]}"
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

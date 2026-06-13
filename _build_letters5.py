#!/usr/bin/env python3
"""Build letters tranche 5: the last 9 pending letters."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\(seal\)', '', l)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = re.sub(r'\bv,\d\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    l = re.sub(r'…\s*\d+\s*characters', '…', l)
    return re.sub(r'\s+', ' ', l).strip()

SRC = {
  'p.oxy;2;298': '_PENDING_p.oxy2_286-320.json',
  'p.oxy;2;259': '_PENDING_p.oxy2_234-285.json',
  'p.oxy;3;525': '_PENDING_p.oxy3_485-534.json',
  'p.oxy;3;529': '_PENDING_p.oxy3_485-534.json',
  'p.tebt;2;408': '_PENDING_p.tebt2_408-445.json',
  'p.tebt;2;409': '_PENDING_p.tebt2_408-445.json',
  'p.tebt;2;415': '_PENDING_p.tebt2_408-445.json',
  'bgu;4;1081': '_PENDING_bgu4_1050-1100.json',
  'p.fay;;128': '_PENDING_p.fay_91-140.json',
}
OXY = dict(found='Oxyrhynchus, Egypt', lat=28.54, lon=30.658)
TEB = dict(found='Tebtunis (Arsinoite nome / Fayum), Egypt', lat=29.108, lon=30.937)

ITEMS = [
 dict(key='p.oxy;2;298', nlines=61, slug='p_oxy_2_298', **OXY,
      name='Letter — the adventures of a tax-collector',
      date='1st century CE',
      content='A harried collector reports from his rounds: sell the wheat and pay the dues, buy purple for a tunic, 30 days in the Letopolite for a paltry 600 drachmas, family greetings and gifts',
      trans=[
        "[…] to his dearest, greeting.",
        "[I received a letter fr]om Pausirion on the 25th of the present month",
        "[…] and read what was written in it, fir-",
        "[st about …] the fine of 200 dr., that the wheat of Arsous",
        "[…], and that the foster-child ran away from you, and that from Pau-",
        "[sirion] you did not get the eight [artab]as, and [tha]t the receipt Eudai-",
        "[mon …]. So, about the fine, se[ll] the wheat",
        "[…] a[n]d pay it, since we owe public dues; and",
        "[…] buy two double-fringed (cloaks?) and two ad-",
        "[ditional …] … of a double-fringed (cloak), and",
        "[…] buy staters’ worth of purple for a tuni(c)",
        "[…] for Thaisous, nothing else. So, having managed these things,",
        "[…] with the little one, since she greatly misses her;",
        "[…] of the business; if with good fortune you arrive, all",
        "[…] memoranda were brought me from Ale-",
        "[xandria … abo]ut the inheritances. And if anything else is still ow-",
        "[ing …] you will at once recover it; meanwhile I am crossing also into",
        "[the … no]me. I have stayed in the Le-",
        "[topolite … 3]0 days, scarcely having exacted 600 dr. I paid out",
        "[…] they have given a deposit of the land-registrations, and",
        "[…] for the little boy Sarapion he has made clothes in …",
        "[… for Thai]sous we did not [fin]d the receipt …",
        "[…] bring up … to me to Memphis, and the",
        "vouchers.",
        "About Hermodoros you write",
        "me: I am much weighed down by",
        "him, for again he troubles every-",
        "thing. If you find with you",
        "a younger man to en[ro]l",
        "in the records, bring him,",
        "since I want to be done with him,",
        "and Anoubas does not",
        "look kindly on h[im].",
        "Greet Ptolema[s] and all",
        "yours by name.",
        "Sarapion greets you,",
        "and all those of our house.",
        "Not much summer-fruit has yet come",
        "to be in Memphis at present.",
        "We sent to the children",
        "of your brother 500 beans and 50 ap-",
        "ples, and to your sister",
        "Apollonous 50 apples, and to the",
        "little one. Farewell. Pauni 26.",
        "We are much distressed on account",
        "of the foster-child Sarapous.",
        "Another time I wrote you",
        "that, if you find a buy-",
        "er for the share",
        "of the house in",
        "Tanais, let it be sold.",
        "And about the inhu-",
        "manity of those who ex[acted]",
        "(the dues), I myself […]",
        "… will repay […]",
        "…[…]",
        "he is seeking … …[…]",
        "of him, and has not …",
        "… until he ar[rives]",
        "to secure our",
        "house and …[…]",
      ]),
 dict(key='p.oxy;2;259', nlines=35, slug='p_oxy_2_259', **OXY,
      name='Letter with a bail-bond on oath — Theon will produce Sarapion',
      date='after 17 May 23 CE',
      content='Copy of a sworn surety: Theon swears by Tiberius Caesar to produce within thirty days the man he has gone bail for, over a gold bracelet; with a grim aside about “our mother”',
      trans=[
        "Copy of a written bon[d].",
        "Theon son of Ammo(nios), P[ersian o]f the epigone,",
        "to Demetrios, appointed over",
        "the prison of Zeus. I swear by Tiberius",
        "Caesar Novus Augustus Imperator",
        "that within thirty days",
        "I will produce the man I have gone bail for",
        "with you, from [t]he civic prison,",
        "in Pha̅o̅phi of the present year —",
        "Sara(pion) son of Sarapio(n), brought in [w]ith respect to a",
        "holograph bond for a gold bracelet of two minaiai,",
        "of Magianos, on the account of Aline daughter of",
        "Dionysios, citizeness, through Billos, assistant of the dioiketes.",
        "And if I do not produce (him) within the",
        "stated days, I will forfeit the",
        "aforesaid two gold mina-",
        "iai without delay, having no",
        "[r]ight to gain other time,",
        "nor to transfer myself to",
        "an[o]ther prison. If I keep my oath, may it",
        "be well with me; if I [fo]rswear, the contrary.",
        "Year 9 of Tiberius Caesar Augustus, Pach(on) 22.",
        "Pick out for Sarapio(n) — on whose account",
        "Dionysios came — that it was paid; and about",
        "the account of Heliodoros, settle it with him too,",
        "and take the silver. We are looking into it",
        "on this account. We did not sail up",
        "in this boat because it did not draw …",
        "or him giving security … me …",
        "until I make him himself …; but if [n]ot,",
        "he has embarked. Farewell.",
        "See me — how our mother",
        "[s]laughtered (a victim?) on account of the bond …",
        "[…]… […] … I have …",
        "[…] he acts we[ll].",
      ]),
 dict(key='p.oxy;3;525', nlines=11, slug='p_oxy_3_525', **OXY,
      name='Letter — the dreadful voyage through the Antaiopolite',
      date='early 2nd century CE',
      content='“The coasting-voyage of the Antaiopolite is most vexing, and every day I am burdened by it”; give a small libation-fee, and remember the night-festival of Isis',
      trans=[
        "The coasting-voyage of the Antaiopolite",
        "is most vexing, and ev-",
        "ery day I am burdened on its account",
        "and quite worn down by the",
        "business. If a small libation-fee must be given to the",
        "brother of the mother of",
        "the sons of Achillas, you will do well to give it,",
        "ta[ki]ng it from Sarapion on",
        "[my] account. Remember the night-",
        "[festival] of Isis in the Sara-",
        "p[eion].",
      ]),
 dict(key='p.oxy;3;529', nlines=20, slug='p_oxy_3_529', **OXY,
      name='Letter — covering note for foodstuffs, off to Koptos with the prefect',
      date='2nd century CE',
      content='Receive by Kerdon, for Dionysios, four kotylai of oil and a basket of sweetmeats with 100 figs and 100 nuts; “I am off to Koptos with the prefect”',
      trans=[
        "Before [all I pray that you]",
        "are in health. Rec[eiv]e by K[e]r-",
        "don, for Dionysios,",
        "four kotylai of unguent and",
        "a basket of sweetmeats",
        "containing 100 figs",
        "(and) 100 nuts, and half a chous",
        "of oil, of which you will give the same",
        "Dionysios",
        "four kotylai, and to yourself two kotý-",
        "lai. Greet your",
        "mother and",
        "Matris and her children",
        "and all who love",
        "you. I myself",
        "am going to Koptos with the",
        "prefect.",
        "[Deliver] to the house of Pausanias, former",
        "[scri]be of the city, to Athenarous, by Ker-",
        "don.",
      ]),
 dict(key='p.tebt;2;408', nlines=19, slug='p_tebt_2_408', **TEB,
      name='Letter — Hipponikos asks that his sons be barred from the grain dole',
      date='9 July 3 CE',
      content='Out of love for his sons, Hipponikos asks the dioiketes Akousilaos not to let wheat be given to them by Soterichos’ people',
      trans=[
        "Hipponikos to Akousila-",
        "os his dear[e]st, very",
        "many greetings. Know-",
        "ing how I es-",
        "teem and love you, I",
        "beg you, concerning my sons,",
        "out of affec-",
        "tion for Sote-",
        "richos’ people, not to allow",
        "wheat to be giv-",
        "en to them. I have written also",
        "to Lys[i]machos my dear-",
        "est about the",
        "same, as to you too. So do",
        "not do otherwise;",
        "and you too, about whatever you wish,",
        "write; for the rest, may you be in health.",
        "Farewell. Year 32 of Caesar, Epeiph 15.",
        "To the dio[i]k[et]es Ak[ousilaos.]",
      ]),
 dict(key='p.tebt;2;409', nlines=14, slug='p_tebt_2_409', **TEB,
      name='Letter — Dorion asks Akousilaos to forward good donkeys',
      date='15 June 5 CE',
      content='Reminding of 12 drachmas given in town, Dorion asks the dioiketes to have Lysimachos send three full-grown donkeys promptly',
      trans=[
        "Dorion to Akousilaos [t]he",
        "dioiketes, very many greetings",
        "and continual health. In",
        "the city I asked you, giving you",
        "12 dr., to give them to Lysimachos and a-",
        "sk him on my behalf to",
        "send 3 full-grown … promptly,",
        "knowing th[at] author-",
        "ity over them belongs to both Lysimachos and you.",
        "[You] I asked, my de[ar]est,",
        "knowing that it is convenient [for yo]u, [an]d",
        "I shall have them good and full-grown and well-",
        "disposed, thanks to you. Farewell. Year 34 of Caesar, P[a]u(ni) 21.",
        "[To] t[h]e city, to Akous, dioiketes.",
      ]),
 dict(key='p.tebt;2;415', nlines=16, slug='p_tebt_2_415', **TEB,
      name='Letter — Heraklas: send the other 96 drachmas, or come yourself',
      date='2nd century CE',
      content='Do not neglect the matter of Horos; send the remaining 96 drachmas at once, or come — “you are neglecting yourself”',
      trans=[
        "Heraklas to Hip[…],",
        "greeting.",
        "You will do w[el]l [not to ne-]",
        "glect abo[ut …]",
        "of Horos. So send",
        "at once the o[th]er",
        "96 dr.; and if you do not",
        "send, come at once",
        "to me, since you are",
        "neglecting your own self. I gr-",
        "eet warmly your fa-",
        "ther [a]nd a[l]l the house-",
        "[ho]ld.",
        "[Fa]rewe[l]l.",
        "To Ploutammon from […]",
        "[.]…ron; deli[ver.]",
      ]),
 dict(key='bgu;4;1081', nlines=9, slug='bgu_4_1081',
      name='Letter — Didymos to his lady Hermione: greetings',
      date='2nd–3rd century CE', found='Arsinoite nome, Fayum, Egypt',
      lat=29.3084, lon=30.8428,
      content='A short note of greeting and prayer for Hermione’s health, asking for news of how she fares; greetings to the family',
      trans=[
        "Didymo[s] to Hermione his lady, ma[n]y greetings.",
        "Finding the opportunity of the man coming to you,",
        "I rejoiced, that I might greet you and pray to the",
        "gods for you, that they keep you safe; and now you will do well",
        "to write us about your health.",
        "Your sons greet you; I greet Eudaimon",
        "and Souerous and Eudaimonis and Elkike(?).",
        "Farewell.",
        "To Hermione ✗ from Didymos.",
      ]),
 dict(key='p.fay;;128', nlines=7, slug='p_fay_128',
      name='Letter — Midas to Akous: the Pontic man and the house',
      date='first half of 3rd century CE (?)',
      content='Go to the estimable Posidonios and tell him the Pontic man has not turned to buying the house from us; we approached him and he gave us a token to Pontikos',
      found='Euhemeria (Arsinoite nome / Fayum), Egypt', lat=29.4333, lon=30.4,
      trans=[
        "Midas to Akous the […], greeting.",
        "Go to the most estimable Posi-",
        "donios and tell him that the",
        "Pontic man has not turned to taking the",
        "house from us. We approached",
        "him and he gave",
        "us a token to Pontikos.",
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
    r = json.load(open(SRC[it['key']], encoding='utf-8'))[it['key']]
    gk = [polish(l) for l in clean(r['greek'])][:it['nlines']]
    gk = [l for l in gk if l]
    tr = it['trans']
    assert len(gk) == len(tr), f"{it['key']}: greek {len(gk)} != trans {len(tr)}"
    parts = it['key'].split(';')
    if parts[0] == 'p.fay':
        label = f"P.Fay. {parts[2]}"
    elif parts[0] == 'p.tebt':
        label = f"P.Tebt {parts[1]}.{parts[2]}"
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

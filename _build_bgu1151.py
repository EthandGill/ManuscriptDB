#!/usr/bin/env python3
"""Build BGU 4.1151-1200 contracts: 1153, 1157, 1163, 1180."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

DATA = json.load(open('_PENDING_bgu4_1151-1200.json', encoding='utf-8'))
ALX = dict(found='Alexandria, Egypt', lat=31.2, lon=29.9)

ITEMS = [
 dict(key='bgu;4;1153', nlines=30, slug='bgu_4_1153', **ALX,
      name='Double release — a repaid loan, and the nurse Martha discharged',
      date='16 May 14 BCE',
      content='Two settlements on one sheet: Arsinoe acknowledges repayment of 300 drachmas with the paramone of Paron annulled; and mutual releases over the child nursed by Martha',
      trans=[
        "[To Pro]tarch(os),",
        "from Arsinoe daughter of Ammo(nios), citizeness, with as guardian her son Niko-",
        "[d]emos son of Dionysio(s), of the Maro(nean) deme, and f(rom) Thermion daughter of Hermio(s), with as guardian",
        "[A]mmo(nios) son of Psammis, of the Eusebe(ian) deme. Arsino(e) concedes that she has received",
        "from Thermion, from hand to hand out of the hou(se), what she lent her by agree(ment)",
        "through the registry in the 15th (year) of Caesar, Thoth: three hundred",
        "silver drachmas; [and] that the agree(ment) of the loan is void, together with the",
        "(clause of) paramone of her son Paron",
        "signified along with it; and that no right of approach is left to",
        "Arsino(e), nor to <any other> on her behalf, against Thermion — neither",
        "about the same matters",
        "nor about anything else at all, written or unwritten, up to the pres(ent)",
        "day; and that whoever transgresses this is liable",
        "<both for the damages and for the appointed fine>, the terms remaining nonetheless valid.",
        "Year 16 of Caesar, Pacho(n) 21.",
        "… in the times of Caesar, concerning her own slave child [Agal]mat[ion, so a]s",
        "to be nursed by the same Martha; and that no (right of approach)",
        "is left [to] Marion, nor to any other on her behalf, against Souerou(s) —",
        "neither upon the aforesaid agree(ment), which likewise is void, nor upon",
        "anything else at all, written or unwrit(ten),",
        "[from times past up to] the pres(ent) day; and that Martha (shall have none)",
        "against Marion, neither",
        "[about the] nursing-wages of the time between, nor against the little slave",
        "child,",
        "[and shall not pro]ceed (against them) in any way; and that whoever does proceed against",
        "Souero(us), or con-",
        "travenes the contract, shall desist at once at his own exp(ense) and — the terms",
        "remaining nonetheless valid —",
        "the transgressor is moreover liable for the dam(ages) and the <appointed> fi(ne). We req(uest registration).",
        "Year 16 of Caesar, Pacho(n) 21.",
      ]),
 dict(key='bgu;4;1157', nlines=29, slug='bgu_4_1157', **ALX,
      name='Hire-purchase of a timber barge — thirty-five cubits long',
      date='11–10 BCE',
      content='Three prior tribunal agreements over a 1,032-drachma loan resolve into a fifty-year lease of two-thirds of Ammonios’ timber-carrying barge',
      trans=[
        "To Pro[tarchos]",
        "f[rom Ammonios son of …, and from Pnepheros son of …,]",
        "[and Piesies son of …, and Petearenphois son of P]iesies.",
        "[Whereas, by three agreements completed through the tribunal — by one,] made [in the]",
        "four[th (year) of Ca]esar, P[auni(?) …,] Pnepheros and",
        "Piesies, and further Petearenphois son of Piesies, [have acknowledged receipt] from Ammonios of one thousand",
        "and thirty-two silver drachmas",
        "at interest; and by the second, Ammonios has acknowledged that, on recovering these and the",
        "in[terest,]",
        "he will credit them to the three — an agreement of hire-purchase of the timber-carry-",
        "ing barge belonging to him, of thirty-five cubits, eleven cubits in beam; and by the third,",
        "made in the nineteenth year of Caesar, Epeiph, that Ammonios, having received",
        "from",
        "Pnepheros and Piesies, toward the aforesaid principal, three hun-",
        "dred silver drachmas, has credited them to Petearenphois according to the agreement approved by them concerning hire-pur-",
        "chase of … a third share of the said barge — now we agree",
        "with one another on these terms: Ammonios, having recovered from Pnepheros and Piesies the remain(ing) […]",
        "of the loan — seven hundred and thirty-two silver drachmas — and the accrued",
        "interest, shall render void … the said agreements of the loan [and] of the hire-purchase,",
        "and forthwith has leased to them, Pnepheros and [Pie]sies,",
        "for a per(iod) of",
        "fifty years from Pharmouthi of the present twentieth year of Caesar, the remaining",
        "[two] shares [of the same barge,] … to work it …",
        "… to bring in, and whatever they may wish to contribute; and forthwith […]",
        "neither of them, nor any other on his behalf, shall proceed about […]",
        "… and the interest; and he shall guarantee the two shares of the [bar]ge […]",
        "[…] … to the two, at once, unimpeded; or — the agreed terms remaining nonetheless valid —",
        "[he shall pay back the] principal with half again, [and the damages and expenses,]",
        "[as if by legal judgment. …]",
      ]),
 dict(key='bgu;4;1163', nlines=26, slug='bgu_4_1163', **ALX,
      name='Release — the price of papyrus rolls paid in full',
      date='16–13 BCE',
      content='Demetrios and Patron paid 300 drachmas through the money-changing bank of Dionysios for papyrus rolls; Demetrios releases Philammon from all claims',
      trans=[
        "(2nd hand?) Sheet (kollema).",
        "(1st hand) To Protarchos,",
        "from Philammon son of Ammonios and f(rom) Deme(trios) son of Sarap(ion), of the Philome(torean) deme.",
        "Concerning the matters agr[eed,] De(metrios) [conce]des",
        "that neither they nor any other on their behalf will proceed against",
        "Philammo(n) over what they have paid through the bank",
        "toward the price of papyrus rolls in the 13th (year) of Caesar, in the Epagomenai — Demetrios one hundred drachmas through the",
        "mo(ney-changing) bank of Dionysios, and Patron through the s(ame)",
        "bank in the same (year) 200 (drachmas), making …",
        "three hundred drach[mas] …; because, over the three hundred drachmas all told, Demetrios",
        "has been satisfied by Philammo(n) and has rece(ived) from him, from",
        "hand to hand out of the hou(se), what was mu-",
        "tually agreed; the said bank-payments are forthwith void; and he will also fur-",
        "nish",
        "Patron not proceeding against the same Philammo(n) about the two hundred silver",
        "(drachmas), [nor]",
        "about anything else at all, written or unwritten, up to the pres(ent) day,",
        "and no",
        "right of approach is left to Deme(trios) against Philammo(n) about anything, like-",
        "wise written or unwritten, from",
        "the same day; and that, should anyone proc[eed] against Philammo(n) about the",
        "same, Demetrios himself will make him desi[st]",
        "at once at his own exp(ense), and will pay him whatever be exacted from or los[t] by Philammon on",
        "account of this, with ha(lf again), and the damages and ex[penses,] as if b[y judg(ment),]",
        "[or —] the agr(eed terms) remaining nonetheless valid —",
        "(he is liable) for the appoin(ted) fi(ne).",
      ]),
 dict(key='bgu;4;1180', nlines=37, slug='bgu_4_1180', **ALX,
      name='Loan of 200 drachmas repaid in papyrus stalks — twenty thousand armfuls',
      date='Mar–Apr 12 BCE',
      content='A legionary lends 200 drachmas interest-free; in lieu of interest the lessees of a papyrus marsh deliver twenty thousand armfuls of stalks and a drachma a day',
      trans=[
        "Sheet.",
        "To Pr[ot]ar[chos]",
        "from Marcus […]…trius, son of Marcus, …, soldier [of the 22nd legi-]",
        "on, of the th[i]rd cohort, century of Atilius, [and from Marius son of …,]",
        "Per(sian) of the epigo(ne), [and] his wife Thaesis daughter of …, [with as guardian her]",
        "husband. Marius and Thaesis concede that they have from Marcus, from",
        "hand to hand out of the hou(se),",
        "two hundred drach(mas) of Ptol(emaic) silver, free of interest, on the binding condition that she and Marius,",
        "in lieu of int(erest) for the 18th (year) of Caesar, will furnish to Marcus of papyrus stalks twenty thousand",
        "armfuls, and of six-armful loads three thousand five hundred, from the",
        "papyrus marsh they hold on lease, deliver…(?) in the …",
        "[…] of however much he receives from them each day […] …",
        "… and … the fines being reckoned for each … either of them …",
        "… and ten yoke(?) … a third; and Marius and Thaesis will pay",
        "to Marcus, toward the two hundred silver (drachmas), from Pauni of the pres-",
        "ent 18th (year) of Caesar, for the remaining six months, one silver (drachma) each (day) …",
        "…, making no day in the month an emp-",
        "ty one, … the stalks to Marcus to …, or to whatever (place)",
        "[he may choose] … at their own expense, deliver-",
        "[ing them] … acceptable, and loads … as is fit(ting) …",
        "… to the same … in kind …",
        "… to them for the aforesaid time …",
        "[…] stalks, nor to drag out the daily",
        "furnishing of the …; or, in whatever they transgress, they are",
        "liable at once to seizure and to be held until they pay back the",
        "two hundred silver (drachmas), or whatever remains, with half again, and the [dam-]",
        "ages and exp(enses), and a fine of 200 (drachmas), the right of execution being from …,",
        "they being mutual sureties for payment, and from either one, whichever he choo(ses), and from",
        "all their belong(ings), as if by judg(ment); void being also whatever pleas",
        "they may bring forward, every shel(ter); and […]",
        "… to them of whatever he receives each day […]",
        "… and not to drag it out; nor may he [before the]",
        "aforesaid time abandon the … of the stalks […;]",
        "and when paid in full with the 200 silver (drachmas) as afore[said, he shall confirm]",
        "this agreement, or he too shall pay whatever [he may owe]",
        "toward the price, with ha(lf again), and the equal fine. We req(uest registration).",
        "Year 18 of Caesar, Pharmo(uthi).",
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
    label = f"BGU 4.{num}"
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

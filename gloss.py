#!/usr/bin/env python3
"""
gloss.py — formula-aware DRAFT translator for the documentary tax-receipt /
grain-measure ostraca (esp. O.Wilck.). It pre-fills the blank [TRANSLATION]
slots of a _translate_*.txt scaffold with a best-effort English draft so the
translator REVIEWS + CORRECTS deltas instead of typing every line.

  python gloss.py _translate_o.wilck_911-960.txt

It NEVER touches [GREEK]; it only fills blank translation lines and drafts a
generic name:/content:. Lines it can't fully resolve keep transliterated Greek
(usually a personal name) so they're easy to eyeball. ALWAYS review the result.
"""
import re, sys, unicodedata

GRK = "Ͱ-Ͽἀ-῿"

# ── Greek numerals → int ──────────────────────────────────────────────────────
_NUMVAL = {'α':1,'β':2,'γ':3,'δ':4,'ε':5,'ϛ':6,'ζ':7,'η':8,'θ':9,'ι':10,
 'κ':20,'λ':30,'μ':40,'ν':50,'ξ':60,'ο':70,'π':80,'ϟ':90,'ρ':100,'σ':200,
 'τ':300,'υ':400,'φ':500,'χ':600,'ψ':700,'ω':800}
def grknum(tok):
    t = tok.strip()
    if not t or any(c not in _NUMVAL for c in t): return None
    return sum(_NUMVAL[c] for c in t)

# ── transliteration (accents stripped) ────────────────────────────────────────
_DIGRAPH = [('γγ','ng'),('γκ','nk'),('γξ','nx'),('γχ','nch'),('ου','ou'),
 ('αυ','au'),('ευ','eu'),('ηυ','eu'),('θ','th'),('φ','ph'),('χ','ch'),('ψ','ps')]
_MONO = {'α':'a','β':'b','γ':'g','δ':'d','ε':'e','ζ':'z','η':'e','ι':'i','κ':'k',
 'λ':'l','μ':'m','ν':'n','ξ':'x','ο':'o','π':'p','ρ':'r','σ':'s','ς':'s','τ':'t',
 'υ':'y','ω':'o','ϊ':'i','ϋ':'y'}
def translit(word):
    w = ''.join(c for c in unicodedata.normalize('NFD', word) if not unicodedata.combining(c))
    w = w.lower()
    for a,b in _DIGRAPH: w = w.replace(a,b)
    out = ''.join(_MONO.get(c, c) for c in w)
    return out.capitalize() if out else word

# ── months ────────────────────────────────────────────────────────────────────
MONTHS = {'Θὼθ':'Thoth','Φαῶφι':'Phaophi','Ἁθὺρ':'Hathyr','Χοίαχ':'Choiak','Χοιὰκ':'Choiak',
 'Τῦβι':'Tybi','Μεχεὶρ':'Mecheir','Μεχ':'Mecheir','Φαμενὼθ':'Phamenoth','Φαμ':'Phamenoth',
 'Φαρμοῦθι':'Pharmouthi','Φαρμ':'Pharmouthi','Παχὼν':'Pachon','Παχ':'Pachon','Παῦνι':'Pauni',
 'Παῦ':'Pauni','Παῦν':'Pauni','Ἐπεὶφ':'Epeiph','Ἐπὶφ':'Epeiph','Ἐφεὶπ':'Epeiph','Μεσορὴ':'Mesore',
 'Μεσο':'Mesore','Καισαρείου':'Kaisareios','Καισ':'Kaisareios'}

# ── ordered phrase/token rules (applied with re.sub in order) ─────────────────
# parentheses in the Greek hold editor-resolved abbreviations; \(.*?\) is tolerated.
P = r"\([^)]*\)"   # an abbreviation-paren
RULES = [
 # most-specific tokens first
 (r"μέ"+P+r"τρ\w*|μέτρη"+P+r"|μέτρ"+P+r"|μέτ"+P+r"(?=\s)|μέ\(τρημα\)", "Measure"),
 (r"\(ὁμοίως\)|ὁ"+P+r"(?=\s)|ὁμ"+P, "likewise"),
 (r"\(δεκανοῦ\)", "decanus"),
 (r"ἀπ"+P+r"(?=\s)|ἀπὸ", "from"),
 # multi-word formula chunks first
 (r"εἰς θησ"+P, "into the granary"),
 (r"θησ"+P+r"|θη"+P+r"|θησαυρ\w*|θησαυρὸν", "of the granary"),
 (r"μη"+P+r"|μητροπ"+P+r"|μητρ"+P+r"|μ"+P+r"(?= γ)", "of the metropolis"),
 (r"κω"+P+r"|κωμ"+P, "of the villages"),
 (r"διο"+P+r"|διοι"+P+r"|διοικ"+P+r"|διοίκ\w*", "of the administration"),
 (r"ἱερῶ"+P+r"|ἱε"+P+r"|ἱερ"+P+r"|ἱερῶν|ἱερῶ\(", "of the temples"),
 (r"Ἄνω\s*"+P, "of the Upper toparchy"),
 (r"κάτω\s*"+P, "of the Lower toparchy"),
 (r"γενή"+P+r"|γ"+P+r"ή"+P+r"|γενημ"+P+r"|γενη"+P+r"|γ\(ενήματος\)|γ\(εν\)ή"+P, "of the produce"),
 (r"διὰ γεω"+P+r"|δι"+P+r"\s*γ"+P+r"|διὰ γ"+P, "through the cultivator"),
 (r"εἰς ἀρίθ"+P+r"\s*μη"+P, "for the account of the month"),
 (r"τοῦ κυρίου|τοῦ κυρ"+P+r"|του κυ"+P+r"|τοῦ κυ"+P, "the lord"),
 (r"τῶν κυρίων", "the lords"), (r"Σεβασ"+P+r"|Σεβαστῶν", "Augusti"),
 (r"Αὐρηλίου|Αὐρη"+P+r"ου|\[Αὐρη\]λίου", "Aurelius"), (r"Οὐήρου|Ο\[ὐήρου\]", "Verus"),
 (r"παρελάβ\w*|παρελαβ\w*", "we have received"),
 (r"γενήματος|γενημ\w*|γενη\w*(?!\))", "of the produce"),
 (r"παρὰ σο\w*", "from you"),
 (r"στεφ"+P+r"\s*χρ?"+P, "the gold-crown tax"),
 (r"τι"+P+r"\s*οἴν\w*", "the price of wine"),
 (r"τι"+P+r"\s*φοί"+P, "the price of dates"),
 # emperors
 (r"Ἀντωνείνου|Ἀντωνίνου|Ἀντ"+P+r"ου|Ἀν"+P+r"ου", "of Antoninus"),
 (r"Ἁδριανοῦ Καίσαρος|Ἁδριανοῦ(?= τοῦ)", "of Hadrian"),
 (r"Τραιανοῦ", "of Trajan"), (r"Δομιτιανοῦ|Δο"+P+r"ου|Δομ"+P+r"ου", "of Domitian"),
 (r"Νέρωνος", "of Nero"), (r"Οὐεσπασιανοῦ|Οὐησπ\w*", "of Vespasian"),
 (r"Καίσαρος", "Caesar"), (r"Σεβαστοῦ", "Augustus"), (r"Γερμανικοῦ", "Germanicus"),
 # office / actor phrases
 (r"πράκ"+P+r"|πρ"+P+r"(?=\s)", "collector"),
 (r"ἀργ"+P, "of money-taxes"),
 (r"τελ"+P+r"|τ"+P+r"λ"+P, "tax-farmers"),
 (r"ἐπιτη"+P+r"|ἐπιτ"+P+r"|ἐπι"+P+r"(?=\sθησ)|ἐπιτηρη"+P, "overseers"),
 (r"ἀπαιτ"+P+r"|ἀπαι"+P+r"|ἀπετητ"+P, "collectors"),
 (r"\(μέτοχοι\)|μ\(έτοχοι\)|μέ"+P+r"χ"+P+r"|μέ"+P+r"(?=\s)|\(μετόχων\)", "partners"),
 (r"ἀχυρ"+P+r"|ἀχυράρι"+P+r"|ἀχυροπράκ"+P, "chaff-collectors"),
 (r"σιτολ"+P+r"|σιτο"+P, "grain-officer"),
 (r"βοηθ"+P+r"|βοη"+P, "assistant"),
 (r"ἐπί\s*τροπ\w*|ἐπίτροπ\w*", "steward"),
 # tax names
 (r"βαλ"+P+r"|βα"+P+r"(?=\s)|βαλανε\w*|βαλανικ\w*", "bath-tax"),
 (r"λαο"+P+r"|λαογρ"+P+r"|λα\(ο\)γρ"+P, "poll-tax"),
 (r"χω"+P+r"|χωμ"+P, "embankment-tax"),
 (r"μερισ"+P+r"|μερισμ"+P+r"|μερι"+P+r"|μερ"+P, "the assessment"),
 (r"σκοπ"+P, "the watchtower-tax"), (r"δι"+P+r"λῶν|διπλῶν|δι"+P+r"\(πλῶν\)", "the doubles"),
 (r"ἐπικ"+P+r"|ἐπι"+P+r"(?=\s)", "the fruit-tax"),
 (r"γεω"+P+r"|γεο"+P+r"|γε"+P+r"(?=\s)", "the land-survey tax"),
 (r"ἐνοικ"+P+r"|ἐνοικί"+P, "rent"),
 (r"ἀννο"+P+r"|ἀννώ"+P+r"|ἀνώ"+P, "the annona"),
 (r"τέλ"+P+r"|τέλο"+P, "the tax"),
 # crops / goods
 (r"\(πυροῦ\)|πυροῦ", "of wheat"), (r"κρ"+P+r"|κριθ"+P+r"|κριθῆς", "of barley"),
 (r"φακοῦ", "of lentils"), (r"κρότωνος|κρό"+P, "of castor"), (r"λαχ"+P+r"|λαχαν\w*", "of vegetable-seed"),
 (r"οἴνου", "of wine"), (r"φοί"+P+r"|φοι"+P, "of dates"), (r"ἐλαίο\w*|ἐλαίου", "of oil"),
 (r"σησάμ\w*", "of sesame"), (r"ἀχύ"+P+r"|ἀχύρου|ἄχυρ\w*", "of chaff"),
 # places
 (r"Χ"+P+r"|Χά"+P, "Charax"), (r"Νό"+P, "the South"), (r"Λ"+P+r"(?=\s|$)", "the West"),
 (r"Ἀγο"+P+r"|Ἀγ"+P, "the Markets"), (r"Κε"+P+r"|Κερ"+P, "the Potteries"),
 (r"Ὠφιήο\w*|Ὠφιή"+P, "Ophieus"), (r"Ἑρμώνθ\w*|Ἑρμ"+P+r"(?=\s)", "Hermonthis"),
 (r"νή"+P, "the islands"),
 # actions / connectors
 (r"μεμέτρη"+P+r"|μεμέ"+P+r"|με"+P+r"τρ\w*|με\(μετρήκασιν\)|μ\(εμέτρηκεν\)", "has measured in"),
 (r"διέγρ"+P+r"|διαγ"+P, "has paid"),
 (r"ἔσχο"+P+r"|ἔσχ"+P, "received"),
 (r"ἀπέσχ"+P+r"|ἀπέχ"+P+r"|ἀπ"+P+r"χ"+P, "received in full"),
 (r"σεση"+P+r"|σ"+P+r"η"+P+r"|σε"+P+r"|σεσημ"+P, "have signed"),
 (r"\(γίνονται\)|\(γίνεται\)|\(γίνεσθαι\)", "total"),
 (r"ὑπ"+P, "for"), (r"ὀνό"+P+r"|ὀν"+P, "in the name of"), (r"διὰ", "through"),
 (r"χα"+P+r"|χαίρειν", "greeting"),
 (r"δι"+P+r"(?=\s)|δ"+P+r"\s*(?=[Α-Ω])", "through"),
 (r"πρ"+P+r"(?=\s)|π\(ρεσβυτέρῳ\)", "the elder"), (r"νε"+P+r"|νεω"+P+r"|ν"+P+r"(?=\s)", "the younger"),
 (r"μη"+P+r"(?=\s[Α-Ω])|μητ"+P, "whose mother is"),
 (r"θυγ"+P, "daughter"), (r"ἀδε"+P+r"|ἀδελφ"+P+r"|ἀδ"+P, "brother"),
 (r"υἱοῦ|υἱὸ"+P+r"|υἱῷ|υἱ"+P, "son"),
 (r"καὶ", "and"), (r"τοῦ καὶ|τὸν καὶ|τῷ καὶ|ἡ καὶ", "also called"),
 (r"χει"+P, "of the winter-crop"),
 # money / measure units
 (r"\(δραχμὰς\)|δραχ"+P+r"|\(δραχμαὶ\)|\(δραχμὴν\)|\(δραχμὴ\)|δραχμ\w*", "drachmas"),
 (r"\(ἀρτάβ\w*\)|ἀρτάβ\w*|\(ἀρτ"+P+r"\)", "artabas"),
 (r"\(ὀβολ\w*\)|ὀβ"+P+r"|ὀβολ\w*", "obols"),
 (r"\(τετρώβολον\)", "4 obols"), (r"\(τριώβολον\)", "3 obols"), (r"\(πεντώβολον\)", "5 obols"),
 (r"\(διώβολον\)", "2 obols"), (r"\(ἡμιωβέλιον\)", "½ obol"),
 (r"χ\(αλκο\w*\)|χ\(αλκοῦ\w*\)|χαλκ\w*", "chalkoi"),
 (r"γό"+P+r"|γόμ"+P+r"|γομ\w*|γόμ\w*", "loads"), (r"ἀγω"+P+r"|ἀγ"+P+r"(?=\s)", "loads"),
 (r"κε"+P+r"αμια|κεράμι\w*|κε"+P, "keramia"),
 # number words
 (r"μίαν|μία|ἓν|ἑνὶ", "one"), (r"δύο|δυω|δυο", "two"), (r"τρεῖς|τρῖς|τρε͂ς|τρεις", "three"),
 (r"τέσσαρ\w*", "four"), (r"πέντε", "five"), (r"ἓξ|ἕξ", "six"), (r"ἑπτὰ", "seven"),
 (r"ὀκτὼ", "eight"), (r"ἐννέα", "nine"), (r"δέκα", "ten"), (r"δώδεκα", "twelve"),
 (r"εἴκοσι", "twenty"), (r"τριάκοντα", "thirty"), (r"τεσσαράκοντα|τεσσερά\w*", "forty"),
 (r"πεντήκοντα", "fifty"), (r"ἑκατὸν|ἑκατόν", "hundred"),
 (r"ἥμισυ|ἥμυσυ|ἤμισυ|ἡμισευ", "and a half"), (r"τρίτον|τρίτο"+P, "and a third"),
 (r"τέταρτον|τέταρτο"+P, "and a quarter"), (r"ἕκτον|ἕκτο"+P, "and a sixth"),
 (r"ὄγδοον|ὄγδο"+P, "and an eighth"), (r"δωδέκατον|δωδέκ"+P, "and a twelfth"),
 (r"τετρακ"+P+r"|τετρακαιεικοστ\w*", "and a twenty-fourth"), (r"δίμοιρον|δίμο"+P, "and two-thirds"),
 (r"δωδέκατο\w*|δωδέκατο"+P, "and a twelfth"),
 (r"ἐπαγο"+P+r"|ἐπαγομενῶν", "intercalary days"),
 (r"\(ἔτους\)|\(ἔτει\)|\(ἔτος\)", "year"), (r"ἔτους", "year"),
]
RULES = [(re.compile(p), r) for p,r in RULES]

FRAC = {'𐅵':'½','𐅷':'⅔','𐅸':'¾','γ´':'⅓','δ´':'¼','ϛ´':'1/6','η´':'1/8','ιβ´':'1/12','κδ´':'1/24','ϛ´':'1/6'}

def gloss_line(greek):
    s = " " + greek + " "
    for sym,v in FRAC.items(): s = s.replace(sym, " "+v+" ")
    # months (word-boundary-ish)
    for g,en in sorted(MONTHS.items(), key=lambda x:-len(x[0])):
        s = re.sub(g, en, s)
    for rx,rep in RULES:
        s = rx.sub(rep, s)
    # merge leftover name-abbreviation parens: "Ψανσνῶτο(ς)" -> "Ψανσνῶτος"; drop "( )"
    s = re.sub(r"\(\s*\)", " ", s)
    s = re.sub(r"([%s])\(([%s]+)\)" % (GRK,GRK), r"\1\2", s)
    # Greek numerals: ONLY space-bounded tokens (years, days, amounts), not letters in words.
    # Skip common function-word forms that happen to be all numeral-letters.
    STOP = {'του','τοῦ','των','τῶν','τον','τὸν','τω','τῷ','τὸ','τα','τὰ','ον','ων','ος','ου',
            'οὐ','σου','σοῦ','συ','σὺ','ρον','νον','τι','τις','ος','ως','ο','η','ηι'}
    def numsub(m):
        tok = m.group(1)
        if tok in STOP: return m.group(0)
        v = grknum(tok)
        return (" "+str(v)+" ") if v is not None else m.group(0)
    s = re.sub(r"(?:^|\s)([αβγδεϛζηθικλμνξοπρστυφχψω]{1,4})(?=[\s.,·]|$)", numsub, s)
    # transliterate any remaining Greek-script runs (personal names)
    s = re.sub(r"[%s][%s'’]*" % (GRK,GRK), lambda m: translit(m.group(0)), s)
    s = re.sub(r"\s+", " ", s).strip(" .,·")
    # cosmetic: "year 17" word order, capitalize first
    s = re.sub(r"\b(\d+)\s+year\b", r"year \1", s)
    return (s[:1].upper()+s[1:]) if s else s

def main():
    path = sys.argv[1]
    raw = open(path, encoding="utf-8").read()
    parts = raw.split("\n=== "); head=parts[0]; out=[]
    filled=0
    for blk in parts[1:]:
        gk=[re.sub(r"^r\.\d+\s+","",l.strip()) for l in blk.split("[GREEK]")[1].split("[TRANSLATION]")[0].splitlines() if l.strip().startswith("r.")]
        drafts=[gloss_line(g) for g in gk]
        new=[]; section=None; ti=0
        for ln in blk.splitlines():
            if ln.strip()=="[TRANSLATION]": section="trans"; new.append(ln); continue
            if ln.startswith("name:") and "TODO" in ln: new.append("name:     Tax/grain receipt (DRAFT - verify)"); continue
            if ln.startswith("content:") and "TODO" in ln: new.append("content:  DRAFT auto-gloss - verify and rewrite"); continue
            if section=="trans":
                m=re.match(r"\s*(\d+)\s*$", ln)
                if m and ti<len(drafts): new.append(f"{int(m.group(1)):<5} {drafts[ti]}"); ti+=1; filled+=1; continue
            new.append(ln)
        out.append("\n".join(new))
    open(path,"w",encoding="utf-8").write(head+"\n=== "+"\n=== ".join(out))
    print(f"Drafted {filled} translation lines into {path}  (REVIEW before assembling)")

if __name__=="__main__":
    main()

"""Post-process all 8 Hebrews manuscripts: fix labels, prefixes, add translations."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
DIR = r'C:\ManuscriptDB\manuscripts'
OLD_TRANS = ('# ── TRANSLATION (optional) ──────────────────────────────────\n'
             '# Uncomment and fill in to show an English translation in the popup.\n'
             '# Format:  verse_ref   English text\n#\n# [TRANSLATION]\n'
             '# 1:1   The book of the genealogy of ...')

def load(name):
    with open(f'{DIR}\\{name}.txt', encoding='utf-8') as f:
        return f.read()

def save(name, txt):
    with open(f'{DIR}\\{name}.txt', 'w', encoding='utf-8') as f:
        f.write(txt)
    print(f'  Saved {name}.txt')

def fix_dup_verse(txt):
    txt = re.sub(r'(\d+):(\d+)-\2\b', r'\1:\2', txt)
    txt = re.sub(r'(\d+:\d+)-\1\b', r'\1', txt)
    return txt

def fix_recto_prefix(txt):
    def swap(m):
        block = m.group(0)
        return re.sub(r'^v\.(\d+)', r'r.\1', block, flags=re.MULTILINE)
    return re.sub(r'^(FOLIO \d+R — .+?)(?=^FOLIO |\Z)', swap, txt,
                  flags=re.MULTILINE | re.DOTALL)

def assign_labels(txt):
    """Replace FOLIO ? with 1R/1V/2R/2V... in order."""
    headers = re.findall(r'^FOLIO \? — .+$', txt, re.MULTILINE)
    for i, h in enumerate(headers):
        n = (i // 2) + 1
        sv = 'R' if i % 2 == 0 else 'V'
        new = h.replace('FOLIO ? — ', f'FOLIO {n}{sv} — ')
        txt = txt.replace(h, new, 1)
    return txt

def add_trans(txt, trans):
    if OLD_TRANS in txt:
        return txt.replace(OLD_TRANS, trans.strip())
    return txt.rstrip() + '\n\n' + trans.strip() + '\n'

def process(name, custom_label_fn=None, trans=''):
    txt = load(name)
    txt = fix_dup_verse(txt)
    if custom_label_fn:
        txt = custom_label_fn(txt)
    else:
        txt = assign_labels(txt)
    txt = fix_recto_prefix(txt)
    if trans:
        txt = add_trans(txt, trans)
    save(name, txt)

# ── P12  Hebrews 1:1 ──────────────────────────────────────────────────────────
# Page 20 = verso side of the leaf; Hebrews 1:1 is on the verso
def p12_labels(txt):
    return txt.replace('FOLIO ? — Hebrews 1:1', 'FOLIO 1V — Hebrews 1:1')

process('P12', p12_labels, """[TRANSLATION]
1:1    Long ago, at many times and in many ways, God spoke to our fathers by the prophets,
""")

# ── P13  Hebrews (scroll — use column labels) ─────────────────────────────────
def p13_labels(txt):
    # Rename sequential ? blocks
    order = [
        ('FOLIO ? — Hebrews 2:14-3:9',   'FOLIO Col.1 — Hebrews 2:14-3:9'),
        ('FOLIO ? — Hebrews 10:8-22',     'FOLIO Col.2 — Hebrews 10:8-22'),
        ('FOLIO ? — Hebrews 11:5-13',     'FOLIO Col.3 — Hebrews 11:5-13'),
        ('FOLIO ? — Hebrews 11:28-12:1',  'FOLIO Col.4 — Hebrews 11:28-12:1'),
        ('FOLIO ? — Hebrews 12:1-11',     'FOLIO Col.5 — Hebrews 12:1-11'),
        ('FOLIO ? — Hebrews 12:11-17',    'FOLIO Col.6 — Hebrews 12:11-17'),
    ]
    for old, new in order:
        txt = txt.replace(old, new, 1)
    # Annotate the all-GAP NTVMR columns with probable verse ranges
    txt = txt.replace('FOLIO 65\n', 'FOLIO Col.65 — Hebrews 10:29-11:4 (lacuna)\n')
    txt = txt.replace('FOLIO 68\n', 'FOLIO Col.68 — Hebrews 11:14-26 (lacuna)\n')
    txt = txt.replace('FOLIO 69\n', 'FOLIO Col.69 — Hebrews 11:26-28 (lacuna)\n')
    return txt

process('P13', p13_labels, """[TRANSLATION]
2:14   Since therefore the children share in flesh and blood, he himself likewise partook of the same things, that through death he might destroy the one who has the power of death, that is, the devil,
2:15   and deliver all those who through fear of death were subject to lifelong slavery.
2:16   For surely it is not angels that he helps, but he helps the offspring of Abraham.
2:17   Therefore he had to be made like his brothers in every respect, so that he might become a merciful and faithful high priest in the service of God, to make propitiation for the sins of the people.
2:18   For because he himself has suffered when tempted, he is able to help those who are being tempted.
3:1    Therefore, holy brothers, you who share in a heavenly calling, consider Jesus, the apostle and high priest of our confession,
3:2    who was faithful to him who appointed him, just as Moses also was faithful in all God's house.
3:3    For Jesus has been counted worthy of more glory than Moses — as much more glory as the builder of a house has more honor than the house itself.
3:4    (For every house is built by someone, but the builder of all things is God.)
3:5    Now Moses was faithful in all God's house as a servant, to testify to the things that were to be spoken later,
3:6    but Christ is faithful over God's house as a son. And we are his house, if indeed we hold fast our confidence and our boasting in our hope.
3:7    Therefore, as the Holy Spirit says, "Today, if you hear his voice,
3:8    do not harden your hearts as in the rebellion, on the day of testing in the wilderness,
3:9    where your fathers put me to the test and saw my works for forty years."
10:8   when he said above, "You have neither desired nor taken pleasure in sacrifices and offerings and burnt offerings and sin offerings" (these are offered according to the law),
10:9   then he added, "Behold, I have come to do your will." He does away with the first in order to establish the second.
10:10  And by that will we have been sanctified through the offering of the body of Jesus Christ once for all.
10:11  And every priest stands daily at his service, offering repeatedly the same sacrifices, which can never take away sins.
10:12  But when Christ had offered for all time a single sacrifice for sins, he sat down at the right hand of God,
10:13  waiting from that time until his enemies should be made a footstool for his feet.
10:14  For by a single offering he has perfected for all time those who are being sanctified.
10:15  And the Holy Spirit also bears witness to us; for after saying,
10:16  "This is the covenant that I will make with them after those days, declares the Lord: I will put my laws on their hearts, and write them on their minds,"
10:17  then he adds, "I will remember their sins and their lawless deeds no more."
10:18  Where there is forgiveness of these, there is no longer any offering for sin.
10:19  Therefore, brothers, since we have confidence to enter the holy places by the blood of Jesus,
10:20  by the new and living way that he opened for us through the curtain, that is, through his flesh,
10:21  and since we have a great priest over the house of God,
10:22  let us draw near with a true heart in full assurance of faith, with our hearts sprinkled clean from an evil conscience and our bodies washed with pure water.
11:5   By faith Enoch was taken up so that he should not see death, and he was not found, because God had taken him. Now before he was taken he was commended as having pleased God.
11:6   And without faith it is impossible to please him, for whoever would draw near to God must believe that he exists and that he rewards those who seek him.
11:7   By faith Noah, being warned by God concerning events as yet unseen, in reverent fear constructed an ark for the saving of his household. By this he condemned the world and became an heir of the righteousness that comes by faith.
11:8   By faith Abraham obeyed when he was called to go out to a place that he was to receive as an inheritance. And he went out, not knowing where he was going.
11:9   By faith he went to live in the land of promise, as in a foreign land, living in tents with Isaac and Jacob, heirs with him of the same promise.
11:10  For he was looking forward to the city that has foundations, whose designer and builder is God.
11:11  By faith Sarah herself received power to conceive, even when she was past the age, since she considered him faithful who had promised.
11:12  Therefore from one man, and him as good as dead, were born descendants as many as the stars of heaven and as many as the innumerable grains of sand by the seashore.
11:13  These all died in faith, not having received the things promised, but having seen them and greeted them from afar, and having acknowledged that they were strangers and exiles on the earth.
11:28  By faith he kept the Passover and sprinkled the blood, so that the Destroyer of the firstborn might not touch them.
11:29  By faith the people crossed the Red Sea as on dry land, but the Egyptians, when they attempted to do the same, were drowned.
11:30  By faith the walls of Jericho fell down after they had been encircled for seven days.
11:31  By faith Rahab the prostitute did not perish with those who were disobedient, because she had given a friendly welcome to the spies.
11:32  And what more shall I say? For time would fail me to tell of Gideon, Barak, Samson, Jephthah, of David and Samuel and the prophets —
11:33  who through faith conquered kingdoms, enforced justice, obtained promises, stopped the mouths of lions,
11:34  quenched the power of fire, escaped the edge of the sword, were made strong out of weakness, became mighty in war, put foreign armies to flight.
11:35  Women received back their dead by resurrection. Some were tortured, refusing to accept release, so that they might rise again to a better life.
12:1   Therefore, since we are surrounded by so great a cloud of witnesses, let us also lay aside every weight, and sin which clings so closely, and let us run with endurance the race that is set before us,
12:2   looking to Jesus, the founder and perfecter of our faith, who for the joy that was set before him endured the cross, despising the shame, and is seated at the right hand of the throne of God.
12:3   Consider him who endured from sinners such hostility against himself, so that you may not grow weary or fainthearted.
12:4   In your struggle against sin you have not yet resisted to the point of shedding your blood.
12:5   And have you forgotten the exhortation that addresses you as sons? "My son, do not regard lightly the discipline of the Lord, nor be weary when reproved by him.
12:6   For the Lord disciplines the one he loves, and chastises every son whom he receives."
12:7   It is for discipline that you have to endure. God is treating you as sons.
12:8   If you are left without discipline, in which all have participated, then you are illegitimate children and not sons.
12:9   Besides this, we have had earthly fathers who disciplined us and we respected them. Shall we not much more be subject to the Father of spirits and live?
12:10  For they disciplined us for a short time as it seemed best to them, but he disciplines us for our good, that we may share his holiness.
12:11  For the moment all discipline seems painful rather than pleasant, but later it yields the peaceful fruit of righteousness to those who have been trained by it.
12:12  Therefore lift your drooping hands and strengthen your weak knees,
12:13  and make straight paths for your feet, so that what is lame may not be put out of joint but rather be healed.
12:14  Strive for peace with everyone, and for the holiness without which no one will see the Lord.
12:15  See to it that no one fails to obtain the grace of God; that no "root of bitterness" springs up and causes trouble, and by it many become defiled;
12:16  that no one is sexually immoral or unholy like Esau, who sold his birthright for a single meal.
12:17  For you know that afterward, when he desired to inherit the blessing, he was rejected, for he found no chance to repent, though he sought it with tears.
""")

# ── P17  Hebrews 9:12-19 ──────────────────────────────────────────────────────
process('P17', trans="""[TRANSLATION]
9:12   he entered once for all into the holy places, not by means of the blood of goats and calves but by means of his own blood, thus securing an eternal redemption.
9:13   For if the blood of goats and bulls, and the sprinkling of defiled persons with the ashes of a heifer, sanctify for the purification of the flesh,
9:14   how much more will the blood of Christ, who through the eternal Spirit offered himself without blemish to God, purify our conscience from dead works to serve the living God.
9:15   Therefore he is the mediator of a new covenant, so that those who are called may receive the promised eternal inheritance, since a death has occurred that redeems them from the transgressions committed under the first covenant.
9:16   For where a will is involved, the death of the one who made it must be established.
9:17   For a will takes effect only at death, since it is not in force as long as the one who made it is alive.
9:18   Therefore not even the first covenant was inaugurated without blood.
9:19   For when every commandment of the law had been declared by Moses to all the people, he took the blood of calves and goats, with water and scarlet wool and hyssop, and sprinkled both the book itself and all the people,
""")

# ── P79  Hebrews 10:10-12; 10:28-30 ──────────────────────────────────────────
process('P79', trans="""[TRANSLATION]
10:10  And by that will we have been sanctified through the offering of the body of Jesus Christ once for all.
10:11  And every priest stands daily at his service, offering repeatedly the same sacrifices, which can never take away sins.
10:12  But when Christ had offered for all time a single sacrifice for sins, he sat down at the right hand of God,
10:28  Anyone who has set aside the law of Moses dies without mercy on the evidence of two or three witnesses.
10:29  How much worse punishment, do you think, will be deserved by the one who has trampled underfoot the Son of God, and has profaned the blood of the covenant by which he was sanctified, and has outraged the Spirit of grace?
10:30  For we know him who said, "Vengeance is mine; I will repay." And again, "The Lord will judge his people."
""")

# ── P89  Hebrews 6:7-9, 15-17 ────────────────────────────────────────────────
process('P89', trans="""[TRANSLATION]
6:7    For land that has drunk the rain that often falls on it, and produces a crop useful to those for whose sake it is cultivated, receives a blessing from God.
6:8    But if it bears thorns and thistles, it is worthless and near to being cursed, and its end is to be burned.
6:9    Though we speak in this way, yet in your case, beloved, we feel sure of better things — things that belong to salvation.
6:15   And thus Abraham, having patiently waited, obtained the promise.
6:16   For people swear by something greater than themselves, and in all their disputes an oath is final for confirmation.
6:17   So when God desired to show more convincingly to the heirs of the promise the unchangeable character of his purpose, he guaranteed it with an oath,
""")

# ── P114  Hebrews 1:7-12 ─────────────────────────────────────────────────────
def p114_labels(txt):
    # Only one page (page 10 = recto); label as 1R
    return txt.replace('FOLIO ? — Hebrews 1:7-12', 'FOLIO 1R — Hebrews 1:7-12')

process('P114', p114_labels, """[TRANSLATION]
1:7    Of the angels he says, "He makes his angels winds, and his ministers a flame of fire."
1:8    But of the Son he says, "Your throne, O God, is forever and ever, the scepter of uprightness is the scepter of your kingdom.
1:9    You have loved righteousness and hated wickedness; therefore God, your God, has anointed you with the oil of gladness beyond your companions."
1:10   And, "You, Lord, laid the foundation of the earth in the beginning, and the heavens are the work of your hands;
1:11   they will perish, but you remain; they will all wear out like a garment,
1:12   like a robe you will roll them up, like a garment they will be changed. But you are the same, and your years will have no end."
""")

# ── P116  Hebrews 2:9-11; 3:3-6 ──────────────────────────────────────────────
process('P116', trans="""[TRANSLATION]
2:9    But we see him who for a little while was made lower than the angels, namely Jesus, crowned with glory and honor because of the suffering of death, so that by the grace of God he might taste death for everyone.
2:10   For it was fitting that he, for whom and by whom all things exist, in bringing many sons to glory, should make the founder of their salvation perfect through suffering.
2:11   For he who sanctifies and those who are sanctified all have one source. That is why he is not ashamed to call them brothers,
3:3    For Jesus has been counted worthy of more glory than Moses — as much more glory as the builder of a house has more honor than the house itself.
3:4    (For every house is built by someone, but the builder of all things is God.)
3:5    Now Moses was faithful in all God's house as a servant, to testify to the things that were to be spoken later,
3:6    but Christ is faithful over God's house as a son. And we are his house, if indeed we hold fast our confidence and our boasting in our hope.
""")

# ── P126  Hebrews 13:12-13, 19-20 ────────────────────────────────────────────
process('P126', trans="""[TRANSLATION]
13:12  So Jesus also suffered outside the gate in order to sanctify the people through his own blood.
13:13  Therefore let us go to him outside the camp and bear the reproach he endured.
13:19  I urge you the more earnestly to do this in order that I may be restored to you the sooner.
13:20  Now may the God of peace who brought again from the dead our Lord Jesus, the great shepherd of the sheep, by the blood of the eternal covenant,
""")

print("\n=== ALL POST-PROCESSING DONE ===")

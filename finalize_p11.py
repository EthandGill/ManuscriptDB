"""
Finalize P11.txt:
1. Fix ? folio labels
2. Fix duplicate verse numbers (2:14-14, 3:20-20, 4:12-12)
3. Insert missing folios F1V, F4V, F6R in correct positions
4. Add full [TRANSLATION] section
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\ManuscriptDB\manuscripts\P11.txt'
with open(path, encoding='utf-8') as f:
    txt = f.read()

# ── 1. Fix ? labels ──────────────────────────────────────────────────────────
fixes = [
    ('FOLIO ? — 1 Corinthians 1:25-27', 'FOLIO 2R — 1 Corinthians 1:25-27'),
    ('FOLIO ? — 1 Corinthians 2:6-8',   'FOLIO 3V — 1 Corinthians 2:6-8'),
    ('FOLIO ? — 1 Corinthians 3:8-10',  'FOLIO 7R — 1 Corinthians 3:8-10'),
    ('FOLIO ? — 1 Corinthians 3:20-20', 'FOLIO 8R — 1 Corinthians 3:20'),
    ('FOLIO 5R — 1 Corinthians 2:14-14','FOLIO 5R — 1 Corinthians 2:14'),
    ('FOLIO 11R — 1 Corinthians 4:12-12','FOLIO 11R — 1 Corinthians 4:12'),
]
for old, new in fixes:
    if old in txt:
        txt = txt.replace(old, new, 1)
        print('Fixed: {}'.format(old[:45]))

# ── 2. Missing folio content blocks ─────────────────────────────────────────
F1V = """FOLIO 1V — 1 Corinthians 1:20-22

v.1      GAP:
v.2      του αιωνος το[υτου]
v.3      ουχι εμωραν[εν] [ο] {θς}
v.4      την σοφιαν το[υ] [κοσ]—
v.5      μου τουτου ε[πειδη]
v.6      γαρ εν τη σοφ[ια] [του]
v.7      {θυ} ουκ εγνω [ο] [κοσμος]
v.8      δια της σοφι[ας] [τον]
v.9      {θν} ηυδοκη[σεν] [ο] {θς} [δια]
v.10     της μωριας [του] [κη]—
v.11     ρυγματος σ[ωσαι] [τους]
v.12     πιστευοντα[ς] [επει]—
v.13     δη και ιουδα[ιοι] [ση]—
v.14     [μεια] αιτουσ[ιν] [και]

"""

F4V = """FOLIO 4V — 1 Corinthians 2:11-12

v.1      GAP:
v.2      μη [το] {πνα} [του] {ανου} [το]
v.3      εν [αυτω] [ουτως] [και]
v.4      τα [του] {θυ} [ουδεις] [εγνω]—
v.5      κε[ν] [ει] [μη] [το] {πνα} [του]
v.6      {θυ} [ημεις] [δε] [ου] [το] {πνα}
v.7      το[υ] [κοσμου] [ελαβομεν]

"""

F6R = """FOLIO 6R — 1 Corinthians 3:2-3

r.1      GAP:
r.2      σθε αλλ ου[δε] [ετι] [νυν]
r.3      δυνασθαι ετ[ι] [γαρ] [σαρ]—
r.4      κικοι εστε οπ[ου] [γαρ]
r.5      εν υμιν ζηλος [και] [ε]—
r.6      ρις ουχι σαρκ[ικοι]

"""

# Insert F1V between F1R and F2R
txt = txt.replace(
    'FOLIO 2R — 1 Corinthians 1:25-27',
    F1V + 'FOLIO 2R — 1 Corinthians 1:25-27', 1)
print('Inserted F1V')

# Insert F4V between F4R and F5R
txt = txt.replace(
    'FOLIO 5R — 1 Corinthians 2:14',
    F4V + 'FOLIO 5R — 1 Corinthians 2:14', 1)
print('Inserted F4V')

# Insert F6R between F6V... wait, F6R comes BEFORE F6V in canonical order.
# Current order: 6V then nothing before it. F6R should be between 5V and 6V.
txt = txt.replace(
    'FOLIO 6V — 1 Corinthians 3:5-6',
    F6R + 'FOLIO 6V — 1 Corinthians 3:5-6', 1)
print('Inserted F6R')

# ── 3. Replace translation placeholder with full translation ─────────────────
TRANSLATION = """[TRANSLATION]
1:17   For Christ did not send me to baptize but to preach the gospel, and not with words of eloquent wisdom, lest the cross of Christ be emptied of its power.
1:18   For the word of the cross is folly to those who are perishing, but to us who are being saved it is the power of God.
1:19   For it is written, "I will destroy the wisdom of the wise, and the discernment of the discerning I will thwart."
1:20   Where is the one who is wise? Where is the scribe? Where is the debater of this age? Has not God made foolish the wisdom of the world?
1:21   For since, in the wisdom of God, the world did not know God through wisdom, it pleased God through the folly of what we preach to save those who believe.
1:22   For Jews demand signs and Greeks seek wisdom,
1:25   For the foolishness of God is wiser than men, and the weakness of God is stronger than men.
1:26   For consider your calling, brothers: not many of you were wise according to worldly standards, not many were powerful, not many were of noble birth.
1:27   But God chose what is foolish in the world to shame the wise; God chose what is weak in the world to shame the strong;
2:6    Yet among the mature we do impart wisdom, although it is not a wisdom of this age or of the rulers of this age, who are doomed to pass away.
2:7    But we impart a secret and hidden wisdom of God, which God decreed before the ages for our glory.
2:8    None of the rulers of this age understood this, for if they had, they would not have crucified the Lord of glory.
2:9    But, as it is written, "What no eye has seen, nor ear heard, nor the heart of man imagined, what God has prepared for those who love him" —
2:10   these things God has revealed to us through the Spirit. For the Spirit searches everything, even the depths of God.
2:11   For who knows a person's thoughts except the spirit of that person, which is in him? So also no one comprehends the thoughts of God except the Spirit of God.
2:12   Now we have received not the spirit of the world, but the Spirit who is from God, that we might understand the things freely given us by God.
2:14   The natural person does not accept the things of the Spirit of God, for they are folly to him, and he is not able to understand them because they are spiritually discerned.
3:1    But I, brothers, could not address you as spiritual people, but as people of the flesh, as infants in Christ.
3:2    I fed you with milk, not solid food, for you were not ready for it. And even now you are not yet ready,
3:3    for you are still of the flesh. For while there is jealousy and strife among you, are you not of the flesh and behaving only in a human way?
3:5    What then is Apollos? What is Paul? Servants through whom you believed, as the Lord assigned to each.
3:6    I planted, Apollos watered, but God gave the growth.
3:8    He who plants and he who waters are one, and each will receive his wages according to his labor.
3:9    For we are God's fellow workers. You are God's field, God's building.
3:10   According to the grace of God given to me, like a skilled master builder I laid a foundation, and someone else is building upon it.
3:20   The Lord knows the thoughts of the wise, that they are futile.
4:3    But with me it is a very small thing that I should be judged by you or by any human court. In fact, I do not even judge myself.
4:4    For I am not aware of anything against myself, but I am not thereby acquitted. It is the Lord who judges me.
4:5    Therefore do not pronounce judgment before the time, before the Lord comes, who will bring to light the things now hidden in darkness and will disclose the purposes of the heart.
4:6    I have applied all these things to myself and Apollos for your benefit, brothers, that you may learn by us not to go beyond what is written, that none of you may be puffed up in favor of one against another.
4:7    For who sees anything different in you? What do you have that you did not receive? If then you received it, why do you boast as if you did not receive it?
4:8    Already you have all you want! Already you have become rich! Without us you have become kings!
4:9    For I think that God has exhibited us apostles as last of all, like men sentenced to death, because we have become a spectacle to the world, to angels, and to men.
4:10   We are fools for Christ's sake, but you are wise in Christ. We are weak, but you are strong. You are held in honor, but we in disrepute.
4:12   and we labor, working with our own hands. When reviled, we bless; when persecuted, we endure;
4:13   when slandered, we entreat. We have become, and are still, like the scum of the world, the refuse of all things.
4:14   I do not write these things to make you ashamed, but to admonish you as my beloved children.
4:15   For though you have countless guides in Christ, you do not have many fathers. For I became your father in Christ Jesus through the gospel.
4:16   I urge you, then, be imitators of me.
4:17   That is why I sent you Timothy, my beloved and faithful child in the Lord, to remind you of my ways in Christ, as I teach them everywhere in every church.
4:18   Now some are arrogant, as though I were not coming to you.
4:19   But I will come to you soon, if the Lord wills, and I will find out not the talk of these arrogant people but their power.
4:20   For the kingdom of God does not consist in talk but in power.
4:21   What do you wish? Shall I come to you with a rod, or with love in a spirit of gentleness?
5:1    It is actually reported that there is sexual immorality among you, and of a kind that is not tolerated even among pagans, for a man has his father's wife.
5:2    And you are arrogant! Ought you not rather to mourn? Let him who has done this be removed from among you.
5:3    For though absent in body, I am present in spirit; and as if present, I have already pronounced judgment on the one who did such a thing.
5:4    When you are assembled in the name of the Lord Jesus and my spirit is present, with the power of our Lord Jesus,
5:5    you are to deliver this man to Satan for the destruction of the flesh, so that his spirit may be saved in the day of the Lord.
5:7    Cleanse out the old leaven that you may be a new lump, as you really are unleavened. For Christ, our Passover lamb, has been sacrificed.
5:8    Let us therefore celebrate the festival, not with the old leaven, the leaven of malice and evil, but with the unleavened bread of sincerity and truth.
6:5    I say this to your shame. Can it be that there is no one among you wise enough to settle a dispute between the brothers,
6:6    but brother goes to law against brother, and that before unbelievers?
6:7    To have lawsuits at all with one another is already a defeat for you. Why not rather suffer wrong? Why not rather be defrauded?
6:11   And such were some of you. But you were washed, you were sanctified, you were justified in the name of the Lord Jesus Christ and by the Spirit of our God.
6:12   "All things are lawful for me," but not all things are helpful. "All things are lawful for me," but I will not be dominated by anything.
6:13   "Food is meant for the stomach and the stomach for food" — and God will destroy both one and the other. The body is not meant for sexual immorality, but for the Lord, and the Lord for the body.
6:14   And God raised the Lord and will also raise us up by his power.
6:15   Do you not know that your bodies are members of Christ? Shall I then take the members of Christ and make them members of a prostitute? Never!
6:16   Or do you not know that he who is joined to a prostitute becomes one body with her? For, as it is written, "The two will become one flesh."
6:17   But he who is joined to the Lord becomes one spirit with him.
6:18   Flee from sexual immorality. Every other sin a person commits is outside the body, but the sexually immoral person sins against his own body.
7:3    The husband should give to his wife her conjugal rights, and likewise the wife to her husband.
7:4    For the wife does not have authority over her own body, but the husband does. Likewise the husband does not have authority over his own body, but the wife does.
7:5    Do not deprive one another, except perhaps by agreement for a limited time, that you may devote yourselves to prayer; but then come together again, so that Satan may not tempt you because of your lack of self-control.
7:6    Now as a concession, not a command, I say this.
7:10   To the married I give this charge (not I, but the Lord): the wife should not separate from her husband
7:11   (but if she does, she should remain unmarried or else be reconciled to her husband), and the husband should not divorce his wife.
7:12   To the rest I say (I, not the Lord) that if any brother has a wife who is an unbeliever, and she consents to live with him, he should not divorce her.
7:13   If any woman has a husband who is an unbeliever, and he consents to live with her, she should not divorce him.
7:14   For the unbelieving husband is made holy because of his wife, and the unbelieving wife is made holy because of her husband.
"""

# Replace the placeholder translation comment
old_trans = """# ── TRANSLATION (optional) ──────────────────────────────────
# Uncomment and fill in to show an English translation in the popup.
# Format:  verse_ref   English text
#
# [TRANSLATION]
# 1:1   The book of the genealogy of ..."""

if old_trans in txt:
    txt = txt.replace(old_trans, TRANSLATION.strip(), 1)
    print('Added full translation section')
else:
    # If translation placeholder isn't there, append at end
    txt = txt.rstrip() + '\n\n' + TRANSLATION.strip() + '\n'
    print('Appended translation section')

with open(path, 'w', encoding='utf-8') as f:
    f.write(txt)
print('Done — P11.txt finalized.')

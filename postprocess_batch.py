"""
Post-process all 11 newly imported manuscripts:
  1. Replace FOLIO ? labels with numbered 1R/1V/2R/2V etc.
  2. Fix v.N → r.N for recto folios
  3. Fix duplicate verse refs (e.g. 4:12-12 → 4:12)
  4. Split multi-book [GREEK] into [GREEK:Book] sections (P92, P30)
  5. Add [TRANSLATION] sections
"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

MANUSCRIPTS_DIR = r'C:\ManuscriptDB\manuscripts'

OLD_TRANS = ('# ── TRANSLATION (optional) ──────────────────────────────────\n'
             '# Uncomment and fill in to show an English translation in the popup.\n'
             '# Format:  verse_ref   English text\n'
             '#\n'
             '# [TRANSLATION]\n'
             '# 1:1   The book of the genealogy of ...')


def fix_folio_labels_and_prefixes(txt, page_count):
    """Replace FOLIO ? blocks with numbered 1R/1V/2R/2V...
       Also fix v. → r. for recto folios.
    """
    # Find all FOLIO ? headers in order
    folio_pattern = re.compile(r'^(FOLIO \? — .+)$', re.MULTILINE)
    headers = folio_pattern.findall(txt)

    for i, header in enumerate(headers):
        folio_num = (i // 2) + 1
        is_recto = (i % 2 == 0)
        suffix = 'R' if is_recto else 'V'
        # Extract verse part
        verse_part = header.replace('FOLIO ? — ', '')
        new_header = f'FOLIO {folio_num}{suffix} — {verse_part}'
        txt = txt.replace(header, new_header, 1)

    # Fix duplicate verse refs: e.g. "4:12-12" → "4:12"
    txt = re.sub(r'(\d+:\d+)-\1\b', r'\1', txt)
    # Also "4:12-12" where just verse repeats:  (\d+):(\d+)-\2
    txt = re.sub(r'(\d+):(\d+)-\2\b', r'\1:\2', txt)

    # Fix v. → r. for recto folios
    # For each FOLIO NR block, replace v.N with r.N within that block
    def fix_recto_block(m):
        block = m.group(0)
        block = re.sub(r'^v\.(\d+)', r'r.\1', block, flags=re.MULTILINE)
        return block

    # Match each recto folio block (from FOLIO NR to next FOLIO or end)
    txt = re.sub(
        r'^(FOLIO \d+R — .+?)(?=^FOLIO |\Z)',
        fix_recto_block,
        txt, flags=re.MULTILINE | re.DOTALL
    )

    return txt


def split_multibook(txt, split_at_folio, book1, book2):
    """Split [GREEK] into [GREEK:book1] and [GREEK:book2].
       split_at_folio: the FOLIO label where book2 starts (e.g. 'FOLIO 2R')
    """
    # Find the position of split_at_folio
    split_marker = f'\n{split_at_folio}'
    if split_marker not in txt:
        return txt  # Can't split, leave as-is

    greek_pos = txt.index('[GREEK]\n')
    split_pos = txt.index(split_marker)

    # Replace [GREEK] with [GREEK:book1]
    txt = txt[:greek_pos] + f'[GREEK:{book1}]' + txt[greek_pos+7:]

    # Recalculate split_pos after replacement
    split_pos = txt.index(split_marker)
    # Insert [GREEK:book2] just before the split folio
    txt = txt[:split_pos+1] + f'[GREEK:{book2}]\n\n' + txt[split_pos+1:]

    return txt


def write_file(path, txt):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(txt)
    print(f'  Written: {path}')


def process(fname, page_count, translation, split=None):
    path = f'{MANUSCRIPTS_DIR}\\{fname}.txt'
    with open(path, encoding='utf-8') as f:
        txt = f.read()

    txt = fix_folio_labels_and_prefixes(txt, page_count)

    if split:
        txt = split_multibook(txt, split['at'], split['book1'], split['book2'])

    # Replace translation placeholder
    if OLD_TRANS in txt:
        txt = txt.replace(OLD_TRANS, translation.strip())
    else:
        txt = txt.rstrip() + '\n\n' + translation.strip() + '\n'

    write_file(path, txt)


# ─── P51  Galatians 1:2-10, 13, 16-20 ────────────────────────────────────────
process('P51', 2, """[TRANSLATION]
1:2    and all the brothers who are with me, To the churches of Galatia:
1:3    Grace to you and peace from God our Father and the Lord Jesus Christ,
1:4    who gave himself for our sins to deliver us from the present evil age, according to the will of our God and Father,
1:5    to whom be the glory forever and ever. Amen.
1:6    I am astonished that you are so quickly deserting him who called you in the grace of Christ and are turning to a different gospel —
1:7    not that there is another one, but there are some who trouble you and want to distort the gospel of Christ.
1:8    But even if we or an angel from heaven should preach to you a gospel contrary to the one we preached to you, let him be accursed.
1:9    As we have said before, so now I say again: If anyone is preaching to you a gospel contrary to the one you received, let him be accursed.
1:10   For am I now seeking the approval of man, or of God? Or am I trying to please man? If I were still trying to please man, I would not be a servant of Christ.
1:13   For you have heard of my former life in Judaism, how I persecuted the church of God violently and tried to destroy it.
1:16   he was pleased to reveal his Son to me, in order that I might preach him among the Gentiles, I did not immediately consult with anyone;
1:17   nor did I go up to Jerusalem to those who were apostles before me, but I went away into Arabia, and returned again to Damascus.
1:18   Then after three years I went up to Jerusalem to visit Cephas and remained with him fifteen days.
1:19   But I saw none of the other apostles except James the Lord's brother.
1:20   (In what I am writing to you, before God, I do not lie!)
""")

# ─── P49  Ephesians 4:16-5:13 ─────────────────────────────────────────────────
process('P49', 2, """[TRANSLATION]
4:16   from whom the whole body, joined and held together by every joint with which it is equipped, when each part is working properly, makes the body grow so that it builds itself up in love.
4:17   Now this I say and testify in the Lord, that you must no longer walk as the Gentiles do, in the futility of their minds.
4:18   They are darkened in their understanding, alienated from the life of God because of the ignorance that is in them, due to their hardness of heart.
4:19   They have become callous and have given themselves up to sensuality, greedy to practice every kind of impurity.
4:20   But that is not the way you learned Christ! —
4:21   assuming that you have heard about him and were taught in him, as the truth is in Jesus,
4:22   to put off your old self, which belongs to your former manner of life and is corrupt through deceitful desires,
4:23   and to be renewed in the spirit of your minds,
4:24   and to put on the new self, created after the likeness of God in true righteousness and holiness.
4:25   Therefore, having put away falsehood, let each one of you speak the truth with his neighbor, for we are members one of another.
4:26   Be angry and do not sin; do not let the sun go down on your anger,
4:27   and give no opportunity to the devil.
4:28   Let the thief no longer steal, but rather let him labor, doing honest work with his own hands, so that he may have something to share with anyone in need.
4:29   Let no corrupting talk come out of your mouths, but only such as is good for building up, as fits the occasion, that it may give grace to those who hear.
4:31   Let all bitterness and wrath and anger and clamor and slander be put away from you, along with all malice.
4:32   Be kind to one another, tenderhearted, forgiving one another, as God in Christ forgave you.
5:1    Therefore be imitators of God, as beloved children.
5:2    And walk in love, as Christ loved us and gave himself up for us, a fragrant offering and sacrifice to God.
5:3    But sexual immorality and all impurity or covetousness must not even be named among you, as is proper among saints.
5:4    Let there be no filthiness nor foolish talk nor crude joking, which are out of place, but instead let there be thanksgiving.
5:5    For you may be sure of this, that everyone who is sexually immoral or impure, or who is covetous (that is, an idolater), has no inheritance in the kingdom of Christ and God.
5:6    Let no one deceive you with empty words, for because of these things the wrath of God comes upon the sons of disobedience.
5:7    Therefore do not become partners with them;
5:8    for at one time you were darkness, but now you are light in the Lord. Walk as children of light
5:9    (for the fruit of light is found in all that is good and right and true),
5:10   and try to discern what is pleasing to the Lord.
5:11   Take no part in the unfruitful works of darkness, but instead expose them.
5:12   For it is shameful even to speak of the things that they do in secret.
5:13   But when anything is exposed by the light, it becomes visible,
""")

# ─── P92  Ephesians + 2 Thessalonians ─────────────────────────────────────────
process('P92', 4,
    split={'at': 'FOLIO 2R', 'book1': 'Ephesians', 'book2': '2 Thessalonians'},
    translation="""[TRANSLATION:Ephesians]
1:11   In him we have obtained an inheritance, having been predestined according to the purpose of him who works all things according to the counsel of his will,
1:12   so that we who were the first to hope in Christ might be to the praise of his glory.
1:13   In him you also, when you heard the word of truth, the gospel of your salvation, and believed in him, were sealed with the promised Holy Spirit,
1:19   and what is the immeasurable greatness of his power toward us who believe, according to the working of his great might
1:20   that he worked in Christ when he raised him from the dead and seated him at his right hand in the heavenly places,
1:21   far above all rule and authority and power and dominion, and above every name that is named, not only in this age but also in the one to come.

[TRANSLATION:2 Thessalonians]
1:4    Therefore we ourselves boast about you in the churches of God for your steadfastness and faith in all your persecutions and in the afflictions that you are enduring.
1:5    This is evidence of the righteous judgment of God, that you may be considered worthy of the kingdom of God, for which you are also suffering —
1:11   To this end we always pray for you, that our God may make you worthy of his calling and may fulfill every resolve for good and every work of faith by his power,
1:12   so that the name of our Lord Jesus may be glorified in you, and you in him, according to the grace of our God and the Lord Jesus Christ.
""")

# ─── P132  Ephesians 3:21-4:2, 14-16 ─────────────────────────────────────────
process('P132', 2, """[TRANSLATION]
3:21   to him be glory in the church and in Christ Jesus throughout all generations, forever and ever. Amen.
4:1    I therefore, a prisoner for the Lord, urge you to walk in a manner worthy of the calling to which you have been called,
4:2    with all humility and gentleness, with patience, bearing with one another in love,
4:14   so that we may no longer be children, tossed to and fro by the waves and carried about by every wind of doctrine, by human cunning, by craftiness in deceitful schemes.
4:15   Rather, speaking the truth in love, we are to grow up in every way into him who is the head, into Christ,
4:16   from whom the whole body, joined and held together by every joint with which it is equipped, when each part is working properly, makes the body grow so that it builds itself up in love.
""")

# ─── P16  Philippians 3:10-17; 4:2-8 ─────────────────────────────────────────
process('P16', 2, """[TRANSLATION]
3:10   that I may know him and the power of his resurrection, and may share his sufferings, becoming like him in his death,
3:11   that by any means possible I may attain the resurrection from the dead.
3:12   Not that I have already obtained this or am already perfect, but I press on to make it my own, because Christ Jesus has made me his own.
3:13   Brothers, I do not consider that I have made it my own. But one thing I do: forgetting what lies behind and straining forward to what lies ahead,
3:14   I press on toward the goal for the prize of the upward call of God in Christ Jesus.
3:15   Let those of us who are mature think this way, and if in anything you think otherwise, God will reveal that also to you.
3:16   Only let us hold true to what we have attained.
3:17   Brothers, join in imitating me, and keep your eyes on those who walk according to the example you have in us.
4:2    I entreat Euodia and I entreat Syntyche to agree in the Lord.
4:3    Yes, I ask you also, true companion, help these women, who have labored side by side with me in the gospel together with Clement and the rest of my fellow workers, whose names are in the book of life.
4:4    Rejoice in the Lord always; again I will say, rejoice.
4:5    Let your reasonableness be known to everyone. The Lord is at hand;
4:6    do not be anxious about anything, but in everything by prayer and supplication with thanksgiving let your requests be made known to God.
4:7    And the peace of God, which surpasses all understanding, will guard your hearts and your minds in Christ Jesus.
4:8    Finally, brothers, whatever is true, whatever is honorable, whatever is just, whatever is pure, whatever is lovely, whatever is commendable, if there is any excellence, if there is anything worthy of praise, think about these things.
""")

# ─── P30  1 Thessalonians + 2 Thessalonians ───────────────────────────────────
process('P30', 8,
    split={'at': 'FOLIO 4V', 'book1': '1 Thessalonians', 'book2': '2 Thessalonians'},
    translation="""[TRANSLATION:1 Thessalonians]
4:12   so that you may walk properly before outsiders and be dependent on no one.
4:13   But we do not want you to be uninformed, brothers, about those who are asleep, that you may not grieve as others do who have no hope.
4:16   For the Lord himself will descend from heaven with a cry of command, with the voice of an archangel, and with the sound of the trumpet of God. And the dead in Christ will rise first.
4:17   Then we who are alive, who are left, will be caught up together with them in the clouds to meet the Lord in the air, and so we will always be with the Lord.
5:2    For you yourselves are fully aware that the day of the Lord will come like a thief in the night.
5:3    While people are saying, "There is peace and security," then sudden destruction will come upon them as labor pains come upon a pregnant woman, and they will not escape.
5:8    But since we belong to the day, let us be sober, having put on the breastplate of faith and love, and for a helmet the hope of salvation.
5:9    For God has not destined us for wrath, but to obtain salvation through our Lord Jesus Christ,
5:10   who died for us so that whether we are awake or asleep we might live with him.
5:12   We ask you, brothers, to respect those who labor among you and are over you in the Lord and admonish you,
5:13   and to esteem them very highly in love because of their work. Be at peace among yourselves.
5:14   And we urge you, brothers, admonish the idle, encourage the fainthearted, help the weak, be patient with them all.
5:15   See that no one repays anyone evil for evil, but always seek to do good to one another and to everyone.
5:16   Rejoice always,
5:17   pray without ceasing,
5:18   give thanks in all circumstances; for this is the will of God in Christ Jesus for you.
5:25   Brothers, pray for us.
5:26   Greet all the brothers with a holy kiss.
5:27   I put you under oath before the Lord to have this letter read to all the brothers.
5:28   The grace of our Lord Jesus Christ be with you.

[TRANSLATION:2 Thessalonians]
1:1    Paul, Silvanus, and Timothy, To the church of the Thessalonians in God our Father and the Lord Jesus Christ:
1:2    Grace to you and peace from God our Father and the Lord Jesus Christ.
""")

# ─── P65  1 Thessalonians 1:3-2:13 ───────────────────────────────────────────
process('P65', 2, """[TRANSLATION]
1:3    remembering before our God and Father your work of faith and labor of love and steadfastness of hope in our Lord Jesus Christ.
1:4    For we know, brothers loved by God, that he has chosen you,
1:5    because our gospel came to you not only in word, but also in power and in the Holy Spirit and with full conviction. You know what kind of men we proved to be among you for your sake.
1:6    And you became imitators of us and of the Lord, for you received the word in much affliction, with the joy of the Holy Spirit,
1:7    so that you became an example to all the believers in Macedonia and in Achaia.
1:8    For not only has the word of the Lord sounded forth from you in Macedonia and Achaia, but your faith in God has gone forth everywhere, so that we need not say anything.
1:9    For they themselves report concerning us the kind of reception we had among you, and how you turned to God from idols to serve the living and true God,
1:10   and to wait for his Son from heaven, whom he raised from the dead, Jesus who delivers us from the wrath to come.
2:1    For you yourselves know, brothers, that our coming to you was not in vain.
2:6    Nor did we seek glory from people, whether from you or from others, though we could have made demands as apostles of Christ.
2:7    But we were gentle among you, like a nursing mother taking care of her own children.
2:8    So, being affectionately desirous of you, we were ready to share with you not only the gospel of God but also our own selves, because you had become very dear to us.
2:9    For you remember, brothers, our labor and toil: we worked night and day, that we might not be a burden to any of you, while we proclaimed to you the gospel of God.
2:10   You are witnesses, and God also, how holy and righteous and blameless was our conduct toward you believers.
2:11   For you know how, like a father with his children,
2:12   we exhorted each one of you and encouraged you and charged you to walk in a manner worthy of God, who calls you into his own kingdom and glory.
2:13   And we also thank God constantly for this, that when you received the word of God, which you heard from us, you accepted it not as the word of men but as what it really is, the word of God, which is at work in you believers.
""")

# ─── P133  1 Timothy 3:13-4:8 ─────────────────────────────────────────────────
process('P133', 2, """[TRANSLATION]
3:13   For those who serve well as deacons gain a good standing for themselves and also great confidence in the faith that is in Christ Jesus.
3:14   I hope to come to you soon, but I am writing these things to you so that,
3:15   if I delay, you may know how one ought to behave in the household of God, which is the church of the living God, a pillar and buttress of the truth.
3:16   Great indeed, we confess, is the mystery of godliness: He was manifested in the flesh, vindicated by the Spirit, seen by angels, proclaimed among the nations, believed on in the world, taken up in glory.
4:1    Now the Spirit expressly says that in later times some will depart from the faith by devoting themselves to deceitful spirits and teachings of demons,
4:2    through the insincerity of liars whose consciences are seared,
4:3    who forbid marriage and require abstinence from foods that God created to be received with thanksgiving by those who believe and know the truth.
4:4    For everything created by God is good, and nothing is to be rejected if it is received with thanksgiving,
4:5    for it is made holy by the word of God and prayer.
4:6    If you put these things before the brothers, you will be a good servant of Christ Jesus, being trained in the words of the faith and of the good doctrine that you have followed.
4:7    Have nothing to do with irreverent, silly myths. Rather train yourself for godliness;
4:8    for while bodily training is of some value, godliness is of value in every way, as it holds promise for the present life and also for the life to come.
""")

# ─── P32  Titus 1:11-15; 2:3-8 ───────────────────────────────────────────────
process('P32', 2, """[TRANSLATION]
1:11   They must be silenced, since they are upsetting whole families by teaching for shameful gain what they ought not to teach.
1:12   One of the Cretans, a prophet of their own, said, "Cretans are always liars, evil beasts, lazy gluttons."
1:13   This testimony is true. Therefore rebuke them sharply, that they may be sound in the faith,
1:14   not devoting themselves to Jewish myths and the commands of people who turn away from the truth.
1:15   To the pure, all things are pure, but to the defiled and unbelieving, nothing is pure; but both their minds and their consciences are defiled.
2:3    Older women likewise are to be reverent in behavior, not slanderers or slaves to much wine. They are to teach what is good,
2:4    and so train the young women to love their husbands and children,
2:5    to be self-controlled, pure, working at home, kind, and submissive to their own husbands, that the word of God may not be reviled.
2:6    Likewise, urge the younger men to be self-controlled.
2:7    Show yourself in all respects to be a model of good works, and in your teaching show integrity, dignity,
2:8    and sound speech that cannot be condemned, so that an opponent may be put to shame, having nothing evil to say about us.
""")

# ─── P87  Philemon 13-15, 24-25 ───────────────────────────────────────────────
process('P87', 2, """[TRANSLATION]
1:13   I would have been glad to keep him with me, in order that he might serve me on your behalf during my imprisonment for the gospel,
1:14   but I preferred to do nothing without your consent in order that your goodness might not be by compulsion but of your own accord.
1:15   For this perhaps is why he was parted from you for a while, that you might have him back forever,
1:24   Mark, Aristarchus, Demas, and Luke, my fellow workers, greet you.
1:25   The grace of the Lord Jesus Christ be with your spirit.
""")

# ─── P139  Philemon 1:6-8, 18-20 ─────────────────────────────────────────────
process('P139', 2, """[TRANSLATION]
1:6    and I pray that the sharing of your faith may become effective for the full knowledge of every good thing that is in us for the sake of Christ.
1:7    For I have derived much joy and comfort from your love, my brother, because the hearts of the saints have been refreshed through you.
1:8    Accordingly, though I am bold enough in Christ to command you to do what is required,
1:18   If he has wronged you at all, or owes you anything, charge that to my account.
1:19   I, Paul, write this with my own hand: I will repay it — to say nothing of your owing me even your own self.
1:20   Yes, brother, I want some benefit from you in the Lord. Refresh my heart in Christ.
""")

print("\n=== ALL POST-PROCESSING DONE ===")

#!/usr/bin/env python3
"""Build BGU 4.1141 — long apologetic letter of a freedman to his patron."""
import json, re, sys
sys.path.insert(0, '.')
from _clean import clean

def polish(line):
    l = re.sub(r'\(perpendicular\)\s*', '', line)
    l = re.sub(r'\d*,ms(up)?\b', '', l)
    l = l.replace('⁦ vac. ? ⁩', ' ').replace('vac.', ' ')
    return re.sub(r'\s+', ' ', l).strip()

DATA = json.load(open('_PENDING_bgu4_1100-1150.json', encoding='utf-8'))

ITEMS = [
 dict(key='bgu;4;1141', nlines=62, slug='bgu_4_1141',
      name='Letter — a freedman defends himself to his patron',
      date='14–13 BCE', found='Alexandria, Egypt', lat=31.2, lon=29.9,
      content='A freedman, stung by his patron’s reproaches over an estate, defends his loyalty in raw emotional Greek and reports the affair of the purple cloth and the rings',
      trans=[
        "To Erosis(?), very many gree(tings). I received from Ph[i]lox[enos] [yo]ur letter,",
        "only it (and)",
        "… we have been at odds since … . Wherefore also [with]",
        "much [j]oy I detained them […] … and these (men),",
        "and to do the necessary things …",
        "is treated humanely. You sent, then, both Ph[ilóxe]nos and Hilaros, to find out",
        "as to what I wrote you, whether it is so or not. You seem to have lost your wits, since you compel me, fool that I am, to write to you —",
        "(but) I will no longer write you anything, [so that] you may understand that in my first",
        "letter there is no fault; for I am not doing the work of an in-",
        "former, nor do I think you hold me in an informer’s place. So I ask",
        "you and entreat you and adjure you by the Fortune of Caesar — and [thu]s may I",
        "see you free — that you laid the letter aside in anger. Ask those",
        "you have sent, item by item, and I have given true proofs.",
        "You are absurd, writing that, if Eros satisfies you, I should write you; and by writ-",
        "ing to him to insult me, you wrote this to mock me. As for me, I do not",
        "think I deserve to be insulted,",
        "for I have done you no wrong, nor will it appear to your friends that I am insulted, satisfying",
        "you while you",
        "satisfy me. For I trust in myself:",
        "since I became your friend, I left no room (for blame). One thing you will charge me with,",
        "if you both confer honor on me and want me to be a man …",
        "and recommended me both to fellow-slaves and to fellow-freedmen — which to me",
        "is wealth, in your eyes — yet I insult the now-rich, beside your",
        "fellow-slave and fellow-freedman.",
        "For I did not become your friend in order to snatch anything away; rather your",
        "own soul knows that, just as a slave on the eve of freedom wishes to please, so",
        "I too, wishing your friendship blameless, kept myself so.",
        "For what an outrage he did me in the garden and in",
        "the house of Terentius, with Priamos and Philoxenos and Hilaros present — were it (possible) to write you tears,",
        "I would have written you out of my tears, and …(?)",
        "our walk(?) from the garden. About these things those you have sent will make clear,",
        "if only they are not willing to do a favor to a fellow-slave.",
        "And about Xystos you write me that he is in poor health outside; whether the fellow-slave",
        "can recommend him, I do not know, for I do not sleep",
        "inside to know. On the days when I go up, I find him sitting",
        "and stuffing himself with woof-thread(?); and each day I question the door-keeper",
        "whether anyone has slept outside, and the man of the house never once (told) me",
        "that anyone had dined outside. But learning that Xystos had dined inside",
        "in the house with Eros, twice I took him into the house with me and",
        "gave him instructions that there be nothing between him and that man — being cautious,",
        "because I had learned beforehand about the little rings that Eros made,",
        "lest he persuade him to disclose something in the handling. And about",
        "the shadow-cloth(?) it became clear to me, when I investigated with Philoxenos and Hilaros, that the pur-",
        "ple had been",
        "exchanged by Diodoros and not given to you — against which he showed you",
        "a sample — because the old man who was hiding the shadow-cloth, when ques-",
        "tioned by me, said it had been exchanged … said to him: “Why from the start did you not disclose these things, so that",
        "you too might be treated kindly?” He said: “Diodoros had promised me",
        "the kindness,” who neither paid me my wages nor the kindness;",
        "wherefore necessity compelled me to inform.” So, having put him to the test,",
        "I questioned him privately, unknown to Xystos,",
        "wishing to learn whether Xystos too",
        "was privy to it; the old man said he knew nothing at all about these matters.",
        "And I said to him: “You must also give a written bond that Xystos was not privy",
        "to these things,” who first … him to give a written bond by the cubit-rule …",
        "… Diodoros, because …",
        "who urges me to await the …",
        "to him Diodoros, because he had not given …",
        "to him being … (in office?)",
        "I am in health …(?) being present …",
        "… and to be of use … It seemed good to me, then …",
        "… could … the written [bond] …",
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

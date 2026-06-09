#!/usr/bin/env python3
"""
test_extract_verses.py  —  offline regression test for extract_verses.py

Runs without any network access. Verifies the TEI verse-anchor parser:
  * groups words under the correct <ab n="..."> verse
  * re-joins words split across <lb break="no"/>
  * keeps [reconstructions] and {nomina sacra}
  * marks gaps with …
  * collates / sorts verses by (chapter, verse)

Run:
    python test_extract_verses.py
    # or, if you use pytest:
    pytest test_extract_verses.py
"""

import extract_verses as ev


# A synthetic TEI page exercising every tricky case at once.
SAMPLE_XML = """<?xml version="1.0" encoding="utf-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
 <text><body>
  <ab n="B07K7V19">
   <w>ουδεν</w>
   <w>εστιν</w>
  </ab>
  <ab n="B07K7V18">
   <w>τις</w>
   <lb n="1"/>
   <w>κε<supplied reason="lost">κλη</supplied><lb break="no"/>ται</w>
   <w>μη</w>
   <w><abbr type="nomSac">θυ</abbr></w>
   <gap reason="lacuna" extent="2"/>
  </ab>
 </body></text>
</TEI>"""


def _collated():
    verse_list = ev.parse_page_verses(SAMPLE_XML)
    book_order, by_book = ev.collate([verse_list])
    return book_order, by_book


def test_book_detected():
    book_order, _ = _collated()
    assert book_order == ["1 Corinthians"], book_order


def test_verses_sorted_and_present():
    _, by_book = _collated()
    refs = [(c, v) for (c, v, _t) in by_book["1 Corinthians"]]
    assert refs == [(7, 18), (7, 19)], refs   # sorted even though XML had 19 first


def test_split_word_rejoined_and_markers_kept():
    _, by_book = _collated()
    text = {(c, v): t for (c, v, t) in by_book["1 Corinthians"]}
    # κε + [κλη] (supplied) + ται (continued across break="no") -> one token
    assert text[(7, 18)] == "τις κε[κλη]ται μη {θυ} …", repr(text[(7, 18)])


def test_plain_verse():
    _, by_book = _collated()
    text = {(c, v): t for (c, v, t) in by_book["1 Corinthians"]}
    assert text[(7, 19)] == "ουδεν εστιν", repr(text[(7, 19)])


def test_multibook_section_headers():
    multi = """<?xml version="1.0" encoding="utf-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
 <ab n="B07K16V1"><w>περι</w><w>δε</w></ab>
 <ab n="B08K5V1"><w>οιδαμεν</w><w>γαρ</w></ab>
</body></text></TEI>"""
    verse_list = ev.parse_page_verses(multi)
    book_order, by_book = ev.collate([verse_list])
    assert book_order == ["1 Corinthians", "2 Corinthians"], book_order
    scaffold = ev.build_scaffold("TEST", "Pxx", book_order, by_book)
    assert "[TRANSLATION:1 Corinthians]" in scaffold
    assert "[TRANSLATION:2 Corinthians]" in scaffold


def _run_all():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  [PASS] {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  [FAIL] {t.__name__}: {e}")
    print()
    if failed:
        print(f"{failed}/{len(tests)} tests FAILED ❌")
        return 1
    print(f"All {len(tests)} tests passed ✅")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_run_all())

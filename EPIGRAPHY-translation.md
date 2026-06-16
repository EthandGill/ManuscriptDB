# Epigraphy translation (Phase 2)

Add faithful English translations to the ~2,000 Latin inscriptions already in
`static/epigraphy_data.js`. Same scaffold→fill→assemble protocol as
`WORKFLOW-translation.md`, but the data is already on disk (no Firecrawl, no
NTVMR) — `epigraphy_translate.py` just adds a `translation` field per record.

Unlike the papyri (line-aligned), inscriptions are translated as **free prose per
inscription** — Latin epigraphy is abbreviation-dense and enjambed, so a 1:1
line map is wrong. The safety check on assemble is therefore *id-exists* +
*translation-non-empty*, not a line count.

## The loop

```
# 1. pull the next un-translated batch (resumable: skips records already done)
python epigraphy_translate.py scaffold --batch 150
#    -> writes _epi_translate_<NNN>.txt

# 2. fill it: under each [ENGLISH], translate the Latin shown (expand the
#    standard abbreviations). Leave [ENGLISH] blank to skip a record.

# 3. merge back in (backs up to epigraphy_data.js.bak, prints counts)
python epigraphy_translate.py assemble _epi_translate_<NNN>.txt

# repeat until scaffold reports "Nothing to do"
```

`python epigraphy_translate.py selftest` runs the offline parser check.

## Translation rules

Translate the **actual Latin shown**, expanding standard epigraphic abbreviations
to their full sense in English:

- `D(is) M(anibus)` → "To the Spirits of the Dead"
- `H(ic) s(itus/ita) e(st)` → "Here lies"
- `v(ixit) a(nnos) N` / `vix(it) ann(os) N` → "lived N years" (add months/days:
  `m(enses)`, `d(ies)`)
- `b(ene) m(erenti)` → "to the well-deserving"
- `f(ecit)`, `p(osuit)`, `c(uravit)` → "made / set up / saw to (this)"
- `co(n)s(ul)`, `trib(unicia) pot(estate)`, `imp(erator)`, `p(ater) p(atriae)` →
  spell out the imperial titulature
- `[supplied]` text in brackets is editorially restored — translate it normally;
  `…` / `(vac.)` mark gaps/blanks, render as "…".

Keep it faithful and literal (this is a study tool), not a loose paraphrase. A
fragmentary inscription gets a fragmentary translation. Names stay in Latin
nominative form (Marcus Ulpius Fronto), not anglicised.

## Notes

- Independent of Phase 1 (the reader/title work) — they touch different things and
  can run in parallel. Translations only *display* once Phase 1 wires the reader.
- `_epi_translate_*.txt` and `epigraphy_data.js.bak` are git-ignored.
- After a run: commit and push so the site updates —
  `git add static/epigraphy_data.js && git commit -m "Translate inscriptions <NNN>" && git push`
  (or double-click `update_website.bat`).

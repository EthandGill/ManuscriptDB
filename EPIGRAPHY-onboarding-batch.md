# Onboarding the next 2,000 inscriptions (repeatable batch)

The EDH dump in `data-master/` holds ~71,000 inscriptions; we load them in batches
of 2,000 (best-preserved first). This is the repeatable procedure for each new
batch. It is **additive** — every batch leaves the already-loaded inscriptions
(and their translations, genres, city nodes) untouched.

Tools involved (all offline, no Firecrawl):
- `edh_ingest.py` — parses the dump → `static/epigraphy_data.js`. `--add` appends
  the next best inscriptions that aren't already in the file.
- `reclassify_epigraphy.py` — applies the extra genres (e.g. defixio) by content.
- `epigraphy_city_nodes.py` — gives new findspots a city node + last-mile route
  (see `EPIGRAPHY-city-nodes.md`).
- `epigraphy_translate.py` — the resumable translation loop (see
  `EPIGRAPHY-translation.md`); it only touches records whose `translation` is empty,
  so it automatically translates just the new batch.

## Step 1 — ingest the next 2,000 (additive)

```
py edh_ingest.py data-master --add --cap 2000
```

This keeps every existing record exactly as-is and appends the next 2,000 best
inscriptions not already loaded — each with its text already split into lines
(`text` is a line array), a genre, a citation `title`, coordinates, and an empty
`translation` ready to fill. Expect a line like
`Add mode: 2000 existing + 2000 new = 4000 total`. The record count in
`static/epigraphy_data.js` should jump by exactly 2,000.

## Step 2 — genres for the new records

```
py reclassify_epigraphy.py
```

Re-applies the content-based genres (defixio, etc.) across the whole file so the
new batch is classified like the first. Idempotent.

## Step 3 — city nodes + routes for new findspots

Follow `EPIGRAPHY-city-nodes.md`:

```
python epigraphy_city_nodes.py --report     # lists findspots with no city node
python epigraphy_city_nodes.py --apply      # adds node + last-mile foot/horse leg
```

So none of the new inscriptions is a homeless "This site" orb.

## Step 4 — translate the new batch (resumable)

Per `EPIGRAPHY-translation.md`, run the scaffold → fill → assemble loop until it
reports "Nothing to do". Because it skips records that already have a translation,
it translates only the 2,000 just added:

```
py epigraphy_translate.py scaffold --batch 150     # writes _epi_translate_<NNN>.txt
#   fill each [ENGLISH] from the Latin shown (expand D(is) M(anibus), v(ixit) a(nnos), …)
py epigraphy_translate.py assemble _epi_translate_<NNN>.txt
#   repeat until "Nothing to do"
```

## Step 5 — verify + publish

- `python epigraphy_translate.py scaffold --batch 1` should say "Nothing to do".
- `py app.py`, hard-refresh: ~4,000 inscriptions now, the new ones open in the
  reader with line-split Latin + English, sensible genres, and map orbs with homes.
- Publish: double-click `update_website.bat` (or
  `git add static/epigraphy_data.js static/data/* edh_ingest.py && git commit && git push`).

## Rules

- Run only **one** window editing `static/epigraphy_data.js` at a time (ingest in
  one window, then translate — never both at once) or they clobber each other.
- The translation step needs the model; the ingest/reclassify/city-node steps don't.

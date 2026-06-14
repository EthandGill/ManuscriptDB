# EPIGRAPHY TASK — start here (run this in a SECOND Claude Code window)

This Claude Code task does **only Latin epigraphy**. Another task/window is busy
onboarding papyri manuscripts at the same time, so to stay out of its way:

- **Only touch** `edh_ingest.py` and `static/epigraphy_data.js`.
- **Do NOT** touch `manuscripts/`, `parallel_sweep.py`, `_sweep_*.json`,
  `sweep_ranges*.txt`, or run any scraper — that's the other task's job and it
  spends Firecrawl credits. Epigraphy is free (a downloaded dump), no credits.
- **Git is shared**, so commit only your one file and rebase before pushing
  (steps below) so you don't collide with the manuscripts task's pushes.

Background detail lives in `EPIGRAPHY-plan.md`; this file is the quick, safe
runbook.

## What's already built (no code changes needed)
- `edh_ingest.py` — reads an EDH/LIST dump → `static/epigraphy_data.js`.
- The frontend is already wired to load `epigraphy_data.js` into the epigraphy
  browser (funerary / honourific / public).

## Step 0 — the one manual step (download the dump)
EDH's live site is bot-gated, but the corpus is a free download. **Don't grab the
8 sub-folders one by one** — get everything at once:
- EDH repo: on `github.com/epigraphic-database-heidelberg/data` click green
  **Code → Download ZIP**, unzip into `C:\ManuscriptDB\`. (Its `inscriptions/`
  files are **EpiDoc XML**; `geography/` holds GeoJSON coordinates.)
- OR LIST (EDH + EDCS, one file, text+coords+attributes): `zenodo.org/records/10473706`.

**Format note:** `edh_ingest.py` as written reads GeoJSON / JSON arrays. The EDH
inscriptions are EpiDoc XML and the LIST file may be CSV — so the FIRST job of
this task is to look at what was actually downloaded and, if needed, extend
`edh_ingest.py` to parse that format (an EpiDoc-XML reader joining text to the
`geography/` GeoJSON coords by HD-number, or a CSV reader for LIST). The target
output (`static/epigraphy_data.js` with {id,name,genre,lat,lon,date,language,
text,source}) and the genre rules stay the same.

## Steps 1-4 — run these (zero credits)
```
py edh_ingest.py --inspect edh_inscriptions.geojson
py edh_ingest.py edh_inscriptions.geojson --cap 2000
py app.py        # open the site, confirm the Epigraphy browser fills, then Ctrl+C
git pull --rebase
git add static/epigraphy_data.js
git commit -m "Add Latin epigraphy batch 1 (~2000 EDH inscriptions)"
git push
```
If `--inspect` shows the transcription / type / date / coordinates aren't being
picked up, add the real key names to the `*_KEYS` lists at the top of
`edh_ingest.py`, then re-run step 2.

If `git push` is rejected (the manuscripts task pushed first), just run
`git pull --rebase` then `git push` again.

---

## Kickoff prompt (paste into the epigraphy Claude Code window)

> You are the EPIGRAPHY task. Follow EPIGRAPHY-START.md exactly. Only work with
> edh_ingest.py and static/epigraphy_data.js — do not touch manuscripts/, the
> scrapers, sweep_ranges files, or _sweep_*.json (another task owns those).
> 1. First look at what was downloaded into this folder (a ZIP of the EDH repo,
>    its inscriptions/*.xml EpiDoc files + geography/*.geojson coords, or a LIST
>    CSV/JSON). If it's NOT already a GeoJSON/JSON array that edh_ingest.py can
>    read, extend edh_ingest.py to parse the real format: for EDH EpiDoc XML,
>    read the transcription + type + date from each XML and join coordinates from
>    the geography/ GeoJSON by HD-number; for LIST CSV, read the relevant columns.
>    Keep the same output shape and genre rules. Use --inspect to sanity-check.
> 2. Run edh_ingest.py over the data with --cap 2000 — report the per-genre counts.
> 3. py app.py, verify the Epigraphy browser fills and /api/manuscripts has 0
>    parse errors, then stop the server.
> 4. git pull --rebase ; git add static/epigraphy_data.js ; git commit -m "Add
>    Latin epigraphy batch 1" ; git push. If push is rejected, git pull --rebase
>    and push again.
> Spend no Firecrawl credits — this is all offline. Stop when epigraphy_data.js is
> committed and pushed.

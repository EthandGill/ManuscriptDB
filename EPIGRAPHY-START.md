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
EDH's live site is bot-gated, but the corpus is a free download:
- EDH GeoJSON: `github.com/epigraphic-database-heidelberg/data` → `inscriptions/`, or
- LIST (EDH + EDCS): `zenodo.org/records/10473706`.
Save it into `C:\ManuscriptDB\` as `edh_inscriptions.geojson` (any name is fine;
use it below).

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
> The dump is `edh_inscriptions.geojson` in this folder.
> 1. py edh_ingest.py --inspect edh_inscriptions.geojson — confirm the fields map;
>    if not, add the real keys to the *_KEYS lists in edh_ingest.py.
> 2. py edh_ingest.py edh_inscriptions.geojson --cap 2000 — report the per-genre counts.
> 3. py app.py, verify the Epigraphy browser fills and /api/manuscripts has 0
>    parse errors, then stop the server.
> 4. git pull --rebase ; git add static/epigraphy_data.js ; git commit -m "Add
>    Latin epigraphy batch 1" ; git push. If push is rejected, git pull --rebase
>    and push again.
> Spend no Firecrawl credits — this is all offline. Stop when epigraphy_data.js is
> committed and pushed.

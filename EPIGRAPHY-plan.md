# Epigraphy (CIL / Latin inscriptions) — onboarding plan

## Key decision: this is a free DOWNLOAD, not a Firecrawl scrape

EDH's live site/API is now behind the **Anubis bot-gate** (same as papyri.info),
so per-request fetching is blocked. But the full corpus is published as **bulk
open data** on GitHub and Zenodo — plain downloads, no Anubis, **0 Firecrawl
credits**, CC BY-SA 4.0:

- **EDH GitHub dumps** — `github.com/epigraphic-database-heidelberg/data`,
  `inscriptions/` folder = **GeoJSON** (coords + text + type + dates). ~71k curated
  Latin/bilingual inscriptions with CIL cross-references.
- **LIST dataset (EDH + EDCS aggregated)** — Zenodo `zenodo.org/records/10473706`,
  ~525,870 inscriptions, 65 attributes. Use this if you want EDCS breadth too.

So the "EDH base + EDCS gaps" plan is satisfied by **one free download** — keep the
5,000 credits for papyri. Only fall back to Firecrawl if you later need a specific
inscription neither dump contains.

## Why a download beats scraping here

- No Anubis, no rate limits, no credits.
- The whole corpus at once, refreshed daily.
- Structured fields already (coordinates, date range, inscription type) — they map
  straight onto the app's epigraphy schema, so little cleaning.

## The app side (what already exists)

`static/script.js` has the scaffold: `EPIGRAPHY_GENRES` = funerary / honourific /
public, and `let epigraphy = []` (empty), rendered by `renderEpigraphySection()`.
There is **no backend route and no data yet** — inscriptions just need to be
loaded into that `epigraphy` array. Target schema per item:
`{ id, name, genre, lat, lon, date, language, text, source }`.

## The pipeline to build (next step)

1. **Download** the EDH GeoJSON dump (or the LIST file) into the project once.
2. **`edh_ingest.py`** (no credits, offline): read the dump →
   - keep only records with coordinates **and** a transcription (so they map + read),
   - classify each into funerary / honourific / public from EDH's
     "type of inscription" field (e.g. *titulus sepulcralis* → funerary,
     *titulus honorarius* → honourific, building/dedication/legal → public),
   - **cap the first batch** (the browser loads these into memory — a few thousand
     is fine, 525k is not), preferring records with rich text + good coords,
   - emit `static/epigraphy_data.js` → `window.EPIGRAPHY_DATA = [ ... ]`.
3. **Wire the frontend** (tiny, additive, low-risk):
   - add `<script src="epigraphy_data.js">` before `script.js` in `index.html`,
   - change `let epigraphy = []` → `let epigraphy = window.EPIGRAPHY_DATA || []`.
4. **Verify + deploy**: load locally, confirm the epigraphy browser fills and the
   inscriptions pin on the map, then `update_website.bat`.

## Run it (you do this once — free, no credits)

Built and wired already: `edh_ingest.py`, the `epigraphy_data.js` include in
`index.html`, and `script.js` now reads `window.EPIGRAPHY_DATA`. You just need the
data file:

1. **Download a dump** (either):
   - EDH GeoJSON: browse `github.com/epigraphic-database-heidelberg/data/tree/master/inscriptions`
     and download the inscriptions GeoJSON, OR
   - LIST (EDH+EDCS) from `zenodo.org/records/10473706`.
   Save it into `C:\ManuscriptDB\` (e.g. `edh_inscriptions.geojson`).
2. **Confirm the fields** (schema varies):
   ```
   python edh_ingest.py --inspect edh_inscriptions.geojson
   ```
   If a target field looks empty later, add its real key to the `*_KEYS` lists at
   the top of `edh_ingest.py`.
3. **Build the batch** (~2,000 best-preserved, all provinces):
   ```
   python edh_ingest.py edh_inscriptions.geojson --cap 2000
   ```
   Writes `static/epigraphy_data.js`.
4. **Verify + publish**: `python app.py`, open the site, confirm the Epigraphy
   browser fills (funerary / honourific / public). Then `update_website.bat`.

`epigraphy_data.js` is a generated data file — keep it committed (unlike the
scratch `_sweep_*.json`), since the live site loads it.

## Drop-in Claude Code prompt (paste after the dump is downloaded)

Once you've saved the EDH/LIST dump into `C:\ManuscriptDB\` (e.g.
`edh_inscriptions.geojson`), paste this into Claude Code (Shift+Tab for
auto-accept first):

> Onboard the first batch of Latin epigraphy per EPIGRAPHY-plan.md, using the
> dump file `edh_inscriptions.geojson` in this folder.
> 1. Run `python edh_ingest.py --inspect edh_inscriptions.geojson` and check the
>    field keys. If the transcription / type / date / coordinates fields aren't
>    being picked up, add their real key names to the `*_KEYS` lists at the top of
>    `edh_ingest.py`.
> 2. Run `python edh_ingest.py edh_inscriptions.geojson --cap 2000` to write
>    `static/epigraphy_data.js`. Report the per-genre counts.
> 3. Start the app (`python app.py`), load `/api/manuscripts` and the homepage,
>    and confirm the Epigraphy browser fills with funerary / honourific / public
>    inscriptions and there are 0 parse errors.
> 4. Commit and push: `git add -A && git commit -m "Add Latin epigraphy batch 1
>    (~2000 EDH inscriptions)" && git push`.
> If any field looks wrong or empty, fix the mapping in `edh_ingest.py` and re-run
> before committing. Don't spend any Firecrawl credits — this is all offline.

## Open choice for the first batch

525k is too many to load in the browser at once, so batch 1 needs a cap/scope —
e.g. "≈2,000 best-preserved inscriptions with coordinates, all provinces" or
"everything from a chosen province (Aegyptus / Roma / Africa)". Pick the slice and
I'll build the ingester around it.

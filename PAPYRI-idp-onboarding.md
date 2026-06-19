# Onboarding documentary papyri from idp.data (free, no Firecrawl)

We Firecrawl papyri.info only because its live site is bot-gated. The same data is
published in bulk on GitHub at **github.com/papyri/idp.data** (CC BY 3.0), so we can
onboard documentary papyri offline for **zero Firecrawl credits** — and reuse the
HGV English translations that already exist, saving model tokens too. This is the
papyrus twin of the EDH pipeline (`edh_ingest.py`).

## What's in the repo (verified)

Three parallel TEI/EpiDoc trees, all linked by the HGV/TM number:

- `DDB_EpiDoc_XML/<collection>/<collection>.<vol>/<collection>.<vol>.<n>.xml`
  — the Greek/Latin transcription. e.g. `DDB_EpiDoc_XML/bgu/bgu.1/bgu.1.2.xml`.
- `HGV_meta_EpiDoc/HGV<k>/<N>.xml` where `k = ceil(N/1000)` — date + provenance.
  e.g. HGV 8961 → `HGV_meta_EpiDoc/HGV9/8961.xml`.
- `HGV_trans_EpiDoc/<N>.xml` — **flat, no subfolders** — translations (sparse;
  mostly German, a growing minority English).

**Linking:** each DDB file's header has
`<idno type="HGV">8961</idno>` (= `<idno type="TM">`), plus
`<idno type="ddb-hybrid">bgu;1;2</idno>` (→ citation "BGU 1.2", source URL
`https://papyri.info/ddbdp/bgu;1;2`). Map DDB → `HGV_meta_EpiDoc/HGV{ceil(N/1000)}/N.xml`
and → `HGV_trans_EpiDoc/N.xml`.

**EpiDoc markup** (same as EDH — reuse `edh_ingest`'s `_render` logic):
- text in `<div type="edition">/<ab>`; lines `<lb n="1"/>` (word continues if
  `break="no"`); expansions `<expan>στρ<ex>ατηγῷ</ex></expan>` → `στρατηγῷ`;
  restorations `<supplied reason="lost">τ</supplied>` → `[τ]`; gaps
  `<gap reason="lost"/>` / `<gap quantity="N" unit="character"/>` → `…`.
- Skip stubs: some files have an empty `<ab/>` (cross-reference only) — no text.

**HGV metadata fields:**
- date: `…/history/origin/origDate` — `@when` (e.g. `0209-01-23`) OR
  `@notBefore`/`@notAfter` for ranges.
- provenance: `origin/origPlace` + `provenance[@type="located"]//placeName`.
- subject/genre keyword: `textClass/keywords[@scheme="hgv"]`.
- **No coordinates.** Place names carry `@ref` with Pleiades
  (`pleiades.stoa.org/places/<id>`) and Trismegistos (`trismegistos.org/place/<id>`)
  IDs only — coords must be resolved externally (below).

**HGV translation:** `<div type="translation" xml:lang="en">/<p>` with
`<milestone n="N" unit="line"/>` line markers. A file may hold several translation
divs in different languages — **take the `xml:lang="en"` one**; ignore German-only.

## Setup (one time)

1. **Shallow-clone the data** next to the repo (don't nest it inside, and gitignore it):
   ```
   git clone --depth 1 https://github.com/papyri/idp.data.git ..\idp.data
   ```
   (Only `DDB_EpiDoc_XML`, `HGV_meta_EpiDoc`, `HGV_trans_EpiDoc` are needed.)
2. **Coordinates source — Pleiades dump** (free, CC-BY): download
   `pleiades-places-latest.csv.gz` from atlantides.org/downloads/pleiades/dumps,
   which has `id, reprLat, reprLong`. Build `{pleiades_id -> (lat, lon)}`.
3. Add `idp.data/` and the Pleiades csv to `.gitignore`.

## Build `idp_ingest.py` (papyrus twin of edh_ingest.py)

Mirror `edh_ingest.py`'s structure and **reuse existing helpers**:
- EpiDoc rendering → borrow `edh_ingest._render` (expan/supplied/gap/lb).
- citation/slug/genre/date cleaning + the find-site `COORDS` map → borrow from
  `build_from_sweep.py` (`citation()`, `slug()`, `clean_greek()`, `GENRE_RULES`,
  `COORDS`, `clean_date()`).
- Output `.txt` format = exactly what `build_from_sweep` writes (so the app parses
  it unchanged): `[META]` (id/label=citation, name, genre, date, language:
  "Greek (Koiné)", found=origPlace, held, shelf, content, tm, source, lat, lon),
  `[GREEK]` (`r.N <line>`), `[TRANSLATION]` (`N <english>`).

Per papyrus:
1. Parse the DDB XML; render the edition into clean numbered Greek lines. Skip if
   no text (empty `<ab/>`).
2. Read `<idno type="HGV">` (= N) and `ddb-hybrid` (→ citation, source URL, slug).
3. Open `HGV_meta_EpiDoc/HGV{ceil(N/1000)}/N.xml`: get date (origDate when /
   notBefore-notAfter), found (origPlace), genre (map the hgv keyword via
   `GENRE_RULES`, else "documents"), and the Pleiades id from the placeName `@ref`.
4. Coords: Pleiades id → (lat,lon) from the dump; fallback to the `COORDS`
   name map (origPlace substring), else leave blank (check_city_nodes handles later).
5. Translation scaffold (line-aligned is REQUIRED): write a `[TRANSLATION]` block
   with one blank numbered slot per Greek `r.N` line, so the model can fill them so
   the English lines up with the Greek line-for-line (same as `build_from_sweep`,
   which asserts `#greek == #translation`). If `HGV_trans_EpiDoc/N.xml` has an
   English `<div type="translation" xml:lang="en">`, capture its prose as a
   **commented reference** under the `[TRANSLATION]` header (e.g.
   `# HGV-EN: <prose>`) — a head-start for the translator, NOT the final text
   (HGV is prose, not line-aligned). German-only files: skip.
6. Write `manuscripts/<slug>.txt`.

**Additive + capped, like edh_ingest:**
- `--add` (default behaviour for batches): skip any papyrus whose `.txt` already
  exists in `manuscripts/`, so re-runs never duplicate and never overwrite
  hand-translated files.
- `--cap N` (default 2000): onboard the next N best-preserved (most text) papyri
  not already present.
- `--inspect` / `--selftest`: offline sanity check on a couple of sample files.

## Run + verify

```
py idp_ingest.py ..\idp.data --cap 2000          # writes manuscripts/*.txt (no credits)
py check_city_nodes.py                           # add any missing find-site nodes
py app.py                                         # spot-check: Greek renders, [supplied] is blue,
                                                  #   HGV-English papyri already show a translation
```

Then run the model translation pass (`build_from_sweep`/the translation loop) to fill
the line-aligned English for the batch. Every papyrus needs this pass for the aligned
English; where an HGV English reference was captured, the model lays *that* out
line-by-line (faster, faithful) instead of translating cold. Publish with
`update_website.bat`.

## Notes

- **Zero interference with inscriptions:** this writes `manuscripts/*.txt` and
  `static/data/custom_locations.json`; inscription onboarding writes
  `static/epigraphy_data.js`. Different files. Just keep one git committer at a time.
- The contents API caps listings at 1000; crawl the local clone with `os.walk`
  (or `git ls-files`) instead.
- Firecrawl is now only for sources that are NOT in idp.data / EDH / the NTVMR API.

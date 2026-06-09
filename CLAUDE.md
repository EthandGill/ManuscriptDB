# ManuscriptDB

A Flask web app for exploring ancient New Testament papyri on an interactive map,
with Greek/English diglot reading and travel-route planning across the ancient world.

## Run it

```
python app.py        # Flask dev server on http://localhost:5000
```

(VS Code launch config: `.claude/launch.json`, name "ManuscriptDB", port 5000.)

## Architecture

- **`app.py`** — Flask backend. Serves `index.html` at `/` and a JSON feed at
  `/api/manuscripts`. The core is `parse_manuscript()`, which reads the custom
  `.txt` format in `manuscripts/` into structured JSON. `app.json.sort_keys = False`
  preserves dict order in responses.
- **`manuscripts/*.txt`** — the data. ~134 papyri (P1–P141) in a custom
  bracket-tagged text format (see below).
- **`templates/index.html`** — single-page UI: sidebar (manuscript search +
  date/pericope filters, epigraphy browser, route planner, ancient-cities list,
  social networks), a Leaflet map (`#map`), and the "Writing Stand" (`#writing-stand`)
  diglot reader.
- **`static/`**
  - `script.js` (~117KB) — main frontend app
  - `pauline_network.js` — Pauline social network graph (62 people)
  - `manuscript_network.js` — manuscript relationship network
  - `style.css`, plus Leaflet map `tiles/` (zoom levels 1–6)
  - `data/` — ORBIS travel network (`orbis.json`, `orbis_network.json`),
    `gorbit-nodes.csv` / `gorbit-edges.csv`, and `custom_locations.json`
    (find-site coordinates for manuscripts not in ORBIS)

## Manuscript `.txt` format

```
[META]
id:       P1
name:     Papyrus 1
genre:    new-testament
date:     c. 250 CE
found:    Oxyrhynchus, Egypt
held:     Penn Museum (E 2746)
content:  Matthew 1:1-9, 1:12-20
lat:      28.5383
lon:      30.6765
book:     Matthew          # comma-separated for multi-book manuscripts

[GREEK]
FOLIO Recto
r.1   βιβλος γενεσεως {ιυ} {χυ} ...
r.2   ... GAP: not preserved

[TRANSLATION]
1:1   The book of the genealogy of Jesus Christ ...
```

Notation parsed by `app.py`:
- `{word}` = nomen sacrum (rendered with overline)
- `[word]` = supplied / reconstructed lacuna
- `FOLIO <label>` = folio separator header
- `r.N` / `v.N` = recto/verso line markers
- `GAP: ...` = line not preserved
- Multi-book manuscripts use `[GREEK:BookName]` / `[TRANSLATION:BookName]` /
  `[CONTENT:BookName]` sections instead of flat `[GREEK]` / `[TRANSLATION]`.

## Importing new manuscripts

The **`grab-manuscript`** skill (`.claude/skills/grab-manuscript/SKILL.md`) handles
fetching papyri from the NTVMR (Münster) transcription API. Triggered by requests
like "grab me P46" / "fetch P117". Flow: look up metadata → probe page IDs
(`.claude/skills/grab-manuscript/scripts/probe_pages.py`) → `import_manuscript.py`
→ post-process folio labels → add translations. NTVMR docID = `10000 + GA number`.

Translations should be faithful to **this manuscript's actual Greek** (including
its variant readings), not the generic ESV text for the verse numbers. Use
**`extract_verses.py`** to make that efficient: it re-fetches the NTVMR pages,
reads the TEI `<ab n="B07K7V10">` verse anchors the importer discards, and emits a
verse-aligned `[TRANSLATION]` scaffold showing the real reconstructed Greek per
verse (split words re-joined, `[reconstructions]`/`{nomina sacra}` kept, gaps as
`…`). Then translate each verse from the Greek shown.

```
python extract_verses.py --docID 10015 --id P15 --pages 10 20 --out manuscripts\P15.translation.txt
python extract_verses.py --selftest      # offline parser check
python test_extract_verses.py            # offline regression suite
```

The other root-level `*.py` scripts (`postprocess_batch.py`, `finalize_p11.py`,
`probe_*.py`, `fetch_missing.py`, etc.) are one-off import/cleanup utilities used
while building out the collection.

## Sharing a live demo

`share_with_cloudflare.bat` puts the running app on a public link for free using
a Cloudflare quick tunnel (no account/domain needed). Double-click it: it
installs `cloudflared` if missing, starts `python app.py`, and prints a public
`https://….trycloudflare.com` URL that proxies to `localhost:5000`. The URL is
temporary and changes each run; keep the window open while sharing, Ctrl+C to
stop. For a permanent address, register a domain on Cloudflare and create a named
tunnel (`cloudflared tunnel create` + a DNS route) instead.

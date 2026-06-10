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

## Scraping manuscripts from the web (Firecrawl)

The **`scrape-manuscript`** skill (`.claude/skills/scrape-manuscript/SKILL.md`)
pulls papyri from web sources — primarily **papyri.info (DDbDP)** for *documentary*
papyri (receipts, contracts, leases, letters) that the NTVMR API doesn't carry.
It uses **Firecrawl**, which renders JS and clears the "Anubis" bot-gate that
blocks plain WebFetch on papyri.info. Trigger: "scrape me a receipt", "firecrawl
bgu;3;697", "pull contracts from Trismegistos". Documentary `.txt` files use
`genre: receipts|contracts|letters`, line-numbered `r.N` Greek (no book/chapter),
a `tm:`/`source:` field, and a faithful literal translation (e.g. `bgu_3_697.txt`).

Setup: `pip install firecrawl-py truststore`; put the key in the `FIRECRAWL_API_KEY`
env var (never hardcode it). On this machine TLS inspection breaks cert validation,
so the helpers call `truststore.inject_into_ssl()` to trust the Windows cert store.
`firecrawl_scrape.py` (repo root) is a generic scrape-any-URL helper;
`.claude/skills/scrape-manuscript/scripts/scrape_papyrus.py` extracts the
TM/origin/date/Greek fields from a papyri.info DDbDP id.

## Sharing a live demo

`share_with_cloudflare.bat` puts the running app on a public link for free using
a Cloudflare quick tunnel (no account/domain needed). Double-click it: it
installs `cloudflared` if missing, starts `python app.py`, and prints a public
`https://….trycloudflare.com` URL that proxies to `localhost:5000`. The URL is
temporary and changes each run; keep the window open while sharing, Ctrl+C to
stop. For a permanent address, register a domain on Cloudflare and create a named
tunnel (`cloudflared tunnel create` + a DNS route) instead.

## Continuous bulk import (run without re-prompting)

To import many manuscripts in one autonomous run instead of one-at-a-time:

1. **Build the worklist:** `python make_queue.py` scans `manuscripts/` and writes
   `import_queue.txt` with every Gregory-Aland number still missing (gaps in
   P1–P141 by default; `--max N` to extend). Skip rules: lines starting with `#`
   or `DONE ` are ignored, so items can be ticked off as `DONE P14`.
2. **Turn off the pauses:** in Claude Code press **Shift+Tab** to reach
   *auto-accept edits* / bypass-permissions, or add an allowlist to
   `.claude/settings.json` (see below) so the run never stops for approval.
3. **Kick it off with one looping prompt** (this is the whole point — it does not
   stop between manuscripts):

   > Work through `import_queue.txt` top to bottom. For each ID not already in
   > `manuscripts/`, run the full grab-manuscript flow (probe -> `import_manuscript.py`
   > -> post-process folio labels -> `extract_verses.py` -> translate every verse
   > faithfully from the actual Greek per Step 5). Then mark that line `DONE` in
   > the queue and **immediately continue to the next without asking me**. Don't
   > stop until the queue is empty. If one manuscript errors, append it to
   > `import_errors.log` and move on to the next.

   Re-running the same prompt later resumes where it left off (DONE lines skip).

**Speed:** the probe/import/post-process steps need no model, so for raw Greek
import you can fan out parallel subagents (one per manuscript). The translation
step needs the model, so it runs in the main session as the loop proceeds.

**Unattended / scheduled:** for hands-off recurring runs, schedule a headless call
on Windows Task Scheduler, e.g. daily:
`claude -p "process the next 10 items in import_queue.txt per CLAUDE.md"`
(run from `C:\ManuscriptDB`). The NTVMR fetch needs outbound internet, so this
runs on your machine, not on a restricted host.

**Permission allowlist** (paste into `.claude/settings.json` to avoid prompts):

```json
{
  "permissions": {
    "allow": [
      "Bash(python *)",
      "Bash(python3 *)",
      "Read(*)",
      "Write(manuscripts/*)",
      "Edit(manuscripts/*)",
      "Edit(import_queue.txt)"
    ]
  }
}
```

# ManuscriptDB — Manuscript-Retrieving Skills

A single reference for every skill that **brings new manuscripts into the
corpus** (`C:\ManuscriptDB\manuscripts\*.txt`) and keeps the map consistent
afterward. Three skills, each living under `.claude/skills/<name>/SKILL.md`:

| Skill | Source | Use it for | Cost |
|-------|--------|------------|------|
| [`grab-manuscript`](#1-grab-manuscript--ntvmr-nt-papyri) | NTVMR transcription API (Münster) | **New Testament** Gregory-Aland papyri (P1–P141…) | Free |
| [`scrape-manuscript`](#2-scrape-manuscript--firecrawl-documentary-papyri) | papyri.info / DDbDP, Trismegistos, web | **Documentary** papyri: receipts, contracts, leases, sales, petitions, letters | Firecrawl credits |
| [`check-city-nodes`](#3-check-city-nodes--map-consistency-run-last) | local data | **Map consistency** — run as the last step of any onboarding batch | Free |

> **Trigger them by talking to Claude**, e.g. *"grab me P46"*, *"fetch P117"*,
> *"scrape me a receipt"*, *"firecrawl bgu;3;697"*, *"check city nodes"*. Claude
> auto-selects the right skill; you don't invoke them manually.

---

## Decision: which skill?

```
Is it a New Testament papyrus (a "P<number>" / Gregory-Aland id)?
├── YES → grab-manuscript   (NTVMR API, free, no Firecrawl)
└── NO  → scrape-manuscript (Firecrawl — receipts/contracts/letters/petitions/documents)

After ANY onboarding batch → check-city-nodes  (must end with ORPHAN: 0)
```

Both retrieval skills write the same on-disk format (see
[Output format](#shared-the-txt-format)) and follow the same quality bar:
**faithful, line-aligned translations of what *this* manuscript actually says** —
never a generic paraphrase.

---

## 1. `grab-manuscript` — NTVMR NT papyri

Fetches one or more Gregory-Aland papyri from the **NTVMR** (Institut für
Neutestamentliche Textforschung, University of Münster) transcription API and
writes `manuscripts/P<N>.txt`. Handles single manuscripts or batches.

**Key fact:** `docID = 10000 + GA number` (P46 → `10046`, P117 → `10117`).

### Flow

0. **Check existing** — skip any `P<N>` already in `manuscripts/`.
1. **Look up metadata** (Wikipedia `…/wiki/Papyrus_<N>` or web search): `content`
   (verse ranges), `date` (paleographic), `found` (find-site), `held`
   (institution + shelf mark), `book`, and **find-site** `lat`/`lon`
   (the find-site, *not* the holding museum).
2. **Probe page IDs:**
   ```
   python .claude\skills\grab-manuscript\scripts\probe_pages.py <docID> --max 400
   ```
   Prints a `FOUND_PAGES:10,20,31,…` line. Most small papyri have only pages 10 & 20;
   large codices (P11, P46, P45, P75) spread 20–30+ pages across 1–400. The API
   returns intermittent HTTP 500s — the probe retries.
3. **Import:**
   ```
   python import_manuscript.py --docID <docID> --id P<N> --name "Papyrus <N>" \
     --genre new-testament --date "<date>" --found "<site>" --held "<inst (shelf)>" \
     --content "<verse ranges>" --book "<book>" --lat <lat> --lon <lon> \
     --pages <space-separated page IDs>
   ```
   The importer fetches each page (4 retries), parses TEI XML into clean Greek with
   `[lacuna]` / `{nomina sacra}` notation, extracts folio labels from editorial
   notes, and builds `FOLIO NR — Book Chapter:Verse` headers.
4. **Post-process the `.txt`:**
   - Fill `FOLIO ?` labels (2-page → `1R`/`1V`; multi-page → infer from verse sequence).
   - Strip duplicate verse ranges (`2:14-14` → `2:14`).
   - Fix `v.` → `r.` line markers inside any recto folio block.
5. **Add translations** — one line per verse under `[TRANSLATION]`, translated
   **faithfully to this manuscript's actual reconstructed Greek (incl. variant
   readings), not the generic ESV** for the verse numbers. Use **`extract_verses.py`**
   to emit a verse-aligned scaffold of the real Greek per verse, then translate from
   it; gaps as `…`. Multi-book manuscripts use `[TRANSLATION:BookName]` sections
   matching the importer's `[GREEK:BookName]` sections.
6. **Report** what was added/skipped (content, date, held, folios).

### Gotchas
- P11: skip page 230 (Romans content misassigned).
- A page with content but 0 imported lines → re-run the import for that page (flaky API).
- Reclassified fragments ("Vormals P14") lack folio labels — assign by verse position.

---

## 2. `scrape-manuscript` — Firecrawl documentary papyri

Web-scrapes a documentary or literary papyrus — primarily from **papyri.info
(DDbDP)** — using **Firecrawl**, which renders JavaScript and clears the "Anubis"
bot-gate that plain WebFetch cannot. This is the companion to `grab-manuscript`
for everything that is *not* an NT transcription on NTVMR.

### Setup (once)
```
python -m pip install firecrawl-py truststore
```
- **API key** comes from the `FIRECRAWL_API_KEY` env var — **never hardcode/commit it**.
  `PowerShell: $env:FIRECRAWL_API_KEY = "fc-…"`
- This machine does **TLS inspection**, so the helper calls
  `truststore.inject_into_ssl()` to trust the Windows cert store (verification stays on).
  Run scrape commands **outside the sandbox** if you hit a TLS error in-sandbox.

### Flow

1. **Identify the source** — a DDbDP id (`bgu;1;2`, `p.oxy;1;1`) or a full URL
   (papyri.info, `trismegistos.org/text/<n>`, Wikipedia, NTVMR). To *find* texts,
   browse papyri.info / Trismegistos search, collect ids, and report how many you
   covered (never silently cap).
2. **Scrape:**
   ```
   python .claude\skills\scrape-manuscript\scripts\scrape_papyrus.py <id-or-url> --out _raw.md
   ```
   Prints `TM / ORIGIN / DATE / SUPPORT / TITLE / CITATION / SUBJECTS / SHELF` plus
   the Greek lines. Re-run once if the page looks blocked. Delete `_raw.md` when done.
   (`firecrawl_scrape.py` at the repo root is a generic scrape-any-URL helper.)
3. **Clean the Greek** — convert papyri.info markup to ManuscriptDB notation:
   `\[ … \]` → `[ … ]` (lacuna/restoration); keep editor-resolved abbreviations;
   strip the every-5 line-number digit (`5σήκοντα` → `σήκοντα`); **drop** apparatus
   criticus and edit-history lines. Keep the editor's line breaks (one line → one `r.N`).
4. **Classify genre + geolocate** — the `Subjects` row (German HGV keywords) is the
   fastest signal:
   - `Quittung` → **receipts** (`ἔσχον` / `ἀπέχω`, tax/rent acknowledgements)
   - `Vertrag` / `Kaufvertrag` / `Pachtvertrag` / `Darlehen` → **contracts**
     (`ὁμολογῶ`; sales, leases, loans, marriage, apprenticeship)
   - `Brief` → **letters** (`χαίρειν`, `ἐρρῶσθαί σε εὔχομαι`)
   - `Eingabe` / `Petition` → **petitions**; other admin texts → **documents**
   Map `Origin` → find-site `lat`/`lon` (table of common provenances in the SKILL).
   The `Inv. no.` → the `shelf:` field (shown in the sidebar).
5. **Write the `.txt`** — documentary texts have no chapter:verse, so use `r.N`
   line numbers; filename is a citation slug (`bgu_1_2.txt`).
6. **Translate** literally and faithfully to what the papyrus says; keep documentary
   formulae recognizable ("I, NN, acknowledge that I have received…"); end where it
   breaks off, marking lost stretches with `…`.
7. **Report** + verify it parses (the new entry appears under its genre with Greek
   + translation).

> **Genres in use:** `new-testament`, `receipts`, `contracts`, `letters`,
> `petitions`, `documents`.

---

## 3. `check-city-nodes` — map consistency (run last)

The map draws one **orb** per location. Each manuscript's `(lat, lon)` find-site is
**snapped to the nearest city within 0.3° (≈33 km)** — ORBIS cities
(`static/data/orbis.json`) **plus** `static/data/custom_locations.json`. A find-site
with no city in range falls back to an unnamed **"This site"** orb. Goal: **0 orphans**.

### Flow
1. **Scan:**
   ```
   python check_city_nodes.py          # exits 1 + lists orphan find-sites if any
   python check_city_nodes.py --list   # also prints per-city distribution
   ```
   It mirrors the frontend's `findSnapCity` 0.3° rule and reports orphan coordinate
   clusters with example manuscripts and their `found:` field.
2. **Add a node per orphan** — append to `static/data/custom_locations.json` at the
   **exact orphan coordinate** (distance 0 always wins the tiebreak):
   ```json
   { "id": "<kebab-slug>", "name": "<City>", "modern": "<modern place>, <country>",
     "lat": <lat>, "lon": <lon> }
   ```
   Take `name`/`modern` from the orphan's `found:` field. If two distinct villages
   share one fallback coordinate, nudge one manuscript's `lat`/`lon` slightly and give
   each place its own node.
3. **Re-verify:** `python check_city_nodes.py` → must print **`ORPHAN: 0`**.

This skill is **data-only** (`custom_locations.json`, occasionally one `lat`/`lon`
line) — it never edits `script.js`. Custom nodes also appear in the Ancient-Cities
list and as route endpoints, but are not in the ORBIS road/sea network (not routable).

---

## Shared: the `.txt` format

Both retrieval skills emit the same bracket-tagged file consumed by
`parse_manuscript()` in `app.py`:

```
[META]
id:       <label>            # e.g. P117  or  BGU 1.2
label:    <label>
name:     <short human title>
genre:    new-testament | receipts | contracts | letters | petitions | documents
date:     <normalised date, e.g. 209 CE>
language: Greek (Koine)
found:    <find-site, e.g. Oxyrhynchus, Egypt>
held:     <institution>
shelf:    <Inv. no. — shown in the sidebar>   # documentary texts
content:  <one-line summary / verse ranges>
book:     <Book>             # NT only; comma-separated for multi-book
tm:       <Trismegistos no.> # documentary texts
source:   <URL>
lat:      <find-site latitude>
lon:      <find-site longitude>

[GREEK]
r.1   βιβλος γενεσεως {ιυ} {χυ} …      # {word}=nomen sacrum  [word]=lacuna  GAP: not preserved
r.2   …

[TRANSLATION]
1     The book of the genealogy …        # keyed to the SAME line/verse numbers
```

- NT papyri key Greek/translation by `chapter:verse`; documentary papyri by `r.N`
  line numbers. `FOLIO <label>` headers mark folio/side breaks in both sections.
- Multi-book NT manuscripts use `[GREEK:Book]` / `[TRANSLATION:Book]` / `[CONTENT:Book]`
  sections instead of flat ones.

---

## Bulk / continuous import

`make_queue.py` builds a worklist of every Gregory-Aland number still missing
(`import_queue.txt`; lines starting with `#` or `DONE ` are skipped). A single
looping prompt then runs the full `grab-manuscript` flow per id, marking each
`DONE` and continuing without re-prompting — re-running resumes where it left off.
Probe/import/post-process need no model and can fan out to parallel subagents; the
translation step runs in the main session. See **CLAUDE.md → "Continuous bulk
import"** for the exact prompt, the `.claude/settings.json` permission allowlist,
and Windows Task Scheduler / headless `claude -p "…"` setup.

## Supporting scripts (repo root)

| Script | Purpose |
|--------|---------|
| `import_manuscript.py` | NTVMR fetch → parse TEI → write `P<N>.txt` (used by grab-manuscript) |
| `extract_verses.py` | Re-fetch NTVMR pages, read TEI verse anchors, emit a verse-aligned `[TRANSLATION]` scaffold of the *real* reconstructed Greek to translate from |
| `firecrawl_scrape.py` | Generic "scrape any URL via Firecrawl" helper |
| `check_city_nodes.py` | Map-orphan audit (used by check-city-nodes) |
| `make_queue.py` | Build `import_queue.txt` of missing GA numbers |
| `share_with_cloudflare.bat` | Put the running app on a public `…trycloudflare.com` link |

---

*Each skill's `SKILL.md` is the authoritative, detailed source; this file is the
map across all three. Keep them in sync if a workflow changes.*

---
name: grab-manuscript
description: >
  Fetches a New Testament papyrus manuscript from the NTVMR (Institut für
  Neutestamentliche Textforschung, University of Münster) API and adds it to
  the ManuscriptDB project at C:\ManuscriptDB. Use this skill whenever the
  user says anything like "grab me P46", "fetch manuscript P117", "add P45
  from NTVMR", "Claude get this papyrus: P11, P15", or any request to import
  one or more Gregory-Aland papyri into the database. Also trigger when the
  user asks to "download" or "pull" a papyrus, even without explicitly
  mentioning NTVMR. Handles single manuscripts or batches in one go.
---

# Grab Manuscript from NTVMR

You are fetching one or more New Testament papyri from the NTVMR (Münster)
transcription API and adding them to `C:\ManuscriptDB\manuscripts\`.

## Step 0 — Check what already exists

```python
import os
existing = set(f.replace('.txt','') for f in os.listdir(r'C:\ManuscriptDB\manuscripts') if f.endswith('.txt'))
```

For each requested manuscript (e.g. "P46", "P117"), skip it with a note if
`f"P{n}"` is already in `existing`. Continue only with the new ones.

---

## Step 1 — Look up metadata

For each new manuscript, fetch its Wikipedia page or use web search to find:

| Field | How to get it |
|-------|--------------|
| **content** | Exact verse ranges (e.g. `"1 Corinthians 7:18-8:4"`) |
| **date** | Paleographic date (e.g. `"c. 3rd-4th century CE"`) |
| **found** | Find site (e.g. `"Oxyrhynchus, Egypt"`) |
| **held** | Institution + shelf mark (e.g. `"Sackler Library, Oxford (P. Oxy. 1008)"`) |
| **book** | Biblical book name(s) for the `book:` META field |
| **lat/lon** | Coordinates of the *find site* (not the holding institution) |

Wikipedia URL pattern: `https://en.wikipedia.org/wiki/Papyrus_<N>`

Common find-site coordinates:
- Oxyrhynchus, Egypt → lat 28.5383, lon 30.6765
- Fayyum, Egypt → lat 29.3084, lon 30.8428
- Unknown Egypt → lat 28.5383, lon 30.6765 (generic)
- Qumran → lat 31.7433, lon 35.4572

The **docID** for NTVMR is always `10000 + GA number`:
- P11 → docID 10011
- P46 → docID 10046
- P117 → docID 10117

---

## Step 2 — Probe for valid page IDs

Run the probe script to discover which page IDs have transcription content:

```bash
cd C:\ManuscriptDB
python .claude\skills\grab-manuscript\scripts\probe_pages.py <docID> --max 400
```

The script prints each found page and ends with a `FOUND_PAGES:10,20,31,...` line.

**Tips from experience:**
- Most small manuscripts (1–2 leaves) only have pages 10 and 20
- Large manuscripts like P11 or P46 may have 20–30+ pages spread across 1–400
- The NTVMR API returns HTTP 500 intermittently — the probe retries automatically
- For P11 specifically, skip page 230: it contains Romans content erroneously assigned to the manuscript
- If a page has content but produces 0 lines after import, re-run the import with that page — the server is flaky

---

## Step 3 — Import via import_manuscript.py

Run the importer with all discovered page IDs:

```bash
cd C:\ManuscriptDB
python import_manuscript.py \
  --docID <docID> \
  --id P<N> \
  --name "Papyrus <N>" \
  --genre new-testament \
  --date "<date>" \
  --found "<find site>" \
  --held "<institution (shelf mark)>" \
  --content "<verse ranges>" \
  --book "<book name>" \
  --lat <lat> --lon <lon> \
  --pages <space-separated page IDs>
```

The importer:
- Fetches each page from NTVMR with 4 retries
- Parses TEI XML into clean Greek lines with `[lacuna]` and `{nomina sacra}` notation
- Extracts folio labels from `<note type="editorial">` elements (e.g. `"F19v = frg. XVI"` → `19V`)
- Builds `FOLIO NR — Book Chapter:Verse` headers automatically
- Writes `C:\ManuscriptDB\manuscripts\P<N>.txt`

---

## Step 4 — Post-process the output file

Read the generated `.txt` file and apply these fixes:

### 4a. Fix `FOLIO ?` labels

When NTVMR has no editorial folio note, the importer writes `FOLIO ? — Book X:Y`.
Replace these with correct labels based on the manuscript's physical sequence:

- **2-page manuscripts** (pages 10 and 20): `FOLIO 1R — ...` and `FOLIO 1V — ...`
- **Multi-page manuscripts**: use the verse content to determine position relative to
  the known folios (e.g. if F6V=3:5 and F9R=4:3, a page with 3:8 is likely F7R)

### 4b. Fix duplicate verse ranges

The importer sometimes writes `FOLIO 5R — 1 Corinthians 2:14-14` when a folio
contains only a single verse. Strip the duplicate: `2:14-14` → `2:14`.
Pattern: any `N:M-M` where both verse numbers are identical.

### 4c. Fix wrong `v.` prefixes on recto folios

The importer defaults to `v.` (verso) when a folio label doesn't explicitly
contain a digit+R pattern. For `FOLIO 1R` or any recto folio, change all
`v.N` line markers in that folio's block to `r.N`.

Apply the fix only within the block that belongs to that folio (stop at the
next `FOLIO` header).

---

## Step 5 — Add translations

Add a `[TRANSLATION]` section at the end of the file (replacing the commented
placeholder). Write one line per verse for every verse range in the manuscript:

```
[TRANSLATION]
7:6    But God, who comforts the downcast, comforted us by the coming of Titus,
7:7    and not only by his coming but also by the comfort...
```

Use ESV-style English translations (standard modern scholarly rendering).

**For multi-book manuscripts** (e.g. P34 containing both 1 Cor and 2 Cor):
- The importer already wrote `[GREEK:1 Corinthians]` and `[GREEK:2 Corinthians]` sections
- Write matching `[TRANSLATION:1 Corinthians]` and `[TRANSLATION:2 Corinthians]` sections

---

## Step 6 — Report

After completing all manuscripts, report:

```
✅ Added P117
   Content:  2 Corinthians 7:6–11
   Date:     c. 4th–5th century CE
   Held:     University of Hamburg (Inv. NS 1002)
   Folios:   1R (7:6–8) · 1V (7:9–11)

⏭️  Skipped P34 — already in database

✅ Added P124
   Content:  2 Corinthians 11:1–4, 6–9
   ...
```

---

## Common patterns

### Tiny fragment (1–2 folios)
Most papyri are tiny — only pages 10 and 20.
Run the probe, confirm two pages, import, assign `1R`/`1V`, add translation. Done in under a minute.

### Medium manuscript (3–10 folios)
Pages spread across 10, 20, 30... with gaps. The probe finds them all.
Folio labels usually come from editorial notes. Check for any remaining `?` labels and
fill them in by looking at the verse sequence.

### Large codex (P11, P46, P45, P75)
20–30+ pages, often with non-sequential IDs (e.g. 31, 41, 81, 192...).
Some pages may have "Vormals P14" or similar notes indicating reclassified fragments —
these lack folio labels. Assign based on their verse position in the sequence.
Re-run the import for any pages that produced 0 lines (the NTVMR API is flaky at scale).

### Multi-book manuscript (P34, P46, P72)
When `book:` contains multiple books (e.g. `"1 Corinthians, 2 Corinthians"`):
- The importer splits into `[GREEK:BookName]` sections automatically
- Add matching `[TRANSLATION:BookName]` sections (not a single `[TRANSLATION]`)

---

## Reference: Book → docID examples

| Manuscript | docID | Content |
|-----------|-------|---------|
| P11 | 10011 | 1 Cor 1:17–7:14 |
| P15 | 10015 | 1 Cor 7:18–8:4 |
| P34 | 10034 | 1 Cor 16 + 2 Cor 5, 10, 11 |
| P46 | 10046 | Romans–1 Thess (Chester Beatty) |
| P66 | 10066 | John 1:1–14:26 |
| P72 | 10072 | 1–2 Peter, Jude |
| P75 | 10075 | Luke + John |
| P117 | 10117 | 2 Cor 7:6–11 |
| P124 | 10124 | 2 Cor 11:1–4, 6–9 |

---
name: scrape-manuscript
description: >
  Web-scrapes a documentary or literary papyrus from an online source
  (papyri.info / DDbDP, Trismegistos, NTVMR, Wikipedia) using Firecrawl, and
  adds it to the ManuscriptDB project at C:\ManuscriptDB. Firecrawl renders
  JavaScript and clears bot-gates (e.g. the "Anubis" check on papyri.info) that
  plain WebFetch cannot. Use this skill whenever the user wants to scrape or pull
  a papyrus from the web — especially DOCUMENTARY papyri such as RECEIPTS,
  CONTRACTS, LEASES, SALES, PETITIONS and LETTERS for the receipts/contracts/
  letters genres — e.g. "scrape me a receipt", "webscrape P.Oxy 1 from
  papyri.info", "pull contracts from Trismegistos", "firecrawl this papyrus:
  bgu;1;2", "add documentary papyri". For Gregory-Aland NT papyri fetched from
  the NTVMR transcription API, use the grab-manuscript skill instead.
---

# Scrape Manuscript from the Web (Firecrawl)

You are fetching a papyrus from a web source via **Firecrawl** and adding it to
`C:\ManuscriptDB\manuscripts\`. This is the companion to `grab-manuscript`:
that skill targets the NTVMR API for NT (Gregory-Aland) papyri; THIS skill scrapes
arbitrary web pages — primarily **papyri.info (DDbDP)** for documentary papyri
(receipts, contracts, leases, sales, petitions, private letters).

## Step 0 — Setup check

```bash
python -m pip install firecrawl-py truststore     # once
```

The API key is read from the `FIRECRAWL_API_KEY` environment variable — NEVER
hardcode it in a file that gets committed. Set it for the shell:

```
PowerShell:  $env:FIRECRAWL_API_KEY = "fc-..."
bash:        export FIRECRAWL_API_KEY="fc-..."
```

**Two machine-specific gotchas (already handled by the helper script):**
- This machine does TLS inspection; Python's certifi bundle doesn't trust the
  injected root, so requests fail with `CERTIFICATE_VERIFY_FAILED`. The fix is
  `truststore.inject_into_ssl()` (trust the Windows cert store; verification stays on).
- Run scrape commands outside the sandbox if you hit a TLS error in-sandbox.

Check what already exists so you don't duplicate:

```python
import os
existing = set(f for f in os.listdir(r'C:\ManuscriptDB\manuscripts') if f.endswith('.txt'))
```

---

## Step 1 — Identify the source

- **papyri.info DDbDP id** (preferred for documentary texts): e.g. `bgu;1;2`,
  `p.oxy;1;1`. The scraper builds `https://papyri.info/ddbdp/<id>`.
- A full URL to any page (papyri.info, Trismegistos `trismegistos.org/text/<n>`,
  a Wikipedia papyrus page, an NTVMR page).
- If the user asks to *find* receipts/contracts rather than naming ids, browse
  papyri.info search (`https://papyri.info/search`) or Trismegistos, collect the
  DDbDP ids, then scrape each. Note in your report how many you covered and that
  more exist (do not silently cap).

---

## Step 2 — Scrape

```bash
cd C:\ManuscriptDB
python .claude\skills\scrape-manuscript\scripts\scrape_papyrus.py <ddbdp-id-or-url> --out _raw.md
```

The script prints `TM / ORIGIN / DATE / SUPPORT / TITLE / CITATION` and the
Greek transcription lines, and saves the full raw markdown to `--out` for reference.
Delete the `_raw.md` scratch file when done.

If a page returns little/looks blocked, re-run once (Firecrawl occasionally needs
a second pass to clear a bot-gate).

---

## Step 3 — Clean the Greek transcription

papyri.info markdown carries editorial markup that must be converted to the
ManuscriptDB notation:

| papyri.info / markdown            | ManuscriptDB             | meaning                          |
|-----------------------------------|--------------------------|----------------------------------|
| `\[ ... \]` (escaped brackets)    | `[ ... ]`                | editorial restoration / lacuna   |
| `(...)` after an abbrev (e.g. `στρ(ατηγῷ)`) | keep the resolved form | abbreviation expanded by editors |
| leading every-5 line number (e.g. `5σήκοντα`, `10καὶ`) | strip the digit | papyri.info line counter         |
| `⟦ ... ⟧` / `{ ... }` (deletions) | drop / note             | scribal deletion                 |
| trailing `1. l. …`, vote/commit log lines | DROP                | apparatus criticus & edit history — NOT text |
| nomen sacrum (rare in documents) | `{...}`                  | sacred-name abbreviation         |

Keep the editor's line breaks: each transcription line becomes one `r.N` line.
Documentary papyri are single-side unless the source marks recto/verso — then use
`FOLIO Recto` / `FOLIO Verso` headers (and they will also appear in the translation,
Step 5).

---

## Step 4 — Classify the genre + geolocate

papyri.info's **`Subjects`** row (German HGV keywords) is the fastest genre signal:
`Quittung` = receipt · `Vertrag`/`Kaufvertrag`/`Pachtvertrag`/`Darlehen` = contract
(sale/lease/loan) · `Brief` = letter · `Eingabe`/`Petition` = petition. The scraper
prints `SUBJECTS:` and `SHELF:` (from the `Inv. no.` row — the museum shelf mark,
which **must** go in the `shelf:` field so it shows in the sidebar). Confirm with the
Greek; set `genre:` to one of ManuscriptDB's documentary genres:

- **receipts** — acknowledgement of payment received: `ἔσχον` / `ἀπέχω`
  ("I have received"), tax/rent receipts, ostraca for grain or money.
- **contracts** — `ὁμολογῶ` ("I acknowledge/agree"), leases (`ἐκμίσθωσις`/`μισθόω`),
  sales (`πρᾶσις`/`ἀπέδομην`), loans (`δάνειον`), marriage, apprenticeship.
- **letters** — private correspondence: `χαίρειν` greeting, `ἐρρῶσθαί σε εὔχομαι`.
- (petitions/applications like `ἐπιδίδωμι … βιβλίδιον`, `παρὰ X τῷ στρατηγῷ` have no
  dedicated genre yet — confirm with the user whether to add one or file under the
  closest fit.)

Map `Origin` → `lat`/`lon` (find-site coordinates). Common documentary provenances:

| Origin                                   | lat      | lon     |
|------------------------------------------|----------|---------|
| Oxyrhynchus (el-Bahnasa)                 | 28.5383  | 30.6765 |
| Soknopaiu Nesos (Dimeh), Fayum           | 29.5377  | 30.6856 |
| Tebtynis (Umm el-Baragat), Fayum         | 29.1119  | 30.7444 |
| Karanis (Kom Aushim), Fayum              | 29.5186  | 30.9036 |
| Arsinoiton Polis / Krokodilopolis (Fayum)| 29.3084  | 30.8428 |
| Philadelphia, Fayum                      | 29.4500  | 31.1500 |
| Theadelphia (Batn el-Harit), Fayum       | 29.4333  | 30.5500 |
| Hermopolis (el-Ashmunein)                | 27.7820  | 30.8020 |
| Antinoopolis (Sheikh Ibada)              | 27.8126  | 30.8783 |
| Memphis                                  | 29.8444  | 31.2506 |
| Thebes / Hermonthis (Theban ostraca)     | 25.7188  | 32.6573 |
| Syene / Elephantine (Aswan)              | 24.0889  | 32.8997 |

For an origin not listed, look up the modern site's coordinates; if it recurs,
add it to `static/data/custom_locations.json` too.

---

## Step 5 — Write the manuscript .txt

Documentary papyri have **no book/chapter:verse**, so use line numbers. Filename =
a slug of the citation (e.g. `bgu_1_2.txt`).

```
[META]
id:       BGU 1.2
label:    BGU 1.2
name:     Petition to the strategos about crop damage   # short human title
genre:    contracts            # or receipts / letters
date:     209 CE               # normalise the HGV date
language: Greek (Koiné)
found:    Soknopaiu Nesos, Fayum, Egypt
held:     Staatliche Museen zu Berlin
shelf:    Berlin, Staatliche Museen P. 6956   # Inv. no. — shown in the sidebar
content:  Petition to the strategos about crop damage   # one-line summary
tm:       8961
source:   https://papyri.info/ddbdp/bgu;1;2
lat:      29.5377
lon:      30.6856

[GREEK]
r.1   Ἀπολλοφάνι [τ]ῷ καὶ Σαραπάμμωνι στρ(ατηγῷ) Ἀρσι(νοΐτου) Ἡρ(ακλείδου)
r.2   μ[ε]ρίδος
...

[TRANSLATION]
1   To Apollophanes also called Sarapammon, strategos of the Herakleides
2   division of the Arsinoite nome,
...
```

- `[GREEK]` lines use `r.N` markers (the existing parser requires `r.`/`v.`).
- `[TRANSLATION]` lines are keyed by the **same line numbers** so the diglot
  columns align. (A `FOLIO Recto/Verso` header is allowed in BOTH sections and
  renders as a side-break header — include it only if the source distinguishes sides.)
- Polytonic Greek is fine — the app renders it; nomina-sacra/lacuna notation works as
  for NT papyri.

---

## Step 6 — Translate

Translate the Greek **literally and faithfully to what this papyrus actually says**
(the project standard — not a paraphrase). Keep documentary formulae recognisable
("I, NN, acknowledge that I have received…", "in the consulship of…", regnal-year
dating formulae). End where the papyrus breaks off; mark lost stretches with `…`.

---

## Step 7 — Report

```
✅ Scraped BGU 1.2  →  manuscripts/bgu_1_2.txt
   Genre:    contracts (petition)
   Date:     209 CE
   Origin:   Soknopaiu Nesos, Fayum  (lat 29.5377, lon 30.6856)
   TM:       8961
   Lines:    21 (apparatus trimmed)
```

Then verify it parses: load `http://localhost:5000/api/manuscripts` (or restart the
app) and confirm the new entry appears under its genre with Greek + translation.

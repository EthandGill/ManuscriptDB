# ManuscriptDB — Continuous Manuscript-Onboarding Workflow

A self-contained playbook for bulk-uploading ancient papyri into **ManuscriptDB**
(`C:\ManuscriptDB`, a Flask app at `http://localhost:5000`). Paste this into Cowork
to run a repeatable, batch-by-batch onboarding loop. It encodes the exact process
proven over a long working session that grew the collection from **134 → 408
manuscripts** with **0 parse errors**.

---

## 0. Current state (snapshot)

| Genre | Count | Source |
|---|---|---|
| New Testament | 134 (P1–P141) | NTVMR (Münster) API |
| Receipts | 221 | papyri.info — mostly **O.Wilck. 1–260** (Syene/Elephantine tax ostraca) + BGU |
| Contracts | 6 | papyri.info — BGU 1/3, P.Oxy 2, BGU 4 (loan, lease, sale, marriage) |
| Letters | 47 | papyri.info — **P.Mich VIII** (34, Tiberianus/Terentianus archive) + BGU 3 (13) |
| **Total** | **408** | 0 parse errors |

**Pending (already scraped, zero re-scrape cost):**
`_PENDING_scraped_p.oxy1.101_bgu4.1149.json` — P.Oxy 1.101 lease + BGU 4.1149 loan, awaiting build.

---

## 1. Two pipelines

| | NT papyri | Documentary papyri (receipts/contracts/letters) |
|---|---|---|
| Source | NTVMR (Münster) API | papyri.info / DDbDP via **Firecrawl** |
| Skill | `grab-manuscript` | `scrape-manuscript` |
| Why Firecrawl | n/a | papyri.info hides behind an "Anubis" JS bot-gate; Firecrawl renders JS and clears it |
| Genre | `new-testament` | `receipts` \| `contracts` \| `letters` |
| Greek refs | `r.N`/`v.N`, verse-keyed translation | `r.N` line numbers, **line-keyed** translation |

This playbook is about the **documentary pipeline** (the scalable one). NT import is
covered in `CLAUDE.md`.

---

## 2. One-time setup

```
pip install firecrawl-py truststore
# set the key in the shell (NEVER hardcode it in a committed file):
PowerShell:  $env:FIRECRAWL_API_KEY = "fc-..."
```

**Machine gotcha (critical):** this PC does TLS inspection, so Python's certifi
bundle rejects `api.firecrawl.dev` (`CERTIFICATE_VERIFY_FAILED`). Every script
calls `truststore.inject_into_ssl()` first — that trusts the Windows cert store
(verification stays ON). Also run scrape commands **outside the sandbox** if you
hit a TLS error in-sandbox.

**Credits:** check balance any time —
`GET https://api.firecrawl.dev/v1/team/credit-usage` (Bearer key) returns
`remaining_credits` + `billing_period_end`. ~1 credit per scraped page.

---

## 3. The repeatable batch loop

Each batch = **one DDbDP series-range**. The cycle:

```
SWEEP (scrape ~50 ids, save JSON)  →  CLASSIFY (by Subjects keyword)
   →  PICK well-preserved items  →  TRANSLATE (faithful, line-aligned)
   →  BUILD (.txt via script, asserting line counts)  →  VERIFY (0 parse errors)
   →  CHECKPOINT (report tally)  →  next range
```

### 3a. SWEEP — scrape a range to JSON
Scrape `papyri.info/ddbdp/<id>` for each id; the page yields **metadata + Greek
transcription**. Save everything to a JSON so a batch never needs re-scraping.
Key fields to pull per record:
- `tm` — Trismegistos number (`trismegistos.org/text/(\d+)`)
- `subjects` — German HGV genre keyword (the classifier; see 3b)
- `shelf` — the museum inventory mark (`Inv. no.` row) → **shows in sidebar**
- `origin` / `Provenance`, `date`
- `greek` — transcription lines (keep only lines containing Greek glyphs)

Use **per-id retry with backoff** — DNS/network blips (`getaddrinfo failed`) are
transient; 3–4 retries clears them. (See the `_sweep.py` template the session used.)

### 3b. CLASSIFY — by the `Subjects` keyword (German)
| Keyword | Genre | Greek cue |
|---|---|---|
| `Quittung` | receipts | `διέγραψεν`/`ἔσχον`/`ἀπέχω` ("paid"/"I have received") |
| `Vertrag`, `Kauf`, `Darlehen`, `Pacht`, `Ehe` | contracts | `ὁμολογῶ`, `ἐμίσθωσεν`, `συγχωροῦσιν` |
| `Brief` (privat/amtlich) | letters | `χαίρειν` greeting, `ἐρρῶσθαί σε εὔχομαι` |
| `Eingabe`/`Petition`, `Abrechnung`, `Liste` | (no genre yet — skip or ask) | |

Skip records with **0 Greek glyphs** (Latin texts, or image-only/unpublished).

### 3c. CLEAN the Greek (papyri.info → ManuscriptDB notation)
- `\[ ... \]` → `[ ... ]` (editorial restoration / lacuna)
- strip the every-5 line-number digit merged onto a word (`5Ταμείων` → `Ταμείων`)
- drop apparatus & commentary lines (they trail the text). Filter a line if it
  starts with `.`/`-`, or contains: `l.`, `BL `, `prev. ed`, `O.Wilck`, `P.Mich`,
  `P.Oxy`, `#`, `Traces`, `→`, `Z. `, `APF`, `ZPE`, `corr.`, `papyrus`, `cf.`
- remove `⟦deletions⟧`, `\interlinear/` slashes, `((editorial notes))`, `~~~`, `vac.`/`ca.?` markers
- nomina sacra (rare in documents) → `{...}`

### 3d. TRANSLATE — faithfully, line-aligned
- Translate the **actual Greek of THIS papyrus** (word order, tense, variants,
  vulgar spellings) — NOT a smooth standard rendering.
- **One English line per Greek `r.N` line** so the diglot columns align.
- Stop where the papyrus breaks; mark lost stretches `[...]` / `…`.
- Keep documentary formulae recognizable ("X paid for the poll-tax of year N of
  Emperor", "I, NN, acknowledge…", regnal-year dating).
- Leave the `[GREEK]` untouched; **flag** suspected transcription errors separately.

### 3e. BUILD — write `.txt` with a script that asserts line counts
The proven pattern: a build script with three dicts (`NLINES`, metadata, `TRANS`),
take `raw_greek[:NLINES]` (apparatus trails, so the first N lines are the text),
pair with the `TRANS` list, and **error out on any `len(greek) != len(trans)`
mismatch**. This caught every alignment bug instantly. `.txt` skeleton:

```
[META]
id:       O.Wilck. 3          # publication citation = id/label
label:    O.Wilck. 3
name:     Tax receipt — poll-tax (laographia)
genre:    receipts            # receipts | contracts | letters
date:     19 CE
language: Greek (Koiné)
found:    Syene / Elephantine (Aswan), Egypt
held:     (see shelf)
shelf:    Leiden, National Museum of Antiquities B.A. 200   # Inv. no. → sidebar
content:  Ostracon tax receipt — poll-tax, Syene/Elephantine
tm:       24732
source:   https://papyri.info/ddbdp/o.wilck;;3
lat:      24.0889
lon:      32.8997

[GREEK]
r.1   διαγεγράφ(ηκε)
r.2   Ζμηύθιος Παχνούβιος
...

[TRANSLATION]
1   Has paid:
2   Zmeuthis son of Pachnoubis,
...
```
- Filename = a slug of the id (`o_wilck_3.txt`, `bgu_3_697.txt`, `p_mich_8_476.txt`).
- Add `FOLIO Recto/Verso` headers in BOTH `[GREEK]` and `[TRANSLATION]` when the
  source distinguishes sides (the parser renders them as a break in each column).
- Provenance → lat/lon (find-site, or place-of-writing for letters). Common coords:
  Oxyrhynchus 28.5383/30.6765 · Soknopaiou Nesos 29.5377/30.6856 · Karanis
  29.5186/30.9036 · Arsinoite 29.3084/30.8428 · Syene/Elephantine 24.0889/32.8997 ·
  Alexandria 31.2001/29.9187 · Rome 41.8931/12.4828 · Bostra 32.5185/36.4817.

### 3f. VERIFY
Fetch `http://localhost:5000/api/manuscripts` (gzipped) and assert
**`parse errors == 0`**; print the per-genre tally. The browser/`fetch` path is
reliable; raw `curl` of the uncompressed feed occasionally truncates (dev-server
quirk) — use `--compressed` and retry, or check via the browser.

### 3g. CHECKPOINT
Report: total manuscripts, per-genre counts, this batch's range, credits used /
remaining. Then move to the next range.

---

## 4. Source map (where the manuscripts are)

| Series (DDbDP id form) | What it is | Yield |
|---|---|---|
| `o.wilck;;N` (1–1624) | Wilcken ostraca — **Syene/Elephantine tax receipts** | ~80% receipts; the deepest receipt well (only 1–260 done) |
| `o.fay;;N` | Fayum ostraca | receipts |
| `bgu;1;N`, `bgu;3;N` | Berlin papyri (Soknopaiou/Arsinoite) | mixed — receipts, letters, a few contracts |
| `bgu;3;800–849` | BGU 3 | private **letters** dense |
| `bgu;4;N` (~1000s) | Alexandria | **contracts** dense (marriage, loan, sale) |
| `p.oxy;V;N` | Oxyrhynchus | **contracts** dense (lease, sale, loan); also letters |
| `p.mich;8;N` (464–514) | Karanis — Tiberianus/Terentianus archive | **letters** (Greek ones done; Latin ones skipped) |
| `cpr;1;N`, `p.cair.masp` | Byzantine | contracts |

**Continue-from queue:**
- Receipts: `o.wilck;;261+`
- Contracts: `p.oxy` and `bgu;4` ranges (probe a few first to find dense blocks)
- Letters: Heroninos archive, Zenon archive, more BGU/P.Oxy
- Pending build (free): P.Oxy 1.101 lease + BGU 4.1149 loan

---

## 5. Designing the continuous Cowork workflow

**Batch size:** ~50 scrapes/range. Receipts are formulaic (translate ~40/turn).
Letters are real prose (~10–15/turn). Don't promise more than you can translate at
quality in one turn — the **translation is the bottleneck, not credits**.

**Quality bar (non-negotiable):** faithful per-line translation; build script
asserts line counts; verify 0 parse errors every batch; never edit `[GREEK]` (flag
issues instead). Skip heavily-fragmentary items (note them) rather than guess.

**Statefulness / resumption:**
- **Preserve scrape JSON** for anything not yet built (rename to `_PENDING_*.json`)
  so resuming costs zero credits. (The session lost ~30 letters' data twice by
  deleting JSON too early — don't.)
- Keep a simple queue of ranges done / next (like the `import_queue.txt` +
  `DONE`-line convention in `CLAUDE.md` §"Continuous bulk import").
- Clean up only the throwaway build/sweep scripts each turn; keep pending data.

**Autonomy:** to run without per-step approval, allowlist in `.claude/settings.json`:
`Bash(python *)`, `Read(*)`, `Write(manuscripts/*)`, and the `curl` verify command;
or Shift+Tab to auto-accept. For unattended runs, schedule a headless
`claude -p "sweep o.wilck;;261-310 per WORKFLOW-manuscript-onboarding.md, build the
receipts, verify"` from `C:\ManuscriptDB`.

**Suggested loop prompt for Cowork:**
> Following `WORKFLOW-manuscript-onboarding.md`: sweep the next range in the
> continue-from queue, classify by `Subjects`, build the well-preserved items with
> faithful line-aligned translations (build script asserts line counts), verify the
> API shows 0 parse errors, report the per-genre tally and credits remaining, then
> continue to the next range without asking. Preserve scrape JSON for anything not
> built. Stop when I say or credits run low.

---

## 6. Frontend features already wired (so onboarded data "just works")

- **Genres**: receipts/contracts/letters render as a flat list showing
  `label · shelf · date` — so the **shelf number appears in the sidebar** (and search).
- **Green orbs**: documentary papyri glow **green** on the map (biblical = red);
  expanding a documentary genre lights up its find-sites.
- **Recto/verso breaks** show in both Greek and English columns of the reader.
- **Gzip + fetch-retry** make the (now large) `/api/manuscripts` feed load reliably.

---

## 7. House rules learned this session

- Münster/NTVMR has **only NT** manuscripts — no receipts/contracts. Use
  papyri.info for documentary texts.
- Trismegistos is **metadata only** (no transcriptions); it links to papyri.info,
  which has the actual Greek + a TM cross-reference.
- The **API key was pasted in chat** → rotate it; always read from
  `FIRECRAWL_API_KEY` env var.
- Latin papyri (e.g. several P.Mich VIII Terentianus letters) are out of scope for
  the Greek translation pipeline — skip with a note.

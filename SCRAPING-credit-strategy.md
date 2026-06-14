# Scraping & Firecrawl-Credit Strategy

How to scrape aggressively without wasting Firecrawl credits, using the
**producer/consumer split**: a plain-Python terminal scrapes (spends credits →
banks JSON), and a separate Claude terminal translates (spends zero credits).

Pricing assumption: **~1 credit per page (per DDbDP id)**. Check your live balance:
`GET https://api.firecrawl.dev/v1/team/credit-usage` (Bearer key) →
`remaining_credits` + `billing_period_end`.

---

## 1. The two-terminal architecture

| | Terminal A — SCRAPER | Terminal B — TRANSLATOR |
|---|---|---|
| App | plain PowerShell (no Claude) | Claude Code |
| Spends | Firecrawl credits | Claude usage only |
| Reads | `sweep_ranges.txt` | `_sweep_*.json` |
| Writes | `_sweep_<range>.json` | `manuscripts/*.txt` |
| Git | **never touches git** | **only committer** |
| Command | `python parallel_sweep.py 4` | the build-from-pending loop |

They never collide because they write to **different files**. The only shared
resource is git, and only Terminal B uses it. `_sweep_*.json` / `_PENDING_*.json`
are git-ignored so B's commits never grab A's half-written scratch.

**Golden rule:** credits are spent only in Terminal A. Terminal B (translation)
must never re-scrape — everything it needs is already in the JSON (see §4).

---

## 2. The ten credit-conservation rules

1. **Probe before you commit a big range.** Sweep 2–3 ids of a new series first
   (`python _sweep.py o.fay;;51-53`) and look at the JSON: how many have non-empty
   `greek`? what `subjects`? If a block is sparse, Latin-only, or image-only,
   a 50-id sweep wastes ~50 credits. Probe = ~3 credits to save ~47.

2. **Never scrape the same id twice.** Overlapping ranges = double-charged.
   `parallel_sweep.py` auto-skips any range whose `_sweep_*.json` already exists,
   and `sweep_ranges.txt` is the single source of truth — keep its lines disjoint.

3. **Preserve every JSON forever.** The scrape is the only thing credits buy. Once
   `_sweep_<range>.json` exists, that range is paid for permanently. Keep these
   files on disk (they're git-ignored, not deleted). Re-running never re-charges.

4. **Translate from JSON, never re-fetch.** The build/translate step reads the
   saved JSON only. If you ever find yourself scraping again to translate, stop —
   that's paying twice. (`_sweep.py` already captures everything needed: §4.)

5. **Target dense wells first.** Best yield-per-credit is the formulaic series you
   know are dense — Wilcken ostraca receipts (`o.wilck`, runs to ~1624). Exhaust
   the sure things before probing thin/scattered series.

6. **Mind concurrency, not credits, when picking workers.** Extra workers don't
   cost extra credits, but exceeding your plan's concurrency limit causes 429s and
   wasted retries (slower, not pricier). Start `parallel_sweep.py 4`; raise only if
   clean.

7. **Batch the budget.** 5,000 credits ≈ ~5,000 ids. Decide the split up front,
   e.g. 3,000 receipts / 1,000 contracts / 1,000 letters+petitions, and fill
   `sweep_ranges.txt` accordingly so you don't drift into low-value blocks.

8. **Stop-loss on a bad series.** If a swept range comes back mostly empty
   `greek`, don't continue that series — note it and move on. One 50-id dud is
   cheap; ten in a row is 500 credits gone.

9. **Watch the balance between batches.** Glance at `remaining_credits` after each
   `parallel_sweep.py` run so a runaway range list can't silently drain the month.

10. **Scrape ahead of translation, not in lockstep.** Translation is the real
    bottleneck, so it's fine (good, even) to bank far more JSON than you've
    translated. The JSON waits for free; credits don't refund.

---

## 3. The scrape blitz, step by step (Terminal A)

```powershell
cd C:\ManuscriptDB
# key must be set in THIS window:
$env:FIRECRAWL_API_KEY = "fc-..."        # or rely on the persistent user var
# edit sweep_ranges.txt to the ranges you want, then:
python parallel_sweep.py 4
```
- Re-run any time; finished ranges are skipped, failed ones retried.
- Output: one `_sweep_<range>.json` per line in `sweep_ranges.txt`.
- This window never needs Claude and never touches git.

---

## 4. Why translation never needs to re-scrape

`_sweep.py` already extracts, per id: `tm`, `subjects` (the genre keyword),
`shelf` (sidebar inventory mark), `origin`, `date`, and the `greek` transcription
lines. That's everything the build step and the translation need. So once a range
is in `_sweep_*.json`, Terminal B can classify, clean, translate, and build the
`.txt` entirely offline — zero further credits. If a field is missing for a
specific high-value text, fix it by hand rather than re-sweeping the whole range.

---

## 5. Quick reference

- Probe a series:        `python _sweep.py <series>;;<a>-<a+2>`
- Bank a backlog:        `python parallel_sweep.py 4`
- Check credits:         `GET https://api.firecrawl.dev/v1/team/credit-usage`
- Ranges live in:        `sweep_ranges.txt`
- Scratch (git-ignored): `_sweep_*.json`, `_PENDING_*.json`
- Deepest well:          `o.wilck` receipts (to ~1624)

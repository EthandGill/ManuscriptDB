# Translation Workflow (Terminal B — the consumer)

This is the second half of the producer/consumer split. **Terminal A** scrapes
and banks `_sweep_*.json` (see `SCRAPING-credit-strategy.md`). **Terminal B**
(this one, Claude Code) turns that JSON into finished, translated
`manuscripts/*.txt` and pushes them live — spending **zero Firecrawl credits**.

Translation is the real bottleneck, so this terminal is where you spend your
effort. `build_from_sweep.py` does all the mechanical, error-prone parts; you
only supply the actual English.

---

## The loop (per `_sweep_*.json`)

```
scaffold → (fill translations) → assemble (asserts line counts) → commit+push → next
```

1. **Scaffold** — classify, clean, number, pre-fill metadata:
   ```
   python build_from_sweep.py scaffold _sweep_o.wilck_561-610.json
   ```
   Produces `_translate_o.wilck_561-610.txt`: one block per well-preserved
   record with the cleaned `[GREEK]` numbered `r.1..r.N` and a blank
   `[TRANSLATION]` line per Greek line. Sparse/Latin/unclassified records are
   listed as `# SKIPPED` (no work needed).

2. **Fill it** — for each record, edit the scaffold in place:
   - Replace `TODO` in `name:` (a short title, e.g. "Tax receipt — poll-tax")
     and `content:` (one-line summary).
   - Type one English line per Greek line, after each number. **Translate the
     actual Greek shown**, line-aligned. Leave a record's translation blank to
     drop it.

3. **Assemble** — safety-checked write:
   ```
   python build_from_sweep.py assemble _translate_o.wilck_561-610.txt
   ```
   For each record it asserts `#Greek == #translation` and that `name:`/`content:`
   are filled, then writes `manuscripts/<slug>.txt`. Any mismatch aborts that
   record with a clear message (exit 1) — this is the check that catches every
   alignment bug. Fix and re-run.

4. **Verify** — confirm the app still parses everything cleanly:
   - Locally: `python app.py` then load `http://localhost:5000/api/manuscripts`
     and check there are **0 parse errors**, OR after deploy check the live feed.

5. **Commit + push** (this is the ONLY terminal that touches git):
   ```
   git add -A && git commit -m "Onboard o.wilck;;561-610: +N receipts" && git push
   ```
   Railway auto-deploys. One commit per `_sweep` file keeps the live site fresh
   without flooding deploys. (`_sweep_*.json`, `_translate_*.txt`, `_PENDING_*.json`
   are git-ignored, so only the real `manuscripts/*.txt` get committed.)

6. **Next file.** Repeat for the next `_sweep_*.json`.

---

## Quality bar (non-negotiable)

- **Faithful, line-aligned.** Translate this papyrus's actual Greek — its word
  order, tense, vulgar spellings, variants — not a smooth standard rendering.
  One English line per `r.N` so the diglot columns line up.
- **Never edit `[GREEK]`.** If you spot a transcription error, flag it in a note;
  don't alter the Greek.
- **Skip, don't guess.** Heavily-lacunose items: leave the translation blank
  (the assembler drops them) rather than inventing text. Mark gaps with `…`.
- **Keep the documentary formulae recognizable**: "X has paid for the poll-tax of
  year N", "I, NN, acknowledge…", regnal-year dating.

## Throughput (pace by genre)

Translation quality is the limiter, not credits or scripting. Realistic per turn:
- **Receipts** (formulaic): ~40.
- **Contracts / petitions / documents**: ~15–25.
- **Letters** (real prose): ~10–15.
It's fine for one `_sweep` file to take several turns. Don't mark a file done
until its well-preserved records are built and verified.

## Classification & coords (handled, but extensible)

`build_from_sweep.py` maps the German `Subjects` keyword to a genre
(`Quittung`→receipts, `Vertrag/Kauf/Darlehen/Pacht/Ehe`→contracts, `Brief`→letters,
`Eingabe/Petition`→petitions, `Abrechnung/Liste/Deklaration`→documents) and maps
known find-sites to lat/lon. If a record is skipped as "unclassified", add a rule
to `GENRE_RULES`; if `lat/lon` come out blank, add the origin to `COORDS` (or let
`check_city_nodes.py` flag the orphan later).

---

## Terminal B kickoff prompt (hands-off)

Paste once; it runs the loop on its own. (Shift+Tab to auto-accept first.)

> Process every `_sweep_*.json` in this folder that doesn't yet have its records
> in `manuscripts/`. For each file, following WORKFLOW-translation.md:
> 1. `python build_from_sweep.py scaffold <file>`.
> 2. Open the generated `_translate_*.txt` and fill it: a short `name:` and
>    `content:` per record, and one faithful, line-aligned English line per Greek
>    line (translate the actual Greek; leave blank to drop fragmentary records).
> 3. `python build_from_sweep.py assemble <_translate_file>`; if it reports any
>    `[ERR ]`, fix the alignment and re-run until clean.
> 4. Commit and push: `git add -A && git commit -m "Onboard <range>: +N <genre>"
>    && git push`.
> 5. Continue to the next `_sweep` file without asking me. Pace by quality per the
>    throughput guide; stop when there are no un-built `_sweep` files left.

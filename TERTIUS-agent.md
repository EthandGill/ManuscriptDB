# TERTIUS — the translating agent (build spec)

> Paste/point Claude Code at this file from `C:\ManuscriptDB`:
> **"Read TERTIUS-agent.md and build it, step by step. Ask me before anything destructive."**

*Tertius* is named after the scribe of Romans (Rom 16:22, "I Tertius, who wrote
this letter…"). He is a background agent that works through every untranslated
manuscript in `manuscripts/`, translates it, and shows his progress in two places:

1. **On my desktop** — a small floating pop-up I can drag anywhere and click to expand.
2. **On the live website** — a badge in the top corner:
   **"Tertius has translated 30 of 100 sources"**.

---

## 0. Ground rules for Claude Code

- **Reuse, don't rebuild.** The translation engine already exists:
  `translate_mss_max.py` (Max-plan, `claude -p`, batched, resumable, sleeps
  through usage windows, commits+pushes every 25) built on
  `translate_mss_api.py` (`SYSTEM` prompt, `parse_txt`, `needs_translation`,
  `parse_reply`, `write_translation`, `git_commit`) and `_claude_max.py`.
  Tertius is a **wrapper** around these — import them, don't copy them.
- **Never edit `[GREEK]`.** Only `[TRANSLATION]` sections are written.
- **Keep everything resumable.** Kill Tertius at any point, restart, and he
  picks up where he left off (the existing "any filled slot = translated" rule).
- **No new paid services, no API key billing.** Max plan only, like
  `translate_mss_max.py`.
- **Performance:** `manuscripts/` holds ~60,000 files. Never rescan the whole
  folder on every tick or on every web request. Scan once at startup, then
  update counts incrementally as each manuscript is written.
- Windows machine, Python 3, stdlib preferred (Tkinter for the desktop UI).

---

## 1. Requirements (from Ethan)

| # | Requirement | Where it shows |
|---|---|---|
| 1 | **Which manuscript** Tertius is working on right now | Desktop pop-up (and website, as of last push) |
| 2 | **How many translated** — shown as a fraction, e.g. `30 / 100` | Desktop + website |
| 3 | **How many left** — shown as a fraction, e.g. `70 / 100` | Desktop |
| 4 | Translate each manuscript and **reflect its lacunae in the blue bracketed style the site already uses** | `manuscripts/*.txt` → rendered on site |
| 5 | Named **Tertius**; live badge in the top corner of the website: *"Tertius has translated 30 of 100 sources"* | Website |

---

## 2. Architecture

```
tertius.py  (worker — the agent)
   │  imports translate_mss_api / _claude_max / translate_mss_max helpers
   │  translates batch → write_translation() → validate lacunae
   │
   ├─► tertius_status.json          (local, every step; git-ignored)
   │        read by ──► tertius_widget.py  (desktop pop-up, Tkinter)
   │
   └─► static/data/tertius_progress.json   (committed with each push of 25)
            served by Railway ──► badge in templates/index.html (top-right)
```

Why two status files: the desktop needs second-by-second updates, but the live
site only changes when a commit is pushed and Railway redeploys. The local file
is git-ignored; the public file is small and committed with each batch.

---

## 3. The worker — `tertius.py`

CLI (mirror `translate_mss_max.py`'s flags and pass them through):

```
py tertius.py                 # run the full backlog, show the pop-up
py tertius.py --limit 10      # smoke test
py tertius.py --no-widget     # headless (e.g. Task Scheduler)
py tertius.py --status        # print the fractions and exit (no tokens)
py tertius.py --selftest      # offline checks
```

Behaviour:

1. **Startup scan (once):** walk `manuscripts/*.txt` with `parse_txt`, and
   count:
   - `total` = manuscripts Tertius is responsible for (flat papyri with Greek
     lines — the same set `needs_translation` judges; multi-book NT manuscripts
     using `[GREEK:Book]` are out of scope, as today).
   - `translated` = of those, how many already have a filled translation.
   - `remaining` = `total - translated`.
   Cache the result to `tertius_index.json` (path → translated? + mtime) so
   later startups only re-parse changed files.
2. **Launch the pop-up** (`subprocess.Popen` of `tertius_widget.py`, unless
   `--no-widget`). The pop-up appears only while Tertius is running.
3. **Loop** using the same batching as `translate_mss_max.run()`. Before each
   batch, write status `state: "translating"` with `current` = the manuscript
   ids/names in the batch. After each manuscript is written and validated
   (§5): increment `translated`, append it to `recent`, rewrite status.
4. **Every 25 (the existing `--commit-every`):** write
   `static/data/tertius_progress.json`, `git add` it **together with**
   `manuscripts/`, commit `"Tertius: translated N of M sources"`, push.
   (Extend `git_commit` to accept extra paths; don't fork it.)
5. **Usage-window sleep:** when `_claude_max` is waiting for the window to reset,
   set `state: "resting"` with `resume_at` so the pop-up can say
   *"Tertius is resting — resumes 02:40"*.
6. **Errors:** keep logging to `_translate_errors.log`; also put the last error
   in status (`last_error`) and skip on, as now.
7. **Finish/exit:** `state: "done"` or `"stopped"`, final push, then signal
   the pop-up to close (it fades out after ~5 s).
8. **Stop/pause control:** the worker checks for a `tertius.control` file each
   loop (`pause` / `resume` / `stop`) so the pop-up buttons can steer him. Stop
   must finish the manuscript in hand and push before exiting; never leave a
   half-written `.txt`.

### `tertius_status.json` (local, git-ignored)

```json
{
  "agent": "Tertius",
  "state": "translating",            // translating | resting | paused | done | stopped | error
  "current": [{"id": "BGU 5.1210", "file": "bgu_5_1210.txt",
               "name": "Documentary papyrus — Theadelphia (Arsinoites)",
               "lines": 12}],
  "translated": 30, "remaining": 70, "total": 100,
  "session_done": 7,
  "recent": [{"id": "P.Oxy 6.984", "at": "2026-10-07T21:04:11-04:00"}],
  "last_line": {"greek": "το[ῦ γ]νώμον[ος], ὃν ὁ θεὸς Σεβαστὸς…",
                "english": "Of the [Gn]omon, which the god Augustus…"},
  "resume_at": null,
  "last_error": null,
  "heartbeat": "2026-10-07T21:04:12-04:00"
}
```

Write it atomically (write `*.tmp`, then `os.replace`) so the pop-up never
reads half a file.

---

## 4. The desktop pop-up — `tertius_widget.py`

Tkinter, frameless (`overrideredirect(True)`), always on top, polls
`tertius_status.json` every 1 s.

**Collapsed (default)**: a small rounded pill, ~260×56 px, bottom-right on first run.

```
 ✒  Tertius · translating      30 / 100
```

**Expanded (on click)**: ~380×300 px card:

```
 ✒  TERTIUS                                   [–] [⏸] [■]
 ───────────────────────────────────────────────
 Now translating
   BGU 5.1210 — Documentary papyrus, Theadelphia
   (+7 more in this batch)

 Translated      30 / 100   ████████░░░░░░░░░░░░
 Left to go      70 / 100

 Latest line
   το[ῦ γ]νώμον[ος], ὃν ὁ θεὸς Σεβαστὸς…
   Of the [Gn]omon, which the god Augustus…
                                  ← [ ] and … in lacuna blue

 Recently finished: P.Oxy 6.984 · P.Tebt 1.62 · BGU 9.1898
```

Must-haves:
- **Draggable** anywhere (mouse press/drag on the body); click without drag
  toggles collapsed ↔ expanded. Remember position + state in
  `tertius_widget.json` (wrap in try/except; fall back to defaults).
- **Fractions, not just counts**: show `translated / total` and
  `remaining / total`, exactly as above.
- **Lacuna colouring** in the "Latest line" preview: use a Tkinter `Text`
  widget with a tag coloured **`#607888`** (the site's `.ms-supplied` colour)
  applied to every `[...]` and `…` run, same regex the site uses:
  `/(\[[^\]]*\]|…+)/`.
- States: *translating* (subtle pulsing quill), *resting — resumes HH:MM*,
  *paused*, *done — 100 / 100 🎉*, *error* (red dot + last error on hover).
- Buttons: minimise to pill, pause/resume, stop (writes `tertius.control`).
- **Visible only while working**: if the heartbeat is older than 2 minutes or
  state is `done`/`stopped`, fade out and exit.
- Styling: match the site's parchment/dark palette from `static/style.css`
  (read it for the real colours) and use a Greek-capable font (e.g. "Gentium
  Plus" if installed, else "Segoe UI").
- Optional: a `Tertius.bat` / desktop shortcut that runs `pythonw tertius.py`
  so no console window is left open.

---

## 5. Translation + lacunae (requirement #4)

The site already colours lacunae blue: in `static/script.js` (`fmtLacuna`,
~line 2344) any `[...]` or `…` in a translation line is wrapped in
`<span class="ms-supplied">`, and `.ms-supplied { color: #607888; }` in
`style.css`. **So the job is to get the brackets right in the English;
no new markup needed in the `.txt` files.**

Rules (already in `translate_mss_api.SYSTEM`, keep them and tighten):
- One English line per Greek `r.N` line, line-aligned (asserted by `parse_reply`).
- Text the editor **restored** in the Greek (`[...]`) → the corresponding English
  words go **inside `[ ]`**. Partial-word restorations (`το[ῦ γ]νώμον[ος]`)
  → bracket the English word that depends on the restoration (`[Gn]omon` or
  `[of the Gnomon]`), don't drop the brackets.
- Lost/illegible stretches → `…`. Never invent text to fill a gap.
- Nomina sacra `{...}` are a Greek-side feature; translate normally.

**Add a lacuna check** in `tertius.py` after `parse_reply`, before `write_translation`:
- If a Greek line contains `[` but its English line contains neither `[` nor `…`,
  flag it.
- If a Greek line is entirely bracketed/gap and the English is a fluent full
  sentence, flag it.
- Flagged manuscripts: retry once with an extra instruction line
  ("Line N restores text in brackets; mark the English for it with [ ]"). If it
  still fails, write the translation anyway, but add a
  `# tertius: lacuna-check failed lines 3,8` comment under `[TRANSLATION]` and log it,
  so I can review them later with `py tertius.py --review`.

---

## 6. The live website badge (requirement #5)

**Data:** `static/data/tertius_progress.json` (committed by Tertius every push):

```json
{ "translated": 30, "total": 100,
  "current": "BGU 5.1210", "state": "translating",
  "updated": "2026-10-07T21:05:00-04:00" }
```

**Endpoint:** add `GET /api/tertius` in `app.py` that returns that file (read
once and cache with mtime check; **don't** rescan `manuscripts/` per request).

**Badge** in `templates/index.html` + `static/style.css` + `static/script.js`:
- Fixed in the **top-right corner**, above the map, small and unobtrusive;
  must not cover the existing account/menu controls (check `index.html` and
  shift if needed).
- Text: **"Tertius has translated 30 of 100 sources"** (numbers with thousands
  separators, e.g. "12,480 of 59,624").
- A thin progress bar underneath, filled in the lacuna blue `#607888`.
- Tooltip/click: "Currently working on BGU 5.1210 · updated 4 min ago".
- If `state` is `done`: "Tertius has translated all 59,624 sources ✓".
- Poll `/api/tertius` every 60 s; hide the badge silently if the request fails.
- Works on mobile (shrinks to "Tertius · 30/100").

Note: the website only knows what's been **pushed**, so it lags the desktop
pop-up by up to 25 manuscripts. That's expected.

---

## 7. Housekeeping

- Add to `.gitignore`: `tertius_status.json`, `tertius_index.json`,
  `tertius_widget.json`, `tertius.control`.
  **Do commit** `static/data/tertius_progress.json`.
- Add a short "Tertius" section to `CLAUDE.md` pointing at this file.
- `translate_status.py` should keep working; optionally make it print
  Tertius's fractions too.

---

## 8. Build order (do these one at a time, test each)

1. `tertius.py --status`: startup scan + index cache + fractions. Confirm the
   numbers with me before going further.
2. `tertius_status.json` writer + `tertius_widget.py` running against a **fake**
   status file (no translation yet). Drag, expand, fractions, lacuna colouring.
3. Wire the worker to the real translation loop: `py tertius.py --limit 3 --no-git`.
   Check the 3 `.txt` files by hand, brackets included.
4. Lacuna check + retry + `--review`.
5. `/api/tertius` + website badge; test locally on `python app.py`.
6. Public progress file + git push every 25; check the badge on the live site
   after Railway redeploys.
7. `Tertius.bat` launcher; then the full overnight run.

## 9. Acceptance checklist

- [ ] Pop-up appears when Tertius starts, disappears when he stops.
- [ ] Drag it anywhere; click to expand/collapse; position remembered.
- [ ] Shows current manuscript, `translated / total`, `remaining / total`.
- [ ] Translations line-aligned; restored text in `[ ]`, gaps as `…`; they
      render blue on the site.
- [ ] Live site top-right: "Tertius has translated N of M sources", updating
      after each push.
- [ ] Stop → restart resumes with no duplicates and no half-written files.
- [ ] `[GREEK]` sections untouched (diff check).

## 10. Open questions — ask Ethan before step 1

1. **What counts as a "source" in "N of M"?** All ~60k manuscripts, or only the
   ones that need translating (flat papyri)? Should the epigraphy
   inscriptions be included?
2. Should Tertius also re-check **already-translated** manuscripts for missing
   lacuna brackets, or only do new ones?
3. Model: keep `haiku` (fast, current default) or use a stronger model for
   better handling of lacunose text?

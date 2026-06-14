# START HERE — how to run the onboarding pipelines

Three workflows, plus the files that drive each. Two rules that prevent every
collision:
- **Firecrawl credits are spent only by the papyri scraper (Terminal A).**
- **Only the translation side (Terminal B / Claude Code) ever runs git / push.**

| File | What it's for |
|---|---|
| `SCRAPING-credit-strategy.md` | How to scrape papyri without wasting credits (Terminal A) |
| `sweep_ranges.txt` | The list of DDbDP ranges to scrape — edit this to choose what |
| `parallel_sweep.py` | Runs many scrapes at once → `_sweep_*.json` |
| `WORKFLOW-translation.md` | The Claude-Code loop that turns JSON into manuscripts (Terminal B) |
| `build_from_sweep.py` | Scaffold + line-count-checked assemble used by Terminal B |
| `EPIGRAPHY-plan.md` | Latin epigraphy (CIL) — free download, no credits |
| `edh_ingest.py` | Turns an EDH/LIST dump into the site's epigraphy data |
| `.vscode/tasks.json` | VS Code menu entries for the two terminals |

---

## Workflow 1 — Papyri scraping (Terminal A, no Claude, spends credits)

In VS Code: open `C:\ManuscriptDB`, then **Terminal → Run Task →
"Scrape papyri (Terminal A)"**. Or in any PowerShell:
```powershell
cd C:\ManuscriptDB
echo $env:FIRECRAWL_API_KEY        # must print fc-...  (one-time: pip install firecrawl-py truststore)
python parallel_sweep.py 4
```
Edit `sweep_ranges.txt` first to pick ranges. Output: `_sweep_*.json`. Details and
credit-saving rules: `SCRAPING-credit-strategy.md`.

## Workflow 2 — Translation (Terminal B = Claude Code, no credits)

In VS Code: **Terminal → Run Task → "Translate (Terminal B — Claude Code)"** (or
run `claude`). Press **Shift+Tab** for auto-accept, then paste the kickoff prompt
at the bottom of `WORKFLOW-translation.md`. It loops: scaffold → you/Claude fill
translations → assemble (asserts line counts) → commit + push → next file.

## Workflow 3 — Latin epigraphy (free, 0 credits)

EDH's API is gated, but the corpus is a free download. One-time:
1. Download a dump (EDH GeoJSON from
   `github.com/epigraphic-database-heidelberg/data` → `inscriptions/`, or the
   EDH+EDCS **LIST** set from `zenodo.org/records/10473706`) into `C:\ManuscriptDB\`.
2. In Claude Code, paste the **epigraphy kickoff prompt** from the bottom of
   `EPIGRAPHY-plan.md`. It inspects the dump, builds ~2,000 best-preserved
   inscriptions into `static/epigraphy_data.js`, verifies, and pushes.

Full detail + run commands: `EPIGRAPHY-plan.md`. (Frontend is already wired to
load `epigraphy_data.js`.)

---

## Typical day

1. Terminal A: `python parallel_sweep.py 4` — bank a backlog of `_sweep_*.json`.
2. Terminal B (Claude Code): paste the translation prompt — it builds + pushes
   continuously.
3. Epigraphy is independent and free — run it whenever; it doesn't touch credits.

---
name: check-city-nodes
description: >
  Audits and fixes city-node coverage for the map in the ManuscriptDB project at
  C:\ManuscriptDB. Every manuscript has a find-site (lat/lon); the map snaps each
  to the nearest city within 0.3° (ORBIS cities + static/data/custom_locations.json).
  A find-site with no city in range shows as an unnamed "This site" orb instead of
  a named city. Use this skill whenever new manuscripts have been onboarded and you
  need to keep locations consistent — e.g. "check city nodes", "scan for missing
  city nodes", "make sure every location has a city", "did onboarding add new
  find-sites without a node", "add a city node for <place>", "why is this orb
  unnamed / showing This site". Run it as the last step of any onboarding batch.
---

# Keep map city-nodes consistent

The map renders one **orb** per location. Each manuscript's `(lat, lon)` find-site
is **snapped to the nearest city within 0.3°** (`findSnapCity` in
`static/script.js`). The city list = **ORBIS cities** (`static/data/orbis.json`,
~197, only ~12 in Egypt) **plus** `static/data/custom_locations.json`.

If a find-site has **no city within 0.3°**, the orb falls back to an unnamed
**"This site"** and is keyed `raw:<lat>,<lon>` instead of `city:<lat>,<lon>`.
The goal of this skill: **every find-site snaps to a named city node** (0 orphans).

## Step 1 — Scan

```
python check_city_nodes.py          # exits 1 + lists orphan find-sites if any
python check_city_nodes.py --list   # also prints the full per-city distribution
```

(Use the real interpreter if `python` resolves to the Windows Store stub:
`C:/Users/Ethan/AppData/Local/Python/pythoncore-3.14-64/python.exe`.)

`check_city_nodes.py` (repo root) replicates the frontend's 0.3° snap rule against
ORBIS + `custom_locations.json`, parses every `manuscripts/*.txt` META block for
`lat`/`lon`/`found`, and prints any orphan coordinate cluster like:

```
  (29.4333, 30.4)  x 23  e.g. ['O.Fay. 10', ...]  ::  Euhemeria (Arsinoite nome / Fayum), Egypt
```

If it prints **`ORPHAN: 0`** and **"All find-sites have a city node."**, you're done.

## Step 2 — Add a node per orphan find-site

For each orphan cluster, append an entry to `static/data/custom_locations.json`
**at the exact orphan coordinate** (so the manuscript snaps to it with distance 0,
which beats any nearby node). The schema is a flat JSON array of:

```json
{ "id": "<kebab-slug>", "name": "<City>", "modern": "<modern place>, <country>",
  "lat": <lat>, "lon": <lon> }
```

- Take `name`/`modern` from the orphan's `found:` field (the ancient city, then a
  modern equivalent). Pick the city from the `found:` string, e.g. `Euhemeria`,
  `Theadelphia`, `Apollonopolis Magna` → `Edfu`, `Hermopolis Magna` → `el-Ashmunein`.
- `id` is a lowercase kebab slug of the name (`apollonopolis-magna`).
- `lat`/`lon` must **exactly match** the manuscript coordinate (copy the orphan
  coord). Don't round differently — the snap picks the nearest node, and an
  exact-match node always wins.

### Two different villages sharing one coordinate

If an orphan cluster contains **two distinct places** at the same coordinate
(they were both given the same fallback coord during onboarding, e.g.
`Polydeukia` + `Thraso` at `29.43, 30.45`), don't lump them under one name.
Nudge ONE manuscript's `lat`/`lon` in its `.txt` to a nearby distinct point
(e.g. `29.46, 30.47`) and add a node for **each** place at its own coordinate.
Edit only the `lat:`/`lon:` lines in `manuscripts/<slug>.txt`.

## Step 3 — Re-verify

```
python check_city_nodes.py          # must now print ORPHAN: 0  (exit 0)
```

Then confirm nothing else broke (you only touched JSON + maybe a `lat`/`lon` line):

```
python -c "import os,app; e=[f for f in sorted(os.listdir('manuscripts')) if f.endswith('.txt') and (lambda p: (app.parse_manuscript(os.path.join('manuscripts',p)) and False) or False)(f)]"
```

…or just reload the running app and check the API tally is unchanged with 0 parse
errors (see CLAUDE.md / the onboarding workflow for the curl-retry verify snippet).

## Notes & gotchas

- **0.3° ≈ 33 km.** Tightly-clustered Fayum villages (Euhemeria, Philoteris,
  Polydeukia, Thraso, Theadelphia) all fall within 0.3° of each other, so each
  needs its **own** node at its **own** coordinate to be labelled distinctly;
  an exact-coordinate node always wins the nearest-city tiebreak.
- Custom nodes are **merged into `orbisData.cities`** at load
  (`data.cities = [...data.cities, ...customLocs]`), so they also appear in the
  Ancient-Cities list and as route-planner endpoints. They are **not** in the
  ORBIS road/sea network, so (like the pre-existing custom nodes) they won't be
  routable — that's expected.
- This skill is **data-only** (`custom_locations.json` + occasionally one
  `lat`/`lon` line). It never changes `static/script.js`; the 0.3° rule lives in
  `findSnapCity` and `check_city_nodes.py` mirrors it — keep the two in sync if
  the snap threshold is ever changed.
- Run this **after every onboarding batch** so new find-sites never silently
  become unnamed "This site" orbs.

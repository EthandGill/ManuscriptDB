# Epigraphy city nodes + routes

Many inscriptions plot on the map at their findspot but have **no city node** — they
show as unnamed "This site" orbs and the Route Planner can't route to them. This task
gives every inscription findspot a real, named city node **and** connects it into the
ORBIS travel network so routes work. It's the epigraphy analogue of the manuscript
`check-city-nodes` skill (`.claude/skills/check-city-nodes/SKILL.md`), extended to also
add the routing layer (the manuscript version only adds the map node).

## Do we need to re-access ORBIS or use Firecrawl?

**No — and don't spend Firecrawl credits on this.** The inscriptions already carry
coordinates (EDH supplied them), so nothing needs scraping. ORBIS is a fixed ~677-node
historical network of major Roman sites; it will not contain these minor findspots, so
"re-accessing" it yields nothing new. The correct, fully-offline fix is to **synthesize**
a node + connecting edges from the coordinates we already have (connect each findspot to
its nearest existing ORBIS node by a road edge). Only consider Firecrawl if a findspot is
missing coordinates entirely (rare) — and even then prefer leaving it out over guessing.

## How the map + routing actually work (verified)

- **Cities** (names the orb + 0.3° map snapping): `static/data/orbis.json` → `cities`
  (197) plus `static/data/custom_locations.json` (currently 25). Shape:
  `{ "id": "<slug>", "name": "<City>", "modern": "<modern, country>", "lat": <n>, "lon": <n> }`.
  Snap rule (must match `findSnapCity` in `script.js` and `check_city_nodes.py`): nearest
  city within **0.3°** of lat AND lon; no city in range ⇒ orphan "This site" orb.
- **Travel graph**: `static/data/orbis_network.json` with:
  - `nodes`: `[{ "id": <int>, "x": <lon>, "y": <lat> }]`  (ids 50001–50801)
  - `cityNodes`: `{ "<city-slug>": <nodeId> }`  (links a city to its graph node)
  - `edges`: `[{ "s": <nodeId>, "t": <nodeId>, "d": <days>, "ty": "road"|"river"|"sea" }]`
    — stored **both directions**; `d` is travel-days (road ≈ km/30).
- The Route Planner reads `cityNodes[city.id]` to find a city's start/end node, then runs
  Dijkstra over `edges`. So a city is routable only if it has a `cityNodes` entry whose
  node has edges into the rest of the graph.

## The fix

Write `epigraphy_city_nodes.py` (repo root) that runs fully offline and does two phases.

### Phase 1 — audit
Read `static/epigraphy_data.js` (strip the `window.EPIGRAPHY_DATA = ` wrapper, parse the
JSON array). Load cities from `orbis.json` + `custom_locations.json`. For each inscription,
snap (lat,lon) to the nearest city within 0.3°. Group **orphans** (no city in range) by
rounded coordinate (4 dp). Print each orphan cluster: coord, count, a sample inscription
id, and the findspot name. `--report` mode stops here (exit 1 if any orphans), mirroring
`check_city_nodes.py`.

### Phase 2 — synthesize nodes + edges (`--apply`)

**Core principle: the inscription's real location never moves.** Every node we create
sits at the *findspot's own* coordinates. The route reaches the **closest existing ORBIS
node**, then covers the remaining "last-mile" gap to the true findspot as an explicit leg
whose distance and travel-time are computed from the real gap. Because the findspot node
is at its true coords, the planner automatically draws that final segment to the actual
site and folds its time into the total.

Group orphans by rounded coordinate (4 dp ≈ same physical spot) so co-located inscriptions
share one node at that exact spot — and so each inscription snaps to a node **at its own
location** (distance ≈ 0) rather than being pulled to a distant city. For each cluster,
append (idempotently — skip if a node already exists within ~0.005° of the coord):

1. **City** → `custom_locations.json` **at the findspot coords**:
   `{ "id": <slug>, "name": <place>, "modern": <place>, "lat": <lat>, "lon": <lon> }`.
   Derive `<place>` from the inscription's findspot: the part after " · " in its `name`
   (e.g. "Funerary inscription · Aquileia" → "Aquileia"); fall back to "Findspot (lat,lon)".
   `<slug>` = lowercased ASCII place, non-alnum → "_", de-duplicated against existing ids.
2. **Graph node** → `orbis_network.json` `nodes`, **at the same findspot coords**:
   `{ "id": <newId>, "x": <lon>, "y": <lat> }`, `<newId>` starting at **60000** (above 50801).
3. **cityNodes** entry: `"<slug>": <newId>`.
4. **Last-mile leg** → find the **single closest** existing ORBIS node by haversine distance
   (search all `nodes`, excluding other new 60000+ findspot nodes). Compute `km` = that
   great-circle gap. Add a **`road`** edge in **both** directions:
   `{ "s": newId, "t": nearId, "d": km / FOOT_KMPD, "ty": "road" }` and its reverse.
   - Type `road` makes the leg traversable by **foot** (`d` days) and **horse** (the planner
     prices horse at `d × 0.5`, i.e. ~2× faster) — the modes a traveller would use off the
     main network. No frontend change is needed: `buildOrbisGraph`/`buildCombinedGraph`
     already turn a `road` edge into foot+horse legs.
   - **Speeds:** `FOOT_KMPD = 30` (matches existing road edges: 54.5 km → 1.818 d). Set
     `d` from foot; horse is derived automatically.
   - **Optional river leg:** if the closest node is a river node (some edge touching it has
     `ty:"river"`) and the findspot is within ~15 km of it, ALSO add a `{ ty:"river" }` edge
     both directions with `d = km / RIVER_KMPD` (use `RIVER_KMPD = 60`). This lets the river
     mode reach riverine findspots. Skip when unsure — road (foot/horse) is the safe default.

Write all four structures back (pretty JSON; preserve existing entries). Print
`Added N city nodes, N graph nodes, E edges` and the min/median/max last-mile km.

### Naming quality (optional, better)
For nicer names, the EDH dump under `data-master/` has `findspot_modern` / `findspot_ancient`
per inscription (see `edh_ingest.py`'s `parse_edh_xml`). If you want authoritative names,
re-read those for the orphan ids instead of parsing them out of `name`. Not required.

## Verify

- Re-run `python epigraphy_city_nodes.py --report` → **0 orphans**.
- `py app.py`, hard-refresh: former "This site" orbs now show real city names; open the
  Route Planner and confirm you can route from Roma to a few newly-added findspots (a path
  appears, with a day/expense estimate). Manuscript routing still works.
- Sanity: no duplicate node ids; every new `cityNodes` slug exists in `custom_locations.json`;
  every new edge's endpoints exist in `nodes`.

## Deploy

```
git add epigraphy_city_nodes.py static/data/custom_locations.json static/data/orbis_network.json
git commit -m "Epigraphy: real city nodes + routes for inscription findspots"
git push
```

(`orbis.json` is not modified — new cities go in `custom_locations.json`.) Run only one
Code window editing these files at a time.

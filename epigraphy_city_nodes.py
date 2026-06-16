#!/usr/bin/env python3
"""epigraphy_city_nodes.py — give every inscription findspot a real, named city
node AND a routable last-mile leg into the ORBIS travel network. Fully offline:
the coordinates already exist in static/epigraphy_data.js (EDH supplied them);
this is pure node/edge synthesis — NO Firecrawl, NO ORBIS re-fetch.

CORE PRINCIPLE — the inscription's real location never moves. Every node we
create sits at the findspot's OWN coordinates. The route travels the network to
the closest existing ORBIS node, then covers the remaining gap to the true
findspot as an explicit last-mile leg whose distance/time come from the real
gap. Because the findspot node is at its true coords, the planner draws that
final segment to the actual site and folds in its time automatically.

  Phase 1 — audit (mirrors check_city_nodes.py):
      python epigraphy_city_nodes.py --report
    Snap each inscription (lat,lon) to the nearest city within 0.3°
    (orbis.json cities + custom_locations.json). Group ORPHANS (no city in
    range) by rounded coord (4 dp); print coord / count / sample-id / findspot.
    Exit 1 if any orphans.

  Phase 2 — synthesize (idempotent):
      python epigraphy_city_nodes.py --apply
    For each orphan cluster (skip if a node already exists within ~0.005°), at
    the findspot's own coords append:
      (1) custom_locations.json city  {id:slug, name:place, modern:place, lat, lon}
      (2) orbis_network.json node      {id:newId>=60000, x:lon, y:lat}
      (3) orbis_network.json cityNodes "slug": newId
      (4) last-mile leg: the single closest existing ORBIS node by haversine
          (search all nodes, exclude 60000+ findspot nodes); add a ROAD edge
          both ways {s,t,d:km/30,ty:"road"}. "road" => traversable by foot (d
          days) and horse (planner prices d×0.5). If that node is a river node
          (some edge touching it has ty:"river") and km<=15, also add a
          {ty:"river"} edge both ways with d:km/60 so the river mode can reach it.
"""

import os, sys, json, math, re, unicodedata, collections, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "static", "epigraphy_data.js")
ORBIS = os.path.join(HERE, "static", "data", "orbis.json")
CUSTOM = os.path.join(HERE, "static", "data", "custom_locations.json")
NETWORK = os.path.join(HERE, "static", "data", "orbis_network.json")

SNAP_DEG = 0.3        # must match findSnapCity() in static/script.js & check_city_nodes.py
NODE_BASE = 60000     # new findspot node ids start here (above ORBIS 50801)
DEDUPE_DEG = 0.005    # idempotency: skip a cluster if a node already sits this close
FOOT_KMPD = 30.0      # road travel-days = km / 30  (matches existing road edges)
RIVER_KMPD = 60.0     # river travel-days = km / 60
RIVER_MAX_KM = 15.0   # only add a river last-mile leg within this gap


# ── shared helpers ───────────────────────────────────────────────────────────
def load_epigraphy():
    raw = open(DATA, encoding="utf-8").read()
    p = "window.EPIGRAPHY_DATA = "
    body = raw[raw.index(p) + len(p):].strip()
    if body.endswith(";"):
        body = body[:-1]
    return json.loads(body)


def load_cities():
    cities = json.load(open(ORBIS, encoding="utf-8"))["cities"]
    if os.path.exists(CUSTOM):
        cities = cities + json.load(open(CUSTOM, encoding="utf-8"))
    return cities


def snap(cities, lat, lon):
    cands = [c for c in cities if abs(c["lat"] - lat) < SNAP_DEG and abs(c["lon"] - lon) < SNAP_DEG]
    if not cands:
        return None
    return min(cands, key=lambda c: (c["lat"] - lat) ** 2 + (c["lon"] - lon) ** 2)


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def coord(e):
    try:
        return float(e["lat"]), float(e["lon"])
    except (TypeError, ValueError, KeyError):
        return None, None


def place_of(name):
    """Findspot place = the part after ' · ' in the inscription name
    ('Funerary inscription · Aquileia' -> 'Aquileia'); '' if not derivable."""
    if name and " · " in name:
        return name.split(" · ", 1)[1].strip()
    return ""


def slugify(place):
    s = unicodedata.normalize("NFKD", place).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return s or "findspot"


def cluster_orphans(epigraphy, cities):
    """Group orphan inscriptions by coord rounded to 4 dp. Returns an ordered
    dict {(lat4,lon4): {'lat','lon','n','ids','places','founds'}}."""
    orphans = collections.OrderedDict()
    for e in epigraphy:
        lat, lon = coord(e)
        if lat is None:
            continue
        if snap(cities, lat, lon) is not None:
            continue
        key = (round(lat, 4), round(lon, 4))
        o = orphans.get(key)
        if o is None:
            o = orphans[key] = {"lat": key[0], "lon": key[1], "n": 0,
                                "ids": [], "places": [], "founds": set()}
        o["n"] += 1
        if len(o["ids"]) < 3:
            o["ids"].append(e.get("id"))
        pl = place_of(e.get("name", ""))
        if pl:
            o["places"].append(pl)
        o["founds"].add(pl or (e.get("name") or "").strip())
    return orphans


# ── PHASE 1: report ──────────────────────────────────────────────────────────
def do_report():
    epigraphy = load_epigraphy()
    cities = load_cities()
    total = nocoord = snapped = 0
    for e in epigraphy:
        total += 1
        lat, lon = coord(e)
        if lat is None:
            nocoord += 1
            continue
        if snap(cities, lat, lon) is not None:
            snapped += 1
    orphans = cluster_orphans(epigraphy, cities)
    n_orphan = sum(o["n"] for o in orphans.values())
    print(f"inscriptions: {total} | no coords: {nocoord} | "
          f"snapped: {snapped} | ORPHAN: {n_orphan} | clusters: {len(orphans)}")
    if orphans:
        print("\n=== ORPHAN findspots (each needs a city node) ===")
        for o in sorted(orphans.values(), key=lambda o: -o["n"]):
            fs = " / ".join(sorted(x for x in o["founds"] if x))[:60]
            print(f"  ({o['lat']}, {o['lon']})  x{o['n']:>3}  e.g. {o['ids']}  ::  {fs}")
        sys.exit(1)
    print("\nAll findspots have a city node. OK")


# ── PHASE 2: synthesize ──────────────────────────────────────────────────────
def do_apply():
    epigraphy = load_epigraphy()
    cities = load_cities()
    orphans = cluster_orphans(epigraphy, cities)
    if not orphans:
        print("No orphans — nothing to do.")
        return

    custom = json.load(open(CUSTOM, encoding="utf-8"))
    net = json.load(open(NETWORK, encoding="utf-8"))
    nodes, cityNodes, edges = net["nodes"], net["cityNodes"], net["edges"]

    # river nodes = any node id touched by a river edge (for the optional river leg)
    river_nodes = set()
    for e in edges:
        if e.get("ty") == "river":
            river_nodes.add(e["s"]); river_nodes.add(e["t"])

    # existing slugs to dedupe against (orbis cities + custom + cityNodes keys)
    used_slugs = {c["id"] for c in json.load(open(ORBIS, encoding="utf-8"))["cities"]}
    used_slugs |= {c["id"] for c in custom}
    used_slugs |= set(cityNodes.keys())

    next_id = max([NODE_BASE - 1] + [n["id"] for n in nodes]) + 1
    backbone = [n for n in nodes if n["id"] < NODE_BASE]  # connect to real ORBIS only

    added_cities = added_nodes = added_edges = skipped = 0
    legs_km = []

    for o in sorted(orphans.values(), key=lambda o: -o["n"]):
        lat, lon = o["lat"], o["lon"]

        # idempotent: skip only if one of OUR synthesized findspot nodes (id >=
        # NODE_BASE) already sits within ~DEDUPE_DEG — covers re-runs and two
        # co-located orphan clusters in the same run (the second snaps to the
        # first's new city). Pre-existing city-less ORBIS waypoint nodes must NOT
        # block creation, or a findspot sitting on one would stay an orphan.
        if any(n["id"] >= NODE_BASE and abs(n["x"] - lon) < DEDUPE_DEG
               and abs(n["y"] - lat) < DEDUPE_DEG for n in nodes):
            skipped += 1
            continue

        place = collections.Counter(o["places"]).most_common(1)
        place = place[0][0] if place else f"Findspot ({lat},{lon})"

        slug = base = slugify(place)
        i = 2
        while slug in used_slugs:
            slug = f"{base}_{i}"; i += 1
        used_slugs.add(slug)

        new_id = next_id; next_id += 1

        # nearest existing ORBIS backbone node by great-circle distance
        near = min(backbone, key=lambda n: haversine_km(lat, lon, n["y"], n["x"]))
        km = haversine_km(lat, lon, near["y"], near["x"])
        legs_km.append(km)
        d_road = round(km / FOOT_KMPD, 4)

        # (1) city at the findspot's own coords
        custom.append({"id": slug, "name": place, "modern": place, "lat": lat, "lon": lon})
        added_cities += 1
        # (2) graph node at the same coords
        nodes.append({"id": new_id, "x": lon, "y": lat})
        added_nodes += 1
        # (3) cityNodes link
        cityNodes[slug] = new_id
        # (4) last-mile ROAD leg both directions (foot + horse)
        edges.append({"s": new_id, "t": near["id"], "d": d_road, "ty": "road"})
        edges.append({"s": near["id"], "t": new_id, "d": d_road, "ty": "road"})
        added_edges += 2
        # optional river leg if the nearest node is riverine and close
        if near["id"] in river_nodes and km <= RIVER_MAX_KM:
            d_river = round(km / RIVER_KMPD, 4)
            edges.append({"s": new_id, "t": near["id"], "d": d_river, "ty": "river"})
            edges.append({"s": near["id"], "t": new_id, "d": d_river, "ty": "river"})
            added_edges += 2

    # write back — custom_locations pretty (2-space), network compact (match file)
    json.dump(custom, open(CUSTOM, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(net, open(NETWORK, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

    print(f"Added {added_cities} city nodes, {added_nodes} graph nodes, {added_edges} edges"
          f" ({skipped} clusters skipped as already present).")
    if legs_km:
        legs_km.sort()
        print(f"Last-mile km — min {legs_km[0]:.2f} | median "
              f"{statistics.median(legs_km):.2f} | max {legs_km[-1]:.2f}")


def main():
    if "--apply" in sys.argv:
        do_apply()
    elif "--report" in sys.argv:
        do_report()
    else:
        print("usage: epigraphy_city_nodes.py --report | --apply")
        sys.exit(2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""check_city_nodes.py — verify every manuscript find-site has a city node.

The map snaps each manuscript's (lat, lon) to the nearest city within 0.3° of
its coordinates (the same rule as findSnapCity in static/script.js). The city
list is ORBIS cities (static/data/orbis.json) PLUS static/data/custom_locations.json.

A manuscript whose find-site has NO city within 0.3° shows up on the map as an
unnamed "This site" orb instead of a named city. Run this after onboarding new
manuscripts; if it reports orphans, add a node for each to custom_locations.json
(id / name / modern / lat / lon) at the orphan coordinate, then re-run.

    python check_city_nodes.py          # report orphan find-sites (exit 1 if any)
    python check_city_nodes.py --list   # also print the full snapped distribution
"""
import os, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP_DEG = 0.3  # must match findSnapCity() in static/script.js


def load_cities():
    cities = json.load(open(os.path.join(HERE, 'static/data/orbis.json'), encoding='utf-8'))['cities']
    cust = os.path.join(HERE, 'static/data/custom_locations.json')
    if os.path.exists(cust):
        cities = cities + json.load(open(cust, encoding='utf-8'))
    return cities


def snap(cities, lat, lon):
    cands = [c for c in cities if abs(c['lat'] - lat) < SNAP_DEG and abs(c['lon'] - lon) < SNAP_DEG]
    if not cands:
        return None
    return min(cands, key=lambda c: (c['lat'] - lat) ** 2 + (c['lon'] - lon) ** 2)


def manuscripts():
    """Yield (id, found, lat, lon) for each manuscript .txt (parsed minimally)."""
    mdir = os.path.join(HERE, 'manuscripts')
    for f in sorted(os.listdir(mdir)):
        if not f.endswith('.txt'):
            continue
        meta = {}
        with open(os.path.join(mdir, f), encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if line == '[GREEK]':
                    break
                if ':' in line and not line.startswith('#') and not line.startswith('['):
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip()
        try:
            lat = float(meta.get('lat')); lon = float(meta.get('lon'))
        except (TypeError, ValueError):
            lat = lon = None
        yield meta.get('id', f), meta.get('found', ''), lat, lon


def main():
    cities = load_cities()
    orphan = collections.defaultdict(lambda: {'n': 0, 'found': set(), 'ids': []})
    snapped = collections.Counter()
    total = nocoord = 0
    for mid, found, lat, lon in manuscripts():
        total += 1
        if lat is None or lon is None:
            nocoord += 1
            continue
        s = snap(cities, lat, lon)
        if s is None:
            o = orphan[(round(lat, 4), round(lon, 4))]
            o['n'] += 1
            o['found'].add((found or '').strip())
            if len(o['ids']) < 3:
                o['ids'].append(mid)
        else:
            snapped[s['name']] += 1

    n_orphan = sum(o['n'] for o in orphan.values())
    print(f"manuscripts: {total} | no coords: {nocoord} | "
          f"snapped: {sum(snapped.values())} | ORPHAN: {n_orphan}")

    if orphan:
        print("\n=== ORPHAN find-sites (add a city node for each) ===")
        for (lat, lon), o in sorted(orphan.items(), key=lambda kv: -kv[1]['n']):
            fs = ' / '.join(sorted(x for x in o['found'] if x))[:70]
            print(f"  ({lat}, {lon})  x{o['n']:>3}  e.g. {o['ids']}  ::  {fs}")
        print("\nAdd each to static/data/custom_locations.json:")
        print('  { "id": "<slug>", "name": "<City>", "modern": "<modern>, Egypt",')
        print('    "lat": <lat>, "lon": <lon> }')

    if '--list' in sys.argv:
        print("\n=== snapped distribution ===")
        for name, n in snapped.most_common():
            print(f"  {name:26} {n}")

    if n_orphan:
        sys.exit(1)
    print("\nAll find-sites have a city node. OK")


if __name__ == '__main__':
    main()

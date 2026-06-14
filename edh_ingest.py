#!/usr/bin/env python3
"""
edh_ingest.py — turn a downloaded EDH/LIST epigraphy dump into the app's
epigraphy data file. NO Firecrawl credits, fully offline.

Source (download once, free, CC BY-SA 4.0 — no Anubis):
  * EDH GeoJSON dumps:  github.com/epigraphic-database-heidelberg/data  ->  inscriptions/*.geojson
  * or the LIST aggregate (EDH+EDCS): zenodo.org/records/10473706

Usage:
  python edh_ingest.py --inspect edh_inscriptions.geojson      # print the real field keys
  python edh_ingest.py edh_inscriptions.geojson                # build static/epigraphy_data.js
  python edh_ingest.py edh_inscriptions.geojson --cap 2000     # cap the first batch

It keeps only inscriptions that have BOTH coordinates and a transcription, scores
them by completeness, takes the best `--cap` (default 2000), classifies each as
funerary / honourific / public, and writes:
    static/epigraphy_data.js  ->  window.EPIGRAPHY_DATA = [ {id,name,genre,lat,lon,date,language,text,source}, ... ]

Schema-tolerant: EDH/LIST field names vary, so each target field tries several
known keys. Run --inspect first; if a field comes out empty, add its real key to
the *_KEYS lists below.
"""

import os, re, sys, json, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "static", "epigraphy_data.js")

# Candidate property keys, tried in order (EDH GeoJSON + LIST aggregate variants)
TEXT_KEYS  = ["transcription", "text", "transcription_clean", "diplomatic", "clean_text_interpretive_word"]
TYPE_KEYS  = ["type_of_inscription", "type_of_inscription_clean", "type_of_inscription_certainty", "type", "type_of_monument"]
LANG_KEYS  = ["language", "language_certainty", "lang"]
NB_KEYS    = ["not_before", "date_not_before", "dating_from", "not_before_clean"]
NA_KEYS    = ["not_after", "date_not_after", "dating_to", "not_after_clean"]
PLACE_KEYS = ["findspot_modern", "findspot_ancient", "findspot", "modern_region_clean", "province_label", "province"]
ID_KEYS    = ["id", "hd_no", "hdnr", "edh", "EDH-ID", "edcs_id"]

# inscription-type term -> app genre
GENRE_MAP = [
    ("funerary",   ["sepulcr", "epitaph", "grave", "funerary", "tomb"]),
    ("honourific", ["honor", "honour", "honorific"]),
    ("public",     ["building", "aedific", "dedicat", "votive", "sacr", "milliar", "miliar",
                    "boundary", "legal", "lex ", "edict", "list", "acta", "public"]),
]


def first_key(props, keys):
    for k in keys:
        if k in props and props[k] not in (None, "", []):
            return props[k]
    # case-insensitive fallback
    low = {k.lower(): v for k, v in props.items()}
    for k in keys:
        if k.lower() in low and low[k.lower()] not in (None, "", []):
            return low[k.lower()]
    return None


def as_text(v):
    if isinstance(v, list):
        return " ".join(str(x) for x in v if x)
    return str(v) if v is not None else ""


def classify(type_str):
    t = (type_str or "").lower()
    for genre, terms in GENRE_MAP:
        if any(term in t for term in terms):
            return genre
    return "public"   # safe catch-all (app only has 3 genres)


def fmt_date(nb, na):
    def yr(v):
        try:
            n = int(re.search(r"-?\d+", str(v)).group())
        except (TypeError, AttributeError):
            return None
        return n
    a, b = yr(nb), yr(na)
    if a is None and b is None:
        return "unknown"
    def lab(n):
        return f"{abs(n)} {'BCE' if n < 0 else 'CE'}"
    if a is not None and b is not None:
        return lab(a) if a == b else f"{lab(a)} – {lab(b)}"
    return lab(a if a is not None else b)


def coords_from(feat, props):
    geom = feat.get("geometry") or {}
    c = geom.get("coordinates")
    if isinstance(c, list) and len(c) >= 2:
        lon, lat = c[0], c[1]           # GeoJSON is [lon, lat]
        try:
            return float(lat), float(lon)
        except (TypeError, ValueError):
            pass
    # LIST/flat fallback: a "coordinates" or lat/lon property
    cc = props.get("coordinates")
    if isinstance(cc, str) and "," in cc:
        try:
            lat, lon = (float(x) for x in cc.split(",")[:2])
            return lat, lon
        except ValueError:
            pass
    try:
        return float(props["lat"]), float(props["lng"])
    except (KeyError, TypeError, ValueError):
        return None, None


def load_features(path):
    data = json.load(open(path, encoding="utf-8"))
    if isinstance(data, dict) and "features" in data:
        return data["features"]
    if isinstance(data, list):                       # plain array of records
        return [{"properties": r, "geometry": None} for r in data]
    raise SystemExit("Unrecognized file: expected GeoJSON FeatureCollection or JSON array.")


def do_inspect(path):
    feats = load_features(path)
    print(f"{len(feats)} features. Property keys on the first few:")
    seen = set()
    for f in feats[:5]:
        for k in (f.get("properties") or {}):
            seen.add(k)
    for k in sorted(seen):
        print("  ", k)
    if feats:
        print("\nSample properties (first feature):")
        print(json.dumps(feats[0].get("properties", {}), ensure_ascii=False, indent=1)[:1500])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="EDH/LIST dump (.geojson or .json)")
    ap.add_argument("--cap", type=int, default=2000)
    ap.add_argument("--inspect", action="store_true")
    args = ap.parse_args()

    if args.inspect:
        do_inspect(args.file)
        return

    feats = load_features(args.file)
    rows = []
    for f in feats:
        props = f.get("properties") or {}
        lat, lon = coords_from(f, props)
        text = as_text(first_key(props, TEXT_KEYS)).strip()
        if lat is None or not text:
            continue                                  # need both coords and text
        type_str = as_text(first_key(props, TYPE_KEYS))
        ident = as_text(first_key(props, ID_KEYS)) or f"edh-{len(rows)}"
        place = as_text(first_key(props, PLACE_KEYS)) or "Roman Empire"
        genre = classify(type_str)
        name = (type_str.strip().title() + " — " + place) if type_str else place
        rows.append({
            "id": ident,
            "name": name[:120],
            "genre": genre,
            "lat": round(lat, 5), "lon": round(lon, 5),
            "date": fmt_date(first_key(props, NB_KEYS), first_key(props, NA_KEYS)),
            "language": as_text(first_key(props, LANG_KEYS)) or "Latin",
            "text": re.sub(r"\s+", " ", text)[:2000],
            "source": f"https://edh.ub.uni-heidelberg.de/edh/inschrift/{ident}",
        })

    # best-preserved first: longer text + having a real type/date
    rows.sort(key=lambda r: (len(r["text"]), r["date"] != "unknown"), reverse=True)
    rows = rows[: args.cap]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("// Generated by edh_ingest.py — EDH/LIST epigraphy (CC BY-SA 4.0).\n")
        fh.write("window.EPIGRAPHY_DATA = ")
        json.dump(rows, fh, ensure_ascii=False)
        fh.write(";\n")

    by = {}
    for r in rows:
        by[r["genre"]] = by.get(r["genre"], 0) + 1
    print(f"Wrote {len(rows)} inscriptions to {OUT}")
    print("By genre:", ", ".join(f"{k}: {v}" for k, v in sorted(by.items())))
    print("Commit + push to publish (the frontend loads epigraphy_data.js).")


if __name__ == "__main__":
    main()

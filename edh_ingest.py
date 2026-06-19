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

import os, re, sys, json, argparse, glob
import xml.etree.ElementTree as ET

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

# inscription-type term -> app genre. EDH types are in GERMAN, so the German
# EpiDoc terms are listed alongside the English/Latin LIST variants.
GENRE_MAP = [
    ("funerary",   ["sepulcr", "epitaph", "grave", "funerary", "tomb",
                    "grabinschrift", "grab"]),                              # Grabinschrift
    ("honourific", ["honor", "honour", "honorific",
                    "ehreninschrift", "ehren"]),                           # Ehreninschrift
    ("votive",     ["weihinschrift", "weih", "votiv", "votive"]),          # Weihinschrift — dedication
    ("building",   ["bauinschrift", "bau", "stifter", "building", "aedific"]),  # Bauinschrift — construction
    ("defixio",    ["defixio", "fluchtafel", "devotio"]),                  # curse tablet (before public)
    ("public",     ["milliar", "miliar",
                    "boundary", "legal", "lex ", "edict", "list", "acta", "public",
                    "meilen", "leugen",                # milestone (Meilen-/Leugenstein)
                    "grenz",                           # boundary marker
                    "rechtlich", "öffentlich",         # legal, public
                    "diplom", "akklam", "verzeichnis", # diploma / acclamation / list
                    "besitzer", "hersteller"]),
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


# ───────────────────────── EDH EpiDoc-XML reader ─────────────────────────
# The real EDH dump (github.com/epigraphic-database-heidelberg/data) ships the
# inscriptions as EpiDoc TEI XML under inscriptions/**/HD*.xml, with coordinates
# in a separate geography/edhGeographicData.json keyed by Trismegistos/GeoNames
# place URIs. We parse each XML into the same {properties, geometry} feature shape
# the rest of this script already understands, joining coords via the place URIs.

TEI_NS = "{http://www.tei-c.org/ns/1.0}"


def _local(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag


def _render(el):
    """Render an EpiDoc edition element to readable text:
    <expan><abbr>D</abbr><ex>is</ex></expan> -> 'D(is)', <supplied>x</supplied> -> '[x]',
    <lb/> -> newline (one source line per <lb>), <gap/> -> '…'. Tails handled by caller."""
    tag = _local(el.tag)
    if tag == "gap":
        return " … "
    if tag == "lb":
        return "\n"                 # a real line break — kept so we can split into lines
    if tag in ("space", "g"):
        return " "
    out = []
    if el.text:
        out.append(el.text)
    for child in el:
        ctag = _local(child.tag)
        if ctag == "ex":
            out.append("(" + _render(child).strip() + ")")
        elif ctag == "supplied":
            out.append("[" + _render(child) + "]")
        else:
            out.append(_render(child))
        if child.tail:
            out.append(child.tail)
    return "".join(out)


# German EpiDoc inscription-type term -> short English descriptor for `name`
TYPE_LABELS = [
    ("grabinschrift", "Funerary inscription"),
    ("weihinschrift",  "Votive inscription"),
    ("ehreninschrift", "Honorific inscription"),
    ("bau",            "Building inscription"),
    ("stifter",        "Building inscription"),
    ("meilen",         "Milestone"),
    ("leugen",         "Milestone"),
    ("militärdiplom",  "Military diploma"),
    ("militardiplom",  "Military diploma"),
    ("defixio",        "Curse tablet"),
    ("akklam",         "Acclamation"),
    ("verzeichnis",    "List / register"),
    ("grenz",          "Boundary marker"),
    ("rechtlich",      "Legal decree"),
    ("besitzer",       "Owner / maker inscription"),
    ("hersteller",     "Owner / maker inscription"),
    ("aufschrift",     "Label inscription"),
    ("beischrift",     "Caption"),
    ("brief",          "Letter"),
    ("elogium",        "Elogium"),
    ("gebet",          "Prayer"),
    ("instrumentum",   "Instrumentum"),
    ("unbestimmt",     "Inscription"),
]


def type_label(type_str):
    """German inscription type -> short English descriptor (trailing '?' tolerated)."""
    tl = (type_str or "").lower().rstrip("?").strip()
    for key, label in TYPE_LABELS:
        if key in tl:
            return label
    return type_str.strip().title() if type_str else "Inscription"


def _citation(root):
    """First <bibl> in the bibliography is the primary publication (CIL/AE/RIB/…).
    Clean trailing edition-quality markers like ' (B)' and the trailing period."""
    for b in root.iter(TEI_NS + "bibl"):
        txt = re.sub(r"\s+", " ", "".join(b.itertext())).strip()
        if not txt:
            continue
        txt = re.sub(r"\s*\([A-Za-z]{1,3}\)\s*$", "", txt)   # drop ' (B)' / ' (BC)'
        txt = txt.rstrip(" .;-")
        if txt:
            return txt
    return None


def _geo_lookups(data_root):
    """Build {trismegistos_place_no -> [lon,lat]} and {geonames_no -> [lon,lat]}."""
    geo_path = os.path.join(data_root, "geography", "edhGeographicData.json")
    tm_map, gn_map = {}, {}
    if not os.path.exists(geo_path):
        raise SystemExit(f"Geography file not found: {geo_path}")
    data = json.load(open(geo_path, encoding="utf-8"))
    for f in data.get("features", []):
        geom = f.get("geometry") or {}
        c = geom.get("coordinates")
        if not (isinstance(c, list) and len(c) >= 2):
            continue
        p = f.get("properties") or {}
        t = p.get("trismegistos_geo_uri")
        g = p.get("geonames_uri")
        if t:
            m = re.search(r"(\d+)", t)
            if m:
                tm_map.setdefault(int(m.group(1)), c)
        if g:
            m = re.search(r"(\d+)", g)
            if m:
                gn_map.setdefault(int(m.group(1)), c)
    return tm_map, gn_map


def parse_edh_xml(path, tm_map, gn_map):
    """Parse one EDH EpiDoc XML into a {properties, geometry} feature, or None."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return None

    # HD-number (filename / localID idno)
    hd = os.path.splitext(os.path.basename(path))[0]
    for idno in root.iter(TEI_NS + "idno"):
        if idno.get("type") == "localID" and (idno.text or "").strip():
            hd = idno.text.strip()
            break

    # transcription text from the <div type="edition"> -> its <ab> blocks.
    # _render emits "\n" per <lb>, so we keep both a flat string (for scoring) and
    # a per-line list (for the reader's verse-style display).
    text = ""
    lines = []
    lang = ""
    for div in root.iter(TEI_NS + "div"):
        if div.get("type") == "edition":
            lang = div.get(TEI_NS + "lang") or div.get("{http://www.w3.org/XML/1998/namespace}lang") or ""
            raw = "\n".join(_render(ab) for ab in div.iter(TEI_NS + "ab"))
            lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in raw.split("\n")]
            lines = [ln for ln in lines if ln]
            text = " ".join(lines)
            break

    # inscription type — the EAGLE <term> in textClass/keywords (German)
    type_str = ""
    for term in root.iter(TEI_NS + "term"):
        if (term.text or "").strip():
            type_str = term.text.strip()
            break

    # date — origDate custom attributes
    nb = na = None
    od = next((e for e in root.iter(TEI_NS + "origDate")), None)
    if od is not None:
        nb = od.get("notBefore-custom") or od.get("notBefore")
        na = od.get("notAfter-custom") or od.get("notAfter")

    # findspot place name + geo refs (Trismegistos in origPlace, GeoNames in provenance)
    place = ""
    tm_ids, gn_ids = [], []
    for op in root.iter(TEI_NS + "origPlace"):
        for pn in op.iter(TEI_NS + "placeName"):
            ref = pn.get("ref") or ""
            m = re.search(r"trismegistos\.org/place/(\d+)", ref)
            if m:
                tm_ids.append(int(m.group(1)))
            if (pn.text or "").strip() and not pn.get("type"):
                place = pn.text.strip()           # the un-typed placeName is the findspot
    for pv in root.iter(TEI_NS + "provenance"):
        if pv.get("type") == "found":
            for pn in pv.iter(TEI_NS + "placeName"):
                ref = pn.get("ref") or ""
                m = re.search(r"geonames\.org/(\d+)", ref)
                if m:
                    gn_ids.append(int(m.group(1)))
                if not place and (pn.text or "").strip() and not pn.get("type"):
                    place = pn.text.strip()

    # resolve coordinates: prefer GeoNames (modern findspot), then the most specific
    # Trismegistos place (findspot listed last), then the province (listed first).
    coords = None
    for gid in gn_ids:
        if gid in gn_map:
            coords = gn_map[gid]
            break
    if coords is None:
        for tid in reversed(tm_ids):
            if tid in tm_map:
                coords = tm_map[tid]
                break

    lang_label = {"la": "Latin", "grc": "Greek", "la,grc": "Latin/Greek",
                  "grc,la": "Latin/Greek"}.get(lang, "Latin")

    label = type_label(type_str)
    name = f"{label} · {place}" if place else label
    citation = _citation(root)

    props = {
        "id": hd,
        "title": citation or ("EDH " + hd),       # citation (CIL/AE/…) or EDH HD-number
        "name": name,                             # short type/place descriptor
        "transcription": text,                    # flat string (scoring / TEXT_KEYS)
        "text_lines": lines,                      # original text, one entry per source line
        "type_of_inscription": type_str,
        "language": lang_label,
        "not_before": nb,
        "not_after": na,
        "findspot_modern": place,
    }
    geometry = {"coordinates": coords} if coords else None
    return {"properties": props, "geometry": geometry}


def load_edh_dump(data_root):
    """Walk inscriptions/**/HD*.xml under an EDH dump root into feature dicts."""
    insc_dir = os.path.join(data_root, "inscriptions")
    if not os.path.isdir(insc_dir):
        raise SystemExit(f"No inscriptions/ dir under {data_root}")
    tm_map, gn_map = _geo_lookups(data_root)
    files = glob.glob(os.path.join(insc_dir, "**", "HD*.xml"), recursive=True)
    files.sort()
    print(f"Parsing {len(files)} EpiDoc XML files (geo: {len(tm_map)} TM / {len(gn_map)} GeoNames places)…")
    feats = []
    for i, fn in enumerate(files):
        feat = parse_edh_xml(fn, tm_map, gn_map)
        if feat is not None:
            feats.append(feat)
        if (i + 1) % 10000 == 0:
            print(f"  …{i + 1}/{len(files)} parsed")
    return feats


def load_features(path):
    # An EDH dump directory (has inscriptions/ + geography/) → parse the EpiDoc XML.
    if os.path.isdir(path):
        return load_edh_dump(path)
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


def _load_existing_translations(path):
    """Return {id: translation} from a previously generated epigraphy_data.js.
    edh_ingest regenerates the file from scratch and translations live ONLY in
    that output file, so we carry them over by id rather than wiping them.
    Tolerant of a missing or partially-written file (returns {})."""
    if not os.path.exists(path):
        return {}
    try:
        raw = open(path, encoding="utf-8").read()
        P = "window.EPIGRAPHY_DATA = "
        payload = raw[raw.index(P) + len(P):].strip()
        if payload.endswith(";"):
            payload = payload[:-1]
        data = json.loads(payload)
    except (ValueError, OSError):
        return {}
    out = {}
    for r in data:
        tr = r.get("translation")
        if tr:
            out[r.get("id")] = tr
    return out


def _load_existing_records(path):
    """Return the full list of records from a previous epigraphy_data.js (or [])."""
    if not os.path.exists(path):
        return []
    try:
        raw = open(path, encoding="utf-8").read()
        P = "window.EPIGRAPHY_DATA = "
        payload = raw[raw.index(P) + len(P):].strip()
        if payload.endswith(";"):
            payload = payload[:-1]
        data = json.loads(payload)
        return data if isinstance(data, list) else []
    except (ValueError, OSError):
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="EDH/LIST dump (.geojson or .json)")
    ap.add_argument("--cap", type=int, default=2000)
    ap.add_argument("--add", action="store_true",
                    help="ADDITIVE: keep the existing epigraphy_data.js untouched and "
                         "append the next --cap best inscriptions NOT already in it.")
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

        # `name` = short type/place descriptor; `title` = citation (CIL/AE/…) or EDH no.
        name = props.get("name") or ((type_str.strip().title() + " — " + place) if type_str else place)
        title = props.get("title") or ("EDH " + ident)

        # `text` is a list of original-text lines; the XML reader supplies text_lines,
        # otherwise fall back to the single flat string. `translation` is an English
        # placeholder, ready to be filled in later (kept parallel to manuscripts).
        text_lines = props.get("text_lines") or [re.sub(r"\s+", " ", text)]
        text_lines = [ln for ln in text_lines if ln]

        rows.append({
            "id": ident,
            "title": title[:120],
            "name": name[:120],
            "genre": genre,
            "lat": round(lat, 5), "lon": round(lon, 5),
            "date": fmt_date(first_key(props, NB_KEYS), first_key(props, NA_KEYS)),
            "language": as_text(first_key(props, LANG_KEYS)) or "Latin",
            "text": text_lines,
            "translation": [],
            "source": f"https://edh.ub.uni-heidelberg.de/edh/inschrift/{ident}",
        })

    # best-preserved first: more text (by total characters) + having a real date
    rows.sort(key=lambda r: (sum(len(x) for x in r["text"]), r["date"] != "unknown"), reverse=True)
    if args.add:
        # Additive: keep every existing record EXACTLY as-is (translations, genres,
        # coords, manual edits) and append only the next --cap best NEW inscriptions.
        existing_records = _load_existing_records(OUT)
        have = {r.get("id") for r in existing_records}
        new_rows = [r for r in rows if r["id"] not in have][: args.cap]
        rows = existing_records + new_rows
        print(f"Add mode: {len(existing_records)} existing + {len(new_rows)} new "
              f"= {len(rows)} total (existing records untouched).")
    else:
        rows = rows[: args.cap]
        # Carry over translations from any previous run so regeneration never wipes
        # the work done by epigraphy_translate.py.
        existing = _load_existing_translations(OUT)
        if existing:
            kept = 0
            for r in rows:
                tr = existing.get(r["id"])
                if tr:
                    r["translation"] = tr
                    kept += 1
            print(f"Preserved {kept} existing translations from the previous file.")

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

#!/usr/bin/env python3
"""
idp_ingest.py — onboard documentary papyri from a local idp.data dump into the
app's manuscripts/*.txt format. NO Firecrawl credits, fully offline.

This is the papyrus twin of edh_ingest.py. The data is the bulk publication of
papyri.info (github.com/papyri/idp.data, CC BY 3.0): three parallel TEI/EpiDoc
trees linked by the HGV/TM number —

  DDB_EpiDoc_XML/<coll>/<coll>.<vol>/<coll>.<vol>.<n>.xml  — Greek transcription
  HGV_meta_EpiDoc/HGV<ceil(N/1000)>/<N>.xml               — date + provenance
  HGV_trans_EpiDoc/<N>.xml                                 — translations (sparse)

Usage:
  py idp_ingest.py <idp.data dir>                 # write the next --cap best papyri
  py idp_ingest.py <idp.data dir> --cap 50        # cap this batch
  py idp_ingest.py <idp.data dir> --add           # explicit additive (the default)
  py idp_ingest.py <idp.data dir> --inspect       # print derived metadata for a few
  py idp_ingest.py --selftest                     # offline parser sanity check

Coordinates come from the Pleiades places dump (pleiades-places-latest.csv.gz from
atlantides.org/downloads/pleiades/dumps; cols id / reprLat / reprLong), keyed by
the Pleiades id on each HGV placeName @ref. Falls back to build_from_sweep's COORDS
name map, else leaves lat/lon blank (check_city_nodes.py handles the rest later).

Per papyrus it renders the <div type="edition">/<ab> into clean numbered Greek
lines (expand <expan>/<ex>, <supplied>→[..], <gap>→…, join break="no", pick the
regularised <reg>/<lem> reading), then writes manuscripts/<slug>.txt in the EXACT
format build_from_sweep.py produces, with one BLANK numbered [TRANSLATION] slot per
Greek line so the model can later fill line-aligned English. Where an English HGV
translation exists it is captured as a "# HGV-EN:" comment under the [TRANSLATION]
header — a head-start for the translator, NOT the final aligned text. German-only
HGV translations are ignored.

Additive + safe: existing manuscripts/<slug>.txt files are NEVER overwritten (so
hand-translated work is preserved), and --cap counts only NEW papyri, best-
preserved (most text) first.
"""

import os, re, sys, csv, gzip, glob, argparse
import xml.etree.ElementTree as ET

import build_from_sweep as bfs   # reuse citation/slug/clean_date/clean_greek/COORDS/classify

try:                                  # Windows consoles default to cp1252; print Greek safely
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
MSS = os.path.join(HERE, "manuscripts")
PLEIADES_GZ = os.path.join(HERE, "pleiades-places-latest.csv.gz")

TEI_NS = "{http://www.tei-c.org/ns/1.0}"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

# join marker emitted for <lb break="no"/> (a word split across source lines)
_JOIN = ""

# genre slug -> short English label for the name/content meta lines
GENRE_LABEL = {
    "receipts": "Receipt", "contracts": "Contract", "letters": "Letter",
    "petitions": "Petition", "documents": "Documentary papyrus",
}


def _local(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag


# ───────────────────────── EpiDoc edition renderer ─────────────────────────
# Adapted from edh_ingest._render, extended for the DDbDP markup: expansions are
# rendered CLEAN (no parentheses) per the onboarding spec, <choice> keeps the
# regularised reading, <app> keeps the editor's <lem>, and <lb break="no"/> joins
# a word split across two source lines.
_SKIP_TAGS = {"note", "rdg", "orig", "sic", "del", "surplus", "handShift",
              "milestone", "lem_skip", "certainty", "figure", "figDesc"}


def _inner(el):
    """Render an element's text + children + tails."""
    out = []
    if el.text:
        out.append(el.text)
    for ch in el:
        out.append(_render(ch))
        if ch.tail:
            out.append(ch.tail)
    return "".join(out)


def _render(el):
    tag = _local(el.tag)
    if tag == "lb":
        return _JOIN if el.get("break") == "no" else "\n"
    if tag == "gap":
        return " … "
    if tag in ("space", "g"):
        return " "
    if tag in _SKIP_TAGS:
        return ""
    if tag == "choice":
        # keep the regularised / corrected reading; drop the diplomatic variant
        for pref in ("reg", "corr"):
            c = el.find(TEI_NS + pref)
            if c is not None:
                return _render(c)
        kids = list(el)
        return _render(kids[0]) if kids else (el.text or "")
    if tag == "app":
        lem = el.find(TEI_NS + "lem")
        return _render(lem) if lem is not None else ""
    if tag == "supplied":
        return "[" + _inner(el) + "]"
    # expan, ex, abbr, num, hi, w, unclear, foreign, q, … -> inner text
    return _inner(el)


def render_edition(root):
    """Render the <div type="edition"> into a list of clean numbered Greek lines."""
    ed = None
    for div in root.iter(TEI_NS + "div"):
        if div.get("type") == "edition":
            ed = div
            break
    if ed is None:
        return []
    abs_ = list(ed.iter(TEI_NS + "ab"))
    if not abs_:
        return []
    raw = "\n".join(_render(ab) for ab in abs_)
    # glue word-splits flagged by <lb break="no"/> (drop surrounding whitespace)
    raw = re.sub(r"\s*" + _JOIN + r"\s*", "", raw)
    lines = [ln for ln in raw.split("\n")]
    # bfs.clean_greek normalises each line, drops apparatus/empty lines and keeps
    # only lines containing Greek (so Latin-only documents naturally fall away).
    return bfs.clean_greek(lines)


# ───────────────────────── DDB / HGV metadata parsing ──────────────────────
def parse_ddb(path):
    """Parse one DDB EpiDoc XML. Returns dict(hgv, hybrid, greek) or None."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return None
    hgv = hybrid = None
    for idno in root.iter(TEI_NS + "idno"):
        t = idno.get("type")
        if t == "HGV" and (idno.text or "").strip():
            hgv = idno.text.strip()
        elif t == "ddb-hybrid" and (idno.text or "").strip():
            hybrid = idno.text.strip()
    if not hybrid:
        return None
    greek = render_edition(root)
    if not greek:
        return None                       # stub <ab/> or no Greek preserved
    return {"hgv": hgv, "hybrid": hybrid, "greek": greek}


def iso_year(s):
    """'0209-01-23' -> 209 ; '-0030-...' -> -30 ; None/'' -> None."""
    if not s:
        return None
    m = re.match(r"\s*(-?)0*(\d+)", str(s))
    if not m:
        return None
    y = int(m.group(2))
    return -y if m.group(1) == "-" else y


def _year_label(y):
    return f"{abs(y)} {'BCE' if y < 0 else 'CE'}"


def hgv_date(root):
    """Date from history/origin/origDate: @when, else @notBefore–@notAfter, else prose."""
    od = next((e for e in root.iter(TEI_NS + "origDate")), None)
    if od is None:
        return "unknown"
    w = iso_year(od.get("when"))
    if w is not None:
        return _year_label(w)
    a, b = iso_year(od.get("notBefore")), iso_year(od.get("notAfter"))
    if a is not None or b is not None:
        if a is not None and b is not None:
            return _year_label(a) if a == b else f"{_year_label(a)} – {_year_label(b)}"
        return _year_label(a if a is not None else b)
    txt = bfs.clean_date("".join(od.itertext()))
    return txt or "unknown"


def hgv_meta(meta_root):
    """Pull (found, genre, date, pleiades_ids[], hgv_keywords, held) from an HGV meta XML."""
    # find-site: origin/origPlace text
    found = ""
    op = next((e for e in meta_root.iter(TEI_NS + "origPlace")), None)
    if op is not None:
        found = "".join(op.itertext()).strip()

    # genre: textClass/keywords[@scheme="hgv"]/term (German) -> GENRE_RULES, else documents
    terms = []
    for kw in meta_root.iter(TEI_NS + "keywords"):
        if kw.get("scheme") == "hgv":
            terms = [(t.text or "").strip() for t in kw.iter(TEI_NS + "term") if (t.text or "").strip()]
            break
    genre = bfs.classify(" ".join(terms)) or "documents"

    # Pleiades ids from every placeName @ref under the manuscript history, in
    # document order (settlement is listed first = most specific find-site).
    pl_ids = []
    for pn in meta_root.iter(TEI_NS + "placeName"):
        for pid in re.findall(r"pleiades\.stoa\.org/places/(\d+)", pn.get("ref") or ""):
            if pid not in pl_ids:
                pl_ids.append(pid)
        if not found and (pn.text or "").strip():
            found = pn.text.strip()

    # holding collection (msIdentifier/settlement), if it isn't an "unknown" stub
    held = ""
    for s in meta_root.iter(TEI_NS + "settlement"):
        v = (s.text or "").strip()
        if v and v.lower() not in ("unbekannt", "unknown", "?"):
            held = v
            break

    date = hgv_date(meta_root)
    # the descriptive (non-first) HGV terms make a useful German title for the translator
    hgv_kw = " — ".join(terms)
    return found or "unknown", genre, date, pl_ids, hgv_kw, held


def _text_no_notes(el):
    """Concatenate an element's running text (incl. tails after empty milestones),
    skipping any <note> subtree (the editor's 'Translation: ...' credit)."""
    parts = []
    if el.text:
        parts.append(el.text)
    for ch in el:
        if _local(ch.tag) != "note":
            parts.append(_text_no_notes(ch))
        if ch.tail:
            parts.append(ch.tail)
    return "".join(parts)


def hgv_english(trans_root):
    """Return the English HGV translation as a single prose string, or '' (German-only)."""
    for div in trans_root.iter(TEI_NS + "div"):
        if div.get("type") == "translation" and div.get(XML_LANG) == "en":
            return re.sub(r"\s+", " ", _text_no_notes(div)).strip()
    return ""


# ───────────────────────── Pleiades coordinate dump ─────────────────────────
def load_pleiades(path):
    """Return {pleiades_id(str) -> (lat, lon)} from pleiades-places-latest.csv.gz."""
    if not os.path.exists(path):
        print(f"  (no Pleiades dump at {os.path.basename(path)} — coords via COORDS only)")
        return {}
    out = {}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        r = csv.reader(fh)
        header = next(r)
        idx = {name: i for i, name in enumerate(header)}
        i_id = idx.get("id")
        i_lat = idx.get("reprLat")
        i_lon = idx.get("reprLong")
        if None in (i_id, i_lat, i_lon):
            i_id, i_lat, i_lon = 11, 17, 19          # known column layout fallback
        for row in r:
            try:
                pid = row[i_id].strip()
                lat = float(row[i_lat]); lon = float(row[i_lon])
            except (IndexError, ValueError):
                continue
            if pid:
                out[pid] = (lat, lon)
    return out


def resolve_coords(pl_ids, pleiades, found):
    """Pleiades id (most specific first) -> coords; else COORDS name map; else (None, None)."""
    for pid in pl_ids:
        if pid in pleiades:
            return pleiades[pid]
    return bfs.coords_for(found)


# ───────────────────────── data-tree discovery ─────────────────────────
def find_trees(root):
    """Locate the DDB/HGV-meta/HGV-trans trees under `root` (handles a nested folder)."""
    root = os.path.abspath(root)
    for dirpath, dirnames, _ in os.walk(root):
        if "DDB_EpiDoc_XML" in dirnames:
            return (os.path.join(dirpath, "DDB_EpiDoc_XML"),
                    os.path.join(dirpath, "HGV_meta_EpiDoc"),
                    os.path.join(dirpath, "HGV_trans_EpiDoc"))
        # don't descend into the huge data trees while searching for the base
        for big in ("DDB_EpiDoc_XML", "HGV_meta_EpiDoc", "HGV_trans_EpiDoc",
                    "DCLP", "APIS", "Biblio", "RDF"):
            if big in dirnames:
                dirnames.remove(big)
    raise SystemExit(f"DDB_EpiDoc_XML not found anywhere under {root}")


def meta_path(meta_dir, hgv):
    """HGV N -> HGV_meta_EpiDoc/HGV{ceil(N/1000)}/N.xml (the dump's bucketing)."""
    try:
        n = int(hgv)
    except (TypeError, ValueError):
        return None
    bucket = -(-n // 1000)               # ceil(n/1000)
    return os.path.join(meta_dir, f"HGV{bucket}", f"{n}.xml")


# ───────────────────────── .txt writer ─────────────────────────
def write_manuscript(rec, ddb_dir, meta_dir, trans_dir, pleiades):
    """Build one manuscripts/<slug>.txt from a parsed DDB record. Returns slug or None."""
    hybrid, hgv, greek = rec["hybrid"], rec["hgv"], rec["greek"]
    cite = bfs.citation(hybrid)
    s = bfs.slug(hybrid)

    found, genre, date, pl_ids, hgv_kw, held = "unknown", "documents", "unknown", [], "", ""
    mp = meta_path(meta_dir, hgv)
    if mp and os.path.exists(mp):
        try:
            mroot = ET.parse(mp).getroot()
            found, genre, date, pl_ids, hgv_kw, held = hgv_meta(mroot)
        except ET.ParseError:
            pass

    lat, lon = resolve_coords(pl_ids, pleiades, found)

    en = ""
    if hgv:
        tp = os.path.join(trans_dir, f"{int(hgv)}.xml") if str(hgv).isdigit() else None
        if tp and os.path.exists(tp):
            try:
                en = hgv_english(ET.parse(tp).getroot())
            except ET.ParseError:
                en = ""

    label = GENRE_LABEL.get(genre, "Documentary papyrus")
    name = f"{label} — {found}" if found and found != "unknown" else label
    content = f"{label} from {found} ({date})" if found != "unknown" else f"{label} ({date})"

    out = ["[META]"]
    out.append(f"id:       {cite}")
    out.append(f"label:    {cite}")
    out.append(f"name:     {name}")
    out.append(f"genre:    {genre}")
    out.append(f"date:     {bfs.clean_date(date)}")
    out.append("language: Greek (Koiné)")
    out.append(f"found:    {found}")
    out.append(f"held:     {held}")
    out.append("shelf:    ")
    out.append(f"content:  {content}")
    if hgv_kw:
        out.append(f"# hgv-keywords: {hgv_kw}")
    out.append(f"tm:       {hgv or ''}")
    out.append(f"source:   https://papyri.info/ddbdp/{hybrid}")
    out.append(f"lat:      {lat if lat is not None else ''}")
    out.append(f"lon:      {lon if lon is not None else ''}")
    out.append("")
    out.append("[GREEK]")
    for i, g in enumerate(greek, 1):
        out.append(f"r.{i:<4} {g}")
    out.append("")
    out.append("[TRANSLATION]")
    if en:
        out.append(f"# HGV-EN: {en}")
        out.append("# ^ reference only (HGV prose) — lay it out line-by-line in the slots below.")
    for i in range(1, len(greek) + 1):
        out.append(f"{i:<5} ")          # one blank numbered slot per Greek line

    path = os.path.join(MSS, s + ".txt")
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    return s


# ───────────────────────── crawl + build ─────────────────────────
def crawl(ddb_dir):
    """Walk DDB_EpiDoc_XML, yielding parsed records that have Greek. Prints progress."""
    files = []
    for dp, _, fns in os.walk(ddb_dir):
        for fn in fns:
            if fn.endswith(".xml"):
                files.append(os.path.join(dp, fn))
    files.sort()
    print(f"Scanning {len(files)} DDB EpiDoc files…")
    recs = []
    for i, fn in enumerate(files):
        rec = parse_ddb(fn)
        if rec is not None:
            recs.append(rec)
        if (i + 1) % 10000 == 0:
            print(f"  …{i + 1}/{len(files)} scanned, {len(recs)} with Greek")
    print(f"Parsed {len(recs)} papyri with preserved Greek.")
    return recs


def run(args):
    ddb_dir, meta_dir, trans_dir = find_trees(args.path)
    print(f"DDB:   {ddb_dir}")
    print(f"meta:  {meta_dir}")
    print(f"trans: {trans_dir}")
    pleiades = load_pleiades(PLEIADES_GZ)
    print(f"Pleiades coordinates: {len(pleiades)} places")

    recs = crawl(ddb_dir)

    # additive + safe: never overwrite an existing manuscripts/<slug>.txt
    os.makedirs(MSS, exist_ok=True)
    have = {os.path.splitext(f)[0] for f in os.listdir(MSS) if f.endswith(".txt")}
    fresh = [r for r in recs if bfs.slug(r["hybrid"]) not in have]
    skipped_existing = len(recs) - len(fresh)

    # best-preserved (most Greek text) first
    fresh.sort(key=lambda r: sum(len(g) for g in r["greek"]), reverse=True)

    if args.inspect:
        print(f"\n{len(fresh)} new candidates (skipped {skipped_existing} already present). "
              f"Top {min(5, len(fresh))} derived records:")
        for r in fresh[:5]:
            s = bfs.slug(r["hybrid"])
            mp = meta_path(meta_dir, r["hgv"])
            found = genre = date = "?"; pl_ids = []
            if mp and os.path.exists(mp):
                found, genre, date, pl_ids, _, _ = hgv_meta(ET.parse(mp).getroot())
            lat, lon = resolve_coords(pl_ids, pleiades, found)
            print(f"  {bfs.citation(r['hybrid']):16} {s:20} {genre:11} {date:14} "
                  f"{found[:24]:24} ({lat},{lon}) {len(r['greek'])} lines")
        return

    selected = fresh[: args.cap]
    print(f"\nWriting {len(selected)} papyri (cap {args.cap}; "
          f"{skipped_existing} already present, skipped)…")

    built, by_genre, with_en, with_coords = 0, {}, 0, 0
    for r in selected:
        s = write_manuscript(r, ddb_dir, meta_dir, trans_dir, pleiades)
        if s:
            built += 1
            # (cheap re-derive only for the summary counters)
            txt = open(os.path.join(MSS, s + ".txt"), encoding="utf-8").read()
            g = re.search(r"^genre:\s*(\S+)", txt, re.M)
            if g:
                by_genre[g.group(1)] = by_genre.get(g.group(1), 0) + 1
            if "# HGV-EN:" in txt:
                with_en += 1
            if re.search(r"^lat:\s*-?\d", txt, re.M):
                with_coords += 1

    print(f"\nWrote {built} manuscripts to {MSS}")
    print("By genre:", ", ".join(f"{k}: {v}" for k, v in sorted(by_genre.items())) or "(none)")
    print(f"With coordinates: {with_coords}/{built} | with HGV-EN reference: {with_en}/{built}")
    print("Next: py check_city_nodes.py  (add nodes for any orphan find-sites), then translate.")


# ───────────────────────── selftest ─────────────────────────
_SELFTEST_DDB = """<?xml version="1.0"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader><fileDesc><publicationStmt>
    <idno type="ddb-hybrid">bgu;1;2</idno>
    <idno type="HGV">8961</idno>
  </publicationStmt></fileDesc></teiHeader>
  <text><body>
    <div xml:lang="grc" type="edition"><ab>
      <lb n="1"/><choice><reg>Ἀπολλοφάνῃ</reg><orig>Ἀπολλοφάνι</orig></choice> <supplied reason="lost">τ</supplied>ῷ <expan>στρ<ex>ατηγῷ</ex></expan>
      <lb n="2"/>παρὰ Ἑριεῦτος ἀπὸ <supplied reason="lost">κ</supplied>ώμης Σοκνο<lb n="3" break="no"/>παίου Νήσου <gap reason="lost"/> οἱ <num value="4">δ</num>
      <lb n="4"/>καὶ <app type="editorial"><lem>Πετρώνιος</lem><rdg>Πατρώνιος</rdg></app> .
    </ab></div>
  </body></text>
</TEI>"""

_SELFTEST_META = """<?xml version="1.0"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
 <teiHeader><fileDesc><sourceDesc><msDesc>
  <msIdentifier><placeName><settlement>unbekannt</settlement></placeName></msIdentifier>
  <history><origin>
    <origPlace>Soknopaiu Nesos (Arsinoites)</origPlace>
    <origDate when="0209-01-23">23. Jan. 209</origDate>
  </origin>
  <provenance type="located"><p>
    <placeName type="ancient" ref="https://pleiades.stoa.org/places/737053 https://www.trismegistos.org/place/2157">Soknopaiu Nesos</placeName>
  </p></provenance></history>
 </msDesc></sourceDesc>
 <profileDesc><textClass><keywords scheme="hgv">
   <term>Eingabe</term><term>Herieus an den Strategen</term>
 </keywords></textClass></profileDesc>
 </fileDesc></teiHeader>
</TEI>"""

_SELFTEST_TRANS = """<?xml version="1.0"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:lang="en">
 <text><body>
  <div xml:lang="de" type="translation"><p>Eine deutsche Übersetzung.</p></div>
  <div xml:lang="en" type="translation"><p>
    <milestone n="1" unit="line"/> To Apollophanes, strategos.
    <note>Translation: Someone</note></p></div>
 </body></text>
</TEI>"""


def selftest():
    ok = True

    def check(label, got, want):
        nonlocal ok
        good = (want in got) if isinstance(want, str) else (got == want)
        print(f"  [{'OK ' if good else 'FAIL'}] {label}: {got!r}")
        ok = ok and good

    droot = ET.fromstring(_SELFTEST_DDB)
    greek = render_edition(droot)
    check("greek line count (lb break=no merges 2&3)", len(greek), 3)
    check("reg reading kept", greek[0], "Ἀπολλοφάνῃ")
    check("supplied -> [..]", greek[0], "[τ]ῷ")
    check("expan clean (no parens)", greek[0], "στρατηγῷ")
    check("break=no join", " ".join(greek), "Σοκνοπαίου")
    check("gap -> ellipsis", " ".join(greek), "…")
    check("app keeps lem", " ".join(greek), "Πετρώνιος")
    check("app drops rdg", "Πατρώνιος" not in " ".join(greek), True)

    mroot = ET.fromstring(_SELFTEST_META)
    found, genre, date, pl_ids, hgv_kw, held = hgv_meta(mroot)
    check("found (origPlace)", found, "Soknopaiu Nesos")
    check("genre (Eingabe->petitions)", genre, "petitions")
    check("date (when->CE)", date, "209 CE")
    check("pleiades id parsed", pl_ids, ["737053"])

    troot = ET.fromstring(_SELFTEST_TRANS)
    en = hgv_english(troot)
    check("english picked over german", "Apollophanes" in en, True)
    check("german not used", "deutsche" not in en, True)

    check("iso_year BCE", iso_year("-0030-01-01"), -30)
    check("citation", bfs.citation("bgu;1;2"), "BGU 1.2")
    check("slug", bfs.slug("bgu;1;2"), "bgu_1_2")

    print("\nSELFTEST:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser(description="Onboard documentary papyri from a local idp.data dump.")
    ap.add_argument("path", nargs="?", help="path to the idp.data dump (dir containing the EpiDoc trees)")
    ap.add_argument("--cap", type=int, default=2000, help="max NEW papyri to write (best-preserved first)")
    ap.add_argument("--add", action="store_true",
                    help="additive (the default): skip any papyrus whose .txt already exists")
    ap.add_argument("--inspect", action="store_true", help="print derived metadata for a few candidates, write nothing")
    ap.add_argument("--selftest", action="store_true", help="offline parser sanity check")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return
    if not args.path:
        ap.error("the idp.data dump path is required (or use --selftest)")
    run(args)


if __name__ == "__main__":
    main()

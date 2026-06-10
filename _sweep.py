#!/usr/bin/env python
"""_sweep.py — scrape a DDbDP series-range to JSON (per-id retry/backoff).

  python _sweep.py o.wilck;;261-310           # -> _sweep_o.wilck_261-310.json
Reads FIRECRAWL_API_KEY from env. Models scrape_papyrus.extract() per id.
"""
import os, re, sys, json, time

try:
    import truststore; truststore.inject_into_ssl()
except ImportError:
    pass
from firecrawl import Firecrawl

GREEK = r"Ͱ-Ͽἀ-῿"
KEY = os.environ.get("FIRECRAWL_API_KEY")
if not KEY:
    sys.exit("ERROR: FIRECRAWL_API_KEY not set")
APP = Firecrawl(api_key=KEY)


def first(pat, text, g=1, flags=re.I):
    m = re.search(pat, text, flags); return m.group(g).strip() if m else None


def extract(md):
    o = {}
    o["tm"] = first(r"trismegistos\.org/text/(\d+)", md)
    o["subjects"] = first(r"\|\s*Subjects?\s*\|\s*([^|<\n]+)", md)
    o["shelf"] = first(r"\|\s*Inv\.?\s*no\.?\s*\|\s*\[?([^\]|<\n]+)", md)
    o["origin"] = first(r"\|\s*Origin\s*\|\s*([^|<\n]+)", md)
    o["date"] = (first(r"\|\s*Date\s*\|\s*([^|<\n]+)", md)
                 or first(r"\|\s*Datierung\s*\|\s*([^|<\n]+)", md))
    gk = []
    for line in md.splitlines():
        if re.search("[" + GREEK + "]", line):
            c = re.sub(r"\[[^\]]*\]\([^)]*\)", "", line)
            c = re.sub(r"\s+", " ", c).strip(" |")
            if re.search("[" + GREEK + "]", c):
                gk.append(c)
    o["greek"] = gk
    return o


def scrape_one(ident, tries=4):
    url = "https://papyri.info/ddbdp/" + ident
    for t in range(tries):
        try:
            doc = APP.scrape(url)
            md = getattr(doc, "markdown", None) or ""
            if md:
                return extract(md)
        except Exception as e:
            sys.stderr.write(f"  {ident} try{t+1} err: {str(e)[:80]}\n")
        time.sleep(2 * (t + 1))
    return {"tm": None, "subjects": None, "shelf": None,
            "origin": None, "date": None, "greek": []}


def main():
    rng = sys.argv[1]                       # o.wilck;;261-310
    series, lohi = rng.rsplit(";;", 1)
    lo, hi = (int(x) for x in lohi.split("-"))
    out = {}
    for n in range(lo, hi + 1):
        ident = f"{series};;{n}"
        rec = scrape_one(ident)
        out[ident] = rec
        ng = len(rec["greek"])
        sys.stderr.write(f"[{n-lo+1}/{hi-lo+1}] {ident}: {ng} gk  {rec.get('subjects') or ''}\n")
    slug = rng.replace(";;", "_").replace(";", "_")
    path = f"C:/ManuscriptDB/_sweep_{slug}.json"
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("SAVED", path, "records:", len(out))


if __name__ == "__main__":
    main()

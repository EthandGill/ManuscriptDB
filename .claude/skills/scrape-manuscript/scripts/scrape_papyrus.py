#!/usr/bin/env python
"""
scrape_papyrus.py — fetch a documentary papyrus from papyri.info via Firecrawl
and pull out the fields ManuscriptDB needs.

Firecrawl renders JavaScript and clears the "Anubis" bot-gate that blocks plain
requests/WebFetch on papyri.info, so it returns both the HGV/APIS metadata AND
the Greek transcription. truststore makes Python trust the Windows cert store
(this machine does TLS inspection, which otherwise breaks verification).

Usage:
  set FIRECRAWL_API_KEY env var first, then:
    python scrape_papyrus.py bgu;1;2
    python scrape_papyrus.py p.oxy;1;1 --out raw.md
    python scrape_papyrus.py https://papyri.info/ddbdp/bgu;1;2   # full URL also ok

Prints a structured block:
    TM / ORIGIN / DATE / SUPPORT / TITLE / and the GREEK transcription lines.
The author (you) then translates the Greek and writes the .txt — see SKILL.md.
"""
import argparse
import os
import re
import sys

try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from firecrawl import Firecrawl

GREEK = r"Ͱ-Ͽἀ-῿"


def to_url(ident):
    if ident.startswith("http"):
        return ident
    # bare ddbdp id like "bgu;1;2" or "p.oxy;1;1"
    return "https://papyri.info/ddbdp/" + ident.strip().lstrip("/")


def scrape_markdown(url):
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        sys.exit("ERROR: set the FIRECRAWL_API_KEY environment variable first.")
    app = Firecrawl(api_key=api_key)
    doc = app.scrape(url)
    return getattr(doc, "markdown", None) or ""


def first(pattern, text, group=1, flags=re.I):
    m = re.search(pattern, text, flags)
    return m.group(group).strip() if m else None


def extract(md):
    info = {}
    info["tm"] = first(r"trismegistos\.org/text/(\d+)", md)
    # HGV metadata table rows look like:  | Origin | Soknopaiu Nesos (Arsinoites) ... |
    info["origin"] = first(r"\|\s*Origin\s*\|\s*([^|<\n]+)", md)
    info["date"] = (first(r"\|\s*Date\s*\|\s*([^|<\n]+)", md)
                    or first(r"\|\s*Datierung\s*\|\s*([^|<\n]+)", md))
    info["support"] = first(r"\|\s*Support(?:/Dimensions)?\s*\|\s*([^|<\n]+)", md)
    info["title"] = first(r"\|\s*Title\s*\|\s*([^|<\n]+)", md)
    # canonical id (e.g. "bgu.1.2 = HGV ...")
    info["citation"] = first(r"###\s*([a-z][a-z0-9.;]+\s*=\s*HGV[^\n]+)", md)
    # Greek transcription lines: keep lines that actually contain Greek glyphs.
    greek_lines = []
    for line in md.splitlines():
        if re.search("[" + GREEK + "]", line):
            # strip markdown link noise [ (\*) ](...) and footnote refs
            clean = re.sub(r"\[[^\]]*\]\([^)]*\)", "", line)
            clean = re.sub(r"\s+", " ", clean).strip(" |")
            if re.search("[" + GREEK + "]", clean):
                greek_lines.append(clean)
    info["greek_lines"] = greek_lines
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ident", help="ddbdp id (e.g. bgu;1;2) or full papyri.info URL")
    ap.add_argument("--out", help="also save the full raw markdown here")
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    url = to_url(args.ident)
    md = scrape_markdown(url)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)

    info = extract(md)
    print("URL:       ", url)
    print("CITATION:  ", info["citation"])
    print("TM:        ", info["tm"])
    print("ORIGIN:    ", info["origin"])
    print("DATE:      ", info["date"])
    print("SUPPORT:   ", info["support"])
    print("TITLE:     ", info["title"])
    print("RAW chars: ", len(md))
    print("--- GREEK TRANSCRIPTION (%d lines) ---" % len(info["greek_lines"]))
    for i, ln in enumerate(info["greek_lines"], 1):
        print(f"{i:>3}  {ln}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
firecrawl_scrape.py — thin wrapper around Firecrawl for the ManuscriptDB project.

Why this exists:
  * Firecrawl renders JavaScript and clears bot-checks (e.g. the "Anubis" gate
    on papyri.info) that plain WebFetch/requests cannot get past — so it's the
    way to pull real manuscript data from papyri.info / Trismegistos / NTVMR.
  * On this machine, TLS inspection injects a root cert that lives in the
    Windows cert store but not in Python's certifi bundle, so requests fail with
    CERTIFICATE_VERIFY_FAILED. `truststore.inject_into_ssl()` makes Python trust
    the OS cert store and fixes it (verification stays ON).

Setup (once):
  pip install firecrawl-py truststore
  set the API key as an env var (do NOT hardcode it in the repo):
      PowerShell:  $env:FIRECRAWL_API_KEY = "fc-..."
      bash:        export FIRECRAWL_API_KEY="fc-..."

Usage:
  python firecrawl_scrape.py https://papyri.info/ddbdp/bgu;1;2
  python firecrawl_scrape.py <url> --out out.md          # save markdown to file
  python firecrawl_scrape.py <url> --format html         # markdown (default) | html
"""
import argparse
import os
import sys

try:
    import truststore
    truststore.inject_into_ssl()          # trust the Windows cert store (fixes TLS)
except ImportError:
    pass                                   # not fatal if certs already validate

from firecrawl import Firecrawl


def scrape(url, fmt="markdown"):
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        sys.exit("ERROR: set the FIRECRAWL_API_KEY environment variable first.")
    app = Firecrawl(api_key=api_key)
    doc = app.scrape(url)
    return getattr(doc, fmt, None) or ""


def main():
    ap = argparse.ArgumentParser(description="Scrape a URL with Firecrawl.")
    ap.add_argument("url", help="URL to scrape")
    ap.add_argument("--format", default="markdown", choices=["markdown", "html"],
                    help="content field to return (default: markdown)")
    ap.add_argument("--out", help="write the content to this file instead of stdout")
    args = ap.parse_args()

    content = scrape(args.url, args.format)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Wrote {len(content)} chars to {args.out}")
    else:
        sys.stdout.reconfigure(encoding="utf-8")   # avoid cp1252 console errors
        print(content)


if __name__ == "__main__":
    main()

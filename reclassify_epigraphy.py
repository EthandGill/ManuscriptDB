#!/usr/bin/env python3
"""reclassify_epigraphy.py — split a new "defixio" (curse tablet) genre out of
"public" in static/epigraphy_data.js, IN PLACE.

Parses out the `window.EPIGRAPHY_DATA = [...]` array, changes ONLY the `genre`
field of matching records, and writes the file back with the identical wrapper
and JSON style (translation and every other field untouched).

Rule — a record becomes genre "defixio" if its `name` contains "Curse tablet"
(case-insensitive) OR its joined `text` matches /\\bdefixi|defigo|devoveo/i.
(~22 records, all currently "public"; the edh_ingest.py classify() change keeps
future re-ingests consistent.)
"""

import os, re, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "static", "epigraphy_data.js")
PREFIX = "window.EPIGRAPHY_DATA = "
DEFIXIO_RE = re.compile(r"\bdefixi|defigo|devoveo", re.IGNORECASE)


def joined_text(rec):
    t = rec.get("text")
    if isinstance(t, list):
        return " ".join(str(x) for x in t)
    return str(t or "")


def is_defixio(rec):
    name = str(rec.get("name") or "")
    if "curse tablet" in name.lower():
        return True
    return bool(DEFIXIO_RE.search(joined_text(rec)))


def dist(records):
    return collections.Counter(r.get("genre") for r in records)


def main():
    raw = open(DATA, encoding="utf-8").read()
    cut = raw.index(PREFIX)
    header = raw[:cut]
    body = raw[cut + len(PREFIX):].strip()
    if body.endswith(";"):
        body = body[:-1]
    records = json.loads(body)

    before = dist(records)
    changed = 0
    for r in records:
        if is_defixio(r) and r.get("genre") != "defixio":
            r["genre"] = "defixio"
            changed += 1
    after = dist(records)

    # write back: identical wrapper + default JSON separators (matches the file)
    out = header + PREFIX + json.dumps(records, ensure_ascii=False) + ";\n"
    open(DATA, "w", encoding="utf-8").write(out)

    keys = sorted(set(before) | set(after))
    print(f"Reclassified {changed} records to 'defixio'.")
    print(f"{'genre':14} {'before':>7} {'after':>7}")
    for k in keys:
        print(f"{str(k):14} {before.get(k,0):>7} {after.get(k,0):>7}")


if __name__ == "__main__":
    main()

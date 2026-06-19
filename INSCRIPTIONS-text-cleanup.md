# Inscription text cleanup: strip EDH "#" multi-reading artifacts

EDH's EpiDoc edition text encodes some words as several `#`-separated readings,
and our `edh_ingest` renderer copied all of them into the displayed Greek/Latin.
A word like Silvinius appears as:

```
SilIvinius#Si[l]vinius#SIIVINIUS
```

i.e. `<merged-blob>#<interpretive>#<DIPLOMATIC-CAPS>`. Only the **middle** form —
the scholarly interpretive reading, lowercase with `[restorations]` / `(expansions)`
— is what's actually meant to display. The merged blob, the ALL-CAPS diplomatic
(letters as carved), and the `#` separators are noise.

Scope: ~485 inscriptions, ~1,176 affected tokens. Verified examples:
- `aderuInt#ader[u]nt#ADERINT` → `ader[u]nt`
- `colonor[um=I]#colonor[um]#COLONORI` → `colonor[um]`
- `redem<p=I>tori#redem[p]tori#REDEMITORI` → `redem[p]tori`
- HD022154 last line `…v(o)ta#DPVTA ac dicat…` → `…vota ac dicata…` (clean: "devota")
- CIMRM 1247 `…SilIvinius#Si[l]vinius#SIIVINIUS Aurelius` → `…Silvinius Aurelius`

(Papyri from idp.data are a different source and have no `#` artifact — leave them alone.)

## The rule

For each `#`-delimited group, **keep the interpretive reading** and drop the rest:
- Prefer the segment containing `[` or `(` (restoration/expansion brackets), or
  with lowercase letters; reject an ALL-CAPS segment (the diplomatic) and the
  garbled merge. When 3 segments → keep the middle (bracketed) one; when 2 → keep
  the bracketed/lowercase one.
- Remove the `#` separators. Lines/tokens with no `#` must be left **byte-for-byte
  unchanged**.
- Beware groups that span a space (e.g. `[t=RE]#qua[e]re#QUAERERE` split oddly):
  operate on whole `#`-groups, not naively on space-tokens — test against the real
  data, not just the examples above.

## Do it two ways

1. **Clean the already-loaded inscriptions in place** — write `clean_inscriptions.py`:
   parse `static/epigraphy_data.js`, apply the rule to every line of each record's
   `text` (a list of lines), and write the file back. Change ONLY `text`; preserve
   `translation`, `genre`, `title`, coordinates, everything else. Token-free.
2. **Fix the source** so future inscription pulls are clean — apply the same
   stripping inside `edh_ingest.py` (in the edition-rendering path, after `_render`),
   so `edh_ingest … --add` never re-introduces `#` artifacts.

## Verify (must pass)

- After cleaning, `grep '#'` across the inscription `text` finds **zero** remaining
  (search the regenerated `static/epigraphy_data.js`).
- HD022154 reads "…devota ac dicata maiestati eius…"; CIMRM 1247's last line ends
  "…Silvinius Aurelius".
- Spot-check 10 inscriptions that never had a `#`: their `text` is identical before
  and after (diff them).
- Record count and translations unchanged; `py app.py` and open a cleaned one — the
  Latin reads cleanly, `[restorations]` still blue.
- Publish: `update_website.bat`.

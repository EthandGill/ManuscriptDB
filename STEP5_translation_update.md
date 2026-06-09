<!--
  Drop-in replacement for the "## Step 5 — Add translations" section of
  .claude/skills/grab-manuscript/SKILL.md

  (The .claude folder is write-protected in Cowork sessions, so paste this in
  manually — replace the old Step 5 block with everything between the rules below.)
-->

---

## Step 5 — Add translations (faithful to THIS manuscript's Greek)

Do **not** paste the generic ESV wording for the verse numbers. Translate the
text the papyrus actually preserves, reflecting its own readings where they
differ from the standard text. Use `extract_verses.py` to make this fast.

### 5a. Generate a verse-aligned Greek scaffold

The importer lays the Greek out by physical line (`r.1`, `r.2`, …) with no verse
markers. `extract_verses.py` re-fetches the same NTVMR pages, reads the TEI
`<ab n="B07K7V10">` verse anchors, and reassembles the manuscript's actual Greek
grouped *per verse* — re-joining split words, keeping `[reconstructions]` and
`{nomina sacra}`, and marking gaps with `…`.

```bash
cd C:\ManuscriptDB
python extract_verses.py --docID <docID> --id P<N> --pages <same page IDs as import> \
    --out manuscripts\P<N>.translation.txt
```

This writes a ready-to-fill `[TRANSLATION]` block. Each verse looks like:

```
# 7:18   GK: [σπα]σθω εν ακροβυστια τις κε[κλη]ται μη περιτεμνεσθω η περιτομη …
7:18
```

(The `GK:` line is a comment showing the real Greek; the bare line below it is
where the English goes.)

### 5b. Translate each verse FROM the Greek shown

For every verse, read the `GK:` line and write a faithful English rendering of
*that* text on the line beneath it:

- Reflect this manuscript's variant readings, word order, and any pluses/minuses
  versus the standard text — the point of the database is to show what each
  witness actually says.
- The bracketed `[...]` portions are editorially reconstructed but are part of
  the verse; translate the full reconstructed verse (smooth English).
- `{nomen sacrum}` words are ordinary sacred names/titles in translation
  (`{θυ}` → "God", `{κυ}` → "Lord", `{ιυ}` `{χυ}` → "Jesus" / "Christ", etc.).
- `…` marks text the papyrus does not preserve at all; render the surrounding
  sense naturally and don't invent content for a long gap.
- If this manuscript's reading is a noteworthy variant from the standard text,
  it's fine to translate it as it stands (that divergence is the interesting part).

### 5c. Move the finished block into the .txt file

Replace the commented `# [TRANSLATION]` placeholder in `manuscripts/P<N>.txt`
with your completed block. Delete the `# … GK:` comment lines once translated
(or keep them as comments if you want the Greek visible in-file — they begin
with `#` so the parser ignores them). The final result is the same format the
app already expects:

```
[TRANSLATION]
7:18   Was anyone already circumcised when called? ...
7:19   ...
```

**For multi-book manuscripts** (e.g. P34, P46): `extract_verses.py` detects
multiple books from the verse anchors and emits matching `[TRANSLATION:1 Corinthians]`
/ `[TRANSLATION:2 Corinthians]` headers automatically — keep those section
headers when you move the block in.

> Tip: run `python extract_verses.py --selftest` once to confirm the parser is
> working (offline, no network) before relying on it for a new manuscript.

---

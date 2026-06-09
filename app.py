from flask import Flask, render_template, jsonify, request
import os, re, gzip

app = Flask(__name__)
# Preserve dict insertion order in JSON responses (default sorts alphabetically)
app.json.sort_keys = False


@app.after_request
def gzip_large_responses(response):
    """Gzip large responses. The Werkzeug dev server intermittently drops the
    body of multi-MB responses on Windows, which truncates the ~7.8 MB
    /api/manuscripts feed and breaks the frontend. Compressing it to ~1 MB
    keeps it well within the size the dev server delivers reliably."""
    accepts = request.headers.get("Accept-Encoding", "")
    if (
        "gzip" in accepts.lower()
        and response.direct_passthrough is False
        and response.content_length is not None
        and response.content_length > 1024
        and "Content-Encoding" not in response.headers
    ):
        data = gzip.compress(response.get_data(), compresslevel=6)
        response.set_data(data)
        response.headers["Content-Encoding"] = "gzip"
        response.headers["Content-Length"] = str(len(data))
        response.headers["Vary"] = "Accept-Encoding"
    return response

MANUSCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "manuscripts")

def parse_manuscript(filepath):
    with open(filepath, encoding="utf-8") as f:
        raw = f.read()

    def section(tag):
        m = re.search(rf"\[{tag}\](.*?)(?=\n\[|\Z)", raw, re.S)
        return m.group(1).strip() if m else ""

    # --- META ---
    meta = {}
    for line in section("META").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()

    # --- PARSE GREEK LINES helper ---
    def _parse_greek_lines(text):
        result = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("FOLIO"):
                folio_label = line.split(None, 1)[1].strip() if len(line.split(None, 1)) > 1 else ""
                result.append({"sep": "folio", "text": folio_label})
                continue
            m = re.match(r"^([rv]\.\d+)\s+(.*)", line)
            if m:
                ref, txt = m.group(1), m.group(2).strip()
                if txt.upper().startswith("GAP:"):
                    gap_note = txt[4:].strip()  # anything after "GAP:"
                    result.append({"sep": "gap", "text": gap_note})
                else:
                    txt = re.sub(r"\{([^}]+)\}", r"__NOM__\1__END__", txt)
                    txt = re.sub(r"\[([^\]]+)\]", r"__SUP__\1__END__", txt)
                    result.append({"ref": ref, "text": txt})
        return result

    # --- PARSE TRANSLATION LINES helper ---
    def _parse_trans_lines(text):
        result = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # FOLIO headers mirror the Greek section, so the English column can
            # show the same recto/verso (folio) breaks.
            if line.startswith("FOLIO"):
                parts = line.split(None, 1)
                folio_label = parts[1].strip() if len(parts) > 1 else ""
                result.append({"sep": "folio", "text": folio_label})
                continue
            m = re.match(r"^([\d:]+)\s+(.*)", line)
            if m:
                result.append({"ref": m.group(1), "text": m.group(2).strip()})
        return result

    # --- CHECK FOR NAMED SECTIONS [GREEK:Book], [TRANSLATION:Book] ---
    named_greek_books   = re.findall(r'\[GREEK:([^\]]+)\]', raw)
    named_trans_books   = re.findall(r'\[TRANSLATION:([^\]]+)\]', raw)
    named_content_books = re.findall(r'\[CONTENT:([^\]]+)\]', raw)

    sections = None
    if named_greek_books or named_trans_books:
        sections = {}
        all_books = list(dict.fromkeys(
            named_greek_books + named_trans_books + named_content_books
        ))  # ordered, deduplicated
        for book in all_books:
            tag_g = re.escape(book)
            gm = re.search(rf'\[GREEK:{tag_g}\](.*?)(?=\n\[|\Z)',       raw, re.S)
            tm = re.search(rf'\[TRANSLATION:{tag_g}\](.*?)(?=\n\[|\Z)', raw, re.S)
            cm = re.search(rf'\[CONTENT:{tag_g}\](.*?)(?=\n\[|\Z)',      raw, re.S)
            sections[book] = {
                "greek":       _parse_greek_lines(gm.group(1).strip()) if gm else [],
                "translation": _parse_trans_lines(tm.group(1).strip()) if tm else [],
                "content":     cm.group(1).strip() if cm else "",
            }
        # Top-level greek / translation = first named book (backward compat)
        first = named_greek_books[0] if named_greek_books else named_trans_books[0]
        greek       = sections[first]["greek"]
        translation = sections[first]["translation"]
    else:
        # Flat single-book format
        greek       = _parse_greek_lines(section("GREEK"))
        translation = _parse_trans_lines(section("TRANSLATION"))

    # Coerce numeric fields
    for field in ("lat", "lon"):
        if field in meta:
            try:
                meta[field] = float(meta[field])
            except ValueError:
                pass

    # book: support comma-separated multi-book (e.g. "Matthew, Mark")
    if "book" in meta:
        meta["books"] = [b.strip() for b in meta["book"].split(",")]
    else:
        meta["books"] = []

    # label defaults to id if not set
    if "label" not in meta and "id" in meta:
        meta["label"] = meta["id"]

    result = {**meta, "greek": greek, "translation": translation}
    if sections:
        result["sections"] = sections
    return result


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/manuscripts")
def api_manuscripts():
    results = []
    if os.path.isdir(MANUSCRIPTS_DIR):
        for fname in sorted(os.listdir(MANUSCRIPTS_DIR)):
            if fname.endswith(".txt"):
                try:
                    results.append(parse_manuscript(
                        os.path.join(MANUSCRIPTS_DIR, fname)
                    ))
                except Exception as e:
                    results.append({"error": str(e), "file": fname})
    return jsonify(results)


if __name__ == "__main__":
    # threaded=True lets the dev server reliably stream large responses
    # (the /api/manuscripts feed is ~7.8 MB); single-threaded mode drops
    # the body mid-transfer on Windows/Python 3.14.
    app.run(debug=True, threaded=True)

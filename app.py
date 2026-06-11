from flask import Flask, render_template, jsonify, request, redirect
import os, re, gzip

app = Flask(__name__)
# Preserve dict insertion order in JSON responses (default sorts alphabetically)
app.json.sort_keys = False

# Email accounts + freemium metering for the search agent (see accounts.py).
from accounts import init_accounts, current_user, consume_quota
init_accounts(app)

# Stripe subscriptions ($10 CAD/mo unlimited) — see stripe_billing.py.
from stripe_billing import init_billing
init_billing(app)


@app.before_request
def force_https():
    """Redirect insecure http:// visitors to https://.

    Railway terminates TLS at its edge and forwards the original scheme in the
    X-Forwarded-Proto header. We only redirect when that header explicitly says
    "http", so this never fires on the local dev server (where the header is
    absent) — `python app.py` on localhost keeps working over http as before."""
    if request.headers.get("X-Forwarded-Proto") == "http":
        return redirect(request.url.replace("http://", "https://", 1), code=301)


@app.after_request
def security_headers(response):
    """Tell browsers to stick to HTTPS on future visits (HSTS). Only sent when
    the request actually arrived over https, so local http dev is unaffected."""
    if request.headers.get("X-Forwarded-Proto") == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"

    # Map tiles never change once generated, so let browsers AND Railway's edge
    # CDN cache them for a year. This makes repeat views instant and lets the
    # CDN serve them from a location near each visitor instead of from origin.
    if request.path.startswith("/static/tiles/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return response


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
        # Skip map tiles / images: PNGs are already compressed, so gzipping them
        # wastes CPU and slows the response without shrinking the payload.
        and not request.path.startswith("/static/tiles/")
        and not (response.mimetype or "").startswith("image/")
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


# Parsing all ~745 manuscript files takes seconds; the data only changes when
# the files do. Cache the parsed list (and its pre-gzipped JSON) keyed by a
# cheap directory fingerprint so repeat requests are served from memory.
_ms_cache = {"fp": None, "data": None, "gz": None}


def _manuscripts_fingerprint():
    if not os.path.isdir(MANUSCRIPTS_DIR):
        return ("missing",)
    n, latest = 0, 0.0
    with os.scandir(MANUSCRIPTS_DIR) as it:
        for e in it:
            if e.name.endswith(".txt"):
                n += 1
                m = e.stat().st_mtime
                if m > latest:
                    latest = m
    return (n, latest)


def get_all_manuscripts():
    fp = _manuscripts_fingerprint()
    if _ms_cache["fp"] != fp:
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
        _ms_cache["fp"] = fp
        _ms_cache["data"] = results
        _ms_cache["gz"] = gzip.compress(
            app.json.dumps(results).encode("utf-8"), compresslevel=6)
    return _ms_cache["data"]


@app.route("/api/manuscripts")
def api_manuscripts():
    get_all_manuscripts()
    if "gzip" in request.headers.get("Accept-Encoding", "").lower():
        resp = app.response_class(_ms_cache["gz"], mimetype="application/json")
        resp.headers["Content-Encoding"] = "gzip"
        resp.headers["Content-Length"] = str(len(_ms_cache["gz"]))
        resp.headers["Vary"] = "Accept-Encoding"
        # direct_passthrough False is fine; the gzip after_request skips us
        # because Content-Encoding is already set.
        return resp
    return jsonify(_ms_cache["data"])


# ── AI MANUSCRIPT SEARCH AGENT ────────────────────────────────────────────
# POST /api/agent-search {"query": "..."} → conversational answer + ranked
# matches, powered by the Claude API over a compact catalog of all manuscripts.

AGENT_MODEL = "claude-haiku-4-5-20251001"

_agent_catalog = None   # [{id, genre, date, found, content, lat, lon, name, label}]
_agent_client = None    # anthropic.Anthropic, created lazily

AGENT_INSTRUCTIONS = """\
You are a search assistant for ManuscriptDB, an archive of ancient manuscripts:
New Testament papyri plus documentary papyri and ostraca (tax receipts, contracts,
leases, loans, sales, letters) from Roman and Ptolemaic Egypt and beyond.

Below is the full catalog, one manuscript per line in the format:
id | genre | date | found | summary

Given a user query, pick the manuscripts that genuinely match, ranked most
relevant first. Understand concepts and synonyms, not just keywords — e.g.
"seed-grain loans" should match loan contracts for wheat/barley seed even if
the words "seed-grain" never appear; "letters from soldiers" should match
letters whose writer is a soldier; "earliest copy of Matthew" should use the
dates. Use the genre field (new-testament, receipts, contracts, letters).

Respond with ONLY a JSON object, no markdown fences, no prose around it:
{"answer": "<1-2 conversational sentences summarizing what you found>",
 "matches": [{"id": "<exact id from the catalog>", "reason": "<one short line: why it matches>"}]}

At most 15 matches. Only use ids that appear in the catalog, copied exactly.
If nothing fits, return an empty matches array and a polite answer saying so.

CATALOG:
"""


def _get_agent_catalog():
    """Compact one-line-per-manuscript catalog, built once and cached."""
    global _agent_catalog
    if _agent_catalog is None:
        rows = []
        for m in get_all_manuscripts():   # shares the parsed in-memory cache
            if "error" in m and "id" not in m:
                continue
            rows.append({
                "id":      m.get("id", ""),
                "label":   m.get("label") or m.get("id", ""),
                "name":    m.get("name", ""),
                "genre":   m.get("genre", ""),
                "date":    m.get("date", ""),
                "found":   m.get("found", ""),
                "content": m.get("content") or m.get("name", ""),
                "lat":     m.get("lat"),
                "lon":     m.get("lon"),
            })
        _agent_catalog = rows
    return _agent_catalog


def _catalog_text(rows):
    return "\n".join(
        f"{r['id']} | {r['genre']} | {r['date']} | {r['found']} | {r['content']}"
        for r in rows
    )


def _anthropic_api_key():
    """ANTHROPIC_API_KEY from the environment (never hardcoded). On Windows,
    fall back to the user-scope registry value so a server launched before the
    var was set still finds it."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            val, _ = winreg.QueryValueEx(k, "ANTHROPIC_API_KEY")
            return val or None
    except Exception:
        return None


def _get_agent_client():
    global _agent_client
    if _agent_client is None:
        key = _anthropic_api_key()
        if not key:
            return None
        # This machine's TLS inspection breaks certifi validation (same gotcha
        # as the Firecrawl scraper) — trust the Windows cert store instead.
        try:
            import truststore
            truststore.inject_into_ssl()
        except ImportError:
            pass
        import anthropic
        _agent_client = anthropic.Anthropic(api_key=key, timeout=30.0, max_retries=1)
    return _agent_client


def _parse_agent_json(text):
    """Parse the model's JSON reply, tolerating markdown fences."""
    import json as _json
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    start, end = t.find("{"), t.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in reply")
    data = _json.loads(t[start:end + 1])
    if not isinstance(data, dict) or "matches" not in data:
        raise ValueError("missing matches")
    return data


def _keyword_fallback(query, rows):
    """Degraded plain keyword search when the Claude API is unavailable."""
    terms = [w for w in re.split(r"\W+", query.lower()) if len(w) > 2]
    scored = []
    for r in rows:
        hay = " ".join([r["id"], r["genre"], r["date"], r["found"],
                        r["content"], r["name"]]).lower()
        score = sum(hay.count(t) for t in terms)
        if score > 0:
            scored.append((score, r))
    scored.sort(key=lambda s: -s[0])
    matches = [{"id": r["id"], "reason": "Keyword match"} for _, r in scored[:15]]
    n = len(matches)
    answer = (f"Found {n} manuscript{'s' if n != 1 else ''} by keyword search."
              if n else "No manuscripts matched those keywords.")
    return {"answer": answer, "matches": matches, "fallback": True}


@app.route("/api/agent-search", methods=["POST"])
def api_agent_search():
    body = request.get_json(silent=True) or {}
    query = (body.get("query") or "").strip()
    if len(query) < 3:
        return jsonify({"error": "Query too short (min 3 characters)."}), 400

    # ── freemium gate ────────────────────────────────────────────────────
    # Require an account, then count this search against the user's daily
    # quota (5/day free; unlimited for subscribers, with an abuse cap).
    user = current_user()
    if user is None:
        return jsonify({"error": "login_required",
                        "message": "Please sign in to use the search assistant."}), 401
    gate = consume_quota(user)
    if not gate["allowed"]:
        return jsonify(gate), gate["status"]

    rows = _get_agent_catalog()
    by_id = {r["id"]: r for r in rows}
    client = _get_agent_client()

    result = None
    if client is not None:
        import anthropic
        # Catalog lives in a cached system block so repeat queries are cheap;
        # the per-request query goes in the (uncached) user turn.
        system_blocks = [{
            "type": "text",
            "text": AGENT_INSTRUCTIONS + _catalog_text(rows),
            "cache_control": {"type": "ephemeral"},
        }]
        for attempt in range(2):
            try:
                resp = client.messages.create(
                    model=AGENT_MODEL,
                    max_tokens=1500,
                    system=system_blocks,
                    messages=[{"role": "user", "content": query}],
                )
                text = next((b.text for b in resp.content if b.type == "text"), "")
                result = _parse_agent_json(text)
                break
            except (ValueError, KeyError):
                continue                      # malformed JSON — retry once
            except anthropic.APIError:
                break                          # API problem — use fallback
            except Exception:
                break

    if result is None:
        result = _keyword_fallback(query, rows)

    # Join model-returned ids against the real data; drop hallucinated ids and
    # never trust the model for coordinates/metadata.
    matches = []
    for m in result.get("matches", [])[:15]:
        r = by_id.get((m.get("id") or "").strip())
        if not r:
            continue
        matches.append({
            "id":     r["id"],
            "label":  r["label"],
            "name":   r["name"],
            "genre":  r["genre"],
            "date":   r["date"],
            "lat":    r["lat"],
            "lon":    r["lon"],
            "reason": (m.get("reason") or "").strip() or "Relevant match",
        })

    return jsonify({
        "answer":   result.get("answer", ""),
        "matches":  matches,
        "fallback": bool(result.get("fallback", False)),
    })


@app.route("/api/health")
def api_health():
    """Lightweight diagnostic: confirms the DB layer and which backend is live.
    'postgresql' = your Railway Postgres (persistent). 'sqlite' = local fallback
    (data is wiped on every Railway redeploy). Exposes no secrets or user data."""
    from accounts import db
    from sqlalchemy import text
    info = {"ok": True}
    try:
        eng = db.engine
        info["db_backend"] = eng.dialect.name
        info["persistent"] = (eng.dialect.name == "postgresql")
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        info["db_connected"] = True
    except Exception as e:
        info.update({"ok": False, "db_connected": False, "error": type(e).__name__})
    return jsonify(info)


if __name__ == "__main__":
    # The Werkzeug dev server transfers large bodies at ~65 KB/s on this
    # machine (and drops them mid-stream), which broke the ~1.3 MB gzipped
    # /api/manuscripts feed. Serve locally with waitress instead — it delivers
    # the feed in milliseconds. app.debug stays on for template auto-reload
    # and the dev-only endpoints; note there is no code auto-reloader, so
    # restart after editing app.py.
    app.debug = True
    try:
        from waitress import serve
        print("Serving on http://localhost:5000 (waitress)")
        serve(app, host="127.0.0.1", port=5000, threads=8)
    except ImportError:
        app.run(debug=True, threaded=True)

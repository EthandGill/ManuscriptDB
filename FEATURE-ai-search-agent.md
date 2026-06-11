# Feature Spec: AI Manuscript Search Agent

Build a chat-style AI search assistant for ManuscriptDB. A user types a natural-language
query like **"do you have seed-grain loans?"** and gets back a ranked dropdown of matching
manuscripts (e.g. loan contracts mentioning seed-grain), with a short conversational answer.
Powered by the Claude API.

---

## 1. UX / Frontend

### Placement & behavior
- Add a **collapsed tab/button on the left edge of the map**, vertically near the Leaflet
  zoom controls (`zoomControl: true` in `static/script.js` — the +/− buttons). Use a chat or
  magnifying-glass icon. It must NOT overlap the existing `#sidebar`.
- Clicking the tab **slides out a panel from the left** (CSS transition, ~320px wide,
  overlaying the map). Clicking the tab again, an × button, or pressing Esc closes it.
- Panel contents, top to bottom:
  1. Header: "Ask the Archive" (or similar) + close ×
  2. **Typeable search input** with placeholder like *"e.g. do you have seed-grain loans?"*
     Submit on Enter or a send button.
  3. **Results area**: while loading, show a subtle spinner/typing indicator. Then render:
     - A 1–2 sentence conversational answer from the agent
       ("Yes — I found 7 loan documents involving seed-grain…")
     - A **dropdown/list of matching manuscripts**, each row showing: name, id,
       genre badge (receipt / contract / letter / new-testament), date, and a one-line
       reason why it matched.
  4. Previous Q&A stays visible above (simple chat history within the session; no persistence).

### Result click behavior — BOTH actions
When the user clicks a result row:
1. **Fly the map** to the manuscript's find-spot (`lat`/`lon` from its META) —
   `map.flyTo([lat, lon], zoom)` and open/highlight its marker popup.
2. **Open the Writing Stand reader** for it — reuse the existing
   `openWritingStand(ms, book)` in `static/script.js` (line ~2516). For documentary
   papyri (no `book`), pass whatever the existing marker-click path passes.
Find the existing marker-click code path (~line 2506) and reuse it rather than
duplicating logic.

### Files to touch (frontend)
- `templates/index.html` — panel markup + tab button
- `static/style.css` — slide-out styles; match the site's existing visual language
- `static/script.js` — panel toggle, fetch to backend, result rendering, click → fly+reader

---

## 2. Backend

### New endpoint
`POST /api/agent-search` in `app.py`. Body: `{"query": "..."}`.
Response:

```json
{
  "answer": "Yes — I found 7 loan documents involving seed-grain.",
  "matches": [
    {"id": "BGU 3.697", "name": "...", "genre": "contracts", "date": "...",
     "lat": 29.3, "lon": 30.8, "reason": "Loan of seed wheat repayable at harvest"}
  ]
}
```

### Claude API integration
- Use the official `anthropic` Python SDK (`pip install anthropic`; add to `requirements.txt`).
- API key from the **`ANTHROPIC_API_KEY` env var — never hardcode** (same convention as
  `FIRECRAWL_API_KEY` in this repo).
- Model: `claude-haiku-4-5-20251001` (fast + cheap; this is a retrieval task, not deep reasoning).

### Giving Claude the corpus (~745 manuscripts)
Do NOT send full Greek/translation texts. At app startup (or lazily on first request,
then cached in a module-level var), build a **compact catalog** from the existing
`parse_manuscript()` output — one line per manuscript:

```
BGU 1.13 | contracts | 289 CE | Arsinoite, Fayum | Deed of sale of a male Arabian camel to a primipilarius, with warranty clauses
```

i.e. `id | genre | date | found | content` (the META `content` field is already a good
summary). ~745 lines ≈ 35–50k tokens — fits comfortably in one request.

**Use prompt caching**: put the catalog in a system block with
`"cache_control": {"type": "ephemeral"}` so repeat queries cost ~10% after the first.

### Prompt design
System prompt (cached): the catalog + instructions:
- You are a search assistant for an ancient-manuscript archive (NT papyri + documentary
  papyri: receipts, contracts, letters, etc.).
- Given a user query, return matching manuscript IDs ranked by relevance, with a one-line
  reason each, plus a short conversational answer. Understand synonyms and concepts —
  "seed-grain loans" should match loan contracts for wheat/barley seed even if the word
  "seed-grain" never appears.
- **Respond ONLY with JSON**: `{"answer": "...", "matches": [{"id": "...", "reason": "..."}]}`.
  Max ~15 matches. Empty `matches` + a polite answer if nothing fits.

Backend then joins the returned IDs against the real manuscript data to fill in
name/genre/date/lat/lon (never trust the model for coordinates), drops any hallucinated
IDs that don't exist, and returns the response above.

### Robustness
- Strip markdown fences before `json.loads`; on parse failure, retry once, then return
  a friendly error.
- 30s timeout; on API error or missing `ANTHROPIC_API_KEY`, **fall back to a plain
  substring/keyword search** over the catalog so the panel still works (degraded), and
  include `"fallback": true` in the response so the UI can note it.
- Rate-limit lightly (e.g. reject queries < 3 chars; debounce on the frontend — submit
  on Enter, not per keystroke).

---

## 3. Acceptance criteria
1. Tab appears beside the zoom controls; panel slides out/in smoothly; Esc closes it.
2. "do you have seed-grain loans" returns loan-related documentary papyri with reasons,
   not random receipts.
3. "letters from soldiers", "camel sales", "tax receipts from the Fayum", "earliest copy
   of Matthew" all return sensible results.
4. Clicking a result flies the map to the find-spot AND opens the Writing Stand reader.
5. Works with no API key set (keyword fallback, UI notes degraded mode).
6. No regressions: existing sidebar search, filters, route planner, and reader untouched.
7. `python app.py` still runs clean on localhost:5000.

## 4. Out of scope (for now)
- Conversation memory across page reloads
- Full-text Greek search inside the agent (catalog summaries only, v1)
- Streaming responses

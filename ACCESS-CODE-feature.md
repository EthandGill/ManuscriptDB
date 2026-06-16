# Feature: Unlimited Access Code ("Tertius") for marketing

Goal: let someone type a secret code to unlock **free unlimited** access to the AI
search agent (no payment), both **at sign-up** and **from the subscribe prompt**
when already logged in. Used for marketing/comps.

This is a server-enforced complimentary grant — NOT a Stripe promo code. (Stripe's
own `allow_promotion_codes` in `create_checkout_session` is unrelated and stays as
is; it discounts a real paid subscription, whereas this code bypasses payment.)

## How access currently works (read these first)

- `accounts.py` — `User` model + freemium metering. **Unlimited = `User.is_subscribed`.**
  `consume_quota(user)` / `quota_status(user)` branch on `user.is_subscribed`:
  subscribed ⇒ unlimited (only the `ABUSE_CAP`), else `FREE_DAILY_LIMIT` (5) / 24h.
  Routes: `/api/register`, `/api/login`, `/api/logout`, `/api/me` (all on blueprint `bp`).
- `stripe_billing.py` — the webhook flips `is_subscribed` for **paid** users, matched
  by `stripe_customer_id`. It must keep owning `is_subscribed`, so comps use a
  **separate** flag (below) to avoid collisions.
- `app.py` — `/api/agent-search` (line ~414) calls `current_user()` then
  `consume_quota(user)`. **No change needed here** — if comp users read as unlimited
  inside `consume_quota`, the gate already lets them through.
- `static/account.js` — all auth/paywall UI. `openAuth("register")` is the sign-up
  modal; `openPaywall()` is the "Subscribe to ManuscriptDB Unlimited" modal;
  `renderBadge()` draws the sidebar account badge. State comes from `/api/me`.

## Backend changes (`accounts.py`)

1. **New column** on `User`:
   ```python
   comp_access = db.Column(db.Boolean, default=False, nullable=False)
   ```

2. **Self-applying migration** (the Railway Postgres `users` table already exists, and
   `db.create_all()` does NOT add columns to existing tables). In `init_accounts`,
   after `db.create_all()`, run a guarded add-column so prod and dev both upgrade with
   no manual step:
   ```python
   from sqlalchemy import text
   try:
       with db.engine.begin() as c:
           c.execute(text("ALTER TABLE users ADD COLUMN comp_access BOOLEAN DEFAULT FALSE"))
   except Exception:
       pass   # already exists — fine (Postgres + SQLite both accept this ALTER)
   ```

3. **Code config** (env-driven so codes can be added/rotated without a deploy):
   ```python
   ACCESS_CODES = {c.strip().lower() for c in
                   os.environ.get("ACCESS_CODES", "Tertius").split(",") if c.strip()}
   def _valid_code(s):
       return bool(s) and s.strip().lower() in ACCESS_CODES
   ```

4. **Unlimited helper** — replace the two `user.is_subscribed` checks in
   `quota_status` and `consume_quota` with this:
   ```python
   def is_unlimited(user):
       return bool(user.is_subscribed or user.comp_access)
   ```
   In both functions branch on `is_unlimited(user)` instead of `user.is_subscribed`.

5. **Surface comp status** so the UI can tell comp from paid. In `quota_status`, when
   unlimited, return `"subscribed": True` AND add `"comp": bool(user.comp_access)`.
   (`_me_payload` already spreads `quota_status`, so `comp` rides along.)

6. **Sign-up redemption** — in `register()`, read `access_code = body.get("access_code")`
   and, before the final commit, `if _valid_code(access_code): user.comp_access = True`.

7. **Logged-in redemption** — new route on `bp`:
   ```python
   @bp.route("/api/redeem-code", methods=["POST"])
   def redeem_code():
       user = current_user()
       if user is None:
           return jsonify({"error":"login_required","message":"Please sign in first."}), 401
       code = (request.get_json(silent=True) or {}).get("access_code")
       if not _valid_code(code):
           return jsonify({"error":"bad_code","message":"That access code isn't valid."}), 400
       user.comp_access = True
       db.session.commit()
       return jsonify(_me_payload(user))
   ```
   Never log the submitted code.

No change to `stripe_billing.py` or `app.py`. The new route auto-registers (it's on
`bp`, which `init_accounts` already registers).

## Frontend changes (`static/account.js`)

1. **Sign-up modal** (`openAuth`, register mode only): add a labelled field **below**
   the password input:
   ```
   <input id="mdb-code" type="text" placeholder="Unlimited Access Code (optional)" autocomplete="off">
   ```
   In `submitAuth(isReg)`, when `isReg`, include `access_code: (el("mdb-code")||{}).value`
   in the `/api/register` body. (Leave login mode unchanged.)

2. **Subscribe / paywall modal** (`openPaywall`): under the existing Subscribe button,
   add a small divider and a redeem row so an already-logged-in user can unlock with a
   code instead of paying:
   ```
   <div style="margin-top:14px;border-top:1px solid #2a2416;padding-top:12px">
     <p style="margin:0 0 6px;font-size:12px;color:#a89878">Have an Unlimited Access Code?</p>
     <input id="mdb-pay-code" type="text" placeholder="Unlimited Access Code" autocomplete="off">
     <div class="mdb-err" id="mdb-code-err"></div>
     <button class="mdb-btn alt" id="mdb-redeem">Redeem code</button>
   </div>
   ```
   Wire `#mdb-redeem`: if not logged in, `openAuth("register")`; else
   `api("/api/redeem-code","POST",{access_code: el("mdb-pay-code").value})`; on `ok`,
   `Object.assign(state,res.data); closeModals(); renderBadge();` on error show
   `res.data.message` in `#mdb-code-err`.

3. **Badge** (`renderBadge`, subscribed branch): comps have no Stripe customer, so the
   "Manage ManuscriptDB Unlimited" bar (which opens the billing portal) would 400 for
   them. When `state.comp` is true, show the **Unlimited** quota text but replace that
   bar with a static, non-clickable note, e.g. `Complimentary unlimited access`. Paid
   subscribers (`subscribed && !comp`) keep the existing Manage bar.

Match the existing gold/black `.mdb-*` styling; reuse `.mdb-card input`, `.mdb-btn`,
`.mdb-btn.alt`, `.mdb-err`.

## Test (local, `py app.py`)

1. **Sign up with the code** → `/api/me` shows `subscribed:true, comp:true`; run 6+ agent
   searches — none get the 402 paywall.
2. **Wrong code at sign-up** → account created as normal free tier (5/day).
3. **Logged-in free user → Subscribe modal → Redeem "Tertius"** → badge flips to
   Unlimited (complimentary), no paywall afterward.
4. **Wrong code in redeem** → 400, friendly error, still metered at 5/day.
5. **Paid subscriber** still shows the Manage-billing bar (unaffected).

Then commit + push (`git add accounts.py static/account.js ACCESS-CODE-feature.md`,
commit, push) → Railway redeploys. Set `ACCESS_CODES` in Railway (and locally) if you
want codes other than the default `Tertius`, comma-separated.

## Notes

- The code is a shared secret: anyone who learns it gets free unlimited access (that's
  the marketing intent). Rotate via the `ACCESS_CODES` env var anytime; removing a code
  does not revoke already-granted comps (they keep `comp_access=true`). To revoke an
  individual later, set that user's `comp_access=false` in the DB.
- Validation is server-side in `_valid_code`, so it can't be bypassed from the browser.

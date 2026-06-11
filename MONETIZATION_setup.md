# Monetization — Phase 1: accounts + freemium metering

This phase adds **email accounts** and a **daily free-search limit** to the
search assistant. Free users get **5 searches per rolling 24 hours**, then hit a
paywall prompting a **$10 CAD/month** subscription. Stripe payment is Phase 2 —
the "Subscribe" button is wired but shows "launching shortly" until then.

## What changed

| File | Purpose |
|---|---|
| `accounts.py` | Accounts + metering: `User` model, `/api/register` `/api/login` `/api/logout` `/api/me`, and the quota logic (`consume_quota`). |
| `app.py` | Calls `init_accounts(app)`; `/api/agent-search` now requires login (401) and counts each search against the quota (402 when exhausted). |
| `static/account.js` | Self-contained UI: sign-in/register modal, "N free left today" badge, and the paywall modal. Included from `index.html`. |
| `requirements.txt` | Adds `Flask-SQLAlchemy` + `psycopg2-binary`. |
| `.gitignore` | Ignores the local SQLite DB and secrets. |

## Run it locally

```powershell
cd C:\ManuscriptDB
pip install -r requirements.txt
$env:SECRET_KEY = "any-long-random-string"   # signs login cookies
python app.py
```

With no `DATABASE_URL` set, it uses a local SQLite file (`manuscriptdb.sqlite3`,
gitignored). Open the site, register an account, and run 6 searches — the 6th
should show the paywall.

## Deploy to Railway (production)

Two things are **required**, because Railway's disk is wiped on every deploy:

1. **Add a Postgres database.** In your Railway project: **New → Database →
   Postgres**. Railway auto-injects a `DATABASE_URL` env var; `accounts.py`
   detects it and uses Postgres automatically (accounts/usage then persist across
   deploys). Without this, every redeploy wipes all accounts.
2. **Set a `SECRET_KEY` variable.** Railway → your service → **Variables** → add
   `SECRET_KEY` = a long random string. (If it's missing, logins silently reset
   and you'll see a warning in the logs.)

Then push as usual (`update_website.bat`). Railway installs the new requirements
and the tables are created on first boot.

## Tunables (top of `accounts.py`)

- `FREE_DAILY_LIMIT = 5` — free searches per window.
- `WINDOW = 24h` — rolling reset period.
- `ABUSE_CAP = 200` — hard ceiling per 24h **even for subscribers**, so a script
  can't run up your Anthropic bill on an "unlimited" plan. Raise/lower freely.

## What Phase 2 (Stripe) will add

- A Stripe account + a $10 CAD/month recurring Price.
- `POST /api/create-checkout-session` → redirects to Stripe Checkout (the
  front-end already calls this endpoint; it just doesn't exist yet).
- A `/api/stripe-webhook` that flips `User.is_subscribed = True` on payment and
  back to `False` on cancellation, and stores `stripe_customer_id`.
- A "Manage subscription" link to Stripe's Customer Portal.
- Before going live: a Terms of Service, Privacy Policy, and refund policy on the
  site, and a decision on sales tax (Stripe Tax can automate GST/HST for CAD).

## Economics sanity check

Each search is one Claude Haiku call with your catalog cached, so a search costs
a fraction of a cent. Even a heavy subscriber doing ~100/day stays well under the
$10/mo price; Stripe takes ~$0.59 per $10 charge. The free tier's job is to
demonstrate value, and the daily reset keeps casual users coming back — which is
exactly the funnel you described.

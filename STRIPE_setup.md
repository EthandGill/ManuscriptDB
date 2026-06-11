# Monetization — Phase 2: Stripe subscriptions ($10 CAD/mo)

The code is done (`stripe_billing.py`, wired into `app.py`, "Subscribe"/"Manage"
buttons in `account.js`). It stays dormant until you set four environment
variables. Do the Stripe dashboard setup below, set the vars on Railway, redeploy.

Work in **Test mode** first (toggle top-right of the Stripe dashboard) — test keys
start `sk_test_`/`pk_test_` and you can pay with card `4242 4242 4242 4242`, any
future date, any CVC. Switch to Live mode and repeat for real money.

## 1. Create a Stripe account
<https://dashboard.stripe.com/register>. Fill in business details (you can start
testing before full activation).

## 2. Create the product + price
- **Product catalog → + Add product**.
- Name: `ManuscriptDB Unlimited`.
- Pricing: **Recurring**, **Monthly**, amount **10.00**, currency **CAD**.
- Save, then open the price and copy its **Price ID** (`price_...`). → this is
  `STRIPE_PRICE_ID`.

## 3. Get your API key
- **Developers → API keys** → copy the **Secret key** (`sk_test_...` in test mode).
  → `STRIPE_SECRET_KEY`.

## 4. Create the webhook
- **Developers → Webhooks → + Add endpoint**.
- Endpoint URL: `https://manuscriptdb.org/api/stripe-webhook`
- Select events to send:
  - `checkout.session.completed`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
- Add endpoint, then copy its **Signing secret** (`whsec_...`).
  → `STRIPE_WEBHOOK_SECRET`.

## 5. Turn on the Customer Portal
- **Settings → Billing → Customer portal** → activate it (lets subscribers
  cancel/update cards themselves). The "Manage" button uses this.

## 6. Set the variables on Railway
Your app service → **Variables** → add:

| Variable | Value |
|---|---|
| `STRIPE_SECRET_KEY` | `sk_test_...` (then `sk_live_...` when live) |
| `STRIPE_PRICE_ID` | `price_...` |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` |
| `PUBLIC_BASE_URL` | `https://manuscriptdb.org` |

Redeploy (push with `update_website.bat`, which also installs the new `stripe`
dependency).

## 7. Test the full loop
1. Register a free account, use up the 5 free searches → paywall appears.
2. Click **Subscribe** → you're sent to Stripe Checkout → pay with `4242…`.
3. You land back on the site; the badge flips to **★ Unlimited** (the webhook fired
   and set `is_subscribed`). Searching no longer counts down.
4. Click **Manage** → Stripe portal → cancel → access reverts to free on the next
   webhook.
5. Visit `https://manuscriptdb.org/api/health` to confirm `"db_backend":
   "postgresql"` (subscriptions must persist, so Postgres is required here).

## How it works (for reference)
- Checkout runs in `subscription` mode with `client_reference_id = your user id`,
  so the webhook knows which account to upgrade.
- `checkout.session.completed` → `is_subscribed = True` + stores `stripe_customer_id`.
- `customer.subscription.deleted` / `.updated` (status not active) → reverts to free.
- No card data ever touches your server; Stripe hosts the payment page.

## Before going live (not legal advice)
- Add **Terms of Service**, **Privacy Policy**, and a **refund policy** page.
- Decide on sales tax: **Stripe Tax** can auto-collect Canadian GST/HST — enable it
  under Settings → Tax if you want it handled automatically.
- Switch all keys from `sk_test`/`pk_test`/`whsec` (test) to their Live-mode values.

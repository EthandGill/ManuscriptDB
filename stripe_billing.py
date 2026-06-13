#!/usr/bin/env python3
"""
stripe_billing.py  —  Stripe subscriptions for ManuscriptDB (monetization Phase 2)

Adds the $10 CAD/month subscription on top of the accounts/metering in
accounts.py. Hosted Stripe Checkout (no card data touches our server) + a webhook
that flips User.is_subscribed, + the Stripe Customer Portal for self-serve
cancellation.

Routes:
  POST /api/create-checkout-session  → {url} to redirect the logged-in user to Checkout
  POST /api/billing-portal           → {url} to Stripe's Customer Portal (manage/cancel)
  POST /api/stripe-webhook           → Stripe calls this; verifies signature, updates the user

Configuration (environment variables — set these in Railway, never hardcode):
  STRIPE_SECRET_KEY      sk_live_... (or sk_test_... while testing)
  STRIPE_PRICE_ID        price_...   the $10 CAD/month recurring Price
  STRIPE_WEBHOOK_SECRET  whsec_...   from the webhook endpoint you create
  PUBLIC_BASE_URL        https://manuscriptdb.org   (used for success/cancel redirects)

If STRIPE_SECRET_KEY is unset, the endpoints return a friendly 503 so the rest of
the site keeps working (the front-end then shows "launching shortly").

Uses only the existing User columns (is_subscribed, stripe_customer_id) — no DB
migration required.
"""

import os, sys, traceback
from flask import Blueprint, request, jsonify

from accounts import db, User, current_user

bp = Blueprint("billing", __name__)


def _cfg(name):
    return os.environ.get(name, "").strip()


def _stripe():
    """Return a configured stripe module, or None if not set up yet."""
    key = _cfg("STRIPE_SECRET_KEY")
    if not key:
        return None
    import stripe
    stripe.api_key = key
    return stripe


def _base_url():
    return _cfg("PUBLIC_BASE_URL") or request.host_url.rstrip("/")


# ── checkout ────────────────────────────────────────────────────────────────
@bp.route("/api/create-checkout-session", methods=["POST"])
def create_checkout_session():
    user = current_user()
    if user is None:
        return jsonify({"error": "login_required",
                        "message": "Please sign in before subscribing."}), 401
    if user.is_subscribed:
        return jsonify({"error": "already_subscribed",
                        "message": "You already have an active subscription."}), 400

    stripe = _stripe()
    price = _cfg("STRIPE_PRICE_ID")
    if stripe is None or not price:
        return jsonify({"error": "billing_unconfigured",
                        "message": "Subscriptions are launching shortly."}), 503

    base = _base_url()
    try:
        kwargs = {
            "mode": "subscription",
            "line_items": [{"price": price, "quantity": 1}],
            "client_reference_id": str(user.id),
            "success_url": base + "/?subscribed=1",
            "cancel_url": base + "/?canceled=1",
            "allow_promotion_codes": True,
        }
        # reuse an existing Stripe customer if we have one, else let Stripe make one
        if user.stripe_customer_id:
            kwargs["customer"] = user.stripe_customer_id
        else:
            kwargs["customer_email"] = user.email
        session = stripe.checkout.Session.create(**kwargs)
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": "stripe_error", "message": str(e)}), 502


# ── customer portal (manage / cancel) ───────────────────────────────────────
@bp.route("/api/billing-portal", methods=["POST"])
def billing_portal():
    user = current_user()
    if user is None:
        return jsonify({"error": "login_required"}), 401
    stripe = _stripe()
    if stripe is None or not user.stripe_customer_id:
        return jsonify({"error": "no_customer",
                        "message": "No subscription found for this account."}), 400
    try:
        portal = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=_base_url() + "/",
        )
        return jsonify({"url": portal.url})
    except Exception as e:
        return jsonify({"error": "stripe_error", "message": str(e)}), 502


# ── webhook ─────────────────────────────────────────────────────────────────
def _set_subscribed(user, value, customer_id=None):
    user.is_subscribed = bool(value)
    if customer_id:
        user.stripe_customer_id = customer_id
    db.session.commit()


def _find_user_for_session(obj):
    """Find the account for a completed checkout. Prefer client_reference_id
    (our user id); fall back to the email Stripe collected during checkout."""
    uid = obj.get("client_reference_id")
    if uid:
        try:
            u = db.session.get(User, int(uid))
            if u is not None:
                return u
        except (ValueError, TypeError):
            pass
    email = obj.get("customer_email") or ""
    if not email:
        details = obj.get("customer_details") or {}
        email = details.get("email") or ""
    email = email.strip().lower()
    if email:
        return db.session.query(User).filter_by(email=email).first()
    return None


@bp.route("/api/stripe-webhook", methods=["POST"])
def stripe_webhook():
    stripe = _stripe()
    secret = _cfg("STRIPE_WEBHOOK_SECRET")
    if stripe is None or not secret:
        return jsonify({"error": "webhook_unconfigured"}), 503

    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except Exception as e:
        # bad signature or malformed — reject so Stripe retries / flags it
        return jsonify({"error": "invalid_signature", "message": str(e)}), 400

    # Process the event. Any failure is caught, logged to Railway, and returned
    # as readable JSON (instead of an opaque 500 HTML page) so it's diagnosable.
    try:
        etype = event["type"]
        obj = event["data"]["object"]

        if etype == "checkout.session.completed":
            user = _find_user_for_session(obj)
            if user is not None:
                _set_subscribed(user, True, obj.get("customer"))

        elif etype == "customer.subscription.deleted":
            cust = obj.get("customer")
            user = db.session.query(User).filter_by(stripe_customer_id=cust).first()
            if user is not None:
                _set_subscribed(user, False)

        elif etype == "customer.subscription.updated":
            cust = obj.get("customer")
            status = obj.get("status")  # active, trialing, past_due, canceled...
            user = db.session.query(User).filter_by(stripe_customer_id=cust).first()
            if user is not None:
                _set_subscribed(user, status in ("active", "trialing"))

        return jsonify({"received": True})
    except Exception as e:
        db.session.rollback()
        traceback.print_exc(file=sys.stderr)   # surfaces in Railway logs
        return jsonify({"error": "handler_exception", "message": str(e)}), 500


def init_billing(app):
    app.register_blueprint(bp)

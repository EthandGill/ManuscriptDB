#!/usr/bin/env python3
"""
accounts.py  —  email accounts + freemium metering for the ManuscriptDB agent

Phase 1 of monetization (metering + paywall gate). Stripe payment is wired in a
later step; for now `is_subscribed` exists but is only ever True if you flip it
manually / via the future webhook.

What it provides:
  * email + password accounts (passwords hashed with werkzeug; never stored raw)
  * a server-side daily quota on the search agent: FREE_DAILY_LIMIT calls per
    rolling 24h window, then a 402 "paywall" response until the window resets
  * an abuse cap even for subscribers (ABUSE_CAP/24h) so a scraper can't run up
    your Anthropic bill on an "unlimited" plan
  * JSON routes: POST /api/register, /api/login, /api/logout ; GET /api/me

Storage: uses DATABASE_URL if set (Railway Postgres in production), else a local
SQLite file for development. NOTE: Railway's disk is ephemeral — in production you
MUST set DATABASE_URL to a real Postgres add-on, or accounts/usage reset on every
deploy.

Integration (see app.py):
    from accounts import init_accounts, current_user, consume_quota
    init_accounts(app)
    ... inside /api/agent-search, before doing work:
        user = current_user()
        if user is None: return jsonify({"error":"login_required", ...}), 401
        gate = consume_quota(user)
        if not gate["allowed"]: return jsonify(gate), gate["status"]
"""

import os, re, datetime
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# ── tunables ────────────────────────────────────────────────────────────────
FREE_DAILY_LIMIT = 5                              # free searches per 24h
WINDOW           = datetime.timedelta(hours=24)   # rolling reset window
ABUSE_CAP        = 200                            # hard cap/24h even for subscribers
MIN_PASSWORD     = 8

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

db = SQLAlchemy()
bp = Blueprint("accounts", __name__)


# ── model ───────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = "users"
    id               = db.Column(db.Integer, primary_key=True)
    email            = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash    = db.Column(db.String(255), nullable=False)
    is_subscribed    = db.Column(db.Boolean, default=False, nullable=False)
    stripe_customer_id = db.Column(db.String(255))   # filled in by the Stripe step
    # free-tier metering
    free_used        = db.Column(db.Integer, default=0, nullable=False)
    window_start     = db.Column(db.DateTime)
    # subscriber abuse-cap metering
    sub_used         = db.Column(db.Integer, default=0, nullable=False)
    sub_window_start = db.Column(db.DateTime)
    created_at       = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# ── helpers ─────────────────────────────────────────────────────────────────
def _now():
    return datetime.datetime.utcnow()


def current_user():
    """Return the logged-in User (from the signed session cookie) or None."""
    uid = session.get("uid")
    if not uid:
        return None
    return db.session.get(User, uid)


def _roll_free_window(user):
    if user.window_start is None or (_now() - user.window_start) >= WINDOW:
        user.window_start = _now()
        user.free_used = 0


def _roll_sub_window(user):
    if user.sub_window_start is None or (_now() - user.sub_window_start) >= WINDOW:
        user.sub_window_start = _now()
        user.sub_used = 0


def _reset_at(window_start):
    if window_start is None:
        return None
    return (window_start + WINDOW).replace(microsecond=0).isoformat() + "Z"


def quota_status(user):
    """Read-only-ish peek at remaining quota (rolls an expired window but does
    not consume a search). Safe to call from /api/me."""
    if user.is_subscribed:
        _roll_sub_window(user)
        db.session.commit()
        return {"subscribed": True, "remaining": None, "limit": None,
                "reset_at": _reset_at(user.sub_window_start)}
    _roll_free_window(user)
    db.session.commit()
    remaining = max(0, FREE_DAILY_LIMIT - user.free_used)
    return {"subscribed": False, "remaining": remaining, "limit": FREE_DAILY_LIMIT,
            "reset_at": _reset_at(user.window_start)}


def consume_quota(user):
    """Count one search against the user's quota. Returns a dict that doubles as
    the JSON body when blocked. Keys: allowed, status, error, message, remaining,
    limit, reset_at, subscribed."""
    if user.is_subscribed:
        _roll_sub_window(user)
        if user.sub_used >= ABUSE_CAP:
            db.session.commit()
            return {"allowed": False, "status": 429, "error": "rate_limited",
                    "subscribed": True, "remaining": 0, "limit": ABUSE_CAP,
                    "reset_at": _reset_at(user.sub_window_start),
                    "message": "Daily usage cap reached. Try again later."}
        user.sub_used += 1
        db.session.commit()
        return {"allowed": True, "subscribed": True, "remaining": None,
                "limit": None, "reset_at": _reset_at(user.sub_window_start)}

    _roll_free_window(user)
    if user.free_used >= FREE_DAILY_LIMIT:
        db.session.commit()
        return {"allowed": False, "status": 402, "error": "quota_exhausted",
                "subscribed": False, "remaining": 0, "limit": FREE_DAILY_LIMIT,
                "reset_at": _reset_at(user.window_start),
                "message": ("You've used your %d free searches for today. "
                            "Subscribe for unlimited access." % FREE_DAILY_LIMIT)}
    user.free_used += 1
    db.session.commit()
    return {"allowed": True, "subscribed": False,
            "remaining": max(0, FREE_DAILY_LIMIT - user.free_used),
            "limit": FREE_DAILY_LIMIT, "reset_at": _reset_at(user.window_start)}


def _me_payload(user):
    if user is None:
        # Surface the daily free allowance so the UI can advertise it pre-login.
        return {"logged_in": False, "free_limit": FREE_DAILY_LIMIT}
    q = quota_status(user)
    return {"logged_in": True, "email": user.email, **q}


# ── routes ──────────────────────────────────────────────────────────────────
@bp.route("/api/register", methods=["POST"])
def register():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    if not EMAIL_RE.match(email):
        return jsonify({"error": "invalid_email", "message": "Enter a valid email address."}), 400
    if len(password) < MIN_PASSWORD:
        return jsonify({"error": "weak_password",
                        "message": "Password must be at least %d characters." % MIN_PASSWORD}), 400
    if db.session.query(User).filter_by(email=email).first():
        return jsonify({"error": "email_taken", "message": "That email is already registered."}), 409
    user = User(email=email, password_hash=generate_password_hash(password),
                window_start=_now())
    db.session.add(user)
    db.session.commit()
    session.permanent = True
    session["uid"] = user.id
    return jsonify(_me_payload(user))


@bp.route("/api/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    user = db.session.query(User).filter_by(email=email).first()
    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "bad_credentials", "message": "Wrong email or password."}), 401
    session.permanent = True
    session["uid"] = user.id
    return jsonify(_me_payload(user))


@bp.route("/api/logout", methods=["POST"])
def logout():
    session.pop("uid", None)
    return jsonify({"logged_in": False})


@bp.route("/api/me", methods=["GET"])
def me():
    return jsonify(_me_payload(current_user()))


# ── init ────────────────────────────────────────────────────────────────────
def init_accounts(app):
    secret = os.environ.get("SECRET_KEY") or os.environ.get("FLASK_SECRET")
    if not secret:
        secret = "dev-insecure-secret-change-me"
        app.logger.warning("SECRET_KEY not set — using an insecure dev key. "
                            "Set SECRET_KEY in production.")
    app.secret_key = secret

    url = os.environ.get("DATABASE_URL", "").strip()
    # SQLAlchemy needs the postgresql:// scheme; Railway/Heroku give postgres://
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if not url:
        url = "sqlite:///" + os.path.join(os.path.dirname(__file__), "manuscriptdb.sqlite3")

    app.config["SQLALCHEMY_DATABASE_URI"] = url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    # secure cookies in production (where a real DB is configured)
    app.config["SESSION_COOKIE_SECURE"] = url.startswith("postgresql")
    app.permanent_session_lifetime = datetime.timedelta(days=30)

    db.init_app(app)
    app.register_blueprint(bp)
    with app.app_context():
        db.create_all()

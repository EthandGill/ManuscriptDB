#!/usr/bin/env python3
"""
comp_report.py — who has complimentary ("Unlimited Access Code") access?

A local, off-website report. It reads the SAME database your app uses (Railway
Postgres if DATABASE_URL is set, otherwise the local dev SQLite) and prints a
breakdown of accounts: complimentary comps, paid subscribers, and free tier.

Usage:
    py comp_report.py                 # summary + list of comp accounts
    py comp_report.py --all           # also list paid + free accounts
    py comp_report.py --csv comps.csv # write the comp accounts to a CSV

To report on the LIVE site's accounts, run it where the production database is
reachable — i.e. with DATABASE_URL set to your Railway Postgres connection
string (Railway → your Postgres add-on → "Connect" gives the URL). Locally with
no DATABASE_URL it reads manuscriptdb.sqlite3 (dev/test accounts only).

Requires the access-code feature (the comp_access column) to be deployed; if the
column isn't there yet it says so.
"""

import os, sys, csv, argparse, datetime
from flask import Flask
import accounts   # reuse the real model + DB config (DATABASE_URL/SQLite resolution)


def _fmt(dt):
    if not isinstance(dt, datetime.datetime):
        return ""
    return dt.replace(microsecond=0).isoformat() + "Z"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="also list paid + free accounts")
    ap.add_argument("--csv", metavar="PATH", help="write comp accounts to a CSV file")
    args = ap.parse_args()

    app = Flask(__name__)
    accounts.init_accounts(app)   # configures the DB exactly like the live app

    with app.app_context():
        User = accounts.User
        try:
            users = accounts.db.session.query(User).order_by(User.created_at).all()
        except Exception as e:
            sys.exit(f"Could not read the users table: {e}")

        # comp_access may not exist if the feature isn't deployed yet
        if not hasattr(User, "comp_access"):
            print("NOTE: the comp_access column isn't in this build yet — deploy the "
                  "Unlimited Access Code feature first. Showing paid/free only.\n")

        comps, paid, free = [], [], []
        for u in users:
            comp = bool(getattr(u, "comp_access", False))
            sub  = bool(getattr(u, "is_subscribed", False))
            if comp:
                comps.append(u)
            elif sub:
                paid.append(u)
            else:
                free.append(u)

        url = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        where = "Railway Postgres" if url.startswith("postgresql") else "local SQLite"
        print(f"Database: {where}")
        print(f"Total accounts:        {len(users)}")
        print(f"Complimentary (comp):  {len(comps)}")
        print(f"Paid subscribers:      {len(paid)}")
        print(f"Free tier:             {len(free)}\n")

        if comps:
            print("Complimentary access accounts:")
            for u in comps:
                print(f"  {u.email:<40} since {_fmt(u.created_at)}")
        else:
            print("No complimentary accounts yet.")

        if args.all:
            print("\nPaid subscribers:")
            for u in paid:
                print(f"  {u.email:<40} since {_fmt(u.created_at)}")
            print("\nFree-tier accounts:")
            for u in free:
                print(f"  {u.email:<40} since {_fmt(u.created_at)}")

        if args.csv:
            with open(args.csv, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["email", "created_at"])
                for u in comps:
                    w.writerow([u.email, _fmt(u.created_at)])
            print(f"\nWrote {len(comps)} comp accounts to {args.csv}")


if __name__ == "__main__":
    main()

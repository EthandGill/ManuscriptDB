#!/usr/bin/env python3
"""
credits_left.py — show your remaining Firecrawl credits.

  py credits_left.py

Reads FIRECRAWL_API_KEY from the environment and calls Firecrawl's
credit-usage endpoint. Run it between scrape batches to see how close you are to
your 5,000. Costs nothing (it's a usage lookup, not a scrape).
"""

import os, sys, json, urllib.request

try:
    import truststore; truststore.inject_into_ssl()   # trust Windows cert store (TLS inspection)
except Exception:
    pass

KEY = os.environ.get("FIRECRAWL_API_KEY")
if not KEY:
    sys.exit("FIRECRAWL_API_KEY not set in this terminal.")

URL = "https://api.firecrawl.dev/v1/team/credit-usage"


def dig(obj, key):
    """Find a key anywhere in a nested dict/list."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = dig(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = dig(v, key)
            if r is not None:
                return r
    return None


def main():
    req = urllib.request.Request(URL, headers={"Authorization": "Bearer " + KEY})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        sys.exit("Could not reach Firecrawl: " + str(e))

    remaining = dig(data, "remaining_credits")
    if remaining is None:
        remaining = dig(data, "remainingCredits")
    period_end = dig(data, "billing_period_end") or dig(data, "plan_credits")

    if remaining is None:
        print("Raw response (couldn't find remaining_credits):")
        print(json.dumps(data, indent=1)[:1200])
        return

    print(f"Firecrawl credits remaining: {remaining}")
    if period_end:
        print(f"(billing period / plan info: {period_end})")
    try:
        rem = int(remaining)
        if rem < 500:
            print("** Low — under 500 left. Wind down the big ranges. **")
    except (TypeError, ValueError):
        pass


if __name__ == "__main__":
    main()

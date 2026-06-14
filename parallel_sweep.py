#!/usr/bin/env python3
"""
parallel_sweep.py — run many _sweep.py scrapes at once (controlled concurrency)

This is the "break the work into parallel windows" step, but cleaner: instead of
juggling terminals, it launches N `_sweep.py` subprocesses at a time, each
scraping a different DDbDP range to its own _sweep_<range>.json. No model, no git,
no shared queue — so it's safe to parallelize and it only ever banks JSON
(translation/build happens later, separately).

Usage:
    1. Put one range per line in  sweep_ranges.txt  (see that file).
    2. Make sure FIRECRAWL_API_KEY is set in this terminal.
    3. Run:
         python parallel_sweep.py            # 4 workers (safe default)
         python parallel_sweep.py 6          # 6 concurrent scrapes
         python parallel_sweep.py 4 myranges.txt

Each worker = roughly one in-flight Firecrawl request at a time, so "workers" ≈
your concurrent-request count. Keep it at or below your Firecrawl plan's
concurrency limit (start at 4; raise cautiously). _sweep.py already retries with
backoff on transient errors.

Ranges already having a _sweep_<range>.json are skipped, so re-running resumes
where it left off without re-spending credits.
"""

import os, sys, subprocess, concurrent.futures

HERE = os.path.dirname(os.path.abspath(__file__))


def slug(rng):
    return rng.replace(";;", "_").replace(";", "_")


def already_done(rng):
    return os.path.exists(os.path.join(HERE, f"_sweep_{slug(rng)}.json"))


def load_ranges(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                out.append(s.split()[0])   # first token = the range id
    return out


def run_one(rng):
    if already_done(rng):
        return rng, "skip", 0
    proc = subprocess.run(
        [sys.executable, "_sweep.py", rng],
        cwd=HERE, capture_output=True, text=True)
    # _sweep prints "SAVED ... records: N" on success
    ok = proc.returncode == 0 and "SAVED" in (proc.stdout or "")
    tail = (proc.stdout or proc.stderr or "").strip().splitlines()[-1:] or [""]
    return rng, ("ok" if ok else "FAIL"), tail[0]


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    ranges_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "sweep_ranges.txt")

    if not os.environ.get("FIRECRAWL_API_KEY"):
        sys.exit("ERROR: FIRECRAWL_API_KEY not set in this terminal.")
    if not os.path.exists(ranges_file):
        sys.exit(f"ERROR: ranges file not found: {ranges_file}")

    ranges = load_ranges(ranges_file)
    todo = [r for r in ranges if not already_done(r)]
    print(f"{len(ranges)} ranges listed, {len(todo)} to scrape, "
          f"{len(ranges)-len(todo)} already done. Workers: {workers}\n")

    done = failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_one, r): r for r in ranges}
        for fut in concurrent.futures.as_completed(futs):
            rng, status, note = fut.result()
            if status == "ok":
                done += 1
            elif status == "FAIL":
                failed += 1
            print(f"[{status:>4}] {rng:<22} {note}")

    print(f"\nDone. {done} scraped, {failed} failed. "
          f"JSON saved as _sweep_<range>.json in {HERE}.")
    if failed:
        print("Re-run to retry failed ranges (completed ones are skipped).")
    print("Next: translate/build from the _sweep_*.json files (build-from-pending).")


if __name__ == "__main__":
    main()

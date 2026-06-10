#!/usr/bin/env python3
"""
next_batch.py  —  queue driver for the documentary onboarding loop

Reads onboarding_queue.txt (one DDbDP series-range per line) and makes the
continuous loop deterministic and resumable. The first whitespace-delimited
token on each line is the range id (e.g. "o.wilck;;261-310"); the rest is a
genre hint / notes for the agent. Lines starting with '#' or 'DONE ' are skipped.

Commands:
    python next_batch.py                      # print the next pending line (range + notes)
    python next_batch.py --range-only         # print just the next range id
    python next_batch.py --list               # show all pending lines
    python next_batch.py --count              # how many ranges remain
    python next_batch.py --done "o.wilck;;261-310"   # mark that range DONE
    python next_batch.py --add  "o.fay;;1-50  receipts  Fayum ostraca"  # append a range

Exit codes: 0 = success; 1 = queue empty / range not found (handy for shell loops).
"""

import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE_PATH = os.path.join(HERE, "onboarding_queue.txt")


def read_lines(path):
    if not os.path.exists(path):
        sys.stderr.write(f"Queue not found: {path}\n")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


def is_skip(line):
    s = line.strip()
    return (not s) or s.startswith("#") or s.startswith("DONE ") or s == "DONE"


def range_token(line):
    return line.strip().split()[0] if line.strip() else ""


def pending(lines):
    return [ln for ln in lines if not is_skip(ln)]


def main():
    p = argparse.ArgumentParser(description="Queue driver for documentary onboarding.")
    p.add_argument("--queue", default=QUEUE_PATH, help="Queue file (default onboarding_queue.txt).")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--range-only", action="store_true", help="Print only the next range id.")
    g.add_argument("--list", action="store_true", help="List all pending lines.")
    g.add_argument("--count", action="store_true", help="Print the number of pending ranges.")
    g.add_argument("--done", metavar="RANGE", help="Mark the line whose range id matches as DONE.")
    g.add_argument("--add", metavar="LINE", help="Append a new range line to the queue.")
    args = p.parse_args()

    lines = read_lines(args.queue)

    if args.add:
        with open(args.queue, "a", encoding="utf-8") as f:
            f.write(args.add.rstrip("\n") + "\n")
        print(f"Added: {args.add.strip()}")
        return

    if args.done:
        target = args.done.strip()
        changed = False
        for i, ln in enumerate(lines):
            if not is_skip(ln) and range_token(ln) == target:
                lines[i] = "DONE " + ln.strip()
                changed = True
                break
        if not changed:
            sys.stderr.write(f"No pending line with range id {target!r}.\n")
            sys.exit(1)
        with open(args.queue, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"Marked DONE: {target}")
        return

    pend = pending(lines)

    if args.count:
        print(len(pend))
        return

    if args.list:
        if not pend:
            print("(queue empty — all ranges DONE)")
            sys.exit(1)
        for ln in pend:
            print(ln.strip())
        return

    # default / --range-only: the next pending line
    if not pend:
        sys.stderr.write("Queue empty — all ranges DONE.\n")
        sys.exit(1)
    nxt = pend[0].strip()
    print(range_token(nxt) if args.range_only else nxt)


if __name__ == "__main__":
    main()

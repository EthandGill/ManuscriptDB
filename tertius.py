#!/usr/bin/env python3
"""
tertius.py — TERTIUS, the translating agent.

    "I Tertius, who wrote this letter, greet you in the Lord."  (Rom 16:22)

Works through every untranslated manuscript in manuscripts/, translates it
line-by-line (lacunae kept in [brackets] / … so the site tints them blue),
and reports progress in two places:

  * tertius_status.json             -> the floating desktop pop-up
                                       (tertius_widget.py, launched automatically)
  * static/data/tertius_progress.json -> committed with every push, read by the
                                       live site's "Tertius has translated N of M
                                       sources" badge (GET /api/tertius)

It is a WRAPPER around the existing Max-plan translator: the prompt, parsing,
writing and `claude -p` driving all come from translate_mss_api.py,
translate_mss_max.py and _claude_max.py. Nothing is billed to an API key.

  py tertius.py                 # translate the whole backlog, pop-up on
  py tertius.py --limit 10      # smoke test
  py tertius.py --no-widget     # headless (Task Scheduler)
  py tertius.py --status        # count + write progress files, no tokens
  py tertius.py --review        # list translations whose lacuna check failed
  py tertius.py --selftest      # offline checks

Stop any time (pop-up ■ button, or Ctrl+C). Re-run to resume — already
translated manuscripts are skipped.
"""
import os, re, sys, json, glob, time, argparse, threading, subprocess
from datetime import datetime, timedelta

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from translate_mss_api import (MSS, SYSTEM, parse_txt, needs_translation,
                               write_translation, parse_reply)
from translate_mss_max import batch_body
import _claude_max as cm

STATUS_PATH   = os.path.join(HERE, "tertius_status.json")      # local, git-ignored
INDEX_PATH    = os.path.join(HERE, "tertius_index.json")       # local, git-ignored
CONTROL_PATH  = os.path.join(HERE, "tertius.control")          # local, git-ignored
PROGRESS_PATH = os.path.join(HERE, "static", "data", "tertius_progress.json")  # committed
ERR_LOG       = os.path.join(HERE, "_translate_errors.log")
WIDGET        = os.path.join(HERE, "tertius_widget.py")

LACUNA_TAG = "# tertius: lacuna-check"
INDEX_VERSION = 1


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def atomic_write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def log_err(msg):
    try:
        with open(ERR_LOG, "a", encoding="utf-8") as f:
            f.write(f"tertius {now_iso()} {msg}\n")
    except Exception:
        pass


# ── metadata helpers ─────────────────────────────────────────────────────────
_META_RX = re.compile(r"^(id|label|name|genre):\s*(.*)$")

def read_meta(path):
    """id / name from the [META] block (cheap: stops at [GREEK])."""
    meta = {}
    try:
        with open(path, encoding="utf-8") as f:
            for ln in f:
                s = ln.strip()
                if s.startswith("[GREEK") or s.startswith("[TRANSLATION"):
                    break
                m = _META_RX.match(s)
                if m and m.group(1) not in meta:
                    meta[m.group(1)] = m.group(2).strip()
    except Exception:
        pass
    stem = os.path.splitext(os.path.basename(path))[0]
    return {"id": meta.get("label") or meta.get("id") or stem,
            "name": meta.get("name") or "", "file": os.path.basename(path)}


# ── the index: which manuscripts are Tertius's job, and which are done ───────
#   state: "done"  = eligible & translated
#          "todo"  = eligible & untranslated
#          "skip"  = not Tertius's job (multi-book NT text, no Greek lines)
def classify(info):
    if info["multibook"] or not info["greek"]:
        return "skip"
    return "done" if info["translated"] else "todo"


def build_index(verbose=True):
    """Scan manuscripts/, re-parsing only files whose mtime/size changed since
    the cached index. Returns {fname: {"m": mtime, "s": size, "st": state}}."""
    cache = {}
    try:
        old = json.load(open(INDEX_PATH, encoding="utf-8"))
        if old.get("v") == INDEX_VERSION:
            cache = old.get("files", {})
    except Exception:
        pass
    files, parsed, t0 = {}, 0, time.time()
    with os.scandir(MSS) as it:
        entries = [e for e in it if e.name.endswith(".txt")]
    n = len(entries)
    for k, e in enumerate(entries, 1):
        st = e.stat()
        c = cache.get(e.name)
        if c and c["m"] == st.st_mtime and c["s"] == st.st_size:
            files[e.name] = c
            continue
        try:
            state = classify(parse_txt(e.path))
        except Exception as ex:
            log_err(f"index {e.name}: {ex}")
            state = "skip"
        files[e.name] = {"m": st.st_mtime, "s": st.st_size, "st": state}
        parsed += 1
        if verbose and parsed % 2000 == 0:
            print(f"  indexing… {k:,}/{n:,}", flush=True)
    atomic_write_json(INDEX_PATH, {"v": INDEX_VERSION, "files": files})
    if verbose:
        print(f"Indexed {n:,} files ({parsed:,} parsed, rest cached) "
              f"in {time.time() - t0:.1f}s")
    return files


def counts(index):
    done = sum(1 for v in index.values() if v["st"] == "done")
    todo = sum(1 for v in index.values() if v["st"] == "todo")
    return {"translated": done, "total": done + todo, "remaining": todo}


def mark_done(index, fname):
    p = os.path.join(MSS, fname)
    st = os.stat(p)
    index[fname] = {"m": st.st_mtime, "s": st.st_size, "st": "done"}


# ── lacuna check (requirement #4) ────────────────────────────────────────────
_GREEK_LETTER = re.compile(r"[Ͱ-Ͽἀ-῿A-Za-z]")

def _letters_outside_brackets(s):
    s = re.sub(r"\bGAP\b.*", "", s, flags=re.I)        # "GAP: not preserved"
    return len(_GREEK_LETTER.findall(re.sub(r"\[[^\]]*\]", "", s)))


def lacuna_issues(greek, eng):
    """1-based line numbers whose English drops the lacuna marking:
      * the Greek line restores text in [ ] but the English has neither [ ] nor …
      * the Greek line is essentially all restoration/gap, yet the English is a
        fluent sentence with no marking."""
    bad = []
    for i, (g, e) in enumerate(zip(greek, eng), 1):
        marked = ("[" in e) or ("…" in e) or ("..." in e)
        if "[" in g and not marked:
            bad.append(i)
        elif ("…" in g or "GAP" in g.upper()) and _letters_outside_brackets(g) < 3 \
                and not marked and len(e.split()) > 2:
            bad.append(i)
    return bad


def add_lacuna_comment(path, lines):
    """Record failed lacuna-check lines as a comment under [TRANSLATION]."""
    raw = open(path, encoding="utf-8").read().split("\n")
    raw = [ln for ln in raw if not ln.strip().startswith(LACUNA_TAG)]
    for i, ln in enumerate(raw):
        if ln.strip() == "[TRANSLATION]":
            raw.insert(i + 1, f"{LACUNA_TAG} failed lines {','.join(map(str, lines))}")
            break
    tmp = path + ".tmp"
    open(tmp, "w", encoding="utf-8").write("\n".join(raw))
    os.replace(tmp, path)


RETRY_NOTE = ("IMPORTANT: in the source lines below, text inside [square brackets] "
              "was restored by the editor because the papyrus is damaged there. "
              "Lines {lines} contain such restorations. In your English, put the "
              "words that translate restored Greek inside [square brackets] too, "
              "and render lost text as … . Never drop the brackets.")


# ── status (desktop pop-up) ──────────────────────────────────────────────────
class Status:
    """Thread-safe writer for tertius_status.json, with a heartbeat thread so
    the pop-up knows Tertius is alive even during a long model call."""
    def __init__(self, c):
        self.lock = threading.Lock()
        self.d = {"agent": "Tertius", "state": "starting", "current": [],
                  "batch_size": 0, **c, "session_done": 0, "recent": [],
                  "last_line": None, "resume_at": None, "last_error": None,
                  "lacuna_flags": 0, "started": now_iso(), "heartbeat": now_iso(),
                  "pid": os.getpid()}
        self._stop = threading.Event()
        self.flush()
        threading.Thread(target=self._beat, daemon=True).start()

    def _beat(self):
        while not self._stop.wait(15):
            self.update()

    def update(self, **kw):
        with self.lock:
            self.d.update(kw)
            self.d["heartbeat"] = now_iso()
            self._write()

    def flush(self):
        with self.lock:
            self._write()

    def _write(self):
        try:
            atomic_write_json(STATUS_PATH, self.d)
        except Exception:
            pass   # a busy file (AV scanner etc.) must never kill the run

    def close(self, state):
        self._stop.set()
        self.update(state=state, current=[], resume_at=None)


# ── public progress (live website badge) ─────────────────────────────────────
def write_progress(c, current="", state="translating"):
    atomic_write_json(PROGRESS_PATH, {
        "agent": "Tertius", "translated": c["translated"], "total": c["total"],
        "current": current, "state": state, "updated": now_iso()})


def git_push(msg):
    try:
        subprocess.run(["git", "add", "manuscripts/",
                        os.path.relpath(PROGRESS_PATH, HERE)], cwd=HERE, check=True)
        subprocess.run(["git", "commit", "-m", msg], cwd=HERE, check=True)
        subprocess.run(["git", "push"], cwd=HERE, check=True)
        print(f"   ↑ pushed: {msg}")
    except Exception as e:
        print(f"   (git step skipped: {e})")
        log_err(f"git: {e}")


# ── control file (pop-up pause / stop buttons) ───────────────────────────────
def read_control():
    try:
        return open(CONTROL_PATH, encoding="utf-8").read().strip().lower()
    except Exception:
        return ""


def clear_control():
    try:
        os.remove(CONTROL_PATH)
    except Exception:
        pass


def wait_if_paused(status):
    """Returns True if Tertius should stop."""
    cmd = read_control()
    if cmd == "stop":
        return True
    if cmd == "pause":
        status.update(state="paused")
        print("Paused (pop-up). Waiting for resume…")
        while True:
            time.sleep(2)
            cmd = read_control()
            if cmd == "stop":
                return True
            if cmd != "pause":
                status.update(state="translating")
                print("Resumed.")
                return False
    return False


def launch_widget():
    if not os.path.exists(WIDGET):
        return None
    exe = sys.executable
    flags = 0
    if os.name == "nt":
        pyw = os.path.join(os.path.dirname(exe), "pythonw.exe")
        if os.path.exists(pyw):
            exe = pyw
        flags = 0x08000000   # CREATE_NO_WINDOW
    try:
        return subprocess.Popen([exe, WIDGET], cwd=HERE, creationflags=flags)
    except Exception as e:
        print(f"(pop-up not started: {e})")
        return None


# ── the run ──────────────────────────────────────────────────────────────────
def translate_batch(batch, args, status, log):
    """batch: [(fname, path, info, meta)]. Returns {fname: [english lines]}."""
    items = [(fname, batch_body(info)) for fname, _, info, _ in batch]
    prompt = cm.build_batch_prompt(
        SYSTEM + "\nEach item below is one papyrus: its numbered Greek source "
        "lines (and possibly a reference translation).", items)
    reply, toks = cm.call_with_window_wait(prompt, args.model, args.claude_cmd,
                                           args.wait_min, args.no_wait, log)
    blocks = cm.split_blocks(reply)
    out = {}
    for fname, _, info, _ in batch:
        blk = blocks.get(fname)
        if blk is None:
            log_err(f"{fname}: no block in reply"); print(f"[skip] {fname}: no block")
            continue
        try:
            out[fname] = parse_reply(blk, len(info["greek"]))
        except ValueError as e:
            log_err(f"{fname}: {e}"); print(f"[skip] {fname}: {e}")
    return out, toks


def retry_lacunae(fname, info, bad, args, log):
    note = RETRY_NOTE.format(lines=", ".join(map(str, bad)))
    prompt = cm.build_batch_prompt(SYSTEM + "\n" + note, [(fname, batch_body(info))])
    reply, _ = cm.call_with_window_wait(prompt, args.model, args.claude_cmd,
                                        args.wait_min, args.no_wait, log)
    blk = cm.split_blocks(reply).get(fname) or reply
    return parse_reply(blk, len(info["greek"]))


def run(args):
    print("Tertius is taking up his pen…")
    clear_control()
    index = build_index()
    c = counts(index)
    print(f"Translated {c['translated']:,} / {c['total']:,}  ·  "
          f"left {c['remaining']:,} / {c['total']:,}")
    status = Status(c)
    write_progress(c, state="translating")
    widget = None if args.no_widget else launch_widget()

    def log(msg):
        print(msg, flush=True)
        if "sleeping" in msg and "Usage window" in msg:
            resume = (datetime.now() + timedelta(minutes=args.wait_min)).astimezone()
            status.update(state="resting", resume_at=resume.isoformat(timespec="seconds"))

    cm.find_claude(args.claude_cmd)

    todo = []
    for fname, v in sorted(index.items()):
        if v["st"] != "todo":
            continue
        path = os.path.join(MSS, fname)
        info = parse_txt(path)
        if not needs_translation(info) or len(info["greek"]) < args.min_lines:
            continue
        if args.genre and info["genre"] not in set(args.genre.split(",")):
            continue
        todo.append((fname, path, info))
    # cheapest first: ones with a free HGV reference, then short texts
    todo.sort(key=lambda t: (t[2]["hgv_ref"] is None, len(t[2]["greek"])))

    done = since_push = 0
    final_state = "done"
    i = 0
    try:
        while i < len(todo):
            if args.limit and done >= args.limit:
                print(f"Limit reached ({args.limit})."); final_state = "stopped"; break
            if wait_if_paused(status):
                print("Stop requested — finishing cleanly."); final_state = "stopped"; break
            batch, nlines = [], 0
            while (i < len(todo) and len(batch) < args.batch
                   and (not batch or nlines + len(todo[i][2]["greek"]) <= args.batch_lines)
                   and (not args.limit or done + len(batch) < args.limit)):
                fname, path, info = todo[i]
                batch.append((fname, path, info, read_meta(path)))
                nlines += len(info["greek"]); i += 1

            status.update(state="translating", batch_size=len(batch),
                          current=[{**m, "lines": len(inf["greek"])}
                                   for _, _, inf, m in batch])
            try:
                results, toks = translate_batch(batch, args, status, log)
            except SystemExit:
                raise
            except Exception as e:
                log_err(f"batch {[b[0] for b in batch]}: {e}")
                print(f"[skip batch] {e}")
                status.update(last_error=f"{type(e).__name__}: {str(e)[:200]}")
                continue

            for fname, path, info, meta in batch:
                eng = results.get(fname)
                if eng is None:
                    continue
                bad = lacuna_issues(info["greek"], eng)
                if bad and not args.no_retry:
                    try:
                        eng2 = retry_lacunae(fname, info, bad, args, log)
                        bad2 = lacuna_issues(info["greek"], eng2)
                        if len(bad2) < len(bad):
                            eng, bad = eng2, bad2
                    except SystemExit:
                        raise
                    except Exception as e:
                        log_err(f"{fname} lacuna retry: {e}")
                write_translation(path, eng)
                if bad:
                    add_lacuna_comment(path, bad)
                    log_err(f"{fname}: lacuna-check failed lines {bad}")
                mark_done(index, fname)
                done += 1; since_push += 1
                c = counts(index)
                # the most bracket-rich line makes the best preview
                k = max(range(len(eng)), key=lambda j: info["greek"][j].count("["))
                recent = ([{"id": meta["id"], "at": now_iso()}] + status.d["recent"])[:5]
                status.update(**c, session_done=done, recent=recent,
                              last_line={"greek": info["greek"][k], "english": eng[k]},
                              lacuna_flags=status.d["lacuna_flags"] + (1 if bad else 0),
                              resume_at=None)
                flag = f"  ⚠ lacuna lines {bad}" if bad else ""
                print(f"[{c['translated']:,}/{c['total']:,}] {meta['id']}  "
                      f"({len(eng)} lines){flag}", flush=True)

                if since_push >= args.commit_every:
                    cur = batch[-1][3]["id"]
                    write_progress(c, current=cur)
                    atomic_write_json(INDEX_PATH, {"v": INDEX_VERSION, "files": index})
                    if not args.no_git:
                        git_push(f"Tertius: translated {c['translated']:,} of "
                                 f"{c['total']:,} sources")
                    since_push = 0
    except KeyboardInterrupt:
        print("\nInterrupted — saving progress.")
        final_state = "stopped"
    except SystemExit as e:
        print(e)
        final_state = "stopped"
    finally:
        c = counts(index)
        if c["remaining"] == 0:
            final_state = "done"
        atomic_write_json(INDEX_PATH, {"v": INDEX_VERSION, "files": index})
        write_progress(c, state=final_state if final_state == "done" else "idle")
        if since_push and not args.no_git:
            git_push(f"Tertius: translated {c['translated']:,} of {c['total']:,} sources")
        status.close(final_state)
        clear_control()
        print(f"\nTertius set down his pen: {done:,} translated this session · "
              f"{c['translated']:,} / {c['total']:,} overall.")


def show_status():
    index = build_index()
    c = counts(index)
    write_progress(c, state="done" if c["remaining"] == 0 else "idle")
    print(f"Translated:  {c['translated']:,} / {c['total']:,}")
    print(f"Left to go:  {c['remaining']:,} / {c['total']:,}")
    skip = sum(1 for v in index.values() if v["st"] == "skip")
    print(f"(Not Tertius's job: {skip:,} multi-book / Greek-less files)")
    print(f"Wrote {os.path.relpath(PROGRESS_PATH, HERE)} for the website badge.")


def review():
    hits = 0
    for p in sorted(glob.glob(os.path.join(MSS, "*.txt"))):
        with open(p, encoding="utf-8") as f:
            for ln in f:
                if ln.startswith(LACUNA_TAG):
                    print(f"{os.path.basename(p)}: {ln[len(LACUNA_TAG):].strip()}")
                    hits += 1
                    break
    print(f"\n{hits} manuscript(s) flagged for lacuna review.")


# ── self-test (offline) ──────────────────────────────────────────────────────
def selftest():
    import tempfile
    # lacuna check
    g = ["το[ῦ γ]νώμον[ος], ὃν ὁ θεὸς", "καὶ τῶν ὑπὸ χεῖρα αὐτῷ", "[κη]π[οτάφια ἢ τοι]αῦτα"]
    assert lacuna_issues(g, ["Of the [Gn]omon, which the god", "and those under him",
                             "[garden-tombs or such]"]) == []
    assert lacuna_issues(g, ["Of the Gnomon, which the god", "and those under him",
                             "garden-tombs or such"]) == [1, 3]
    assert lacuna_issues(["… GAP"], ["The emperor commanded all of them"]) == [1]
    assert lacuna_issues(["… GAP"], ["…"]) == []
    # write + comment + index round trip on a temp manuscripts dir
    d = tempfile.mkdtemp()
    p = os.path.join(d, "x_1.txt")
    open(p, "w", encoding="utf-8").write(
        "[META]\nid:       X 1\nname:     Test papyrus\ngenre:    documents\n\n"
        "[GREEK]\nr.1    το[ῦ γ]νώμον[ος]\nr.2    καὶ\n\n[TRANSLATION]\n1     \n2     \n")
    info = parse_txt(p)
    assert classify(info) == "todo"
    assert read_meta(p)["id"] == "X 1" and read_meta(p)["name"] == "Test papyrus"
    write_translation(p, ["of the Gnomon", "and"])
    add_lacuna_comment(p, [1])
    add_lacuna_comment(p, [1])                       # idempotent, no duplicates
    raw = open(p, encoding="utf-8").read()
    assert raw.count(LACUNA_TAG) == 1, raw
    assert "[GREEK]\nr.1    το[ῦ γ]νώμον[ος]" in raw  # Greek untouched
    info2 = parse_txt(p)
    assert info2["translated"] and classify(info2) == "done"
    # status json atomic write
    sp = os.path.join(d, "s.json")
    atomic_write_json(sp, {"a": 1})
    assert json.load(open(sp, encoding="utf-8")) == {"a": 1}
    assert counts({"a": {"st": "done"}, "b": {"st": "todo"}, "c": {"st": "skip"}}) == \
        {"translated": 1, "total": 2, "remaining": 1}
    cm.selftest()
    print("tertius selftest OK")


def main():
    ap = argparse.ArgumentParser(description="Tertius — the translating agent")
    ap.add_argument("--status", action="store_true", help="print fractions, write progress json")
    ap.add_argument("--review", action="store_true", help="list lacuna-check failures")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-widget", action="store_true", dest="no_widget")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--min-lines", type=int, default=1, dest="min_lines")
    ap.add_argument("--genre", default="")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--batch-lines", type=int, default=150, dest="batch_lines")
    ap.add_argument("--model", default=cm.DEFAULT_MODEL)
    ap.add_argument("--claude-cmd", default="", dest="claude_cmd")
    ap.add_argument("--wait-min", type=int, default=20, dest="wait_min")
    ap.add_argument("--no-wait", action="store_true", dest="no_wait")
    ap.add_argument("--no-retry", action="store_true", dest="no_retry",
                    help="skip the lacuna retry call")
    ap.add_argument("--commit-every", type=int, default=25, dest="commit_every")
    ap.add_argument("--no-git", action="store_true", dest="no_git")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    elif args.status:
        show_status()
    elif args.review:
        review()
    else:
        run(args)


if __name__ == "__main__":
    main()

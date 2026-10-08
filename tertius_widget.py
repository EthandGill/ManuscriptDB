#!/usr/bin/env python3
"""
tertius_widget.py — the floating desktop pop-up for Tertius.

Launched automatically by tertius.py (you can also run it by hand to peek).
Reads tertius_status.json once a second.

  * Collapsed: a small bar  "✒ Tertius · translating   30 / 100"
  * Click it to expand: current manuscript, translated / total, left / total,
    the latest Greek → English line with lacunae in the site's blue, recently
    finished, and pause / stop buttons.
  * Drag it anywhere; position is remembered (tertius_widget.json).
  * It only lives while Tertius is working: when he stops (or goes silent for
    2 minutes) it fades out on its own.

  py tertius_widget.py            # normal
  py tertius_widget.py --demo     # fake status, for trying the look
"""
import os, re, sys, json, time
from datetime import datetime
import tkinter as tk
import tkinter.font as tkfont

HERE = os.path.dirname(os.path.abspath(__file__))
STATUS_PATH  = os.path.join(HERE, "tertius_status.json")
CONTROL_PATH = os.path.join(HERE, "tertius.control")
PREFS_PATH   = os.path.join(HERE, "tertius_widget.json")

# Palette — taken from static/style.css so the pop-up matches the site.
BG      = "#0e0e0e"     # sidebar background
PANEL   = "#161616"     # inputs / cards
EDGE    = "#2a2416"     # warm dark border
GOLD    = "#c9a96e"     # ManuscriptDB title gold
INK     = "#d4c9b8"     # body text
DIM     = "#7a7266"
LACUNA  = "#607888"     # .ms-supplied — reconstructed lacunae
LACUNA_BRIGHT = "#8fb0c4"  # same hue, lifted for the dark pop-up's small text
RED     = "#c0584a"
GREEN   = "#7fa36b"
KEY     = "#010203"     # transparent key colour (Windows rounded corners)

PILL_W, PILL_H = 280, 60
CARD_W, CARD_H = 400, 412
RADIUS = 14
STALE_SEC = 120

LACUNA_RX = re.compile(r"(\[[^\]]*\]|…+|\.\.\.)")


def fmt(n):
    try:
        return f"{int(n):,}"
    except Exception:
        return "—"


def parse_iso(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_json(path, data):
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp, path)
    except Exception:
        pass


def demo_status():
    t = int(time.time())
    done = 30 + (t // 3) % 40
    return {"agent": "Tertius", "state": "translating", "translated": done,
            "total": 100, "remaining": 100 - done, "session_done": done - 30,
            "batch_size": 8,
            "current": [{"id": "BGU 5.1210", "file": "bgu_5_1210.txt",
                         "name": "Documentary papyrus — Theadelphia (Arsinoites)",
                         "lines": 12}],
            "recent": [{"id": "P.Oxy 6.984"}, {"id": "P.Tebt 1.62"}, {"id": "BGU 9.1898"}],
            "last_line": {"greek": "το[ῦ γ]νώμον[ος], ὃν ὁ θεὸς Σεβαστὸς τῇ τοῦ ἰδίου λόγου",
                          "english": "Of the [Gn]omon, which the god Augustus [set] for the Idios Logos…"},
            "lacuna_flags": 1, "resume_at": None, "last_error": None,
            "heartbeat": datetime.now().astimezone().isoformat()}


class TertiusWidget:
    def __init__(self, demo=False):
        self.demo = demo
        self.root = tk.Tk()
        self.root.title("Tertius")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.windows = (os.name == "nt")
        if self.windows:
            try:
                self.root.attributes("-transparentcolor", KEY)
            except tk.TclError:
                self.windows = False
        self.root.configure(bg=KEY if self.windows else BG)

        fams = set(tkfont.families())
        pick = lambda *names: next((n for n in names if n in fams), "TkDefaultFont")
        self.f_title = (pick("Cinzel", "Georgia", "Times New Roman"), 11, "bold")
        self.f_body  = (pick("Inter", "Segoe UI", "Helvetica", "DejaVu Sans"), 9)
        self.f_bold  = (self.f_body[0], 9, "bold")
        self.f_big   = (self.f_body[0], 13, "bold")
        self.f_small = (self.f_body[0], 8)
        self.f_greek = (pick("Gentium Plus", "Gentium Book Plus", "Palatino Linotype",
                             "Cambria", "DejaVu Serif", "Times New Roman"), 10)

        prefs = load_json(PREFS_PATH) or {}
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.pos = prefs.get("pos") or [sw - PILL_W - 24, sh - PILL_H - 72]
        self.expanded = bool(prefs.get("expanded", False))
        self.status = None
        self.missing_since = time.time()
        self.closing = False
        self.stop_armed = False
        self.pulse = False
        self.alpha = 0.0

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bd=0,
                                bg=KEY if self.windows else BG)
        self.canvas.pack(fill="both", expand=True)
        self.inner = None
        self._drag = None
        self.build()
        self.fade_in()
        self.tick()
        self.animate()

    # ── layout ──────────────────────────────────────────────────────────────
    def build(self):
        w, h = (CARD_W, CARD_H) if self.expanded else (PILL_W, PILL_H)
        x, y = self.clamp(self.pos[0], self.pos[1], w, h)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.canvas.delete("all")
        self.canvas.config(width=w, height=h)
        self.round_rect(1, 1, w - 2, h - 2, RADIUS, fill=BG, outline=EDGE, width=1)
        if self.inner is not None:
            self.inner.destroy()
        self.inner = tk.Frame(self.canvas, bg=BG)
        pad = 10
        self.canvas.create_window(pad, pad, anchor="nw", window=self.inner,
                                  width=w - 2 * pad, height=h - 2 * pad)
        (self.build_card if self.expanded else self.build_pill)(self.inner)
        self.bind_drag(self.canvas)
        self.bind_drag(self.inner)
        self.render()

    def build_pill(self, f):
        self.quill = tk.Label(f, text="✒", font=self.f_big, fg=GOLD, bg=BG)
        self.quill.pack(side="left", padx=(4, 6))
        col = tk.Frame(f, bg=BG); col.pack(side="left", fill="y")
        tk.Label(col, text="Tertius", font=self.f_title, fg=GOLD, bg=BG,
                 anchor="w").pack(anchor="w")
        self.p_state = tk.Label(col, text="", font=self.f_small, fg=DIM, bg=BG, anchor="w")
        self.p_state.pack(anchor="w")
        self.p_frac = tk.Label(f, text="", font=self.f_big, fg=INK, bg=BG)
        self.p_frac.pack(side="right", padx=(0, 6))

    def build_card(self, f):
        top = tk.Frame(f, bg=BG); top.pack(fill="x")
        self.quill = tk.Label(top, text="✒", font=self.f_big, fg=GOLD, bg=BG)
        self.quill.pack(side="left")
        tk.Label(top, text="TERTIUS", font=self.f_title, fg=GOLD, bg=BG).pack(side="left", padx=6)
        self.c_dot = tk.Label(top, text="●", font=self.f_small, fg=GREEN, bg=BG)
        self.c_dot.pack(side="left")
        self.c_state = tk.Label(top, text="", font=self.f_small, fg=DIM, bg=BG)
        self.c_state.pack(side="left", padx=4)
        self.b_stop  = self.button(top, "■", self.on_stop, "Stop after this batch")
        self.b_pause = self.button(top, "‖", self.on_pause, "Pause / resume")
        self.button(top, "–", self.toggle, "Collapse")
        self.rule(f)

        tk.Label(f, text="NOW TRANSLATING", font=self.f_small, fg=DIM, bg=BG,
                 anchor="w").pack(fill="x")
        self.c_cur = tk.Label(f, text="", font=self.f_bold, fg=INK, bg=BG, anchor="w",
                              justify="left", wraplength=CARD_W - 30)
        self.c_cur.pack(fill="x")
        self.c_cur2 = tk.Label(f, text="", font=self.f_small, fg=DIM, bg=BG, anchor="w",
                               justify="left", wraplength=CARD_W - 30)
        self.c_cur2.pack(fill="x", pady=(0, 6))

        grid = tk.Frame(f, bg=BG); grid.pack(fill="x")
        tk.Label(grid, text="Translated", font=self.f_body, fg=DIM, bg=BG).grid(row=0, column=0, sticky="w")
        self.c_done = tk.Label(grid, text="", font=self.f_big, fg=INK, bg=BG)
        self.c_done.grid(row=0, column=1, sticky="e", padx=(12, 0))
        tk.Label(grid, text="Left to go", font=self.f_body, fg=DIM, bg=BG).grid(row=1, column=0, sticky="w")
        self.c_left = tk.Label(grid, text="", font=self.f_big, fg=INK, bg=BG)
        self.c_left.grid(row=1, column=1, sticky="e", padx=(12, 0))
        grid.columnconfigure(1, weight=1)
        self.bar = tk.Canvas(f, height=6, bg=PANEL, highlightthickness=0, bd=0)
        self.bar.pack(fill="x", pady=(6, 2))
        self.c_pct = tk.Label(f, text="", font=self.f_small, fg=DIM, bg=BG, anchor="e")
        self.c_pct.pack(fill="x")
        self.rule(f)

        tk.Label(f, text="LATEST LINE", font=self.f_small, fg=DIM, bg=BG,
                 anchor="w").pack(fill="x")
        self.txt = tk.Text(f, height=4, wrap="word", bg=PANEL, fg=INK, bd=0,
                           highlightthickness=0, padx=8, pady=6, cursor="arrow")
        self.txt.tag_configure("greek", font=self.f_greek, foreground=INK)
        self.txt.tag_configure("eng", font=self.f_body, foreground=INK)
        self.txt.tag_configure("lac", foreground=LACUNA_BRIGHT)
        self.txt.pack(fill="x", pady=(2, 6))

        self.c_recent = tk.Label(f, text="", font=self.f_small, fg=DIM, bg=BG, anchor="w",
                                 justify="left", wraplength=CARD_W - 30)
        self.c_recent.pack(fill="x")
        self.c_err = tk.Label(f, text="", font=self.f_small, fg=RED, bg=BG, anchor="w",
                              justify="left", wraplength=CARD_W - 30)
        self.c_err.pack(fill="x")

    def button(self, parent, text, cmd, tip):
        b = tk.Label(parent, text=text, font=self.f_bold, fg=DIM, bg=BG, cursor="hand2",
                     padx=5)
        b.pack(side="right")
        b.bind("<Button-1>", lambda e: (cmd(), "break")[1])
        b.bind("<Enter>", lambda e: b.cget("fg") == DIM and b.config(fg=GOLD))
        b.bind("<Leave>", lambda e: b.cget("fg") == GOLD and b.config(fg=DIM))
        b._is_button = True
        return b

    def rule(self, f):
        tk.Frame(f, bg=EDGE, height=1).pack(fill="x", pady=7)

    def round_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
               x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.canvas.create_polygon(pts, smooth=True, **kw)

    def clamp(self, x, y, w, h):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        return max(0, min(int(x), sw - w)), max(0, min(int(y), sh - h))

    # ── drag vs click ───────────────────────────────────────────────────────
    def bind_drag(self, w):
        if getattr(w, "_is_button", False) or isinstance(w, tk.Text):
            return
        w.bind("<ButtonPress-1>", self.on_press)
        w.bind("<B1-Motion>", self.on_motion)
        w.bind("<ButtonRelease-1>", self.on_release)
        for c in w.winfo_children():
            self.bind_drag(c)

    def on_press(self, e):
        self._drag = (e.x_root, e.y_root, self.root.winfo_x(), self.root.winfo_y(), False)

    def on_motion(self, e):
        if not self._drag:
            return
        x0, y0, wx, wy, moved = self._drag
        dx, dy = e.x_root - x0, e.y_root - y0
        if moved or abs(dx) + abs(dy) > 4:
            self._drag = (x0, y0, wx, wy, True)
            self.root.geometry(f"+{wx + dx}+{wy + dy}")

    def on_release(self, e):
        if not self._drag:
            return
        moved = self._drag[4]
        self._drag = None
        if moved:
            self.pos = [self.root.winfo_x(), self.root.winfo_y()]
            self.save_prefs()
        elif not self.expanded:
            self.toggle()

    def toggle(self):
        self.expanded = not self.expanded
        self.stop_armed = False
        self.save_prefs()
        self.build()

    def save_prefs(self):
        save_json(PREFS_PATH, {"pos": self.pos, "expanded": self.expanded})

    # ── controls ────────────────────────────────────────────────────────────
    def write_control(self, cmd):
        if self.demo:
            return
        try:
            with open(CONTROL_PATH, "w", encoding="utf-8") as f:
                f.write(cmd)
        except Exception:
            pass

    def on_pause(self):
        st = (self.status or {}).get("state")
        cur = ""
        try:
            cur = open(CONTROL_PATH, encoding="utf-8").read().strip()
        except Exception:
            pass
        if st == "paused" or cur == "pause":
            self.write_control("resume")
        else:
            self.write_control("pause")

    def on_stop(self):
        if not self.stop_armed:            # two clicks — no dialogs
            self.stop_armed = True
            self.b_stop.config(text="stop?", fg=RED)
            self.root.after(3000, self.disarm)
            return
        self.write_control("stop")
        self.b_stop.config(text="stopping…", fg=RED)

    def disarm(self):
        if self.stop_armed and self.expanded:
            self.stop_armed = False
            try:
                self.b_stop.config(text="■", fg=DIM)
            except tk.TclError:
                pass

    # ── data → screen ───────────────────────────────────────────────────────
    def state_text(self, s):
        st = s.get("state", "")
        if st == "resting":
            t = parse_iso(s.get("resume_at") or "")
            return f"resting — resumes {t.strftime('%H:%M')}" if t else "resting"
        return {"translating": "translating", "paused": "paused", "done": "finished",
                "stopped": "stopped", "starting": "starting…", "error": "error"}.get(st, st)

    def render(self):
        s = self.status
        if s is None:
            if self.expanded:
                self.c_state.config(text="waiting for Tertius…")
            else:
                self.p_state.config(text="waiting for Tertius…")
                self.p_frac.config(text="")
            return
        done, total = s.get("translated", 0), s.get("total", 0)
        left = s.get("remaining", max(0, total - done))
        stxt = self.state_text(s)
        if not self.expanded:
            self.p_state.config(text=stxt)
            self.p_frac.config(text=f"{fmt(done)} / {fmt(total)}")
            return
        st = s.get("state")
        self.c_state.config(text=stxt)
        self.c_dot.config(fg={"translating": GREEN, "resting": GOLD, "paused": GOLD,
                              "error": RED}.get(st, DIM))
        self.b_pause.config(text="▶" if st == "paused" else "‖")
        cur = s.get("current") or []
        if cur:
            c0 = cur[0]
            self.c_cur.config(text=f"{c0.get('id', '')}" +
                              (f" — {c0['name']}" if c0.get("name") else ""))
            more = len(cur) - 1
            self.c_cur2.config(text=(f"{c0.get('lines', '?')} lines"
                                     + (f"  ·  +{more} more in this batch" if more > 0 else "")))
        else:
            self.c_cur.config(text="All done ✓" if st == "done" else "—")
            self.c_cur2.config(text="")
        self.c_done.config(text=f"{fmt(done)} / {fmt(total)}")
        self.c_left.config(text=f"{fmt(left)} / {fmt(total)}")
        frac = (done / total) if total else 0
        self.bar.update_idletasks()
        bw = max(1, self.bar.winfo_width())
        self.bar.delete("all")
        self.bar.create_rectangle(0, 0, int(bw * frac), 6, fill=LACUNA, width=0)
        sess = s.get("session_done", 0)
        self.c_pct.config(text=f"{frac * 100:.1f}%  ·  {fmt(sess)} this session")

        ll = s.get("last_line") or {}
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        if ll:
            self.insert_lacuna(ll.get("greek", ""), "greek")
            self.txt.insert("end", "\n")
            self.insert_lacuna(ll.get("english", ""), "eng")
        else:
            self.txt.insert("end", "The first line will appear here.", "eng")
        self.txt.config(state="disabled")

        rec = [r.get("id", "") for r in (s.get("recent") or [])][:4]
        flags = s.get("lacuna_flags", 0)
        line = ("Recently finished: " + " · ".join(rec)) if rec else ""
        if flags:
            line += f"\n⚠ {flags} flagged for lacuna review (py tertius.py --review)"
        self.c_recent.config(text=line)
        err = s.get("last_error")
        self.c_err.config(text=f"Last error: {err}" if err else "")

    def insert_lacuna(self, text, base):
        pos = 0
        for m in LACUNA_RX.finditer(text):
            if m.start() > pos:
                self.txt.insert("end", text[pos:m.start()], base)
            self.txt.insert("end", m.group(0), (base, "lac"))
            pos = m.end()
        self.txt.insert("end", text[pos:], base)

    # ── loop ────────────────────────────────────────────────────────────────
    def is_stale(self, s):
        hb = parse_iso(s.get("heartbeat") or "")
        if not hb:
            return False
        age = (datetime.now(hb.tzinfo) - hb).total_seconds()
        return age > STALE_SEC

    def tick(self):
        if self.closing:
            return
        s = demo_status() if self.demo else load_json(STATUS_PATH)
        if s is not None:
            self.status = s
            self.missing_since = None
            st = s.get("state")
            if st in ("done", "stopped"):
                self.render()
                self.root.after(6000, self.fade_out)
                self.closing = True
                return
            if self.is_stale(s):
                self.fade_out()
                return
        elif self.missing_since and time.time() - self.missing_since > 90:
            self.fade_out()
            return
        try:
            self.render()
        except tk.TclError:
            pass
        self.root.after(1000, self.tick)

    def animate(self):
        """Gentle quill pulse while translating."""
        try:
            if (self.status or {}).get("state") == "translating":
                self.pulse = not self.pulse
                self.quill.config(fg=GOLD if self.pulse else "#8a7650")
            else:
                self.quill.config(fg=GOLD)
        except (tk.TclError, AttributeError):
            pass
        self.root.after(700, self.animate)

    def fade_in(self):
        self.alpha = min(0.96, self.alpha + 0.12)
        try:
            self.root.attributes("-alpha", self.alpha)
        except tk.TclError:
            return
        if self.alpha < 0.96:
            self.root.after(30, self.fade_in)

    def fade_out(self):
        self.closing = True
        self.alpha -= 0.08
        if self.alpha <= 0:
            self.root.destroy()
            return
        try:
            self.root.attributes("-alpha", self.alpha)
        except tk.TclError:
            self.root.destroy(); return
        self.root.after(40, self.fade_out)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    TertiusWidget(demo="--demo" in sys.argv).run()

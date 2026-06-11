#!/usr/bin/env python3
"""capture_welcome_shots.py — one-off: render the 4 welcome-screen feature
states in headless Edge and save real screenshots to static/media/welcome/.

    python capture_welcome_shots.py [state ...]
"""
import os, sys, time

from selenium import webdriver
from selenium.webdriver.edge.options import Options

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "static", "media", "welcome")
os.makedirs(OUT, exist_ok=True)

BASE = "http://localhost:5000"
W, H = 1600, 900

WAIT_DATA = """
const done = arguments[arguments.length - 1];
(function poll(n) {
    if (typeof manuscripts !== 'undefined' && manuscripts.length > 100
        && typeof networkData !== 'undefined' && networkData) return done(manuscripts.length);
    if (n > 50) return done('timeout');
    setTimeout(() => poll(n + 1), 500);
})(0);
"""

STATES = {
    # 1 — Search & study manuscripts: genre orbs + Writing Stand diglot reader
    "feature-manuscripts": """
        ['Matthew','John','Romans','Acts','Luke','Mark','Hebrews'].forEach(b => { try { showBookOnMap(b); } catch(e){} });
        const ms = manuscripts.find(m => m.id === 'P46') || manuscripts.find(m => m.genre === 'new-testament');
        openWritingStand(ms, null);
        map.invalidateSize();
        map.setView(geoToCRS(30.6765, 28.5383), 5, {animate:false});
    """,
    # 2 — Route planner: Rome -> Byzantion fastest multi-modal route
    #     (gold road legs + dashed blue sea legs + travel-days readout)
    "feature-routes": """
        const tgl = document.getElementById('route-planner-toggle');
        if (tgl && !tgl.checked) { tgl.checked = true; tgl.dispatchEvent(new Event('change', {bubbles:true})); }
        setActiveSlot('from');
        selectCity('roma');          // fills From, advances to To slot
        selectCity('byzantion');     // fills To + computeAndShow() (runs on rAF)
        map.invalidateSize();
        map.setView(geoToCRS(20.5, 40.5), 5.5, {animate:false});
    """,
    # 3 — Social networks: Pauline 62-person network graph over the Aegean
    "feature-social": """
        if (typeof pnSetActive === 'function') pnSetActive(true);
        else document.getElementById('sn-pauline-btn').click();
        map.invalidateSize();
        map.setView(geoToCRS(25.5, 38.8), 6, {animate:false});
    """,
    # 4 — Manuscript networks: Romans (Corinth -> Rome) land+sea routes
    "feature-msnetworks": """
        if (typeof mnActivateLetter === 'function') mnActivateLetter(MN_LETTERS[0]);
        map.invalidateSize();
        map.setView(geoToCRS(17.5, 40), 5.5, {animate:false});
    """,
}


def load_with_retries(driver):
    for attempt in range(8):
        driver.get(BASE)
        n = driver.execute_async_script(WAIT_DATA)
        if n != "timeout":
            return n
        print(f"  data load attempt {attempt + 1} failed; reloading...")
    sys.exit("manuscripts feed never loaded")


# Undo whatever the previous state turned on (popups, orbs, routes, networks)
CLEANUP = """
    map.closePopup();
    document.getElementById('writing-stand').classList.remove('open');
    try { [...activeMsBooks].forEach(b => hideBookOnMap(b)); } catch(e){}
    try { const cb = document.getElementById('clear-btn'); cb && cb.click(); } catch(e){}
    try { const tgl = document.getElementById('route-planner-toggle');
          if (tgl && tgl.checked) { tgl.checked = false; tgl.dispatchEvent(new Event('change', {bubbles:true})); } } catch(e){}
    try { typeof pnSetActive === 'function' && pnSetActive(false); } catch(e){}
"""


def main():
    wanted = sys.argv[1:] or list(STATES)
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument(f"--window-size={W},{H}")
    opts.add_argument("--force-device-scale-factor=1")
    opts.add_argument("--hide-scrollbars")
    driver = webdriver.Edge(options=opts)
    driver.set_script_timeout(45)
    try:
        n = load_with_retries(driver)       # load ONCE; clean between states
        print(f"data ready ({n})")
        for name in wanted:
            driver.execute_script(CLEANUP + STATES[name])
            if name == "feature-routes":
                # runRoute is deferred to a rAF that sometimes never lands in
                # headless; poll for the drawn route and kick it if needed.
                drawn = driver.execute_async_script("""
                    const done = arguments[arguments.length - 1];
                    let tries = 0;
                    (function poll() {
                        let total = 0;
                        routeLayer.eachLayer(() => total++);
                        if (total > 0) return done(total);
                        if (tries === 8) { try { runRoute(); } catch(e){} }
                        if (tries++ > 16) return done(0);
                        setTimeout(poll, 500);
                    })();
                """)
                print(f"  route polylines: {drawn}")
            time.sleep(4)                   # tiles render + layout settle
            path = os.path.join(OUT, name + ".png")
            driver.save_screenshot(path)
            print(f"saved {path} ({os.path.getsize(path)} bytes)")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()

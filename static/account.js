/* ===========================================================================
 * account.js — accounts + freemium paywall UI for the ManuscriptDB agent
 * ---------------------------------------------------------------------------
 * Self-contained and non-invasive: it injects its own styles + modals, shows a
 * small account badge, and intercepts calls to /api/agent-search so it can pop
 * the login modal (401) or the paywall (402) without touching script.js.
 *
 * Phase 1: the "Subscribe" button is a placeholder until the Stripe step.
 * =========================================================================== */
(function () {
  "use strict";

  var state = { logged_in: false, email: null, subscribed: false,
                remaining: null, limit: null };

  /* ---- tiny helpers ---- */
  function api(path, method, body) {
    return fetch(path, {
      method: method || "GET",
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, status: r.status, data: j }; }); });
  }
  function el(id) { return document.getElementById(id); }

  /* ---- styles ---- */
  function injectStyles() {
    var css = ""
      + ".mdb-badge{position:fixed;top:10px;right:12px;z-index:99999;font:13px/1.3 system-ui,sans-serif;"
      + "background:#1c1c22;color:#eee;border:1px solid #3a3a44;border-radius:8px;padding:7px 11px;"
      + "box-shadow:0 2px 10px rgba(0,0,0,.35);display:flex;gap:8px;align-items:center}"
      + ".mdb-badge a{color:#8ab4ff;cursor:pointer;text-decoration:none}"
      + ".mdb-badge a:hover{text-decoration:underline}"
      + ".mdb-pill{background:#2a2a32;border-radius:20px;padding:2px 9px;font-size:12px}"
      + ".mdb-overlay{position:fixed;inset:0;z-index:100000;background:rgba(0,0,0,.55);"
      + "display:none;align-items:center;justify-content:center}"
      + ".mdb-overlay.open{display:flex}"
      + ".mdb-card{background:#17171c;color:#eee;width:340px;max-width:92vw;border:1px solid #33333d;"
      + "border-radius:14px;padding:22px;font:14px/1.45 system-ui,sans-serif;box-shadow:0 12px 40px rgba(0,0,0,.5)}"
      + ".mdb-card h2{margin:0 0 4px;font-size:19px}"
      + ".mdb-card p{margin:6px 0 14px;color:#b9b9c4}"
      + ".mdb-card input{width:100%;box-sizing:border-box;margin:6px 0;padding:10px;border-radius:8px;"
      + "border:1px solid #3a3a44;background:#0f0f13;color:#fff;font-size:14px}"
      + ".mdb-btn{width:100%;padding:11px;border:0;border-radius:8px;background:#3b6cf6;color:#fff;"
      + "font-size:15px;font-weight:600;cursor:pointer;margin-top:6px}"
      + ".mdb-btn:hover{background:#2f59d6}"
      + ".mdb-btn.alt{background:#2a2a32}"
      + ".mdb-link{color:#8ab4ff;cursor:pointer;text-align:center;margin-top:12px;font-size:13px}"
      + ".mdb-err{color:#ff7676;min-height:16px;font-size:13px;margin:2px 0 4px}"
      + ".mdb-x{float:right;cursor:pointer;color:#888;font-size:18px;line-height:1}";
    var s = document.createElement("style"); s.textContent = css; document.head.appendChild(s);
  }

  /* ---- badge ---- */
  function renderBadge() {
    var b = el("mdb-badge");
    if (!b) { b = document.createElement("div"); b.id = "mdb-badge"; b.className = "mdb-badge"; document.body.appendChild(b); }
    if (!state.logged_in) {
      b.innerHTML = '<span>Search assistant:</span> <a id="mdb-open-login">Sign in</a> '
                  + '<span style="color:#555">/</span> <a id="mdb-open-register">Register</a>';
      el("mdb-open-login").onclick = function () { openAuth("login"); };
      el("mdb-open-register").onclick = function () { openAuth("register"); };
    } else if (state.subscribed) {
      b.innerHTML = '<span class="mdb-pill">★ Unlimited</span> <span>' + esc(state.email) + '</span> '
                  + '<a id="mdb-manage">Manage</a> <a id="mdb-logout">Log out</a>';
      el("mdb-manage").onclick = openPortal;
      el("mdb-logout").onclick = doLogout;
    } else {
      var left = state.remaining == null ? "" : state.remaining;
      b.innerHTML = '<span class="mdb-pill">' + left + ' free left today</span> '
                  + '<a id="mdb-upgrade">Upgrade</a> '
                  + '<a id="mdb-logout">Log out</a>';
      el("mdb-upgrade").onclick = openPaywall;
      el("mdb-logout").onclick = doLogout;
    }
  }
  function esc(s){ return (s||"").replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];}); }

  /* ---- auth modal ---- */
  function openAuth(mode) {
    closeModals();
    var isReg = mode === "register";
    var o = ensureOverlay("mdb-auth");
    o.querySelector(".mdb-card").innerHTML =
        '<span class="mdb-x" id="mdb-auth-x">&times;</span>'
      + '<h2>' + (isReg ? "Create your account" : "Welcome back") + '</h2>'
      + '<p>' + (isReg ? "Free: 5 searches a day. Subscribe anytime for unlimited."
                       : "Sign in to keep using the search assistant.") + '</p>'
      + '<div class="mdb-err" id="mdb-auth-err"></div>'
      + '<input id="mdb-email" type="email" placeholder="you@example.com" autocomplete="email">'
      + '<input id="mdb-pass" type="password" placeholder="Password (min 8 chars)" autocomplete="'
      + (isReg ? "new-password" : "current-password") + '">'
      + '<button class="mdb-btn" id="mdb-auth-go">' + (isReg ? "Create account" : "Sign in") + '</button>'
      + '<div class="mdb-link" id="mdb-auth-swap">'
      + (isReg ? "Already have an account? Sign in" : "New here? Create an account") + '</div>';
    o.classList.add("open");
    el("mdb-auth-x").onclick = closeModals;
    el("mdb-auth-swap").onclick = function () { openAuth(isReg ? "login" : "register"); };
    el("mdb-auth-go").onclick = function () { submitAuth(isReg); };
    el("mdb-pass").onkeydown = function (e) { if (e.key === "Enter") submitAuth(isReg); };
    el("mdb-email").focus();
  }

  function submitAuth(isReg) {
    var email = el("mdb-email").value.trim();
    var pass = el("mdb-pass").value;
    var errEl = el("mdb-auth-err"); errEl.textContent = "";
    api(isReg ? "/api/register" : "/api/login", "POST", { email: email, password: pass })
      .then(function (res) {
        if (!res.ok) { errEl.textContent = res.data.message || "Something went wrong."; return; }
        Object.assign(state, res.data); closeModals(); renderBadge();
      })
      .catch(function () { errEl.textContent = "Network error — try again."; });
  }

  function openPortal() {
    api("/api/billing-portal", "POST").then(function (res) {
      if (res.ok && res.data && res.data.url) { window.location = res.data.url; }
      else { alert((res.data && res.data.message) || "Couldn't open the billing portal."); }
    }).catch(function () { alert("Network error opening the billing portal."); });
  }

  function doLogout() {
    api("/api/logout", "POST").then(function () {
      state = { logged_in: false, email: null, subscribed: false, remaining: null, limit: null };
      renderBadge();
    });
  }

  /* ---- paywall modal ---- */
  function openPaywall(info) {
    closeModals();
    var msg = (info && info.message) || "You've used your free searches for today.";
    var o = ensureOverlay("mdb-pay");
    o.querySelector(".mdb-card").innerHTML =
        '<span class="mdb-x" id="mdb-pay-x">&times;</span>'
      + '<h2>Unlock unlimited searches</h2>'
      + '<p>' + esc(msg) + '</p>'
      + '<p style="color:#e7e7ef"><b>$10 CAD / month</b> — unlimited use of the search assistant, '
      + 'resets never. Cancel anytime.</p>'
      + '<button class="mdb-btn" id="mdb-subscribe">Subscribe — $10 CAD/mo</button>'
      + '<button class="mdb-btn alt" id="mdb-pay-close">Maybe later</button>';
    o.classList.add("open");
    el("mdb-pay-x").onclick = closeModals;
    el("mdb-pay-close").onclick = closeModals;
    el("mdb-subscribe").onclick = startCheckout;
  }

  function startCheckout() {
    if (!state.logged_in) { openAuth("register"); return; }
    // Phase 2 (Stripe) wires this to a real Checkout session. Until then:
    api("/api/create-checkout-session", "POST").then(function (res) {
      if (res.ok && res.data && res.data.url) { window.location = res.data.url; }
      else { alert("Subscriptions are launching shortly — payment isn't switched on yet."); }
    }).catch(function () {
      alert("Subscriptions are launching shortly — payment isn't switched on yet.");
    });
  }

  /* ---- modal plumbing ---- */
  function ensureOverlay(id) {
    var o = el(id);
    if (!o) {
      o = document.createElement("div"); o.id = id; o.className = "mdb-overlay";
      o.innerHTML = '<div class="mdb-card"></div>';
      o.addEventListener("click", function (e) { if (e.target === o) closeModals(); });
      document.body.appendChild(o);
    }
    return o;
  }
  function closeModals() {
    ["mdb-auth", "mdb-pay"].forEach(function (id) { var o = el(id); if (o) o.classList.remove("open"); });
  }

  /* ---- intercept the agent search so we can react to 401/402 ---- */
  function installFetchHook() {
    var _fetch = window.fetch;
    window.fetch = function () {
      var args = arguments;
      var url = (typeof args[0] === "string") ? args[0] : (args[0] && args[0].url) || "";
      var p = _fetch.apply(this, args);
      if (url.indexOf("/api/agent-search") === -1) return p;
      return p.then(function (res) {
        if (res.status === 401) { openAuth("register"); }
        else if (res.status === 402) { res.clone().json().then(openPaywall).catch(function(){ openPaywall(); }); }
        else if (res.ok) { refreshMe(); }
        return res;   // hand the original response back to script.js untouched
      });
    };
  }

  function refreshMe() {
    api("/api/me").then(function (res) { Object.assign(state, res.data); renderBadge(); });
  }

  /* ---- boot ---- */
  function boot() { injectStyles(); installFetchHook(); refreshMe(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();

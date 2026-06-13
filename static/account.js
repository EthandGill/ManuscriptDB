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
      // Account badge — sits in the sidebar header (not fixed top-right);
      // GOLD bar with BLACK text.
      + ".mdb-badge{margin-top:12px;font:11.5px/1.35 'Inter',system-ui,sans-serif;"
      + "background:linear-gradient(180deg,#d8bd86,#c9a96e);color:#0d0c07;"
      + "border:1px solid #b0935a;border-radius:7px;padding:8px 11px;"
      + "display:flex;flex-direction:column;gap:6px}"
      // Logged-out: the whole gold bar is a button that presses in on hover.
      + ".mdb-badge--login{cursor:pointer;text-align:center;padding:10px 11px;"
      + "box-shadow:inset 0 1px 0 rgba(255,255,255,.45),0 2px 5px rgba(0,0,0,.45);"
      + "transition:background .1s,box-shadow .1s,transform .05s}"
      + ".mdb-badge--login:hover{background:linear-gradient(180deg,#c4a361,#b08f52);"
      + "box-shadow:inset 0 2px 6px rgba(0,0,0,.55);transform:translateY(1px)}"
      + ".mdb-badge--login a:hover{color:#fff;text-decoration:none}"
      + ".mdb-badge .mdb-row{display:flex;gap:8px;align-items:center;justify-content:center;flex-wrap:wrap}"
      + ".mdb-badge a{color:#0d0c07;cursor:pointer;text-decoration:none;font-weight:800;letter-spacing:.03em}"
      + ".mdb-badge a:hover{text-decoration:underline}"
      // Logged-in: compact one-line top (Log out + email left, quota right).
      + ".mdb-top{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:9.5px}"
      + ".mdb-left{display:flex;align-items:center;gap:6px;min-width:0;flex:1}"
      + ".mdb-left a{white-space:nowrap}"
      + ".mdb-badge .mdb-email{color:#0d0c07;font-weight:700;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}"
      + ".mdb-quota{font-size:9px;color:#3a2f18;font-weight:800;letter-spacing:.01em;white-space:nowrap;flex:none}"
      // Subscribe bar — dark with gold text; inverts to cream/black on hover.
      + ".mdb-sub-bar{display:block;width:100%;box-sizing:border-box;cursor:pointer;"
      + "background:#0d0c07;color:#c9a96e;border:1px solid #0d0c07;border-radius:5px;"
      + "padding:5px 8px;font-size:9px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;text-align:center;"
      + "transition:background .12s,color .12s}"
      + ".mdb-sub-bar:hover{background:#fff5e0;color:#0d0c07}"
      + ".mdb-overlay{position:fixed;inset:0;z-index:100000;background:rgba(0,0,0,.62);"
      + "display:none;align-items:center;justify-content:center}"
      + ".mdb-overlay.open{display:flex}"
      + ".mdb-card{background:#0d0c07;color:#d6c39a;width:340px;max-width:92vw;border:1px solid #3a3020;"
      + "border-radius:12px;padding:22px;font:14px/1.45 'Inter',system-ui,sans-serif;box-shadow:0 18px 60px rgba(0,0,0,.7)}"
      + ".mdb-card h2{margin:0 0 4px;font-size:19px;color:#c9a96e;font-family:'Cinzel',serif}"
      + ".mdb-card p{margin:6px 0 14px;color:#a89878}"
      + ".mdb-card input{width:100%;box-sizing:border-box;margin:6px 0;padding:10px;border-radius:7px;"
      + "border:1px solid #2a2416;background:#15130d;color:#d6c39a;font-size:14px}"
      + ".mdb-card input:focus{border-color:#c9a96e;outline:none}"
      + ".mdb-btn{width:100%;padding:11px;border:0;border-radius:7px;"
      + "background:linear-gradient(180deg,#d8bd86,#c9a96e);color:#0d0c07;"
      + "font-size:15px;font-weight:700;cursor:pointer;margin-top:6px}"
      + ".mdb-btn:hover{background:#d8bd86}"
      + ".mdb-btn.alt{background:#1e1a12;color:#c9a96e;border:1px solid #3a3020}"
      + ".mdb-link{color:#c9a96e;cursor:pointer;text-align:center;margin-top:12px;font-size:13px}"
      + ".mdb-err{color:#c98a7a;min-height:16px;font-size:13px;margin:2px 0 4px}"
      + ".mdb-x{float:right;cursor:pointer;color:#6a5d42;font-size:18px;line-height:1}"
      + ".mdb-x:hover{color:#c9a96e}";
    var s = document.createElement("style"); s.textContent = css; document.head.appendChild(s);
  }

  /* ---- badge ---- */
  function renderBadge() {
    var b = el("mdb-badge");
    if (!b) {
      b = document.createElement("div"); b.id = "mdb-badge"; b.className = "mdb-badge";
      // Place it just below the header title (inside #sidebar-header), not
      // fixed top-right where it overlapped the reading-stand close button.
      var host = document.getElementById("sidebar-header") || document.body;
      host.appendChild(b);
    }
    var lim = state.limit == null ? (state.free_limit == null ? 5 : state.free_limit) : state.limit;
    b.classList.toggle("mdb-badge--login", !state.logged_in);
    if (!state.logged_in) {
      // Gold pressable bar, black text: "Login or Sign up".
      b.innerHTML = '<div class="mdb-row"><a id="mdb-open-login">Login</a>'
                  + '<span>or</span><a id="mdb-open-register">Sign up</a></div>';
      el("mdb-open-login").onclick = function () { openAuth("login"); };
      el("mdb-open-register").onclick = function () { openAuth("register"); };
    } else if (state.subscribed) {
      // Compact: Log out + email on one line, "Unlimited" across from email,
      // manage bar below.
      b.innerHTML = '<div class="mdb-top"><span class="mdb-left">'
                  + '<a id="mdb-logout">Log out</a>'
                  + '<span class="mdb-email">' + esc(state.email) + '</span></span>'
                  + '<span class="mdb-quota">Unlimited</span></div>'
                  + '<div class="mdb-sub-bar" id="mdb-manage">Manage ManuscriptDB Unlimited</div>';
      el("mdb-manage").onclick = openPortal;
      el("mdb-logout").onclick = doLogout;
    } else {
      // Compact: Log out + email on one line, free-search count across from
      // email, Subscribe bar below.
      b.innerHTML = '<div class="mdb-top"><span class="mdb-left">'
                  + '<a id="mdb-logout">Log out</a>'
                  + '<span class="mdb-email">' + esc(state.email) + '</span></span>'
                  + '<span class="mdb-quota">' + lim + ' free daily AI searches</span></div>'
                  + '<div class="mdb-sub-bar" id="mdb-upgrade">Subscribe to ManuscriptDB Unlimited</div>';
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

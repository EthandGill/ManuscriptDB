# Taking ManuscriptDB live on a custom domain

End result: a permanent, always-on address like `https://manuscriptdb.com` that
stays up even when your PC is off, with automatic HTTPS.

**Total cost:** ~$5/month hosting + ~$10–12/year for the domain name.

I've already made your app production-ready (see "What I changed" at the bottom).
You just need to (1) pick a host, (2) push the code, (3) buy + point a domain.

---

## Recommended path: Railway ($5/mo) + Cloudflare domain

Railway is the best fit for your budget: a true always-on $5/month plan, Git-push
deploys, free HTTPS, and one-click custom domains. (PythonAnywhere's old $5 plan
was discontinued in Jan 2026 and is now $10/mo — see the fallback below if you'd
rather avoid GitHub entirely.)

### Step 1 — Put the project on GitHub
Railway deploys from a Git repo. From `C:\ManuscriptDB`:

```bash
git init
git add .
git commit -m "Deploy ManuscriptDB"
```

Create an empty repo at <https://github.com/new> (e.g. `manuscriptdb`), then:

```bash
git remote add origin https://github.com/YOURNAME/manuscriptdb.git
git branch -M main
git push -u origin main
```

> Your repo is ~36 MB (mostly map tiles in `static/tiles/`) — well within
> GitHub's limits, so just commit everything.

### Step 2 — Deploy on Railway
1. Sign up at <https://railway.com> with your GitHub account.
2. **New Project → Deploy from GitHub repo →** pick `manuscriptdb`.
3. Railway auto-detects Python, installs `requirements.txt`, and runs the
   `Procfile` I added (`gunicorn app:app`). No config needed.
4. Open **Settings → Networking → Generate Domain** to get a temporary
   `…up.railway.app` URL and confirm it works.
5. Upgrade to the **Hobby plan ($5/mo)** so the app stays always-on.

### Step 3 — Buy a domain
Cheapest at-cost registrar is **Cloudflare** (<https://dash.cloudflare.com> →
Domain Registration), typically ~$10/yr for `.com` with free WHOIS privacy.
Namecheap and Porkbun are good alternatives. Buy the name you want
(e.g. `manuscriptdb.com`).

### Step 4 — Connect the domain to Railway
1. In Railway: **Settings → Networking → Custom Domain →** type your domain
   (e.g. `manuscriptdb.com` or `www.manuscriptdb.com`). Railway shows you a
   **CNAME target** (something like `xxxx.up.railway.app`).
2. In your registrar's DNS settings, add the record Railway tells you:
   - For a subdomain (`www`): a **CNAME** `www → xxxx.up.railway.app`.
   - For the root/apex (`manuscriptdb.com`): use a **CNAME** if your registrar
     supports CNAME flattening (Cloudflare does), otherwise the **A record**
     Railway provides.
3. Wait a few minutes for DNS to propagate. Railway auto-issues a free TLS
   certificate, so `https://` works automatically.

Done — your site is live on your own domain. ✅

---

## Updating the site later
Just commit and push; Railway redeploys automatically:

```bash
git add .
git commit -m "Add new manuscripts"
git push
```

(Keep running the `grab-manuscript` imports locally on your PC, then push the
updated `manuscripts/` folder.)

---

## Fallback: PythonAnywhere ($10/mo, no GitHub needed)
If you'd rather upload a zip than use Git, follow the existing
`DEPLOY_pythonanywhere.md` in this folder — it's the same flow, just note the
plan is now **$10/mo** (the Developer tier) for custom-domain support, not $5.
Add your custom domain under the **Web** tab → **Add a new domain**, then create
the CNAME it shows you at your registrar.

## Other options at a glance
- **Render** — has a real free tier, but free apps *sleep* after 15 min (30–60s
  cold start) and paid always-on plans jumped to ~$25/mo in 2026. Good only if
  you're fine with the free tier's sleeping.
- **Fly.io** — ~$5/mo for a small always-on machine, first 10 TLS certs free,
  but pricing is usage-based and can creep up; more involved setup than Railway.

---

## What I changed in your project
- **`requirements.txt`** — added `gunicorn` (the production web server; the Flask
  dev server in `app.py` isn't meant for public traffic).
- **`Procfile`** — tells Railway/Render/Fly how to start the app:
  `gunicorn app:app …`. Binds to the host's `$PORT`, 2 workers + threads.

I booted the app under gunicorn to verify: `/` returns 200 and
`/api/manuscripts` serves the full gzipped feed (~1 MB) correctly. Nothing in
your code needs to change — the `if __name__ == "__main__"` dev-server block is
simply ignored in production.

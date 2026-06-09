# ManuscriptDB → live on your own domain: the cheat-sheet

Follow top to bottom. ~30–40 min, mostly waiting. Cost: **$5/mo (Railway) + ~$10–12/yr (domain)**.

App is already deploy-ready — I added `gunicorn` to `requirements.txt` and a
`Procfile`, and verified the app boots under gunicorn.

---

## A. On your PC — get the code onto GitHub (one time)

Open **Command Prompt** (Win key → type `cmd` → Enter), then:

```cmd
cd C:\ManuscriptDB
rmdir /s /q .git        :: removes the empty .git folder left from my attempt
git init
git add .
git commit -m "Deploy ManuscriptDB"
```

> No git installed? Get it at <https://git-scm.com/download/win>, accept defaults,
> reopen Command Prompt.

**Create the GitHub repo (browser):**
1. Log in / sign up at <https://github.com>.
2. Go to <https://github.com/new>.
3. Repository name: `manuscriptdb`. Leave it **Public** (or Private — both work).
   Do **not** add a README/.gitignore/license. Click **Create repository**.
4. On the next page copy your repo URL (e.g. `https://github.com/YOURNAME/manuscriptdb.git`).

**Push (back in Command Prompt)** — paste your URL:

```cmd
git remote add origin https://github.com/YOURNAME/manuscriptdb.git
git branch -M main
git push -u origin main
```

It'll open a browser window to authorize Git — approve it. When it finishes,
refresh the GitHub page; you should see all your files.

---

## B. Deploy on Railway (browser, $5/mo)

1. Sign up at <https://railway.com> — click **Login**, choose **Login with GitHub**,
   authorize.
2. Click **New Project → Deploy from GitHub repo**. If prompted, **Configure
   GitHub App** and grant access to your `manuscriptdb` repo, then pick it.
3. Railway auto-detects Python, installs `requirements.txt`, and starts the app
   with the `Procfile` (`gunicorn app:app`). Wait for the build to go green.
4. **Settings → Networking → Generate Domain.** Open the `…up.railway.app` URL —
   your site should load. (If a port box appears, enter `8080`; the Procfile binds
   to Railway's `$PORT` automatically, so usually nothing to set.)
5. **Upgrade to the Hobby plan ($5/mo)** under your workspace billing so the app
   stays always-on (free trial credit sleeps/expires).

---

## C. Buy a domain (browser, ~$10–12/yr)

Cheapest at-cost registrar: **Cloudflare** — <https://dash.cloudflare.com> →
**Domain Registration → Register Domains**. Search your name (e.g.
`manuscriptdb.com`), add to cart, pay. WHOIS privacy is free.
(Namecheap or Porkbun are fine alternatives.)

---

## D. Point the domain at Railway (browser)

1. In Railway: **Settings → Networking → Custom Domain** → type your domain.
   - Use `www.yourdomain.com` for the simplest setup, **or** the root
     `yourdomain.com`.
   - Railway shows a **CNAME target** like `abcd1234.up.railway.app`. Copy it.
2. In Cloudflare: **DNS → Records → Add record**:
   - **Type:** CNAME
   - **Name:** `www` (or `@` for the root — Cloudflare flattens CNAMEs at the apex)
   - **Target:** the `…up.railway.app` value Railway gave you
   - **Proxy status:** DNS only (grey cloud) is safest with Railway's own TLS.
   - Save.
3. (Optional) To make the bare `yourdomain.com` redirect to `www`, add the apex
   record too, or set a Cloudflare redirect rule.
4. Wait 2–30 min. Railway auto-issues a free HTTPS certificate. Done — your site
   is live at `https://yourdomain.com`. ✅

---

## Updating the site later
On your PC:
```cmd
cd C:\ManuscriptDB
git add .
git commit -m "Update manuscripts"
git push
```
Railway redeploys automatically. (Keep running `grab-manuscript` imports locally,
then push the updated `manuscripts/` folder.)

---

## If something breaks
- **Build fails on Railway** → open the **Deploy logs**; usually a missing line in
  `requirements.txt`. Yours just needs `Flask` + `gunicorn` (already set).
- **Site loads but no map tiles / manuscripts** → confirm `static/` and
  `manuscripts/` were pushed (check the file list on GitHub).
- **`git push` rejected** → you probably added a README on GitHub; run
  `git pull --rebase origin main` then `git push` again.
- **Domain not secure / not loading** → DNS can take up to an hour; verify the
  CNAME target matches exactly what Railway shows.

---

### No-GitHub alternative (PythonAnywhere, $10/mo)
If you'd rather not touch git at all, see `DEPLOY_pythonanywhere.md` — you upload a
zip of the folder in the browser. Note the plan is now **$10/mo** (Developer tier)
for custom-domain support. Add the domain under the **Web** tab → **Add a new
domain**, then create the CNAME it shows you in Cloudflare (step D above).

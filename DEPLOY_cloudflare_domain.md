# Point manuscriptdb.org at your localhost (Cloudflare named tunnel)

End state: `https://manuscriptdb.org` is a permanent public window onto the
ManuscriptDB app running on your PC. One copy of the site — your local one — so
the live domain and your localhost are always identical.

**Trade-off to accept:** the site is up only while your PC is on and both the
Flask app and the tunnel are running. (Installing both as services, step 7, makes
them start automatically on boot.)

The steps marked 🧑 are yours (account/DNS — I can't do them). The rest is the
config I already prepared.

---

## 1. 🧑 Own the domain and put it on Cloudflare

- If you don't own `manuscriptdb.org` yet, buy it (any registrar, ~$10/yr — `.org`
  is sometimes a bit more).
- Create a free Cloudflare account at <https://dash.cloudflare.com>.
- Click **Add a site**, enter `manuscriptdb.org`, pick the **Free** plan.
- Cloudflare gives you two **nameservers**. Go to wherever you bought the domain
  and replace its nameservers with those two. This is the step that "moves DNS to
  Cloudflare." It can take anywhere from minutes to a few hours to activate;
  Cloudflare emails you when the site is **Active**.

You can't run the tunnel on your domain until Cloudflare shows the site as Active.

## 2. Install cloudflared (if you don't have it)

```powershell
winget install --id Cloudflare.cloudflared -e
```
Close and reopen the terminal afterward.

## 3. 🧑 Log cloudflared into your Cloudflare account

```powershell
cloudflared tunnel login
```
This opens your browser. Pick the **manuscriptdb.org** zone and authorize. It
saves a cert into `C:\Users\Ethan\.cloudflared\`.

## 4. Create the tunnel

```powershell
cloudflared tunnel create manuscriptdb
```
It prints a **Tunnel UUID** and writes `<UUID>.json` into `.cloudflared\`.

## 5. Install the config

- Copy `cloudflared-config.yml` (in C:\ManuscriptDB) to
  `C:\Users\Ethan\.cloudflared\config.yml`.
- Open it and replace both `<TUNNEL-UUID>` placeholders with the UUID from step 4.

## 6. 🧑 Route the domain to the tunnel (creates the DNS records)

```powershell
cloudflared tunnel route dns manuscriptdb manuscriptdb.org
cloudflared tunnel route dns manuscriptdb www.manuscriptdb.org
```

## 7. Run it

Start your app in one terminal:
```powershell
cd C:\ManuscriptDB
python app.py
```
Start the tunnel in another:
```powershell
cloudflared tunnel run manuscriptdb
```
Visit `https://manuscriptdb.org` — it should show your local site.

**Make it permanent (auto-start on boot, no windows to keep open):** install the
tunnel as a Windows service from an **Administrator** terminal:
```powershell
cloudflared service install
```
For the Flask app to also survive reboots, run it under a process manager (e.g.
NSSM, or a scheduled task at logon running `python app.py`). Ask me and I'll set
that part up.

---

## Notes

- Cloudflare gives you HTTPS automatically — no certificate work needed.
- Because the tunnel makes an **outbound** connection from your PC to Cloudflare,
  you do NOT need to open any router ports or expose your IP.
- This is the free Cloudflare tier; the only cost is the domain registration.
- Editing manuscripts or running the onboarding loop updates the site live — no
  redeploy, because it's the same app.

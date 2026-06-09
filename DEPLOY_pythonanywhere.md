# Deploying ManuscriptDB to PythonAnywhere (free, permanent link)

End result: a permanent, always-on URL like `https://YOURUSERNAME.pythonanywhere.com`
that anyone can open. No credit card, no GitHub required.

You'll do this in your browser on pythonanywhere.com. The three files I prepared
(`requirements.txt`, `pythonanywhere_wsgi.py`, and this checklist) are already in
your project folder.

---

## 1. Make a free account

Go to <https://www.pythonanywhere.com/registration/register/beginner/> and sign
up for the free "Beginner" plan. Confirm your email and log in.

---

## 2. Get your project onto PythonAnywhere

Easiest route — upload a zip:

1. On your PC, zip your whole `C:\ManuscriptDB` folder into `ManuscriptDB.zip`
   (right-click the folder → *Send to → Compressed (zipped) folder*).
2. On PythonAnywhere, open the **Files** tab and use **Upload a file** to upload
   `ManuscriptDB.zip` into your home directory (`/home/YOURUSERNAME/`).
3. Open a **Bash console** (Consoles tab → *Bash*) and run:
   ```bash
   cd ~
   unzip ManuscriptDB.zip -d ManuscriptDB
   ls ManuscriptDB        # you should see app.py, manuscripts/, static/, templates/
   ```
   > If the zip already contains a top-level `ManuscriptDB` folder, you'll get
   > `~/ManuscriptDB/ManuscriptDB/...`. If so, run:
   > `mv ~/ManuscriptDB/ManuscriptDB/* ~/ManuscriptDB/` and re-check `ls`.

*(Alternative if your project is on GitHub: in the Bash console run
`git clone <your-repo-url> ManuscriptDB` instead of uploading a zip.)*

---

## 3. Install Flask

In the same Bash console (free tier, install into your user account):

```bash
pip install --user Flask
```

That's the only dependency — `app.py` otherwise uses just the Python standard
library.

---

## 4. Create the web app

1. Go to the **Web** tab → **Add a new web app** → **Next**.
2. When asked for a framework, choose **Manual configuration** (NOT "Flask" —
   we're using your existing `app.py`, not a generated one).
3. Choose a **Python version** — pick the newest offered (e.g. Python 3.10/3.11).
4. Click through to finish. It creates a placeholder web app.

---

## 5. Point it at your app (the WSGI file)

1. Still on the **Web** tab, find **Code → WSGI configuration file**. It's a link
   like `/var/www/YOURUSERNAME_pythonanywhere_com_wsgi.py`. Click it to edit.
2. **Delete everything** in that file.
3. Open `pythonanywhere_wsgi.py` from your project (Files tab), copy its contents,
   and **paste** them into the WSGI editor.
4. Change the one line `project_home = "/home/YOURUSERNAME/ManuscriptDB"` to use
   your real username. **Save** (green button, top right).

While on the Web tab, also set (under **Code**):
- **Source code:** `/home/YOURUSERNAME/ManuscriptDB`
- **Working directory:** `/home/YOURUSERNAME/ManuscriptDB`

---

## 6. (Optional but recommended) Serve the map tiles as static files

Your `static/` folder (map tiles, JS, CSS) serves faster and uses less of your
daily CPU allowance if PythonAnywhere serves it directly instead of Flask.

On the **Web** tab → **Static files** → **Enter URL / Directory**:
- **URL:** `/static/`
- **Directory:** `/home/YOURUSERNAME/ManuscriptDB/static/`

---

## 7. Reload and visit

Click the big green **Reload** button at the top of the Web tab, then open:

```
https://YOURUSERNAME.pythonanywhere.com
```

That's your permanent shareable link. 🎉

---

## Troubleshooting

- **"Something went wrong :-(" / error page** — open the **Error log** link on the
  Web tab; it shows the Python traceback. Most common cause is a wrong path or
  username in the WSGI file (step 5).
- **`ModuleNotFoundError: No module named 'app'`** — `project_home` in the WSGI
  file doesn't match where you unzipped the project. Check `ls /home/YOURUSERNAME/ManuscriptDB`
  actually contains `app.py`.
- **`ModuleNotFoundError: No module named 'flask'`** — re-run step 3, and make
  sure the Bash console's Python version matches the one you picked in step 4.
- **Page loads but no manuscripts / map tiles** — confirm the `manuscripts/` and
  `static/` folders uploaded fully, and that the static mapping in step 6 points
  at the right directory.

## Notes for this app specifically

- You don't need a `SECRET_KEY` or to disable debug mode: under PythonAnywhere's
  WSGI server the `if __name__ == "__main__": app.run(debug=True)` block in
  `app.py` never runs, so debug is already off in production.
- The `grab-manuscript` import scripts that fetch from NTVMR will NOT work on the
  free tier (outbound internet is restricted to a whitelist). Keep doing imports
  locally on your PC, then re-upload the updated `manuscripts/` folder.
- Free tier limits that matter here: ~512 MB disk (your tiles fit easily) and
  100 CPU-seconds/day of *compute* — serving pages/tiles is cheap, so a low-traffic
  reading site is fine. To update the live site later, re-upload changed files and
  hit **Reload**.
- Want a custom domain (e.g. `manuscripts.yoursite.com`) or more CPU? That needs a
  paid plan (~$5/month); everything above stays the same.

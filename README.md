# Rakshita Vijay — Portfolio

A static single-page portfolio (plain HTML/CSS/JS — no build step) modeled on the layout of ishandev.vercel.app, populated with your resume content.

## Files
- `index.html` — page structure & content
- `styles.css` — design tokens, layout, components
- `script.js` — theme toggle + scroll-spy nav
- `assets/rakshita.png` — your photo, extracted from the resume PDF

## Deploy to Vercel

**Option A — Vercel CLI (fastest)**
```bash
npm i -g vercel
cd portfolio
vercel
```
Accept the defaults (it auto-detects a static site). Run `vercel --prod` to push to production.

**Option B — GitHub + Vercel dashboard**
```bash
cd portfolio
git init
git add .
git commit -m "Initial portfolio"
git remote add origin <your-empty-github-repo-url>
git push -u origin main
```
Then on vercel.com → **Add New Project** → import the repo → Framework Preset: **Other** → Deploy.

## Before you publish
- Swap the `href="#"` placeholders in the **GitHub**, **LinkedIn**, and **Download resume** links (top of `index.html`, `<aside class="sidebar">`) for your real profile URLs and a hosted resume PDF link.
- Double check the phone/email in the sidebar — only email is shown right now; add a phone line the same way as the "Reach" row if you want it public.
- Swap `assets/rakshita.png` for a higher-res photo if you have one — the one here was pulled straight out of the resume PDF at 200×200.

## Use in venv
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 --version
which python3      # macOS/Linux
# where python      # Windows

python3 -m pip install -r requirements.txt

deactivate
```

# 🌸 AI Excuse Generator — Deployment Guide

## Your project structure
```
excuse_app/
├── app.py            ← main Streamlit app
├── flux_ai.py        ← image generator (Stability AI)
├── requirements.txt  ← fixed dependencies
├── packages.txt      ← system packages for Streamlit Cloud
└── .env              ← API keys (local only, don't commit!)
```

---

## STEP 1 — Set up API Keys

### On Streamlit Cloud (secrets)
1. Go to [share.streamlit.io](https://share.streamlit.io) → your app → ⚙️ Settings → **Secrets**
2. Paste this:
```toml
OPENROUTER_API_KEY = "sk-or-your-key-here"
STABILITY_API_KEY  = "sk-your-key-here"
```
3. Save → Reboot app.

### Locally (.env file)
Create `.env` in the project root:
```
OPENROUTER_API_KEY=sk-or-your-key-here
STABILITY_API_KEY=sk-your-key-here
```

---

## STEP 2 — Install locally (optional test)

```bash
# Delete old venv if you have one
rm -rf venv

# Create fresh venv
python3.11 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

---

## STEP 3 — Deploy to Streamlit Cloud

```bash
# 1. Make sure all files are saved
# 2. Init git if not done
git init
git add .
git commit -m "Initial commit — fixed deps + new UI"

# 3. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Then on [share.streamlit.io](https://share.streamlit.io):
1. Click **New app**
2. Select your GitHub repo
3. Main file path: `app.py`
4. Click **Deploy**

---

## What was fixed

| Issue | Fix |
|-------|-----|
| `pillow==10.2.0` fails on Python 3.13 | Upgraded to `Pillow==10.4.0` (Python 3.13 compatible) |
| `streamlit==1.31.0` outdated | Upgraded to `1.41.0` |
| `openai==0.28.0` | Pinned to `0.28.1` (stable, compatible) |
| APIs blocked locally | All keys now loaded from Streamlit secrets first |
| `packages.txt` had `libsndfile1` | Removed unnecessary package, kept `ffmpeg` only |

---

## Get your free API keys

- **OpenRouter** (for AI text): https://openrouter.ai — free tier available
- **Stability AI** (for images): https://platform.stability.ai — needed only for Proof Generator tab

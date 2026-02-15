# 🌸 AI Excuse Generator

A Streamlit web app that uses AI to generate believable, personalised excuses in multiple languages — with audio playback, visual proof generation, and emergency message simulation.

**[Live Demo →](https://your-app.streamlit.app)** *(replace with your URL)*

---

## ✨ Features

| Feature | What it does |
|---|---|
| 🎲 Excuse Generator | Pick category, situation & urgency → get a believable excuse instantly |
| 🖼️ Proof Generator | Generate a fake hospital cert, WhatsApp chat, or location log as an image |
| 🚨 Emergency Simulator | Simulate an urgent message from Mom, Boss, Doctor, etc. |
| 🔊 Audio Playback | Hear your excuse read aloud via text-to-speech |
| 🌍 Multi-language | Output in English, Hindi, Tamil, Telugu, or Spanish |
| ⭐ Favourites | Save and revisit your best excuses |

---

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API keys** — create a `.env` file:
```
OPENROUTER_API_KEY=sk-or-your-key-here
STABILITY_API_KEY=sk-your-key-here
```

**4. Run**
```bash
streamlit run app.py
```

---

## ☁️ Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select your repo
3. Add your keys under **Settings → Secrets**:

```toml
OPENROUTER_API_KEY = "sk-or-..."
STABILITY_API_KEY  = "sk-..."
```

4. Click **Deploy** ✅

---

## 🔑 API Keys

- **OpenRouter** (free) → [openrouter.ai](https://openrouter.ai) — powers all text generation
- **Stability AI** (optional) → [platform.stability.ai](https://platform.stability.ai) — only needed for Proof Generator

---

## 🛠️ Built With

- [Streamlit](https://streamlit.io)
- [OpenAI API](https://openrouter.ai) via OpenRouter (Mixtral 8x7B)
- [Stability AI](https://stability.ai) (SDXL)
- [gTTS](https://pypi.org/project/gTTS/) — text to speech
- [deep-translator](https://pypi.org/project/deep-translator/) — multi-language support

---

## 📁 Project Structure

```
├── app.py              # Main Streamlit app
├── flux_ai.py          # Stability AI image generator
├── requirements.txt    # Python dependencies
├── packages.txt        # System packages for Streamlit Cloud
└── .env                # API keys (local only — don't commit!)
```

---

*Built as a solo project in ~1–2 weeks. For entertainment purposes only — use responsibly! 🌿*

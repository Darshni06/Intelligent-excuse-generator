# app.py  ─  AI Excuse Generator  ✨
import streamlit as st
import os
import datetime
import urllib.parse
from io import BytesIO
from collections import Counter

from dotenv import load_dotenv
from gtts import gTTS
from deep_translator import GoogleTranslator
import openai

from flux_ai import FluxImageGenerator
from PIL import Image

# ─────────────────────────────────────────
#  ENV / SECRETS
# ─────────────────────────────────────────
load_dotenv()


def _secret(key: str) -> str:
    """Try Streamlit secrets first, then .env."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, "")


openai.api_key = _secret("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

# ─────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────
st.set_page_config(
    page_title=" Intelligent Excuse Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
#  CUSTOM CSS  ─  pastel + animated
# ─────────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Quicksand:wght@500;600;700&display=swap');

/* ── Root palette ── */
:root {
  --bg:       #fdf6ff;
  --surface:  #ffffff;
  --lavender: #c9b6f7;
  --pink:     #f7b6d2;
  --mint:     #b6f0e0;
  --peach:    #ffd6b0;
  --sky:      #b6dff7;
  --text:     #4a3560;
  --muted:    #9580b8;
  --border:   #e8d8ff;
  --shadow:   rgba(180,140,240,.18);
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* fade-in page */
.main { animation: pageIn .6s ease both; }
@keyframes pageIn {
  from { opacity:0; transform:translateY(12px); }
  to   { opacity:1; transform:translateY(0);    }
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #f0e6ff 0%, #ffe6f4 100%) !important;
    border-right: 2px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: #2a1a40 !important;
}

[data-testid="stSidebar"] .stat-pill {
    background: linear-gradient(135deg,#e8d8ff,#ffdff0) !important;
    border-radius: 40px !important;
    padding: .55rem 1.1rem !important;
    text-align: center !important;
    font-weight: 700 !important;
    font-size: .88rem !important;
    color: #2a1a40 !important;
    border: 1.5px solid var(--border) !important;
    white-space: nowrap !important;
}

/* ── Hero Banner ── */
.hero {
    background: linear-gradient(135deg,
        #f5e6ff 0%, #fce4f4 30%, #ffe8d6 60%, #e4f4ff 100%);
    background-size: 400% 400%;
    animation: gradShift 8s ease infinite;
    border-radius: 24px;
    padding: 2.4rem 2rem 2rem;
    text-align: center;
    margin-bottom: 1.6rem;
    box-shadow: 0 8px 32px var(--shadow);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(circle at 70% 30%,
        rgba(255,255,255,.55) 0%, transparent 60%);
    pointer-events: none;
}
@keyframes gradShift {
  0%,100% { background-position: 0% 50%; }
  50%      { background-position: 100% 50%; }
}
.hero h1 {
    font-family: 'Quicksand', sans-serif !important;
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    color: #6b3fa0 !important;
    margin-bottom: .3rem !important;
    animation: popIn .7s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes popIn {
  from { opacity:0; transform:scale(.85); }
  to   { opacity:1; transform:scale(1);   }
}
.hero p {
    color: #8a60bb !important;
    font-size: 1.05rem;
    font-weight: 600;
    margin: 0 !important;
}
.hero .badges {
    display:flex; gap:.5rem; justify-content:center;
    flex-wrap:wrap; margin-top:.9rem;
}
.badge {
    background: rgba(255,255,255,.7);
    border: 1.5px solid rgba(200,160,255,.5);
    border-radius: 30px;
    padding: .22rem .85rem;
    font-size: .82rem;
    font-weight: 700;
    color: #7044a8;
    backdrop-filter: blur(6px);
    animation: floatBadge 3s ease-in-out infinite;
}
.badge:nth-child(2) { animation-delay:.4s; }
.badge:nth-child(3) { animation-delay:.8s; }
@keyframes floatBadge {
  0%,100% { transform:translateY(0); }
  50%     { transform:translateY(-4px); }
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    margin: .9rem 0;
    box-shadow: 0 4px 18px var(--shadow);
    animation: slideUp .5s ease both;
    transition: transform .25s, box-shadow .25s;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 32px var(--shadow);
}
@keyframes slideUp {
  from { opacity:0; transform:translateY(18px); }
  to   { opacity:1; transform:translateY(0);    }
}

/* colour-coded result card */
.result-card {
    background: linear-gradient(135deg, #f9f0ff, #fff0f8);
    border-left: 5px solid var(--lavender);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin: .8rem 0;
    font-size: 1.05rem;
    line-height: 1.7;
    color: var(--text);
    animation: slideUp .4s ease both;
}

/* ── Stat pill ── */
.stat-pill {
    background: linear-gradient(135deg,#e8d8ff,#ffdff0);
    border-radius: 40px;
    padding: .55rem 1.1rem;
    text-align:center;
    font-weight: 700;
    font-size: .88rem;
    color: var(--text);
    border: 1.5px solid var(--border);
    transition: transform .2s;
}
.stat-pill:hover { transform:scale(1.05); }

/* ── Tip box ── */
.tip-box {
    background: linear-gradient(135deg,#fff7d6,#ffecd6);
    border-left: 4px solid #ffb347;
    border-radius: 12px;
    padding: .9rem 1.2rem;
    font-size: .92rem;
    color: #7a5000;
    font-weight: 600;
    margin: .6rem 0;
}

/* ── Section heading ── */
.section-title {
    font-family: 'Quicksand', sans-serif;
    font-weight: 700;
    font-size: 1.3rem;
    color: #6b3fa0;
    margin: 1.2rem 0 .5rem;
    display: flex;
    align-items: center;
    gap: .4rem;
}

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: #f3e8ff !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: none !important;
}
[data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-family: 'Nunito', sans-serif !important;
    color: var(--muted) !important;
    padding: .5rem 1rem !important;
    transition: all .2s !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: white !important;
    color: #6b3fa0 !important;
    box-shadow: 0 2px 10px var(--shadow) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #d4aaff, #f9aad4, #aadff9) !important;
    background-size: 300% 300% !important;
    animation: btnShimmer 5s ease infinite !important;
    border: none !important;
    border-radius: 14px !important;
    color: #3d1f6a !important;
    font-weight: 700 !important;
    font-family: 'Nunito', sans-serif !important;
    padding: .65rem 1.2rem !important;
    transition: transform .2s, box-shadow .2s !important;
    box-shadow: 0 4px 15px var(--shadow) !important;
}
@keyframes btnShimmer {
  0%,100% { background-position: 0% 50%; }
  50%      { background-position: 100% 50%; }
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 8px 24px var(--shadow) !important;
}
.stButton > button:active { transform:scale(.96) !important; }

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    border-radius: 12px !important;
    border: 1.5px solid var(--border) !important;
    background: #fdf8ff !important;
    color: var(--text) !important;
    font-family: 'Nunito', sans-serif !important;
    transition: border-color .2s, box-shadow .2s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--lavender) !important;
    box-shadow: 0 0 0 3px rgba(200,160,255,.25) !important;
}

/* ── Selectbox ── */
[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 1.5px solid var(--border) !important;
    background: #fdf8ff !important;
    font-family: 'Nunito', sans-serif !important;
}
[data-baseweb="select"] span,
[data-baseweb="select"] div,
[data-baseweb="select"] input,
[data-baseweb="option"] {
    color: #2a1a40 !important;
}
/* dropdown option list */
[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
[role="option"] {
    color: #2a1a40 !important;
    background: #fdf8ff !important;
}
[role="option"]:hover {
    background: #ece0ff !important;
}

/* ── Success / Info / Warning ── */
.stSuccess {
    background: linear-gradient(135deg,#d4f5e9,#e8fdf5) !important;
    border-radius: 12px !important;
}
.stInfo {
    background: linear-gradient(135deg,#e8f0ff,#f0e8ff) !important;
    border-radius: 12px !important;
}

/* ── Footer ── */
.footer {
    text-align:center;
    padding: 1.5rem 0 .5rem;
    color: var(--muted);
    font-size: .88rem;
    font-weight: 600;
}
.footer span { color: #c9b6f7; }

/* ── Divider ── */
hr { border-color: var(--border) !important; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────
for key, default in [
    ("excuse_history", []),
    ("favorites", []),
    ("total_generated", 0),
    ("last_excuse", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────
FAV_FILE = "favorites.txt"
LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Spanish": "es",
}

# ─────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────

def load_favorites() -> list:
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, "r", encoding="utf-8") as f:
                return [l.strip() for l in f if l.strip()]
        except Exception:
            pass
    return []


def save_favorite_to_file(excuse: str) -> bool:
    try:
        if excuse not in load_favorites():
            with open(FAV_FILE, "a", encoding="utf-8") as f:
                f.write(excuse + "\n")
            return True
    except Exception:
        pass
    return False


def call_openai(prompt: str, max_tokens: int = 300, temperature: float = 0.7) -> str:
    if not openai.api_key:
        return "❌ OPENROUTER_API_KEY is missing. Add it to Streamlit secrets."
    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mixtral-8x7b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            headers={
                "HTTP-Referer": "https://excuse-generator.streamlit.app",
                "X-Title": "Intelligent Excuse Generator",
            },
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        return f"❌ API error: {exc}"


def translate_text(text: str, lang: str) -> str:
    if lang == "English" or not text or text.startswith("❌"):
        return text
    try:
        return GoogleTranslator(
            source="auto", target=LANGUAGE_CODES[lang]
        ).translate(text)
    except Exception as exc:
        st.warning(f"Translation skipped: {exc}")
        return text


def ai_rank_excuse(excuse_text: str) -> str:
    prompt = (
        f'Evaluate this excuse for believability:\n\n"{excuse_text}"\n\n'
        "Respond with ONLY one of these:\n"
        "🟢 Highly Believable\n"
        "🟡 Somewhat Believable\n"
        "🔴 Less Believable"
    )
    result = call_openai(prompt, max_tokens=20, temperature=0.3)
    return result if not result.startswith("❌") else "🟡 Somewhat Believable"


def speak_text(text: str, lang_code: str) -> None:
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        buf = BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        st.audio(buf.read(), format="audio/mp3")
    except Exception as exc:
        st.warning(f"Audio generation failed: {exc}")


def generate_excuse(category: str, scenario: str, urgency: str) -> str:
    prompt = (
        f"Write a realistic and believable excuse for someone dealing with '{scenario}' "
        f"related to {category}, with {urgency} urgency. "
        "Write it as a natural paragraph (2-4 sentences) that someone would actually say. "
        "Make it sound genuine and conversational. Do not use bullet points or lists."
    )
    return call_openai(prompt, max_tokens=300)


def simulate_emergency(relation: str, context: str) -> tuple:
    prompt = (
        f"Generate a realistic urgent text message from {relation} about a {context}. "
        "Keep it under 25 words and make it sound genuinely urgent. "
        "Only return the message text, nothing else."
    )
    sms = call_openai(prompt, max_tokens=60, temperature=0.7)
    return f"📞 Incoming Call: {relation}", f"📬 {sms}"


def generate_apology(tone: str, context: str) -> str:
    prompt = (
        f"Write a {tone.lower()} apology message for missing a {context.lower()} obligation. "
        "Make it sincere and appropriate. Keep it 2-3 sentences."
    )
    return call_openai(prompt, max_tokens=200)


def craft_image_prompt(proof_type: str, name: str, reason: str) -> str:
    note = "High quality, realistic, professional. All text clearly readable in English."
    prompts = {
        "Hospital Certificate": (
            f"Professional medical certificate, hospital letterhead, "
            f"patient name '{name}', diagnosis '{reason}', doctor signature, "
            f"hospital stamp, current date. Realistic official document layout. {note}"
        ),
        "WhatsApp Chat": (
            f"WhatsApp conversation screenshot. Boss: 'Why aren't you at work today?' "
            f"Reply from {name}: 'Sorry sir, {reason}. Will send certificate.' "
            f"Realistic WhatsApp UI, timestamps, green bubbles. {note}"
        ),
        "Location Log": (
            f"Google Maps timeline screenshot. User {name} at hospital due to {reason}. "
            f"Red location pin, route, timestamp, realistic phone UI. {note}"
        ),
    }
    return prompts.get(proof_type, f"Realistic {proof_type} document. {note}")


def smart_suggestion() -> str:
    h = datetime.datetime.now().hour
    wd = datetime.datetime.now().weekday()
    if wd >= 5:
        return "🏥 Health emergency"
    if 6 <= h < 9:
        return "🚗 Traffic delay"
    if 9 <= h < 12:
        return "💼 Urgent meeting called"
    if 12 <= h < 15:
        return "🩺 Doctor appointment"
    if 15 <= h < 18:
        return "👨‍👩‍👧 Family responsibility"
    return "⚡ Technical issues"


# ─────────────────────────────────────────
#  LOAD SAVED FAVORITES ON FIRST RUN
# ─────────────────────────────────────────
if not st.session_state.favorites:
    st.session_state.favorites.extend(load_favorites())

# ─────────────────────────────────────────
#  HERO BANNER
# ─────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🤖 Intelligent Excuse Generator</h1>
  <p>Craft believable excuses, visual proof &amp; emergency messages in seconds</p>
  <div class="badges">
    <span class="badge">✨ AI-Powered</span>
    <span class="badge">🌍 Multi-language</span>
    <span class="badge">🔊 Voice Ready</span>
    <span class="badge">🖼️ Proof Generator</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    category = st.selectbox(
        "📂 Category",
        ["Work", "School", "Health", "Family", "Transport", "Technology", "Weather"],
    )
    scenario = st.selectbox(
        "🎯 Situation",
        [
            "Late to Class", "Missed a Deadline", "Didn't Attend a Meeting",
            "Family Emergency", "Health Issue", "Can't Make It", "Need Extension",
        ],
    )
    urgency = st.selectbox("⚠️ Urgency", ["Low", "Medium", "High"])
    language = st.selectbox(
        "🗣️ Language", ["English", "Hindi", "Tamil", "Telugu", "Spanish"]
    )
    auto_save = st.checkbox("📌 Auto-save to favorites")

    st.markdown("---")
    st.markdown("### 📊 Session Stats")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(
            f'<div class="stat-pill">🎲 {st.session_state.total_generated}<br>'
            '<small>Generated</small></div>',
            unsafe_allow_html=True,
        )
    with col_s2:
        st.markdown(
            f'<div class="stat-pill">⭐ {len(st.session_state.favorites)}<br>'
            '<small>Favorites</small></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="tip-box">💡 <b>Smart Suggestion</b><br>{smart_suggestion()}</div>',
        unsafe_allow_html=True,
    )

    # API status indicator
    st.markdown("---")
    st.markdown("### 🔑 API Status")
    ok_color = "#52c41a" if openai.api_key else "#ff4d4f"
    ok_label = "✅ Connected" if openai.api_key else "❌ Missing key"
    st.markdown(
        f'<div style="color:{ok_color};font-weight:700;font-size:.9rem;">'
        f"OpenRouter: {ok_label}</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────
#  MAIN TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["🎲 Generate Excuse", "🖼️ Proof Generator", "🚨 Emergency Simulator", "📜 History & Favs"]
)

# ══════════════════════════════════════════
#  TAB 1 – Generate Excuse
# ══════════════════════════════════════════
with tab1:
    col_gen, col_tip = st.columns([3, 1])

    with col_gen:
        st.markdown('<div class="section-title">🎲 Generate Your Excuse</div>', unsafe_allow_html=True)

        if st.button("✨ Generate Excuse", use_container_width=True):
            if not openai.api_key:
                st.error("❌ OPENROUTER_API_KEY is missing. See the Setup Guide below.")
            else:
                with st.spinner("🤖 Crafting your perfect excuse..."):
                    raw = generate_excuse(category, scenario, urgency)

                if raw.startswith("❌"):
                    st.error(raw)
                else:
                    translated = translate_text(raw, language)
                    st.session_state.last_excuse = translated

                    if translated not in st.session_state.excuse_history:
                        st.session_state.excuse_history.append(translated)
                    st.session_state.total_generated += 1

                    st.success("✅ Excuse ready!")
                    st.markdown(
                        f'<div class="result-card">📝 {translated}</div>',
                        unsafe_allow_html=True,
                    )

                    # Believability rank
                    with st.spinner("Checking believability..."):
                        ranking = ai_rank_excuse(translated)
                    st.markdown(f"**📊 Believability:** {ranking}")

                    if auto_save and translated not in st.session_state.favorites:
                        st.session_state.favorites.append(translated)
                        save_favorite_to_file(translated)
                        st.success("⭐ Auto-saved to favorites!")

                    # Audio
                    st.markdown('<div class="section-title">🔊 Listen</div>', unsafe_allow_html=True)
                    speak_text(translated, LANGUAGE_CODES[language])

                    # Share options
                    st.markdown('<div class="section-title">📤 Share</div>', unsafe_allow_html=True)
                    sh1, sh2, sh3 = st.columns(3)
                    with sh1:
                        wa_url = f"https://wa.me/?text={urllib.parse.quote(translated)}"
                        st.markdown(
                            f'<a href="{wa_url}" target="_blank" style="'
                            "display:block;text-align:center;background:linear-gradient(135deg,#d4ffdf,#b6f5c8);"
                            "border-radius:12px;padding:.55rem;font-weight:700;color:#1a6b3a;text-decoration:none;"
                            'border:1.5px solid #a0e0b0;">📱 WhatsApp</a>',
                            unsafe_allow_html=True,
                        )
                    with sh2:
                        st.download_button(
                            "📥 Download .txt",
                            translated,
                            file_name="excuse.txt",
                            mime="text/plain",
                            use_container_width=True,
                        )
                    with sh3:
                        if st.button("⭐ Save Favorite", use_container_width=True):
                            if translated not in st.session_state.favorites:
                                st.session_state.favorites.append(translated)
                                save_favorite_to_file(translated)
                                st.success("Saved!")
                            else:
                                st.info("Already in favorites!")

                    # Email template
                    st.markdown('<div class="section-title">📧 Email Template</div>', unsafe_allow_html=True)
                    email = (
                        "Subject: Regarding My Absence/Delay\n\n"
                        "Dear Sir/Madam,\n\n"
                        f"{translated}\n\n"
                        "I apologize for any inconvenience caused and appreciate your understanding.\n\n"
                        "Best regards,\n[Your Name]"
                    )
                    st.code(email, language="text")

    with col_tip:
        st.markdown('<div class="section-title">💡 Tips</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card" style="font-size:.9rem; color:#2a1a40;">'
            "🎯 <b>High urgency</b> excuses sound more convincing with health-related scenarios.<br><br>"
            "🌍 Use language matching your recipient for extra authenticity.<br><br>"
            "📞 Pair your excuse with an Emergency Simulator message!"
            "</div>",
            unsafe_allow_html=True,
            
        )

    # ── Apology sub-section ──────────────
    st.markdown("---")
    st.markdown('<div class="section-title">😔 Generate Apology Message</div>', unsafe_allow_html=True)

    ap1, ap2, ap3 = st.columns([2, 2, 1])
    with ap1:
        apology_tone = st.selectbox("Tone", ["Formal", "Emotional", "Casual"], key="ap_tone")
    with ap2:
        apology_ctx = st.selectbox(
            "Context", ["Work", "School", "Family", "Friend"], key="ap_ctx"
        )
    with ap3:
        st.write("")
        st.write("")
        gen_apol = st.button("🙏 Generate", use_container_width=True, key="gen_apol")

    if gen_apol:
        with st.spinner("Writing apology..."):
            apology = generate_apology(apology_tone, apology_ctx)
        if apology.startswith("❌"):
            st.error(apology)
        else:
            st.markdown(
                f'<div class="result-card" style="border-left-color:#f9aad4;">💌 {apology}</div>',
                unsafe_allow_html=True,
            )
            speak_text(apology, LANGUAGE_CODES[language])

# ══════════════════════════════════════════
#  TAB 2 – Proof Generator
# ══════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🖼️ Visual Proof Generator</div>', unsafe_allow_html=True)
    pr1, pr2 = st.columns(2)
    with pr1:
        proof_type = st.selectbox(
            "📄 Proof Type", ["Hospital Certificate", "WhatsApp Chat", "Location Log"]
        )
        proof_name = st.text_input("👤 Your Name", placeholder="e.g. Priya Sharma")
    with pr2:
        proof_reason = st.text_input(
            "📝 Reason / Diagnosis", placeholder="e.g. viral fever"
        )

    if st.button("🎨 Generate Visual Proof", use_container_width=True):
        if not proof_name.strip() or not proof_reason.strip():
            st.warning("⚠️ Please fill in both Name and Reason.")
        else:
            prompt = craft_image_prompt(proof_type, proof_name.strip(), proof_reason.strip())
            with st.spinner("🎨 Generating image — this may take ~30 seconds..."):
                try:
                    flux = FluxImageGenerator()
                    image = flux.generate_image(prompt, width=1024, height=1024)

                    buf = BytesIO()
                    image.save(buf, format="PNG")
                    buf.seek(0)

                    st.success("✅ Image generated!")
                    st.image(buf, caption=proof_type, use_container_width=True)
                    buf.seek(0)
                    st.download_button(
                        "📥 Download Proof Image",
                        buf,
                        file_name=f"{proof_type.lower().replace(' ','_')}_proof.png",
                        mime="image/png",
                        use_container_width=True,
                    )
                except ValueError as exc:
                    st.error(str(exc))
                    st.info("Add STABILITY_API_KEY to your Streamlit secrets to use this feature.")
                except Exception as exc:
                    st.error(f"❌ Image generation failed: {exc}")

# ══════════════════════════════════════════
#  TAB 3 – Emergency Simulator
# ══════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">🚨 Emergency Message Simulator</div>', unsafe_allow_html=True)
    st.markdown("Generate realistic urgent messages from contacts to support your excuse.")

    em1, em2 = st.columns(2)
    with em1:
        relation = st.selectbox(
            "👥 Who is contacting you?",
            ["Mom", "Dad", "Doctor", "College Office", "Spouse", "Friend", "Boss"],
        )
    with em2:
        em_context = st.selectbox(
            "⚠️ Emergency Type",
            ["medical emergency", "accident", "family issue", "urgent meeting", "college notice"],
        )

    if st.button("📞 Generate Emergency Message", use_container_width=True):
        with st.spinner("Creating urgent message..."):
            call_msg, sms_msg = simulate_emergency(relation, em_context)

        st.markdown(
            f'<div class="result-card" style="border-left-color:#f7b6d2;background:linear-gradient(135deg,#fff0f8,#fff8f0);">'
            f"<b>{call_msg}</b></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="result-card" style="border-left-color:#b6dff7;">{sms_msg}</div>',
            unsafe_allow_html=True,
        )

        clean_sms = sms_msg.replace("📬 ", "")
        if not clean_sms.startswith("❌"):
            speak_text(clean_sms, LANGUAGE_CODES[language])

# ══════════════════════════════════════════
#  TAB 4 – History & Favorites
# ══════════════════════════════════════════
with tab4:
    h_col, f_col = st.columns(2)

    with h_col:
        st.markdown('<div class="section-title">📜 Excuse History</div>', unsafe_allow_html=True)

        if st.session_state.excuse_history:
            for i, exc in enumerate(reversed(st.session_state.excuse_history), 1):
                with st.expander(f"Excuse #{i} — {exc[:45]}..."):
                    st.write(exc)
                    if st.button(f"⭐ Save", key=f"sh_{i}"):
                        if exc not in st.session_state.favorites:
                            st.session_state.favorites.append(exc)
                            save_favorite_to_file(exc)
                            st.success("Saved!")
            st.download_button(
                "⬇️ Download All History",
                "\n\n---\n\n".join(st.session_state.excuse_history),
                "excuse_history.txt",
                use_container_width=True,
            )
            if st.button("🧹 Clear History", use_container_width=True):
                st.session_state.excuse_history.clear()
                st.success("Cleared!")
                st.rerun()
        else:
            st.info("No excuses yet — generate some from Tab 1!")

    with f_col:
        st.markdown('<div class="section-title">⭐ Favorites</div>', unsafe_allow_html=True)

        if st.session_state.favorites:
            for i, fav in enumerate(reversed(st.session_state.favorites), 1):
                with st.expander(f"Fav #{i} — {fav[:45]}..."):
                    st.write(fav)

            if len(st.session_state.favorites) > 1:
                st.markdown("**🏆 Most Saved**")
                for rank, (exc, cnt) in enumerate(
                    Counter(st.session_state.favorites).most_common(3), 1
                ):
                    st.markdown(f"**{rank}.** {exc[:55]}…")

            if st.button("🗑️ Clear Favorites", use_container_width=True):
                st.session_state.favorites.clear()
                if os.path.exists(FAV_FILE):
                    os.remove(FAV_FILE)
                st.success("Cleared!")
                st.rerun()
        else:
            st.info("Tick 'Auto-save' in Settings or hit ⭐ on any excuse!")



# ─────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div class="footer">🤖 Intelligent Excuse Generator &nbsp;·&nbsp; '
    'Built with <span>♥</span> using Streamlit &nbsp;·&nbsp; '
    "Use responsibly 🌿</div>",
    unsafe_allow_html=True,
)

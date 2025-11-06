# app.py
from __future__ import annotations
import os
import time
import types
import streamlit as st
from dotenv import load_dotenv
from typing import List, Dict

# ---------- Environment Setup ----------
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
if API_KEY:
    os.environ["GROQ_API_KEY"] = API_KEY

# ---------- Styles ----------
STYLE_THERAPIST_CONCISE = """\
- Empathetic, precise, ≤80 words.
- Ask ≤2 clarifying questions.
- No medicines or prescriptions.
- End with one brief question.
"""

STYLE_SEGMENTED = """\
RESPONSE STYLE — SEGMENTED EXPLAINER (STRICT)
- Use up to 4 sections: TL;DR, Key Points, Steps, Next Actions.
- Max 180 words total.
- Each bullet ≤14 words.
- One small Markdown table if needed.
- End: “Want me to expand any section?”.
"""

# ---------- Page Config ----------
st.set_page_config(
    page_title="Chat Therapy",
    page_icon="assets/favicon.png",
    initial_sidebar_state="collapsed"
)

with st.sidebar:
    st.header("⚙️ Debug Info")
    st.write("**API Key Loaded:**", bool(API_KEY))
    st.write("**Mode:**")
    mode = st.radio("Choose reply style:", ["Therapist (concise)", "Segmented explainer"])

    if st.button("🆕 New Chat"):
        st.session_state.clear()
        st.rerun()

# ---------- Safety Check ----------
if not API_KEY:
    st.error("⚠️ GROQ_API_KEY not found. Add it to .env or Streamlit Secrets.")
    st.stop()

# ---------- Import Agent ----------
from agent import get_response  # noqa: E402

# ---------- Helpers ----------
def stream_text(s: str, delay: float = 0.02):
    for w in s.split():
        yield w + " "
        time.sleep(delay)

def is_stream_like(obj) -> bool:
    return isinstance(obj, types.GeneratorType)

def build_context(history: List[Dict[str, str]], limit=8):
    return [{"role": m["role"], "content": m["content"]} for m in history[-limit:]]

def show_crisis_banner(text: str):
    if any(k in text.lower() for k in ["suicide", "self-harm", "kill myself", "hurt myself"]):
        st.info(
            "If you're in danger or considering self-harm, please call 988 (U.S.) or your local emergency services immediately.",
            icon="🆘"
        )

def choose_avatar(reply: str) -> str:
    """Return the appropriate avatar depending on assistant response."""
    t = reply.lower()
    if any(x in t for x in ["outside my scope", "cannot assist", "not in my scope", "out of scope"]):
        return "assets/red.png"       # 🔴 Out-of-scope
    if any(x in t for x in ["steps", "solution", "try this", "plan", "follow these"]):
        return "assets/green.png"     # 🟢 Solution
    return "assets/favicon.png"       # 🟣 Therapist / default

# ---------- Initialize ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Header ----------
st.markdown(
    """
    <div style='text-align:center;'>
      <img src='assets/favicon.png' width='70' style='border-radius:50%; margin-bottom:8px;'>
      <h1>Chat Therapy</h1>
      <p style='color:gray;'>Your calm space to talk things through 🌿</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- Render Chat History ----------
for m in st.session_state.messages:
    avatar = choose_avatar(m["content"]) if m["role"] == "assistant" else None
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])

# ---------- Input ----------
if prompt := st.chat_input("What’s on your mind?"):
    show_crisis_banner(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    try:
        system_style = STYLE_SEGMENTED if mode == "Segmented explainer" else STYLE_THERAPIST_CONCISE
        context = build_context(st.session_state.messages)

        if mode == "Therapist (concise)":
            # Non-stream to enforce sanitization & word limit
            response = get_response(
                messages=context,
                system_override="Follow these rules:\n" + system_style.strip(),
                stream=False,
                temperature=0.2,
                enforce_format=True
            )
            full_text = str(response)
        else:
            # Stream for segmented mode
            response = get_response(
                messages=context,
                system_override="Follow these rules:\n" + system_style.strip(),
                stream=True,
                temperature=0.4
            )
            if is_stream_like(response):
                full_text = st.write_stream(response)
            else:
                full_text = st.write_stream(stream_text(str(response)))

    except Exception as e:
        st.error(f"Error: {e}")
        full_text = f"[Error] {e}"

    # Choose avatar AFTER full response is ready
    avatar_path = choose_avatar(full_text)

    with st.chat_message("assistant", avatar=avatar_path):
        st.markdown(full_text)

    # Save message
    st.session_state.messages.append({"role": "assistant", "content": full_text})

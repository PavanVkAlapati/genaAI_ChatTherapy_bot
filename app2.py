from __future__ import annotations
import os, re, time, html, base64
from typing import List, Dict
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
from datetime import datetime

# ================== ENV / PAGE ==================
load_dotenv()
st.set_page_config(
    page_title="Chat Therapy",
    page_icon="assets/favicon.png",
    initial_sidebar_state="collapsed",
    layout="wide"
)

from agent import get_response  # Groq streaming wrapper

# ================== UI ASSETS ==================
USER_AVATAR_PATH = "assets/user.png"
ASSIST_BOT       = "assets/bot.png"
ASSIST_GREEN     = "assets/green.png"
ASSIST_RED       = "assets/red.png"

def img_to_data_uri(path: str) -> str:
    """Embed local png/jpg in HTML reliably."""
    if not os.path.exists(path):
        return ""
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "png" if ext == "png" else "jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{mime};base64,{b64}"

USER_AVATAR_URI = img_to_data_uri(USER_AVATAR_PATH)

# ================== THEME + CHAT CSS ==================
st.markdown(
    """
    <style>
    :root{
        --glass-bg: rgba(10, 18, 40, 0.55);
        --glass-border: rgba(160, 200, 255, 0.25);
        --user-bg: rgba(0, 220, 255, 0.12);
        --user-border: rgba(0, 220, 255, 0.60);
        --user-glow: 0 0 28px rgba(0, 220, 255, 0.35);
        --sidebar-bg: radial-gradient(circle at top left, #020617 0%, #020617 45%, #050b1f 100%);
        --cyan: rgba(0,220,255,1);
    }

    /* ===== SIDEBAR THEME ===== */
    [data-testid="stSidebar"]{
        background: var(--sidebar-bg) !important;
        border-right: 1px solid rgba(140,180,255,0.12);
        color: #EAF2FF !important;
    }
    [data-testid="stSidebar"] *{
        color: #EAF2FF !important;
    }
    [data-testid="stSidebar"] hr{
        border-color: rgba(140,180,255,0.16) !important;
    }
    [data-testid="stSidebar"] button{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(150,190,255,0.20) !important;
        border-radius: 14px !important;
        color: #EAF2FF !important;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03);
    }
    [data-testid="stSidebar"] button:hover{
        border-color: rgba(0,220,255,0.55) !important;
        box-shadow: 0 0 16px rgba(0,220,255,0.22);
    }

    /* ===== REMOVE STREAMLIT DEFAULT CHAT INPUT GRADIENT ===== */
    section[data-testid="stChatInput"],
    div[data-testid="stChatInputContainer"]{
        background: transparent !important;
        border-top: 1px solid rgba(0,220,255,0.55) !important;  /* cyan divider */
        box-shadow: 0 -8px 30px rgba(0,220,255,0.08) !important;
        padding-top: 0.25rem !important;
    }
    section[data-testid="stChatInput"] > div{
        border-top: none !important;
        box-shadow: none !important;
    }

    /* ===== CHAT INPUT THEME ===== */
    section[data-testid="stChatInput"] textarea{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(0,220,255,0.45) !important;
        border-radius: 999px !important;
        padding: 12px 18px !important;
        color: #EAF2FF !important;
        outline: none !important;
        box-shadow: none !important;
    }
    section[data-testid="stChatInput"] textarea::placeholder{
        color: rgba(234,242,255,0.55) !important;
    }

    /* ===== REMOVE STREAMLIT DEFAULT CHAT BUBBLES ===== */
    [data-testid="stChatMessage"],
    [data-testid="stChatMessageContent"]{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    [data-testid="stChatMessageContent"]{
        padding: 0 !important;
        margin: 0 !important;
        width: auto !important;
        max-width: none !important;
    }
    [data-testid="stChatMessage"]{
        gap: 10px !important;
        align-items: flex-start !important;
        padding-top: 4px !important;
        padding-bottom: 4px !important;
    }

    /* ===== CUSTOM BUBBLES ===== */
    .bubble-wrap{
        display:flex;
        width:100%;
        margin: 6px 0;
    }
    .bubble{
        padding: 12px 14px;
        border-radius: 18px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        font-size: 15px;
        line-height: 1.45;
        white-space: pre-wrap;
        word-break: break-word;
    }

    /* assistant bubble (left glass card) */
    .bubble.bot{
        max-width: 72%;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        color: #EAF2FF;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04);
    }
    .bubble-wrap.bot{ justify-content:flex-start; }

    /* user pill (right small glow) */
    .bubble.user{
        max-width: 45%;
        background: var(--user-bg);
        border: 1px solid var(--user-border);
        color: #EAFBFF;
        border-radius: 999px;
        padding: 10px 16px;
        box-shadow: var(--user-glow);
    }

    /* user ROW with avatar on right */
    .user-row{
        width:100%;
        display:flex;
        justify-content:flex-end;
        align-items:center;
        gap:10px;
        margin: 6px 0;
    }
    .user-avatar{
        width:34px; height:34px;
        border-radius:50%;
        object-fit:cover;
        box-shadow: 0 0 10px rgba(0,220,255,0.25);
    }

    /* ===== KILL ORANGE FOCUS RING EVERYWHERE, FORCE CYAN ===== */
    .stApp *:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    textarea:focus,
    textarea:focus-visible,
    input:focus,
    input:focus-visible,
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    div[data-baseweb="input"] input:focus,
    div[data-baseweb="textarea"] textarea:focus,
    section[data-testid="stChatInput"]:focus-within textarea {
        outline: none !important;
        border-color: rgba(0,220,255,0.95) !important;
        box-shadow:
            0 0 0 2px rgba(0,220,255,0.25),
            0 0 18px rgba(0,220,255,0.35) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== HELPERS ==================
def show_crisis_banner(text: str):
    t = (text or "").lower()
    if any(k in t for k in ["suicide", "self-harm", "kill myself", "hurt myself"]):
        st.info(
            "If you're in danger or considering self-harm, call 988 (U.S.) or local emergency services."
        )

_TAG_RE = re.compile(r"<[^>]+>")
def strip_html(text: str) -> str:
    if not text:
        return ""
    text = _TAG_RE.sub("", text)
    text = html.unescape(text)
    return text.strip()

def build_full_prompt(history: List[Dict[str, str]], latest: str, mode: str, max_turns: int = 24) -> str:
    pruned = [m for m in history if m["role"] in ("user","assistant")]
    if len(pruned) > max_turns:
        pruned = pruned[-max_turns:]

    lines = []
    for m in pruned:
        role = "User" if m["role"] == "user" else "Assistant"
        content = strip_html(m.get("content", ""))
        if content:
            lines.append(f"{role}: {content}")

    history_text = "\n".join(lines) if lines else "(none)"
    latest_clean = strip_html(latest)

    style_rule = (
        "Empathetic, precise, non-clinical. No medications. Stay in mental-wellbeing scope. "
        "Keep answers ≤80 words; 2–5 short bullets when useful; ≤2 clarifying questions."
        if mode == "Therapist (concise)"
        else
        "When explaining, use up to 4 sections: TL;DR, Key Points, Steps, Next Actions. "
        "Keep ≤180 words total. Each bullet ≤14 words."
    )

    return (
        "System: You are Mr.TomBot, a supportive therapist-style AI.\n"
        f"Style rules: {style_rule}\n\n"
        f"Previous conversation:\n{history_text}\n\n"
        f"Latest query:\n{latest_clean}"
    )

def is_refusal_or_restriction(text: str) -> bool:
    if not text:
        return True
    t = text.lower()
    refusal_phrases = [
        "i can't", "i cannot", "i can’t", "i'm not able to",
        "out of scope", "outside my scope", "not allowed",
        "can't help with that", "cannot help with that",
        "i’m sorry, but", "i'm sorry, but",
        "as an ai", "not a substitute for",
        "seek professional help",
        "i can only talk about therapy", "let’s focus on therapy",
        "policy", "restriction", "decline to answer"
    ]
    return any(p in t for p in refusal_phrases)

def is_probe_reply(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    q_marks = text.count("?")
    probing_markers = [
        "can you tell me", "how are you feeling",
        "tell me more", "help me understand",
        "what do you think", "how does that feel"
    ]
    solution_markers = [
        "here are steps", "step 1", "plan", "checklist",
        "next actions", "recommend", "solution"
    ]
    has_probe = any(p in t for p in probing_markers)
    has_solution = any(s in t for s in solution_markers)
    return (q_marks >= 1 and (has_probe or not has_solution))

def pick_assistant_avatar(reply_text: str) -> str:
    if is_refusal_or_restriction(reply_text):
        return ASSIST_RED
    if is_probe_reply(reply_text):
        return ASSIST_BOT
    return ASSIST_GREEN

def render_bot_bubble(text: str):
    safe = html.escape(text or "")
    st.markdown(
        f"<div class='bubble-wrap bot'><div class='bubble bot'>{safe}</div></div>",
        unsafe_allow_html=True
    )

def render_user_row(text: str):
    safe = html.escape(text or "")
    avatar_html = f"<img class='user-avatar' src='{USER_AVATAR_URI}' />" if USER_AVATAR_URI else ""
    st.markdown(
        f"""
        <div class="user-row">
            <div class="bubble user">{safe}</div>
            {avatar_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------- Export helpers -----------
def export_pdf(messages: List[Dict[str, str]], title="Chat Therapy") -> bytes:
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(w=0, h=10, txt=title, ln=1)
    pdf.ln(3)
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin

    for m in messages:
        role = "You" if m["role"] == "user" else "Assistant"
        pdf.set_font("Arial", "B", 11)
        pdf.multi_cell(usable_w, 6, f"{role}:")
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(usable_w, 6, strip_html(m.get("content") or ""))
        pdf.ln(2)

    out = pdf.output(dest='S')
    return out.encode("latin-1","replace") if isinstance(out, str) else bytes(out)

def export_md(messages: List[Dict[str, str]]) -> bytes:
    lines = []
    for m in messages:
        role = "You" if m["role"] == "user" else "Assistant"
        lines.append(f"**{role}:**\n\n{strip_html(m.get('content',''))}\n")
    return ("\n---\n".join(lines)).encode("utf-8")

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("## Chat Therapy")
    st.caption("Mr.TomBot • Groq LLaMA")
    st.divider()

    mode = st.radio("Reply mode", ["Therapist (concise)", "Segmented explainer"], index=0)

    if st.button("New chat", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.divider()
    st.markdown("### Export chat")
    st.download_button(
        "Download PDF",
        data=export_pdf(st.session_state.get("messages", [])),
        file_name=f"chat_therapy_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.download_button(
        "Download Markdown",
        data=export_md(st.session_state.get("messages", [])),
        file_name=f"chat_therapy_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown",
        use_container_width=True
    )

# ================== SESSION ==================
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = []

# ================== HEADER ==================
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown(
        "<h1 style='text-align:center; margin-bottom:0;'>Chat Therapy</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:gray; margin-top:4px;'>Your calm space to talk things through</p>",
        unsafe_allow_html=True
    )

# ================== HISTORY RENDER ==================
for m in st.session_state.messages:
    if m["role"] == "user":
        render_user_row(m.get("content",""))
    else:
        avatar = m.get("avatar", ASSIST_BOT)
        with st.chat_message("assistant", avatar=avatar):
            render_bot_bubble(m.get("content",""))

# ================== INPUT / RESPONSE ==================
if prompt := st.chat_input("What’s on your mind?"):
    show_crisis_banner(prompt)

    # store + immediate user render (no lag)
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "avatar": USER_AVATAR_PATH
    })
    render_user_row(prompt)

    full_prompt = build_full_prompt(st.session_state.messages, prompt, mode)

    try:
        reply_text = get_response(full_prompt) or ""
    except Exception as e:
        reply_text = f"[Error contacting model] {e}"

    assistant_avatar = pick_assistant_avatar(reply_text)

    with st.chat_message("assistant", avatar=assistant_avatar):
        render_bot_bubble(reply_text if reply_text else "…")

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply_text if reply_text else "…",
        "avatar": assistant_avatar
    })

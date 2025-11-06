# app2.py
from __future__ import annotations
import os, re, time
from typing import List, Dict
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF

# ================== ENV / PAGE ==================
load_dotenv()
st.set_page_config(page_title="Chat Therapy",
                   page_icon="assets/favicon.png",
                   initial_sidebar_state="collapsed")

from agent import get_response  # uses your existing streaming Groq wrapper

# ================== UI HELPERS ==================
THERAPIST_ICON = "assets/favicon.png"
SOLUTION_ICON  = "assets/green.png"
OOS_ICON       = "assets/red.png"

def show_crisis_banner(text: str):
    t = (text or "").lower()
    if any(k in t for k in ["suicide", "self-harm", "kill myself", "hurt myself"]):
        st.info("If you're in danger or considering self-harm, call 988 (U.S.) or local emergency services.", icon="🆘")

def classify_avatar(text: str) -> str:
    t = (text or "").lower()
    oos = ["outside my scope","out of scope","cannot assist","i can’t assist","i can't assist",
           "i can’t help","i can't help","contact hr","report to hr","authorities",
           "legal advice","lawsuit","file a case","police report","financial advice",
           "tax advice","not able to help"]
    if any(x in t for x in oos):
        return OOS_ICON
    solution = ["steps","plan","solution","checklist","follow these","next actions",
                "here’s how","here is how","actionable","tl;dr","tldr"]
    if any(x in t for x in solution):
        return SOLUTION_ICON
    return THERAPIST_ICON

def stream_text(s: str, delay: float = 0.02):
    for part in re.split(r'(\n\n+|\n)', s):
        if part:
            yield part
            time.sleep(delay)

def build_full_prompt(history: List[Dict[str, str]], latest: str, mode: str, max_turns: int = 24) -> str:
    pruned = [m for m in history if m["role"] in ("user","assistant")]
    if len(pruned) > max_turns:
        pruned = pruned[-max_turns:]
    history_lines = [("User" if m["role"]=="user" else "Assistant") + f": {m['content']}" for m in pruned]
    history_text = "\n".join(history_lines) if history_lines else "(none)"

    if mode == "Segmented explainer":
        style_rule = ("When explaining, use up to 4 sections: TL;DR, Key Points, Steps, Next Actions. "
                      "Keep ≤180 words total. Each bullet ≤14 words. End with: 'Want me to expand any section?'.")
    else:
        style_rule = ("Empathetic, precise, non-clinical. No medications. Stay in mental-wellbeing scope. "
                      "Keep answers ≤80 words; 2–5 short bullets when useful; ≤2 clarifying questions.")

    return ( "System: You are Mr.TomBot, a supportive therapist-style AI.\n"
             f"Style rules: {style_rule}\n\n"
             f"Previous conversation:\n{history_text}\n\n"
             f"Latest query:\n{latest}" )

# ----------- Export helpers (ALWAYS return bytes) -----------
def export_pdf(messages: List[Dict[str, str]], title="Chat Therapy") -> bytes:
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_path = "assets/DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.add_font("DejaVu", "B", font_path, uni=True)
        body_font = ("DejaVu", "", 10); head_font = ("DejaVu", "B", 16); role_font = ("DejaVu", "B", 11)
        use_latin1 = False
    else:
        body_font = ("Arial", "", 10); head_font = ("Arial", "B", 16); role_font = ("Arial", "B", 11)
        use_latin1 = True

    pdf.set_title(title); pdf.set_author("Chat Therapy")
    pdf.set_font(*head_font); pdf.cell(w=0, h=10, txt=title)
    pdf.set_xy(x=pdf.l_margin, y=pdf.get_y() + 6)

    usable_w = pdf.w - pdf.l_margin - pdf.r_margin
    for m in messages:
        role = "You" if m["role"]=="user" else "Assistant"
        pdf.set_font(*role_font); pdf.multi_cell(usable_w, 6, f"{role}:", align="L")
        pdf.set_font(*body_font)
        raw = m.get("content") or ""
        safe = raw.replace("\t"," ").replace("\r","")
        if use_latin1:
            safe = safe.encode("latin-1","replace").decode("latin-1")
        pdf.multi_cell(usable_w, 6, safe, align="L")
        pdf.set_xy(x=pdf.l_margin, y=pdf.get_y()+2)

    # fpdf2: output(dest='S') returns str (latin-1) or bytes/bytearray depending on version.
    out = pdf.output(dest='S')
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    if isinstance(out, str):
        return out.encode('latin-1', 'replace')
    # fallback
    return bytes(out)

def export_md(messages: List[Dict[str, str]]) -> bytes:
    lines = []
    for m in messages:
        role = "You" if m["role"]=="user" else "Assistant"
        lines.append(f"**{role}:**\n\n{m['content']}\n")
    return ("\n---\n".join(lines)).encode("utf-8")

# ================== SIDEBAR ==================
with st.sidebar:
    st.header("⚙️ Debug")
    st.write("Python:", os.sys.executable)
    st.write("CWD:", os.getcwd())
    st.write("GROQ_API_KEY present:", bool(os.getenv("GROQ_API_KEY")))
    mode = st.radio("Reply style", ["Therapist (concise)", "Segmented explainer"], index=0)
    if st.button("🆕 New chat", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ================== SESSION ==================
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = []

# ================== HEADER ==================
st.markdown("""
<div style='text-align:center;'>
  <img src='assets/favicon.png' width='70' style='border-radius:50%; margin-bottom:8px;'>
  <h1>Chat Therapy</h1>
  <p style='color:gray;'>Your calm space to talk things through 🌿</p>
</div>
""", unsafe_allow_html=True)

# Welcome card
if not st.session_state.messages:
    st.markdown("""
    <div style="display:flex;justify-content:center;margin-top:24px;">
      <div style="max-width:720px;padding:16px;border-radius:16px;
                  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);">
        <div style="font-weight:700;font-size:18px;margin-bottom:4px;">Welcome 👋</div>
        <div>What’s on your mind today? Try: “I’m feeling overwhelmed about work.”</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# History
for m in st.session_state.messages:
    avatar = m.get("avatar") if m["role"] == "assistant" else None
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])

# Input / Response
if prompt := st.chat_input("What’s on your mind?"):
    show_crisis_banner(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    full_prompt = build_full_prompt(st.session_state.messages, prompt, mode, max_turns=24)
    try:
        reply_text = get_response(full_prompt) or "[No response]"
    except Exception as e:
        reply_text = f"[Error contacting model] {e}"

    avatar_path = classify_avatar(reply_text)
    with st.chat_message("assistant", avatar=avatar_path):
        if len(reply_text) > 500:
            st.write_stream(stream_text(reply_text))
        else:
            st.markdown(reply_text)

    st.session_state.messages.append({"role": "assistant", "content": reply_text, "avatar": avatar_path})

# ================== FOOTER: EXPORT (always uses current state) ==================
from fpdf import FPDF
from datetime import datetime
import os

def export_pdf(messages, title="Chat Therapy") -> bytes:
    """
    Pretty chat export: alternating chat cards, page numbers, unicode support.
    Returns bytes suitable for streamlit.download_button(data=...).
    """

    class ChatPDF(FPDF):
        def header(self):
            self.set_font(self.head_font_name, "B", 15)
            self.set_text_color(255) if self.dark_mode else self.set_text_color(0)
            self.cell(0, 8, title, ln=1)
            self.set_font(self.body_font_name, "", 9)
            subtitle = datetime.now().strftime("Exported %Y-%m-%d %H:%M")
            self.set_text_color(160 if self.dark_mode else 110)
            self.cell(0, 6, subtitle, ln=1)
            self.ln(2)

        def footer(self):
            self.set_y(-15)
            self.set_font(self.body_font_name, "", 9)
            self.set_text_color(150)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = ChatPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)

    # -------- THEME / FONTS --------
    pdf.dark_mode = False  # set True if you want white text on dark background
    font_path = "assets/DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.add_font("DejaVu", "B", font_path, uni=True)
        pdf.body_font_name = "DejaVu"
        pdf.head_font_name = "DejaVu"
        unicode_safe = True
    else:
        # Latin-1 fallback
        pdf.body_font_name = "Arial"
        pdf.head_font_name = "Arial"
        unicode_safe = False

    # Colors (RGB)
    bg_user = (245, 248, 255)       # light blue
    bg_assistant = (245, 245, 245)  # light gray
    text_primary = (20, 20, 20)
    text_secondary = (90, 90, 90)
    role_user = "You"
    role_assistant = "Assistant"

    # Layout
    left = 15
    right = 15
    card_pad = 2.2
    gap_y = 3
    body_size = 11
    role_size = 10

    pdf.add_page()

    def _safe(txt: str) -> str:
        if unicode_safe:
            return txt.replace("\r", "")
        # latin-1 fallback to avoid crashes
        return txt.replace("\r", "").encode("latin-1", "replace").decode("latin-1")

    def chat_card(role: str, text: str, is_user: bool):
        pdf.set_fill_color(* (bg_user if is_user else bg_assistant))
        pdf.set_draw_color(225, 225, 225)
        pdf.set_text_color(*text_primary)

        # Role header
        pdf.set_font(pdf.head_font_name, "B", role_size)
        pdf.set_xy(left, pdf.get_y())
        pdf.cell(0, 5, role, ln=1)

        # Body
        pdf.set_font(pdf.body_font_name, "", body_size)
        pdf.set_text_color(*text_primary)
        x = left
        w = pdf.w - left - right
        y = pdf.get_y()

        # Measure height with multicell to draw background box nicely
        start_x, start_y = x, y
        # create a dummy multicell to get needed height
        # FPDF doesn't directly provide height calculation; we approximate
        # by writing to an off-page position: use a transaction-like approach:
        saved_x, saved_y = pdf.get_x(), pdf.get_y()
        # write to see where it ends
        pdf.multi_cell(w, 6, _safe(text), align="L")
        end_y = pdf.get_y()
        content_h = end_y - y
        # reset cursor to start
        pdf.set_xy(saved_x, saved_y)

        # Draw filled rect as background
        pdf.set_xy(start_x - card_pad, start_y - card_pad)
        pdf.set_fill_color(*(bg_user if is_user else bg_assistant))
        pdf.set_draw_color(230, 230, 230)
        pdf.rect(start_x - card_pad, start_y - card_pad, w + 2*card_pad, content_h + 2*card_pad, style="F")

        # Now write the text for real
        pdf.set_xy(start_x, start_y)
        pdf.set_font(pdf.body_font_name, "", body_size)
        pdf.set_text_color(*text_primary)
        pdf.multi_cell(w, 6, _safe(text), align="L")

        pdf.ln(gap_y)

    # ---- Write all messages ----
    for m in messages:
        role = m.get("role", "")
        text = m.get("content", "").strip()
        if not text:
            continue
        if role == "user":
            chat_card(role_user, text, is_user=True)
        elif role == "assistant":
            chat_card(role_assistant, text, is_user=False)

    # Ensure bytes for Streamlit
    out = pdf.output(dest="S")
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    if isinstance(out, str):
        return out.encode("latin-1", "replace")
    return bytes(out)


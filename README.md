# 🧠 Chat Therapy App

The **Chat Therapy App** is an empathetic, conversational AI built with Streamlit and Groq’s LLaMA-3.3-70B model.  
It simulates guided therapeutic conversations — helping users reflect, express emotions, and document thoughts safely.

---

## 🌿 Overview

| Feature | Description |
|----------|-------------|
| **Purpose** | Guided emotional reflection & conversational journaling |
| **Engine** | `groq:llama-3.3-70b-versatile` via LangChain |
| **UI** | Streamlit with message avatars (Therapist / Reflection cues) |
| **Export Options** | Chat → PDF or Markdown transcript |
| **Data Handling** | Local sessions only (no cloud logging) |

---

## 🧩 How It Works

1. The user starts the app through `hub.py` → **Chat Therapy** tile.  
2. It loads `app3.py` (or `app2.py`) and initializes the **therapy agent** defined in `agent.py`.  
3. Each conversation is stored locally under `/sessions/` for persistence.  
4. Messages are rendered with visual cues:
   - 🟢 **Therapist / Solution** — calm, structured tone  
   - 🔴 **Boundary / Out-of-Scope** — gently declines unsafe requests  
5. Users can **export the entire chat** into:
   - PDF with consistent formatting (uses `assets/DejaVuSans.ttf`)
   - Markdown file for journaling

---

## 🗂️ Project Structure

```
the_hub/
├── app3.py            # or app2.py — main therapy app
├── agent.py           # handles Groq API and response logic
├── assets/
│   ├── green.png      # therapist avatar
│   ├── red.png        # out-of-scope avatar
│   └── DejaVuSans.ttf # PDF export font
├── sessions/          # auto-created local session storage
└── .env               # contains GROQ_API_KEY (ignored in git)
```

---

## ⚙️ Setup

1. **Clone and open the hub**
   ```bash
   git clone https://github.com/<your-username>/the_hub.git
   cd the_hub
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   Create a `.env` file in the root:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the app**
   ```bash
   streamlit run hub.py
   ```
   → Click **🧠 Chat Therapy** on the hub screen.

---

## 💾 Local Data

| Directory | Purpose |
|------------|----------|
| `/sessions/` | Stores chat history as JSON files. |
| `/assets/` | Contains avatars, fonts, and icons used in the UI. |

---

## 🧠 Model Details

- **Model:** `groq:llama-3.3-70b-versatile`
- **Framework:** LangChain message schema (`HumanMessage`, `AIMessage`)
- **Response Guardrails:**
  - No unsafe or medical advice
  - Declines prompts violating scope
  - Maintains reflective, emotionally-aware tone

---

## 📤 Export Options

At any time, users can export conversations as:

- **PDF:** Professionally formatted with timestamps and speaker roles.  
- **Markdown:** Lightweight plain-text version for journaling or reuse.

---

## 💡 Future Improvements

- [ ] Integrate mood tracking dashboard  
- [ ] Add summarization and key-insight extraction  
- [ ] Enable sentiment-based conversation branching  
- [ ] Optional end-of-session AI reflection summary  

---

## 👨‍💻 Author

**Venkata Pavan Kumar Alapati**  
🎓 M.S. Data Analytics | Clark University  
💼 AI & Data Engineer • Creator of *AIIDA* and *Stomes* projects  

---

## 📜 License

Released under the **MIT License** — free for modification and redistribution with attribution.

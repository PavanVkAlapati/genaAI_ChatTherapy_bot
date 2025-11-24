# Chat Therapy Bot  
A minimal, clean, therapy-style conversational AI built using **Streamlit** and **Groq’s LLaMA-3 models**.  
It provides an empathetic, safe-space chat experience with **PDF/Markdown export**, **crisis detection**, and **scope-guarded responses**.

---

## Features

### Therapy-Style Chat  
- Warm, concise mental-wellbeing guidance  
- Optional *Segmented Explainer* mode  
- Streaming text for long responses  

### Crisis Detection  
Highlights crisis phrases (e.g., *self-harm, suicide*)  
Shows a safety banner prompting real-world emergency help.

### Strict Scope Enforcement  
The bot blocks topics outside therapy scope:  
- Finance, legal, travel, coding  
- Medical diagnosis or prescriptions  
- Police, HR, politics, etc.

If out-of-scope → a supportive refusal + alternative wellbeing framing.

### PDF & Markdown Export  
Exports the full chat as beautifully formatted PDF or clean MD text.

### Local Session Memory  
Session stored only in memory — **no cloud logging, no files written**.

---

# Project Structure  
Matches your real folder exactly:

```
genAI_ChatTherapy_bot/
│
├── app2.py               # Main Streamlit UI
├── agent.py              # Groq model wrapper & system prompt
├── requirements.txt      # Python dependencies
├── .env                  # GROQ_API_KEY (ignored in git)
│
└── assets/               # Icons + PDF font
    ├── green.png
    ├── red.png
    ├── favicon.png
    └── DejaVuSans.ttf
```

---

# Installation

### **1. Create venv (recommended)**
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### **2. Install requirements**
```bash
pip install -r requirements.txt
```

### **3. Add your Groq API key**
Create a file named **.env**:

```
GROQ_API_KEY=your_groq_key_here
```

---

# Running the App

```bash
streamlit run app2.py
```

Open:  
http://localhost:8501

---

# How It Works

### **app2.py**
- Handles UI layout and chat rendering  
- Adds avatars depending on content  
- Contains crisis detection logic  
- Builds full prompt → forwarded to agent  
- Exports PDF/MD  
- Uses Streamlit session_state for message history

### **agent.py**
- Loads Groq client  
- Enforces strict therapy-safe system prompt  
- Streams model output  
- Returns a clean string reply

---

# 🛡️ Safety Rules (Enforced in `agent.py`)

The model **must refuse**:
- Medical diagnosis / medication  
- Travel, shopping, coding, finance, legal  
- Anything violent, hateful, or harm-related  
- Searching for services or locations  

Refusal template automatically used:
> “I can't help with that topic here. I focus on mental wellbeing…”

Crisis prompts trigger emergency suggestion (988 US or local services).

---

# Exporting Chats

### **PDF Export**
- Uses `FPDF`  
- Auto page numbers  
- Light card-style chat blocks  
- Unicode font support (via DejaVuSans.ttf)

### **Markdown Export**
- Simple readable format for journaling

Triggered via buttons at the bottom of the UI.

---

# Future Enhancements

- Mood tracking graph  
- Conversation summary AI  
- Daily reflection prompts  
- User-defined journaling templates  

---

# Author  
**Venkata Pavan Kumar Alapati**  
Creator of *AIIDA*, *Stomes*, and multiple AI agent systems  
M.S. Data Analytics — Clark University

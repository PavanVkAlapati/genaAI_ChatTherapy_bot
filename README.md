# Chat Therapy Bot

This project implements a therapy-style conversational agent using Streamlit and Groq’s LLaMA-3 models. It provides structured, safe, and predictable responses appropriate for mental-wellbeing use cases.

---

## Design Flow (Figma)

### Figma Board

[https://www.figma.com/board/r2qgsg2mWeQp1G30gUHVQl/Chat-Therapy-Bot-Process-Flow](https://www.figma.com/board/r2qgsg2mWeQp1G30gUHVQl/Chat-Therapy-Bot-Process-Flow)

## Features

### Therapy-Style Chat

Focused, supportive conversation flow delivering short, empathetic responses designed for general mental wellbeing.

### Crisis Detection

Monitors user messages for crisis keywords and activates an in-app crisis banner with guidance to immediate real-world help resources.

### Scope Control

Strictly prevents answers outside mental-wellbeing scope. Topics related to medical advice, legal, finance, travel, academic work, coding, or operational instructions are refused with a standard supportive message.

### PDF and Markdown Export

Allows users to export the entire chat session either as a formatted PDF or clean Markdown transcript.

### Local Session Memory

Session content is stored only in Streamlit session memory. No persistent storage or logging.

---

## Project Structure

```
genAI_ChatTherapy_bot/
│
├── app2.py               # Main Streamlit UI
├── agent.py              # Groq model wrapper and system prompt
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

## Installation

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add the Groq API key

Create a `.env` file:

```
GROQ_API_KEY=your_key_here
```

---

## Running the Application

```bash
streamlit run app2.py
```

Then open:

```
http://localhost:8501
```

---

## How It Works

### app2.py

* Handles full UI layout
* Implements crisis detection logic
* Renders chat messages with avatars
* Builds the model prompt
* Triggers PDF and Markdown exports
* Stores message history in session_state

### agent.py

* Wraps Groq model client
* Contains the complete system prompt
* Enforces safety and refusal logic
* Streams the model’s token output

---

## Safety Rules

The model is constrained to mental-wellbeing support only.
It refuses to engage in:

* Medical diagnosis, treatments, prescriptions
* Legal, financial, travel, or technical advice
* Violence-related or harmful content
* Operational or actionable instructions

Crisis-related content triggers an emergency-help banner.

---

## Exporting Chats

### PDF

Uses FPDF with a clean page layout and a Unicode-compatible font.

### Markdown

Simple, readable transcript for journaling or personal record keeping.

---

## Author

Venkata Pavan Kumar Alapati
MS Data Analytics, Clark University
Creator of AIIDA, Stomes, and multiple agent-based AI systems


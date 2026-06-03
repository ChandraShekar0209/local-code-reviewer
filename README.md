# 🔍 Local AI Code Reviewer

A privacy-first AI code reviewer that runs three open source LLMs 
entirely on your machine — no data leaves your device, no API costs, 
works completely offline.

---

## 🎯 Why local LLMs?

Companies cannot send proprietary code to cloud APIs like OpenAI — 
it is a legal and security risk. This tool runs everything locally:

| Cloud API | Local LLM (this tool) |
|---|---|
| Code sent to external servers | Code never leaves your machine |
| Costs money per query | Completely free |
| Needs internet | Works offline |
| Privacy risk | Zero privacy risk |

---

## 🤖 Models used

| Model | Size | Strengths |
|---|---|---|
| LLaMA 3.2 (3B) | 2.0 GB | Fast, lightweight, general purpose |
| CodeLlama (7B) | 3.8 GB | Specialised for code — trained on billions of lines |
| Mistral (7B) | 4.4 GB | Strong instruction following, structured output |

---

## 🔍 What it reviews

- 🐛 **Bugs** — logic errors, division by zero, null references
- 🔒 **Security** — SQL injection, hardcoded secrets, input validation
- ⚡ **Performance** — O(n2) loops, redundant computations, memory issues
- 💅 **Style** — naming, docstrings, type hints, PEP8 compliance

---

## 📊 Benchmark comparison

After all 3 models review your code the app shows:
- Response time per model
- Tokens per second
- Review quality score
- Winner recommendation

---

## 🛠️ Tech stack

| Tool | Purpose |
|---|---|
| Ollama | Run LLMs locally |
| LLaMA 3.2 / CodeLlama / Mistral | Open source LLMs |
| Python AST | Code structure analysis before LLM |
| Streamlit | UI |
| ReportLab | PDF report generation |
| psutil | Memory usage monitoring |

---

## ⚙️ Setup

### 1. Install Ollama

```bash
brew install ollama
```

Or download from ollama.com

### 2. Pull the models (one time only)

```bash
ollama pull llama3.2:3b
ollama pull codellama:7b
ollama pull mistral:7b
```

### 3. Clone the repo

```bash
git clone https://github.com/ChandraShekar0209/local-code-reviewer.git
cd local-code-reviewer
```

### 4. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the app

```bash
# terminal 1 — keep running
ollama serve

# terminal 2
streamlit run app.py
```

Open browser at http://localhost:8501

---

## 📁 Project structure

```
local-code-reviewer/
├── src/
│   ├── parser.py       — AST code analysis
│   ├── reviewer.py     — Ollama model calls
│   ├── benchmarker.py  — performance metrics
│   ├── scorer.py       — quality scoring
│   ├── reporter.py     — PDF report generation
│   └── models.py       — model configurations
├── prompts/
│   ├── review_prompt.py — structured review prompt
│   └── score_prompt.py  — quality scoring prompt
├── app.py              — Streamlit UI
└── requirements.txt
```

---

## 🧠 How it works

```
Python code input
      │
      ▼
AST parser — extract functions, classes, detect obvious issues
      │
      ▼
Structured prompt — code + metadata sent to each model
      │
      ▼
3 local LLMs review sequentially (respects 8GB RAM)
      │
      ▼
Benchmarker — measures time, tokens per second, memory per model
      │
      ▼
Scorer — LLM judges which review was best
      │
      ▼
Results displayed + PDF report downloadable
```

---

## 👤 Built by

Chandrashekar Garigapati
MS Data Science — SUNY Albany, Class of 2026
BS Computer Science — SRM University

GitHub: https://github.com/ChandraShekar0209

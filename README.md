# 🔍 Local AI Code Reviewer

A privacy-first AI code reviewer that runs three open source LLMs entirely on your machine — exposed as a production REST API. No data leaves your device, no API costs, works completely offline.

---

## 💡 Why I built this

Companies cannot send proprietary code to cloud APIs like OpenAI or Anthropic — it is a legal and security risk. One API call accidentally sends your company's secret algorithm to a cloud server. Career over.

I built this to solve that problem. This tool runs entirely locally — no internet required, no data leaves your machine, no cost per query. Three open source models review your code simultaneously and the system benchmarks which model gives the best review.

The secondary goal was learning — running local LLMs, understanding model size vs performance tradeoffs, building structured LLM output, and benchmarking AI systems scientifically. Each of these skills maps directly to real AI Engineer responsibilities.

**Note on model selection:**
Three models are used intentionally — LLaMA 3.2, CodeLlama, and Mistral — to demonstrate benchmarking across different architectures. CodeLlama is purpose-built for code and consistently wins on quality. LLaMA 3.2 wins on speed. Mistral wins on structured output quality. The comparison is the point.

---

## 🔌 API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Check API and Ollama status |
| GET | /models | List available local models |
| POST | /review | Full LLM review from all 3 models |
| POST | /analyse | Instant AST analysis — no LLM needed |

---

## 🤖 Models used

| Model | Size | Strengths |
|---|---|---|
| LLaMA 3.2 (3B) | 2.0 GB | Fast, lightweight, general purpose |
| CodeLlama (7B) | 3.8 GB | Specialised for code — trained on billions of lines |
| Mistral (7B) | 4.4 GB | Strong instruction following, structured output |

---

## 🔍 What it reviews

- Bugs — logic errors, division by zero, null references
- Security — SQL injection, hardcoded secrets, input validation
- Performance — O(n2) loops, redundant computations, memory issues
- Style — naming, docstrings, type hints, PEP8 compliance

---

## 🛠️ Tech stack

| Tool | Purpose |
|---|---|
| FastAPI | REST API framework |
| Ollama | Run LLMs locally |
| LLaMA 3.2 / CodeLlama / Mistral | Open source LLMs |
| Python AST | Code structure analysis before LLM |
| ReportLab | PDF report generation |
| psutil | Memory usage monitoring |
| Python | Core language |

---

## ⚙️ Setup

### 1. Install Ollama

```bash
brew install ollama
```

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

### 6. Run the API

```bash
# terminal 1 — keep running
ollama serve

# terminal 2
uvicorn main:app --reload
```

Open interactive API docs at http://localhost:8000/docs

---

## 🧪 Example API calls

```bash
# quick AST analysis — instant, no LLM needed
curl -X POST "http://localhost:8000/analyse" \
  -H "Content-Type: application/json" \
  -d '{"code": "def get_user(id):\n    password = \"admin123\"\n    return id"}'

# full LLM review — one model
curl -X POST "http://localhost:8000/review" \
  -H "Content-Type: application/json" \
  -d '{"code": "def get_user(id):\n    password = \"admin123\"\n    return id", "models": ["llama3.2:3b"]}'
```

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
├── main.py             — FastAPI REST API
└── requirements.txt
```

---

## 🧠 How it works

```
Python code (sent via API)
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
Structured JSON response via REST API
```

---

## 👤 Built by

Chandrashekar Garigapati

MS Data Science — SUNY Albany,

BS Computer Science — SRM University

GitHub: https://github.com/ChandraShekar0209

# ScholarRAG — Ask Your Research Papers Anything

> A local Retrieval-Augmented Generation (RAG) system that lets you ask natural-language questions across a collection of academic PDFs and receive cited, evidence-based answers powered by Claude AI.

---

## What It Does

You drop in a folder of research papers. ScholarRAG extracts the key sections (abstract, introduction, conclusion), indexes them, and serves a clean chat interface where you can ask questions. For every answer, it tells you exactly which papers it drew from.

**No cloud database. No embeddings API. No GPU. Runs entirely on your machine.**

---

## Demo

```
You:      What is explainable AI and how does SHAP work?

Claude:   Explainable AI (XAI) is a field concerned with developing methods
          that explain and interpret machine learning models (RL-26). It emerged
          to address the "black box" problem — where complex models improved
          accuracy but obscured decision-making...

          SHAP (SHapley Additive exPlanations) is model-agnostic and
          data-agnostic, making it applicable to any ML pipeline (RL-2).
          It assigns each feature an importance value for a given prediction...

Sources:  RL-2 · RL-11 · RL-26 · RL-12
```

---

## Architecture

```
pdfs/
  └── paper1.pdf, paper2.pdf ...
        │
        ▼
  extract_pdfs.py          ← pdfminer extracts abstract + intro + conclusion
        │
        ▼
  outputs/docs.json        ← structured text store (local file)
        │
        ▼
  retriever.py             ← keyword scoring ranks top-4 relevant papers
        │
        ▼
  app.py (Flask)           ← builds prompt, calls Claude API, returns answer
        │
        ▼
  index.html               ← browser chat interface
```

**Retrieval algorithm:** keyword frequency scoring — strips stopwords from the question, counts keyword occurrences across each document, returns the top-N scoring papers. Fast, transparent, zero dependencies.

---

## Quick Start

### 1. Prerequisites

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com)

### 2. Clone & Install

```bash
git clone https://github.com/ChaqBD/ScholarRAG.git
cd ScholarRAG
pip install pdfminer.six flask flask-cors
```

### 3. Add Your Papers

Copy your PDF files into the `pdfs/` folder.

### 4. Extract Text (run once)

```bash
python extract_pdfs.py
```

This creates `outputs/docs.json` from your PDFs.

### 5. Set Your API Key

Open `app.py` and replace `YOUR_API_KEY_HERE` with your Anthropic API key:

```python
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
```

Or set it as an environment variable (recommended):

```bash
# Mac/Linux
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows
set ANTHROPIC_API_KEY=sk-ant-...
```

### 6. Start the Server

```bash
python app.py
```

### 7. Open the Chat

Double-click `index.html` in your file explorer, or open it in your browser.

---

## Project Structure

```
ScholarRAG/
├── pdfs/                  # Put your PDF papers here
├── outputs/               # Auto-generated (docs.json lives here)
├── extract_pdfs.py        # PDF text extraction
├── retriever.py           # Keyword-based document ranking
├── app.py                 # Flask server + Claude API integration
├── index.html             # Chat interface (no build step)
└── README.md
```

---

## Configuration

All settings are at the top of `app.py`:

| Setting | Default | Description |
|---|---|---|
| `MODEL` | `claude-sonnet-4-6` | Claude model to use |
| `TOP_N_DOCS` | `4` | Papers retrieved per question |
| `max_tokens` | `1000` | Max length of Claude's answer |

---

## How the Retrieval Works

1. **Question comes in:** *"How does LSTM compare to Random Forest for forecasting?"*
2. **Stopwords stripped:** removes `how`, `does`, `to`, `for` → keywords: `lstm`, `compare`, `random`, `forest`, `forecasting`
3. **Each paper scored:** counts how many times those keywords appear in its extracted sections
4. **Top 4 papers selected** and their text is inserted into the Claude prompt
5. **Claude answers** using only those papers as context, citing each one

---

## Adapting to Your Own Papers

ScholarRAG works on any domain. Just drop in different PDFs. To tune the system prompt for your subject area, edit the `build_system_prompt()` function in `app.py`.

---

## Requirements

```
pdfminer.six
flask
flask-cors
```

No vector database, no OpenAI, no embedding model. Pure Python + Claude.

---

## License

MIT — free to use, fork, and build on.

---

## Author

**Shakir** · [ChaqBD](https://github.com/ChaqBD)

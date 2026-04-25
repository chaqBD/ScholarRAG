"""
Flask Web Server + Claude API
==============================
This is the backend of the RAG system.

What it does:
  1. Loads all extracted documents from outputs/docs.json on startup
  2. Listens for POST requests at http://127.0.0.1:5000/ask
  3. Retrieves the most relevant documents for each incoming question
  4. Builds a prompt containing those documents + the question
  5. Sends the prompt to the Claude API
  6. Returns Claude's answer + which papers were used

Usage:
    python app.py

Then open index.html in your browser.
"""

import json
import os
import urllib.request
import urllib.error

from flask import Flask, request, jsonify
from flask_cors import CORS

from retriever import load_documents, find_relevant_docs


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION  — edit this section
# ══════════════════════════════════════════════════════════════════════════════

# Your Anthropic API key.
# Get one at: https://console.anthropic.com
#
# Option A (quick):  paste your key directly below
# Option B (safer):  set an environment variable and read it:
#     Mac/Linux:  export ANTHROPIC_API_KEY="sk-ant-..."
#     Windows:    set ANTHROPIC_API_KEY=sk-ant-...
#
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")

# Claude model to use
MODEL = "claude-sonnet-4-6"

# Anthropic API endpoint
API_URL = "https://api.anthropic.com/v1/messages"

# How many papers to retrieve per question (higher = more context, slower)
TOP_N_DOCS = 4

# ══════════════════════════════════════════════════════════════════════════════


# ── Flask setup ───────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow browser requests from index.html

# Load documents once at startup (not on every request)
print("\nLoading documents from outputs/docs.json ...")
try:
    DOCUMENTS = load_documents('outputs/docs.json')
    print(f"Loaded {len(DOCUMENTS)} documents.")
    print(f"    Papers: {', '.join(list(DOCUMENTS.keys())[:5])} ...")
except FileNotFoundError as e:
    print(f"\nERROR: {e}")
    print("    Run  python extract_pdfs.py  first, then restart this server.\n")
    DOCUMENTS = {}

print("\nServer ready!  Open index.html in your browser.\n")


# ── Claude API call ───────────────────────────────────────────────────────────
def call_claude(system_prompt: str, user_question: str) -> str:
    """
    Send a request to the Claude API and return the response text.

    Args:
        system_prompt  : Instructions + retrieved document context
        user_question  : The user's actual question

    Returns:
        Claude's answer as a plain string
    """
    if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
        raise ValueError(
            "API key not set.\n"
            "Open app.py and replace YOUR_API_KEY_HERE with your real key,\n"
            "or set the ANTHROPIC_API_KEY environment variable."
        )

    payload = {
        "model": MODEL,
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_question}
        ]
    }

    data = json.dumps(payload).encode('utf-8')

    req = urllib.request.Request(
        url=API_URL,
        data=data,
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'x-api-key': API_KEY,
            'anthropic-version': '2023-06-01'
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        return result['content'][0]['text']

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise RuntimeError(f"API error {e.code}: {error_body}")


# ── Prompt builder ─────────────────────────────────────────────────────────────
def build_system_prompt(relevant_docs: list) -> str:
    """
    Construct the system prompt that Claude will read.

    The prompt contains:
      - Instructions telling Claude how to behave
      - The full text of the retrieved papers as context
    """
    # Build the context block from retrieved documents
    context_parts = []
    for doc_name, score in relevant_docs:
        doc_text = DOCUMENTS.get(doc_name, '')
        context_parts.append(f"=== Paper: {doc_name} ===\n{doc_text}")

    context = "\n\n".join(context_parts)

    return f"""You are a helpful research assistant. You have been given extracts from academic papers on Supply Chain Management, AI/ML, Explainable AI (XAI), demand forecasting, and related topics.

INSTRUCTIONS:
- Answer the question using ONLY the paper extracts provided below.
- When you use information from a specific paper, cite it (e.g. "According to RL-7...").
- Be concise, clear, and helpful.
- If the question cannot be answered from the provided papers, say so honestly.

PAPER EXTRACTS:
{context}"""


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    """Quick check to confirm the server is running."""
    return jsonify({
        'status': 'ok',
        'documents_loaded': len(DOCUMENTS),
        'model': MODEL
    })


@app.route('/ask', methods=['POST'])
def ask():
    """
    Main endpoint — receives a question, returns an answer.

    Request body  (JSON):  { "question": "What is SHAP?" }
    Response body (JSON):  { "answer": "SHAP is...", "sources": ["RL-22", "RL-26"] }
    """
    # Parse incoming request
    body     = request.get_json(silent=True) or {}
    question = body.get('question', '').strip()

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    if not DOCUMENTS:
        return jsonify({'error': 'No documents loaded. Run extract_pdfs.py first.'}), 500

    print(f"\nQuestion: {question}")

    # Step 1: Find relevant documents
    relevant = find_relevant_docs(question, DOCUMENTS, top_n=TOP_N_DOCS, verbose=True)
    sources  = [name for name, score in relevant]
    print(f"Using papers: {sources}")

    # Step 2: Build prompt with context
    system_prompt = build_system_prompt(relevant)

    # Step 3: Call Claude API
    try:
        answer = call_claude(system_prompt, question)
        print(f"Answer generated ({len(answer)} chars)")
        return jsonify({'answer': answer, 'sources': sources})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


# ── Start server ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',  # Only accessible from your own machine
        port=5000,
        debug=True         # Auto-restarts when you edit this file
    )

# RAG PDF Q&A System
# ==================
# Supply Chain Analytics & Explainable AI Research Papers
#
# ── QUICK START ───────────────────────────────────────────────────────────────
#
# 1. PUT YOUR PDFs IN THE pdfs/ FOLDER
#
# 2. INSTALL LIBRARIES (run once)
#       pip install pdfminer.six flask flask-cors
#
# 3. EXTRACT TEXT FROM PDFS (run once)
#       python extract_pdfs.py
#
# 4. ADD YOUR API KEY
#       Open app.py and replace YOUR_API_KEY_HERE with your Anthropic API key
#       (Get one at https://console.anthropic.com)
#
# 5. START THE SERVER
#       python app.py
#
# 6. OPEN THE CHAT PAGE
#       Double-click index.html  — OR —  right-click → Open with Live Server
#
# ── FILES ─────────────────────────────────────────────────────────────────────
#
#   extract_pdfs.py   Extract text from your PDFs → saves to outputs/docs.json
#   retriever.py      Keyword search algorithm (used by app.py automatically)
#   app.py            Flask web server + Claude API connection
#   index.html        The browser chat interface
#
#   pdfs/             PUT YOUR PDF FILES HERE
#   outputs/          Auto-generated files go here (docs.json)
#
# ── HOW IT WORKS ──────────────────────────────────────────────────────────────
#
#   Your Question
#       ↓
#   retriever.py  →  Scores all papers by keyword matches
#       ↓
#   Top 4 papers  →  Injected into the Claude prompt as context
#       ↓
#   Claude API    →  Reads context + generates answer
#       ↓
#   Your Answer (shown in browser with which papers were used)
#
# ── REQUIREMENTS ──────────────────────────────────────────────────────────────
#
#   Python 3.8+
#   pdfminer.six    (PDF text extraction)
#   flask           (local web server)
#   flask-cors      (allows browser requests to Flask)
#   Anthropic API key (console.anthropic.com)

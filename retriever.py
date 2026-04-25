"""
Keyword Retriever
==================
Finds the most relevant documents for any user question.

Algorithm:
  1. Split the question into individual words
  2. Remove stopwords (common words like "what", "is", "the")
  3. Count how many times each keyword appears in each document
  4. Return the top N documents with the highest keyword counts

This module is imported and used by app.py — you do not run it directly.
To test it, run:  python retriever.py
"""

import json
import re
from typing import List, Tuple

# ── Stopwords ──────────────────────────────────────────────────────────────────
# Common English words that appear everywhere and carry no search meaning.
# We filter these out so only meaningful keywords remain.
STOPWORDS = {
    'what', 'this', 'that', 'with', 'from', 'have', 'they',
    'their', 'does', 'about', 'which', 'would', 'could', 'should',
    'will', 'been', 'were', 'more', 'than', 'when', 'where', 'also',
    'into', 'over', 'after', 'some', 'such', 'other', 'most', 'each',
    'both', 'many', 'these', 'those', 'how', 'why', 'can', 'are',
    'the', 'and', 'for', 'not', 'but', 'has', 'had', 'its', 'our',
    'all', 'any', 'use', 'used', 'using', 'explain', 'describe',
    'tell', 'give', 'make', 'show', 'please', 'help', 'between',
    'paper', 'study', 'research', 'results', 'data', 'method',
}


def load_documents(docs_path: str = 'outputs/docs.json') -> dict:
    """Load extracted document text from the JSON file."""
    if not __import__('os').path.exists(docs_path):
        raise FileNotFoundError(
            f"'{docs_path}' not found.\n"
            "Please run  python extract_pdfs.py  first."
        )
    with open(docs_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_keywords(question: str) -> List[str]:
    """
    Turn a question string into a list of meaningful keywords.

    Example:
        Input  → "What is SHAP and how does it explain AI decisions?"
        Output → ['shap', 'explain', 'decisions']
    """
    words    = re.findall(r'\b[a-z]+\b', question.lower())
    keywords = [w for w in words if w not in STOPWORDS and len(w) >= 3]
    return keywords


def score_document(doc_text: str, keywords: List[str]) -> int:
    """
    Count how many times each keyword appears in a document.
    Returns the total count — higher means more relevant.
    """
    doc_lower = doc_text.lower()
    score = 0
    for keyword in keywords:
        matches = re.findall(r'\b' + re.escape(keyword) + r'\b', doc_lower)
        score += len(matches)
    return score


def find_relevant_docs(
    question:  str,
    documents: dict,
    top_n:     int = 4,
    verbose:   bool = False
) -> List[Tuple[str, int]]:
    """
    Main retrieval function.

    Given a user question and the full document dictionary, return
    the top_n most relevant document names with their scores.

    Args:
        question  : The user's question string
        documents : Dict of {doc_name: doc_text}
        top_n     : How many documents to return (default 4)
        verbose   : Print scoring details to terminal

    Returns:
        List of (doc_name, score) tuples, sorted by descending score
    """
    keywords = extract_keywords(question)

    if verbose:
        print(f"\n  Keywords -> {keywords}")

    if not keywords:
        # No meaningful keywords — return first top_n docs as fallback
        return [(name, 0) for name in list(documents.keys())[:top_n]]

    # Score every document
    scored = []
    for doc_name, doc_text in documents.items():
        score = score_document(doc_text, keywords)
        scored.append((doc_name, score))

    # Sort highest score first
    scored.sort(key=lambda x: x[1], reverse=True)

    if verbose:
        print("  Scores:")
        for name, score in scored:
            bar = '█' * min(score, 30)
            print(f"    {name:<12} {score:>3}  {bar}")

    # Return top N (must have at least 1 match)
    top = [(name, score) for name, score in scored[:top_n] if score > 0]

    # Fallback: if nothing scored, return top_n anyway
    if not top:
        top = scored[:top_n]

    return top


# ── Self-test ──────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("Loading documents...")
    docs = load_documents()
    print(f"Loaded {len(docs)} documents.\n")

    test_questions = [
        "What is explainable AI and how does SHAP work?",
        "How does LSTM compare to Random Forest for demand forecasting?",
        "What are the challenges of AI adoption in supply chain management?",
    ]

    for q in test_questions:
        print(f"Question: {q}")
        results = find_relevant_docs(q, docs, top_n=4, verbose=True)
        print(f"  -> Top docs: {[name for name, _ in results]}\n")

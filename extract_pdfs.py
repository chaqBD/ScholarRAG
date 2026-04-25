"""
STEP 3: Extract text from all PDFs
===================================
Run this script ONCE before starting the app.

It reads every PDF in the pdfs/ folder, extracts the
abstract, introduction, and conclusion, then saves the
result to outputs/docs.json

Usage:
    python extract_pdfs.py
"""

from pdfminer.high_level import extract_text
import os
import json


def extract_key_sections(full_text, max_chars=6000):
    """
    Extract only the most important sections from a paper:
      - Abstract     (what the paper is about)
      - Introduction (background and context)
      - Conclusion   (key findings)

    This keeps each document under 6000 characters so we can
    fit multiple documents into a single API call.
    """
    text_lower = full_text.lower()
    sections = {}

    # ── Abstract ─────────────────────────────────────────────────────────────
    abstract_start = text_lower.find('abstract')
    if abstract_start != -1:
        sections['abstract'] = full_text[abstract_start: abstract_start + 2000]

    # ── Introduction ─────────────────────────────────────────────────────────
    intro_start = text_lower.find('introduction')
    if intro_start != -1:
        sections['intro'] = full_text[intro_start: intro_start + 1500]
    else:
        sections['intro'] = full_text[:1500]  # fallback: start of document

    # ── Conclusion ───────────────────────────────────────────────────────────
    # Use rfind() so we search from the END (the conclusion is always at the end)
    for keyword in ['conclusion', 'discussion', 'summary']:
        conclusion_start = text_lower.rfind(keyword)
        # Only accept it if it's in the second half of the document
        if conclusion_start != -1 and conclusion_start > len(full_text) // 2:
            sections['conclusion'] = full_text[conclusion_start: conclusion_start + 3000]
            break

    # ── Combine and cap ───────────────────────────────────────────────────────
    combined = '\n\n'.join(sections.values())
    return combined[:max_chars]


def extract_all_pdfs(pdf_folder='pdfs', output_file='outputs/docs.json'):
    """
    Loop through all PDFs in pdf_folder, extract key sections,
    and save everything to a single JSON file.
    """
    # Get list of PDF files
    if not os.path.exists(pdf_folder):
        print(f"ERROR: Folder '{pdf_folder}/' not found.")
        print("       Please create a 'pdfs' folder and put your PDFs in it.")
        return

    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"ERROR: No PDF files found in '{pdf_folder}/' folder.")
        return

    print(f"Found {len(pdf_files)} PDFs. Extracting text...\n")

    all_documents = {}

    for filename in sorted(pdf_files):
        filepath = os.path.join(pdf_folder, filename)
        doc_name = filename.replace('.pdf', '').replace('.PDF', '')

        try:
            full_text = extract_text(filepath)
            key_text  = extract_key_sections(full_text)
            all_documents[doc_name] = key_text

            print(f"  OK  {filename:<30}  {len(full_text):>8,} chars  ->  {len(key_text):>5,} chars (key sections)")

        except Exception as e:
            print(f"  ERR  ERROR processing {filename}: {e}")

    # Save to JSON
    os.makedirs('outputs', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_documents, f, indent=2, ensure_ascii=False)

    total = sum(len(v) for v in all_documents.values())
    print(f"\nDone!")
    print(f"    Documents extracted : {len(all_documents)}")
    print(f"    Total characters    : {total:,}")
    print(f"    Saved to            : {output_file}")
    print(f"\n    Next step -> Run:  python app.py")


if __name__ == '__main__':
    extract_all_pdfs()

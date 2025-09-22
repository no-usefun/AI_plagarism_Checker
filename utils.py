import PyPDF2
from docx import Document
import joblib
import re
import unicodedata
import os
import numpy as np

# ---------------- Load Model & Vectorizer ----------------
MODEL_PATH = os.path.join("models", "lightgbm_ai_detector.pkl")
VECTORIZER_PATH = os.path.join("models", "tfidf_vectorizer.pkl")

lgb_model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# ---------------- Text Cleaning ----------------
def clean_text(text):
    """Normalize text to remove weird Unicode characters."""
    if not text:
        return ""
    text = unicodedata.normalize('NFKC', text)
    text = ''.join(c if c.isprintable() else ' ' for c in text)
    # Replace fancy quotes
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ---------------- Raw Text Processing ----------------
def process_text(text):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    pages = [paragraphs]
    chunks = paragraph_chunks_by_page(pages)
    detections = detect_ai_text_paragraphs(pages)
    return chunks, detections

# ---------------- PDF Extraction ----------------
def extract_paragraphs_pdf(file_path):

    reader = PyPDF2.PdfReader(file_path)
    pages = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            # Split by double newline for real paragraphs
            paragraphs = [clean_text(p) for p in re.split(r'\n\s*\n', page_text) if p.strip()]
            pages.append(paragraphs)
    return pages

# ---------------- DOCX Extraction ----------------
def extract_paragraphs_docx(file_path_or_bytes, in_memory=False):
    # Load document
    doc = Document(file_path_or_bytes)  # Works for both file and BytesIO

    pages = [[]]  # Start with first "page"
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        # Check for manual page break
        has_page_break = False
        for run in para.runs:
            for elem in run._element:
                if elem.tag.endswith('br') and elem.get(
                    '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type'
                ) == 'page':
                    has_page_break = True
        if has_page_break:
            # Start a new page
            pages.append([])
        pages[-1].append(clean_text(text))

    # Remove empty pages
    pages = [page for page in pages if page]

    # Instead of returning pages, flatten into paragraph-numbered chunks
    paragraphs = []
    para_num = 1
    for page in pages:
        for para in page:
            paragraphs.append([clean_text(para)])  # keep same structure
            para_num += 1

    return paragraphs  # Each entry = single paragraph


# ---------------- Paragraph Chunking ----------------
def paragraph_chunks_by_page(pages):
    chunks = []
    for i, page in enumerate(pages, start=1):
        for para in page:
            chunks.append((i, para))
    return chunks



# ---------------- AI Detection ----------------
def detect_ai_text_paragraphs(pages, model=None, vectorizer=None, threshold=0.6):
    if model is None:
        model = lgb_model
    if vectorizer is None:
        vectorizer = globals()["vectorizer"]
        
    chunks = paragraph_chunks_by_page(pages)
    texts = [para for _, para in chunks]

    X = vectorizer.transform(texts)

    # try:
    #     probs = model.predict_proba(X)[:,1] * 25
    # except:
    raw_scores = model.predict_proba(X)[:,1] * 25
    probs = 1 / (1 + np.exp(-raw_scores))

    results = []
    for (page_num, para), prob in zip(chunks, probs):
        label = "AI-generated" if prob >= threshold else "Human-written"
        results.append({
            "page": page_num,
            "paragraph": para,
            "word_count": len(para.split()),
            "probability_AI": round(float(prob), 4),
            "prediction": label
        })
    return results

def overall_ai_score(detections):
    if not detections:
        return 0.0

    ai_sum = sum(d["probability_AI"] for d in detections if d["prediction"] == "AI-generated")
    human_sum = sum(d["probability_AI"] for d in detections if d["prediction"] == "Human-written")

    denom = ai_sum + human_sum
    if denom == 0:
        return 0.0

    overall_score = (ai_sum / denom) * 100
    return round(overall_score, 2)


import PyPDF2
import docx

def extract_text_pdf(file_path):
    reader = PyPDF2.PdfReader(file_path)
    pages = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            paragraphs = [p.strip() for p in page_text.split("\n") if p.strip()]
            pages.append(paragraphs)
    return pages

def extract_text_docx(file_path):
    doc = docx.Document(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    # Split DOCX into pages every N paragraphs (e.g., 10 per page)
    paragraphs_per_page = 10
    pages = []
    for i in range(0, len(paragraphs), paragraphs_per_page):
        pages.append(paragraphs[i:i+paragraphs_per_page])
    return pages

def smart_chunk_paragraphs_by_page(pages, min_words=200, max_words=300):
 
    chunks = []

    for i, page in enumerate(pages, start=1):
        current_chunk = []
        word_count = 0

        for para in page:
            words = para.split()
            n_words = len(words)

            # Split large paragraph into multiple chunks
            if n_words > max_words:
                if current_chunk:
                    # Save any existing chunk first
                    chunks.append((i, " ".join(current_chunk)))
                    current_chunk = []
                    word_count = 0
                for j in range(0, n_words, max_words):
                    chunks.append((i, " ".join(words[j:j+max_words])))
                continue

            # Combine small paragraphs
            if word_count + n_words > max_words:
                # Save current chunk
                chunks.append((i, " ".join(current_chunk)))
                current_chunk = []
                word_count = 0

            current_chunk.append(para)
            word_count += n_words

        if current_chunk:
            chunks.append((i, " ".join(current_chunk)))

    return chunks

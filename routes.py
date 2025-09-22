from flask import Blueprint, request, render_template
from io import BytesIO
from utils import (
    extract_paragraphs_pdf,
    extract_paragraphs_docx,
    paragraph_chunks_by_page,
    detect_ai_text_paragraphs,
    process_text,
    overall_ai_score
)
import os

main_routes = Blueprint('main', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = {"pdf", "docx"}

# ---------------- Helpers ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- Routes ----------------
@main_routes.route("/", methods=["GET", "POST"])
def upload_file():
    file_chunks, file_detections = [], []
    text_chunks, text_detections = [], []
    filetype, filename = None, None
    overall_score = None

    if request.method == "POST":

        # ---------- File Upload ----------
        if "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]
            filename = file.filename
            ext = os.path.splitext(filename)[1].lower()

            if not allowed_file(filename):
                return render_template(
                    "upload.html",
                    file_chunks=[(0, "❌ Unsupported file format.")],
                    file_detections=[],
                    overall_score=None
                )

            try:
                file_bytes = BytesIO(file.read())
                if ext == ".pdf":
                    pages = extract_paragraphs_pdf(file_bytes)
                else:
                    pages = extract_paragraphs_docx(file_bytes, in_memory=True)

                file_detections = detect_ai_text_paragraphs(pages)
                overall_score = overall_ai_score(file_detections)

                file_chunks = paragraph_chunks_by_page(pages)
                filetype = ext[1:]
            except Exception as e:
                return render_template(
                    "upload.html",
                    file_chunks=[(0, f"❌ Error processing file: {str(e)}")],
                    file_detections=[],
                    overall_score=None
                )

        # ---------- Text Input ----------
        if "input_text" in request.form:
            user_text = request.form.get("input_text", "").strip()
            if user_text:
                text_chunks, text_detections = process_text(user_text)
                overall_score = overall_ai_score(text_detections)

    return render_template(
        "upload.html",
        file_chunks=file_chunks,
        file_detections=file_detections,
        text_chunks=text_chunks,
        text_detections=text_detections,
        filetype=filetype,
        filename=filename,
        zipped_file_data=zip(file_chunks, file_detections),
        overall_score=overall_score
    )

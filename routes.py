from flask import Blueprint, request, render_template, send_file, jsonify
from io import BytesIO
from utils import (
    extract_paragraphs_pdf,
    extract_paragraphs_docx,
    paragraph_chunks_by_page,
    detect_ai_text_paragraphs,
    process_text
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import json

main_routes = Blueprint('main', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = {"pdf", "docx"}


# ---------------- Helpers ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_ai_pdf(detections, filename="AI_Paragraphs.pdf"):
    """
    Generate a PDF containing only AI-generated paragraphs.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin
    line_height = 14
    c.setFont("Helvetica", 12)

    for det in detections:
        if det.get("prediction") != "AI-generated":
            continue

        paragraph_text = f"Page {det['page']}: {det['paragraph']}"
        # Split text into lines safely
        lines = paragraph_text.split('\n')
        for line in lines:
            # Wrap long lines to fit page width
            while len(line) > 100:
                if y < margin:
                    c.showPage()
                    y = height - margin
                    c.setFont("Helvetica", 12)
                c.drawString(margin, y, line[:100])
                line = line[100:]
                y -= line_height
            if y < margin:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 12)
            c.drawString(margin, y, line)
            y -= line_height
        y -= 10  # extra space between paragraphs

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')


# ---------------- Routes ----------------
@main_routes.route("/", methods=["GET", "POST"])
def upload_file():
    file_chunks, file_detections = [], []
    text_chunks, text_detections = [], []
    filetype, filename = None, None

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
                )

            try:
                file_bytes = BytesIO(file.read())
                if ext == ".pdf":
                    pages = extract_paragraphs_pdf(file_bytes)
                else:
                    pages = extract_paragraphs_docx(file_bytes, in_memory=True)

                file_chunks = paragraph_chunks_by_page(pages)
                file_detections = detect_ai_text_paragraphs(pages)
                filetype = ext[1:]
            except Exception as e:
                return render_template(
                    "upload.html",
                    file_chunks=[(0, f"❌ Error processing file: {str(e)}")],
                    file_detections=[],
                )

        # ---------- Text Input ----------
        if "input_text" in request.form:
            user_text = request.form.get("input_text", "").strip()
            if user_text:
                text_chunks, text_detections = process_text(user_text)

    return render_template(
        "upload.html",
        file_chunks=file_chunks,
        file_detections=file_detections,
        text_chunks=text_chunks,
        text_detections=text_detections,
        filetype=filetype,
        filename=filename,
        zipped_file_data=zip(file_chunks, file_detections)
    )


@main_routes.route("/download_ai_pdf", methods=["POST"])
def download_ai_pdf():
    """
    Generate PDF with only AI-generated paragraphs.
    Receives detections JSON from frontend.
    """
    data = request.form.get("detections_json", "[]")
    try:
        detections = json.loads(data)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400

    return create_ai_pdf(detections)

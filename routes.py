from flask import Blueprint, request, render_template, send_from_directory, current_app
from utils import extract_text_pdf, extract_text_docx, smart_chunk_paragraphs_by_page

main_routes = Blueprint('main', __name__, template_folder='templates')

@main_routes.route("/", methods=["GET", "POST"])
def upload_file():
    chunks, filetype, filename = [], None, None

    if request.method == "POST":
        file = request.files["file"]
        filename = file.filename
        filepath = f"{current_app.config['UPLOAD_FOLDER']}/{filename}"
        file.save(filepath)

        if filename.lower().endswith(".pdf"):
            pages = extract_text_pdf(filepath)
            filetype = "pdf"
            chunks = smart_chunk_paragraphs_by_page(pages)

        elif filename.lower().endswith(".docx"):
            pages = extract_text_docx(filepath)
            filetype = "docx"
            chunks = smart_chunk_paragraphs_by_page(pages)

        else:
            chunks = [(0, "❌ Unsupported file format. Please upload PDF or DOCX.")]
            return render_template("upload.html", chunks=chunks, filetype=None, filename=None)

    return render_template(
        "upload.html",
        chunks=chunks,
        filetype=filetype,
        filename=filename
    )

@main_routes.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

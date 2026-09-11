import os
from pathlib import Path
from docx import Document
from app.tools.ocr import extract_text, BASE_DIR

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


def _resolve_file_path(file_path: str) -> Path:
    p = Path(file_path)
    if p.is_file():
        return p
    cand_backend = BASE_DIR / file_path
    if cand_backend.is_file():
        return cand_backend
    cand_uploads = BASE_DIR / "uploads" / file_path
    if cand_uploads.is_file():
        return cand_uploads
    cand_data = BASE_DIR / "data" / file_path
    if cand_data.is_file():
        return cand_data
    return p


def extract_docx_text(path: Path) -> str:
    try:
        doc = Document(str(path))
        lines = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                lines.append(text)
        for table in doc.tables:
            for row in table.rows:
                row_str = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_str:
                    lines.append(row_str)
        if not lines:
            return "The document appears to be empty."
        return "\n".join(lines)
    except Exception as e:
        return f"Error reading Word document: {e}"


def extract_pdf_text(path: Path) -> str:
    if not PYPDF_AVAILABLE:
        return "PDF reader module (pypdf) is not installed."
    try:
        reader = PdfReader(str(path))
        lines = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                lines.append(f"--- Page {i+1} ---\n{page_text.strip()}")
        if not lines:
            return "No extractable text found in PDF (it may contain scanned images)."
        return "\n\n".join(lines)
    except Exception as e:
        return f"Error reading PDF document: {e}"


def extract_text_file(path: Path, max_chars: int = 25000) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_chars)
    except Exception as e:
        return f"Error reading text file: {e}"


def extract_file_content(file_path: str) -> tuple[str, str]:
    """
    Extracts readable text content from any supported file attachment.
    Returns (task_type, extracted_text).
    task_type: 'image' or 'document'
    """
    p = _resolve_file_path(file_path)
    if not p.is_file():
        return "document", f"Error: File not found at '{file_path}'"

    ext = p.suffix.lower()

    # Image attachments -> Tesseract OCR
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".gif"}:
        return "image", extract_text(str(p))

    # Microsoft Word documents (.docx, .doc)
    if ext in {".docx", ".doc"}:
        return "document", extract_docx_text(p)

    # Adobe PDF documents (.pdf)
    if ext == ".pdf":
        return "document", extract_pdf_text(p)

    # General text, code, csv, markdown, logs
    return "document", extract_text_file(p)

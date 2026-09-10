import shutil
import platform
from pathlib import Path
import pytesseract
from PIL import Image, UnidentifiedImageError

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Try to find tesseract automatically first (works cross-platform if it's on PATH).
# Only fall back to a hardcoded path on Windows, where PATH setup is often missed.
if shutil.which("tesseract") is None and platform.system() == "Windows":
    default_windows_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = default_windows_path


def _resolve_image_path(image_path: str) -> Path:
    p = Path(image_path)
    if p.is_file():
        return p
    # Check relative to backend directory
    cand_backend = BASE_DIR / image_path
    if cand_backend.is_file():
        return cand_backend
    # Check relative to backend/data directory
    cand_data = BASE_DIR / "data" / image_path
    if cand_data.is_file():
        return cand_data
    return p


def extract_text(image_path: str) -> str:
    """
    Extract text from an image using Tesseract OCR.

    This is a lightweight stand-in for a full vision-language model:
    it reads printed/typed text reliably, but will perform poorly on
    handwriting or heavily skewed/low-quality scans.
    """
    resolved_path = _resolve_image_path(image_path)
    try:
        img = Image.open(resolved_path)
    except FileNotFoundError:
        return f"Error: image not found at '{image_path}'"
    except UnidentifiedImageError:
        return f"Error: '{image_path}' isn't a valid or supported image file"
    except Exception as e:
        return f"Error opening image: {e}"

    try:
        text = pytesseract.image_to_string(img)
    except pytesseract.TesseractNotFoundError:
        return (
            "OCR failed: Tesseract engine is not installed or not on PATH. "
            "Please install Tesseract OCR and ensure it is available on your system PATH."
        )
    except Exception as e:
        return f"OCR failed: {e}"

    if not text.strip():
        return "No text could be extracted from this image — it may be blank, too low-resolution, or the text may be handwritten."

    return text.strip()
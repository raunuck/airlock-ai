import shutil
import platform
import pytesseract
from PIL import Image, UnidentifiedImageError

# Try to find tesseract automatically first (works cross-platform if it's on PATH).
# Only fall back to a hardcoded path on Windows, where PATH setup is often missed.
if shutil.which("tesseract") is None and platform.system() == "Windows":
    default_windows_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = default_windows_path


def extract_text(image_path: str) -> str:
    """
    Extract text from an image using Tesseract OCR.

    This is a lightweight stand-in for a full vision-language model:
    it reads printed/typed text reliably, but will perform poorly on
    handwriting or heavily skewed/low-quality scans. That's expected
    and worth saying out loud in the demo.
    """
    try:
        img = Image.open(image_path)
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
            "OCR failed: Tesseract engine isn't installed or isn't on PATH. "
            "Install it separately from the pytesseract pip package — "
        )
    except Exception as e:
        return f"OCR failed: {e}"

    if not text.strip():
        return "No text could be extracted from this image — it may be blank, too low-resolution, or the text may be handwritten."

    return text.strip()
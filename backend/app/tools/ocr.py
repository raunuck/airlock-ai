import shutil
import platform
from pathlib import Path
import pytesseract
from PIL import Image, UnidentifiedImageError

BASE_DIR = Path(__file__).resolve().parent.parent.parent

import os

# Try to find tesseract automatically first (works cross-platform if it's on PATH).
# Fall back to standard paths on Windows, where PATH setup is often missed.
if shutil.which("tesseract") is None and platform.system() == "Windows":
    candidates = [
        os.environ.get("TESSERACT_PATH"),
        os.environ.get("TESSERACT_CMD"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Tesseract-OCR", "tesseract.exe"),
        os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Programs", "Tesseract-OCR", "tesseract.exe"),
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            pytesseract.pytesseract.tesseract_cmd = candidate
            break


def _resolve_image_path(image_path: str) -> Path:
    p = Path(image_path)
    if p.is_file():
        return p
    # Check relative to backend directory
    cand_backend = BASE_DIR / image_path
    if cand_backend.is_file():
        return cand_backend
    # Check relative to backend/uploads directory
    cand_uploads = BASE_DIR / "uploads" / image_path
    if cand_uploads.is_file():
        return cand_uploads
    # Check relative to backend/data directory
    cand_data = BASE_DIR / "data" / image_path
    if cand_data.is_file():
        return cand_data
    return p


from PIL import Image, ImageOps, ImageEnhance, ImageStat, ImageFilter, UnidentifiedImageError


def _preprocess_image(img: Image.Image) -> list[Image.Image]:
    """
    Generates optimized image variants for Tesseract OCR:
    - Auto-inverts dark backgrounds (e.g. dark mode IDE code screenshots)
    - Upscales small/medium images with Lanczos filtering
    - Enhances contrast and sharpness for clean character edges
    """
    variants = []
    
    # 1. Grayscale
    gray = img.convert("L")
    
    # Check mean brightness
    stat = ImageStat.Stat(gray)
    mean_brightness = stat.mean[0]
    
    # If dark background, invert so text is dark on white
    if mean_brightness < 130:
        base = ImageOps.invert(gray)
    else:
        base = gray

    # 2. Rescale for optimal OCR character height
    w, h = base.size
    if w < 1200 or h < 900:
        scale = max(1.5, min(3.0, 1400.0 / max(w, 1)))
        new_w, new_h = int(w * scale), int(h * scale)
        upscaled = base.resize((new_w, new_h), Image.Resampling.LANCZOS)
    else:
        upscaled = base

    # 3. Contrast enhanced variant
    enhancer = ImageEnhance.Contrast(upscaled)
    enhanced = enhancer.enhance(1.6)
    enhanced = enhanced.filter(ImageFilter.SHARPEN)
    
    variants.append(enhanced)
    variants.append(upscaled)
    variants.append(gray)
    return variants


def extract_text(image_path: str) -> str:
    """
    Extract text from an image using Tesseract OCR with automatic image preprocessing.
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
        variants = _preprocess_image(img)
        best_text = ""
        
        # Test OCR passes on variants with PSM 6 (uniform text block) and PSM 3 (auto page segmentation)
        for variant in variants:
            for psm in ["--psm 6", "--psm 3"]:
                try:
                    res = pytesseract.image_to_string(variant, config=psm).strip()
                    if len(res) > len(best_text):
                        best_text = res
                except Exception:
                    continue
            if len(best_text) > 15:
                break

        text = best_text
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
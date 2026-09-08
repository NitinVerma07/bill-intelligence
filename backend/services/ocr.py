import os
from typing import Any
from .preprocessing import preprocess_image


def _configure_tesseract():
    try:
        import pytesseract
        from shutil import which
        if which("tesseract") is None:
            windows_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(windows_path):
                pytesseract.pytesseract.tesseract_cmd = windows_path
        return pytesseract
    except ImportError:
        return None


def run_ocr_pass(image_path: str) -> dict[str, Any]:
    pytesseract = _configure_tesseract()
    if pytesseract is None:
        raise RuntimeError(
            "pytesseract is not installed. Run: pip install pytesseract"
        )

    try:
        from PIL import Image, ImageOps, ImageEnhance
    except ImportError as exc:
        raise RuntimeError("Pillow is not installed.") from exc

    if not os.path.exists(image_path):
        raise RuntimeError("Uploaded image was not found.")

    enhanced_path = preprocess_image(image_path)
    paths = [image_path]
    if enhanced_path != image_path and os.path.exists(enhanced_path):
        paths.append(enhanced_path)

    texts = []
    confidences = []

    for path in paths:
        img = Image.open(path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        # Slight contrast/sharpness improvement for thermal receipts.
        img = ImageOps.autocontrast(img)
        img = ImageEnhance.Sharpness(img).enhance(1.5)

        data = pytesseract.image_to_data(
            img, config="--psm 6", output_type=pytesseract.Output.DICT
        )
        words = []
        local_conf = []
        for i, word in enumerate(data["text"]):
            word = (word or "").strip()
            if not word:
                continue
            words.append(word)
            try:
                c = float(data["conf"][i])
                if c >= 0:
                    local_conf.append(c / 100.0)
            except Exception:
                pass

        text = pytesseract.image_to_string(img, config="--psm 6")
        if text.strip():
            texts.append(text)
        if local_conf:
            confidences.append(sum(local_conf) / len(local_conf))

    if not texts:
        raise RuntimeError(
            "OCR returned no readable text. Try a clearer, brighter, more front-facing bill photo."
        )

    # Prefer the longest OCR result; it usually contains the most receipt lines.
    raw_text = max(texts, key=len)
    confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.55
    return {"raw_text": raw_text, "confidence": confidence, "boxes": []}

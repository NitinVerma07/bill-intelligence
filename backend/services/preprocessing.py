import os
import cv2
import numpy as np


def preprocess_image(image_path: str, output_path: str | None = None) -> str:
    if not os.path.exists(image_path):
        return image_path

    img = cv2.imread(image_path)
    if img is None:
        return image_path

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    norm = np.zeros_like(gray)
    gray = cv2.normalize(gray, norm, 0, 255, cv2.NORM_MINMAX)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)

    if output_path is None:
        base, ext = os.path.splitext(image_path)
        output_path = f"{base}_enhanced{ext}"

    cv2.imwrite(output_path, filtered)
    return output_path

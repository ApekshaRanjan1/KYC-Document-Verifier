# regex_ex.py
import cv2
import numpy as np
import pytesseract
import re
from PIL import Image

# ----------------------------
# Tesseract Path (Windows)
# ----------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ----------------------------
# Regex Patterns
# ----------------------------
PAN_REGEX = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
AADHAAR_REGEX = r"\b\d{4}\s\d{4}\s\d{4}\b"

# ----------------------------
# Image Preprocessing
# ----------------------------
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image from path: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh


# ----------------------------
# Main Extraction Function
# ----------------------------
def extract_details(image_path, extracted_text, predicted_label):
    """
    Extract PAN or Aadhaar details from image + OCR text.
    Uses regex patterns to find key identifiers.
    """
    processed = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'
    text_from_image = pytesseract.image_to_string(processed, lang="eng+hin", config=custom_config)

    # If OCR fails, fallback to grayscale
    if not text_from_image.strip():
        gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        text_from_image = pytesseract.image_to_string(gray, lang="eng+hin", config=custom_config)

    # Combine text from ML OCR + image OCR
    full_text = f"{extracted_text}\n{text_from_image}"

    # Apply regex
    pan_matches = re.findall(PAN_REGEX, full_text)
    aadhaar_matches = re.findall(AADHAAR_REGEX, full_text)

    # Filter based on document prediction
    if "Aadhaar" in predicted_label:
        filtered = aadhaar_matches
    elif "PAN" in predicted_label:
        filtered = pan_matches
    else:
        filtered = []

    return {
        "raw_text": full_text.strip(),
        "pan_matches": pan_matches,
        "aadhaar_matches": aadhaar_matches,
        "filtered_matches": filtered
    }

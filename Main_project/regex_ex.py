# regex_ex.py
import cv2
import numpy as np
import pytesseract
import re
from PIL import Image

# Adjust path if needed for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Regex patterns
PAN_REGEX = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
AADHAAR_REGEX = r"\b\d{4}\s\d{4}\s\d{4}\b"


def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh


def extract_details(image_path, predicted_label):
    """
    Extract PAN or Aadhaar details from the image based on predicted label.
    """
    processed = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(processed, lang="eng+hin", config=custom_config)

    # Fallback to grayscale OCR if empty
    if not text.strip():
        gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        text = pytesseract.image_to_string(gray, lang="eng+hin", config=custom_config)

    pan_matches = re.findall(PAN_REGEX, text)
    aadhaar_matches = re.findall(AADHAAR_REGEX, text)

    # Filter details based on predicted type
    if "Aadhaar" in predicted_label:
        filtered = aadhaar_matches
    elif "PAN" in predicted_label:
        filtered = pan_matches
    else:
        filtered = []

    return {
        "raw_text": text,
        "pan_matches": pan_matches,
        "aadhaar_matches": aadhaar_matches,
        "filtered_matches": filtered
    }

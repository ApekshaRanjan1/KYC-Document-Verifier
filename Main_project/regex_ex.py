# regex_ex.py
import cv2
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
DOB_REGEX = r"\b\d{2}/\d{2}/\d{4}\b"  # Adjust for DOB formats

# ----------------------------
# Image Preprocessing
# ----------------------------
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

# ----------------------------
# Main Extraction Function
# ----------------------------
def extract_details(image_path, extracted_text, predicted_label):
    """
    Extract Aadhaar/PAN info using OCR + regex, supports English + Hindi,
    returns structured JSON like:
    {
      "document_type": "PAN",
      "name": "Apeksha Aakanksha",
      "dob": "2000-01-01",
      "document_number": "ABCDE1234F",
      "status": "verified"
    }
    """
    processed = preprocess_image(image_path)
    config = r"--oem 3 --psm 6 -l eng+hin"

    # OCR from image
    text_from_image = pytesseract.image_to_string(processed, config=config)
    if not text_from_image.strip():
        gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        text_from_image = pytesseract.image_to_string(gray, config=config)

    # Merge OCRs
    full_text = f"{extracted_text}\n{text_from_image}"
    clean_text = re.sub(r"[^A-Za-z0-9\s\u0900-\u097F/]", " ", full_text)

    # Detect document type via keywords
    doc_type = "Unknown"
    if re.search(r"आधार|aadhaar|uidai", clean_text, re.I):
        doc_type = "Aadhaar Card"
    elif re.search(r"pan|income|tax", clean_text, re.I):
        doc_type = "PAN Card"

    # Regex matches
    pan_match = re.search(PAN_REGEX, clean_text)
    aadhaar_match = re.search(AADHAAR_REGEX, clean_text)
    dob_match = re.search(DOB_REGEX, clean_text)

    # Name heuristic: first 2 words
    words = clean_text.split()
    name = " ".join(words[:2]) if len(words) > 1 else "Unknown"

    # Build structured output
    if "PAN" in doc_type or "PAN" in predicted_label:
        structured_data = {
            "document_type": "PAN",
            "name": name,
            "dob": dob_match.group() if dob_match else "Unknown",
            "document_number": pan_match.group() if pan_match else "Unknown",
            "status": "verified" if pan_match else "unknown"
        }
    elif "Aadhaar" in doc_type or "Aadhaar" in predicted_label:
        structured_data = {
            "document_type": "Aadhaar",
            "name": name,
            "aadhaar_number": aadhaar_match.group() if aadhaar_match else "Unknown",
            "status": "verified" if aadhaar_match else "unknown"
        }
    else:
        structured_data = {
            "document_type": "Unknown",
            "raw_text": clean_text.strip(),
            "status": "unknown"
        }

    return structured_data

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
# Extraction Function
# ----------------------------
def extract_details(image_path, extracted_text, predicted_label):
    """Extract Aadhaar/PAN info using OCR + regex, supporting English + Hindi."""
    processed = preprocess_image(image_path)
    config = r"--oem 3 --psm 6 -l eng+hin"

    # Extract text
    text_from_image = pytesseract.image_to_string(processed, config=config)
    if not text_from_image.strip():
        gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        text_from_image = pytesseract.image_to_string(gray, config=config)

    # Merge OCRs
    full_text = f"{extracted_text}\n{text_from_image}"

    # Clean text (remove weird characters)
    clean_text = re.sub(r"[^A-Za-z0-9\s\u0900-\u097F]", " ", full_text)

    # Detect document type via keywords
    doc_type = "Unknown"
    if re.search(r"आधार|aadhaar|uidai", clean_text, re.I):
        doc_type = "Aadhaar Card"
    elif re.search(r"pan|income|tax", clean_text, re.I):
        doc_type = "PAN Card"

    # Apply regex
    pan_matches = re.findall(PAN_REGEX, clean_text)
    aadhaar_matches = re.findall(AADHAAR_REGEX, clean_text)

    # Final filter
    if "Aadhaar" in predicted_label or doc_type == "Aadhaar Card":
        filtered = aadhaar_matches
    elif "PAN" in predicted_label or doc_type == "PAN Card":
        filtered = pan_matches
    else:
        filtered = []

    return {
        "document_type": doc_type,
        "raw_text": clean_text.strip(),
        "pan_matches": pan_matches,
        "aadhaar_matches": aadhaar_matches,
        "filtered_matches": filtered
    }

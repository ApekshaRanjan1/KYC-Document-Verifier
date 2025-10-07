# regex_ex.py
import cv2
import pytesseract
import re
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

PAN_REGEX = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
AADHAAR_REGEX = r"\b\d{4}\s\d{4}\s\d{4}\b"

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

def extract_details(image_path, extracted_text, predicted_label):
    """Extract PAN/Aadhaar info using OCR + regex."""
    processed = preprocess_image(image_path)
    config = r"--oem 3 --psm 6 -l eng+hin"

    text_from_image = pytesseract.image_to_string(processed, config=config)
    if not text_from_image.strip():
        gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        text_from_image = pytesseract.image_to_string(gray, config=config)

    full_text = f"{extracted_text}\n{text_from_image}"
    clean_text = re.sub(r"[^A-Za-z0-9\s\u0900-\u097F:/.,-]", " ", full_text)

    doc_type = "Unknown"
    if re.search(r"आधार|aadhaar|uidai", clean_text, re.I):
        doc_type = "Aadhaar Card"
    elif re.search(r"pan|income|tax", clean_text, re.I):
        doc_type = "PAN Card"

    pan_matches = re.findall(PAN_REGEX, clean_text)
    aadhaar_matches = re.findall(AADHAAR_REGEX, clean_text)

    filtered = []
    name = ""
    dob = ""
    document_number = ""

    if doc_type == "Aadhaar Card":
        filtered = aadhaar_matches
        document_number = aadhaar_matches[0] if aadhaar_matches else ""
        name_match = re.search(r"(?:Name|नाम)[:\s]*([A-Za-z\s]+)", clean_text, re.I)
        if name_match:
            name = name_match.group(1).strip()
    elif doc_type == "PAN Card":
        filtered = pan_matches
        document_number = pan_matches[0] if pan_matches else ""
        # Find name: often above PAN number
        if pan_matches:
            pan_idx = clean_text.find(pan_matches[0])
            # Take 100 chars before PAN number and try to find the name
            before_pan = clean_text[max(0, pan_idx-100):pan_idx]
            # Heuristic: Names are words with capital letters
            name_candidates = re.findall(r"[A-Z][a-z]+(?: [A-Z][a-z]+)*", before_pan)
            if name_candidates:
                name = " ".join(name_candidates)
        # Try DOB
        dob_match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", clean_text)
        if dob_match:
            dob = dob_match.group(1)

    return {
        "document_type": doc_type,
        "status": "verified" if filtered else "unverified",
        "name": name,
        "document_number": document_number,
        "dob": dob,
        "raw_text": clean_text.strip(),
        "pan_matches": pan_matches,
        "aadhaar_matches": aadhaar_matches,
        "filtered_matches": filtered
    }

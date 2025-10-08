import cv2
import pytesseract
import re
import os
from PIL import Image

# Set your tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Regex patterns for PAN and Aadhaar
PAN_REGEX = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
AADHAAR_REGEX = r"\b\d{4}\s\d{4}\s\d{4}\b"


# -----------------------------
# Image Preprocessing
# -----------------------------
def preprocess_image(image_path, save_path=None):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Contrast enhancement (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Mild denoising
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Adaptive threshold for clarity
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 10
    )

    # Save preprocessed image (optional, for debugging)
    if save_path:
        cv2.imwrite(save_path, thresh)

    return thresh


# -----------------------------
# OCR + Extraction Logic
# -----------------------------
def extract_details(image_path, extracted_text="", predicted_label="", save_processed_path=None):
    """
    Performs two-pass OCR (raw + preprocessed), merges results, and extracts details.
    """
    config = r"--oem 3 --psm 6 -l eng+hin"

    # -------- PASS 1: Raw OCR --------
    try:
        raw_ocr = pytesseract.image_to_string(Image.open(image_path), config=config)
    except Exception as e:
        raw_ocr = ""
        print(f"[WARN] Raw OCR failed: {e}")

    # -------- PASS 2: Preprocessed OCR --------
    processed = preprocess_image(image_path, save_path=save_processed_path)
    processed_ocr = pytesseract.image_to_string(processed, config=config)

    # Fallback if processed gives empty
    if not processed_ocr.strip():
        gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        processed_ocr = pytesseract.image_to_string(gray, config=config)

    # -------- MERGE TEXT --------
    full_text = f"{extracted_text}\n{raw_ocr}\n{processed_ocr}"
    clean_text = re.sub(r"[^A-Za-z0-9\s\u0900-\u097F:/.,-]", " ", full_text)

    # -------- DETECT DOCUMENT TYPE --------
    doc_type = "Unknown"
    if re.search(r"आधार|aadhaar|uidai", clean_text, re.I):
        doc_type = "Aadhaar Card"
    elif re.search(r"pan|income|tax", clean_text, re.I):
        doc_type = "PAN Card"

    # -------- EXTRACT IDENTIFIERS --------
    pan_matches = re.findall(PAN_REGEX, clean_text)
    aadhaar_matches = re.findall(AADHAAR_REGEX, clean_text)

    filtered = []
    name = ""
    dob = ""
    document_number = ""

    # -------- Aadhaar Extraction --------
    if doc_type == "Aadhaar Card":
        filtered = aadhaar_matches
        document_number = aadhaar_matches[0] if aadhaar_matches else ""

        name_match = re.search(r"(?:Name|नाम)[:\s]*([A-Za-z\s]+)", clean_text, re.I)
        if name_match:
            name = name_match.group(1).strip()

    # -------- PAN Extraction --------
    elif doc_type == "PAN Card":
        filtered = pan_matches
        document_number = pan_matches[0] if pan_matches else ""

        if pan_matches:
            pan_idx = clean_text.find(pan_matches[0])
            before_pan = clean_text[max(0, pan_idx - 100):pan_idx]
            name_candidates = re.findall(r"[A-Z][a-z]+(?: [A-Z][a-z]+)*", before_pan)
            if name_candidates:
                name = " ".join(name_candidates)

        dob_match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", clean_text)
        if dob_match:
            dob = dob_match.group(1)

    # -------- RETURN STRUCTURED DATA --------
    return {
        "document_type": doc_type,
        "status": "verified" if filtered else "unverified",
        "name": name,
        "document_number": document_number,
        "dob": dob,
        "raw_text": clean_text.strip(),
        "pan_matches": pan_matches,
        "aadhaar_matches": aadhaar_matches,
        "filtered_matches": filtered,
        "raw_ocr": raw_ocr.strip(),
        "processed_ocr": processed_ocr.strip(),
    }

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
DOB_REGEX = r"\b\d{2}/\d{2}/\d{4}\b"  # For PAN DOB extraction

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
    """
    Extract structured Aadhaar or PAN details using OCR + regex.
    Outputs a dictionary like:
    {
        "document_type": "Aadhaar",
        "name": "Full Name",
        "dob": "YYYY-MM-DD",
        "aadhaar_number": "XXXX XXXX XXXX",
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

    # Merge ML OCR + image OCR
    full_text = f"{extracted_text}\n{text_from_image}"

    # Clean text (remove weird symbols)
    clean_text = re.sub(r"[^A-Za-z0-9\s\u0900-\u097F:/,.-]", " ", full_text)

    # Detect document type via keywords
    doc_type = "Unknown"
    if re.search(r"आधार|aadhaar|uidai", clean_text, re.I):
        doc_type = "Aadhaar"
    elif re.search(r"pan|income|tax", clean_text, re.I):
        doc_type = "PAN"

    result = {"document_type": doc_type, "status": "unverified"}

    # Extract numbers
    pan_matches = re.findall(PAN_REGEX, clean_text)
    aadhaar_matches = re.findall(AADHAAR_REGEX, clean_text)

    if doc_type == "Aadhaar":
        result["aadhaar_number"] = aadhaar_matches[0] if aadhaar_matches else "Unknown"

        # Name extraction (look for lines after "name" or "c/o")
        name_match = re.search(r"(?:name|नाम|c/o)\s*[:\-]?\s*([A-Za-z\s]+)", clean_text, re.I)
        result["name"] = name_match.group(1).strip() if name_match else "Unknown"

        result["document_number"] = result["aadhaar_number"]

    elif doc_type == "PAN":
        result["document_number"] = pan_matches[0] if pan_matches else "Unknown"

        # Name extraction (usually above PAN number)
        name_match = re.search(r"([A-Z][a-z]+\s[A-Z][a-z]+)", clean_text)
        result["name"] = name_match.group(1) if name_match else "Unknown"

        # DOB extraction
        dob_match = re.search(DOB_REGEX, clean_text)
        result["dob"] = dob_match.group(0) if dob_match else "Unknown"

    # Verify if key fields are present
    key_fields = ["name", "document_number"]
    result["status"] = "verified" if all(result.get(k) and result[k] != "Unknown" for k in key_fields) else "unverified"

    # Add raw text for debugging if needed
    result["raw_text"] = clean_text.strip()

    return result

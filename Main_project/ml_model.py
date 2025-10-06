import pickle
import pytesseract
from PIL import Image

# ----------------------------
# Load OCR + TF-IDF Model
# ----------------------------
MODEL_PATH = r"C:\Users\apeks\OneDrive\Desktop\Apeksha Desktop\College\SBI-Internship\KYC\ML_model\model\ocr_model.pkl"

with open(MODEL_PATH, "rb") as f:
    vectorizer, clf_text = pickle.load(f)


def preprocess_text(filepath: str):
    """Extract text from image using pytesseract and preprocess for ML model."""
    text = pytesseract.image_to_string(Image.open(filepath))
    text = text.strip().lower() or "empty"
    return vectorizer.transform([text]), text

def predict_document_type(filepath: str):
    """Predict whether the document is Aadhaar or PAN using ML + regex fallback."""
    features, extracted_text = preprocess_text(filepath)
    prediction = clf_text.predict(features)[0]

    # --- Heuristic override based on regex ---
    import re
    PAN_REGEX = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
    AADHAAR_REGEX = r"\b\d{4}\s\d{4}\s\d{4}\b"

    if re.search(PAN_REGEX, extracted_text):
        prediction = "PAN"
    elif re.search(AADHAAR_REGEX, extracted_text):
        prediction = "Aadhaar"

    label_map = {
        "aadhaar": "Aadhaar Card",
        "pan": "PAN Card"
    }
    readable_label = label_map.get(prediction.lower(), prediction)

    return readable_label, extracted_text


import base64
import requests
import re

API_KEY = "YOUR_API_KEY"  # Replace with your Google Vision API key
VISION_URL = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"

def extract_text_api_key(image_path):
    """Extracts full text from image using Google Vision API with API key"""
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    payload = {
        "requests": [
            {
                "image": {"content": img_b64},
                "features": [{"type": "TEXT_DETECTION"}]
            }
        ]
    }

    response = requests.post(VISION_URL, json=payload)
    result = response.json()
    try:
        return result["responses"][0]["fullTextAnnotation"]["text"]
    except KeyError:
        return ""

# -------------------- Aadhaar Parser --------------------
def parse_aadhaar_text(text):
    data = {"name": None, "dob": None, "gender": None, "aadhaar": None}
    name_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', text)
    dob_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
    gender_match = re.search(r'(?i)Male|Female', text)
    aadhaar_match = re.search(r'\d{4}\s\d{4}\s\d{4}', text)

    if name_match: data["name"] = name_match.group()
    if dob_match: data["dob"] = dob_match.group()
    if gender_match: data["gender"] = gender_match.group()
    if aadhaar_match: data["aadhaar"] = aadhaar_match.group()
    return data

# -------------------- PAN Parser --------------------
def parse_pan_text(text):
    data = {"name": None, "pan_number": None, "dob": None}
    pan_match = re.search(r'[A-Z]{5}\d{4}[A-Z]', text)
    dob_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
    name_match = re.search(r'([A-Z][A-Z ]+)', text)  # PAN names usually uppercase

    if name_match: data["name"] = name_match.group().title()
    if dob_match: data["dob"] = dob_match.group()
    if pan_match: data["pan_number"] = pan_match.group()
    return data

# -------------------- Unified KYC Extractor --------------------
def extract_kyc_data(image_path, doc_type="aadhaar"):
    text = extract_text_api_key(image_path)
    if doc_type.lower() == "aadhaar":
        return parse_aadhaar_text(text)
    elif doc_type.lower() == "pan":
        return parse_pan_text(text)
    else:
        raise ValueError("doc_type must be 'aadhaar' or 'pan'")

# -------------------- TEST --------------------
if __name__ == "__main__":
    aadhaar_file = "test_aadhaar.jpg"
    pan_file = "test_pan.jpg"

    print("Aadhaar Data:")
    print(extract_kyc_data(aadhaar_file, "aadhaar"))

    print("\nPAN Data:")
    print(extract_kyc_data(pan_file, "pan"))

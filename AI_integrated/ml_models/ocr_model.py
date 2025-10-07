import os
import re
from google.cloud import vision

def extract_text_google(image_path):
    from dotenv import load_dotenv
    load_dotenv()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    client = vision.ImageAnnotatorClient()

    with open(image_path, "rb") as f:
        content = f.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    return texts[0].description if texts else ""

def parse_aadhaar_text(text):
    name = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', text)
    dob = re.search(r'\d{2}/\d{2}/\d{4}', text)
    gender = re.search(r'(?i)Male|Female', text)
    aadhaar = re.search(r'\d{4}\s\d{4}\s\d{4}', text)
    return {
        "name": name.group() if name else None,
        "dob": dob.group() if dob else None,
        "gender": gender.group() if gender else None,
        "aadhaar": aadhaar.group() if aadhaar else None
    }

from flask import Flask, render_template, request, send_from_directory
import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
import re
import uuid

app = Flask(__name__)

# ✅ Folder for uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ✅ Set path to Tesseract (Windows only)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ PAN & Aadhaar regex
PAN_REGEX = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
AADHAAR_REGEX = r"\b\d{4}\s\d{4}\s\d{4}\b"


# ---------- Preprocessing Helpers ----------
def preprocess_for_ocr(img_cv):
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Otsu threshold
    otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # White pixel ratio
    white_ratio = cv2.countNonZero(otsu) / (otsu.shape[0] * otsu.shape[1])

    if white_ratio < 0.1 or white_ratio > 0.9:
        # fallback: adaptive threshold
        processed = cv2.adaptiveThreshold(
            blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 2
        )
        # Dilation (helps thin fonts)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        processed = cv2.dilate(processed, kernel, iterations=1)
    else:
        processed = otsu

    return processed


def deskew_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    coords = np.column_stack(np.where(gray > 0))

    if len(coords) == 0:
        return image

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 2:
        return image

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
    return rotated


# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def upload_and_scan():
    if request.method == "POST":
        file = request.files.get("image")
        if not file:
            return "No file uploaded!", 400

        # Unique filename
        uid = str(uuid.uuid4())
        orig_filename = f"{uid}_original.png"
        proc_filename = f"{uid}_processed.png"

        orig_path = os.path.join(app.config["UPLOAD_FOLDER"], orig_filename)
        proc_path = os.path.join(app.config["UPLOAD_FOLDER"], proc_filename)

        # Save original
        file.save(orig_path)

        # Load + preprocess
        img = Image.open(orig_path).convert("RGB")
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Deskew
        deskewed = deskew_image(img_cv)

        # Resize if too small
        h, w = deskewed.shape[:2]
        if h < 600 or w < 600:
            deskewed = cv2.resize(deskewed, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Processed version
        processed = preprocess_for_ocr(deskewed)

        # Save processed
        cv2.imwrite(proc_path, processed)

        # OCR
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(processed, lang="eng+hin", config=custom_config)

        # Fallback to grayscale if empty
        if not extracted_text.strip():
            gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)
            extracted_text = pytesseract.image_to_string(gray, lang="eng+hin", config=custom_config)

        # PAN & Aadhaar detection
        pan_matches = re.findall(PAN_REGEX, extracted_text)
        aadhaar_matches = re.findall(AADHAAR_REGEX, extracted_text)

        result = {
            "filename": orig_filename,
            "processed_filename": proc_filename,
            "raw_text": extracted_text,
            "pan_found": bool(pan_matches),
            "aadhaar_found": bool(aadhaar_matches),
            "pan_matches": pan_matches,
            "aadhaar_matches": aadhaar_matches
        }

        return render_template("result.html", result=result)

    return render_template("index.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)

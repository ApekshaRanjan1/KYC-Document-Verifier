from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import pytesseract
import os
import re
import cv2
import numpy as np
from PIL import Image

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "tiff", "bmp", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "replace-with-a-random-secret"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Regex patterns
PAN_REGEX = re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", re.IGNORECASE)
AADHAAR_REGEX = re.compile(r"\b(\d{4}\s?\d{4}\s?\d{4})\b")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def deskew_image(img_cv):
    """Detects skew and rotates image to correct it"""
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(bw > 0))
    if len(coords) == 0:
        return img_cv  # nothing to deskew
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = img_cv.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img_cv, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

@app.route("/", methods=["GET", "POST"])
def upload_and_scan():
    if request.method == "POST":
        if "image" not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files["image"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            # --- Read original image ---
            img_cv = cv2.imread(file_path)

            # --- Deskew / rotation correction ---
            img_cv = deskew_image(img_cv)

            # --- Preprocessing for OCR ---
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            processed_for_ocr = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

            # --- Preprocessing for display (human-friendly) ---
            preview = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            preview = cv2.GaussianBlur(preview, (3, 3), 0)

            processed_filename = "processed_" + filename
            processed_path = os.path.join(app.config["UPLOAD_FOLDER"], processed_filename)
            cv2.imwrite(processed_path, preview)

            # --- OCR ---
            raw_text = pytesseract.image_to_string(
                Image.fromarray(processed_for_ocr),
                lang="eng+hin",
                config="--psm 6"
            )
            cleaned_text = raw_text.strip()

            # --- PAN / Aadhaar Detection ---
            pan_matches = PAN_REGEX.findall(cleaned_text)
            aadhaar_matches = AADHAAR_REGEX.findall(cleaned_text)

            aadhaar_matches_normalized = []
            for m in aadhaar_matches:
                digits = re.sub(r"\s+", "", m)
                if len(digits) == 12:
                    spaced = f"{digits[0:4]} {digits[4:8]} {digits[8:12]}"
                    aadhaar_matches_normalized.append(spaced)

            # --- Result dictionary ---
            result = {
                "raw_text": cleaned_text,
                "pan_found": bool(pan_matches),
                "pan_matches": pan_matches,
                "aadhaar_found": bool(aadhaar_matches_normalized),
                "aadhaar_matches": aadhaar_matches_normalized,
                "filename": filename,
                "processed_filename": processed_filename
            }

            return render_template("result.html", result=result)
        else:
            flash("File type not allowed. Please upload an image.")
            return redirect(request.url)

    return render_template("index.html")

# Serve uploaded images
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True)

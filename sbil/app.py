from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import os
import re

# If tesseract is not in PATH, set it manually like this:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "tiff", "bmp", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "replace-with-a-random-secret"  # required for flash messages

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Regex patterns
PAN_REGEX = re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", re.IGNORECASE)
AADHAAR_REGEX = re.compile(r"\b(\d{4}\s?\d{4}\s?\d{4})\b")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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

            # Open image and perform OCR
            try:
                img = Image.open(file_path)
            except Exception as e:
                flash("Unable to open image: " + str(e))
                return redirect(request.url)

            raw_text = pytesseract.image_to_string(img, lang="eng", config="--psm 6")
            cleaned_text = raw_text.strip()

            # Search PAN / Aadhaar
            pan_matches = PAN_REGEX.findall(cleaned_text)
            aadhaar_matches = AADHAAR_REGEX.findall(cleaned_text)

            aadhaar_matches_normalized = []
            for m in aadhaar_matches:
                digits = re.sub(r"\s+", "", m)
                if len(digits) == 12:
                    spaced = f"{digits[0:4]} {digits[4:8]} {digits[8:12]}"
                    aadhaar_matches_normalized.append(spaced)

            result = {
                "raw_text": cleaned_text,
                "pan_found": bool(pan_matches),
                "pan_matches": pan_matches,
                "aadhaar_found": bool(aadhaar_matches_normalized),
                "aadhaar_matches": aadhaar_matches_normalized,
                "filename": filename
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

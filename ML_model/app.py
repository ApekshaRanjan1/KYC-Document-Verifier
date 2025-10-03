from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import pickle
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import pytesseract
from PIL import Image

UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load ML model
MODEL_PATH = os.path.join("model", "trained_model.pkl")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# Helper
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

# Preprocessing for ML model (image-based)
def preprocess(filepath):
    img = cv2.imread(filepath)
    img = cv2.resize(img, (128, 128))    # must match training size
    img = img.flatten().reshape(1, -1)   # flatten to vector
    return img

# OCR keyword-based fallback
def ocr_check(filepath):
    text = pytesseract.image_to_string(Image.open(filepath)).lower()
    if "income tax department" in text or "permanent account number" in text:
        return "pan"
    elif "aadhaar" in text:
        return "aadhaar"
    return None

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("index"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # ML model prediction
        features = preprocess(filepath)
        prediction = model.predict(features)[0]

        # Cross-check with OCR
        ocr_result = ocr_check(filepath)
        if ocr_result:
            prediction = ocr_result

        return render_template("result.html", filename=filename, prediction=prediction)

    return redirect(url_for("index"))

# Serve uploaded files
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(port=5001, debug=True)

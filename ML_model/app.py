from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import pickle
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import cv2
import numpy as np

# ----------------------------
# Config
# ----------------------------
UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------------------
# Load Models
# ----------------------------
MODEL_DIR = "model"

# OCR model
with open(os.path.join(MODEL_DIR, "ocr_model.pkl"), "rb") as f:
    vectorizer, clf_text = pickle.load(f)

# Image model
with open(os.path.join(MODEL_DIR, "img_model.pkl"), "rb") as f:
    clf_img = pickle.load(f)

# ----------------------------
# Helpers
# ----------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def preprocess_text(filepath):
    text = pytesseract.image_to_string(Image.open(filepath))
    text = text.strip().lower()
    if not text:
        text = "empty"
    return vectorizer.transform([text])

def preprocess_image(filepath):
    img = cv2.imread(filepath)
    img = cv2.resize(img, (128, 128))
    img = img.flatten().reshape(1, -1)
    return img

# ----------------------------
# Routes
# ----------------------------
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

        # OCR-based prediction
        features_text = preprocess_text(filepath)
        pred_text = clf_text.predict(features_text)[0]

        # Image-based prediction
        features_img = preprocess_image(filepath)
        pred_img = clf_img.predict(features_img)[0]

        return render_template(
            "result.html",
            filename=filename,
            pred_text=pred_text,
            pred_img=pred_img
        )

    return redirect(url_for("index"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    app.run(port=5001, debug=True)

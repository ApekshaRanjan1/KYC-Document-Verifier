from flask import Flask, render_template, request, redirect, url_for
import os
import pickle
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {"png", "jpg", "jpeg", "pdf"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load ML model
MODEL_PATH = os.path.join("model", "trained_model.pkl")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# ---- If using OCR+TFIDF ----
# with open(os.path.join("model", "vectorizer.pkl"), "rb") as f:
#     vectorizer = pickle.load(f)

# Helper
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# ================================================================
# OPTION 1: OCR + Text-based features
# ================================================================
"""
import pytesseract
from PIL import Image

def preprocess(filepath):
    # Extract text from image
    text = pytesseract.image_to_string(Image.open(filepath))
    # Convert to TF-IDF vector
    return vectorizer.transform([text])
"""

# ================================================================
# OPTION 2: Image-based model (e.g., SVM, RF on pixel features)
# ================================================================
import cv2
import numpy as np

def preprocess(filepath):
    img = cv2.imread(filepath)
    img = cv2.resize(img, (128, 128))    # must match training size
    img = img.flatten().reshape(1, -1)   # flatten to vector
    return img


# ================================================================
# Routes
# ================================================================
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

        # Preprocess & predict
        features = preprocess(filepath)
        prediction = model.predict(features)[0]

        return render_template("result.html", filename=filename, prediction=prediction)

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(port=5001, debug=True)

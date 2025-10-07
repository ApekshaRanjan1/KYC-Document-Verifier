from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from ml_model import predict_document_type
from regex_ex import extract_details

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXT = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

# ----------------------------
# Landing Page
# ----------------------------
@app.route("/landing")
def landing():
    return render_template("landing.html")

# ----------------------------
# Upload Page
# ----------------------------
@app.route("/scan", methods=["GET"])
def index():
    return render_template("index.html")

# ----------------------------
# Handle Upload + Scan (AJAX)
# ----------------------------
@app.route("/scan", methods=["POST"])
def scan():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        prediction, extracted_text = predict_document_type(filepath)
        extracted_data = extract_details(filepath, extracted_text, prediction)

        return jsonify({
            "filename": filename,
            "prediction": prediction,
            "extracted_data": extracted_data,
            "extracted_text": extracted_text
        })

    return jsonify({"error": "Invalid file"}), 400

# ----------------------------
# Result Page
# ----------------------------
@app.route("/result/<filename>")
def result(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(filepath):
        return "File not found", 404

    prediction, extracted_text = predict_document_type(filepath)
    extracted_data = extract_details(filepath, extracted_text, prediction)

    return render_template(
        "result.html",
        filename=filename,
        prediction=prediction,
        extracted_data=extracted_data,
        extracted_text=extracted_text
    )

# ----------------------------
# Serve Uploaded Files
# ----------------------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ----------------------------
# Root Redirect to Landing
# ----------------------------
@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("landing"))

if __name__ == "__main__":
    app.run(port=5001, debug=True)

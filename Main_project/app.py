from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from ml_model import predict_document_type
from regex_ex import extract_details

UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@app.route("/")
def index():
    return render_template("index.html")


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


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(port=5001, debug=True)

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from ml_model import predict_document_type
from regex_ex import extract_details

# ----------------------------
# Config
# ----------------------------
UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ----------------------------
# Helpers
# ----------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# ----------------------------
# Routes
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(url_for("index"))

        file = request.files["file"]
        if file.filename == "":
            return redirect(url_for("index"))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Run ML model
            prediction, extracted_text = predict_document_type(filepath)

            # Run regex extraction (image path + extracted text + label)
            extracted_data = extract_details(filepath, extracted_text, prediction)

            # Render result page
            return render_template(
                "result.html",
                filename=filename,
                prediction=prediction,
                extracted_data=extracted_data,
                extracted_text=extracted_text
            )

    return render_template("index.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    app.run(port=5001, debug=True)

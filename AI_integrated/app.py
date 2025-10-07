from flask import Flask, render_template, request
from ml_models.ocr_kyc import extract_kyc_data
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    if request.method == 'POST':
        doc_type = request.form.get('doc_type')
        id_file = request.files['id_image']
        id_path = os.path.join(UPLOAD_FOLDER, id_file.filename)
        id_file.save(id_path)

        # Extract structured data
        data = extract_kyc_data(id_path, doc_type)

    return render_template('index.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)

import os
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from qr_extraction import extract_qr_from_image
from pyaadhaar.decode import AadhaarOldQr, AadhaarSecureQr
import cv2
from pyzbar.pyzbar import decode

# ----------------------------
# Config
# ----------------------------
UPLOAD_FOLDER = 'dataset'
QR_FOLDER = 'output/valid'
OUTPUT_INVALID = 'output/invalid'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_INVALID, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'replace_this_with_env_secret'


# ----------------------------
# Helpers
# ----------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def decode_aadhaar_qr(qr_image_path):
    """
    Robust Aadhaar QR decoding — supports both Old & Secure formats,
    and gracefully handles malformed or partial QR data.
    """
    try:
        # Try Old Aadhaar QR first
        qr = AadhaarOldQr(qr_image_path)
        if qr.isValid():
            return 'valid', qr.decodeddata()

        # Try Secure Aadhaar QR
        secure = AadhaarSecureQr(qr_image_path)
        if secure.isValid():
            decoded = secure.decodeddata()
            if isinstance(decoded, dict) and 'uid' in decoded:
                return 'valid', decoded
            else:
                return 'invalid', 'Decoded but not in valid Aadhaar format'

        # Try manual decoding as fallback
        img = cv2.imread(qr_image_path)
        decoded_objs = decode(img)
        if decoded_objs:
            raw_text = decoded_objs[0].data.decode('utf-8', errors='ignore')
            if len(raw_text.strip()) > 20:
                return 'raw', raw_text

        # If all failed
        return 'invalid', 'QR not valid or unsupported format'

    except Exception as e:
        return 'error', f'Decode failed: {str(e)}'


# ----------------------------
# Flask Routes
# ----------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        qr_path = os.path.join(QR_FOLDER, f'qr_{filename}')
        found = extract_qr_from_image(save_path, qr_path)

        if not found:
            return render_template('index.html', error='QR not found in the image')

        status, payload = decode_aadhaar_qr(qr_path)
        if status == 'valid':
            return render_template('index.html', result=payload, filename=filename)
        elif status == 'raw':
            return render_template('index.html', raw_qr=payload, filename=filename)
        elif status == 'invalid':
            return render_template('index.html', error='QR found but invalid/unsupported')
        else:
            return render_template('index.html', error=f'Decoding error: {payload}')

    flash('File type not allowed')
    return redirect(url_for('index'))


# ----------------------------
# Run the app
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)

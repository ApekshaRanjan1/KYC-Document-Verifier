# qr_extraction.py

import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image

def extract_qr_from_image(input_path, output_path):
    """
    Robust Aadhaar QR extractor.
    Uses preprocessing + multiple detection methods.
    Returns True if QR found and saved.
    """
    img = cv2.imread(input_path)
    if img is None:
        print("❌ Could not read input image")
        return False

    # -------------------------
    # Step 1: Preprocess for better visibility
    # -------------------------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Improve contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Slight blur reduction & denoising
    gray = cv2.fastNlMeansDenoising(gray, None, 15, 7, 21)

    # Resize (upscale small images)
    h, w = gray.shape
    if w < 1000:
        scale = 2
        gray = cv2.resize(gray, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
        img = cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

    # -------------------------
    # Step 2: Try pyzbar (most reliable)
    # -------------------------
    decoded = decode(Image.fromarray(gray))
    if decoded:
        for obj in decoded:
            (x, y, w, h) = obj.rect
            qr_crop = img[y:y + h, x:x + w]
            cv2.imwrite(output_path, qr_crop)
            print("✅ QR detected via pyzbar")
            return True

    # -------------------------
    # Step 3: Try OpenCV QRCodeDetector
    # -------------------------
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(gray)
    if points is not None:
        pts = points[0] if isinstance(points, (list, tuple)) or points.shape[0] == 1 else points
        xs, ys = pts[:, 0], pts[:, 1]
        x_min, x_max = int(xs.min()), int(xs.max())
        y_min, y_max = int(ys.min()), int(ys.max())
        pad = 12
        h, w = img.shape[:2]
        x_min, y_min = max(0, x_min - pad), max(0, y_min - pad)
        x_max, y_max = min(w, x_max + pad), min(h, y_max + pad)
        qr_crop = img[y_min:y_max, x_min:x_max]
        cv2.imwrite(output_path, qr_crop)
        print("✅ QR detected via OpenCV")
        return True

    # -------------------------
    # Step 4: Try edge/contour fallback (for faint QRs)
    # -------------------------
    edged = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    possible_qr = [cv2.boundingRect(c) for c in contours if 100 < cv2.contourArea(c) < 50000]
    if possible_qr:
        # Pick the largest square-ish contour
        x, y, w, h = sorted(possible_qr, key=lambda r: r[2]*r[3], reverse=True)[0]
        qr_crop = img[y:y + h, x:x + w]
        cv2.imwrite(output_path, qr_crop)
        print("⚠️  QR approximated via contour fallback")
        return True

    print("❌ No QR detected by any method")
    return False

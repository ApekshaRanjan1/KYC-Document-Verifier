# qr_extraction.py — Correct debug folder placement (outside static)

import cv2
import os

def extract_qr_from_image(input_path, output_path):
    """
    Detect QR in Aadhaar image with enhanced preprocessing.
    Returns True if QR detected and cropped, else False.
    """

    img = cv2.imread(input_path)
    if img is None:
        print("❌ Could not read input image:", input_path)
        return False

    qr_detector = cv2.QRCodeDetector()

    # ✅ Keep all debug stuff OUTSIDE /static/
    debug_dir = os.path.join("output", "debug")
    os.makedirs(debug_dir, exist_ok=True)

    cv2.imwrite(os.path.join(debug_dir, "original.jpg"), img)

    preprocess_variants = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    preprocess_variants.append(("gray", gray))

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)
    preprocess_variants.append(("clahe", clahe))

    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 15, 10
    )
    preprocess_variants.append(("adaptive_thresh", thresh))

    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    preprocess_variants.append(("otsu", otsu))

    edges = cv2.Canny(gray, 100, 200)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(edges, kernel, iterations=1)
    preprocess_variants.append(("dilated_edges", dilated))

    for name, variant in preprocess_variants:
        data, points, _ = qr_detector.detectAndDecode(variant)
        cv2.imwrite(os.path.join(debug_dir, f"{name}.jpg"), variant)

        if points is not None and len(points) > 0:
            points = points.astype(int).reshape(-1, 2)
            cv2.polylines(img, [points], True, (0, 255, 0), 2)
            x, y, w, h = cv2.boundingRect(points)
            pad = 10
            x_min, y_min = max(0, x - pad), max(0, y - pad)
            x_max, y_max = min(img.shape[1], x + w + pad), min(img.shape[0], y + h + pad)

            qr_crop = img[y_min:y_max, x_min:x_max]
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, qr_crop)

            print(f"✅ QR detected using {name} preprocessing → {output_path}")
            print(f"🔍 Decoded data preview: {data[:80] if data else 'N/A'}")
            return True

    print("❌ No QR detected in any preprocessing stage. Try clearer or closer image.")
    return False

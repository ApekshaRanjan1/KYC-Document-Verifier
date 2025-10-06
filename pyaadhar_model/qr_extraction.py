import cv2
import os

def extract_qr(input_path, output_path):
    """Detect and crop QR code from Aadhaar image."""
    img = cv2.imread(input_path)
    qr_detector = cv2.QRCodeDetector()

    data, points, _ = qr_detector.detectAndDecode(img)
    if points is not None:
        points = points[0]
        x_min = int(min(points[:, 0]))
        x_max = int(max(points[:, 0]))
        y_min = int(min(points[:, 1]))
        y_max = int(max(points[:, 1]))

        qr_crop = img[y_min:y_max, x_min:x_max]
        cv2.imwrite(output_path, qr_crop)
        return True
    else:
        return False

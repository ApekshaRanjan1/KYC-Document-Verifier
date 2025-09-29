import os
import cv2
import re
import pytesseract
from ultralytics import YOLO

# -------------------------------
# 1️⃣ Paths
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "dataset")   # dataset root folder

# -------------------------------
# 2️⃣ Check dataset structure
# -------------------------------
for split in ["train", "val"]:
    split_path = os.path.join(DATA_DIR, split)
    if not os.path.exists(split_path):
        raise FileNotFoundError(f"{split_path} not found! Make sure train/val folders exist.")
    for cls in ["pan", "aadhar"]:
        cls_path = os.path.join(split_path, cls)
        if not os.path.exists(cls_path):
            raise FileNotFoundError(f"{cls_path} not found! Create subfolders for each class.")
        if len(os.listdir(cls_path)) == 0:
            raise ValueError(f"No images found in {cls_path}!")

print("✅ Dataset structure looks good!")

# -------------------------------
# 3️⃣ Load pretrained YOLOv8 classification model
# -------------------------------
model = YOLO("yolov8n-cls.pt")   # classification backbone

# -------------------------------
# 4️⃣ Train the classifier
# -------------------------------
model.train(
    data=DATA_DIR,                 # dataset root (train/val inside)
    epochs=4,
    imgsz=224,
    batch=32,
    name="pan_aadhar_classifier"
)

# -------------------------------
# 5️⃣ Inference function
# -------------------------------
def infer(image_path):
    results = model.predict(image_path)
    results.show()  # display image with predicted label

    probs = results[0].probs  # classification probabilities
    pred_class = int(probs.top1)
    confidence = float(probs.top1conf)
    class_name = model.names[pred_class]

    print(f"Predicted: {class_name}, Confidence: {confidence:.2f}")
    return class_name, confidence

# -------------------------------
# 6️⃣ OCR extraction (optional)
# -------------------------------
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config="--psm 6")

    # Regex patterns
    pan_match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", text.replace(" ", ""), re.I)
    aadhaar_match = re.search(r"(\d{4}\s?\d{4}\s?\d{4})", text)

    return {
        "pan_number": pan_match.group(0) if pan_match else None,
        "aadhaar_number": aadhaar_match.group(0) if aadhaar_match else None,
        "raw_text": text.strip()
    }

# -------------------------------
# 7️⃣ Test (uncomment to run)
# -------------------------------
# class_name, conf = infer("dataset/val/pan/sample_pan.jpg")
# print(extract_text_from_image("dataset/val/pan/sample_pan.jpg"))

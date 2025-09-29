# train.py
from ultralytics import YOLO
import cv2
import pytesseract
import re

# -------------------------------
# 1) Train YOLOv8 classifier
# -------------------------------
model = YOLO('yolov8n-cls.pt')  # pretrained YOLOv8 classification model

# Train on your PAN/Aadhaar dataset
model.train(
    data='data.yaml',
    epochs=30,        # increase if dataset is large
    imgsz=224,
    batch=32,
    lr0=0.01
)

# -------------------------------
# 2) Evaluate the model
# -------------------------------
metrics = model.val()
print("Validation metrics:", metrics)

# -------------------------------
# 3) Inference on new image
# -------------------------------
def infer(image_path):
    results = model.predict(image_path)
    results.show()  # show image with predicted label
    # extract predicted class and confidence
    pred_class = results[0].boxes.cls[0] if len(results[0].boxes) > 0 else None
    confidence = results[0].boxes.conf[0] if len(results[0].boxes) > 0 else None
    class_name = model.names[int(pred_class)] if pred_class is not None else "Unknown"
    print(f"Predicted: {class_name}, Confidence: {confidence}")
    return class_name, float(confidence) if confidence is not None else None

# Example usage:
infer('dataset/val/pan/sample_pan.jpg')  # replace with your test image
infer('dataset/val/aadhar/sample_aadhar.jpg')

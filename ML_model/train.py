import os
import pickle
import pytesseract
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# -----------------------------
# 1. Load Data (Images of Aadhaar & PAN)
# -----------------------------
# Suppose you have two folders:
# dataset/
#   aadhaar/
#       img1.jpg, img2.jpg ...
#   pan/
#       img1.jpg, img2.jpg ...

DATASET_DIR = "dataset"

texts, labels = [], []

for label_name in ["aadhaar", "pan"]:
    folder = os.path.join(DATASET_DIR, label_name)
    for filename in os.listdir(folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(folder, filename)
            text = pytesseract.image_to_string(Image.open(path))
            texts.append(text)
            labels.append(label_name)

print(f"Loaded {len(texts)} samples.")

# -----------------------------
# 2. Split Data
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# -----------------------------
# 3. Build Pipeline (TF-IDF + LogisticRegression)
# -----------------------------
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words="english")),
    ("clf", LogisticRegression(max_iter=1000))
])

# -----------------------------
# 4. Train Model
# -----------------------------
pipeline.fit(X_train, y_train)

# -----------------------------
# 5. Evaluate
# -----------------------------
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))

# -----------------------------
# 6. Save Model
# -----------------------------
MODEL_DIR = "model"
os.makedirs(MODEL_DIR, exist_ok=True)
with open(os.path.join(MODEL_DIR, "trained_model.pkl"), "wb") as f:
    pickle.dump(pipeline, f)

print("✅ Model trained and saved at model/trained_model.pkl")

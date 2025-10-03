import os
import pytesseract
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle

# Paths
dataset_path = "dataset"                # original dataset
augmented_path = "augmented_dataset"    # new Aadhaar-only augmentations

texts = []
labels = []

def load_images_from_folder(folder, label):
    """OCR all images from a folder with progress tracking"""
    data = []
    files = os.listdir(folder)
    total = len(files)

    for i, filename in enumerate(files, start=1):
        filepath = os.path.join(folder, filename)
        try:
            text = pytesseract.image_to_string(Image.open(filepath))
            data.append(text)
            labels.append(label)
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")

        # progress log every 10 images
        if i % 10 == 0 or i == total:
            print(f"✅ Processed {i}/{total} files in {label}...")
    return data

# -------------------------------
# 1. Load PAN (only original)
# -------------------------------
pan_folder = os.path.join(dataset_path, "pan")
if os.path.isdir(pan_folder):
    print("📂 Loading PAN images...")
    texts.extend(load_images_from_folder(pan_folder, "pan"))

# -------------------------------
# 2. Load Aadhaar (original + augmented)
# -------------------------------
aadhaar_folder = os.path.join(dataset_path, "aadhaar")
aug_aadhaar_folder = os.path.join(augmented_path, "aadhaar")

if os.path.isdir(aadhaar_folder):
    print("📂 Loading Aadhaar images...")
    texts.extend(load_images_from_folder(aadhaar_folder, "aadhaar"))

if os.path.isdir(aug_aadhaar_folder):
    print("📂 Loading Augmented Aadhaar images...")
    texts.extend(load_images_from_folder(aug_aadhaar_folder, "aadhaar"))

# -------------------------------
# 3. Training
# -------------------------------
print("🔹 Vectorizing...")
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(texts)
y = labels

print("🔹 Training model...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
clf = LinearSVC(class_weight="balanced")  # ✅ balance classes
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))

acc = accuracy_score(y_test, y_pred)
print(f"✅ Accuracy: {acc*100:.2f}%")

# Save model + vectorizer
os.makedirs("model", exist_ok=True)
with open("model/ocr_model.pkl", "wb") as f:
    pickle.dump((vectorizer, clf), f)

print("✅ Model trained and saved at model/ocr_model.pkl")

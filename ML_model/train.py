import os
import json
import time
import pytesseract
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
from collections import Counter
import re

# ----------------------------
# CONFIG (absolute paths)
# ----------------------------
BASE_DIR = r"C:\Users\apeks\OneDrive\Desktop\Apeksha Desktop\College\SBI-Internship\KYC\ML_model"

dataset_path = os.path.join(BASE_DIR, "dataset")                 # contains aadhaar/ and pan/
augmented_path = os.path.join(BASE_DIR, "augmented_dataset")     # contains augmented aadhaar/ and pan/
ocr_cache_file = os.path.join(BASE_DIR, "model", "ocr_cache.json")
MODEL_OUT = os.path.join(BASE_DIR, "model", "ocr_model.pkl")

# TF-IDF limit for speed/size
TFIDF_MAX_FEATURES = 3000

# ----------------------------
# Helpers
# ----------------------------
def clean_text_for_vectorizer(text):
    """Normalize OCR output before vectorizing."""
    if not text:
        return "empty"
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else "empty"

def load_ocr_cache(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_ocr_cache(path, cache):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)

def ocr_text_from_file(filepath, cache, new_count):
    """Return OCR text; use cache if available, otherwise run pytesseract and store."""
    key = os.path.abspath(filepath)
    if key in cache:
        return cache[key], new_count
    try:
        text = pytesseract.image_to_string(Image.open(filepath))
        cache[key] = text
        new_count += 1
    except Exception as e:
        print(f"❌ OCR error for {filepath}: {e}")
        text = ""
    return text, new_count

def gather_image_files():
    """Return [(filepath, label)] for PAN + Aadhaar (original + augmented)."""
    items = []

    # PAN (original)
    pan_folder = os.path.join(dataset_path, "pan")
    if os.path.isdir(pan_folder):
        for fname in os.listdir(pan_folder):
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                items.append((os.path.join(pan_folder, fname), "pan"))

    # Aadhaar (original)
    aadhaar_folder = os.path.join(dataset_path, "aadhaar")
    if os.path.isdir(aadhaar_folder):
        for fname in os.listdir(aadhaar_folder):
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                items.append((os.path.join(aadhaar_folder, fname), "aadhaar"))

    # Augmented Aadhaar
    aug_aadhaar_folder = os.path.join(augmented_path, "aadhaar")
    if os.path.isdir(aug_aadhaar_folder):
        for fname in os.listdir(aug_aadhaar_folder):
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                items.append((os.path.join(aug_aadhaar_folder, fname), "aadhaar"))

    # Augmented PAN
    aug_pan_folder = os.path.join(augmented_path, "pan")
    if os.path.isdir(aug_pan_folder):
        for fname in os.listdir(aug_pan_folder):
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                items.append((os.path.join(aug_pan_folder, fname), "pan"))

    return items

# ----------------------------
# MAIN
# ----------------------------
def main():
    start_time = time.time()

    # Load cache
    ocr_cache = load_ocr_cache(ocr_cache_file)
    print(f"🔹 OCR cache loaded: {len(ocr_cache)} entries (will grow)")

    # Gather all image paths
    files = gather_image_files()
    total = len(files)
    if total == 0:
        print("❌ No image files found. Check dataset folders.")
        return

    print(f"📊 Found {total} total images (PAN + Aadhaar + augmentations).")

    texts, labels = [], []
    new_ocr_count = 0

    # OCR all images
    for idx, (fp, label) in enumerate(files, start=1):
        text, new_ocr_count = ocr_text_from_file(fp, ocr_cache, new_ocr_count)
        text = clean_text_for_vectorizer(text)
        texts.append(text)
        labels.append(label)

        if idx % 10 == 0 or idx == total:
            print(f"✅ OCR processed {idx}/{total} files...")

    # Save updated cache
    save_ocr_cache(ocr_cache_file, ocr_cache)
    cached_now = len(ocr_cache)
    cached_before = cached_now - new_ocr_count

    print(f"\n📦 OCR summary:")
    print(f"   🔁 Cached images used: {cached_before}")
    print(f"   🆕 New OCR runs: {new_ocr_count}")
    print(f"   💾 Total cached entries: {cached_now}")

    # Class distribution
    dist = Counter(labels)
    print("\n📈 Class distribution:", dict(dist))

    # ----------------------------
    # Training
    # ----------------------------
    print("\n🔹 Vectorizing (TF-IDF)...")
    vectorizer = TfidfVectorizer(max_features=TFIDF_MAX_FEATURES)
    X = vectorizer.fit_transform(texts)
    y = labels

    print("🔹 Training model (LinearSVC)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = LinearSVC(class_weight="balanced", dual=False, max_iter=5000, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluate
    print("\n📊 Classification Report:")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))

    acc = accuracy_score(y_test, y_pred)
    train_acc = accuracy_score(y_train, clf.predict(X_train))
    print(f"✅ Test Accuracy: {acc*100:.2f}%")
    print(f"✅ Train Accuracy: {train_acc*100:.2f}%")

    # Save model
    os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
    with open(MODEL_OUT, "wb") as f:
        pickle.dump((vectorizer, clf), f)

    elapsed = time.time() - start_time
    print(f"\n✅ Model trained and saved at {MODEL_OUT}")
    print(f"⏱️ Total time: {elapsed:.1f}s")

# ----------------------------
if __name__ == "__main__":
    main()

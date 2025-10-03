import os
import pytesseract
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle

dataset_path = "dataset"
texts = []
labels = []

count = 0
total_files = sum(len(files) for _, _, files in os.walk(dataset_path))

for label in os.listdir(dataset_path):
    folder = os.path.join(dataset_path, label)
    if not os.path.isdir(folder):
        continue
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        try:
            text = pytesseract.image_to_string(Image.open(filepath))
            texts.append(text)
            labels.append(label)
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
        count += 1
        if count % 10 == 0:
            print(f"✅ Processed {count}/{total_files} files...")

print("🔹 Vectorizing...")
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(texts)
y = labels

print("🔹 Training model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = LinearSVC()
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model + vectorizer
os.makedirs("model", exist_ok=True)
with open("model/trained_model.pkl", "wb") as f:
    pickle.dump(clf, f)
with open("model/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ Model trained and saved at model/trained_model.pkl")

import os
import pandas as pd
from pyaadhaar.decode import AadhaarQr, AadhaarSecureQr
from qr_extraction import extract_qr

# Input & Output folders
DATASET_DIR = "dataset"
OUTPUT_VALID = "output/valid"
OUTPUT_INVALID = "output/invalid"
RESULTS_FILE = "output/results.csv"

os.makedirs(OUTPUT_VALID, exist_ok=True)
os.makedirs(OUTPUT_INVALID, exist_ok=True)

results = []

for filename in os.listdir(DATASET_DIR):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue

    input_path = os.path.join(DATASET_DIR, filename)
    qr_path = os.path.join(OUTPUT_VALID, f"qr_{filename}")

    print(f"Processing: {filename}")

    # Step 1: Extract QR code
    if not extract_qr(input_path, qr_path):
        print("❌ QR not detected")
        results.append({"file": filename, "status": "QR Not Found"})
        os.rename(input_path, os.path.join(OUTPUT_INVALID, filename))
        continue

    # Step 2: Decode QR using pyaadhaar
    try:
        # Try normal QR (old Aadhaar format)
        qr = AadhaarQr(qr_path)
        if qr.isValid():
            data = qr.decodeddata()
            results.append({"file": filename, "status": "Valid", **data})
            print("✅ Decoded using AadhaarQr")
            continue

        # Try secure QR (new format)
        secure_qr = AadhaarSecureQr(qr_path)
        if secure_qr.isValid():
            data = secure_qr.decodeddata()
            results.append({"file": filename, "status": "Valid", **data})
            print("✅ Decoded using AadhaarSecureQr")
        else:
            results.append({"file": filename, "status": "Invalid QR"})
            os.rename(input_path, os.path.join(OUTPUT_INVALID, filename))
            print("❌ Invalid QR")

    except Exception as e:
        print("⚠️ Error decoding:", e)
        results.append({"file": filename, "status": "Error", "error": str(e)})
        os.rename(input_path, os.path.join(OUTPUT_INVALID, filename))

# Step 3: Save results to CSV
df = pd.DataFrame(results)
df.to_csv(RESULTS_FILE, index=False)
print(f"\n📄 Results saved to {RESULTS_FILE}")


import os
import cv2
import numpy as np
import random
from tqdm import tqdm

# Paths
DATASET_DIR = "dataset"
AADHAAR_DIR = os.path.join(DATASET_DIR, "aadhaar")
PAN_DIR = os.path.join(DATASET_DIR, "pan")

# Output dir for augmented Aadhaar
AUG_DIR = os.path.join(DATASET_DIR, "aadhaar_augmented")
os.makedirs(AUG_DIR, exist_ok=True)

# Count current files
aadhaar_count = len(os.listdir(AADHAAR_DIR))
pan_count = len(os.listdir(PAN_DIR))

print(f"📊 Aadhaar: {aadhaar_count}, PAN: {pan_count}")

# Number of extra Aadhaar images needed to match PAN
extra_needed = max(0, pan_count - aadhaar_count)
print(f"✅ Will generate {extra_needed} augmented Aadhaar images")

if extra_needed == 0:
    print("⚠️ Aadhaar already balanced or more than PAN. Nothing to do.")
    exit()

# Augmentation functions
def augment(img):
    aug_list = []
    
    # Blur
    aug_list.append(cv2.GaussianBlur(img, (5, 5), 0))
    
    # Noise
    noise = np.random.randint(0, 50, img.shape, dtype="uint8")
    aug_list.append(cv2.add(img, noise))
    
    # Brightness/Contrast
    alpha = random.uniform(0.7, 1.3)
    beta = random.randint(-30, 30)
    aug_list.append(cv2.convertScaleAbs(img, alpha=alpha, beta=beta))
    
    # Rotation
    (h, w) = img.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), random.randint(-5, 5), 1.0)
    aug_list.append(cv2.warpAffine(img, M, (w, h)))
    
    return aug_list

# Create augmented images
all_files = os.listdir(AADHAAR_DIR)
idx = 0
pbar = tqdm(total=extra_needed, desc="Augmenting Aadhaar")

while idx < extra_needed:
    fname = random.choice(all_files)
    path = os.path.join(AADHAAR_DIR, fname)
    img = cv2.imread(path)

    if img is None:
        continue

    for aug_img in augment(img):
        if idx >= extra_needed:
            break
        out_name = f"aug_{idx}_{fname}"
        out_path = os.path.join(AUG_DIR, out_name)
        cv2.imwrite(out_path, aug_img)
        idx += 1
        pbar.update(1)

pbar.close()
print("✅ Augmentation complete!")

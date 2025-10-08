# augment_aadhaar.py
import os
import cv2
import numpy as np   # ✅ needed for noise
import random
from PIL import Image, ImageEnhance, ImageFilter

dataset_path = "dataset/aadhaar"          
augmented_path = "augmented_dataset/aadhaar"  
os.makedirs(augmented_path, exist_ok=True)

# how many new augmented versions per Aadhaar image
N_AUGMENTS = 2  

def augment_image(img):
    """Apply a random augmentation to the given PIL image"""
    choice = random.choice(["blur", "noise", "contrast", "rotate"])
    if choice == "blur":
        return img.filter(ImageFilter.GaussianBlur(radius=2))
    elif choice == "noise":
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        noise = (np.random.randn(*cv_img.shape) * 25).astype("uint8")
        cv_img = cv2.add(cv_img, noise)
        return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
    elif choice == "contrast":
        return ImageEnhance.Contrast(img).enhance(random.uniform(0.5, 1.5))
    elif choice == "rotate":
        return img.rotate(random.choice([5, -5, 10, -10]))
    return img

print("📂 Starting Aadhaar augmentation...")

# count total files for progress tracking
all_files = [f for f in os.listdir(dataset_path) if os.path.isfile(os.path.join(dataset_path, f))]
total_files = len(all_files)

count = 0
for idx, filename in enumerate(all_files, start=1):
    filepath = os.path.join(dataset_path, filename)
    try:
        img = Image.open(filepath)

        for i in range(N_AUGMENTS):
            aug_img = augment_image(img)
            save_name = f"{os.path.splitext(filename)[0]}_aug{i}.png"
            save_path = os.path.join(augmented_path, save_name)
            aug_img.save(save_path)
            count += 1

        # ✅ show progress every 10 files
        if idx % 10 == 0 or idx == total_files:
            print(f"✅ Processed {idx}/{total_files} Aadhaar files...")

    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")

print(f"\n✅ Augmentation complete! Generated {count} new Aadhaar images in {augmented_path}")

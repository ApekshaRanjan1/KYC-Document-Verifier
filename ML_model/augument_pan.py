import os
import random
from PIL import Image, ImageEnhance, ImageFilter
from tqdm import tqdm

# ------------------------------------------
# CONFIG
# ------------------------------------------
SOURCE_DIR = r"C:\Users\apeks\OneDrive\Desktop\Apeksha Desktop\College\SBI-Internship\KYC\ML_model\dataset\pan"   # original PAN images
DEST_DIR = r"C:\Users\apeks\OneDrive\Desktop\Apeksha Desktop\College\SBI-Internship\KYC\ML_model\augmented_dataset\pan"  # save augmented images here
AUG_PER_IMAGE = 2    # only 2 augmentations per image

# ------------------------------------------
# AUGMENTATION HELPERS
# ------------------------------------------
def augment_image(img):
    """Randomly apply one of several simple augmentations."""
    augmentations = [
        lambda x: x.rotate(random.uniform(-5, 5)),  # small rotation
        lambda x: x.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5))),  # light blur
        lambda x: ImageEnhance.Brightness(x).enhance(random.uniform(0.8, 1.2)),         # brightness tweak
        lambda x: ImageEnhance.Contrast(x).enhance(random.uniform(0.8, 1.2)),           # contrast tweak
        lambda x: ImageEnhance.Sharpness(x).enhance(random.uniform(0.8, 1.3))           # sharpness tweak
    ]
    return random.choice(augmentations)(img)

# ------------------------------------------
# MAIN
# ------------------------------------------
def main():
    os.makedirs(DEST_DIR, exist_ok=True)

    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    total = len(files)

    if total == 0:
        print("❌ No PAN images found.")
        return

    print(f"📂 Found {total} PAN images for augmentation")
    print(f"⚙️ Generating {AUG_PER_IMAGE} augmentations per image ({total * AUG_PER_IMAGE} total)")

    for fname in tqdm(files, desc="Augmenting PANs"):
        src_path = os.path.join(SOURCE_DIR, fname)
        try:
            img = Image.open(src_path)
            for i in range(AUG_PER_IMAGE):
                aug_img = augment_image(img)
                base_name, ext = os.path.splitext(fname)
                dest_name = f"{base_name}_aug{i+1}{ext}"
                dest_path = os.path.join(DEST_DIR, dest_name)
                aug_img.save(dest_path)
        except Exception as e:
            print(f"❌ Error processing {fname}: {e}")

    print(f"✅ Done. {total * AUG_PER_IMAGE} augmented PAN images saved in {DEST_DIR}")

if __name__ == "__main__":
    main()

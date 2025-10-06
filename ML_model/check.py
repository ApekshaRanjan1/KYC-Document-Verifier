from collections import Counter
from train import gather_image_files
print(Counter([label for _, label in gather_image_files()]))

import os
import random
from PIL import Image, ImageEnhance, ImageFilter

random.seed(42)

os.makedirs("static/images", exist_ok=True)

base = Image.open("base_image.jpg").convert("RGB")

for i in range(1, 51):
    brightness = random.uniform(0.91, 1.09)
    contrast   = random.uniform(0.93, 1.07)
    color      = random.uniform(0.94, 1.06)
    sharpness  = random.uniform(0.92, 1.08)

    img = ImageEnhance.Brightness(base).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(color)
    img = ImageEnhance.Sharpness(img).enhance(sharpness)

    if random.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.7)))

    img.save(f"static/images/image_{i:02d}.jpg", quality=85, optimize=False)

print("50 imagens geradas.")

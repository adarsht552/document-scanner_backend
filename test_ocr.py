
from pathlib import Path

from app.services.ocr_service import extract_text_from_image


# Put your test JPG image in the project root
image_path = Path("img.jpg")

if not image_path.exists():
    print("Image not found:", image_path.resolve())
else:
    image_content = image_path.read_bytes()

    extracted_text = extract_text_from_image(image_content)

    print("\n========== OCR RESULT ==========\n")
    print(extracted_text)
    print("\n================================")

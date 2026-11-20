
import cv2
import pytesseract
import numpy as np
from PIL import Image
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_image(file_content: bytes) -> str:
    try:
        # Convert uploaded bytes into an OpenCV image
        image_array = np.frombuffer(file_content, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Invalid image file")

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Improve local contrast
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )
        enhanced = clahe.apply(gray)

        # Reduce background noise
        denoised = cv2.fastNlMeansDenoising(
            enhanced,
            None,
            10,
            7,
            21
        )

        # Apply adaptive thresholding
        processed = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11
        )

        # Run OCR
        extracted_text = pytesseract.image_to_string(
            processed,
            lang="eng",
            config="--oem 3 --psm 6"
        )

        return extracted_text.strip()

    except Exception as exc:
        print("OCR ERROR:", repr(exc))
        raise Exception("Failed to extract text from image")

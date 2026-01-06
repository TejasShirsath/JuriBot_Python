"""
OCR Utilities for JuriBot
Handles text extraction from PDFs, images, and scanned documents
"""

import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import io
import os
from dotenv import load_dotenv
load_dotenv()
import tempfile

# Configure Tesseract path (uncomment and modify if needed)
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")
def extract_text_from_image(image_file):
    """
    Extract text from an image file using Tesseract OCR

    Args:
        image_file: UploadedFile object or PIL Image

    Returns:
        str: Extracted text
    """
    try:
        if hasattr(image_file, "read"):
            # If it's a file-like object
            image = Image.open(image_file)
        else:
            image = image_file

        # Perform OCR
        text = pytesseract.image_to_string(image, lang="eng+hin")
        return text.strip()
    except Exception as e:
        return f"Error during OCR: {str(e)}"


def extract_text_from_pdf_ocr(pdf_file):
    """
    Extract text from a PDF using OCR (for scanned PDFs)

    Args:
        pdf_file: UploadedFile object

    Returns:
        str: Extracted text from all pages
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_path = tmp_file.name

        # Convert PDF pages to images
        try:
            images = convert_from_path(tmp_path)
        except Exception as e:
            # Try with poppler path if conversion fails
            # Uncomment and modify if needed:
            # poppler_path = r'C:\path\to\poppler\bin'
            # images = convert_from_path(tmp_path, poppler_path=poppler_path)
            raise e

        # Extract text from each page
        full_text = []
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang="eng+hin")
            full_text.append(f"--- Page {i+1} ---\n{text}")

        # Clean up temporary file
        os.unlink(tmp_path)

        return "\n\n".join(full_text)
    except Exception as e:
        return f"Error during PDF OCR: {str(e)}"


def is_scanned_pdf(pdf_text, threshold=50):
    """
    Determine if a PDF is scanned (has little to no text)

    Args:
        pdf_text: Text extracted from PDF
        threshold: Minimum character count for non-scanned PDF

    Returns:
        bool: True if likely scanned, False otherwise
    """
    clean_text = pdf_text.strip()
    return len(clean_text) < threshold


def preprocess_image_for_ocr(image):
    """
    Preprocess image to improve OCR accuracy

    Args:
        image: PIL Image object

    Returns:
        PIL Image: Preprocessed image
    """
    from PIL import ImageEnhance, ImageFilter

    # Convert to grayscale
    image = image.convert("L")

    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)

    return image


def extract_text_with_confidence(image_file):
    """
    Extract text with confidence scores from image

    Args:
        image_file: UploadedFile object or PIL Image

    Returns:
        dict: {'text': str, 'confidence': float, 'data': dict}
    """
    try:
        if hasattr(image_file, "read"):
            image = Image.open(image_file)
        else:
            image = image_file

        # Get detailed data
        data = pytesseract.image_to_data(
            image, lang="eng+hin", output_type=pytesseract.Output.DICT
        )

        # Extract text
        text = pytesseract.image_to_string(image, lang="eng+hin")

        # Calculate average confidence
        confidences = [int(conf) for conf in data["conf"] if conf != "-1"]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {"text": text.strip(), "confidence": avg_confidence, "data": data}
    except Exception as e:
        return {"text": "", "confidence": 0, "error": str(e)}

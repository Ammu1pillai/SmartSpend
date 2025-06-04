# SmartSpendAnalyser/backend/app/ocr_utils.py
import pytesseract
from PIL import Image
import os

# --- IMPORTANT: Tesseract Path Configuration ---
# If Tesseract is not in your system's PATH, uncomment and modify the line below
# to point to the full path of your tesseract executable.
# Example for Windows: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Example for macOS/Linux if installed in a non-standard location: pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

# Try to get it from an environment variable first, if defined
TESSERACT_PATH = os.getenv("TESSERACT_CMD_PATH")

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print(f"Pytesseract Tesseract CMD set to: {TESSERACT_PATH}")
else:
    # --- START OF ADDITION/CHANGE ---
    # Fallback to a local path if TESSERACT_CMD_PATH environment variable is not set.
    # This assumes tesseract.exe is located at SmartSpendAnalyser/backend/app/tesseract_installed/tesseract.exe
    # relative to where this ocr_utils.py file is.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tesseract_installed_dir = os.path.join(current_dir, 'tesseract_installed')
    local_tesseract_executable_path = os.path.join(tesseract_installed_dir, 'tesseract.exe')

    if os.path.exists(local_tesseract_executable_path):
        pytesseract.pytesseract.tesseract_cmd = local_tesseract_executable_path
        print(f"TESSERACT_CMD_PATH environment variable not set. Using local Tesseract installation: {local_tesseract_executable_path}")
    else:
        print("TESSERACT_CMD_PATH environment variable not set, and local 'tesseract_installed' not found.")
        print("Pytesseract will rely on system PATH. Please ensure Tesseract is installed and in PATH.")
    # --- END OF ADDITION/CHANGE ---

def extract_text_from_image(image_path):
    """
    Extracts text from an image using Tesseract OCR.
    Args:
        image_path (str): The path to the image file.
    Returns:
        str: The extracted text.
    Raises:
        pytesseract.TesseractNotFoundError: If Tesseract is not installed or not in PATH.
        Exception: For other errors during image processing or OCR.
    """
    try:
        img = Image.open(image_path)
        # You can add language parameter here, e.g., lang='eng+fra'
        text = pytesseract.image_to_string(img)
        return text
    except pytesseract.TesseractNotFoundError as e:
        print(f"Tesseract OCR engine not found. Please install it: {e}")
        raise e
    except Exception as e:
        print(f"Error processing image {image_path} for OCR: {e}")
        raise e

if __name__ == '__main__':
    # Simple test: Create a dummy image and try to OCR it
    try:
        from PIL import ImageDraw, ImageFont
        dummy_image_path = "test_receipt.png"
        img_width, img_height = 400, 200
        img = Image.new('RGB', (img_width, img_height), color = (255, 255, 255)) # White background
        d = ImageDraw.Draw(img)

        # Try to use a default font or specify a path
        try:
            # Example font path for Linux/macOS: '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
            # Example font path for Windows: 'C:/Windows/Fonts/arial.ttf'
            # You might need to find a font file on your system
            font = ImageFont.load_default() # Use default if no specific font is found
            # Or try a common path:
            # font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" # Linux/macOS
            # font = ImageFont.truetype(font_path, 20)
        except Exception:
            font = ImageFont.load_default()

        d.text((50,50), "Total: $123.45", fill=(0,0,0), font=font)
        d.text((50,80), "Date: 2024-06-03", fill=(0,0,0), font=font)
        d.text((50,110), "Store: Dummy Mart", fill=(0,0,0), font=font)

        img.save(dummy_image_path)
        print(f"Created dummy image: {dummy_image_path}")

        extracted = extract_text_from_image(dummy_image_path)
        print("\n--- Extracted Text from Dummy Image ---")
        print(extracted)

        os.remove(dummy_image_path)
        print(f"Removed dummy image: {dummy_image_path}")

    except pytesseract.TesseractNotFoundError:
        print("Tesseract not found. Please install Tesseract OCR and ensure it's in your system's PATH.")
        print("Or set TESSERACT_CMD_PATH environment variable or pytesseract.pytesseract.tesseract_cmd in ocr_utils.py.")
    except Exception as e:
        print(f"An error occurred during OCR test: {e}")
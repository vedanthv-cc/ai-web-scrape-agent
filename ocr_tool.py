import time
from playwright.sync_api import sync_playwright
from PIL import Image
import pytesseract

def ocr_resized_image(image_path, scale_factor=0.5):
    """
    Resizes the image and applies OCR.
    :param image_path: Path to the input image.
    :param scale_factor: Scaling factor.
    :return: OCR extracted text.
    """
    image = Image.open(image_path)
    new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
    # Optionally, save the resized image for debugging
    resized_image.save("resized.png")
    return pytesseract.image_to_string(resized_image)

def capture_screenshot(url, screenshot_path):
    """
    Captures a full-page screenshot using Playwright.
    :param url: URL to capture.
    :param screenshot_path: File path to save the screenshot.
    """
    with sync_playwright() as p:
        # browser = p.chromium.launch(
        #     headless=True,
        #     args=["--disable-http2", "--disable-blink-features=AutomationControlled"]
        # )
        # context_args = {"viewport": {"width": 1280, "height": 720}}
        # context = browser.new_context(**context_args)
        browser = p.chromium.launch(headless=True,args=["--disable-blink-features=AutomationControlled"])

        # Create a browser context with a specific viewport size (e.g., 1280x720)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/105.0.0.0 Safari/537.36"
            ),
            viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        # Anti-detection script
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)
        try:
            page.goto(url, wait_until="load")
            page.wait_for_timeout(3000)  # Wait for lazy-loaded content
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved as {screenshot_path}")
        except Exception as e:
            print(f"Error capturing screenshot for {url}: {e}")
        finally:
            page.close()
            context.close()
            browser.close()

def extract_text_from_url(url, scale_factor=0.8, screenshot_path=None):
    """
    Captures a webpage screenshot and extracts text using OCR.
    :param url: URL to capture.
    :param scale_factor: Scaling factor for OCR.
    :param screenshot_path: Optional custom path; if not provided a unique one is generated.
    :return: A tuple (extracted_text, screenshot_path)
    """
    # Create a unique filename if not provided
    if not screenshot_path:
        screenshot_path = f"screenshot_{int(time.time())}.png"
    capture_screenshot(url, screenshot_path)
    extracted_text = ocr_resized_image(screenshot_path, scale_factor)
    return extracted_text, screenshot_path

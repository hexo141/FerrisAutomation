import PIL.ImageGrab
import base64
import io
import os
from datetime import datetime


def capture_screen(region=None):
    """Capture a screenshot of the screen or a specific region.

    Args:
        region: Tuple of (x, y, width, height) or None for full screen.

    Returns:
        PIL Image object of the captured screenshot.

    Raises:
        Exception: If screenshot capture fails.
    """
    try:
        if region is None:
            image = PIL.ImageGrab.grab()
        else:
            x, y, width, height = region
            image = PIL.ImageGrab.grab(bbox=(x, y, x + width, y + height))
        return image
    except Exception as e:
        raise Exception(f"Failed to capture screenshot: {e}")


def image_to_base64(image, format="PNG"):
    """Convert a PIL Image to a base64 encoded string.

    Args:
        image: PIL Image object.
        format: Image format for encoding (default: "PNG").

    Returns:
        Base64 encoded string without data URI prefix.

    Raises:
        Exception: If encoding fails.
    """
    try:
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode("utf-8")
        return encoded
    except Exception as e:
        raise Exception(f"Failed to convert image to base64: {e}")


def save_screenshot(image, filepath=None):
    """Save a PIL Image to a file.

    Args:
        image: PIL Image object.
        filepath: Path to save the image. If None, saves to default location with timestamp.

    Returns:
        String filepath where the screenshot was saved.

    Raises:
        Exception: If saving fails.
    """
    try:
        if filepath is None:
            os.makedirs("screenshots", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join("screenshots", f"screenshot_{timestamp}.png")

        image.save(filepath)
        return filepath
    except Exception as e:
        raise Exception(f"Failed to save screenshot: {e}")

import requests
import base64
import io
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OmniParser:
    def __init__(self, base_url="http://localhost:8000", timeout=30, max_retries=3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    def parse_screenshot(self, image):
        import PIL.Image

        if isinstance(image, PIL.Image.Image):
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        elif isinstance(image, str):
            image_base64 = image
        else:
            raise ValueError("Image must be a PIL Image or base64 string")

        return self.parse_screenshot_base64(image_base64)

    def parse_screenshot_base64(self, image_base64):
        payload = {"base64_image": image_base64}
        headers = {"Content-Type": "application/json"}

        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(
                    f"{self.base_url}/parse",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                logger.warning(f"Connection error (attempt {attempt}/{self.max_retries}): {e}")
            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"Request timed out (attempt {attempt}/{self.max_retries}): {e}")
            except requests.exceptions.HTTPError as e:
                last_exception = e
                logger.error(f"HTTP error: {e}")
                raise
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"Request failed (attempt {attempt}/{self.max_retries}): {e}")

            if attempt < self.max_retries:
                backoff = 2 ** (attempt - 1)
                logger.info(f"Retrying in {backoff} seconds...")
                time.sleep(backoff)

        raise Exception(
            f"Failed to parse screenshot after {self.max_retries} attempts. Last error: {last_exception}"
        )

    def parse_with_details(self, image):
        result = self.parse_screenshot(image)
        return self.format_parsed_result(result)

    def is_available(self):
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            try:
                response = requests.get(
                    self.base_url,
                    timeout=5
                )
                return response.status_code < 500
            except requests.exceptions.RequestException:
                return False

    def format_parsed_result(self, result):
        if not result:
            return "No parsing result available."

        lines = []
        lines.append("=" * 50)
        lines.append("OmniParser Result")
        lines.append("=" * 50)

        parsed_elements = result.get("parsed", [])

        if isinstance(parsed_elements, list) and parsed_elements:
            lines.append(f"\nTotal elements detected: {len(parsed_elements)}")
            lines.append("-" * 50)

            ui_elements = []
            text_content = []
            interactive_elements = []

            for i, element in enumerate(parsed_elements):
                if isinstance(element, dict):
                    elem_type = element.get("type", "unknown")
                    elem_text = element.get("text", element.get("content", ""))
                    bbox = element.get("bbox", element.get("box", None))
                    description = element.get("description", "")

                    ui_elements.append(element)

                    if elem_text:
                        text_content.append(elem_text)

                    if elem_type.lower() in ("button", "link", "input", "checkbox", "radio", "dropdown", "clickable"):
                        interactive_elements.append({
                            "type": elem_type,
                            "text": elem_text,
                            "bbox": bbox
                        })

            if ui_elements:
                lines.append("\nDetected UI Elements:")
                for i, elem in enumerate(ui_elements[:50]):
                    if isinstance(elem, dict):
                        elem_type = elem.get("type", "unknown")
                        elem_text = elem.get("text", elem.get("content", ""))
                        bbox = elem.get("bbox", elem.get("box", None))
                        lines.append(f"  {i+1}. [{elem_type}] {elem_text}")
                        if bbox:
                            lines.append(f"     Position: {bbox}")
                if len(ui_elements) > 50:
                    lines.append(f"  ... and {len(ui_elements) - 50} more elements")

            if text_content:
                lines.append("\nText Content Found:")
                combined_text = " | ".join(text_content)
                if len(combined_text) > 500:
                    lines.append(f"  {combined_text[:500]}...")
                else:
                    lines.append(f"  {combined_text}")

            if interactive_elements:
                lines.append("\nInteractive Elements:")
                for elem in interactive_elements:
                    bbox_str = f" at {elem['bbox']}" if elem['bbox'] else ""
                    lines.append(f"  - [{elem['type']}] {elem['text']}{bbox_str}")
        else:
            lines.append("\nNo elements detected in the screenshot.")

        for key, value in result.items():
            if key not in ("parsed", "screenshot_parsed"):
                if isinstance(value, (str, int, float, bool)):
                    lines.append(f"\n{key}: {value}")

        summary = "\n".join(lines)

        if len(summary) > 2000:
            summary = summary[:2000] + "\n... (output truncated)"

        return summary

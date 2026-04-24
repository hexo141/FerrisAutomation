import requests
import json
import logging
import os
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are an AI computer control assistant. Your task is to analyze the current screen state and determine the appropriate actions to perform.

Available action types:
- click: Click at specific coordinates
  Parameters: {"x": int, "y": int, "button": "left"|"right"}
- type: Type text
  Parameters: {"text": string}
- scroll: Scroll the screen
  Parameters: {"direction": "up"|"down"|"left"|"right", "amount": int}
- key: Press a keyboard key or combination
  Parameters: {"keys": string} (e.g., "ctrl+c", "enter")
- wait: Wait for a specified duration
  Parameters: {"duration": float} (in seconds)
- screenshot: Take a screenshot to analyze the current state
  Parameters: {}

When responding, always provide your analysis and the action in JSON format:
{
  "analysis": "Brief explanation of what you see and why you're taking this action",
  "action": {
    "type": "click"|"type"|"scroll"|"key"|"wait"|"screenshot",
    "parameters": {}
  }
}

Be precise with coordinates and always explain your reasoning."""


class LLMClient:
    def __init__(self, api_key, base_url="https://api.openai.com/v1", model="gpt-4o", max_tokens=4096):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.max_tokens = max_tokens
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def chat_completion(self, messages, temperature=0.7, max_tokens=None):
        if max_tokens is None:
            max_tokens = self.max_tokens

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse API response: {e}")
            raise

    def chat_with_image(self, system_prompt, user_text, image_base64, temperature=0.7):
        image_url = f"data:image/png;base64,{image_base64}"

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            }
        ]

        return self.chat_completion(messages, temperature=temperature)

    def stream_chat(self, messages, temperature=0.7):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.max_tokens,
            "stream": True
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                stream=True
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            parsed = json.loads(data)
                            delta = parsed["choices"][0].get("delta", {})
                            content = delta.get("content")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
        except requests.exceptions.RequestException as e:
            logger.error(f"Streaming API request failed: {e}")
            raise

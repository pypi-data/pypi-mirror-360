from typing import Optional, List, Union
import requests
import io
import webbrowser
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
from rawa_bots.exceptions import GeminiError, AuthenticationError, InvalidModelError, ImageGenNotAllowedError, ImageGenAPIError

class OpenAIBot:
    """
    High-level interface for OpenAI's API chatbot.
    Supports conversational and single-turn modes, and (optionally) image generation.
    Uses direct HTTP requests to OpenAI API.
    """
    DEFAULT_TEXT_MODEL = "gpt-3.5-turbo"
    DEFAULT_IMAGE_MODEL = "dall-e-3"
    OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
    OPENAI_IMAGE_URL = "https://api.openai.com/v1/images/generations"

    def __init__(self, api_key, model_name=None, system_prompt=None, conversational=False, allow_image_gen=False, **kwargs):
        self.api_key = api_key
        self.model_name = model_name or self.DEFAULT_TEXT_MODEL
        self.system_prompt = system_prompt
        self.conversational = conversational
        self.allow_image_gen = allow_image_gen
        self.generation_config = kwargs
        self._history = []
        self._validate_api_key()
        if self.conversational:
            self._history = []

    def _validate_api_key(self):
        if not self.api_key or not isinstance(self.api_key, str):
            raise AuthenticationError("A valid OpenAI API key must be provided.")

    def ask(self, prompt: str) -> str:
        url = self.OPENAI_CHAT_URL
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if self.conversational and self._history:
            for user, bot in self._history:
                messages.append({"role": "user", "content": user})
                messages.append({"role": "assistant", "content": bot})
        messages.append({"role": "user", "content": prompt})
        data = {
            "model": self.model_name,
            "messages": messages
        }
        if self.generation_config:
            data.update(self.generation_config)
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed.")
            if resp.status_code == 404:
                raise InvalidModelError(f"Model '{self.model_name}' not found.")
            if not resp.ok:
                raise GeminiError(f"OpenAI API error: {resp.status_code} {resp.text}")
            result = resp.json()
            choices = result.get("choices", [])
            if not choices:
                raise GeminiError("No response choices from OpenAI API.")
            text = choices[0]["message"]["content"]
            if self.conversational:
                self._history.append((prompt, text))
            return text
        except (requests.RequestException, KeyError, IndexError) as e:
            raise GeminiError(f"Error during ask: {e}")

    def reset(self):
        self._history = []

    def generate_image(self, prompt: str, n: int = 1, output_path: Optional[str] = None, show: bool = False) -> Union[str, List[str]]:
        if not self.allow_image_gen:
            raise ImageGenNotAllowedError("Image generation is not enabled for this bot instance.")
        url = self.OPENAI_IMAGE_URL
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.DEFAULT_IMAGE_MODEL,
            "prompt": prompt,
            "n": n,
            "size": "1024x1024",
            "response_format": "b64_json"
        }
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=60)
            if resp.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed.")
            if resp.status_code == 404:
                raise InvalidModelError(f"Image model '{self.DEFAULT_IMAGE_MODEL}' not found.")
            if not resp.ok:
                raise ImageGenAPIError(f"OpenAI API error: {resp.status_code} {resp.text}")
            result = resp.json()
            images = result.get("data", [])
            if not images:
                raise ImageGenAPIError("No image data from OpenAI API.")
            image_paths = []
            for idx, img_obj in enumerate(images):
                img_b64 = img_obj.get("b64_json")
                if img_b64:
                    import base64
                    img_data = base64.b64decode(img_b64)
                    if output_path:
                        save_path = self._save_image_file(img_data, output_path, idx, n, prefix="openai_image")
                        image_paths.append(save_path)
                        if show:
                            self._show_image_file(save_path)
                    elif show:
                        if PIL_AVAILABLE:
                            img = Image.open(io.BytesIO(img_data))
                            img.show()
                        else:
                            raise ImageGenAPIError("PIL is required to show images from memory. Please install Pillow.")
                    else:
                        save_path = self._save_image_file(img_data, None, idx, n, prefix="openai_image")
                        image_paths.append(save_path)
            if not image_paths and not show:
                raise ImageGenAPIError("Image generation response did not contain image data.")
            if not output_path and not show:
                return image_paths[0] if n == 1 else image_paths
            if output_path:
                return image_paths[0] if n == 1 else image_paths
            raise ImageGenAPIError("Unexpected error: image generation did not return data.")
        except (requests.RequestException, KeyError, IndexError) as e:
            raise ImageGenAPIError(f"Image generation failed: {e}")

    def _save_image_file(self, img_data, output_path, idx, n, prefix="openai_image"):
        import os
        if output_path:
            if os.path.isdir(output_path):
                base = os.path.join(output_path, prefix)
                ext = ".png"
            else:
                base, ext = os.path.splitext(output_path)
                if not ext:
                    ext = ".png"
        else:
            base = prefix
            ext = ".png"
        if n == 1:
            save_path = f"{base}{ext}"
        else:
            save_path = f"{base}_{idx+1}{ext}"
        with open(save_path, "wb") as f:
            f.write(img_data)
        return save_path

    def _show_image_file(self, path):
        if PIL_AVAILABLE:
            try:
                img = Image.open(path)
                img.show()
            except Exception:
                import os
                webbrowser.open(f"file://{os.path.abspath(path)}")
        else:
            import os
            webbrowser.open(f"file://{os.path.abspath(path)}") 
import os
import io
import webbrowser
import requests
from typing import Optional, Union, List
from rawa_bots.exceptions import GeminiError, AuthenticationError, InvalidModelError, ImageGenNotAllowedError, ImageGenAPIError

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class GeminiBot:
    """
    High-level interface for Google's Gemini API chatbot.
    Supports conversational and single-turn modes, and (optionally) image generation.
    Uses direct HTTP requests to Gemini Developer API.
    """
    DEFAULT_TEXT_MODEL = "gemini-2.0-flash"
    DEFAULT_IMAGE_MODEL = "imagen-3.0-generate-002"
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    GEMINI_LIST_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

    def __init__(self, api_key, model_name=None, system_prompt=None, conversational=False, allow_image_gen=False, **kwargs):
        """
        Initialize the GeminiBot.
        Args:
            api_key (str): Gemini API key.
            model_name (str, optional): Model name (e.g., 'gemini-2.0-flash'). Defaults to 'gemini-2.0-flash'.
            system_prompt (str, optional): System prompt/instruction.
            conversational (bool): If True, maintains conversation history.
            allow_image_gen (bool): If True, enables image generation features.
            **kwargs: Advanced generation parameters (temperature, top_p, etc).
        """
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
            raise AuthenticationError("A valid Gemini API key must be provided.")

    def ask(self, prompt: str) -> str:
        """
        Send a prompt to the Gemini model and return the response.
        Args:
            prompt (str): User input.
        Returns:
            str: Model response.
        """
        url = self.GEMINI_API_URL.format(model=self.model_name, api_key=self.api_key)
        headers = {"Content-Type": "application/json"}
        messages = []
        # Prepend system prompt to user prompt if present
        if self.system_prompt:
            prompt = f"{self.system_prompt}\n{prompt}"
        if self.conversational and self._history:
            for user, bot in self._history:
                messages.append({"role": "user", "parts": [{"text": user}]})
                messages.append({"role": "model", "parts": [{"text": bot}]})
        messages.append({"role": "user", "parts": [{"text": prompt}]})
        data = {
            "contents": messages,
        }
        # Add advanced config if present
        if self.generation_config:
            data["generationConfig"] = self.generation_config
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed.")
            if resp.status_code == 404:
                raise InvalidModelError(f"Model '{self.model_name}' not found.")
            if not resp.ok:
                raise GeminiError(f"Gemini API error: {resp.status_code} {resp.text}")
            result = resp.json()
            # Extract the text from the response
            candidates = result.get("candidates", [])
            if not candidates:
                raise GeminiError("No response candidates from Gemini API.")
            text = candidates[0]["content"]["parts"][0]["text"]
            if self.conversational:
                self._history.append((prompt, text))
            return text
        except (requests.RequestException, KeyError, IndexError) as e:
            raise GeminiError(f"Error during ask: {e}")

    def reset(self):
        """
        Reset the conversation history (for conversational mode).
        """
        self._history = []

    def generate_image(self, prompt: str, n: int = 1, output_path: Optional[str] = None, show: bool = False) -> Union[str, List[str]]:
        """
        Generate image(s) from a prompt using Gemini's image generation API.
        Args:
            prompt (str): The image prompt.
            n (int): Number of images to generate.
            output_path (str, optional): Path to save the image(s). If n > 1, will save as output_path_1.png, output_path_2.png, etc.
            show (bool): If True, open the image(s) after saving.
        Returns:
            str or List[str]: Image URL(s) or file path(s).
        Raises:
            ImageGenNotAllowedError: If image generation is not enabled.
            ImageGenAPIError: If the image generation API fails.
        """
        if not self.allow_image_gen:
            raise ImageGenNotAllowedError("Image generation is not enabled for this bot instance.")
        # Use the endpoint and model from the provided curl command
        image_model = "gemini-2.0-flash-preview-image-generation"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{image_model}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "contents": [{
                "parts": [
                    {"text": prompt}
                ]
            }],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "candidateCount": n}
        }
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=60)
            response_log = []
            response_log.append("--- Gemini Image API HTTP Response ---\n")
            response_log.append(f"Status: {resp.status_code}\n")
            response_log.append(f"Headers: {dict(resp.headers)}\n")
            response_log.append(f"Body: {resp.text}\n")
            response_log.append("--- END RESPONSE ---\n")
            with open("gemini_image_response.txt", "w", encoding="utf-8") as f:
                f.writelines(response_log)
            print("Gemini image API response written to gemini_image_response.txt")
            if resp.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed.")
            if resp.status_code == 404:
                raise InvalidModelError(f"Image model '{image_model}' not found.")
            if not resp.ok:
                raise ImageGenAPIError(f"Gemini API error: {resp.status_code} {resp.text}")
            result = resp.json()
            print("Image API raw response:", result)  # Debug print
            candidates = result.get("candidates", [])
            if not candidates:
                raise ImageGenAPIError("No image candidates from Gemini API.")
            image_paths = []
            for idx, candidate in enumerate(candidates):
                # Look for any part with inlineData (base64 image)
                parts = candidate["content"]["parts"]
                img_saved = False
                for part in parts:
                    img_b64 = part.get("inlineData", {}).get("data")
                    if img_b64:
                        import base64
                        img_data = base64.b64decode(img_b64)
                        save_path = self._save_image_file(img_data, output_path, idx, n)
                        image_paths.append(save_path)
                        img_saved = True
                        if show:
                            self._show_image_file(save_path)
                        break  # Only save the first image per candidate
                if not img_saved:
                    # Fallback to previous logic for url/fileData/uri
                    part = parts[0]
                    img_url = part.get("fileData", {}).get("fileUri") or part.get("url")
                    if not img_url and "uri" in part:
                        img_url = part["uri"]
                    if img_url:
                        if output_path:
                            r = requests.get(img_url)
                            img_data = r.content
                            save_path = self._save_image_file(img_data, output_path, idx, n)
                            image_paths.append(save_path)
                            if show:
                                self._show_image_file(save_path)
                        else:
                            image_paths.append(img_url)
                            if show:
                                webbrowser.open(img_url)
            if not image_paths:
                raise ImageGenAPIError("Image generation response did not contain image data.")
            if not output_path:
                return image_paths[0] if n == 1 else image_paths
            return image_paths[0] if n == 1 else image_paths
        except (requests.RequestException, KeyError, IndexError) as e:
            raise ImageGenAPIError(f"Image generation failed: {e}")

    def list_available_models(self) -> List[str]:
        """
        List all available model names for the current API key.
        Returns:
            List[str]: List of model names.
        """
        url = self.GEMINI_LIST_MODELS_URL.format(api_key=self.api_key)
        try:
            resp = requests.get(url, timeout=20)
            if not resp.ok:
                return []
            result = resp.json()
            return [m["name"].split("/")[-1] for m in result.get("models", [])]
        except Exception:
            return []

    def _save_image_file(self, img_data, output_path, idx, n):
        import os
        if output_path:
            # If output_path is a directory, save inside it with default name
            if os.path.isdir(output_path):
                base = os.path.join(output_path, "gemini_image")
                ext = ".png"
            else:
                base, ext = os.path.splitext(output_path)
                if not ext:
                    ext = ".png"
        else:
            # Save in CWD with default name
            base = "gemini_image"
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
                webbrowser.open(f"file://{os.path.abspath(path)}")
        else:
            webbrowser.open(f"file://{os.path.abspath(path)}") 
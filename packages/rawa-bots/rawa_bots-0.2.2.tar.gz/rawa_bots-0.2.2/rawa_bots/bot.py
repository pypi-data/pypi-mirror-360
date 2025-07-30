import os
import io
import webbrowser
from typing import Optional, Union, List
from google import genai
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
    """
    DEFAULT_TEXT_MODEL = "gemini-2.0-flash"
    DEFAULT_IMAGE_MODEL = "imagen-4.0-generate-preview-06-06imagen-4.0-ultra-generate-preview-06-06"

    def __init__(self, api_key, model_name=None, system_prompt=None, conversational=False, allow_image_gen=False, **kwargs):
        """
        Initialize the GeminiBot.
        Args:
            api_key (str): Gemini API key.
            model_name (str, optional): Model name (e.g., 'gemini-2.0-flash' or 'models/gemini-2.0-flash'). Defaults to 'gemini-2.0-flash'.
            system_prompt (str, optional): System prompt/instruction.
            conversational (bool): If True, maintains conversation history.
            allow_image_gen (bool): If True, enables image generation features.
            **kwargs: Advanced generation parameters (temperature, top_p, etc).
        """
        self.api_key = api_key
        self.user_model_name = model_name or self.DEFAULT_TEXT_MODEL  # Use default if not specified
        self.system_prompt = system_prompt
        self.conversational = conversational
        self.allow_image_gen = allow_image_gen
        self.generation_config = kwargs
        self._client = None
        self._chat = None
        self._history = []
        self._init_client()
        self.model_name = self._resolve_model_name(self.user_model_name)
        self._validate_model_name()
        if self.conversational:
            self._start_chat()

    def _init_client(self):
        try:
            self._client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise AuthenticationError(f"Failed to authenticate with Gemini API: {e}")

    def _resolve_model_name(self, model_name):
        # Accept both 'gemini-1.5-pro' and 'models/gemini-1.5-pro'
        if model_name.startswith("models/"):
            return model_name
        # Try to find the full name from the available models
        try:
            available_models = [m.name for m in self._client.models.list()]
            for full_name in available_models:
                if full_name.split("/", 1)[-1] == model_name:
                    return full_name
        except Exception:
            pass  # Fallback below if listing fails
        # Default to prepending 'models/'
        return f"models/{model_name}"

    def _validate_model_name(self):
        try:
            available_models = [m.name for m in self._client.models.list()]
            if self.model_name not in available_models:
                raise InvalidModelError(
                    f"Model '{self.user_model_name}' not found.\nAvailable: {[m.split('/', 1)[-1] for m in available_models]}\n"
                    f"Tip: Use a valid Gemini model name, e.g., 'gemini-1.5-pro' or 'models/gemini-1.5-pro'."
                )
        except InvalidModelError:
            raise
        except Exception as e:
            raise GeminiError(f"Failed to validate model: {e}")

    def _start_chat(self):
        try:
            self._chat = self._client.chats.create(model=self.model_name)
            self._history = []
        except Exception as e:
            raise GeminiError(f"Failed to start chat session: {e}")

    def ask(self, prompt: str) -> str:
        """
        Send a prompt to the Gemini model and return the response.
        Args:
            prompt (str): User input.
        Returns:
            str: Model response.
        """
        try:
            config = self._build_config()
            if self.conversational:
                if self._chat is None:
                    self._start_chat()
                response = self._chat.send_message(prompt, config=config)
                self._history.append((prompt, response.text))
                return response.text
            else:
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                return response.text
        except genai.errors.APIError as e:
            if e.code == 401:
                raise AuthenticationError("Invalid API key or authentication failed.")
            elif e.code == 404:
                raise InvalidModelError(f"Model '{self.user_model_name}' not found.")
            else:
                raise GeminiError(f"Gemini API error: {e}")
        except Exception as e:
            raise GeminiError(f"Error during ask: {e}")

    def _build_config(self):
        config = dict(self.generation_config) if self.generation_config else {}
        if self.system_prompt:
            config['system_instruction'] = self.system_prompt
        return config

    def reset(self):
        """
        Reset the conversation history (for conversational mode).
        """
        if self.conversational:
            self._start_chat()
        self._history = []

    # Placeholder for future async support
    async def ask_async(self, prompt: str) -> str:
        raise NotImplementedError("Async support coming soon.")

    def generate_image(self, prompt: str, resolution: str = "1024x1024", n: int = 1, output_path: Optional[str] = None, show: bool = False) -> Union[str, List[str]]:
        """
        Generate image(s) from a prompt using Gemini's image generation API.
        Args:
            prompt (str): The image prompt.
            resolution (str): Image resolution (e.g., '1024x1024'). (Note: Not all Gemini models support this parameter. Currently ignored.)
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
        try:
            # Find an image generation model
            available_models = [m.name for m in self._client.models.list()]
            image_models = [m for m in available_models if "image" in m or "imagen" in m]
            # Prefer the default image model if available
            image_model = None
            for m in image_models:
                if m.endswith(self.DEFAULT_IMAGE_MODEL) or m == self.DEFAULT_IMAGE_MODEL or m.split("/", 1)[-1] == self.DEFAULT_IMAGE_MODEL:
                    image_model = m
                    break
            if not image_model:
                image_model = image_models[0] if image_models else None
            if not image_model:
                raise ImageGenAPIError("No image generation model available in your Gemini account.")
            # Only pass valid config keys. 'candidate_count' is supported. 'image_resolution' is not.
            config = {"candidate_count": n}
            # Future: Add valid config keys for image size if Gemini API supports it.
            response = self._client.models.generate_content(
                model=image_model,
                contents=prompt,
                config=config
            )
            # Try to extract image URLs or data from the response
            image_paths = []
            if hasattr(response, "generated_images"):
                images = response.generated_images
                for idx, img_obj in enumerate(images):
                    img_data = None
                    img_url = getattr(img_obj.image, "url", None)
                    if img_url:
                        # Download the image if output_path is set, else just return the URL
                        if output_path:
                            import requests
                            r = requests.get(img_url)
                            img_data = r.content
                        else:
                            image_paths.append(img_url)
                            continue
                    else:
                        # If not a URL, try to get bytes directly
                        img_data = getattr(img_obj.image, "data", None) or img_obj.image
                    # Save to file if requested
                    if output_path and img_data:
                        if n == 1:
                            save_path = output_path
                        else:
                            base, ext = os.path.splitext(output_path)
                            save_path = f"{base}_{idx+1}{ext or '.png'}"
                        with open(save_path, "wb") as f:
                            f.write(img_data)
                        image_paths.append(save_path)
                        if show:
                            self._show_image_file(save_path)
                    elif show and img_url:
                        webbrowser.open(img_url)
                if not output_path:
                    # If not saving, return URLs or data
                    return image_paths[0] if n == 1 else image_paths
                return image_paths[0] if n == 1 else image_paths
            # Fallback: try to find image URLs in response
            if hasattr(response, "text") and response.text.startswith("http"):
                if output_path:
                    import requests
                    r = requests.get(response.text)
                    with open(output_path, "wb") as f:
                        f.write(r.content)
                    if show:
                        self._show_image_file(output_path)
                    return output_path
                if show:
                    webbrowser.open(response.text)
                return response.text
            raise ImageGenAPIError("Image generation response did not contain image data.")
        except ImageGenAPIError:
            raise
        except Exception as e:
            raise ImageGenAPIError(f"Image generation failed: {e}")

    def _show_image_file(self, path):
        if PIL_AVAILABLE:
            try:
                img = Image.open(path)
                img.show()
            except Exception:
                webbrowser.open(f"file://{os.path.abspath(path)}")
        else:
            webbrowser.open(f"file://{os.path.abspath(path)}") 
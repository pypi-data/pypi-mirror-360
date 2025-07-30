from google import genai
from rawa_bots.exceptions import GeminiError, AuthenticationError, InvalidModelError

class GeminiBot:
    """
    High-level interface for Google's Gemini API chatbot.
    Supports conversational and single-turn modes.
    """
    def __init__(self, api_key, model_name, system_prompt=None, conversational=False, **kwargs):
        """
        Initialize the GeminiBot.
        Args:
            api_key (str): Gemini API key.
            model_name (str): Model name (e.g., 'gemini-1.5-pro' or 'models/gemini-1.5-pro').
            system_prompt (str, optional): System prompt/instruction.
            conversational (bool): If True, maintains conversation history.
            **kwargs: Advanced generation parameters (temperature, top_p, etc).
        """
        self.api_key = api_key
        self.user_model_name = model_name  # Store what the user passed
        self.system_prompt = system_prompt
        self.conversational = conversational
        self.generation_config = kwargs
        self._client = None
        self._chat = None
        self._history = []
        self._init_client()
        self.model_name = self._resolve_model_name(model_name)
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
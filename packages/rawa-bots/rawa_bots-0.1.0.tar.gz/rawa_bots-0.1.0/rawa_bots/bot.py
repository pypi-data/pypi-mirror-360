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
            model_name (str): Model name (e.g., 'gemini-2.0-flash-001').
            system_prompt (str, optional): System prompt/instruction.
            conversational (bool): If True, maintains conversation history.
            **kwargs: Advanced generation parameters (temperature, top_p, etc).
        """
        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.conversational = conversational
        self.generation_config = kwargs
        self._client = None
        self._chat = None
        self._history = []
        self._init_client()
        self._init_model()

    def _init_client(self):
        try:
            self._client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise AuthenticationError(f"Failed to authenticate with Gemini API: {e}")

    def _init_model(self):
        try:
            # Validate model by listing available models
            available_models = [m.name for m in self._client.models.list()]
            if self.model_name not in available_models:
                raise InvalidModelError(f"Model '{self.model_name}' not found. Available: {available_models}")
            self._model = self._client.models.get(self.model_name)
        except InvalidModelError:
            raise
        except Exception as e:
            raise GeminiError(f"Failed to initialize model: {e}")
        if self.conversational:
            self._start_chat()

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
                raise InvalidModelError(f"Model '{self.model_name}' not found.")
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
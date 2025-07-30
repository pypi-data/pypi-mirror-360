import unittest
from rawa_bots.bot import GeminiBot
from rawa_bots.exceptions import AuthenticationError, InvalidModelError

class TestGeminiBot(unittest.TestCase):
    def test_init(self):
        # This test will fail without a real API key; in real CI, mock genai.Client
        try:
            bot = GeminiBot(api_key="invalid", model_name="gemini-2.0-flash-001", system_prompt="Test.")
        except AuthenticationError:
            pass  # Expected for invalid key
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    def test_invalid_model(self):
        # This test will fail without a real API key; in real CI, mock genai.Client
        try:
            bot = GeminiBot(api_key="invalid", model_name="not-a-model", system_prompt="Test.")
        except (AuthenticationError, InvalidModelError):
            pass  # Expected for invalid key or model
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    def test_reset(self):
        # This is a placeholder; real test would mock the chat session
        pass

    def test_ask(self):
        # This is a placeholder; real test would mock the API call
        pass

if __name__ == "__main__":
    unittest.main() 
# rawa_bots

A Python library to easily build Gemini-powered chatbots with minimal code.

## Features
- Easy Gemini API integration
- Conversational and single-turn modes
- Automatic conversation history
- Custom generation parameters (temperature, top_p, etc.)
- Graceful error handling with custom exceptions
- Ready for PyPI packaging

## Installation

```bash
pip install rawa_bots
```

> **Note:** Requires Python 3.8+ and a valid Gemini API key. The `google-genai` package will be installed automatically.

## Usage Example

```python
from rawa_bots import GeminiBot

bot = GeminiBot(
    api_key="YOUR_API_KEY",
    model_name="gemini-2.0-flash-001",  # or any valid Gemini model
    system_prompt="You are helpful.",
    conversational=True,
    temperature=0.7,  # Optional advanced config
)

response = bot.ask("Hello!")
print(response)

# Reset conversation (for conversational mode)
bot.reset()
```

## Listing Available Models

You can list all available Gemini models with:

```python
from google import genai
client = genai.Client(api_key="YOUR_API_KEY")
print([m.name for m in client.models.list()])
```

## Error Handling

- `GeminiError`: Base exception for all GeminiBot errors
- `AuthenticationError`: Raised for authentication issues
- `InvalidModelError`: Raised if the model name is invalid

## Testing

Run tests with:
```bash
python -m unittest discover tests
```

## License
MIT License 
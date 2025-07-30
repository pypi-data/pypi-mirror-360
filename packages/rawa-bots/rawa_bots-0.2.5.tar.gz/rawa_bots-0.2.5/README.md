# rawa_bots

A simple Python library for interacting with Google Gemini and OpenAI chat and image generation APIs using direct HTTP requests (no official SDKs required).

## Features
- Unified interface for Gemini and OpenAI bots
- Text and image generation
- Easy to switch between providers
- No official SDKs required (uses `requests`)

## Installation

```bash
pip install -r requirements.txt
# or if using pyproject.toml
pip install .
```

## Requirements
- Python 3.8+
- `requests`
- `Pillow` (for image display)

## Usage

### GeminiBot Example
```python
from rawa_bots import GeminiBot

gemini = GeminiBot(api_key="YOUR_GEMINI_API_KEY", allow_image_gen=True)

# Text generation
response = gemini.ask("Tell me a joke about robots.")
print("GeminiBot says:", response)

# Image generation
image_path = gemini.generate_image(
    "A futuristic cityscape at sunset",
    output_path="gemini_image.png"
)
print("GeminiBot image saved to:", image_path)
```

### OpenAIBot Example
```python
from rawa_bots import OpenAIBot

openai = OpenAIBot(api_key="YOUR_OPENAI_API_KEY", allow_image_gen=True)

# Text generation
response = openai.ask("Tell me a joke about robots.")
print("OpenAIBot says:", response)

# Image generation
image_path = openai.generate_image(
    "A futuristic cityscape at sunset",
    output_path="openai_image.png"
)
print("OpenAIBot image saved to:", image_path)
```

## Error Handling
All errors are raised as custom exceptions (e.g., `AuthenticationError`, `ImageGenAPIError`).

## Switching Providers
Just change the import and class name:
```python
# For Gemini
from rawa_bots import GeminiBot
# For OpenAI
from rawa_bots import OpenAIBot
```

## License
MIT 
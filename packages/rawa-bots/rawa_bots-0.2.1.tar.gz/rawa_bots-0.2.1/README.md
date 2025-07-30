# rawa_bots

A Python library to easily build Gemini-powered chatbots and generate images with minimal code.

## Features
- Easy Gemini API integration
- Conversational and single-turn modes
- Automatic conversation history
- Custom generation parameters (temperature, top_p, etc.)
- Graceful error handling with custom exceptions
- Image generation support (with save and preview options)
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
    # model_name is optional; defaults to 'gemini-2.0-flash' for text, 'gemini-2.0-flash-preview-image-generation' for images
    system_prompt="You are helpful.",
    conversational=True,
    allow_image_gen=True  # Enable image generation
)

# Text chat
print(bot.ask("Hello!"))

# Image generation (returns URL or file path)
img_path = bot.generate_image(
    "A dragon flying over a castle at night",
    output_path="dragon.png",  # Save to file (optional)
    show=True                   # Open image after saving (optional)
)
print("Image saved to:", img_path)
```

## Image Generation API

- `allow_image_gen`: Set to `True` to enable image generation.
- `generate_image(prompt, resolution="1024x1024", n=1, output_path=None, show=False)`
  - `prompt`: The image prompt.
  - `resolution`: Image resolution (default: 1024x1024).
  - `n`: Number of images to generate.
  - `output_path`: If set, saves the image(s) to this path (adds _1, _2, ... if n > 1).
  - `show`: If True, opens the image(s) after saving.
  - Returns: URL(s) or file path(s).

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
- `ImageGenNotAllowedError`: Raised if image generation is not enabled
- `ImageGenAPIError`: Raised for image generation API errors

## Testing

Run tests with:
```bash
python -m unittest discover tests
```

## License
MIT License 
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

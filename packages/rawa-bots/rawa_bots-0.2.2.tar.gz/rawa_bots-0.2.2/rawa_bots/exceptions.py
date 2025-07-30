class GeminiError(Exception):
    """Base exception for rawa_bots."""
    pass

class AuthenticationError(GeminiError):
    """Raised when authentication fails."""
    pass

class InvalidModelError(GeminiError):
    """Raised when an invalid model is specified."""
    pass

class ImageGenNotAllowedError(GeminiError):
    """Raised when image generation is not allowed but attempted."""
    pass

class ImageGenAPIError(GeminiError):
    """Raised for errors from the image generation API."""
    pass 
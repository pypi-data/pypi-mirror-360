class GeminiError(Exception):
    """Base exception for rawa_bots."""
    pass

class AuthenticationError(GeminiError):
    """Raised when authentication fails."""
    pass

class InvalidModelError(GeminiError):
    """Raised when an invalid model is specified."""
    pass 
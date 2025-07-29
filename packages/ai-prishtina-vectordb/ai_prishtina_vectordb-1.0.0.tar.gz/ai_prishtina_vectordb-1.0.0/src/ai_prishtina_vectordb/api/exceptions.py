"""
API-specific exceptions for AI Prishtina VectorDB.
"""

from ..exceptions import AIPrishtinaError

class APIError(AIPrishtinaError):
    """Base exception for API-related errors."""
    pass

class APIConfigurationError(APIError):
    """Raised when there is an error in API configuration."""
    pass

class APIAuthenticationError(APIError):
    """Raised when there is an authentication error with the API."""
    pass

class APIRateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    pass

class APIValidationError(APIError):
    """Raised when API input validation fails."""
    pass

class APINotFoundError(APIError):
    """Raised when a requested API resource is not found."""
    pass

class APIConnectionError(APIError):
    """Raised when there is an error connecting to the API."""
    pass

class APITimeoutError(APIError):
    """Raised when an API request times out."""
    pass

class APIServerError(APIError):
    """Raised when there is an error on the API server."""
    pass

class APIClientError(APIError):
    """Raised when there is an error on the client side."""
    pass 
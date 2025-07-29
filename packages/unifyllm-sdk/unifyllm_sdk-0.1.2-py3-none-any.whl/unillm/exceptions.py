"""
Custom exceptions for UniLLM library.
"""

from typing import Any, Dict, Optional


class UniLLMError(Exception):
    """Base exception for UniLLM library."""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.provider = provider
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class AuthenticationError(UniLLMError):
    """Raised when authentication fails."""
    pass


class RateLimitError(UniLLMError):
    """Raised when rate limit is exceeded."""
    pass


class QuotaExceededError(UniLLMError):
    """Raised when quota is exceeded."""
    pass


class ModelNotFoundError(UniLLMError):
    """Raised when the requested model is not found."""
    pass


class InvalidRequestError(UniLLMError):
    """Raised when the request is invalid."""
    pass


class ServerError(UniLLMError):
    """Raised when the server encounters an error."""
    pass


class TimeoutError(UniLLMError):
    """Raised when the request times out."""
    pass


class NetworkError(UniLLMError):
    """Raised when there's a network connectivity issue."""
    pass


def handle_http_error(
    status_code: int,
    response_data: Dict[str, Any],
    provider: Optional[str] = None,
) -> UniLLMError:
    """Convert HTTP error to appropriate UniLLM exception."""
    
    error_message = response_data.get("error", {}).get("message", "Unknown error")
    
    if status_code == 401:
        return AuthenticationError(
            f"Authentication failed: {error_message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data,
        )
    elif status_code == 429:
        return RateLimitError(
            f"Rate limit exceeded: {error_message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data,
        )
    elif status_code == 402:
        return QuotaExceededError(
            f"Quota exceeded: {error_message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data,
        )
    elif status_code == 404:
        return ModelNotFoundError(
            f"Model not found: {error_message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data,
        )
    elif status_code == 400:
        return InvalidRequestError(
            f"Invalid request: {error_message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data,
        )
    elif status_code >= 500:
        return ServerError(
            f"Server error: {error_message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data,
        )
    else:
        return UniLLMError(
            f"HTTP {status_code}: {error_message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data,
        )


class APIError(UniLLMError):
    """Raised when the API returns an error."""
    pass 
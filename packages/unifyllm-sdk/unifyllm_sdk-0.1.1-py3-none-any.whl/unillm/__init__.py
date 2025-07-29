"""
UniLLM - Unified API Gateway for Multiple LLM Providers

A simple client library for accessing multiple LLM providers through a unified interface.
"""

from .client import UniLLM
from .client_models import ChatResponse, Message
from .exceptions import UniLLMError

__version__ = "0.1.0"
__all__ = ["UniLLM", "ChatResponse", "Message", "UniLLMError"]

# Convenience function for quick usage
def chat(model: str, messages: list, api_key: str = None, **kwargs) -> ChatResponse:
    """
    Quick chat function for simple use cases.
    
    Args:
        model: The model to use (e.g., "gpt-4", "claude-3-sonnet")
        messages: List of message dictionaries
        api_key: Your UniLLM API key (or set UNILLM_API_KEY env var)
        **kwargs: Additional parameters (temperature, max_tokens, etc.)
    
    Returns:
        ChatResponse object with the model's response
    
    Example:
        >>> from unillm import chat
        >>> response = chat("gpt-4", [{"role": "user", "content": "Hello!"}])
        >>> print(response.content)
    """
    client = UniLLM(api_key=api_key)
    return client.chat(model=model, messages=messages, **kwargs) 
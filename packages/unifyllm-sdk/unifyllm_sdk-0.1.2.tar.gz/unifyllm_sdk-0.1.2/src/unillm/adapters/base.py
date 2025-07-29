"""
Base adapter interface for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, Optional

from ..models import ChatMessage, ChatRequest, ChatResponse


class BaseAdapter(ABC):
    """Base class for all LLM provider adapters."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = 30
    
    @abstractmethod
    def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """Send a chat completion request."""
        pass
    
    @abstractmethod
    def chat_stream(
        self,
        request: ChatRequest,
    ) -> Generator[ChatResponse, None, None]:
        """Send a streaming chat completion request."""
        pass
    
    @abstractmethod
    def _convert_messages(
        self,
        messages: List[ChatMessage],
    ) -> List[Dict[str, Any]]:
        """Convert UniLLM messages to provider-specific format."""
        pass
    
    @abstractmethod
    def _convert_response(
        self,
        response_data: Dict[str, Any],
        model: str,
    ) -> ChatResponse:
        """Convert provider response to UniLLM format."""
        pass
    
    @abstractmethod
    def _convert_stream_response(
        self,
        chunk_data: Dict[str, Any],
        model: str,
    ) -> ChatResponse:
        """Convert streaming response chunk to UniLLM format."""
        pass
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _validate_request(self, request: ChatRequest) -> None:
        """Validate the request before sending."""
        if not request.messages:
            raise ValueError("Messages cannot be empty")
        
        if not request.model:
            raise ValueError("Model must be specified")
        
        # Validate temperature
        if request.temperature is not None and (
            request.temperature < 0 or request.temperature > 2
        ):
            raise ValueError("Temperature must be between 0 and 2")
        
        # Validate top_p
        if request.top_p is not None and (
            request.top_p < 0 or request.top_p > 1
        ):
            raise ValueError("top_p must be between 0 and 1")
        
        # Validate max_tokens
        if request.max_tokens is not None and request.max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
    
    def _get_provider_name(self) -> str:
        """Get the provider name for this adapter."""
        return self.__class__.__name__.replace("Adapter", "").lower() 
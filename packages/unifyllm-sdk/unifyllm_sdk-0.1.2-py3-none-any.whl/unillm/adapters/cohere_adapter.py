"""
Cohere adapter for UniLLM library.
"""

import json
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional

import requests

from .base import BaseAdapter
from ..exceptions import (
    handle_http_error,
    TimeoutError,
    NetworkError,
)
from ..models import ChatMessage, ChatRequest, ChatResponse, TokenUsage


class CohereAdapter(BaseAdapter):
    """Adapter for Cohere API."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.base_url = base_url or "https://api.cohere.ai/v1"
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """Send a chat completion request to Cohere."""
        self._validate_request(request)
        
        url = f"{self.base_url}/chat"
        headers = self._get_headers()
        
        payload = {
            "model": request.model,
            "message": self._convert_messages_to_text(request.messages),
            "temperature": request.temperature,
            "p": request.top_p,
            "max_tokens": request.max_tokens,
            "stream": False,
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            
            if response.status_code != 200:
                raise handle_http_error(
                    response.status_code,
                    response.json(),
                    provider="cohere",
                )
            
            response_data = response.json()
            return self._convert_response(response_data, request.model)
            
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out", provider="cohere")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", provider="cohere")
    
    def chat_stream(
        self,
        request: ChatRequest,
    ) -> Generator[ChatResponse, None, None]:
        """Send a streaming chat completion request to Cohere."""
        self._validate_request(request)
        
        url = f"{self.base_url}/chat"
        headers = self._get_headers()
        
        payload = {
            "model": request.model,
            "message": self._convert_messages_to_text(request.messages),
            "temperature": request.temperature,
            "p": request.top_p,
            "max_tokens": request.max_tokens,
            "stream": True,
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                stream=True,
            )
            
            if response.status_code != 200:
                raise handle_http_error(
                    response.status_code,
                    response.json(),
                    provider="cohere",
                )
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data == '[DONE]':
                            break
                        
                        try:
                            chunk_data = json.loads(data)
                            if chunk_data.get('event_type') == 'text-generation':
                                yield self._convert_stream_response(
                                    chunk_data, request.model
                                )
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out", provider="cohere")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", provider="cohere")
    
    def _convert_messages(
        self,
        messages: List[ChatMessage],
    ) -> List[Dict[str, Any]]:
        """Convert UniLLM messages to Cohere format."""
        # Cohere uses a different format, but we'll implement this for completeness
        converted = []
        for msg in messages:
            converted_msg = {
                "role": msg.role,
                "content": msg.content,
            }
            converted.append(converted_msg)
        return converted
    
    def _convert_messages_to_text(self, messages: List[ChatMessage]) -> str:
        """Convert messages to a single text string for Cohere."""
        text_parts = []
        for msg in messages:
            if msg.role == "system":
                text_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                text_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                text_parts.append(f"Assistant: {msg.content}")
        
        return "\n".join(text_parts)
    
    def _convert_response(
        self,
        response_data: Dict[str, Any],
        model: str,
    ) -> ChatResponse:
        """Convert Cohere response to UniLLM format."""
        content = response_data["text"]
        
        usage_data = response_data.get("meta", {}).get("billed_units", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
            total_tokens=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
        )
        
        return ChatResponse(
            content=content,
            model=model,
            provider="cohere",
            usage=usage,
            finish_reason="COMPLETE",
            created_at=datetime.now(),
        )
    
    def _convert_stream_response(
        self,
        chunk_data: Dict[str, Any],
        model: str,
    ) -> ChatResponse:
        """Convert Cohere streaming response chunk to UniLLM format."""
        content = chunk_data.get("text", "")
        
        return ChatResponse(
            content=content,
            model=model,
            provider="cohere",
            usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            finish_reason=None,
            created_at=datetime.now(),
        ) 
"""
Mistral adapter for UniLLM library.
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


class MistralAdapter(BaseAdapter):
    """Adapter for Mistral AI API."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.base_url = base_url or "https://api.mistral.ai/v1"
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """Send a chat completion request to Mistral."""
        self._validate_request(request)
        
        url = f"{self.base_url}/chat/completions"
        headers = self._get_headers()
        
        payload = {
            "model": request.model,
            "messages": self._convert_messages(request.messages),
            "temperature": request.temperature,
            "top_p": request.top_p,
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
                    provider="mistral",
                )
            
            response_data = response.json()
            return self._convert_response(response_data, request.model)
            
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out", provider="mistral")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", provider="mistral")
    
    def chat_stream(
        self,
        request: ChatRequest,
    ) -> Generator[ChatResponse, None, None]:
        """Send a streaming chat completion request to Mistral."""
        self._validate_request(request)
        
        url = f"{self.base_url}/chat/completions"
        headers = self._get_headers()
        
        payload = {
            "model": request.model,
            "messages": self._convert_messages(request.messages),
            "temperature": request.temperature,
            "top_p": request.top_p,
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
                    provider="mistral",
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
                            if chunk_data.get('choices'):
                                yield self._convert_stream_response(
                                    chunk_data, request.model
                                )
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out", provider="mistral")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", provider="mistral")
    
    def _convert_messages(
        self,
        messages: List[ChatMessage],
    ) -> List[Dict[str, Any]]:
        """Convert UniLLM messages to Mistral format."""
        converted = []
        for msg in messages:
            converted_msg = {
                "role": msg.role,
                "content": msg.content,
            }
            if msg.name:
                converted_msg["name"] = msg.name
            converted.append(converted_msg)
        return converted
    
    def _convert_response(
        self,
        response_data: Dict[str, Any],
        model: str,
    ) -> ChatResponse:
        """Convert Mistral response to UniLLM format."""
        choice = response_data["choices"][0]
        message = choice["message"]
        
        usage_data = response_data.get("usage", {})
        usage = TokenUsage.from_dict(usage_data)
        
        return ChatResponse(
            content=message["content"],
            model=model,
            provider="mistral",
            usage=usage,
            finish_reason=choice.get("finish_reason", "stop"),
            created_at=datetime.fromtimestamp(response_data.get("created", 0)),
        )
    
    def _convert_stream_response(
        self,
        chunk_data: Dict[str, Any],
        model: str,
    ) -> ChatResponse:
        """Convert Mistral streaming response chunk to UniLLM format."""
        choice = chunk_data["choices"][0]
        delta = choice.get("delta", {})
        
        return ChatResponse(
            content=delta.get("content", ""),
            model=model,
            provider="mistral",
            usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            finish_reason=choice.get("finish_reason"),
            created_at=datetime.now(),
        ) 
"""
OpenAI adapter for UniLLM library.
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


class OpenAIAdapter(BaseAdapter):
    """Adapter for OpenAI API."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.base_url = base_url or "https://api.openai.com/v1"
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """Send a chat completion request to OpenAI."""
        self._validate_request(request)
        
        url = f"{self.base_url}/chat/completions"
        headers = self._get_headers()
        
        payload = {
            "model": request.model,
            "messages": self._convert_messages(request.messages),
            "temperature": request.temperature,
            "top_p": request.top_p,
            "n": request.n,
            "stream": False,
            "max_tokens": request.max_tokens,
            "presence_penalty": request.presence_penalty,
            "frequency_penalty": request.frequency_penalty,
            "logit_bias": request.logit_bias,
            "user": request.user,
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
                # Log error details
                print(f"[OpenAIAdapter] Error: Status {response.status_code}, Response: {response.text}")
                raise handle_http_error(
                    response.status_code,
                    response.json(),
                    provider="openai",
                )
            
            response_data = response.json()
            return self._convert_response(response_data, request.model)
            
        except requests.exceptions.Timeout as e:
            print(f"[OpenAIAdapter] Timeout: {e}")
            raise TimeoutError("Request timed out", provider="openai")
        except requests.exceptions.RequestException as e:
            print(f"[OpenAIAdapter] Network error: {e}")
            raise NetworkError(f"Network error: {str(e)}", provider="openai")
        except Exception as e:
            print(f"[OpenAIAdapter] Unexpected error: {e}")
            raise
    
    def chat_stream(
        self,
        request: ChatRequest,
    ) -> Generator[ChatResponse, None, None]:
        """Send a streaming chat completion request to OpenAI."""
        self._validate_request(request)
        
        url = f"{self.base_url}/chat/completions"
        headers = self._get_headers()
        
        payload = {
            "model": request.model,
            "messages": self._convert_messages(request.messages),
            "temperature": request.temperature,
            "top_p": request.top_p,
            "n": request.n,
            "stream": True,
            "max_tokens": request.max_tokens,
            "presence_penalty": request.presence_penalty,
            "frequency_penalty": request.frequency_penalty,
            "logit_bias": request.logit_bias,
            "user": request.user,
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
                    provider="openai",
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
            raise TimeoutError("Request timed out", provider="openai")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", provider="openai")
    
    def _convert_messages(
        self,
        messages: List[ChatMessage],
    ) -> List[Dict[str, Any]]:
        """Convert UniLLM messages to OpenAI format."""
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
        """Convert OpenAI response to UniLLM format."""
        choice = response_data["choices"][0]
        message = choice["message"]
        
        usage_data = response_data.get("usage", {})
        usage = TokenUsage.from_dict(usage_data)
        
        return ChatResponse(
            content=message["content"],
            model=model,
            provider="openai",
            usage=usage,
            finish_reason=choice.get("finish_reason", "stop"),
            created_at=datetime.fromtimestamp(response_data.get("created", 0)),
            system_fingerprint=response_data.get("system_fingerprint"),
        )
    
    def _convert_stream_response(
        self,
        chunk_data: Dict[str, Any],
        model: str,
    ) -> ChatResponse:
        """Convert OpenAI streaming response chunk to UniLLM format."""
        choice = chunk_data["choices"][0]
        delta = choice.get("delta", {})
        
        # For streaming, we create a minimal response
        return ChatResponse(
            content=delta.get("content", ""),
            model=model,
            provider="openai",
            usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            finish_reason=choice.get("finish_reason"),
            created_at=datetime.now(),
        ) 
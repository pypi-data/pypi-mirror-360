"""
Gemini adapter for UniLLM library.
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


class GeminiAdapter(BaseAdapter):
    """Adapter for Google Gemini API."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.base_url = base_url or "https://generativelanguage.googleapis.com/v1beta"
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """Send a chat completion request to Gemini."""
        self._validate_request(request)
        
        url = f"{self.base_url}/models/{request.model}:generateContent"
        headers = self._get_headers()
        
        payload = {
            "contents": self._convert_messages(request.messages),
            "generationConfig": {
                "temperature": request.temperature,
                "topP": request.top_p,
                "maxOutputTokens": request.max_tokens,
            },
        }
        
        # Remove None values from generationConfig
        payload["generationConfig"] = {
            k: v for k, v in payload["generationConfig"].items() if v is not None
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                params={"key": self.api_key},
            )
            
            if response.status_code != 200:
                raise handle_http_error(
                    response.status_code,
                    response.json(),
                    provider="gemini",
                )
            
            response_data = response.json()
            return self._convert_response(response_data, request.model)
            
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out", provider="gemini")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", provider="gemini")
    
    def chat_stream(
        self,
        request: ChatRequest,
    ) -> Generator[ChatResponse, None, None]:
        """Send a streaming chat completion request to Gemini."""
        self._validate_request(request)
        
        url = f"{self.base_url}/models/{request.model}:streamGenerateContent"
        headers = self._get_headers()
        
        payload = {
            "contents": self._convert_messages(request.messages),
            "generationConfig": {
                "temperature": request.temperature,
                "topP": request.top_p,
                "maxOutputTokens": request.max_tokens,
            },
        }
        
        # Remove None values from generationConfig
        payload["generationConfig"] = {
            k: v for k, v in payload["generationConfig"].items() if v is not None
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                stream=True,
                params={"key": self.api_key},
            )
            
            if response.status_code != 200:
                raise handle_http_error(
                    response.status_code,
                    response.json(),
                    provider="gemini",
                )
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        
                        try:
                            chunk_data = json.loads(data)
                            if chunk_data.get('candidates'):
                                yield self._convert_stream_response(
                                    chunk_data, request.model
                                )
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out", provider="gemini")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", provider="gemini")
    
    def _convert_messages(
        self,
        messages: List[ChatMessage],
    ) -> List[Dict[str, Any]]:
        """Convert UniLLM messages to Gemini format."""
        converted = []
        for msg in messages:
            if msg.role == "system":
                # Gemini doesn't support system messages in the same way
                # We'll prepend system messages to the first user message
                continue
            
            converted_msg = {
                "role": "user" if msg.role == "user" else "model",
                "parts": [{"text": msg.content}],
            }
            converted.append(converted_msg)
        
        # Handle system messages by prepending to first user message
        system_messages = [msg for msg in messages if msg.role == "system"]
        if system_messages and converted:
            system_content = "\n".join([msg.content for msg in system_messages])
            converted[0]["parts"][0]["text"] = f"{system_content}\n\n{converted[0]['parts'][0]['text']}"
        
        return converted
    
    def _convert_response(
        self,
        response_data: Dict[str, Any],
        model: str,
    ) -> ChatResponse:
        """Convert Gemini response to UniLLM format."""
        candidate = response_data["candidates"][0]
        content = candidate["content"]["parts"][0]["text"]
        
        usage_data = response_data.get("usageMetadata", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("promptTokenCount", 0),
            completion_tokens=usage_data.get("candidatesTokenCount", 0),
            total_tokens=usage_data.get("totalTokenCount", 0),
        )
        
        return ChatResponse(
            content=content,
            model=model,
            provider="gemini",
            usage=usage,
            finish_reason=candidate.get("finishReason", "STOP"),
            created_at=datetime.now(),
        )
    
    def _convert_stream_response(
        self,
        chunk_data: Dict[str, Any],
        model: str,
    ) -> ChatResponse:
        """Convert Gemini streaming response chunk to UniLLM format."""
        candidate = chunk_data.get("candidates", [{}])[0]
        content = ""
        
        if "content" in candidate and "parts" in candidate["content"]:
            content = candidate["content"]["parts"][0].get("text", "")
        
        return ChatResponse(
            content=content,
            model=model,
            provider="gemini",
            usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            finish_reason=candidate.get("finishReason"),
            created_at=datetime.now(),
        ) 
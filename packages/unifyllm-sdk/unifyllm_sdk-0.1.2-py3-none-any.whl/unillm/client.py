"""
Simple client for UniLLM API Gateway.
"""

import os
import requests
from typing import Dict, List, Optional, Union
from .client_models import ChatResponse, Message
from .exceptions import UniLLMError


class UniLLM:
    """Simple client for UniLLM API Gateway."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "http://localhost:8000"):
        """
        Initialize the UniLLM client.
        
        Args:
            api_key: Your UniLLM API key (or set UNILLM_API_KEY env var)
            base_url: Base URL of your UniLLM API gateway
        """
        self.api_key = api_key or os.getenv("UNILLM_API_KEY")
        if not self.api_key:
            raise UniLLMError(
                "API key required. Set UNILLM_API_KEY environment variable or pass api_key parameter."
            )
        
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> ChatResponse:
        """
        Send a chat completion request.
        
        Args:
            model: The model to use (e.g., "gpt-4", "claude-3-sonnet")
            messages: List of message dictionaries with "role" and "content"
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response (not yet supported)
            **kwargs: Additional parameters
            
        Returns:
            ChatResponse object with the model's response
            
        Example:
            >>> client = UniLLM("your-api-key")
            >>> response = client.chat(
            ...     "gpt-4",
            ...     [{"role": "user", "content": "Hello!"}]
            ... )
            >>> print(response.content)
        """
        if stream:
            raise NotImplementedError("Streaming not yet supported")
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        
        # Add any additional kwargs
        payload.update(kwargs)
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Handle UniLLM server response format
            if "response" in data:
                # UniLLM server format
                content = data["response"]
                model_used = data.get("model", model)
                
                return ChatResponse(
                    content=content,
                    model=model_used,
                    usage=data.get("usage", {}),
                    finish_reason=data.get("finish_reason", "stop")
                )
            elif "choices" in data and len(data["choices"]) > 0:
                # Standard OpenAI format
                choice = data["choices"][0]
                content = choice.get("message", {}).get("content", "")
                model_used = data.get("model", model)
                
                return ChatResponse(
                    content=content,
                    model=model_used,
                    usage=data.get("usage", {}),
                    finish_reason=choice.get("finish_reason", "stop")
                )
            else:
                raise UniLLMError("Invalid response format from API")
                
        except requests.exceptions.RequestException as e:
            raise UniLLMError(f"API request failed: {str(e)}")
        except Exception as e:
            raise UniLLMError(f"Unexpected error: {str(e)}")
    
    def health_check(self) -> bool:
        """Check if the API gateway is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False 
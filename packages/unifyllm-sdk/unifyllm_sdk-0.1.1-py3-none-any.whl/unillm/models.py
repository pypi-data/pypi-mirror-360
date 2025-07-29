"""
Data models for UniLLM library (backend/server).
"""

from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """A message in a chat conversation."""
    role: Literal["system", "user", "assistant"] = Field(description="The role of the message sender")
    content: str = Field(description="The content of the message")
    name: Optional[str] = Field(default=None, description="Optional name for the message sender")

class TokenUsage(BaseModel):
    """Token usage information for a request/response."""
    prompt_tokens: int = Field(description="Number of tokens in the prompt")
    completion_tokens: int = Field(description="Number of tokens in the completion")
    total_tokens: int = Field(description="Total number of tokens used")
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "TokenUsage":
        return cls(
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
        )

class ChatResponse(BaseModel):
    """Response from a chat completion request."""
    content: str = Field(description="The generated text content")
    model: str = Field(description="The model used for generation")
    provider: str = Field(description="The provider (openai, anthropic, etc.)")
    usage: TokenUsage = Field(description="Token usage information")
    finish_reason: str = Field(description="Why the response finished")
    created_at: datetime = Field(description="Timestamp of the response")
    system_fingerprint: Optional[str] = Field(default=None, description="System fingerprint for OpenAI models")
    logprobs: Optional[Dict] = Field(default=None, description="Log probabilities if requested")
    def __str__(self) -> str:
        return self.content
    def __iter__(self):
        if hasattr(self, '_chunks'):
            for chunk in self._chunks:
                yield chunk
        else:
            yield self

class ChatRequest(BaseModel):
    """Request for a chat completion."""
    model: str = Field(description="The model to use")
    messages: List[ChatMessage] = Field(description="The conversation messages")
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    n: Optional[int] = Field(default=1, ge=1, le=10, description="Number of completions to generate")
    stream: Optional[bool] = Field(default=False, description="Whether to stream the response")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Maximum number of tokens to generate")
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    logit_bias: Optional[Dict[str, float]] = Field(default=None, description="Logit bias for specific tokens")
    user: Optional[str] = Field(default=None, description="User identifier for tracking") 
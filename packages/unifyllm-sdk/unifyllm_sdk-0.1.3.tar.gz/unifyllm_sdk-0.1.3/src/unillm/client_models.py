"""
Simple data models for UniLLM client library (client only).
"""

from typing import Dict, Optional

class ChatResponse:
    """Response from a chat completion request."""
    def __init__(self, content: str, model: str, usage: Dict = None, finish_reason: str = "stop"):
        self.content = content
        self.model = model
        self.usage = usage or {}
        self.finish_reason = finish_reason
    def __str__(self) -> str:
        return self.content
    def __repr__(self) -> str:
        return f"ChatResponse(content='{self.content[:50]}...', model='{self.model}')"

class Message:
    """A message in a chat conversation."""
    def __init__(self, role: str, content: str, name: Optional[str] = None):
        self.role = role
        self.content = content
        self.name = name
    def to_dict(self) -> Dict[str, str]:
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            name=data.get("name")
        ) 
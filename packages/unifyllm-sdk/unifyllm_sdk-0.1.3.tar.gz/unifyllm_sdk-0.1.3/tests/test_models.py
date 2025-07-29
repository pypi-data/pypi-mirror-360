"""
Tests for UniLLM data models.
"""

import pytest
from datetime import datetime

from unillm.models import ChatMessage, ChatResponse, TokenUsage, ChatRequest


class TestChatMessage:
    """Test ChatMessage model."""
    
    def test_create_chat_message(self):
        """Test creating a ChatMessage."""
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None
    
    def test_create_chat_message_with_name(self):
        """Test creating a ChatMessage with name."""
        msg = ChatMessage(role="user", content="Hello", name="John")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name == "John"
    
    def test_invalid_role(self):
        """Test that invalid role raises error."""
        with pytest.raises(ValueError):
            ChatMessage(role="invalid", content="Hello")


class TestTokenUsage:
    """Test TokenUsage model."""
    
    def test_create_token_usage(self):
        """Test creating TokenUsage."""
        usage = TokenUsage(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 30
    
    def test_from_dict(self):
        """Test creating TokenUsage from dictionary."""
        data = {
            "prompt_tokens": 15,
            "completion_tokens": 25,
            "total_tokens": 40
        }
        usage = TokenUsage.from_dict(data)
        assert usage.prompt_tokens == 15
        assert usage.completion_tokens == 25
        assert usage.total_tokens == 40
    
    def test_from_dict_missing_keys(self):
        """Test creating TokenUsage from dictionary with missing keys."""
        data = {"prompt_tokens": 10}
        usage = TokenUsage.from_dict(data)
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0


class TestChatResponse:
    """Test ChatResponse model."""
    
    def test_create_chat_response(self):
        """Test creating ChatResponse."""
        usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        response = ChatResponse(
            content="Hello world",
            model="gpt-4",
            provider="openai",
            usage=usage,
            finish_reason="stop",
            created_at=datetime.now()
        )
        assert response.content == "Hello world"
        assert response.model == "gpt-4"
        assert response.provider == "openai"
        assert response.usage == usage
        assert response.finish_reason == "stop"
    
    def test_str_representation(self):
        """Test string representation."""
        usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        response = ChatResponse(
            content="Hello world",
            model="gpt-4",
            provider="openai",
            usage=usage,
            finish_reason="stop",
            created_at=datetime.now()
        )
        assert str(response) == "Hello world"
    
    def test_iteration(self):
        """Test iteration (for streaming)."""
        usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        response = ChatResponse(
            content="Hello world",
            model="gpt-4",
            provider="openai",
            usage=usage,
            finish_reason="stop",
            created_at=datetime.now()
        )
        
        # Should yield itself when no chunks are set
        chunks = list(response)
        assert len(chunks) == 1
        assert chunks[0] == response


class TestChatRequest:
    """Test ChatRequest model."""
    
    def test_create_chat_request(self):
        """Test creating ChatRequest."""
        messages = [
            ChatMessage(role="user", content="Hello")
        ]
        request = ChatRequest(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
        assert request.model == "gpt-4"
        assert request.messages == messages
        assert request.temperature == 0.7
        assert request.max_tokens == 100
        assert request.stream is False
    
    def test_default_values(self):
        """Test default values."""
        messages = [ChatMessage(role="user", content="Hello")]
        request = ChatRequest(model="gpt-4", messages=messages)
        assert request.temperature == 1.0
        assert request.top_p == 1.0
        assert request.n == 1
        assert request.stream is False
        assert request.max_tokens is None
    
    def test_validation_temperature(self):
        """Test temperature validation."""
        messages = [ChatMessage(role="user", content="Hello")]
        
        # Valid temperature
        request = ChatRequest(model="gpt-4", messages=messages, temperature=0.5)
        assert request.temperature == 0.5
        
        # Invalid temperature (too low)
        with pytest.raises(ValueError):
            ChatRequest(model="gpt-4", messages=messages, temperature=-0.1)
        
        # Invalid temperature (too high)
        with pytest.raises(ValueError):
            ChatRequest(model="gpt-4", messages=messages, temperature=2.1)
    
    def test_validation_top_p(self):
        """Test top_p validation."""
        messages = [ChatMessage(role="user", content="Hello")]
        
        # Valid top_p
        request = ChatRequest(model="gpt-4", messages=messages, top_p=0.5)
        assert request.top_p == 0.5
        
        # Invalid top_p (too low)
        with pytest.raises(ValueError):
            ChatRequest(model="gpt-4", messages=messages, top_p=-0.1)
        
        # Invalid top_p (too high)
        with pytest.raises(ValueError):
            ChatRequest(model="gpt-4", messages=messages, top_p=1.1)
    
    def test_validation_max_tokens(self):
        """Test max_tokens validation."""
        messages = [ChatMessage(role="user", content="Hello")]
        
        # Valid max_tokens
        request = ChatRequest(model="gpt-4", messages=messages, max_tokens=100)
        assert request.max_tokens == 100
        
        # Invalid max_tokens (too low)
        with pytest.raises(ValueError):
            ChatRequest(model="gpt-4", messages=messages, max_tokens=0) 
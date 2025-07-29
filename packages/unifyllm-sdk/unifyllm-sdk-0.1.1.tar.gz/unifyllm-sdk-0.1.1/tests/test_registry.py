"""
Tests for UniLLM model registry.
"""

import pytest

from unillm.registry import ModelRegistry


class TestModelRegistry:
    """Test ModelRegistry functionality."""
    
    def test_initialization(self):
        """Test that registry initializes with default models."""
        registry = ModelRegistry()
        
        # Check that providers are registered
        providers = registry.list_providers()
        assert "openai" in providers
        assert "anthropic" in providers
        assert "gemini" in providers
        assert "mistral" in providers
        assert "cohere" in providers
    
    def test_model_registration(self):
        """Test registering new models."""
        registry = ModelRegistry()
        
        # Register a new model
        registry.register_model("test-model", "test-provider")
        
        # Check that it's registered
        assert registry.get_provider("test-model") == "test-provider"
        assert registry.is_model_supported("test-model")
        
        # Check that it appears in provider models
        provider_models = registry.get_models_for_provider("test-provider")
        assert "test-model" in provider_models
    
    def test_get_provider(self):
        """Test getting provider for known models."""
        registry = ModelRegistry()
        
        # Test OpenAI models
        assert registry.get_provider("gpt-4") == "openai"
        assert registry.get_provider("gpt-3.5-turbo") == "openai"
        
        # Test Anthropic models
        assert registry.get_provider("claude-3-sonnet") == "anthropic"
        assert registry.get_provider("claude-3-opus") == "anthropic"
        
        # Test Gemini models
        assert registry.get_provider("gemini-pro") == "gemini"
        assert registry.get_provider("gemini-pro-vision") == "gemini"
        
        # Test Mistral models
        assert registry.get_provider("mistral-large") == "mistral"
        assert registry.get_provider("mistral-medium") == "mistral"
        
        # Test Cohere models
        assert registry.get_provider("command") == "cohere"
        assert registry.get_provider("command-light") == "cohere"
    
    def test_get_provider_unknown_model(self):
        """Test getting provider for unknown model."""
        registry = ModelRegistry()
        assert registry.get_provider("unknown-model") is None
    
    def test_get_models_for_provider(self):
        """Test getting models for a specific provider."""
        registry = ModelRegistry()
        
        openai_models = registry.get_models_for_provider("openai")
        assert "gpt-4" in openai_models
        assert "gpt-3.5-turbo" in openai_models
        
        anthropic_models = registry.get_models_for_provider("anthropic")
        assert "claude-3-sonnet" in anthropic_models
        assert "claude-3-opus" in anthropic_models
    
    def test_get_models_for_unknown_provider(self):
        """Test getting models for unknown provider."""
        registry = ModelRegistry()
        models = registry.get_models_for_provider("unknown-provider")
        assert models == set()
    
    def test_list_models(self):
        """Test listing all models."""
        registry = ModelRegistry()
        models = registry.list_models()
        
        # Should contain models from all providers
        assert "gpt-4" in models
        assert "claude-3-sonnet" in models
        assert "gemini-pro" in models
        assert "mistral-large" in models
        assert "command" in models
    
    def test_list_providers(self):
        """Test listing all providers."""
        registry = ModelRegistry()
        providers = registry.list_providers()
        
        expected_providers = {"openai", "anthropic", "gemini", "mistral", "cohere"}
        assert set(providers) == expected_providers
    
    def test_is_model_supported(self):
        """Test checking if model is supported."""
        registry = ModelRegistry()
        
        # Known models
        assert registry.is_model_supported("gpt-4")
        assert registry.is_model_supported("claude-3-sonnet")
        assert registry.is_model_supported("gemini-pro")
        
        # Unknown models
        assert not registry.is_model_supported("unknown-model")
        assert not registry.is_model_supported("")
    
    def test_get_model_info(self):
        """Test getting model information."""
        registry = ModelRegistry()
        
        # Known model
        info = registry.get_model_info("gpt-4")
        assert info is not None
        assert info["model"] == "gpt-4"
        assert info["provider"] == "openai"
        
        # Unknown model
        info = registry.get_model_info("unknown-model")
        assert info is None
    
    def test_register_existing_model(self):
        """Test registering a model that already exists."""
        registry = ModelRegistry()
        
        # Register a model
        registry.register_model("test-model", "provider1")
        assert registry.get_provider("test-model") == "provider1"
        
        # Register the same model with different provider (should override)
        registry.register_model("test-model", "provider2")
        assert registry.get_provider("test-model") == "provider2"
        
        # Check that it's removed from the first provider
        provider1_models = registry.get_models_for_provider("provider1")
        assert "test-model" not in provider1_models
        
        # Check that it's added to the second provider
        provider2_models = registry.get_models_for_provider("provider2")
        assert "test-model" in provider2_models 
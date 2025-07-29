"""
Model registry for routing requests to the correct provider.
"""

from typing import Dict, List, Optional, Set


class ModelRegistry:
    """Registry for mapping model names to providers."""
    
    def __init__(self):
        self._model_to_provider: Dict[str, str] = {}
        self._provider_models: Dict[str, Set[str]] = {}
        self._aliases: Dict[str, str] = {}  # alias -> canonical
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize the default model mappings."""
        
        # OpenAI models
        openai_models = {
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4-32k",
            "gpt-4-32k-turbo",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-instruct",
        }
        
        # Anthropic models
        anthropic_models = {
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
            "claude-3-7-sonnet-20250219",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-3-5-haiku-20241022",
            "claude-3-5-sonnet-20240620",
        }
        
        # Google Gemini models
        gemini_models = {
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        }
        
        # Mistral models
        mistral_models = {
            "mistral-large",
            "mistral-medium",
            "mistral-small",
            "mistral-7b-instruct",
        }
        
        # Cohere models
        cohere_models = {
            "command",
            "command-light",
            "command-nightly",
            "command-light-nightly",
        }
        
        # Register all models
        for model in openai_models:
            self.register_model(model, "openai")
        
        for model in anthropic_models:
            self.register_model(model, "anthropic")
        
        for model in gemini_models:
            self.register_model(model, "gemini")
        
        for model in mistral_models:
            self.register_model(model, "mistral")
        
        for model in cohere_models:
            self.register_model(model, "cohere")
        
        # Add aliases for full Anthropic model names to short names
        anthropic_aliases = {
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-haiku": "claude-3-haiku-20240307",
            "claude-3-sonnet": "claude-3-5-sonnet-20241022",  # Use the newer 3.5 version
            "claude-3-sonnet-20240229": "claude-3-5-sonnet-20241022",  # Map to newer version
        }
        for alias, canonical in anthropic_aliases.items():
            self.register_model(alias, "anthropic")
            self._aliases[alias] = canonical
    
    def resolve_alias(self, model: str) -> str:
        return self._aliases.get(model, model)
    
    def register_model(self, model: str, provider: str):
        """Register a model with its provider."""
        model = self.resolve_alias(model)
        # If the model was already registered with a different provider, remove it
        old_provider = self._model_to_provider.get(model)
        if old_provider and old_provider != provider:
            if old_provider in self._provider_models:
                self._provider_models[old_provider].discard(model)
        
        # Register the model with the new provider
        self._model_to_provider[model] = provider
        if provider not in self._provider_models:
            self._provider_models[provider] = set()
        self._provider_models[provider].add(model)
    
    def get_provider(self, model: str) -> Optional[str]:
        """Get the provider for a given model."""
        model = self.resolve_alias(model)
        return self._model_to_provider.get(model)
    
    def get_models_for_provider(self, provider: str) -> Set[str]:
        """Get all models for a given provider."""
        return self._provider_models.get(provider, set())
    
    def list_models(self) -> List[str]:
        """List all registered models."""
        models = list(self._model_to_provider.keys())
        # Add aliases to the list
        models.extend(list(self._aliases.keys()))
        return models
    
    def list_providers(self) -> List[str]:
        """List all registered providers."""
        return list(self._provider_models.keys())
    
    def is_model_supported(self, model: str) -> bool:
        """Check if a model is supported."""
        model = self.resolve_alias(model)
        return model in self._model_to_provider
    
    def get_model_info(self, model: str) -> Optional[Dict[str, str]]:
        """Get information about a model."""
        model = self.resolve_alias(model)
        provider = self.get_provider(model)
        if provider:
            return {
                "model": model,
                "provider": provider,
            }
        return None


# Global registry instance
model_registry = ModelRegistry() 
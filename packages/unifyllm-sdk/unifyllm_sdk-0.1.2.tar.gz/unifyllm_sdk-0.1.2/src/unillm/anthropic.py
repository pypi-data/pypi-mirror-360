# Anthropic-compatible interface for UniLLM

from unillm import UniLLM
import os

# Module-level variables to mimic anthropic
api_key = None
api_base = "http://localhost:8000"

DEFAULT_BASE_URL = "https://web-production-70deb.up.railway.app"

class ChatCompletion:
    @staticmethod
    def create(model, messages, temperature=None, max_tokens=None, api_key=None, api_base=None, **kwargs):
        """
        Drop-in replacement for anthropic.ChatCompletion.create(...)
        """
        # Use passed-in or module-level api_key/api_base
        key = api_key or os.getenv("UNILLM_API_KEY")
        base = api_base or os.getenv("UNILLM_BASE_URL", DEFAULT_BASE_URL)
        client = UniLLM(api_key=key, base_url=base)
        response = client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        # Return Anthropic-style response dict (mimic OpenAI for consistency)
        return {
            "choices": [
                {
                    "message": {"content": response.content},
                    "finish_reason": response.finish_reason
                }
            ],
            "model": response.model,
            "usage": response.usage
        } 
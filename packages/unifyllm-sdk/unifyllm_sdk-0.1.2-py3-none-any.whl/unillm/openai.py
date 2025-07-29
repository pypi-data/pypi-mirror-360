# OpenAI-compatible interface for UniLLM

from unillm import UniLLM
import os

# Module-level variables to mimic openai
api_key = None
api_base = "http://localhost:8000"

DEFAULT_BASE_URL = "https://web-production-70deb.up.railway.app"

class _ChatCompletions:
    def __init__(self, client):
        self._client = client
    def create(self, model, messages, temperature=None, max_tokens=None, **kwargs):
        response = self._client._unillm.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        # Mimic OpenAI v1.x response object
        class Message:
            def __init__(self, content):
                self.content = content
        class Choice:
            def __init__(self, message, finish_reason):
                self.message = message
                self.finish_reason = finish_reason
        class Response:
            def __init__(self, choices, model, usage):
                self.choices = choices
                self.model = model
                self.usage = usage
        return Response(
            choices=[Choice(Message(response.content), response.finish_reason)],
            model=response.model,
            usage=response.usage
        )

class _Chat:
    def __init__(self, client):
        self.completions = _ChatCompletions(client)

class OpenAI:
    def __init__(self, api_key=None, base_url=None):
        if base_url is None:
            base_url = os.getenv("UNILLM_BASE_URL", DEFAULT_BASE_URL)
        self._unillm = UniLLM(api_key=api_key, base_url=base_url)
        self.chat = _Chat(self)

class ChatCompletion:
    @staticmethod
    def create(model, messages, temperature=None, max_tokens=None, api_key=None, api_base=None, **kwargs):
        """
        Drop-in replacement for openai.ChatCompletion.create(...)
        """
        # Use passed-in or module-level api_key/api_base
        key = api_key or globals()["api_key"]
        base = api_base or globals()["api_base"]
        client = UniLLM(api_key=key, base_url=base)
        response = client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        # Return OpenAI-style response dict
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
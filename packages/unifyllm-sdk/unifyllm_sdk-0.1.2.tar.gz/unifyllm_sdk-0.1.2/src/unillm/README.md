# UniLLM Python Client Library ![version](https://img.shields.io/badge/version-0.1.0-blue)

## Overview

**UniLLM** is a unified Python client for accessing multiple large language model (LLM) providers (OpenAI, Anthropic, Gemini, Mistral, Cohere, and more) through a single, easy-to-use interface.  
It abstracts away provider-specific details, allowing you to switch models and providers with minimal code changes.

---

## Features

- **Unified API:** One interface for all supported LLM providers and models.
- **Drop-in replacements:** Use `from unillm import openai` or `from unillm import anthropic_dropin as anthropic` for seamless migration from official SDKs.
- **Provider/model switching:** Change models/providers by changing a string.
- **API key management:** Pass your UniLLM API key directly or via environment variable.
- **Custom error handling:** Catch and handle errors with meaningful exceptions.
- **Health check:** Programmatically check if your backend is up.
- **Extensible:** Add new providers via adapters.

---

## Installation

```sh
pip install unillm
```

---

## Quick Start

### 1. **Unified API Example**

```python
from unillm import UniLLM

client = UniLLM(api_key="YOUR_API_KEY", base_url="https://your-backend.url")
response = client.chat(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello, world!"}],
    temperature=0.7,
    max_tokens=100
)
print(response.content)
```

---

### 2. **OpenAI Drop-in Replacement**

```python
from unillm import openai
openai.api_key = "YOUR_API_KEY"
openai.api_base = "https://your-backend.url"
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}],
    temperature=0.7,
    max_tokens=100
)
print(response["choices"][0]["message"]["content"])
```

---

### 3. **Anthropic Drop-in Replacement**

```python
from unillm import anthropic_dropin as anthropic
anthropic.api_key = "YOUR_API_KEY"
anthropic.api_base = "https://your-backend.url"
response = anthropic.ChatCompletion.create(
    model="claude-3-5-sonnet-20240620",
    messages=[{"role": "user", "content": "Hello, Claude!"}],
    temperature=0.7,
    max_tokens=100
)
print(response["choices"][0]["message"]["content"])
```

---

### 4. **Switching Providers/Models**

Just change the `model` string:
```python
response = client.chat(
    model="claude-3-5-sonnet-20240620",  # Anthropic model
    messages=[{"role": "user", "content": "Hello, Claude!"}]
)
```

---

### 5. **Migration Notes**
- For OpenAI: Change `import openai` to `from unillm import openai` and set `api_base`/`api_key`.
- For Anthropic: Change `import anthropic` to `from unillm import anthropic_dropin as anthropic` and set `api_base`/`api_key`.
- All other code can remain the same for chat completions.

---

## API Reference

### **UniLLM Class**

```python
UniLLM(api_key=None, base_url="http://localhost:8000")
```
- `api_key`: Your UniLLM API key (or set `UNILLM_API_KEY` env var)
- `base_url`: URL of your UniLLM backend

#### **chat()**
```python
chat(
    model: str,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    **kwargs
) -> ChatResponse
```
- `model`: Model name (e.g., `"gpt-4"`, `"claude-3-5-sonnet-20240620"`)
- `messages`: List of messages (`{"role": ..., "content": ...}`)
- `temperature`, `max_tokens`, etc.: Standard LLM parameters

#### **health_check()**
```python
health_check() -> bool
```
Returns `True` if backend is healthy.

---

### **ChatCompletion Drop-ins**
- `openai.ChatCompletion.create(...)`
- `anthropic.ChatCompletion.create(...)`

---

## Supported Models & Providers

- **OpenAI:** `"gpt-4"`, `"gpt-3.5-turbo"`, etc.
- **Anthropic:** `"claude-3-5-sonnet-20240620"`, etc.
- **Gemini, Mistral, Cohere:** (see full list in your backend/docs)

---

## Troubleshooting

- **502/connection errors:** Check your backend URL and health.
- **Model not found:** Ensure the model name is supported by your backend.
- **API key errors:** Make sure your key is valid and set correctly.

---

## Contributing

- PRs and issues welcome!
- See [CONTRIBUTING.md] for guidelines.

---

## License

MIT 
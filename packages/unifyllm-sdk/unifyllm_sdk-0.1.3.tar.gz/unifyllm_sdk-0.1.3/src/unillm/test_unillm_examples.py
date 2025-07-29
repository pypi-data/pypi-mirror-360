import os
from unillm import UniLLM, chat, Message, UniLLMError

def main():
    API_KEY = os.getenv("UNILLM_API_KEY") or "YOUR_API_KEY"
    BASE_URL = os.getenv("UNILLM_BASE_URL") or "https://your-backend.url"
    print("=== UniLLM Example Test ===")

    # 1. Basic Chat Completion
    try:
        client = UniLLM(api_key=API_KEY, base_url=BASE_URL)
        response = client.chat(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello, world!"}],
            temperature=0.7,
            max_tokens=100
        )
        print("Basic chat response:", response.content)
    except Exception as e:
        print("Basic chat failed:", e)

    # 2. Quick chat() function
    try:
        response = chat(
            model="gpt-4",
            messages=[{"role": "user", "content": "Quick chat!"}],
            api_key=API_KEY,
            base_url=BASE_URL
        )
        print("Quick chat response:", response.content)
    except Exception as e:
        print("Quick chat failed:", e)

    # 3. Health check
    try:
        healthy = client.health_check()
        print("Health check:", healthy)
    except Exception as e:
        print("Health check failed:", e)

    # 4. Switching models/providers
    try:
        response = client.chat(
            model="claude-3-sonnet-20240229",
            messages=[{"role": "user", "content": "Hello, Claude!"}]
        )
        print("Anthropic model response:", response.content)
    except Exception as e:
        print("Anthropic model failed:", e)

    # 5. Error handling
    try:
        response = client.chat(
            model="non-existent-model",
            messages=[{"role": "user", "content": "Test error handling"}]
        )
    except UniLLMError as e:
        print("Caught UniLLMError as expected:", e)

    # 6. Message object
    msg = Message(role="user", content="Hello!", name="Alice")
    print("Message as dict:", msg.to_dict())
    msg2 = Message.from_dict({"role": "user", "content": "Hi!", "name": "Bob"})
    print("Message from dict:", msg2.to_dict())

    # 7. Multi-provider loop
    models = ["gpt-4", "claude-3-sonnet-20240229"]
    for model in models:
        try:
            response = client.chat(
                model=model,
                messages=[{"role": "user", "content": f"Hello from {model}!"}]
            )
            print(f"{model} response:", response.content)
        except Exception as e:
            print(f"{model} failed:", e)

if __name__ == "__main__":
    main() 
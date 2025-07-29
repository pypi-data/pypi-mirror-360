import os

# 1. Test with official OpenAI package (new client interface)
try:
    import openai as openai_native
    def test_openai_native():
        print("\n--- Official OpenAI SDK (Client Interface) ---")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("OPENAI_API_KEY not set, skipping native OpenAI test.")
            return
        try:
            client = openai_native.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say hello from OpenAI native!"}],
                temperature=0.7,
                max_tokens=20
            )
            print("OpenAI native response:", response)
            print("Model reply:", response.choices[0].message.content)
        except Exception as e:
            print("OpenAI native test failed:", e)
except ImportError:
    def test_openai_native():
        print("openai package not installed, skipping native OpenAI test.")

# 2. Test with unillm.openai drop-in (new client interface)
from unillm import openai as openai_unify

def test_openai_unify():
    print("\n--- UniLLM OpenAI Drop-in (Client Interface) ---")
    client = openai_unify.OpenAI(
        api_key=os.getenv("UNILLM_API_KEY") or "YOUR_API_KEY",
        base_url=os.getenv("UNILLM_BASE_URL") or "https://your-backend.url"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello from UniLLM OpenAI drop-in!"}],
            temperature=0.7,
            max_tokens=20
        )
        print("UniLLM OpenAI drop-in response:", response)
        print("Model reply:", response.choices[0].message.content)
    except Exception as e:
        print("UniLLM OpenAI drop-in test failed:", e)

# 3. Test with official anthropic package
try:
    import anthropic as anthropic_native
    def test_anthropic_native():
        print("\n--- Official Anthropic SDK ---")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            print("ANTHROPIC_API_KEY not set, skipping native Anthropic test.")
            return
        try:
            client = anthropic_native.Client(api_key=anthropic_api_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                messages=[{"role": "user", "content": "Say hello from Anthropic native!"}],
                max_tokens=20
            )
            print("Anthropic native response:", response)
            # Print the first message content if available
            if hasattr(response, 'content'):
                print("Model reply:", response.content)
            elif isinstance(response, dict):
                print("Model reply:", response.get("content") or response)
        except Exception as e:
            print("Anthropic native test failed:", e)
except ImportError:
    def test_anthropic_native():
        print("anthropic package not installed, skipping native Anthropic test.")

# 4. Test with unillm.anthropic drop-in
from unillm import anthropic

def test_anthropic_unify():
    print("\n--- UniLLM Anthropic Drop-in ---")
    anthropic.api_key = os.getenv("UNILLM_API_KEY") or "YOUR_API_KEY"
    anthropic.api_base = os.getenv("UNILLM_BASE_URL") or "https://your-backend.url"
    try:
        response = anthropic.ChatCompletion.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": "Say hello from UniLLM Anthropic drop-in!"}],
            temperature=0.7,
            max_tokens=20
        )
        print("UniLLM Anthropic drop-in response:", response)
        print("Model reply:", response["choices"][0]["message"]["content"])
    except Exception as e:
        print("UniLLM Anthropic drop-in test failed:", e)

if __name__ == "__main__":
    test_openai_native()
    test_openai_unify()
    test_anthropic_native()
    test_anthropic_unify() 
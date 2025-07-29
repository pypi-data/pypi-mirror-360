from unillm import openai
import os

def main():
    # Set API key and base URL (from env or hardcoded)
    openai.api_key = os.getenv("UNILLM_API_KEY") or "YOUR_API_KEY"
    openai.api_base = os.getenv("UNILLM_BASE_URL") or "https://your-backend.url"

    print("=== OpenAI Drop-in Replacement Test ===")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello from OpenAI drop-in!"}],
            temperature=0.7,
            max_tokens=50
        )
        print("OpenAI-style response:", response)
        print("Model reply:", response["choices"][0]["message"]["content"])
    except Exception as e:
        print("OpenAI drop-in test failed:", e)

if __name__ == "__main__":
    main() 
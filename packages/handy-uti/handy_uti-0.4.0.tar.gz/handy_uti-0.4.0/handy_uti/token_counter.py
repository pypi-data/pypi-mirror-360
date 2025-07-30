import os
from google import genai
from groq import Groq


def google_token_counter(content: str, model: str = "gemini-2.5-flash") -> int:
    client = genai.Client()
    total_tokens = client.models.count_tokens(model=model, contents=content)
    return total_tokens


def groq_token_counter(
    content: str, model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
) -> int:
    """Count tokens using Groq API and Llama 4 models"""
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    # The Groq API does not provide a direct token counting endpoint, so we simulate a completion and read the usage
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": content}],
        model=model,
        max_tokens=1,  # Minimize cost, we only want token usage
    )
    return response.usage.prompt_tokens

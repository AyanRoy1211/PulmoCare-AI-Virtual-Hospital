# shared/llm_client.py

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def chat(prompt: str, model: str = "llama-3.1-8b-instant", max_tokens: int = 1500):
    """Stream tokens from the LLM"""

    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def vision(image_base64: str, prompt: str) -> str:
    """Vision call for prescription parsing."""
    response = client.chat.completions.create(
        model="qwen/qwen3.5-9b:free",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            }
        ],
        max_tokens=1000
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("Response content is None")
    return content
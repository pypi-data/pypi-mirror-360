# ollama_llm.py

from openai import OpenAI

def call_local_llm(prompt: str, base_url: str, model: str = "qwen3:30b", api_key: str = "ollama") -> str:
    """
    Calls a local OpenAI-compatible LLM (e.g., Ollama) and returns the response content.

    Args:
        prompt (str): User prompt
        base_url (str): Base URL of local LLM server (e.g., Ollama)
        model (str): Model name (default = 'qwen3:30b')
        api_key (str): Required API key placeholder (default = 'ollama')

    Returns:
        str: Model-generated response
    """
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model=model,
        max_tokens=3000,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content

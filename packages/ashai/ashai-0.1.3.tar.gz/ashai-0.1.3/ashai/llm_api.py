# llm_api.py
import requests
from typing import Optional

def llm(system_instruction: str, user_prompt: str, api_url: str, api_key: str) -> str:
    """
    Calls the LLM API with a system instruction and user prompt,
    using user-supplied API URL and key.
    """
    if not api_url or not api_key:
        raise ValueError("You must provide both LLM API endpoint and key.")

    body = {
        "max_tokens": 4000,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user",   "content": user_prompt}
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    print("LLM Request Body:", body)  # Debugging log

    response = requests.post(api_url, headers=headers, json=body, verify=False)

    if response.status_code == 200:
        result = response.json()
        print("LLM Response:", result)  # Debugging log
        return result["choices"][0]["message"]["content"]
    else:
        print(f"LLM API call failed: {response.status_code} - {response.text}")
        return "Error: Unable to generate response"


if __name__ == "__main__":
    # Example usage for manual testing
     llm("you are a smart assistant", "how are you?", api_url="https://your-endpoint.com", api_key="your-api-key")

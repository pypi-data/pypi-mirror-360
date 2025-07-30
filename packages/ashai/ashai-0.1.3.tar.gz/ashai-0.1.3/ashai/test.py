from openai import OpenAI
def call_llm(prompt):
    client = OpenAI(
    base_url="http://BMC-XRYXW6XGCJ.got.volvo.net:11434/v1",
    api_key="ollama",
)
    response = client.chat.completions.create(
        model="qwen3:30b",
        max_tokens=3000,
        messages=[
            {"role": "user", "content": prompt}
        ],
       
    )
    print(response)
    return response.choices[0].message.content
    
 


from wraipperz.api.llm import call_ai
from dotenv import load_dotenv

load_dotenv()

messages = [
    {"role": "user", "content": "Say 'Hello from Vertex AI'"}
]

try:
    response, cost = call_ai(
        model="vertex/claude-opus-4@20250514",
        messages=messages,
        temperature=0,
        max_tokens=50
    )
    print(f"Success! Response: {response}")
    print(f"Cost: ${cost}")
except Exception as e:
    print(f"Error: {e}")

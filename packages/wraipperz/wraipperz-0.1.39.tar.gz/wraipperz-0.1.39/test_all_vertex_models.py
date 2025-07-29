from anthropic import AnthropicVertex
from dotenv import load_dotenv
import os

load_dotenv()

client = AnthropicVertex(project_id="blinktoon-prod", region="us-east5")

models = [
    "claude-opus-4@20250514",
    "claude-sonnet-4@20250514",
    "claude-3-7-sonnet@20250219"
]

for model in models:
    print(f"\nTesting {model}...")
    try:
        message = client.messages.create(
            model=model,
            max_tokens=20,
            messages=[{"role": "user", "content": "Say hello"}],
        )
        print(f"✓ {model} works! Response: {message.content[0].text}")
    except Exception as e:
        print(f"✗ {model} failed: {str(e)[:100]}...")

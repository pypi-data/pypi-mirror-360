from anthropic import AnthropicVertex
from dotenv import load_dotenv
import os

load_dotenv()

client = AnthropicVertex(project_id="blinktoon-prod", region="us-east5")

# Test the models that work in vertex1.py
models_to_test = [
    "claude-opus-4@20250514",  # This works in your example
    "claude-3-5-sonnet-v2@20241022",
    "claude-3-haiku@20240307",
    "claude-3-5-haiku@20241022",
]

for model in models_to_test:
    print(f"\nTesting model: {model}")
    try:
        message = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}],
        )
        print(f"✓ {model} works!")
    except Exception as e:
        print(f"✗ {model} failed: {str(e)[:200]}...")

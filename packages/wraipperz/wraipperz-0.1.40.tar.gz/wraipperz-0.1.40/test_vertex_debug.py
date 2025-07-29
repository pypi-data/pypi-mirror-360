import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

print("=== Environment Variables ===")
print(f"VERTEX_PROJECT_ID: {os.getenv('VERTEX_PROJECT_ID')}")
print(f"VERTEX_LOCATION: {os.getenv('VERTEX_LOCATION')}")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

# Test direct AnthropicVertex
from anthropic import AnthropicVertex

print("\n=== Direct AnthropicVertex Test ===")
client = AnthropicVertex(project_id="blinktoon-prod", region="us-east5")
print(f"Client created with region: us-east5")

# Test VertexAIProvider
from wraipperz.api.llm import VertexAIProvider

print("\n=== VertexAIProvider Test ===")
provider = VertexAIProvider()
print(f"Provider project_id: {provider.project_id}")
print(f"Provider location: {provider.location}")

# Test with call_ai
from wraipperz.api.llm import call_ai

print("\n=== call_ai Test ===")
try:
    response, cost = call_ai(
        model="vertex/claude-3-haiku@20240307",
        messages=[{"role": "user", "content": "Say hello"}],
        temperature=0,
        max_tokens=50
    )
    print(f"Success! Response: {response}")
except Exception as e:
    print(f"Error: {e}")
    # Check if it's using wrong region
    if "us-central1" in str(e):
        print("ERROR: Still using us-central1 instead of us-east5!")

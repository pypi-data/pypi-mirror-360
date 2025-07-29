from anthropic import AnthropicVertex
from dotenv import load_dotenv
import os

load_dotenv()

project_id = os.getenv("VERTEX_PROJECT_ID")
# モデルが実行されている場所
region = os.getenv("VERTEX_LOCATION")

print(project_id)
print(region)

client = AnthropicVertex(project_id=project_id, region=region)

message = client.messages.create(
    model="claude-opus-4@20250514",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Hey Claude!",
        }
    ],
)
print(message)
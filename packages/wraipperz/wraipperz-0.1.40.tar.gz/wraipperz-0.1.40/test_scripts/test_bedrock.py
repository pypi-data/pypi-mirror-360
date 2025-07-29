from wraipperz import call_ai

# Basic text completion
messages = [
    {"role": "user", "content": "Hello, how are you?"}
]

# Use Claude 3.5 Sonnet via Bedrock
response = call_ai("bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0", messages)

# Use Amazon Nova Pro
# response = call_ai("bedrock/amazon.nova-pro-v1:0", messages)

# Use Meta Llama 3.1 70B
# response = call_ai("bedrock/meta.llama3-1-70b-instruct-v1:0", messages)

# With system prompt and images (for supported models)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "path/to/image.jpg"}}
    ]}
]
response = call_ai("bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0", messages)
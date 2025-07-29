"""
Example: Using Claude models via Google Cloud Vertex AI

Prerequisites:
1. Set up a Google Cloud project with Vertex AI API enabled
2. Install required dependencies:
   pip install 'anthropic[vertex]'
3. Set environment variables:
   - VERTEX_PROJECT_ID: Your Google Cloud project ID
   - VERTEX_LOCATION: Region where Claude models are available (e.g., us-east5)
   - GOOGLE_APPLICATION_CREDENTIALS: Path to your service account key JSON file

Note: Claude models availability varies by region. Check Vertex AI Model Garden
for the latest availability in your region.
"""

import os
from wraipperz.api.llm import call_ai
from wraipperz.api.messages import MessageBuilder

# Option 1: Using environment variables (recommended)
# export VERTEX_PROJECT_ID="your-project-id"
# export VERTEX_LOCATION="us-east5"
# export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Option 2: Setting environment variables in code (for testing only)
# os.environ["VERTEX_PROJECT_ID"] = "your-project-id"
# os.environ["VERTEX_LOCATION"] = "us-east5"  # Claude models are available in us-east5
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/service-account-key.json"


def main():
    # Example 1: Basic text generation with Claude Haiku
    print("Example 1: Basic text generation")
    messages = MessageBuilder().add_user("What is the capital of France?").build()
    
    try:
        response, cost = call_ai(
            model="vertex/claude-3-haiku@20240307",  # Fast, cost-effective model
            messages=messages,
            temperature=0,
            max_tokens=100
        )
        print(f"Response: {response}")
        print(f"Cost estimate: ${cost:.4f}\n")
    except Exception as e:
        print(f"Error: {e}\n")
        print("Tip: Make sure VERTEX_LOCATION is set to a region where Claude is available (e.g., us-east5)")
    
    # Example 2: Using Claude Sonnet 3.5 for more complex tasks
    print("Example 2: Complex reasoning with Claude Sonnet 3.5")
    messages = (
        MessageBuilder()
        .add_system("You are a helpful coding assistant.")
        .add_user("Write a Python function to calculate the Fibonacci sequence.")
        .build()
    )
    
    try:
        response, cost = call_ai(
            model="vertex/claude-3-5-sonnet-v2@20241022",  # More capable model
            messages=messages,
            temperature=0,
            max_tokens=500
        )
        print(f"Response: {response}")
        print(f"Cost estimate: ${cost:.4f}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 3: Image analysis with Claude
    print("Example 3: Image analysis")
    # Note: Replace with path to your image
    image_path = "path/to/your/image.jpg"
    
    if os.path.exists(image_path):
        messages = (
            MessageBuilder()
            .add_user("What do you see in this image?")
            .add_image(image_path)
            .build()
        )
        
        try:
            response, cost = call_ai(
                model="vertex/claude-3-5-sonnet-v2@20241022",
                messages=messages,
                temperature=0,
                max_tokens=300
            )
            print(f"Response: {response}")
            print(f"Cost estimate: ${cost:.4f}\n")
        except Exception as e:
            print(f"Error: {e}\n")
    else:
        print("Skipping image analysis - no image found\n")
    
    # Example 4: Using Claude 4 models (if you have access)
    print("Example 4: Premium Claude 4 models")
    messages = MessageBuilder().add_user("Explain quantum computing in simple terms.").build()
    
    # Try Claude Opus 4 (most capable)
    try:
        response, cost = call_ai(
            model="vertex/claude-opus-4@20250514",
            messages=messages,
            temperature=0,
            max_tokens=300
        )
        print(f"Claude Opus 4 Response: {response[:100]}...")
        print(f"Cost estimate: ${cost:.4f}\n")
    except Exception as e:
        if "not found" in str(e).lower() or "access" in str(e).lower():
            print("Claude Opus 4 not available - this is a premium model with limited access\n")
        else:
            print(f"Error: {e}\n")
    
    # Example 5: Direct provider usage (for advanced control)
    print("Example 5: Direct provider usage")
    from wraipperz.api.llm import VertexAIProvider
    
    try:
        # Create provider with explicit configuration
        provider = VertexAIProvider(
            project_id=os.getenv("VERTEX_PROJECT_ID"),
            location="us-east5"  # Explicitly specify region
        )
        
        response = provider.call_ai(
            messages=[{"role": "user", "content": "Hello, Claude!"}],
            temperature=0,
            max_tokens=50,
            model="vertex/claude-3-haiku@20240307"
        )
        print(f"Direct provider response: {response}\n")
    except Exception as e:
        print(f"Error: {e}\n")


if __name__ == "__main__":
    print("Vertex AI Claude Models Example")
    print("================================\n")
    
    # Check configuration
    if not os.getenv("VERTEX_PROJECT_ID"):
        print("⚠️  Warning: VERTEX_PROJECT_ID not set")
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("⚠️  Warning: GOOGLE_APPLICATION_CREDENTIALS not set")
    
    location = os.getenv("VERTEX_LOCATION", "us-east5 (default)")
    print(f"📍 Using location: {location}")
    print(f"🔑 Project ID: {os.getenv('VERTEX_PROJECT_ID', 'Not set')}\n")
    
    main() 
#!/usr/bin/env python3
"""
Test script for AWS Bedrock with APAC inference profiles
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, "src")

from wraipperz.api.llm import call_ai

def test_bedrock_apac():
    """Test Bedrock with APAC inference profiles"""
    
    # Test message
    messages = [
        {"role": "user", "content": "Hello! Can you tell me a short joke?"}
    ]
    
    # List of APAC inference profiles available in your account
    apac_models = [
        "bedrock/apac.anthropic.claude-3-haiku-20240307-v1:0",
        "bedrock/apac.anthropic.claude-3-sonnet-20240229-v1:0",
        "bedrock/apac.anthropic.claude-3-5-sonnet-20240620-v1:0",
        "bedrock/apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "bedrock/apac.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "bedrock/apac.anthropic.claude-sonnet-4-20250514-v1:0",
    ]
    
    print("Testing AWS Bedrock with APAC inference profiles...")
    print(f"Region: {os.getenv('AWS_DEFAULT_REGION', 'not set')}")
    print()
    
    # Test with Claude 3.5 Sonnet (fastest and most cost-effective)
    test_model = "bedrock/apac.anthropic.claude-3-5-sonnet-20240620-v1:0"
    
    try:
        print(f"Testing model: {test_model}")
        response = call_ai(test_model, messages, temperature=0.7, max_tokens=500)
        print(f"✅ Success!")
        print(f"Response: {response}")
        print()
        
    except Exception as e:
        print(f"❌ Error with {test_model}: {e}")
        print()
    
    # Test with Claude 3 Haiku (fastest)
    test_model = "bedrock/apac.anthropic.claude-3-haiku-20240307-v1:0"
    
    try:
        print(f"Testing model: {test_model}")
        response = call_ai(test_model, messages, temperature=0.7, max_tokens=500)
        print(f"✅ Success!")
        print(f"Response: {response}")
        print()
        
    except Exception as e:
        print(f"❌ Error with {test_model}: {e}")
        print()

def test_system_prompt():
    """Test with system prompt"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant that responds in haiku format."},
        {"role": "user", "content": "Tell me about artificial intelligence."}
    ]
    
    model = "bedrock/apac.anthropic.claude-3-5-sonnet-20240620-v1:0"
    
    try:
        print(f"Testing system prompt with: {model}")
        response = call_ai(model, messages, temperature=0.7, max_tokens=500)
        print(f"✅ Success!")
        print(f"Response: {response}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()

if __name__ == "__main__":
    # Check AWS credentials
    if not (os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE")):
        print("⚠️  AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or configure AWS_PROFILE")
        sys.exit(1)
    
    if not os.getenv("AWS_DEFAULT_REGION"):
        print("⚠️  AWS_DEFAULT_REGION not set. Using ap-northeast-1")
        os.environ["AWS_DEFAULT_REGION"] = "ap-northeast-1"
    
    test_bedrock_apac()
    test_system_prompt() 
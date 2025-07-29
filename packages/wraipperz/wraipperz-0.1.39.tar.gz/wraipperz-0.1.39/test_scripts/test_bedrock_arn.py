#!/usr/bin/env python3
"""
Test script for AWS Bedrock with full ARN inference profiles
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, "src")

from wraipperz.api.llm import call_ai

def test_bedrock_arn():
    """Test Bedrock with full ARN inference profiles"""
    
    # Test message
    messages = [
        {"role": "user", "content": "Hello! Can you tell me a short joke?"}
    ]
    
    # Your actual inference profile ARNs from ap-northeast-1
    # Note: Replace the account ID and region if needed
    account_id = "633359116962" 
    region = "ap-northeast-1"
    
    inference_profiles = {
        "Claude 3 Haiku": f"arn:aws:bedrock:{region}:{account_id}:inference-profile/apac.anthropic.claude-3-haiku-20240307-v1:0",
        "Claude 3 Sonnet": f"arn:aws:bedrock:{region}:{account_id}:inference-profile/apac.anthropic.claude-3-sonnet-20240229-v1:0", 
        "Claude 3.5 Sonnet (v1)": f"arn:aws:bedrock:{region}:{account_id}:inference-profile/apac.anthropic.claude-3-5-sonnet-20240620-v1:0",
        "Claude 3.5 Sonnet (v2)": f"arn:aws:bedrock:{region}:{account_id}:inference-profile/apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "Claude 3.7 Sonnet": f"arn:aws:bedrock:{region}:{account_id}:inference-profile/apac.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "Claude Sonnet 4": f"arn:aws:bedrock:{region}:{account_id}:inference-profile/apac.anthropic.claude-sonnet-4-20250514-v1:0",
    }
    
    print("Testing AWS Bedrock with full ARN inference profiles...")
    print(f"Region: {os.getenv('AWS_DEFAULT_REGION', 'not set')}")
    print()
    
    # Test with Claude 3 Haiku first (should be fastest and cheapest)
    test_name = "Claude 3 Haiku"
    test_arn = inference_profiles[test_name]
    
    try:
        print(f"Testing {test_name}:")
        print(f"ARN: {test_arn}")
        
        # For bedrock provider, we need to use the format: bedrock/<model_id>
        model_id = f"bedrock/{test_arn}"
        
        response = call_ai(model_id, messages, temperature=0.7, max_tokens=500)
        print(f"✅ Success!")
        print(f"Response: {response}")
        print()
        
    except Exception as e:
        print(f"❌ Error with {test_name}: {e}")
        print()
    
    # Test with Claude 3.5 Sonnet if Haiku works
    test_name = "Claude 3.5 Sonnet (v1)"
    test_arn = inference_profiles[test_name]
    
    try:
        print(f"Testing {test_name}:")
        print(f"ARN: {test_arn}")
        
        model_id = f"bedrock/{test_arn}"
        
        response = call_ai(model_id, messages, temperature=0.7, max_tokens=500)
        print(f"✅ Success!")
        print(f"Response: {response}")
        print()
        
    except Exception as e:
        print(f"❌ Error with {test_name}: {e}")
        print()

def test_short_ids():
    """Test with short inference profile IDs"""
    print("=== Testing Short Inference Profile IDs ===")
    
    messages = [{"role": "user", "content": "Hello!"}]
    
    short_ids = [
        "apac.anthropic.claude-3-haiku-20240307-v1:0",
        "apac.anthropic.claude-3-5-sonnet-20240620-v1:0"
    ]
    
    for short_id in short_ids:
        try:
            print(f"Testing short ID: {short_id}")
            model_id = f"bedrock/{short_id}"
            response = call_ai(model_id, messages, temperature=0.7, max_tokens=100)
            print(f"✅ Success with short ID!")
            print(f"Response: {response}")
            print()
            break
            
        except Exception as e:
            print(f"❌ Error with short ID {short_id}: {e}")
            print()

def check_environment():
    """Check environment setup"""
    print("=== Environment Check ===")
    
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION"]
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    print()
    
    if not all_set:
        print("⚠️  Please set all required environment variables:")
        print("export AWS_ACCESS_KEY_ID=your_access_key")
        print("export AWS_SECRET_ACCESS_KEY=your_secret_key") 
        print("export AWS_DEFAULT_REGION=ap-northeast-1")
        print()
    
    return all_set

if __name__ == "__main__":
    if not check_environment():
        sys.exit(1)
    
    # Try short IDs first (simpler)
    test_short_ids()
    
    # Then try full ARNs
    test_bedrock_arn() 
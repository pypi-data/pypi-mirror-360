#!/usr/bin/env python3
"""
Simple Bedrock test without inference profiles
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, "src")

from wraipperz.api.llm import call_ai

def test_basic_bedrock():
    """Test basic Bedrock models without inference profiles"""
    
    print("🧪 Testing Basic Bedrock Access")
    print("=" * 40)
    print()
    
    # Simple message
    messages = [
        {"role": "user", "content": "Say 'Hello from Bedrock!' in exactly those words."}
    ]
    
    # Try basic Anthropic models available in most regions
    basic_models = [
        "bedrock/anthropic.claude-3-haiku-20240307-v1:0",
        "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",
        "bedrock/anthropic.claude-v2:1",
    ]
    
    print(f"Current region: {os.getenv('AWS_DEFAULT_REGION', 'not set')}")
    print()
    
    for model in basic_models:
        print(f"Testing: {model.replace('bedrock/', '')}")
        
        try:
            response = call_ai(model, messages, temperature=0.1, max_tokens=50)
            print(f"✅ SUCCESS!")
            print(f"Response: {response}")
            print()
            print("🎉 Bedrock is working! You can use this model.")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "AccessDeniedException" in error_msg:
                print("❌ Access denied - model not available in your account/region")
            elif "ValidationException" in error_msg:
                print("❌ Model not available in this region")
            else:
                print(f"❌ Error: {e}")
        
        print()
    
    print("❌ No basic models accessible.")
    return False

def suggest_setup():
    """Suggest setup steps"""
    
    print("🔧 SETUP SUGGESTIONS:")
    print()
    print("1. **Set your region to match your inference profiles:**")
    print("   export AWS_DEFAULT_REGION=ap-northeast-1")
    print()
    print("2. **Request model access in AWS Console:**")
    print("   - Go to: https://console.aws.amazon.com/bedrock")
    print("   - Navigate to 'Model access'")
    print("   - Request access to Anthropic Claude models")
    print()
    print("3. **Use your inference profiles:**")
    print("   - bedrock/apac.anthropic.claude-3-haiku-20240307-v1:0")
    print("   - bedrock/apac.anthropic.claude-3-5-sonnet-20240620-v1:0")
    print()

if __name__ == "__main__":
    success = test_basic_bedrock()
    
    if not success:
        suggest_setup()
    
    print("💡 Pro tip: Make sure AWS_DEFAULT_REGION matches where your")
    print("   inference profiles are located (ap-northeast-1)") 
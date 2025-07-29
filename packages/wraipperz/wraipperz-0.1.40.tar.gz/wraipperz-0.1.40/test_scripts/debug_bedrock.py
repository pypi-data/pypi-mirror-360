#!/usr/bin/env python3
"""
Debug script to check BedrockProvider registration
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, "src")

def debug_bedrock_setup():
    """Debug the Bedrock provider setup"""
    
    print("=== Debugging Bedrock Provider Setup ===")
    print()
    
    # Check boto3 availability
    try:
        import boto3
        print("✅ boto3 is available")
        BEDROCK_AVAILABLE = True
    except ImportError:
        print("❌ boto3 is NOT available - install with: pip install boto3")
        BEDROCK_AVAILABLE = False
        return
    
    # Check AWS credentials
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_profile = os.getenv("AWS_PROFILE")
    aws_region = os.getenv("AWS_DEFAULT_REGION")
    
    print(f"AWS_ACCESS_KEY_ID: {'✅ Set' if aws_access_key else '❌ Not set'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'✅ Set' if aws_secret_key else '❌ Not set'}")
    print(f"AWS_PROFILE: {'✅ Set' if aws_profile else '❌ Not set'}")
    print(f"AWS_DEFAULT_REGION: {aws_region if aws_region else '❌ Not set'}")
    print()
    
    # Check the condition for adding Bedrock provider
    condition_met = (
        (aws_access_key and aws_secret_key) or
        aws_profile or
        aws_region
    )
    
    print(f"Bedrock provider condition met: {'✅ Yes' if condition_met else '❌ No'}")
    print()
    
    # Try to create BedrockProvider directly
    try:
        from wraipperz.api.llm import BedrockProvider
        provider = BedrockProvider(region_name=aws_region or "us-east-1")
        print("✅ BedrockProvider created successfully")
        print(f"Number of supported models: {len(provider.supported_models)}")
        
        # Check if our APAC models are in the list
        apac_models = [model for model in provider.supported_models if "apac." in model]
        print(f"APAC models found: {len(apac_models)}")
        for model in apac_models[:5]:  # Show first 5
            print(f"  - {model}")
        
    except Exception as e:
        print(f"❌ Error creating BedrockProvider: {e}")
        return
    
    print()
    
    # Check AI manager
    try:
        from wraipperz.api.llm import AIManagerSingleton
        ai_manager = AIManagerSingleton.get_instance()
        
        print("Available providers:")
        for provider_name in ai_manager.providers.keys():
            print(f"  - {provider_name}")
        
        print()
        
        # Try to get provider for our model
        test_model = "bedrock/apac.anthropic.claude-3-5-sonnet-20240620-v1:0"
        try:
            provider = ai_manager.get_provider(test_model)
            print(f"✅ Provider found for {test_model}: {provider.__class__.__name__}")
        except Exception as e:
            print(f"❌ No provider found for {test_model}: {e}")
            
    except Exception as e:
        print(f"❌ Error with AI manager: {e}")

if __name__ == "__main__":
    debug_bedrock_setup() 
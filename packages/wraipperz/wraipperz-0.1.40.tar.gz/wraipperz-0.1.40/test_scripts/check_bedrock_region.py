#!/usr/bin/env python3
"""
Script to check Bedrock inference profiles and region setup
"""

import os
import sys
import boto3
from botocore.exceptions import ClientError

# Add the src directory to Python path
sys.path.insert(0, "src")

def check_bedrock_regions():
    """Check Bedrock setup across regions"""
    
    print("=== Bedrock Region Analysis ===")
    print()
    
    current_region = os.getenv("AWS_DEFAULT_REGION", "not set")
    print(f"Current AWS_DEFAULT_REGION: {current_region}")
    print()
    
    # Test regions where you might have access
    test_regions = ["ap-northeast-1", "ap-southeast-2", "us-east-1"]
    
    for region in test_regions:
        print(f"Testing region: {region}")
        
        try:
            # Create bedrock client for this region
            bedrock = boto3.client("bedrock", region_name=region)
            
            # List available models
            models = bedrock.list_foundation_models()
            anthropic_models = [
                model for model in models['modelSummaries'] 
                if 'anthropic' in model['modelId'].lower()
            ]
            
            print(f"  ✅ Accessible")
            print(f"  📊 Found {len(anthropic_models)} Anthropic models")
            
            if anthropic_models:
                print("  🤖 Available Anthropic models:")
                for model in anthropic_models[:3]:  # Show first 3
                    print(f"    - {model['modelId']}")
                if len(anthropic_models) > 3:
                    print(f"    ... and {len(anthropic_models) - 3} more")
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            print(f"  ❌ Error: {error_code}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()

def check_inference_profiles():
    """Check for inference profiles"""
    
    print("=== Checking Inference Profiles ===")
    print()
    
    regions_to_check = ["ap-northeast-1", "ap-southeast-2"]
    
    for region in regions_to_check:
        print(f"Checking inference profiles in {region}:")
        
        try:
            bedrock = boto3.client("bedrock", region_name=region)
            
            # Try to list inference profiles (this might not be supported in all regions)
            try:
                response = bedrock.list_inference_profiles()
                profiles = response.get('inferenceProfileSummaries', [])
                
                print(f"  ✅ Found {len(profiles)} inference profiles")
                
                for profile in profiles[:5]:  # Show first 5
                    print(f"    - ID: {profile['inferenceProfileId']}")
                    print(f"      Name: {profile.get('inferenceProfileName', 'N/A')}")
                    
            except Exception as e:
                print(f"  ⚠️  Inference profiles API not available: {e}")
                
        except Exception as e:
            print(f"  ❌ Cannot access region {region}: {e}")
        
        print()

def test_simple_models():
    """Test basic model access without inference profiles"""
    
    print("=== Testing Basic Model Access ===")
    print()
    
    regions_to_test = ["ap-northeast-1", "us-east-1"]
    basic_models = [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-5-sonnet-20240620-v1:0"
    ]
    
    for region in regions_to_test:
        print(f"Testing basic models in {region}:")
        
        try:
            bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)
            
            for model_id in basic_models:
                try:
                    # Try a minimal request
                    request_body = {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": [{"type": "text", "text": "Hi"}]}]
                    }
                    
                    response = bedrock_runtime.invoke_model(
                        modelId=model_id,
                        body=str(request_body).replace("'", '"'),
                        contentType="application/json"
                    )
                    
                    print(f"  ✅ {model_id} - ACCESSIBLE")
                    return region, model_id  # Found working combination
                    
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                    print(f"  ❌ {model_id} - {error_code}")
                except Exception as e:
                    print(f"  ❌ {model_id} - {e}")
                    
        except Exception as e:
            print(f"  ❌ Cannot access region {region}: {e}")
        
        print()
    
    return None, None

def main():
    print("🔍 Bedrock Access Diagnostic Tool")
    print("=" * 50)
    print()
    
    # Check environment
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return
    
    # Run checks
    check_bedrock_regions()
    check_inference_profiles()
    
    working_region, working_model = test_simple_models()
    
    print("=" * 50)
    print("📋 RECOMMENDATIONS:")
    print()
    
    if working_region and working_model:
        print(f"✅ FOUND WORKING SETUP:")
        print(f"   Region: {working_region}")
        print(f"   Model: {working_model}")
        print()
        print("🔧 To use this setup:")
        print(f"   export AWS_DEFAULT_REGION={working_region}")
        print(f"   # Then use: bedrock/{working_model}")
        print()
    else:
        print("❌ No basic model access found.")
        print()
        print("🔧 NEXT STEPS:")
        print("1. Check AWS Bedrock Console for model access")
        print("2. Request access to Anthropic models in your region")
        print("3. Try a different region where you have access")
        print()
        print("🌍 Common regions for Bedrock:")
        print("   - us-east-1 (N. Virginia)")
        print("   - us-west-2 (Oregon)")  
        print("   - ap-northeast-1 (Tokyo)")
        print("   - eu-central-1 (Frankfurt)")

if __name__ == "__main__":
    main() 
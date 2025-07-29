"""
Test script for verifying the fix to prevent unwanted API calls when using the wraipperz library.

This test specifically checks that:
1. When using a Pixverse model, only Pixverse API calls are made (no FAL calls)
2. When using a FAL model, only FAL API calls are made (no Pixverse calls)

Run this test with:
python test_providers.py path_to_test_image.png

Note: You need to have the appropriate API keys in your .env file:
- PIXVERSE_API_KEY for testing Pixverse models
- FAL_KEY for testing FAL models
"""

import os
import sys
from pathlib import Path
import time
import logging
from dotenv import load_dotenv
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ProviderTest")

# Add the project root to the Python path if needed
sys.path.append('.')

# Import from wraipperz
try:
    from wraipperz.api.video_gen import (
        generate_video_from_image, 
        VideoGenManagerSingleton,
        FalProvider,
        PixVerseProvider
    )
except ImportError:
    try:
        from src.wraipperz.api.video_gen import (
            generate_video_from_image, 
            VideoGenManagerSingleton,
            FalProvider,
            PixVerseProvider
        )
    except ImportError:
        print("ERROR: Could not import the wraipperz library. Make sure it's installed.")
        sys.exit(1)

# Load environment variables
load_dotenv(override=True)

# Tracking API calls
pixverse_api_calls = []
fal_api_calls = []

# Store original methods
original_pixverse_image_to_video = None
original_fal_image_to_video = None
original_pixverse_get_video_status = None
original_fal_get_video_status = None

def patch_providers():
    """Patch both PixVerse and FAL providers to track API calls"""
    global original_pixverse_image_to_video, original_fal_image_to_video
    global original_pixverse_get_video_status, original_fal_get_video_status
    
    # Get the manager instance
    manager = VideoGenManagerSingleton.get_instance()
    
    # Find and patch the providers
    for provider_name, provider in manager.providers.items():
        if isinstance(provider, PixVerseProvider):
            # Save original methods
            original_pixverse_image_to_video = provider.image_to_video
            original_pixverse_get_video_status = provider.get_video_status
            
            # Replace with tracked versions
            def tracked_pixverse_image_to_video(self, image_path, prompt, negative_prompt=None, **kwargs):
                pixverse_api_calls.append(f"PixVerse API call: image_to_video({prompt[:20]}...)")
                logger.info(f"PixVerse API call: image_to_video({prompt[:20]}...)")
                return original_pixverse_image_to_video(image_path, prompt, negative_prompt, **kwargs)
            
            def tracked_pixverse_get_video_status(self, video_id):
                pixverse_api_calls.append(f"PixVerse API call: get_video_status({video_id})")
                logger.info(f"PixVerse API call: get_video_status({video_id})")
                return original_pixverse_get_video_status(video_id)
            
            # Apply patches
            provider.image_to_video = tracked_pixverse_image_to_video.__get__(provider, PixVerseProvider)
            provider.get_video_status = tracked_pixverse_get_video_status.__get__(provider, PixVerseProvider)
            logger.info("PixVerse provider patched for tracking")
            
        elif isinstance(provider, FalProvider):
            # Save original methods
            original_fal_image_to_video = provider.image_to_video
            original_fal_get_video_status = provider.get_video_status
            
            # Replace with tracked versions
            def tracked_fal_image_to_video(self, image_path, prompt, negative_prompt=None, **kwargs):
                fal_api_calls.append(f"FAL API call: image_to_video({prompt[:20]}...)")
                logger.info(f"FAL API call: image_to_video({prompt[:20]}...)")
                return original_fal_image_to_video(image_path, prompt, negative_prompt, **kwargs)
            
            def tracked_fal_get_video_status(self, video_id):
                fal_api_calls.append(f"FAL API call: get_video_status({video_id})")
                logger.info(f"FAL API call: get_video_status({video_id})")
                return original_fal_get_video_status(video_id)
            
            # Apply patches
            provider.image_to_video = tracked_fal_image_to_video.__get__(provider, FalProvider)
            provider.get_video_status = tracked_fal_get_video_status.__get__(provider, FalProvider)
            logger.info("FAL provider patched for tracking")

def unpatch_providers():
    """Restore original methods for both providers"""
    global original_pixverse_image_to_video, original_fal_image_to_video
    global original_pixverse_get_video_status, original_fal_get_video_status
    
    # Get the manager instance
    manager = VideoGenManagerSingleton.get_instance()
    
    # Restore original methods
    for provider_name, provider in manager.providers.items():
        if isinstance(provider, PixVerseProvider):
            if original_pixverse_image_to_video:
                provider.image_to_video = original_pixverse_image_to_video
            if original_pixverse_get_video_status:
                provider.get_video_status = original_pixverse_get_video_status
            logger.info("PixVerse provider unpatched")
            
        elif isinstance(provider, FalProvider):
            if original_fal_image_to_video:
                provider.image_to_video = original_fal_image_to_video
            if original_fal_get_video_status:
                provider.get_video_status = original_fal_get_video_status
            logger.info("FAL provider unpatched")

def test_model(model_name, image_path, prompt, expected_provider_type):
    """Test video generation with a specific model and verify correct provider is used"""
    logger.info(f"\n{'='*80}")
    logger.info(f"TESTING MODEL: {model_name}")
    logger.info(f"EXPECTED PROVIDER TYPE: {expected_provider_type.__name__}")
    logger.info(f"{'='*80}")
    
    output_filename = f"{model_name.split('/')[-1].replace('-', '_')}_test.mp4"
    
    logger.info(f"Input image: {image_path}")
    logger.info(f"Prompt: {prompt}")
    logger.info(f"Output file: {output_filename}")
    
    try:
        # Reset tracking lists
        pixverse_api_calls.clear()
        fal_api_calls.clear()
        
        # Patch providers to track API calls
        patch_providers()
        
        # Start a timer
        start_time = time.time()
        
        # Convert the image to a video
        result = generate_video_from_image(
            model=model_name,
            image_path=image_path,
            prompt=prompt,
            negative_prompt="low quality, blurry",
            duration=5,
            quality="720p",
            wait_for_completion=False  # Don't wait to avoid long test times
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Request completed in {elapsed:.2f} seconds")
        
        # Check API calls
        logger.info(f"PixVerse API calls: {len(pixverse_api_calls)}")
        for call in pixverse_api_calls:
            logger.info(f"  - {call}")
            
        logger.info(f"FAL API calls: {len(fal_api_calls)}")
        for call in fal_api_calls:
            logger.info(f"  - {call}")
        
        # Verify correct provider was used
        if expected_provider_type == PixVerseProvider:
            if len(pixverse_api_calls) > 0 and len(fal_api_calls) == 0:
                logger.info("✅ PASS: Only PixVerse API was called, as expected")
            else:
                logger.error("❌ FAIL: Expected only PixVerse API calls")
                if len(fal_api_calls) > 0:
                    logger.error("   Unwanted FAL API calls detected!")
        elif expected_provider_type == FalProvider:
            if len(fal_api_calls) > 0 and len(pixverse_api_calls) == 0:
                logger.info("✅ PASS: Only FAL API was called, as expected")
            else:
                logger.error("❌ FAIL: Expected only FAL API calls")
                if len(pixverse_api_calls) > 0:
                    logger.error("   Unwanted PixVerse API calls detected!")
        
        # Unpatch before returning
        unpatch_providers()
        
        return True
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        
        # Unpatch in case of error
        unpatch_providers()
        
        return False

if __name__ == "__main__":
    # Check if API keys are available
    has_pixverse_key = os.getenv("PIXVERSE_API_KEY") is not None
    has_fal_key = os.getenv("FAL_KEY") is not None
    
    if not (has_pixverse_key or has_fal_key):
        logger.error("ERROR: No API keys found. Set PIXVERSE_API_KEY or FAL_KEY environment variables.")
        sys.exit(1)
    
    # Check if an image path is provided as a command-line argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Use a default test image if none provided
        image_path = "test_image.png"
    
    # Verify image exists
    if not Path(image_path).exists():
        logger.error(f"ERROR: Image file not found: {image_path}")
        logger.error("Please provide a valid image path as the first argument or create a 'test_image.png' file.")
        sys.exit(1)
    
    # Set up the prompt
    prompt = "Add gentle motion and subtle animation. Maintain the original composition."
    
    # Test PixVerse if key is available
    if has_pixverse_key:
        test_model("pixverse/image-to-video-v4.0", image_path, prompt, PixVerseProvider)
    else:
        logger.warning("Skipping PixVerse test: No API key available")
    
    # Test FAL if key is available
    if has_fal_key:
        test_model("fal/minimax-video", image_path, prompt, FalProvider)
    else:
        logger.warning("Skipping FAL test: No API key available")
    
    # Run a final verification test - this should only use PixVerse
    if has_pixverse_key and has_fal_key:
        logger.info("\n\n")
        logger.info(f"{'='*80}")
        logger.info("RUNNING FINAL VERIFICATION TEST (PixVerse model with both providers available)")
        logger.info(f"{'='*80}")
        test_model("pixverse/image-to-video-v4.0", image_path, prompt, PixVerseProvider)
        
    logger.info("\nAll tests completed!") 
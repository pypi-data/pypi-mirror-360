import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PixverseTest")

# Add the project root to the Python path if needed
sys.path.append('.')

# Try to import from wraipperz
try:
    from wraipperz.api.video_gen import (
        generate_video_from_image, 
        wait_for_video_completion,
        VideoGenManagerSingleton,
        FalProvider
    )
except ImportError:
    try:
        from src.wraipperz.api.video_gen import (
            generate_video_from_image, 
            wait_for_video_completion,
            VideoGenManagerSingleton,
            FalProvider
        )
    except ImportError:
        print("ERROR: Could not import the wraipperz library. Make sure it's installed.")
        sys.exit(1)

# Load environment variables
load_dotenv(override=True)

# Patch FAL provider to track API calls
fal_api_calls = []

# Get the original methods
original_fal_get_video_status = None
original_fal_image_to_video = None

def patch_fal_provider():
    global original_fal_get_video_status, original_fal_image_to_video
    
    # Get the manager instance
    manager = VideoGenManagerSingleton.get_instance()
    
    # Find the FAL provider
    fal_provider = None
    for provider_name, provider in manager.providers.items():
        if isinstance(provider, FalProvider):
            fal_provider = provider
            break
    
    if fal_provider:
        # Save the original methods
        original_fal_get_video_status = fal_provider.get_video_status
        original_fal_image_to_video = fal_provider.image_to_video
        
        # Replace with our tracked versions
        def tracked_get_video_status(self, video_id):
            fal_api_calls.append(f"FAL API call: get_video_status({video_id})")
            logger.warning(f"DETECTED UNWANTED FAL API CALL: get_video_status({video_id})")
            return original_fal_get_video_status(video_id)
        
        def tracked_image_to_video(self, image_path, prompt, negative_prompt=None, **kwargs):
            fal_api_calls.append(f"FAL API call: image_to_video({prompt[:20]}...)")
            logger.warning(f"DETECTED UNWANTED FAL API CALL: image_to_video({prompt[:20]}...)")
            return original_fal_image_to_video(image_path, prompt, negative_prompt, **kwargs)
        
        # Apply the patches
        fal_provider.get_video_status = tracked_get_video_status.__get__(fal_provider, FalProvider)
        fal_provider.image_to_video = tracked_image_to_video.__get__(fal_provider, FalProvider)
        logger.info("FAL provider patched for tracking")
    else:
        logger.info("FAL provider not found, no patching needed")

def unpatch_fal_provider():
    global original_fal_get_video_status, original_fal_image_to_video
    
    # Get the manager instance
    manager = VideoGenManagerSingleton.get_instance()
    
    # Find the FAL provider
    fal_provider = None
    for provider_name, provider in manager.providers.items():
        if isinstance(provider, FalProvider):
            fal_provider = provider
            break
    
    if fal_provider:
        # Restore the original methods
        if original_fal_get_video_status:
            fal_provider.get_video_status = original_fal_get_video_status
        if original_fal_image_to_video:
            fal_provider.image_to_video = original_fal_image_to_video
        logger.info("FAL provider unpatched")

# Function to test video generation with a specific model
def test_model(model_name, image_path, prompt):
    logger.info(f"\n{'='*50}")
    logger.info(f"TESTING MODEL: {model_name}")
    logger.info(f"{'='*50}")
    
    output_filename = f"pixverse_{model_name.split('/')[-1].replace('-', '_')}.mp4"
    
    logger.info(f"Input image: {image_path}")
    logger.info(f"Prompt: {prompt}")
    logger.info(f"Output file: {output_filename}")
    
    try:
        # Reset tracking list before each test
        fal_api_calls.clear()
        
        # Patch the FAL provider to track API calls
        patch_fal_provider()
        
        # Convert the image to a video with motion
        result = generate_video_from_image(
            model=model_name,
            image_path=image_path,
            prompt=prompt,
            negative_prompt="low quality, blurry",
            duration=5,
            quality="720p",
            motion_mode="normal",
            wait_for_completion=True,
            output_path=output_filename,
            max_wait_time=300  # Wait up to 5 minutes for completion
        )
        
        logger.info("\nVIDEO GENERATION RESULT:")
        logger.info(f"Video ID: {result.get('video_id', 'unknown')}")
        logger.info(f"Request ID: {result.get('request_id', 'unknown')}")
        
        if 'file_path' in result:
            logger.info(f"SUCCESS! Video downloaded to: {result['file_path']}")
        else:
            logger.info("The video was generated but could not be automatically downloaded.")
            logger.info(f"Video URL (if available): {result.get('url', 'Not available')}")
            logger.info("You can access your videos in the Pixverse dashboard: https://app.pixverse.ai/studio")
        
        # Check if any unwanted FAL API calls were made
        if fal_api_calls:
            logger.error(f"PROBLEM DETECTED: {len(fal_api_calls)} unwanted FAL API calls were made:")
            for call in fal_api_calls:
                logger.error(f"  - {call}")
            logger.error("The fix for preventing unwanted FAL API calls is not working!")
        else:
            logger.info("VERIFICATION SUCCESSFUL: No unwanted FAL API calls detected!")
        
        # Unpatch before returning
        unpatch_fal_provider()
        
        return True
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        
        # Unpatch in case of error
        unpatch_fal_provider()
        
        return False

# Main execution
if __name__ == "__main__":
    # Check if an image path is provided as a command-line argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Use a default test image if none provided
        image_path = "EP001_01_06.png"
    
    # Verify image exists
    if not Path(image_path).exists():
        logger.error(f"ERROR: Image file not found: {image_path}")
        logger.error("Please provide a valid image path as the first argument or create a 'test_image.png' file.")
        sys.exit(1)
    
    # Set up the prompt
    prompt = "Add gentle motion and subtle animation. Maintain the original composition. Good quality, detailed animation."
    
    # Test v4.0 model (will be converted to v4 internally)
    test_model("pixverse/image-to-video-v4.0", image_path, prompt)
    
    # Test v4.5 model
    # test_model("pixverse/image-to-video-v4.5", image_path, prompt)
    
    logger.info("\nAll tests completed. Check the output files if successful.") 
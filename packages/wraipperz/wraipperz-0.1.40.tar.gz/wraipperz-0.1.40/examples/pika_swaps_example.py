#!/usr/bin/env python
# Example script for using Pika Swaps for video-to-video inpainting

import os
import time
from dotenv import load_dotenv
from pathlib import Path
from wraipperz.api import video_gen

# Load environment variables from .env file (should contain FAL_KEY)
load_dotenv()

def main():
    # Check if FAL_KEY is set
    if not os.getenv("FAL_KEY"):
        print("Error: FAL_KEY environment variable not set")
        print("Please set it in a .env file or directly in your environment")
        return
    
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # ----- OPTION 1: Using a URL for the input video -----
    video_url = "https://v3.fal.media/files/monkey/vXi5n_oq0Qpnbs7Eb2k-b_output.mp4"
    
    # ----- OPTION 2: Using a local video file -----
    # Path to your local video file
    # Uncomment the next line and comment out the video_url above to use a local file
    # video_url = Path("path/to/your/local/video.mp4")
    
    # Optional: URL or path to image to swap with
    # image_url = "https://example.com/your-image.jpg"
    # OR local image:
    # image_url = Path("path/to/your/local/image.jpg")
    
    # Define the prompt and region to modify
    prompt = "Replace the background with a vibrant beach scene"
    modify_region = "the background"
    
    print(f"Generating inpainted video...")
    print(f"Input video: {video_url}")
    print(f"Prompt: {prompt}")
    print(f"Region to modify: {modify_region}")
    
    try:
        
        # Generate the modified video
        result = video_gen.generate_video_from_video(
            model="fal/pika-swaps-v2",
            video_url=video_url,
            prompt=prompt,
            modify_region=modify_region,
            # image_url=image_url,  # Uncomment to use an image for swapping
            wait_for_completion=True,  # Wait for the video to be generated
            output_path="output/pika_swaps_result.mp4"  # Where to save the result
        )
        
        print("\nResult:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"URL: {result.get('url', 'N/A')}")
        
        if "file_path" in result:
            print(f"Saved to: {result['file_path']}")
            print(f"Video successfully saved as: {result['file_path']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 
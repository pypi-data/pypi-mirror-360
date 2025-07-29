import os
from wraipperz import generate_video_from_image, wait_for_video_completion
from PIL import Image
from dotenv import load_dotenv

load_dotenv(override=True)


# Convert the image to a video with motion and try to download automatically
result = generate_video_from_image(
    model="pixverse/image-to-video-v4.0",
    image_path="test_image2.png",  # Can also be a file path string
    prompt="Static image of a city",
    negative_prompt="",
    duration=5,
    quality="720p",
    wait_for_completion=True,  # Try waiting with our improved mechanism
    output_path="animated_image_pixaverse2.mp4",  # Specify full path with extension
    max_wait_time=300  # Wait up to 5 minutes for completion
)

print("\nVIDEO GENERATION RESULT:")
print(f"Video ID: {result.get('video_id', 'unknown')}")
print(f"Request ID: {result.get('request_id', 'unknown')}")

if 'file_path' in result:
    print(f"SUCCESS! Video downloaded to: {result['file_path']}")
else:
    print("The video was generated but could not be automatically downloaded.")
    print(f"Video URL (if available): {result.get('url', 'Not available')}")
    print("You can access your videos in the Pixverse dashboard: https://app.pixverse.ai/studio")
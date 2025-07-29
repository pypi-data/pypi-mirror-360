import os
from wraipperz import generate_video_from_image
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Models to test (excluding veo2 and kling)
models = [
    "fal/pixverse-v4",
    # "fal/wan-pro", 
    #"fal/magi-distilled",
    #"fal/vidu",
    #"fal/ltx-video-v095"
]

# Test image and prompt to use for all models
image_path = "test_image2.png"
prompt = "static webtoon"

# Process each model
for model in models:
    print(f"\n\n==== Testing model: {model} ====")
    
    # Extract model name for filename
    model_name = model.split('/')[1]
    output_path = f"output_{model_name}.mp4"
    
    try:
        result = generate_video_from_image(
            model=model,
            image_path=image_path,
            prompt=prompt,
            duration="5",
            aspect_ratio="9:16",
            wait_for_completion=True,
            output_path=output_path,
            quality="720p"
        )
        
        print(f"✅ Success for {model}")
        print(f"Video downloaded to: {result['file_path']}")
    except Exception as e:
        print(f"❌ Error with {model}: {str(e)}")
        
print("\n\nTesting complete!")


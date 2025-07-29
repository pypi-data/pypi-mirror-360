import requests
import json
import base64
import uuid
import time
import sys
from pathlib import Path

# Step 1: Upload the image and get an img_id
def upload_image(api_key, image_path):
    # Use the correct API endpoint for image upload
    upload_url = "https://app-api.pixverse.ai/openapi/v2/image/upload"
    
    # Create unique trace ID
    ai_trace_id = str(uuid.uuid4())
    
    # Prepare headers
    headers = {
        "API-KEY": api_key,
        "Ai-trace-id": ai_trace_id
    }
    
    # Prepare files for multipart/form-data
    files = [
        ('image', (Path(image_path).name, open(image_path, 'rb'), 'application/octet-stream'))
    ]
    
    # Make upload request
    print("Uploading image...")
    upload_response = requests.post(upload_url, headers=headers, files=files)
    print(f"Upload response: {upload_response.text}")
    
    # Check if successful
    upload_result = upload_response.json()
    if upload_result.get("ErrCode") != 0:
        raise ValueError(f"Image upload failed: {upload_result.get('ErrMsg')}")
    
    # Get img_id from the response
    img_id = upload_result["Resp"]["img_id"]
    print(f"Uploaded image ID: {img_id}")
    return img_id

# Step 2: Generate video from image ID with model v4.0
def generate_video(api_key, img_id, prompt):
    url = "https://app-api.pixverse.ai/openapi/v2/video/img/generate"
    
    # Create unique trace ID
    ai_trace_id = str(uuid.uuid4())
    
    # Create payload as a dictionary first
    payload_dict = {
        "duration": 5,  # Integer, not string
        "img_id": img_id,
        "model": "v4",  # Changed from v4.0 to v4 (exact format from API docs)
        "motion_mode": "normal",
        "negative_prompt": "low quality, blurry",
        "prompt": prompt,
        "quality": "720p",  # Upgraded from 540p to 720p
        "seed": 99,
        "water_mark": False  # Python False will be properly converted to JSON false
    }
    
    # Convert to JSON string
    payload = json.dumps(payload_dict)
    
    headers = {
        "API-KEY": api_key,
        "Ai-trace-id": ai_trace_id,
        "Content-Type": "application/json"
    }
    
    print("Generating video...")
    print(f"Using payload: {payload}")
    response = requests.post(url, headers=headers, data=payload)
    print(f"Generation response: {response.text}")
    
    # Check if successful
    result = response.json()
    if result.get("ErrCode") != 0:
        raise ValueError(f"Video generation failed: {result.get('ErrMsg')}")
    
    return result["Resp"]["video_id"], ai_trace_id

# Step 2 Alternative: Generate video using v4.5 model
def generate_video_v45(api_key, img_id, prompt):
    url = "https://app-api.pixverse.ai/openapi/v2/video/img/generate"
    
    # Create unique trace ID
    ai_trace_id = str(uuid.uuid4())
    
    # Create payload as a dictionary first
    payload_dict = {
        "duration": 5,  # Integer, not string
        "img_id": img_id,
        "model": "v4.5",  # Using the exact v4.5 model name from API docs
        "motion_mode": "normal",
        "negative_prompt": "low quality, blurry",
        "prompt": prompt,
        "quality": "720p",
        "seed": 42,
        "water_mark": False  # Python False will be properly converted to JSON false
    }
    
    # Convert to JSON string
    payload = json.dumps(payload_dict)
    
    headers = {
        "API-KEY": api_key,
        "Ai-trace-id": ai_trace_id,
        "Content-Type": "application/json"
    }
    
    print("Generating video with v4.5 model...")
    print(f"Using payload: {payload}")
    response = requests.post(url, headers=headers, data=payload)
    print(f"Generation response: {response.text}")
    
    # Check if successful
    result = response.json()
    if result.get("ErrCode") != 0:
        raise ValueError(f"Video generation failed: {result.get('ErrMsg')}")
    
    return result["Resp"]["video_id"], ai_trace_id

# Step 3: Try multiple approaches to check video status
def wait_for_video_completion(api_key, video_id, trace_id, max_attempts=30, interval=10):
    print(f"Waiting for video with ID {video_id} to complete...")
    
    # Base headers for all requests
    base_headers = {
        "API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    # Different endpoints to try - CORRECT ONE FIRST based on the example code
    endpoints = [
        # Main endpoint that should work based on the example code
        {"url": f"https://app-api.pixverse.ai/openapi/v2/video/result/{video_id}", "method": "GET"},
        # Fallback options
        {"url": "https://app-api.pixverse.ai/openapi/v2/video/status", "method": "GET", "params": {"video_id": video_id}},
        {"url": "https://app-api.pixverse.ai/openapi/v2/video/query", "method": "POST", "body": {"video_id": video_id}},
        {"url": "https://app-api.pixverse.ai/openapi/v1/video/status", "method": "GET", "params": {"video_id": video_id}},
        {"url": "https://app-api.pixverse.ai/openapi/v2/video/get", "method": "GET", "params": {"trace_id": trace_id}}
    ]
    
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        print(f"\nAttempt {attempt}/{max_attempts}:")
        
        # Try each endpoint
        for endpoint in endpoints:
            try:
                print(f"Trying endpoint: {endpoint['url']}")
                
                if endpoint.get("method") == "GET":
                    response = requests.get(
                        endpoint["url"], 
                        headers=base_headers, 
                        params=endpoint.get("params", {})
                    )
                else:  # POST
                    response = requests.post(
                        endpoint["url"],
                        headers=base_headers,
                        data=json.dumps(endpoint.get("body", {}))
                    )
                
                # Print response for debugging
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:200]}..." if len(response.text) > 200 else f"Response: {response.text}")
                
                # If we get a successful response
                if response.status_code == 200:
                    try:
                        result = response.json()
                        
                        # Different APIs might have different response structures
                        # Try to extract the relevant fields
                        
                        # Case 1: Standard API response with ErrCode/Resp structure
                        if "ErrCode" in result and result["ErrCode"] == 0 and "Resp" in result:
                            resp = result["Resp"]
                            
                            # Check if the video is ready or still processing
                            if isinstance(resp, dict):
                                # Check the status code
                                status_code = resp.get("status")
                                
                                # Status code values (from example code):
                                # 1 = Success
                                # 5 = Processing
                                # 2,3,4 = Failed, Timeout, Rejected
                                
                                if status_code == 1:  # Success
                                    # Extract URL if present
                                    if "url" in resp and resp["url"]:
                                        print(f"Video is ready! URL: {resp['url']}")
                                        return resp["url"]
                                elif status_code == 5:  # Still processing
                                    print(f"Video is still processing... Waiting {interval} seconds.")
                                    # Continue to next attempt
                                    break
                                elif status_code in [2, 3, 4]:  # Failed states
                                    status_messages = {
                                        2: "Failed",
                                        3: "Timeout",
                                        4: "Rejected"
                                    }
                                    print(f"Video generation {status_messages.get(status_code, 'failed')}.")
                                    return None
                                
                        # Case 2: Direct JSON response with URL
                        if "url" in result and result["url"]:
                            print(f"Found video URL: {result['url']}")
                            return result["url"]
                            
                        # Case 3: Direct JSON response with status
                        if "status" in result:
                            status = result["status"]
                            if status == 1:  # Success
                                if "url" in result and result["url"]:
                                    print(f"Found video URL: {result['url']}")
                                    return result["url"]
                            elif status == 5:  # Processing
                                print(f"Video is still processing... Waiting {interval} seconds.")
                                # Continue to next attempt
                                break
                    except Exception as e:
                        print(f"Error parsing response: {str(e)}")
            except Exception as e:
                print(f"Error with endpoint {endpoint['url']}: {str(e)}")
        
        # Wait before next attempt
        print(f"Video not ready yet, waiting {interval} seconds...")
        time.sleep(interval)
    
    print("Max attempts reached. Video generation might still be in progress.")
    print("You can access the video from the PixVerse dashboard: https://app.pixverse.ai/studio")
    return None

# Step 4: Download the video
def download_video(api_key, video_url, output_path):
    if not video_url:
        print("No video URL available to download.")
        return None
    
    headers = {
        "API-KEY": api_key
    }
    
    try:
        print(f"Downloading video from {video_url} to {output_path}...")
        response = requests.get(video_url, headers=headers, stream=True)
        
        if response.status_code != 200:
            print(f"Download failed with status code {response.status_code}: {response.text}")
            return None
        
        # Save the video file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Video downloaded successfully to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None

# Main execution
if __name__ == "__main__":
    # Your API key
    api_key = "sk-868a5bc41520503eff11aba5c17fbf61"
    
    # Path to your image
    image_path = "EP001_02_03.png"
    
    # Prompt for video
    prompt = "Anime-style comic panel. Minimal motion: soft hair sway very light shadow movement. No major camera movement. Keep the composition fixed, like a living manga panel. Stylized 2D line art with clean webtoon rendering, warm indoor lighting. No sound or dialogue. Calm, slightly awkward atmosphere. Hair and clothes slightly moving in the wind. Silent."
    
    try:
        # Step 1: Upload image
        img_id = upload_image(api_key, image_path)
        
        # Choose which model to test
        print("\n=== Choose a model to test ===")
        print("1. PixVerse v4.0")
        print("2. PixVerse v4.5")
        choice = input("Enter choice (1 or 2): ")
        
        if choice == "2":
            # Test with v4.5
            output_path = "pixverse_v45_video.mp4"
            print("\n=== Testing PixVerse v4.5 model ===")
            video_id, trace_id = generate_video_v45(api_key, img_id, prompt)
            print(f"Video generation started with v4.5 model. ID: {video_id}, trace ID: {trace_id}")
        else:
            # Default to v4.0
            output_path = "pixverse_v40_video.mp4"
            print("\n=== Testing PixVerse v4.0 model ===")
            video_id, trace_id = generate_video(api_key, img_id, prompt)
            print(f"Video generation started with v4.0 model. ID: {video_id}, trace ID: {trace_id}")
        
        # Step 3: Wait for completion and get URL
        video_url = wait_for_video_completion(api_key, video_id, trace_id)
        
        # Step 4: Download the video if URL is available
        if video_url:
            downloaded_path = download_video(api_key, video_url, output_path)
            if downloaded_path:
                print(f"Success! Video downloaded to: {downloaded_path}")
            else:
                print("Video was generated but could not be downloaded automatically.")
                print(f"Video URL: {video_url}")
        else:
            print("Video was generated but the URL could not be retrieved automatically.")
            print("You can access your videos in the PixVerse dashboard: https://app.pixverse.ai/studio")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
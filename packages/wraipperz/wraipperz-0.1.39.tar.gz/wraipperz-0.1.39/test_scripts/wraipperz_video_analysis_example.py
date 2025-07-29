"""
Enhanced Gemini Video Analysis with Wraipperz

This example shows how to use the enhanced wraipperz library to achieve 
the same video analysis functionality as your hardcoded implementation.

Features demonstrated:
- Video file upload and processing
- Thinking budget configuration
- Advanced safety settings (already configured)
- Structured output with Pydantic models
- Error handling and fallback mechanisms
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

from wraipperz import call_ai, MessageBuilder


class LineAnalysis(BaseModel):
    """Analysis of a single dialogue line from video."""
    
    action: str = Field(
        description="Description of the character's actions or expressions",
        json_schema_extra={"example": "Character looks worried and fidgets with their hands"}
    )
    
    voice_type: str = Field(
        description="Voice type: VO for voice over, OFF for offscreen, WHISPER for whispers, or NORMAL for normal voices",
        json_schema_extra={"example": "NORMAL"}
    )
    
    location: str = Field(
        description="The location where the dialogue takes place",
        json_schema_extra={"example": "Living room"}
    )
    
    time_of_day: str = Field(
        description="Time of day (e.g., DAY, NIGHT, MORNING, etc.)",
        json_schema_extra={"example": "DAY"}
    )
    
    translation: str = Field(
        description="High-quality English translation of the dialogue",
        json_schema_extra={"example": "I can't believe this is happening."}
    )
    
    scene_change: Optional[str] = Field(
        default="",
        description="Brief description of scene change if any, empty if no scene change",
        json_schema_extra={"example": "Characters move to the kitchen to prepare dinner"}
    )


class VideoAnalysisResponse(BaseModel):
    """Complete video analysis response containing all line analyses."""
    
    lines: List[LineAnalysis] = Field(
        description="Analysis for each line of dialogue in the script, in order"
    )


def analyze_video_with_wraipperz(
    video_path: str,
    prompt: str,
    model: str = "gemini/gemini-2.5-pro-preview-06-05",
    thinking_budget: int = 24576,
    max_tokens: int = 4096,
    temperature: float = 0.2
):
    """
    Analyze a video using the enhanced wraipperz Gemini provider.
    
    Args:
        video_path: Path to the video file
        prompt: Analysis prompt for the video
        model: Gemini model to use
        thinking_budget: Thinking budget in tokens
        max_tokens: Maximum output tokens
        temperature: Temperature for generation
        
    Returns:
        Tuple of (response_text, cost)
    """
    
    # Build messages with video support
    messages = (
        MessageBuilder()
        .add_system(
            "You are a professional video analyst specializing in dialogue, "
            "action, and scene analysis. Analyze videos with comprehensive "
            "safety settings configured to BLOCK_NONE for all adjustable categories."
        )
        .add_video(video_path, prompt)
        .build()
    )
    
    try:
        # Call AI with thinking budget and structured output
        response, cost = call_ai(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_budget=thinking_budget,  # Enable thinking with budget
            response_schema=VideoAnalysisResponse,  # Structured output
            response_mime_type="application/json"
        )
        
        return response, cost
        
    except Exception as e:
        print(f"❌ Video analysis failed: {e}")
        
        # Implement fallback to script-only analysis if needed
        fallback_prompt = f"""
        Video processing failed. Please provide analysis based on this prompt instead:
        {prompt}
        
        Provide a structured response following the same format but with placeholder values.
        """
        
        fallback_messages = (
            MessageBuilder()
            .add_system("You are a helpful assistant providing fallback analysis.")
            .add_user(fallback_prompt)
            .build()
        )
        
        try:
            fallback_response, fallback_cost = call_ai(
                model="gemini/gemini-2.0-flash-exp",  # Use faster model for fallback
                messages=fallback_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_schema=VideoAnalysisResponse,
                response_mime_type="application/json"
            )
            
            print("🔄 Used fallback analysis")
            return fallback_response, fallback_cost
            
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            raise


def main():
    """Example usage of video analysis with wraipperz."""
    
    # Set your API key
    os.environ["GOOGLE_API_KEY"] = "your-google-api-key"
    
    # Video analysis prompt similar to your hardcoded implementation
    analysis_prompt = """
    Analyze this video and provide detailed information for each line of dialogue.
    Focus on:
    1. Character actions and expressions
    2. Voice type (normal, whisper, off-screen, voice-over)
    3. Location/setting details
    4. Time of day
    5. High-quality English translation if needed
    6. Scene changes between lines
    
    Provide comprehensive analysis while maintaining safety and accuracy.
    """
    
    # Example video file
    video_file = "path/to/your/video.mp4"
    
    if not Path(video_file).exists():
        print(f"❌ Video file not found: {video_file}")
        print("Please update the video_file path to point to an actual video.")
        return
    
    try:
        print(f"🎬 Analyzing video: {video_file}")
        print(f"🧠 Using thinking budget: 24576 tokens")
        
        # Analyze the video
        response, cost = analyze_video_with_wraipperz(
            video_path=video_file,
            prompt=analysis_prompt,
            model="gemini/gemini-2.5-pro-preview-06-05",
            thinking_budget=24576,
            max_tokens=4096,
            temperature=0.2
        )
        
        print(f"✅ Analysis completed!")
        print(f"💰 Cost: ${cost}")
        print(f"📝 Response preview: {str(response)[:200]}...")
        
        # Parse the structured response if it's JSON
        if isinstance(response, str):
            import json
            try:
                parsed_response = json.loads(response)
                print(f"📊 Found {len(parsed_response.get('lines', []))} dialogue lines analyzed")
            except json.JSONDecodeError:
                print("📄 Response is text format")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")


if __name__ == "__main__":
    main() 
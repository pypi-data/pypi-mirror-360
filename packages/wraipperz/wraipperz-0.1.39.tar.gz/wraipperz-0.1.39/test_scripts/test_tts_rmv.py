from pathlib import Path
import os
from dotenv import load_dotenv
from wraipperz.api.tts import create_tts_manager


def test_openai_tts():
    # Load environment variables
    load_dotenv()

    # Create the TTS manager
    tts_manager = create_tts_manager()

    # Test text
    text = "Is this him?"
    instructions = """
Deliver this line with suspicious curiosity. Your voice should be slightly hushed but intense, with a quick, almost breathless quality. Put subtle emphasis on "this" to suggest you're confirming the identity of someone you've been searching for or heard about. End with a slight upward inflection to convey genuine questioning, but maintain an undercurrent of wariness. The delivery should be rapid and tight, with almost no pause between words, creating a sense of alertness and immediacy. Imagine you're finally face-to-face with someone important or dangerous, and you need confirmation without revealing too much of your own thoughts.
"""

    # Output file path
    output_path = Path("test_gpt4o_mini_tts.mp3")

    # Test parameters
    test_params = {
        "model": "gpt-4o-mini-tts",
        "voice": "echo",
        "instructions": instructions,
    }

    print(f"Testing OpenAI TTS with gpt-4o-mini-tts model...")
    print(f"Text: {text}")
    print(f"Voice: {test_params['voice']}")
    print(f"Instructions: {test_params['instructions']}")

    try:
        # Generate speech
        result = tts_manager.generate_speech(
            provider_name="openai",
            text=text,
            output_path=str(output_path),
            **test_params,
        )

        # Check result
        if result and result.get("status") == "success":
            print(f"\nSuccess! Audio generated and saved to: {output_path.absolute()}")
            print(f"Result details: {result}")

            # Get file size
            file_size = output_path.stat().st_size / 1024  # KB
            print(f"File size: {file_size:.2f} KB")

            return True
        else:
            print(f"\nGeneration completed but with unexpected result: {result}")
            return False

    except Exception as e:
        print(f"\nError during TTS generation: {str(e)}")
        return False


if __name__ == "__main__":
    test_openai_tts()

from wraipperz.api.tts import create_tts_manager

tts_manager = create_tts_manager()
tts_manager.generate_speech(
    provider_name="gemini",
    text="This is a test of Gemini's TTS capabilities.",
    output_path="output.wav",
    voice="Charon",  # Or other available voices
    model="gemini-2.5-pro-preview-tts",  # Or "gemini-2.5-flash-preview-tts"
    instructions="Speak in an extremelly depressing tone",
)
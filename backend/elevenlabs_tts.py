import os
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load environment variables from project root
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

def text_to_speech(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb") -> bytes:
    """
    Convert text to speech using ElevenLabs API.
    
    Args:
        text: The text to convert to speech
        voice_id: ElevenLabs voice ID (default: George - conversational)
    
    Returns:
        Audio data as bytes (MP3 format)
    """
    try:
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        
        # Convert generator to bytes
        audio_bytes = b"".join(audio_generator)
        return audio_bytes
    
    except Exception as e:
        print(f"❌ Text-to-speech failed: {e}")
        return b""

def text_to_speech_stream(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb"):
    """
    Convert text to speech and return as a generator for streaming.
    
    Args:
        text: The text to convert to speech
        voice_id: ElevenLabs voice ID
    
    Returns:
        Generator yielding audio chunks
    """
    try:
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        
        return audio_generator
    
    except Exception as e:
        print(f"❌ Text-to-speech streaming failed: {e}")
        return iter([])


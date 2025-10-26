import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from flask import jsonify

# Load environment variables from project root
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise RuntimeError("Missing ELEVENLABS_API_KEY environment variable")

def transcribe_audio_file(audio_file_path) -> str:
    """
    Send an audio file to ElevenLabs STT and return the transcription.
    Accepts either a file path (string) or a Flask FileStorage object.
    """
    if not audio_file_path:
        return ""

    url = "https://api.elevenlabs.io/v1/speech-to-text"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    
    # Handle both file path and FileStorage object
    if isinstance(audio_file_path, str):
        with open(audio_file_path, 'rb') as f:
            files = {"audio": f}
            response = requests.post(url, headers=headers, files=files)
    else:
        files = {"audio": (audio_file_path.filename, audio_file_path.stream, audio_file_path.content_type)}
        response = requests.post(url, headers=headers, files=files)

    if response.status_code != 200:
        print(f"❌ ElevenLabs transcription failed: {response.text}")
        return ""

    try:
        transcription = response.json().get("text", "")
        return transcription
    except Exception as e:
        print(f"❌ Failed to parse transcription response: {e}")
        return ""

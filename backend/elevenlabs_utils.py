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
        print("⚠️ No audio file provided")
        return ""

    print(f"🎤 Transcribing audio file: {audio_file_path}")
    url = "https://api.elevenlabs.io/v1/speech-to-text"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    
    # Handle both file path and FileStorage object
    if isinstance(audio_file_path, str):
        print(f"📂 Reading file from path: {audio_file_path}")
        with open(audio_file_path, 'rb') as f:
            files = {"audio": f}
            response = requests.post(url, headers=headers, files=files)
    else:
        print(f"📤 Uploading file from stream: {audio_file_path.filename}")
        files = {"audio": (audio_file_path.filename, audio_file_path.stream, audio_file_path.content_type)}
        response = requests.post(url, headers=headers, files=files)

    print(f"📡 ElevenLabs response status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ ElevenLabs transcription failed: {response.text}")
        return ""

    try:
        response_json = response.json()
        print(f"📝 Response JSON: {response_json}")
        transcription = response_json.get("text", "")
        print(f"✅ Transcription: {transcription}")
        return transcription
    except Exception as e:
        print(f"❌ Failed to parse transcription response: {e}")
        print(f"Raw response: {response.text}")
        return ""

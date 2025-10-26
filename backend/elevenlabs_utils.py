import os
import requests
from flask import jsonify

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise RuntimeError("Missing ELEVENLABS_API_KEY environment variable")

def transcribe_audio_file(audio_file) -> dict:
    """
    Send an audio file to ElevenLabs STT and return the transcription.
    """
    if not audio_file:
        return {"error": "No audio file provided"}

    url = "https://api.elevenlabs.io/v1/speech-to-text"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    files = {"file": (audio_file.filename, audio_file.stream, audio_file.content_type)}

    response = requests.post(url, headers=headers, files=files)

    if response.status_code != 200:
        return {"error": "Failed to transcribe", "details": response.text}

    try:
        transcription = response.json().get("text", "")
    except Exception:
        transcription = ""

    return {"transcription": transcription}

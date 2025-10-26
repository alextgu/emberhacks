# Text-to-Speech Integration Guide

## Overview

ElevenLabs text-to-speech has been integrated to read out AI feedback to users. The system can convert any text response from Gemini AI into natural-sounding speech.

## Features

- ✅ High-quality AI voice synthesis
- ✅ Multiple voice options
- ✅ Streaming support for long text
- ✅ Automatic playback control
- ✅ Frontend hook for easy integration

## Backend API

### Endpoint: `POST /text_to_speech`

Converts text to speech and returns audio file.

**Request:**
```json
{
  "text": "The first move is what sets everything in motion.",
  "voice_id": "JBFqnCBsd6RMkjVDRZzb"  // Optional, defaults to George
}
```

**Response:**
- Content-Type: `audio/mpeg`
- Returns MP3 audio file

**Example:**
```bash
curl -X POST http://localhost:8000/text_to_speech \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test"}' \
  --output speech.mp3
```

### Endpoint: `POST /text_to_speech_stream`

Streams audio for real-time playback (better for long text).

**Request:** Same as above

**Response:**
- Content-Type: `audio/mpeg`
- Streams audio chunks

## Frontend Usage

### Using the Hook

```javascript
import { useTextToSpeech } from "./hooks/useTextToSpeech";

function MyComponent() {
  const { speak, stop, isPlaying } = useTextToSpeech();

  const handleSpeak = () => {
    speak("Hello! This is ZED speaking.");
  };

  return (
    <div>
      <button onClick={handleSpeak} disabled={isPlaying}>
        {isPlaying ? "Speaking..." : "Speak"}
      </button>
      <button onClick={stop} disabled={!isPlaying}>
        Stop
      </button>
    </div>
  );
}
```

### Hook API

**`speak(text, voiceId?)`**
- Converts text to speech and plays it
- `text`: String to speak
- `voiceId`: Optional ElevenLabs voice ID (default: George)

**`stop()`**
- Stops current playback

**`isPlaying`**
- Boolean indicating if audio is currently playing

## Integrating with Gemini AI Responses

Here's how to make the AI responses speak automatically:

```javascript
// In App.jsx or your component

// When you get a response from the agent
useEffect(() => {
  if (agentResponse) {
    // Speak the response
    speak(agentResponse);
  }
}, [agentResponse, speak]);
```

### Example: Auto-speak transcribed commands

```javascript
// Auto-speak confirmation of what was heard
useEffect(() => {
  if (transcribedText) {
    speak(`I heard: ${transcribedText}`);
  }
}, [transcribedText, speak]);
```

### Example: Speak AI feedback

```javascript
// When agent completes a task
const handleTaskComplete = (result) => {
  const feedback = `Task completed. ${result.message}`;
  speak(feedback);
};
```

## Available Voices

ElevenLabs offers many voices. Here are some popular ones:

| Voice ID | Name | Description |
|----------|------|-------------|
| `JBFqnCBsd6RMkjVDRZzb` | George | Warm, conversational (default) |
| `21m00Tcm4TlvDq8ikWAM` | Rachel | Clear, professional |
| `AZnzlk1XvdvUeBnXmlld` | Domi | Friendly, energetic |
| `EXAVITQu4vr4xnSDxMaL` | Bella | Soft, calm |
| `ErXwobaYiN019PkySvjV` | Antoni | Deep, authoritative |
| `MF3mGyEYCl7XYWbV9V6O` | Elli | Young, upbeat |
| `TxGEqnHWrfWFTfGW9XjX` | Josh | Casual, friendly |
| `VR6AewLTigWG4xSOukaG` | Arnold | Strong, confident |
| `pNInz6obpgDQGcFmaJgB` | Adam | Smooth, professional |
| `yoZ06aMxZJJ28mfd3POQ` | Sam | Neutral, versatile |

To use a different voice:
```javascript
speak("Hello!", "21m00Tcm4TlvDq8ikWAM"); // Rachel's voice
```

## Backend Implementation

### File: `backend/elevenlabs_tts.py`

```python
from elevenlabs.client import ElevenLabs

def text_to_speech(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb") -> bytes:
    """Convert text to speech"""
    audio_generator = elevenlabs_client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    return b"".join(audio_generator)
```

### Integration Points

1. **After transcription**: Confirm what was heard
2. **During processing**: Update user on progress
3. **After completion**: Announce results
4. **On errors**: Speak error messages

## Example: Complete Integration

```javascript
import { useTextToSpeech } from "./hooks/useTextToSpeech";
import { useRecorder } from "./hooks/useRecorder";

function VoiceAssistant() {
  const { speak, isPlaying } = useTextToSpeech();
  const { transcribedText, startRecording, stopRecording } = useRecorder();
  const [aiResponse, setAiResponse] = useState("");

  // Confirm what was heard
  useEffect(() => {
    if (transcribedText) {
      speak(`I heard: ${transcribedText}. Processing your request.`);
      // Send to AI
      processCommand(transcribedText);
    }
  }, [transcribedText]);

  // Speak AI response
  useEffect(() => {
    if (aiResponse) {
      speak(aiResponse);
    }
  }, [aiResponse]);

  const processCommand = async (command) => {
    const response = await fetch("http://localhost:8000/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command }),
    });
    const data = await response.json();
    setAiResponse(data.result);
  };

  return (
    <div>
      <button onMouseDown={startRecording} onMouseUp={stopRecording}>
        Hold to Speak
      </button>
      {isPlaying && <div>🔊 Speaking...</div>}
    </div>
  );
}
```

## Configuration

### Change Voice Quality

In `backend/elevenlabs_tts.py`, modify the output format:

```python
output_format="mp3_44100_128",  # Standard quality
# or
output_format="mp3_44100_192",  # Higher quality
# or
output_format="pcm_44100",      # Uncompressed (larger files)
```

### Change Model

```python
model_id="eleven_multilingual_v2",  # Supports multiple languages
# or
model_id="eleven_monolingual_v1",   # English only, faster
# or
model_id="eleven_turbo_v2",         # Fastest, lower latency
```

## Cost Considerations

ElevenLabs charges based on characters converted:
- Free tier: ~10,000 characters/month
- Paid tiers: Check https://elevenlabs.io/pricing

**Tips to reduce costs:**
- Keep responses concise
- Cache common phrases
- Use shorter confirmations
- Only speak important feedback

## Testing

### Test Backend Endpoint

```bash
# Terminal
curl -X POST http://localhost:8000/text_to_speech \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing one two three"}' \
  --output test.mp3 && open test.mp3
```

### Test Frontend Hook

```javascript
// In browser console
speak("Hello from the console!");
```

## Troubleshooting

### "Failed to generate audio"

**Check:**
- ElevenLabs API key in `.env`
- API credits remaining
- Text is not empty
- Backend is running

### Audio doesn't play

**Check:**
- Browser audio permissions
- Volume is not muted
- Check browser console for errors
- Try a different browser

### Choppy playback

**Solutions:**
- Use streaming endpoint for long text
- Reduce audio quality
- Check network connection
- Clear browser cache

## Advanced Usage

### Queue Multiple Speeches

```javascript
const speechQueue = useRef([]);

const queueSpeak = (text) => {
  speechQueue.current.push(text);
  if (!isPlaying) {
    playNext();
  }
};

const playNext = () => {
  if (speechQueue.current.length > 0) {
    const next = speechQueue.current.shift();
    speak(next).then(() => playNext());
  }
};
```

### Add Visual Feedback

```javascript
{isPlaying && (
  <div className="flex items-center gap-2">
    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
    <span>AI is speaking...</span>
  </div>
)}
```

### Interrupt and Replace

```javascript
const speakNow = (text) => {
  stop(); // Stop current speech
  speak(text); // Start new speech
};
```

## Best Practices

1. **Keep it natural**: Use conversational language
2. **Be concise**: Shorter responses are better
3. **Add pauses**: Use punctuation for natural pauses
4. **Test voices**: Try different voices for your use case
5. **Handle errors**: Always have fallback text display
6. **Show status**: Indicate when AI is speaking
7. **Allow interruption**: Let users stop playback

## Example Responses

### Good Examples:
```javascript
speak("Got it! Opening Google for you.");
speak("I found 5 results. Here's the first one.");
speak("Task completed successfully.");
```

### Bad Examples (too long):
```javascript
speak("I have successfully completed the task that you requested and here are all the details..."); // Too verbose
```

## Summary

✅ **Backend Setup:**
- `elevenlabs_tts.py` - TTS utility
- `/text_to_speech` endpoint - Convert text
- `/text_to_speech_stream` - Stream audio

✅ **Frontend Setup:**
- `useTextToSpeech` hook - Easy integration
- Auto-play support
- Playback control

✅ **Integration:**
- Call `speak(text)` with any AI response
- Monitor `isPlaying` for UI feedback
- Use `stop()` to interrupt

Now your AI can talk back! 🗣️✨


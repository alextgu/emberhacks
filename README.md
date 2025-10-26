# 🎙️ ZED - Voice-Controlled AI Assistant

An intelligent AI assistant powered by Google Gemini, featuring voice commands, speech-to-text, and text-to-speech capabilities.

## ✨ Features

- 🎤 **Voice Commands** - Speak naturally to control your AI assistant
- 🗣️ **Text-to-Speech** - AI responses spoken in natural voice
- 🔊 **Voice Activity Detection** - Automatically stops recording after 2s of silence
- 🎯 **Smart Wake Word** - Say "Hey Zed" to activate (optional)
- 🤖 **AI-Powered** - Google Gemini for intelligent responses
- 🌐 **Browser Automation** - Control browser with voice commands
- 🔒 **Privacy-First** - Wake word detection runs locally in browser

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Modern web browser (Chrome/Firefox recommended)

### 1. Get API Keys

You'll need three API keys:

**Google Gemini API Key**
- Go to: https://aistudio.google.com/app/apikey
- Sign in and create an API key

**ElevenLabs API Key**
- Go to: https://elevenlabs.io/
- Sign up and get your API key from Settings

**Porcupine Access Key** (Optional - for "Hey Zed" wake word)
- Go to: https://console.picovoice.ai/
- Sign up and copy your Access Key

### 2. Install Dependencies

**Backend:**
```bash
cd /Users/agu/Desktop/emberhacks/emberhacks
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 3. Configure Environment Variables

**Create `.env` in project root:**
```bash
cd /Users/agu/Desktop/emberhacks/emberhacks
nano .env
```

Add:
```env
GOOGLE_API_KEY=your_google_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

**Create `frontend/.env`:**
```bash
cd frontend
nano .env
```

Add:
```env
VITE_PORCUPINE_KEY=your_porcupine_key_here
```

### 4. Start the Application

**Terminal 1 - Start Backend:**
```bash
cd /Users/agu/Desktop/emberhacks/emberhacks
source venv/bin/activate
python backend/main.py
```

You should see:
```
 * Running on http://0.0.0.0:8000
```

**Terminal 2 - Start Frontend:**
```bash
cd /Users/agu/Desktop/emberhacks/emberhacks/frontend
npm run dev
```

You should see:
```
➜  Local:   http://localhost:5173/
```

**Open Browser:**
- Go to http://localhost:5173
- Complete login
- Start using ZED!

## 🎯 How to Use

### Voice Commands

**Option 1: Wake Word (if enabled)**
1. Wait for green "Listening active" indicator
2. Say "Hey Zed"
3. Speak your command
4. Recording stops automatically after 2s of silence

**Option 2: Hold to Speak**
1. Click and hold "Hold to Speak" button
2. Speak your command
3. Release button or wait for silence detection

**Option 3: Text Input**
1. Click "Click to Type"
2. Type your command
3. Press Enter

### Example Commands

- "Open Google"
- "Search for Python tutorials"
- "What's the weather today"
- "Summarize this page"
- "Click the first link"

### Test Voice Features

**Test Text-to-Speech:**
- Click the "🎵 Test Voice" button on the main screen
- You should hear ZED speak

**Test Speech-to-Text:**
- Click "Hold to Speak"
- Say something
- Release and wait
- Your words should appear as text

## 📁 Project Structure

```
emberhacks/
├── backend/
│   ├── main.py                 # Flask API server
│   ├── agent_runner.py         # AI agent logic
│   ├── elevenlabs_utils.py     # Speech-to-text
│   ├── elevenlabs_tts.py       # Text-to-speech
│   └── browser_computer.py     # Browser automation
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main application
│   │   ├── hooks/
│   │   │   ├── useWakeWord.js  # Wake word detection
│   │   │   ├── useRecorder.js  # Audio recording
│   │   │   └── useTextToSpeech.js # TTS playback
│   │   └── components/         # UI components
│   └── public/
│       └── models/             # Wake word models
├── .env                        # Backend API keys
├── frontend/.env               # Frontend API keys
└── requirements.txt            # Python dependencies
```

## 🔧 Configuration

### Change Recording Duration

In `frontend/src/hooks/useRecorder.js`:
```javascript
const SILENCE_DURATION = 2000; // Change to 3000 for 3 seconds
```

### Change Voice (Text-to-Speech)

In `frontend/src/App.jsx`:
```javascript
speak("Hello!", "21m00Tcm4TlvDq8ikWAM"); // Rachel's voice
```

Available voices in `TEXT_TO_SPEECH_GUIDE.md`

### Enable/Disable Wake Word

In `frontend/src/App.jsx`:
```javascript
const shouldListen = phase === "main"; // true = enabled
const shouldListen = false; // false = disabled
```

## 🐛 Troubleshooting

### Backend Won't Start

**Error: "Missing ELEVENLABS_API_KEY"**
- Make sure `.env` file exists in project root
- Check API key is correct (no quotes, no spaces)
- Restart backend after adding keys

**Error: "ModuleNotFoundError"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Issues

**Wake Word Not Working**
- Check `VITE_PORCUPINE_KEY` in `frontend/.env`
- Restart frontend after adding key: `npm run dev`
- Grant microphone permission in browser
- Check for "Listening active" green indicator

**No Audio Recording**
- Grant microphone permission
- Check browser console (F12) for errors
- Try different browser
- Check microphone works in other apps

**Transcription Not Working**
- Make sure backend is running on port 8000
- Check `ELEVENLABS_API_KEY` in `.env`
- Check backend terminal for errors
- Verify you have ElevenLabs API credits

**Text-to-Speech Not Working**
- Check backend is running
- Verify `ELEVENLABS_API_KEY` in `.env`
- Check browser console for errors
- Try the "🎵 Test Voice" button

### Connection Issues

**"ERR_CONNECTION_REFUSED"**
- Backend is not running
- Start backend: `python backend/main.py`
- Check it's running on port 8000

**CORS Errors**
- Backend should allow all origins (already configured)
- Try restarting both frontend and backend

## 📊 API Endpoints

### Backend API

**POST `/transcribe_audio`**
- Converts audio to text
- Body: multipart/form-data with audio file
- Returns: `{"status": "transcribed", "text": "..."}`

**POST `/text_to_speech`**
- Converts text to speech
- Body: `{"text": "...", "voice_id": "..."}`
- Returns: MP3 audio file

**POST `/command`**
- Sends command to AI agent
- Body: `{"command": "..."}`
- Returns: `{"status": "queued", "command": "..."}`

**POST `/start`**
- Starts the AI agent
- Body: `{"goal": "..."}`
- Returns: `{"status": "started"}`

**GET `/status`**
- Gets agent status
- Returns: Agent state and info

## 💰 Cost Considerations

### API Usage

**ElevenLabs:**
- Free tier: ~10,000 characters/month
- Speech-to-text: Pay per character transcribed
- Text-to-speech: Pay per character generated
- Check: https://elevenlabs.io/pricing

**Google Gemini:**
- Free tier available
- Check: https://ai.google.dev/pricing

**Porcupine:**
- Free tier available
- Wake word detection runs locally (no per-use cost)
- Check: https://picovoice.ai/pricing

## 🔒 Security & Privacy

- ✅ API keys stored in `.env` files (gitignored)
- ✅ Wake word detection runs locally in browser
- ✅ Audio only sent to server when recording
- ✅ Temporary files deleted after transcription
- ✅ No audio stored on backend

**Best Practices:**
- Never commit `.env` files
- Rotate keys if exposed
- Monitor API usage regularly
- Use environment variables in production

## 📚 Documentation

- **TEXT_TO_SPEECH_GUIDE.md** - Complete TTS integration guide
- **ENV_SETUP.md** - Environment variables setup
- **DEBUG_CHECKLIST.md** - Troubleshooting guide

## 🛠️ Development

### Run in Development Mode

**Backend:**
```bash
source venv/bin/activate
python backend/main.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Build for Production

**Frontend:**
```bash
cd frontend
npm run build
```

### Run Tests

**Test ElevenLabs API:**
```bash
python backend/test_elevenlabs.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

[Your License Here]

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review documentation files
3. Check browser console (F12) and backend logs
4. Verify all API keys are correct

## ✅ Quick Checklist

Before starting, make sure you have:

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Google Gemini API key
- [ ] ElevenLabs API key
- [ ] Porcupine key (optional)
- [ ] `.env` file in project root
- [ ] `frontend/.env` file created
- [ ] Dependencies installed (pip & npm)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Microphone permission granted

## 🎉 You're Ready!

Open http://localhost:5173 and start talking to ZED!

---

**Made with ❤️ for EmberHacks**


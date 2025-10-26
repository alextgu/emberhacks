# Debug Checklist - Speech-to-Text Issues

Use this checklist to troubleshoot issues with the "Hey Zed" speech-to-text feature.

## 🔍 Quick Diagnostics

### Test 1: Check Backend is Running
```bash
curl http://localhost:8000/status
```
✅ Should return JSON with agent status
❌ If connection refused: Backend not running

### Test 2: Check ElevenLabs API Key
```bash
cd /Users/agu/Desktop/emberhacks/emberhacks
python backend/test_elevenlabs.py
```
✅ Should show "All tests passed!"
❌ If fails: Check API key in `.env`

### Test 3: Check Frontend is Running
Open browser to `http://localhost:5173`
✅ Should see ZED interface
❌ If not loading: Check frontend terminal for errors

### Test 4: Check Microphone Access
Look at browser address bar
✅ Should see microphone icon (not blocked)
❌ If blocked: Click icon and allow microphone

## 🎤 Wake Word Detection Issues

### Symptom: Green dot never appears

**Check:**
- [ ] Browser granted microphone permission
- [ ] `VITE_PORCUPINE_KEY` is set in `frontend/.env`
- [ ] Wake word model files exist in `frontend/public/models/`
- [ ] No other app is using the microphone
- [ ] Browser console shows no errors

**Try:**
1. Refresh the page
2. Clear browser cache
3. Try different browser
4. Check browser console for errors

### Symptom: Green dot appears but "Hey Zed" not detected

**Check:**
- [ ] Speaking clearly and at normal volume
- [ ] Saying "Hey Zed" (not "Hey Z" or "Hey Zedd")
- [ ] Microphone is working (test with other apps)
- [ ] Not too much background noise

**Try:**
1. Speak louder
2. Get closer to microphone
3. Reduce background noise
4. Try saying it slower: "Hey ... Zed"

**Adjust sensitivity:**
In `frontend/src/hooks/useWakeWord.js`, change:
```javascript
sensitivity: 0.5, // Try 0.6 or 0.7 for more sensitive
```

## 🎙️ Recording Issues

### Symptom: Recording doesn't start after "Hey Zed"

**Check Browser Console:**
```
Should see: "🎤 WAKE WORD DETECTED!"
Should see: "🎙️ Auto-starting recording after wake word..."
```

**If missing:**
- [ ] Check `handleWakeWord` function in `App.jsx`
- [ ] Check `startRecording` is being called
- [ ] Check no JavaScript errors in console

### Symptom: Recording starts but no countdown

**Check:**
- [ ] `recordingCountdown` state is updating
- [ ] Timer is being set correctly
- [ ] No JavaScript errors

**Look for in console:**
```
🎙️ Auto-starting recording after wake word...
⏹️ Auto-stopping recording...
```

### Symptom: Recording doesn't stop after 5 seconds

**Check:**
- [ ] `stopRecording` is being called
- [ ] No errors in console
- [ ] Timer cleanup is working

**Try:**
- Manually click "Hold to Speak" to test if recording works at all

## 📤 Transcription Issues

### Symptom: Recording completes but no transcription

**Check Backend Logs:**
Should see:
```
POST /transcribe_audio
```

**Check Browser Console:**
Should see:
```
📤 Sending audio to ElevenLabs for transcription...
✅ Transcription: [your text]
```

**If you see errors:**

#### Error: "Failed to upload audio"
- [ ] Backend is running
- [ ] Backend is on port 8000
- [ ] No CORS errors
- [ ] Network connection working

#### Error: "Backend error"
- [ ] Check backend terminal for errors
- [ ] Check ElevenLabs API key is correct
- [ ] Check you have API credits
- [ ] Check audio file was created

### Symptom: Transcription is empty or wrong

**Check:**
- [ ] Speaking clearly during recording
- [ ] Recording duration is sufficient (5 seconds)
- [ ] Audio quality is good
- [ ] Microphone is working properly

**Try:**
1. Test with manual "Hold to Speak" button
2. Speak louder and clearer
3. Reduce background noise
4. Check microphone settings in OS

### Symptom: "ElevenLabs transcription failed"

**Check:**
- [ ] ElevenLabs API key is valid
- [ ] You have API credits remaining
- [ ] API endpoint is correct
- [ ] Audio format is supported

**Test API key:**
```bash
python backend/test_elevenlabs.py
```

**Check ElevenLabs dashboard:**
https://elevenlabs.io/

## 🔧 Common Fixes

### Fix 1: Restart Everything
```bash
# Stop backend (Ctrl+C)
# Stop frontend (Ctrl+C)

# Start backend
cd /Users/agu/Desktop/emberhacks/emberhacks
python backend/main.py

# Start frontend (new terminal)
cd /Users/agu/Desktop/emberhacks/emberhacks/frontend
npm run dev
```

### Fix 2: Clear Browser Cache
1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"

### Fix 3: Check Environment Variables
```bash
# Backend
cd /Users/agu/Desktop/emberhacks/emberhacks
cat .env

# Should show:
# GOOGLE_API_KEY=...
# ELEVENLABS_API_KEY=...

# Frontend
cd frontend
cat .env

# Should show:
# VITE_PORCUPINE_KEY=...
```

### Fix 4: Reinstall Dependencies
```bash
# Frontend
cd /Users/agu/Desktop/emberhacks/emberhacks/frontend
rm -rf node_modules
npm install

# Backend
cd /Users/agu/Desktop/emberhacks/emberhacks
pip install -r requirements.txt
```

### Fix 5: Check File Permissions
```bash
# Make sure model files are readable
ls -la frontend/public/models/
# Should show .ppn and .pv files
```

## 📊 Expected Console Output

### Successful Flow - Browser Console:
```
🎙 Requesting microphone...
✅ Microphone access granted: [device name]
🧠 Loading Hey Zed model...
🔊 Listening for 'Hey ZED'...
🎤 WAKE WORD DETECTED!
🎙️ Auto-starting recording after wake word...
⏹️ Auto-stopping recording...
📤 Sending audio to ElevenLabs for transcription...
✅ Transcription: [your command]
📤 Sending transcribed text to backend: [your command]
```

### Successful Flow - Backend Terminal:
```
 * Running on http://0.0.0.0:8000
127.0.0.1 - - [date] "POST /transcribe_audio HTTP/1.1" 200 -
127.0.0.1 - - [date] "POST /command HTTP/1.1" 200 -
```

## 🆘 Still Not Working?

1. **Check all environment variables are set correctly**
   - No quotes around values
   - No spaces before/after values
   - Keys are valid and not expired

2. **Check API quotas/limits**
   - Porcupine: https://console.picovoice.ai/
   - ElevenLabs: https://elevenlabs.io/
   - Google: https://aistudio.google.com/

3. **Check browser compatibility**
   - Chrome/Edge: Full support ✅
   - Firefox: Full support ✅
   - Safari: May have issues with WebAssembly ⚠️

4. **Check system requirements**
   - Modern browser (last 2 versions)
   - Microphone connected and working
   - Internet connection for API calls

5. **Look for specific error messages**
   - Browser console (F12)
   - Backend terminal
   - Network tab in DevTools

## 📝 Debug Mode

### Enable Verbose Logging

Add to `frontend/src/hooks/useWakeWord.js`:
```javascript
console.log("Porcupine status:", status);
console.log("Audio processing:", pcm.length);
```

Add to `frontend/src/hooks/useRecorder.js`:
```javascript
console.log("Recording state:", recording);
console.log("Audio blob size:", blob.size);
```

Add to `backend/elevenlabs_utils.py`:
```python
print(f"Audio file size: {os.path.getsize(audio_file_path)}")
print(f"API response: {response.status_code}")
```

## 🎯 Testing Each Component

### Test 1: Wake Word Only
1. Open app
2. Wait for green "Listening active"
3. Say "Hey Zed"
4. Should see green flash
5. Check console for "WAKE WORD DETECTED"

### Test 2: Manual Recording Only
1. Open app
2. Click and hold "Hold to Speak"
3. Speak something
4. Release button
5. Should see transcription

### Test 3: Full Flow
1. Open app
2. Wait for green "Listening active"
3. Say "Hey Zed"
4. Immediately say your command
5. Wait 5 seconds
6. Should see transcription

## 📞 Getting Help

If still stuck:
1. Copy error messages from console
2. Copy backend terminal output
3. Check `SPEECH_TO_TEXT_SETUP.md` for detailed info
4. Verify all API keys are valid
5. Test each API independently

## ✅ Success Indicators

You know it's working when:
- ✅ Green "Listening active" indicator
- ✅ Green flash on "Hey Zed"
- ✅ Red recording indicator with countdown
- ✅ Blue "Transcribing" indicator
- ✅ Text appears below buttons
- ✅ Console shows successful transcription
- ✅ Backend receives command


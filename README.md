# 🎙️ ZED - Voice-Controlled AI Assistant

**Zed** is your **autonomous AI study partner** that connects directly to your student account and responds to your **voice** to create a personalized, productive learning experience. 
Ask questions about **deadlines, study tips, or how to approach a problem** — Zed provides guidance that **challenges your brain to learn**, rather than simply giving you answers to copy.

Check it out on Devpost:  
🔗 [https://devpost.com/software/zed-7z0wg4](https://devpost.com/software/zed-7z0wg4?_gl=1*1dkw02l*_gcl_au*MzE5MzI5ODc2LjE3NTQ5NTY4OTQ.*_ga*MjgxNzY0MDIwLjE3NTQ5NTY4OTQ.*_ga_0YHJK3Y10M*czE3NjE1NzY1MDgkbzEyOCRnMSR0MTc2MTU3NzA2NSRqNTckbDAkaDA.)

## 🧠 What It Does

### 🤖 Zed, Your Study Buddy
Zed is your autonomous AI study partner that connects directly to your student account and responds to your voice to create a personalized and highly productive learning experience. Ask questions about deadlines, study tips, or how to approach a problem—Zed will provide guidance that challenges your brain to learn rather than simply giving you answers to copy.

### 🔐 Authenticates as Your Study Buddy
Securely logs into your **Canvas** or **Blackboard** account via **Auth0**, just like a studious classmate with access to the same materials you do.  
Encrypted credential storage ensures your login information stays safe while enabling autonomous course access.

### 📚 Intelligently Scrapes Your Actual Courses
Automatically downloads your **syllabus**, **professor’s lecture slides**, and **assignments** from your enrolled courses.  
Extracts exam dates, topics, and deadlines using the **Gemini 2.5 Compute engine** — no manual input needed.

### 🎤 Provides Natural Voice Interaction
Wake word activation with **Porcupine** — just say “Hey Zed!”  
Receive spoken responses via **ElevenLabs text-to-speech** that sound like a supportive study buddy.  
Study while cooking, exercising, or walking around — Zed makes learning seamless and non-distracting.

---
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
4. Recording stops automatically after 3s of silence

**Option 2: Hold to Speak**
1. Click and hold "Hold to Speak" button
2. Speak your command
3. Release button or wait for silence detection

**Option 3: Text Input**
1. Click "Click to Type"
2. Type your command
3. Press Enter


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




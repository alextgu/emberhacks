# Environment Variables Setup

## Quick Setup

### 1. Backend Environment Variables

Create `.env` in the **project root**:

```bash
cd /Users/agu/Desktop/emberhacks/emberhacks
cp .env.template .env
nano .env
```

Add your API keys:
```env
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXX
ELEVENLABS_API_KEY=sk_XXXXXXXXXXXXXXXXXXXXXXXX
```

### 2. Frontend Environment Variables

Create `.env` in the **frontend folder**:

```bash
cd /Users/agu/Desktop/emberhacks/emberhacks/frontend
cp .env.template .env
nano .env
```

Add your Porcupine key:
```env
VITE_PORCUPINE_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## Where to Get API Keys

1. **Google Gemini API Key**
   - Go to: https://aistudio.google.com/app/apikey
   - Sign in with Google account
   - Click "Create API Key"
   - Copy the key

2. **ElevenLabs API Key**
   - Go to: https://elevenlabs.io/
   - Sign up or log in
   - Go to Settings → API Key
   - Copy your API key

3. **Porcupine Access Key**
   - Go to: https://console.picovoice.ai/
   - Sign up or log in
   - Copy your Access Key from the dashboard

## File Structure

```
emberhacks/
├── .env                    ← Backend API keys (ROOT)
├── .env.template          ← Template for backend
├── frontend/
│   ├── .env               ← Frontend API keys
│   └── .env.template      ← Template for frontend
└── backend/
    └── (no .env here!)
```

## Important Notes

- ✅ All backend files now load from **project root** `.env`
- ✅ Frontend loads from `frontend/.env`
- ✅ `.env` files are in `.gitignore` (never committed)
- ✅ Use `.env.template` files as reference

## Start the Application

After setting up environment variables:

**Terminal 1 - Backend:**
```bash
cd /Users/agu/Desktop/emberhacks/emberhacks
source venv/bin/activate
python backend/main.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/agu/Desktop/emberhacks/emberhacks/frontend
npm run dev
```

## Troubleshooting

### "Missing ELEVENLABS_API_KEY"

Make sure:
1. `.env` file exists in **project root** (not in backend folder)
2. File contains: `ELEVENLABS_API_KEY=your_actual_key`
3. No quotes around the key
4. No spaces before/after the `=`

### "No module named 'google.generativeai'"

Run:
```bash
cd /Users/agu/Desktop/emberhacks/emberhacks
source venv/bin/activate
pip install google-generativeai flask python-dotenv requests playwright
```

### Backend can't find .env

All backend files now automatically load from project root. If you still have issues:
```bash
# Check if .env exists in root
ls -la /Users/agu/Desktop/emberhacks/emberhacks/.env

# Check contents
cat /Users/agu/Desktop/emberhacks/emberhacks/.env
```

## Files Updated

These files now load `.env` from project root:
- ✅ `backend/main.py`
- ✅ `backend/agent_runner.py`
- ✅ `backend/test_elevenlabs.py`

All use:
```python
from pathlib import Path
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)
```


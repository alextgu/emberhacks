#!/bin/bash

# Script to start the backend server
# Usage: ./start-backend.sh

echo "🚀 Starting EmberHacks Backend Server"
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo ""
    echo "Please create a .env file with:"
    echo "  GOOGLE_API_KEY=your_google_api_key"
    echo "  ELEVENLABS_API_KEY=your_elevenlabs_api_key"
    echo ""
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "📦 Installing/updating dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "🌐 Starting server on http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""
echo "======================================"
echo ""

# Start the server
python backend/main.py


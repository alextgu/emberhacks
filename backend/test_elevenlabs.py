#!/usr/bin/env python3
"""
Test script for ElevenLabs Speech-to-Text API
Run this to verify your ElevenLabs API key is working correctly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def test_api_key():
    """Test if the ElevenLabs API key is set"""
    if not ELEVENLABS_API_KEY:
        print("❌ ERROR: ELEVENLABS_API_KEY not found in environment variables")
        print("Please create a .env file in the project root with:")
        print("ELEVENLABS_API_KEY=your_key_here")
        return False
    
    print("✅ ElevenLabs API key found")
    print(f"   Key starts with: {ELEVENLABS_API_KEY[:8]}...")
    return True

def test_api_connection():
    """Test connection to ElevenLabs API"""
    try:
        import requests
    except ImportError:
        print("❌ ERROR: requests library not installed")
        print("Run: pip install requests")
        return False
    
    print("\n🔍 Testing ElevenLabs API connection...")
    
    # Test with a simple API call to check if the key is valid
    url = "https://api.elevenlabs.io/v1/user"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Successfully connected to ElevenLabs API")
            data = response.json()
            print(f"   Subscription: {data.get('subscription', {}).get('tier', 'Unknown')}")
            print(f"   Character count: {data.get('subscription', {}).get('character_count', 0)}")
            print(f"   Character limit: {data.get('subscription', {}).get('character_limit', 0)}")
            return True
        elif response.status_code == 401:
            print("❌ ERROR: Invalid API key")
            print("   Please check your ELEVENLABS_API_KEY in .env file")
            return False
        else:
            print(f"⚠️  WARNING: Unexpected response code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to connect to ElevenLabs API")
        print(f"   {str(e)}")
        return False

def main():
    print("=" * 60)
    print("ElevenLabs Speech-to-Text API Test")
    print("=" * 60)
    
    if not test_api_key():
        sys.exit(1)
    
    if not test_api_connection():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print("\nYour ElevenLabs integration is ready to use.")
    print("You can now start the backend server with: python backend/main.py")

if __name__ == "__main__":
    main()


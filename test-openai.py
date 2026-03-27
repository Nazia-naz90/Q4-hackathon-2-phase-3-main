# test-openai.py
"""Test script to verify OpenAI API Key is working"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env from project root
project_root = Path(__file__).resolve().parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Get OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")

print("=" * 60)
print("OPENAI API KEY TEST")
print("=" * 60)

if not openai_api_key:
    print("[ERROR] OPENAI_API_KEY not found in .env file!")
else:
    print(f"[OK] OPENAI_API_KEY found: {openai_api_key[:15]}...{openai_api_key[-10:]}")
    
    # Check if it's a valid format
    if openai_api_key.startswith("sk-proj-") or openai_api_key.startswith("sk-"):
        print("[OK] API Key format looks valid")
    else:
        print("[WARNING] API Key format might be invalid")
    
    print("\nAttempting to test with OpenAI API...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        
        # Test with a simple completion
        print("Connecting to OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one word"}
            ],
            max_tokens=10
        )
        
        print(f"[SUCCESS] OpenAI API is working!")
        print(f"Response: {response.choices[0].message.content}")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage}")
        
    except ImportError:
        print("[WARNING] OpenAI library not installed. Install with: pip install openai")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        print("\nPossible issues:")
        print("1. API Key quota might be exhausted")
        print("2. API Key might be invalid/expired")
        print("3. Network connectivity issue")
        print("\nCheck your API key at: https://platform.openai.com/api-keys")

print("=" * 60)

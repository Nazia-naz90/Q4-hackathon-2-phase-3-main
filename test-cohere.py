#!/usr/bin/env python3
"""Test script to verify COHERE_API_KEY is working correctly"""

import os
import asyncio
from dotenv import load_dotenv
import cohere

# Load .env from project root
load_dotenv()

# Get configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-r-plus")

print("=" * 60)
print("COHERE API TEST")
print("=" * 60)
print(f"API Key configured: {'✅ Yes' if COHERE_API_KEY else '❌ No'}")
print(f"Model: {COHERE_MODEL}")
print("=" * 60)

async def test_cohere():
    """Test Cohere API connection and parsing"""
    
    if not COHERE_API_KEY:
        print("❌ ERROR: COHERE_API_KEY not found in .env file!")
        return
    
    try:
        client = cohere.AsyncClient(api_key=COHERE_API_KEY)
        
        # Test 1: Basic connection
        print("\n[Test 1] Testing basic connection...")
        response = await client.chat(
            model=COHERE_MODEL,
            message="Hello! Respond with just 'OK' if you can read this.",
            temperature=0.1
        )
        print(f"✅ Connection successful!")
        print(f"   Response: {response.text[:50]}...")
        
        # Test 2: Parse task extraction
        print("\n[Test 2] Testing task extraction...")
        test_message = "Meray liya aik task create krdo jis ka name 'My app' ho"
        parse_prompt = f"""
You are a Natural Language Parser. Analyze this message:

User Message: "{test_message}"

Extract:
- intent: "create", "list", "update", "delete", or "chat"
- title: clean task title (remove filler words)
- extra: any extra info

Output ONLY JSON: {{"intent": "...", "title": "...", "extra": "..."}}

Examples:
- "Groceries khareedne hain, task add kar do" -> {{"intent": "create", "title": "Groceries khareedne hain", "extra": null}}
- "jiska name 'My app' ho" -> {{"intent": "create", "title": "My app", "extra": null}}
"""
        
        response = await client.chat(
            model=COHERE_MODEL,
            message=parse_prompt,
            temperature=0.1,
            prompt_truncation="OFF"
        )
        
        import json
        import re
        
        response_text = response.text.strip()
        print(f"   Raw response: {response_text[:100]}...")
        
        # Extract JSON
        json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group()
            parsed = json.loads(json_text)
            
            intent = parsed.get("intent", "unknown")
            title = parsed.get("title", "not found")
            
            print(f"✅ Parsing successful!")
            print(f"   Intent: {intent}")
            print(f"   Title: {title}")
            
            # Verify extraction
            if intent == "create" and title == "My app":
                print(f"\n✅✅✅ PERFECT! Task extraction working correctly!")
            else:
                print(f"\n⚠️  Extraction needs improvement")
                print(f"   Expected: intent='create', title='My app'")
                print(f"   Got: intent='{intent}', title='{title}'")
        else:
            print(f"⚠️  Could not extract JSON from response")
        
        # Test 3: Another example
        print("\n[Test 3] Testing another example...")
        test_message2 = "Groceries khareedne hain, task add kar do"
        parse_prompt2 = f"""
Parse this: "{test_message2}"

Output ONLY JSON: {{"intent": "...", "title": "..."}}

Example: "Groceries khareedne hain, task add kar do" -> {{"intent": "create", "title": "Groceries khareedne hain"}}
"""
        
        response2 = await client.chat(
            model=COHERE_MODEL,
            message=parse_prompt2,
            temperature=0.1
        )
        
        response_text2 = response2.text.strip()
        json_match2 = re.search(r'\{[^}]+\}', response_text2, re.DOTALL)
        if json_match2:
            parsed2 = json.loads(json_match2.group())
            title2 = parsed2.get("title", "not found")
            print(f"   Input: {test_message2}")
            print(f"   Extracted title: {title2}")
            
            if title2 == "Groceries khareedne hain":
                print(f"   ✅ Correct!")
            else:
                print(f"   ⚠️  Expected: 'Groceries khareedne hain'")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        
    except cohere.errors.UnauthorizedError:
        print(f"\n❌ ERROR: Invalid COHERE_API_KEY!")
        print(f"   Your key: {COHERE_API_KEY[:20]}...")
        print(f"   Get a valid key from: https://dashboard.cohere.com/api-keys")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_cohere())

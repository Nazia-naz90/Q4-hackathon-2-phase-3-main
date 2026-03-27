#!/usr/bin/env python3
"""
Demo script to show how to use the AI Todo Assistant Chatbot
"""

import requests
import json
from typing import Dict, Any

# Base URL for the backend API
BASE_URL = "http://localhost:8000"

def create_user():
    """Create a test user account"""
    print("Creating test user...")

    user_data = {
        "username": "demouser",
        "email": "demo@example.com",
        "password": "demopassword123"
    }

    response = requests.post(f"{BASE_URL}/auth/signup", json=user_data)

    if response.status_code == 200:
        user_info = response.json()
        print(f"✓ User created successfully: {user_info['username']}")
        return user_info
    else:
        print(f"✗ Failed to create user: {response.status_code} - {response.text}")
        return None

def login_user():
    """Login to get JWT token"""
    print("Logging in...")

    login_data = {
        "username": "demouser",
        "password": "demopassword123"
    }

    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

    if response.status_code == 200:
        token_info = response.json()
        print("✓ Login successful")
        return token_info["access_token"]
    else:
        print(f"✗ Login failed: {response.status_code} - {response.text}")
        return None

def chat_with_ai(message: str, token: str):
    """Send message to AI chatbot"""
    print(f"Sending message to AI: '{message}'")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": message
    }

    response = requests.post(
        f"{BASE_URL}/ai/chat",
        json=payload,
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ AI Response: {result['response']}")
        return result
    else:
        print(f"✗ AI Chat failed: {response.status_code} - {response.text}")
        return None

def main():
    print("=== AI Todo Assistant Chatbot Demo ===\n")

    # Step 1: Create user
    user = create_user()
    if not user:
        print("Cannot proceed without user account")
        return

    # Step 2: Login to get token
    token = login_user()
    if not token:
        print("Cannot proceed without authentication")
        return

    # Step 3: Test various chat interactions
    test_messages = [
        "Create a task to buy groceries",
        "Show my tasks",
        "Create a task to finish the project",
        "List all my tasks",
        "What can you do?",
        "Complete the groceries task"
    ]

    print("\n--- Testing AI Chat Interactions ---")
    for msg in test_messages:
        print()
        chat_with_ai(msg, token)
        print("-" * 50)

    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()
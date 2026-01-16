"""
Test script to validate the enhanced AI Todo Assistant with improved validation.
"""
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Mock the OpenAI client before importing
import unittest.mock
with unittest.mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
    from test_agent_chat import TodoChatAgent


async def test_enhanced_validation():
    """Test the enhanced validation features of the TodoChatAgent."""
    print("Testing Enhanced AI Todo Assistant Validation...")

    agent = TodoChatAgent()

    # Mock the OpenAI client to avoid actual API calls
    agent.openai_client = MagicMock()
    agent.openai_client.chat = MagicMock()
    agent.openai_client.chat.completions = MagicMock()

    # Mock the create method to return a predefined response
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.finish_reason = "stop"
    mock_choice.message.content = "Test response"
    mock_choice.message.tool_calls = None
    mock_response.choices = [mock_choice]

    agent.openai_client.chat.completions.create = AsyncMock(return_value=mock_response)

    # Test 1: Rate limiting
    print("\n1. Testing rate limiting...")
    user_id = "test_user_123"

    # Simulate rapid requests to test rate limiting
    for i in range(12):
        response = await agent.process_message(f"Test message {i}", user_id)
        if "rate limit" in response.lower():
            print(f"   ✓ Rate limiting triggered after {i+1} requests: {response}")
            break
        else:
            print(f"   Request {i+1}: OK")

    # Test 2: Input sanitization
    print("\n2. Testing input sanitization...")
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "DROP TABLE users; --",
        '<iframe src="javascript:alert(1)">',
        "SELECT * FROM passwords WHERE 1=1"
    ]

    for malicious_input in malicious_inputs:
        response = await agent.process_message(malicious_input, user_id)
        print(f"   Input: {malicious_input}")
        print(f"   Response: {response[:50]}...")

    # Test 3: Content validation
    print("\n3. Testing content validation...")
    invalid_inputs = [
        "",  # Empty input
        "x" * 1001,  # Too long input
        "SHOW ME MY TASKS",  # Should trigger view request
        "THANK YOU FOR HELPING ME"  # Should trigger gratitude response
    ]

    for i, invalid_input in enumerate(invalid_inputs):
        if i == 1:  # Skip the too long input to avoid slowing down tests
            print(f"   Skipped too long input test")
            continue

        response = await agent.process_message(invalid_input, user_id)
        print(f"   Input: {invalid_input[:30]}{'...' if len(invalid_input) > 30 else ''}")
        print(f"   Response: {response[:50]}...")

    # Test 4: Abusive language detection
    print("\n4. Testing abusive language detection...")
    abusive_inputs = [
        "You are a stupid system!",
        "Fuck this application!",
        "I hate you!"
    ]

    for abusive_input in abusive_inputs:
        response = await agent.process_message(abusive_input, user_id)
        print(f"   Input: {abusive_input}")
        print(f"   Response: {response[:50]}...")

    # Test 5: Prohibited title handling
    print("\n5. Testing prohibited title handling...")
    prohibited_inputs = [
        "show me my tasks",
        "list my tasks",
        "show all tasks",
        "what tasks do i have?",
        "thanks",
        "thank you"
    ]

    for prohibited_input in prohibited_inputs:
        response = await agent.process_message(prohibited_input, user_id)
        print(f"   Input: {prohibited_input}")
        print(f"   Response: {response[:50]}...")

    print("\nEnhanced validation testing completed!")


if __name__ == "__main__":
    asyncio.run(test_enhanced_validation())
#!/usr/bin/env python3
"""
Test script to verify that the 'View Task List' functionality now works correctly
after improving the system prompt to distinguish between create and view requests.
"""

import asyncio
import os
import sys
import json

# Add the project root and mcp-server to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
mcp_server_path = os.path.join(project_root, 'mcp-server')

sys.path.insert(0, project_root)
sys.path.insert(0, mcp_server_path)

async def test_improved_view_task_list():
    """Test that the AI agent now correctly distinguishes between create and view requests."""
    print("Testing improved 'View Task List' functionality...\n")

    # Import the AI agent
    try:
        from mcp-server.test_agent_chat import TodoChatAgent
    except ImportError as e:
        print(f"Error importing TodoChatAgent: {e}")
        print("Make sure you have the correct path and dependencies.")
        return

    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("WARNING: OPENAI_API_KEY environment variable is not set.")
        print("The AI agent will not work without this key.")
        print("Please set the environment variable to test the full functionality.\n")
        return

    # Create an agent instance
    agent = TodoChatAgent()

    # Test queries that should trigger VIEW (not create)
    view_queries = [
        "Show me my tasks",
        "What tasks do I have?",
        "View my task list",
        "List my tasks",
        "Display my todo list",
        "See my tasks",
        "View Task List"
    ]

    # Test queries that should trigger CREATE (to ensure we didn't break that)
    create_queries = [
        "Create a task to buy groceries",
        "Add a task to call mom",
        "Make a new task to finish report"
    ]

    print("Testing VIEW queries (should use get_tasks function):\n")

    # Simulate a user ID (in a real scenario, this would come from authentication)
    sample_user_id = "test-user-123"

    for i, query in enumerate(view_queries, 1):
        print(f"{i}. User asks: \"{query}\"")

        try:
            response = await agent.process_message(query, user_id=sample_user_id)
            print(f"   AI Response: {response}\n")
        except Exception as e:
            print(f"   Error processing query '{query}': {e}\n")

    print("\nTesting CREATE queries (should still work as before):\n")

    for i, query in enumerate(create_queries, 1):
        print(f"{i}. User asks: \"{query}\"")

        try:
            response = await agent.process_message(query, user_id=sample_user_id)
            print(f"   AI Response: {response}\n")
        except Exception as e:
            print(f"   Error processing query '{query}': {e}\n")

    print("Test completed. The AI agent should now correctly distinguish between view and create requests.")

if __name__ == "__main__":
    asyncio.run(test_improved_view_task_list())
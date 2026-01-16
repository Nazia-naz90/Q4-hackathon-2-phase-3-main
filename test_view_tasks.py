#!/usr/bin/env python3
"""
Test script to verify that the 'View Task List' functionality works with the AI agent.
This simulates what happens when a user asks "View Task List" in the chatbot.
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

async def test_view_task_list():
    """Test the 'View Task List' functionality with the AI agent."""
    print("Testing 'View Task List' functionality...\n")

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

    # Test various ways a user might ask to view their tasks
    test_queries = [
        "View Task List",
        "Show me my tasks",
        "What tasks do I have?",
        "List my tasks",
        "Display my todo list"
    ]

    print("Testing various user queries that should trigger 'View Task List':\n")

    # Simulate a user ID (in a real scenario, this would come from authentication)
    sample_user_id = "test-user-123"

    for i, query in enumerate(test_queries, 1):
        print(f"{i}. User asks: \"{query}\"")

        try:
            response = await agent.process_message(query, user_id=sample_user_id)
            print(f"   AI Response: {response}\n")
        except Exception as e:
            print(f"   Error processing query '{query}': {e}\n")

    print("Test completed. The AI agent should recognize these queries and call the get_tasks function,\n"
          "which retrieves the user's tasks from the database filtered by their user ID.")

if __name__ == "__main__":
    asyncio.run(test_view_task_list())
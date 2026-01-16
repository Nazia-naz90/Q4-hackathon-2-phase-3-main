#!/usr/bin/env python3
"""
Final test to verify that the AI agent correctly handles 'Show me my tasks' requests
after the system prompt improvements.
"""

import asyncio
import os
import sys

# Add the project root and mcp-server to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
mcp_server_path = os.path.join(project_root, 'mcp-server')

sys.path.insert(0, project_root)
sys.path.insert(0, mcp_server_path)

async def test_final_fix():
    """Test that the AI agent now correctly handles 'Show me my tasks' requests."""
    print("Testing the final fix for 'Show me my tasks' functionality...\n")

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

    # Critical test queries that should trigger VIEW (not create)
    critical_view_queries = [
        "Show me my tasks",
        "View Task List",
        "Show all tasks",
        "What tasks do I have?",
        "List my tasks"
    ]

    print("Testing CRITICAL view queries that were previously misinterpreted as create requests:\n")

    # Simulate a user ID (in a real scenario, this would come from authentication)
    sample_user_id = "test-user-123"

    for i, query in enumerate(critical_view_queries, 1):
        print(f"{i}. User asks: \"{query}\"")

        try:
            response = await agent.process_message(query, user_id=sample_user_id)
            print(f"   AI Response: {response}\n")

            # Check if the response indicates it's showing tasks rather than creating them
            if "show" in response.lower() or "list" in response.lower() or "here are" in response.lower():
                print(f"   ✅ SUCCESS: Correctly interpreted as a view request\n")
            else:
                print(f"   ⚠️  WARNING: May not be correctly interpreted as a view request\n")

        except Exception as e:
            print(f"   Error processing query '{query}': {e}\n")

    print("Test completed. The AI agent should now correctly display task lists when users ask to view them.")

if __name__ == "__main__":
    asyncio.run(test_final_fix())
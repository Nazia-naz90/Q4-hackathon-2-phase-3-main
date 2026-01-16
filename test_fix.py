#!/usr/bin/env python3
"""
Test script to verify that the TodoChatAgent error is fixed.
"""

import asyncio
from mcp_server.test_agent_chat import TodoChatAgent


async def test_todo_chat_agent():
    """Test the TodoChatAgent to ensure the user_id error is fixed."""
    print("Testing TodoChatAgent with user_id parameter...")

    agent = TodoChatAgent()

    # Test creating a task with user_id (this should not throw the error anymore)
    try:
        result = await agent.create_task(
            title="Test task",
            description="This is a test task",
            priority="medium",
            user_id="test-user-123"
        )
        print(f"✓ create_task succeeded: {result}")
    except TypeError as e:
        if "got an unexpected keyword argument 'user_id'" in str(e):
            print(f"✗ create_task failed with the original error: {e}")
            return False
        else:
            print(f"✗ create_task failed with a different error: {e}")
            return False
    except Exception as e:
        print(f"✗ create_task failed with an unexpected error: {e}")
        return False

    # Test other functions as well
    try:
        result = await agent.get_tasks(user_id="test-user-123")
        print(f"✓ get_tasks succeeded: {type(result)}")

        # If we got tasks, try updating one
        if 'tasks' in result and result['tasks']:
            task_id = result['tasks'][0]['id']
            update_result = await agent.update_task(
                task_id=task_id,
                title="Updated test task",
                user_id="test-user-123"
            )
            print(f"✓ update_task succeeded: {type(update_result)}")

        # Test toggling completion
        if 'tasks' in result and result['tasks']:
            task_id = result['tasks'][0]['id']
            toggle_result = await agent.toggle_task_completion(
                task_id=task_id,
                user_id="test-user-123"
            )
            print(f"✓ toggle_task_completion succeeded: {type(toggle_result)}")

        # Test deleting a task
        if 'tasks' in result and result['tasks']:
            task_id = result['tasks'][0]['id']
            delete_result = await agent.delete_task(
                task_id=task_id,
                user_id="test-user-123"
            )
            print(f"✓ delete_task succeeded: {type(delete_result)}")

    except TypeError as e:
        if "got an unexpected keyword argument 'user_id'" in str(e):
            print(f"✗ Other function failed with the original error: {e}")
            return False
        else:
            print(f"✗ Other function failed with a different error: {e}")
            return False
    except Exception as e:
        print(f"✗ Other function failed with an unexpected error: {e}")
        return False

    print("\n✓ All tests passed! The user_id error has been fixed.")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_todo_chat_agent())
    if not success:
        exit(1)
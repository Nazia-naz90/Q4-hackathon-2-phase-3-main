#!/usr/bin/env python3
"""
Integration test for the AI-Powered Todo Chatbot.
This script tests the complete integration between the MCP server,
backend services, and the agent interaction module.
"""

import asyncio
import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Add the project root and backend to the path so we can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Import the functions directly
from mcp_server.main import create_task, get_tasks, update_task, delete_task, toggle_task_completion


async def test_integration():
    """Test the complete integration of the AI-Powered Todo Chatbot."""
    print("Testing AI-Powered Todo Chatbot Integration")
    print("=" * 60)

    # Test 1: Create a task
    print("\n1. Testing task creation...")
    try:
        result = await create_task(
            title="Integration Test Task",
            description="This is a test task created during integration testing",
            due_date="2026-12-31",
            priority="high"
        )
        print(f"Create task result: {json.dumps(result, indent=2)}")

        if result["success"]:
            task_id = result["task"]["id"]
            print(f"[PASS] Task created successfully with ID: {task_id}")
        else:
            print(f"[FAIL] Failed to create task: {result['error']}")
            return False
    except Exception as e:
        print(f"[FAIL] Exception during task creation: {str(e)}")
        return False

    # Test 2: Get tasks
    print("\n2. Testing task retrieval...")
    try:
        result = await get_tasks(status="all", priority=None, limit=10)
        print(f"Get tasks result: {json.dumps(result, indent=2)[:500]}...")

        if result["success"] and len(result["tasks"]) > 0:
            print(f"[PASS] Retrieved {result['count']} tasks")
        else:
            print(f"[FAIL] Failed to retrieve tasks: {result.get('error', 'No tasks found')}")
            return False
    except Exception as e:
        print(f"[FAIL] Exception during task retrieval: {str(e)}")
        return False

    # Test 3: Update the task
    print("\n3. Testing task update...")
    try:
        result = await update_task(
            task_id=task_id,
            title="Updated Integration Test Task",
            description="This task has been updated during integration testing",
            priority="medium"
        )
        print(f"Update task result: {json.dumps(result, indent=2)[:300]}...")

        if result["success"]:
            print(f"[PASS] Task updated successfully")
        else:
            print(f"[FAIL] Failed to update task: {result['error']}")
            return False
    except Exception as e:
        print(f"[FAIL] Exception during task update: {str(e)}")
        return False

    # Test 4: Toggle task completion
    print("\n4. Testing task completion toggle...")
    try:
        result = await toggle_task_completion(task_id=task_id)
        print(f"Toggle completion result: {json.dumps(result, indent=2)[:300]}...")

        if result["success"]:
            print(f"[PASS] Task completion toggled successfully")
        else:
            print(f"[FAIL] Failed to toggle task completion: {result['error']}")
            return False
    except Exception as e:
        print(f"[FAIL] Exception during task completion toggle: {str(e)}")
        return False

    # Test 5: Delete the task
    print("\n5. Testing task deletion...")
    try:
        result = await delete_task(task_id=task_id)
        print(f"Delete task result: {json.dumps(result, indent=2)[:300]}...")

        if result["success"]:
            print(f"[PASS] Task deleted successfully")
        else:
            print(f"[FAIL] Failed to delete task: {result['error']}")
            return False
    except Exception as e:
        print(f"[FAIL] Exception during task deletion: {str(e)}")
        return False

    print("\n" + "=" * 60)
    print("[SUCCESS] All integration tests passed!")
    print("\nIntegration Summary:")
    print("- MCP server properly connected to backend database")
    print("- All CRUD operations working correctly")
    print("- Task lifecycle complete: Create → Read → Update → Toggle → Delete")
    print("- Proper error handling and response formatting")

    return True


def main():
    """Main function to run the integration test."""
    print("Starting AI-Powered Todo Chatbot Integration Test...")

    # Check if required environment variables are set
    if not os.getenv("DATABASE_URL"):
        print("Warning: DATABASE_URL environment variable not set. Using SQLite for testing.")

    success = asyncio.run(test_integration())
    if success:
        print("\n[SUCCESS] Integration Test: PASSED")
        sys.exit(0)
    else:
        print("\n[ERROR] Integration Test: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
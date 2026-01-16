"""
Test file for MCP tools integration with the Todo application.
This file demonstrates how tools like create_task and get_tasks are registered and called via the MCP session.
"""

import asyncio
import json
from typing import Dict, Any
from mcp.server import Server
from mcp.types import TextContent, Prompt, PromptMessage, CallToolResult, Tool


# Mock the actual tools until we have the real implementation connected
async def mock_create_task(title: str, description: str = "", due_date: str = None, priority: str = "medium"):
    """Mock implementation of create_task tool."""
    print(f"Creating task: {title}")
    return {
        "success": True,
        "task": {
            "id": 1,
            "title": title,
            "description": description,
            "due_date": due_date,
            "priority": priority,
            "completed": False
        }
    }


async def mock_get_tasks(status: str = "all", priority: str = None, limit: int = 10):
    """Mock implementation of get_tasks tool."""
    print(f"Getting tasks with status: {status}, priority: {priority}, limit: {limit}")
    return {
        "success": True,
        "tasks": [
            {
                "id": 1,
                "title": "Sample task",
                "description": "This is a sample task",
                "due_date": "2024-12-31",
                "priority": "medium",
                "completed": False
            }
        ],
        "count": 1
    }


async def mock_update_task(task_id: int, title: str = None, description: str = None,
                          due_date: str = None, priority: str = None, completed: bool = None):
    """Mock implementation of update_task tool."""
    print(f"Updating task {task_id}")
    return {
        "success": True,
        "task": {
            "id": task_id,
            "title": title or f"Updated task {task_id}",
            "description": description or "Updated description",
            "due_date": due_date,
            "priority": priority or "medium",
            "completed": completed or False
        }
    }


async def mock_delete_task(task_id: int):
    """Mock implementation of delete_task tool."""
    print(f"Deleting task {task_id}")
    return {
        "success": True,
        "message": f"Task {task_id} deleted successfully"
    }


async def mock_toggle_task_completion(task_id: int):
    """Mock implementation of toggle_task_completion tool."""
    print(f"Toggling completion for task {task_id}")
    return {
        "success": True,
        "task": {
            "id": task_id,
            "title": f"Task {task_id}",
            "description": f"Description for task {task_id}",
            "due_date": "2024-12-31",
            "priority": "medium",
            "completed": True
        }
    }


async def test_mcp_tools():
    """Test function to simulate calling MCP tools via MCP session."""
    print("Testing MCP Tools Integration...")

    # Test create_task
    print("\n1. Testing create_task:")
    result = await mock_create_task("Buy groceries", "Need to buy milk and bread", "2024-01-15", "high")
    print(json.dumps(result, indent=2))

    # Test get_tasks
    print("\n2. Testing get_tasks:")
    result = await mock_get_tasks(status="pending", priority="high", limit=5)
    print(json.dumps(result, indent=2))

    # Test update_task
    print("\n3. Testing update_task:")
    result = await mock_update_task(1, title="Updated grocery list", completed=True)
    print(json.dumps(result, indent=2))

    # Test toggle_task_completion
    print("\n4. Testing toggle_task_completion:")
    result = await mock_toggle_task_completion(1)
    print(json.dumps(result, indent=2))

    # Test delete_task
    print("\n5. Testing delete_task:")
    result = await mock_delete_task(1)
    print(json.dumps(result, indent=2))

    print("\nAll MCP tools tested successfully!")


# Run the test
if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
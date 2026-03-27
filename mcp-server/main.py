# mcp-server\main.py
from mcp.server.fastmcp import FastMCP
import httpx
from typing import Optional, List, Dict, Any

# Initialize FastMCP server
mcp = FastMCP("TodoManager")

BACKEND_URL = "http://localhost:8000"

@mcp.tool()
async def get_tasks(session_token: str) -> List[Dict[str, Any]]:
    """
    Retrieve all tasks for the authenticated user.
    :param session_token: The session token of the user.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/tasks/",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def create_task(session_token: str, title: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new todo item.
    :param session_token: The session token of the user.
    :param title: The title of the task.
    :param description: Optional description of the task.
    """
    async with httpx.AsyncClient() as client:
        payload = {"title": title}
        if description:
            payload["description"] = description

        response = await client.post(
            f"{BACKEND_URL}/tasks/",
            json=payload,
            headers={"Authorization": f"Bearer {session_token}"}
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def update_task(
    session_token: str,
    task_id: str,
    title: Optional[str] = None,
    status: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing task.
    :param session_token: The session token of the user.
    :param task_id: The UUID of the task to update.
    :param title: New title for the task.
    :param status: New status (e.g., 'pending', 'completed').
    :param description: New description for the task.
    """
    async with httpx.AsyncClient() as client:
        payload = {}
        if title is not None:
            payload["title"] = title
        if status is not None:
            payload["status"] = status
        if description is not None:
            payload["description"] = description

        response = await client.put(
            f"{BACKEND_URL}/tasks/{task_id}",
            json=payload,
            headers={"Authorization": f"Bearer {session_token}"}
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def delete_task(session_token: str, task_id: str) -> Dict[str, Any]:
    """
    Delete a task.
    :param session_token: The session token of the user.
    :param task_id: The UUID of the task to delete.
    """
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BACKEND_URL}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    mcp.run()

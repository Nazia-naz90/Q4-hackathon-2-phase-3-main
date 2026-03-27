# MCP Server

This is an MCP (Model Context Protocol) server that provides tools for managing todo items. It connects to the main backend API and exposes tools that can be used by AI agents.

## Tools Available

- `get_tasks(session_token)` - Retrieve all tasks for the authenticated user
- `create_task(session_token, title, description)` - Create a new todo item
- `update_task(session_token, task_id, title, status, description)` - Update an existing task (task_id is a UUID string)
- `delete_task(session_token, task_id)` - Delete a task (task_id is a UUID string)

## Setup

```bash
cd mcp-server
uv sync
```

## Running Standalone

```bash
uv run main.py
```

## Running with AI Agent

The MCP server is automatically started by the AI Agent server. No need to run it separately.

## Configuration

The server connects to the backend API at `http://localhost:8000`.
Modify the `BACKEND_URL` constant in `main.py` if your backend runs on a different port.

## Integration with OpenAI Agents

The MCP server provides tools to the OpenAI Agents SDK, allowing the AI agent to:
1. Fetch user tasks from the backend
2. Create new tasks based on natural language requests
3. Update task status, title, or description
4. Delete completed or unwanted tasks

The AI Agent uses the `gpt-4o-mini` model and authenticates with the backend using the user's session token.

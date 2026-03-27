# AI Integration Service

This service combines the MCP Server and AI Agent into a single FastAPI application that integrates with the main backend.

## Setup

```bash
uv sync
```

## Running

```bash
uv run main.py
```

The service will start on `http://localhost:8001`

## API Endpoints

### POST /chat

Chat with the AI assistant.

**Headers:**
- `Authorization: Bearer <session_token>`

**Request:**
```json
{
    "message": "Create a task to buy groceries"
}
```

**Response:**
```json
{
    "response": "I've created a task: 'Buy groceries'"
}
```

### GET /health

Check the health status of the AI integration service.

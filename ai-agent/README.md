# AI Agent

This is an AI agent that uses OpenAI Agents SDK with MCP (Model Context Protocol) to provide a conversational interface for managing todo items.

## Setup

1. Create a `.env` file in the project root with your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

2. Install dependencies:
```bash
uv sync
```

## Running

Start the AI agent server:
```bash
uv run main.py
```

The server will start on `http://localhost:8001`.

## API Endpoints

### POST /chat

Send a message to the AI agent.

**Headers:**
- `Authorization: Bearer <session_token>`

**Request Body:**
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

## Architecture

The AI agent uses:
- **OpenAI Agents SDK** for conversational AI
- **MCP Server** to interact with the todo backend
- **FastAPI** for the HTTP API

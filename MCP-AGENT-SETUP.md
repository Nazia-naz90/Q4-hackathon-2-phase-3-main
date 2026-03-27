# MCP & AI Agent Setup Guide

This guide explains how to connect your AI Todo Assistant Chatbot with MCP (Model Context Protocol) server and AI agents using OpenAI API.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│   AI Agent      │────▶│   MCP Server    │
│   (Next.js)     │     │  (FastAPI)      │     │  (FastMCP)      │
│   Port 3000     │     │   Port 8001     │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   Backend API   │
                                                │   (FastAPI)     │
                                                │   Port 8000     │
                                                └─────────────────┘
```

## Prerequisites

1. **Python 3.13+** installed
2. **uv** package manager installed
3. **Node.js** and **npm** installed
4. **OpenAI API Key** (already configured in `.env`)

## Quick Start

### Step 1: Install Dependencies

```bash
# Install backend dependencies
cd backend
uv sync

# Install MCP server dependencies
cd ../mcp-server
uv sync

# Install AI agent dependencies
cd ../ai-agent
uv sync

# Install frontend dependencies
cd ../frontend
npm install
```

### Step 2: Verify Environment Variables

Make sure your `.env` file contains:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-your-api-key-here

# Database connection string
DATABASE_URL=postgresql+asyncpg://...

# JWT Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# AI Agent Configuration
AI_AGENT_URL=http://localhost:8001
BACKEND_URL=http://localhost:8000
```

### Step 3: Start All Servers

**Option A: Using the batch script (Windows)**

```bash
start-servers.bat
```

**Option B: Manually start each server**

```bash
# Terminal 1 - Backend Server
cd backend
uv run uvicorn main:app --reload --port 8000

# Terminal 2 - AI Agent Server (includes MCP)
cd ai-agent
uv run uvicorn main:app --reload --port 8001

# Terminal 3 - Frontend Server
cd frontend
npm run dev
```

## How It Works

### 1. MCP Server (`mcp-server/`)

The MCP server exposes tools that the AI agent can use:

- **get_tasks**: Fetch all tasks for a user
- **create_task**: Create a new task
- **update_task**: Update task properties
- **delete_task**: Remove a task

### 2. AI Agent (`ai-agent/`)

The AI agent:
- Uses OpenAI's `gpt-4o-mini` model
- Connects to the MCP server for tool access
- Authenticates with the backend using user session tokens
- Processes natural language requests to manage tasks

### 3. Backend (`backend/`)

The backend API:
- Manages user authentication (JWT)
- Stores tasks in PostgreSQL (Neon)
- Provides REST endpoints for CRUD operations

## Testing the Integration

### Test Backend API

```bash
# Check backend health
curl http://localhost:8000

# Create a test user (via frontend signup)
```

### Test AI Agent

```bash
# Get a session token first (login via frontend)
# Then test the chat endpoint
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -d '{"message": "Create a task to buy groceries"}'
```

### Test MCP Server Directly

```bash
cd mcp-server
uv run main.py
```

## Usage Examples

Once everything is running, you can chat with the AI agent:

**User**: "Create a task to finish the project report by Friday"
**AI Agent**: *Creates task using MCP tools* ✅ Task created: "Finish the project report"

**User**: "Show me all my tasks"
**AI Agent**: *Fetches tasks using MCP tools* 📋 Here are your tasks...

**User**: "Mark the groceries task as complete"
**AI Agent**: *Updates task status using MCP tools* ✅ Task marked as completed!

## Troubleshooting

### AI Agent not responding

1. Check if `OPENAI_API_KEY` is set correctly in `.env`
2. Verify the AI agent server is running on port 8001
3. Check the AI agent logs for errors

### MCP tools not available

1. Ensure the MCP server is starting with the AI agent
2. Check that `BACKEND_URL` is correct in `mcp-server/main.py`
3. Verify the backend is running on port 8000

### Authentication errors

1. Make sure you have a valid session token
2. Check that JWT_SECRET matches between backend and frontend
3. Verify the token hasn't expired

## Project Structure

```
q4-hackathone2-phase-3/
├── backend/           # FastAPI backend with task management
│   ├── main.py       # Main API endpoints
│   ├── models.py     # SQLModel database models
│   └── database.py   # Database connection
├── mcp-server/       # MCP server providing tools
│   └── main.py       # MCP tool definitions
├── ai-agent/         # AI Agent using OpenAI + MCP
│   ├── main.py       # FastAPI chat endpoint
│   └── agent.py      # Agent configuration
├── frontend/         # Next.js frontend
└── .env              # Environment variables (API keys)
```

## Security Notes

- Never commit your `.env` file with real API keys
- Use a strong `SECRET_KEY` in production
- Enable CORS only for trusted origins in production
- Rotate your OpenAI API key if exposed

## Additional Resources

- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)

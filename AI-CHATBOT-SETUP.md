# AI Assistant Chatbot - Setup Guide

This guide explains how to run the complete AI Assistant Chatbot integrated with the Todo application.

## Architecture

### Option 1: Simple Setup (Recommended) - Single Server
```
┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend       │
│   (Next.js)     │     │   (FastAPI)     │
│   Port: 3000    │     │   Port: 8000    │
│                 │     │   + AI Chatbot  │
└─────────────────┘     └─────────────────┘
```

### Option 2: Advanced AI (Optional) - Multiple Servers
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   AI Agent      │────▶│   MCP Server    │
│   (Next.js)     │     │   (FastAPI)     │     │   (MCP)         │
│   Port: 3000    │     │   Port: 8001    │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   Backend       │
                                                │   (FastAPI)     │
                                                │   Port: 8000    │
                                                └─────────────────┘
```

## Quick Start (Simple Setup)

### 1. Start the Backend Server (with AI Chatbot)

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

The backend will run on `http://localhost:8000` and includes:
- ✅ Todo API endpoints
- ✅ Authentication endpoints
- ✅ **AI Chatbot endpoint** (`/ai/chat`)

### 2. Start the Frontend

```bash
cd frontend
npm run dev
```

The frontend will run on `http://localhost:3000`

### 3. Use the Chatbot!

1. **Login** at `http://localhost:3000/login`
2. Navigate to the **Dashboard**
3. Click the **chat bubble icon** in the bottom-right corner
4. Start chatting!

## Advanced Setup (Optional - OpenAI Integration)

If you want advanced AI capabilities with OpenAI:

### Prerequisites
- OpenAI API Key

### Setup

1. **Configure Environment Variables**

Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your-openai-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

2. **Start All Servers**

Open 4 terminals:

**Terminal 1 - Backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - MCP Server:**
```bash
cd mcp-server
uv run main.py
```

**Terminal 3 - AI Agent:**
```bash
cd ai-agent
uv run main.py
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm run dev
```

## Using the AI Chatbot

### Simple AI (Built-in)

The backend includes a rule-based AI that can:

- **Create tasks:** "Create a task to buy groceries"
- **List tasks:** "Show my tasks" or "List all tasks"
- **Complete tasks:** "Complete task [ID]" or "Mark task as done"
- **Delete tasks:** "Delete task [ID]"
- **Help:** "What can you do?"

### Advanced AI (OpenAI)

With OpenAI integration, the AI can understand natural language better and:
- Create tasks with descriptions and priorities
- Update task details
- Answer questions about your tasks
- Provide smart suggestions

### Example Commands

Try these commands with the AI assistant:

```
"Create a task to buy groceries"
"Show me all my tasks"
"Mark task 1 as completed"
"Delete task 3"
"Update task 2 to high priority"
"What tasks do I have pending?"
```

## Troubleshooting

### Chatbot not responding

1. Make sure the backend server is running
2. Check that you're logged in (the chatbot uses your session token)
3. Open browser console (F12) to see any error messages

### "Failed to fetch" error

This means the backend is not reachable. Make sure:
- Backend is running on `http://localhost:8000`
- Frontend is running on `http://localhost:3000`
- Check the browser console for CORS errors

### Authentication errors

Make sure you're logged in. The chatbot uses your session token to authenticate with the backend.

## Project Structure

```
q4-hackathone2-phase-3/
├── backend/           # FastAPI backend with todo API + AI chatbot
├── frontend/          # Next.js frontend with chatbot UI
├── mcp-server/        # MCP server for advanced AI (optional)
├── ai-agent/          # AI agent using OpenAI + MCP (optional)
├── ai-integration/    # Alternative AI integration layer
├── .env               # Environment variables (OpenAI API key)
└── AI-CHATBOT-SETUP.md  # This file
```

## API Endpoints

### AI Chatbot API (Built-in)

- `POST /ai/chat` - Chat with the AI assistant
  - Headers: `Authorization: Bearer <session_token>`
  - Body: `{ "message": "your message" }`
  - Response: `{ "response": "AI response" }`

- `GET /ai/health` - Check AI chatbot status

### Backend API

- `GET /tasks` - Get all tasks
- `POST /tasks` - Create a task
- `PUT /tasks/{id}` - Update a task
- `DELETE /tasks/{id}` - Delete a task

### AI Agent API (Advanced - Optional)

- `POST /chat` - Chat with advanced AI agent
  - Requires running ai-agent server on port 8001

## Tips

1. **Simple setup is enough** - Start with just backend + frontend
2. The built-in AI works without OpenAI API key
3. For advanced AI, add your OpenAI API key and run additional servers
4. Keep terminal windows open while using the application
5. The AI chatbot is available on all pages (floating button)

## Switching to Advanced AI

To use the advanced OpenAI-based AI instead of the simple rule-based AI:

1. Update `frontend/src/lib/chatAPI.ts` to point to the AI agent server:
```typescript
const AI_AGENT_URL = 'http://localhost:8001';
```

2. Run all servers (backend, MCP, AI agent, frontend)

3. The chatbot will now use OpenAI for smarter responses!

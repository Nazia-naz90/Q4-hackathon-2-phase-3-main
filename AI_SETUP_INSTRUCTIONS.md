# AI Setup Instructions

This document explains how to set up and run the complete AI system with Cohere integration.

## Prerequisites

- Python 3.13+
- A valid Cohere API key (get one from [Cohere Dashboard](https://dashboard.cohere.com/api-keys))

## Configuration

1. Make sure your `.env` file contains:
```
COHERE_API_KEY=your_actual_cohere_api_key_here
COHERE_MODEL=command-r-plus
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install ai-agent dependencies:
```bash
cd ai-agent
pip install -r requirements.txt
# Or if using uv: uv sync
```

## Running the Complete AI System

There are two ways to run the AI system:

### Option 1: Backend Only (Recommended for initial setup)
This uses the Cohere integration directly in the main backend:

1. Start the backend:
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

2. The AI chatbot will be available at `http://localhost:8000/ai/chat`

### Option 2: Full AI Agent System (Advanced)
This uses the separate AI agent service with MCP server:

1. Start the MCP server:
```bash
cd mcp-server
python main.py
```

2. Start the AI agent service:
```bash
cd ai-agent
python -m uvicorn main:app --reload --port 8001
```

3. Start the main backend:
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

4. Configure the backend to use the AI agent by ensuring your `.env` has:
```
AI_AGENT_URL=http://localhost:8001
```

## Testing the AI Integration

Once the system is running:

1. Access the web interface at `http://localhost:3000`
2. Log in with your credentials
3. Click the AI chatbot button in the bottom right corner
4. Try commands like:
   - "Create a task to buy groceries"
   - "Show my tasks"
   - "Complete task [task-id]"
   - "What can you do?"

## Troubleshooting

### Common Issues:

1. **Cohere API Key Not Found**: Make sure your `.env` file has the correct `COHERE_API_KEY` value.

2. **AI Chatbot Not Responding**: Check that the backend is running and the API key is valid.

3. **Mixed Language Processing**: The updated system now handles mixed English-Urdu-Hindi inputs much better than the previous rule-based system.

4. **Connection Issues**: If using the full AI agent system, ensure all services (MCP server, AI agent, backend) are running simultaneously.

### Health Checks:

- Backend AI health: `GET http://localhost:8000/ai/health`
- AI agent health: `GET http://localhost:8001/health`

## Features of the Updated AI System

1. **Enhanced Language Processing**: Better handling of mixed-language inputs like "meray liya naya Task create kro"
2. **Cohere AI Integration**: Uses advanced natural language processing instead of simple rule matching
3. **Context Awareness**: AI understands the user's current tasks when responding
4. **Fallback System**: Maintains rule-based functionality if Cohere API is unavailable
5. **Improved Responses**: More natural and helpful AI responses using Cohere's command-r-plus model

## Architecture

```
Frontend (Next.js)
    ↓ (calls /ai/chat)
Backend (FastAPI)
    ↓ (uses Cohere API or falls back to rule-based)
Cohere AI Service / Rule-Based System
    ↓ (if using full system)
AI Agent Service (FastAPI)
    ↓ (uses MCP server)
MCP Server ↔ Backend API
```

The system can run in either simplified mode (Backend ↔ Cohere) or full mode (Frontend ↔ Backend ↔ AI Agent ↔ MCP Server ↔ Backend).
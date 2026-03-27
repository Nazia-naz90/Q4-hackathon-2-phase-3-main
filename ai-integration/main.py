# ai-integration\main.py
"""
AI Integration Server - Combines MCP Server and AI Agent into a single FastAPI application
This integrates with the main backend to provide AI chatbot functionality
"""
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Import MCP and Agents
from mcp import StdioServerParameters
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
import httpx

# Define lifespan for MCP server management
mcp_server = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_server
    
    # Setup MCP server connection to main backend
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "mcp-server/main.py"],
        env=os.environ.copy()
    )
    
    mcp_server = MCPServerStdio(server_params, client_session_timeout_seconds=30)
    
    # Start MCP server
    await mcp_server.__aenter__()
    
    yield
    
    # Cleanup MCP server
    if mcp_server:
        await mcp_server.__aexit__(None, None, None)

app = FastAPI(
    title="AI Integration API",
    description="AI Chatbot API integrated with MCP and Todo Backend",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend URL (main todo API)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not set. AI features will not work.")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

def create_todo_agent():
    """Create the Todo AI Agent with MCP tools"""
    return Agent(
        name="TodoAgent",
        instructions="""
        You are a helpful productivity assistant integrated with a Todo application.
        You can help users manage their tasks (create, list, update, delete) using the provided tools.
        The user's session token is provided - use it for all API calls.
        Be concise and helpful in your responses.
        """,
        mcp_servers=[mcp_server] if mcp_server else [],
        model="gpt-4o-mini"
    )

async def get_current_user(authorization: str = Header(None)):
    """Validate user session by checking with main backend"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authorization header")
    
    token = authorization.split(" ")[1]
    
    # Verify token with main backend
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BACKEND_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            return response.json()
        except httpx.RequestError:
            # If backend is not available, allow the request (fallback mode)
            return {"id": "fallback-user"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: str = Header(None)):
    """
    Chat with the AI assistant
    The AI can help manage tasks using MCP tools
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authorization header")

    session_token = authorization.split(" ")[1]
    
    if not mcp_server:
        raise HTTPException(status_code=503, detail="MCP server not available")

    agent = create_todo_agent()

    # Prepend the session token to the user message
    full_message = f"User session token: {session_token}\n\nUser message: {request.message}"

    try:
        result = await Runner.run(agent, full_message)
        return ChatResponse(response=result.final_output)
    except Exception as e:
        print(f"Error chatting with agent: {e}")
        raise HTTPException(status_code=500, detail=f"AI agent error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_server": "connected" if mcp_server else "disconnected",
        "backend_url": BACKEND_URL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

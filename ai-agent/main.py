# ai-agent\main.py
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from agent import chat_with_agent, get_mcp_server
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Global MCP server instance
mcp_server_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MCP server lifecycle"""
    global mcp_server_instance
    # Initialize MCP server on startup
    mcp_server_instance = await get_mcp_server()
    yield
    # Cleanup happens automatically with context manager

app = FastAPI(title="AI Agent API (Cohere + MCP)", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": "command-r-plus (Cohere)",
        "mcp_server": "connected" if mcp_server_instance else "disconnected"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authorization header")

    session_token = authorization.split(" ")[1]

    # Prepend the session token to the user message
    try:
        agent_response = await chat_with_agent(request.message, session_token, mcp_server_instance)
        return ChatResponse(response=agent_response)
    except Exception as e:
        print(f"Error chatting with agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

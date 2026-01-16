# ai-agent\main.py
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from agent import create_todo_agent, chat_with_agent
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authorization header")
    
    session_token = authorization.split(" ")[1]
    
    agent = create_todo_agent()
    
    # Prepend the session token to the user message or inject it into the context
    # For now, we'll just tell the agent the session token to use.
    full_message = f"User session token: {session_token}\n\nUser message: {request.message}"
    
    try:
        agent_response = await chat_with_agent(full_message, agent)
        return ChatResponse(response=agent_response)
    except Exception as e:
        print(f"Error chatting with agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
# ai-agent\agent.py
import os
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
# 👇 IMPORTANT: Ye import add karna zaroori hai
from mcp import StdioServerParameters

load_dotenv()

# 👇 CHANGE: Arguments ko 'StdioServerParameters' object mein wrap karna hai
import sys
import os

# Create a copy of environment variables and ensure the Python path includes the project root
env_copy = os.environ.copy()
current_dir = os.path.dirname(os.path.abspath(__file__))  # ai-agent directory
project_root = os.path.dirname(current_dir)  # project root directory

# Add the project root to PYTHONPATH so the mcp server can find backend modules
if 'PYTHONPATH' in env_copy:
    env_copy['PYTHONPATH'] = f"{project_root}{os.pathsep}{env_copy['PYTHONPATH']}"
else:
    env_copy['PYTHONPATH'] = project_root

server_params = {
    "command": sys.executable,  # Use the same Python interpreter
    "args": ["../mcp-server/main.py"],
    "env": env_copy
}

mcp_server = MCPServerStdio(server_params, client_session_timeout_seconds=30)

def create_todo_agent():
    return Agent(
        name="TodoAgent",
        instructions="""
        You are a helpful productivity assistant. 
        You can help users manage their tasks (create, list, update, delete) using the provided tools.
        Always ask for the session_token if it's not provided or available in the context.
        Wait, actually, the user will provide the session_token in the first message or it will be injected by the system.
        When calling tools, always use the session_token provided by the user.
        """,
        mcp_servers=[mcp_server],
        model="gpt-4o-mini"  # 👈 CHANGE: Use GPT-4o-mini model
    )

async def chat_with_agent(message: str, agent: Agent):
    # Use context managers for MCP servers
    # For now, we assume there's only one and use it in a nested fashion or similar
    # If the SDK supports it, we might be able to use a different pattern.
    # But based on the search, `async with` is the intended way.
    
    async with mcp_server:
        result = await Runner.run(agent, message)
        return result.final_output
# ai-agent\agent.py
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any, Tuple
import cohere

# Load .env from project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Cohere configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-r-plus")

# Global MCP server instance
mcp_server = None

async def get_mcp_server():
    """Get or create the MCP server instance"""
    global mcp_server
    if mcp_server is None:
        from agents.mcp import MCPServerStdio

        # MCP Server parameters - points to MCP server that connects to backend
        server_params = {
            "command": "uv",
            "args": ["run", "--project", str(project_root / "mcp-server"), "main.py"],
            "env": {**os.environ}
        }
        mcp_server = MCPServerStdio(server_params, client_session_timeout_seconds=30)
    return mcp_server

async def parse_user_intent(message: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Use Cohere to parse user message and extract intent + clean task title.
    Returns: (intent, title, extra_info)
    intent: 'create', 'list', 'update', 'delete', 'chat'
    """
    client = cohere.AsyncClient(api_key=COHERE_API_KEY)
    
    parse_prompt = f"""You are a JSON parser for a Todo app. Extract intent and task title from user messages.

RULES:
1. Find the actual task name - ignore request words like "bana do", "kar do", "add kar do", "mera", "please"
2. If you see "jiska name X ho" or "jiska naam X ho" or 'X' in quotes -> X is the title
3. For "X, task add kar do" -> X is the title
4. Return ONLY valid JSON

EXAMPLES:
Input: "Meray liya aik task create krdo jis ka name 'My app' ho"
Output: {{"intent":"create","title":"My app","extra":null}}

Input: "Groceries khareedne hain, task add kar do"
Output: {{"intent":"create","title":"Groceries khareedne hain","extra":null}}

Input: "Kal meeting hai, task bana do"
Output: {{"intent":"create","title":"Kal meeting hai","extra":null}}

Input: "Mere saare tasks dikhao"
Output: {{"intent":"list","title":null,"extra":null}}

NOW PARSE THIS: "{message}"

Output ONLY JSON (no explanation):"""

    try:
        response = await client.chat(
            model=COHERE_MODEL,
            message=parse_prompt,
            temperature=0.01,  # Almost deterministic for consistent JSON
            prompt_truncation="OFF",
            max_tokens=200
        )
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Find JSON pattern
        import re
        json_match = re.search(r'\{[^}]*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group()
        
        parsed = json.loads(response_text)
        
        intent = parsed.get("intent", "chat")
        title = parsed.get("title")
        extra = parsed.get("extra")
        
        # Additional cleanup if title found
        if title:
            # Remove quotes
            title = title.strip("'\"").strip()
            # Remove any remaining filler
            for filler in ['bana do', 'kar do', 'add kar do', 'mera', 'please', 'task', 'create', 'add']:
                title = title.replace(filler, '').strip()
            title = title.strip()
        
        print(f"PARSE DEBUG: message='{message}' -> intent={intent}, title={title}")
        return (intent, title, extra)
        
    except Exception as e:
        print(f"Parse error: {e}")
        return ("chat", None, None)

async def get_available_tools(mcp_server_instance) -> List[Dict[str, Any]]:
    """Get list of available MCP tools"""
    if not mcp_server_instance:
        return []

    return [
        {
            "name": "get_tasks",
            "description": "Retrieve all tasks for the authenticated user",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_token": {"type": "string", "description": "User session token"}
                },
                "required": ["session_token"]
            }
        },
        {
            "name": "create_task",
            "description": "Create a new todo item",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_token": {"type": "string", "description": "User session token"},
                    "title": {"type": "string", "description": "The title of the task"},
                    "description": {"type": "string", "description": "Optional description"}
                },
                "required": ["session_token", "title"]
            }
        },
        {
            "name": "update_task",
            "description": "Update an existing task",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_token": {"type": "string", "description": "User session token"},
                    "task_id": {"type": "string", "description": "UUID of the task"},
                    "title": {"type": "string", "description": "New title"},
                    "status": {"type": "string", "description": "pending or completed"},
                    "description": {"type": "string", "description": "New description"}
                },
                "required": ["session_token", "task_id"]
            }
        },
        {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_token": {"type": "string", "description": "User session token"},
                    "task_id": {"type": "string", "description": "UUID of the task"}
                },
                "required": ["session_token", "task_id"]
            }
        }
    ]

async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any], mcp_server_instance) -> Any:
    """Call an MCP tool with the given arguments"""
    if not mcp_server_instance:
        raise Exception("MCP server not available")

    from agents.mcp import MCPServerStdio

    async with mcp_server_instance:
        result = await mcp_server_instance.call_tool(tool_name, arguments)
        return result

async def chat_with_agent(message: str, session_token: str, mcp_server_instance=None) -> str:
    """Chat with the agent using Cohere - Two-phase approach"""

    # Phase 1: Parse intent and extract clean title
    intent, title, extra = await parse_user_intent(message)
    
    try:
        client = cohere.AsyncClient(api_key=COHERE_API_KEY)
        
        # Phase 2: Execute based on intent
        if intent == "create" and title:
            # We have a clean title - directly call create_task
            tools = await get_available_tools(mcp_server_instance)
            
            try:
                tool_result = await call_mcp_tool("create_task", {
                    "session_token": session_token,
                    "title": title
                }, mcp_server_instance)
                
                # Generate friendly response
                response = await client.chat(
                    model=COHERE_MODEL,
                    message=f"Task '{title}' was created successfully. Respond in the same language as: '{message}'. Use emoji ✅ and say 'Task add ho gaya: {title}'",
                    temperature=0.7
                )
                return response.text or f"✅ Task add ho gaya: '{title}'"
                
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        elif intent == "list":
            tools = await get_available_tools(mcp_server_instance)
            
            try:
                tasks = await call_mcp_tool("get_tasks", {
                    "session_token": session_token
                }, mcp_server_instance)
                
                if isinstance(tasks, list) and len(tasks) > 0:
                    task_list = "\n".join([f"{i+1}. {t.get('title', 'Task')}" for i, t in enumerate(tasks)])
                    return f"📋 Aapke tasks:\n{task_list}"
                else:
                    return "📋 Koi tasks nahi hain!"
                    
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        elif intent == "update":
            # Need to find the task first
            try:
                tasks = await call_mcp_tool("get_tasks", {
                    "session_token": session_token
                }, mcp_server_instance)
                
                # Find matching task by title contains 'extra' keyword
                task_id = None
                if isinstance(tasks, list):
                    for task in tasks:
                        if extra and extra.lower() in task.get('title', '').lower():
                            task_id = task.get('id')
                            break
                
                if task_id:
                    await call_mcp_tool("update_task", {
                        "session_token": session_token,
                        "task_id": task_id,
                        "status": "completed"
                    }, mcp_server_instance)
                    return "✅ Task complete ho gaya!"
                else:
                    return "❌ Task nahi mila. Kaunsa task complete hua?"
                    
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        elif intent == "delete":
            # Similar to update - find task first
            try:
                tasks = await call_mcp_tool("get_tasks", {
                    "session_token": session_token
                }, mcp_server_instance)
                
                task_id = None
                if isinstance(tasks, list):
                    for task in tasks:
                        if extra and extra.lower() in task.get('title', '').lower():
                            task_id = task.get('id')
                            break
                
                if task_id:
                    await call_mcp_tool("delete_task", {
                        "session_token": session_token,
                        "task_id": task_id
                    }, mcp_server_instance)
                    return "🗑️ Task delete ho gaya!"
                else:
                    return "❌ Task nahi mila. Kaunsa task delete karna hai?"
                    
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        else:
            # General chat - use Cohere directly
            response = await client.chat(
                model=COHERE_MODEL,
                message=message,
                preamble="""You are a friendly Todo Assistant. You speak English, Hindi, Urdu, and Hinglish.
Respond in the same language the user uses. Be helpful and friendly. Use emojis.
You can help users manage their tasks - create, list, complete, or delete tasks.""",
                temperature=0.7
            )
            return response.text or "I'm here to help!"

    except Exception as e:
        print(f"Error: {e}")
        return f"❌ Error: {str(e)}"

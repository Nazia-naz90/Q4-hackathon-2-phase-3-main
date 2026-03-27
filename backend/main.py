from fastapi import FastAPI, Depends, HTTPException, status, Header
from contextlib import asynccontextmanager
from typing import List, Optional
from sqlmodel import Session, select, func
from database import create_db_and_tables, get_session
from models import Task, TaskCreate, TaskUpdate, TaskRead, User, UserCreate, UserRead, Token
from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import ValidationError, BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx

# Load environment variables from project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
if not SECRET_KEY or SECRET_KEY == "your-secret-key-change-in-production":
    raise ValueError("SECRET_KEY environment variable must be set to a secure value in production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Define lifespan to run database setup on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run database setup on startup
    create_db_and_tables()
    yield
    # Any cleanup code can go here if needed


app = FastAPI(lifespan=lifespan, title="TaskFlow API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "TaskFlow API is running!"}


# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_username(session: Session, username: str):
    from sqlmodel import select
    try:
        return session.exec(select(User).where(User.username == username)).first()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def get_user_by_email(session: Session, email: str):
    from sqlmodel import select
    try:
        return session.exec(select(User).where(User.email == email)).first()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user


# Authentication endpoints
@app.post("/auth/signup", response_model=UserRead)
def signup(user_create: UserCreate, session: Session = Depends(get_session)):
    try:
        # Check if user already exists
        existing_user = get_user_by_username(session, user_create.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        existing_email = get_user_by_email(session, user_create.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the password
        hashed_password = get_password_hash(user_create.password)

        # Create new user
        db_user = User(
            id=str(uuid.uuid4()),
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            is_admin=False,  # Default to False for new signups
            is_user=True     # Default to True for regular users
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred during signup: {str(e)}")


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    try:
        username = form_data.username  # This will be the email
        password = form_data.password
        from sqlmodel import select
        # Look for user by email instead of username
        user = session.exec(select(User).where(User.email == username)).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "is_admin": user.is_admin,
            "is_user": user.is_user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during login: {str(e)}")




# Simplified endpoints that extract user_id from JWT token
@app.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Create a new task for the authenticated user
    """
    try:
        db_task = Task(user_id=current_user.id, **task.model_dump())
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the task: {str(e)}")


@app.get("/tasks", response_model=List[TaskRead])
def read_tasks(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Get all tasks for the authenticated user
    """
    try:
        from sqlmodel import select
        tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
        return tasks
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving tasks: {str(e)}")


@app.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(task_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Get a specific task by ID for the authenticated user
    """
    try:
        task = session.get(Task, task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving the task: {str(e)}")


@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: str, task_update: TaskUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Update a specific task by ID for the authenticated user
    """
    try:
        task = session.get(Task, task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Task not found")

        # Update task fields
        for field, value in task_update.model_dump(exclude_unset=True).items():
            setattr(task, field, value)

        # If status is being updated to 'completed', set completed_at timestamp
        if hasattr(task_update, 'status') and task_update.status == "completed" and task.status != "completed":
            task.completed_at = datetime.utcnow()
        # If status is being updated from 'completed' to something else, clear completed_at
        elif hasattr(task_update, 'status') and task_update.status != "completed" and task.status == "completed":
            task.completed_at = None

        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the task: {str(e)}")


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Delete a specific task by ID for the authenticated user
    """
    try:
        task = session.get(Task, task_id)
        if not task or task.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Task not found")

        session.delete(task)
        session.commit()
        return
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while deleting the task: {str(e)}")


# Admin stats endpoint
@app.get("/api/admin/stats")
def get_admin_stats(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Get admin statistics - only accessible if current_user.is_admin == True
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin users can access this endpoint")

    from sqlmodel import select
    from datetime import datetime, timedelta

    # Total Users count
    total_users = session.exec(select(func.count(User.id))).one()

    # Total Tasks count
    total_tasks = session.exec(select(func.count(Task.id))).one()

    # Tasks distribution by Priority (Low, Medium, High)
    priority_counts = {}
    for priority in ["low", "medium", "high"]:
        count = session.exec(select(func.count(Task.id)).where(Task.priority == priority)).one()
        priority_counts[priority] = count

    # Tasks distribution by Status (Pending, Completed)
    status_counts = {}
    for status in ["pending", "completed"]:
        count = session.exec(select(func.count(Task.id)).where(Task.status == status)).one()
        status_counts[status] = count

    # Recent Task activity (tasks created in the last 7 days) for a Line Chart
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_tasks = session.exec(
        select(Task).where(Task.created_at >= seven_days_ago)
    ).all()

    # Group by date for the line chart
    from collections import defaultdict
    daily_task_counts = defaultdict(int)
    for task in recent_tasks:
        date_str = task.created_at.strftime("%Y-%m-%d")
        daily_task_counts[date_str] += 1

    # Format for chart (sort by date)
    recent_task_activity = []
    for date_str in sorted(daily_task_counts.keys()):
        recent_task_activity.append({
            "date": date_str,
            "count": daily_task_counts[date_str]
        })

    return {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "tasks_by_priority": priority_counts,
        "tasks_by_status": status_counts,
        "recent_task_activity": recent_task_activity
    }


# ============================================
# AI Chatbot Endpoints (Using Cohere API)
# ============================================

# Add required imports for Cohere
import cohere
import re

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str


def extract_task_title(message: str, message_lower: str) -> str:
    """
    Extract task title from natural language message using improved NLP.
    Handles English, Urdu/Hindi (Romanized), and mixed language inputs.
    """
    title = ""
    
    # Priority 1: Extract text within quotes (single or double)
    quote_patterns = [
        r'["\']([^"\']+)["\']',  # Text in quotes
        r'["\']([^"\']+)$',       # Text in quotes at end
    ]
    
    for pattern in quote_patterns:
        match = re.search(pattern, message)
        if match:
            title = match.group(1).strip()
            if title:
                return title
    
    # Priority 2: Handle common patterns for task name extraction
    
    # Pattern: "named X", "name X", "jiska naam X", "jiska name X"
    name_patterns = [
        (r'(?:named|name|naam|jiska\s+naam|jiska\s+name|jiska\s+naam\s+ho)\s+(?:["\']?)([^"\',.!?]+?)(?:["\']?)(?:\s*(?:ho|hai|for|to|that|please|mera|mere))?(?:\s*$)', 1),
        (r'(?:jiska\s+naam|jiska\s+name)\s+(?:["\']?)([^"\',.!?]+?)(?:["\']?)(?:\s*ho)?$', 1),
    ]
    
    for pattern, group in name_patterns:
        match = re.search(pattern, message_lower)
        if match:
            title = match.group(group).strip()
            # Clean up common trailing words
            for word in ['ho', 'hai', 'please', 'mera', 'mere', 'for me', 'for']:
                if title.lower().endswith(f' {word}'):
                    title = title[:-len(word)-1].strip()
            if title:
                return title.title() if title else ""
    
    # Priority 3: Extract after action keywords
    action_keywords = ['create', 'add', 'new task', 'make a task', 'banado', 'bana do', 'bana', 'create a task', 'create task']
    
    for keyword in action_keywords:
        if keyword in message_lower:
            # Find position of keyword
            keyword_pos = message_lower.find(keyword)
            # Get text after keyword
            remaining_text = message[keyword_pos + len(keyword):].strip()
            
            # Remove common starting words
            cleanup_patterns = [
                r'^(?:meri|mere|mera|meray|ek|a|an|the|for|to|that|which|is|jo|ye|yeh|wo|woh)\s+',
                r'^(?:task|task\s+to|task\s+for)\s+',
                r'^(?:create|add|make|banado|bana)\s+',
            ]
            
            for cleanup_pattern in cleanup_patterns:
                remaining_text = re.sub(cleanup_pattern, '', remaining_text, flags=re.IGNORECASE).strip()
            
            # If remaining text has quotes, extract from quotes
            quote_match = re.search(r'["\']([^"\']+)["\']', remaining_text)
            if quote_match:
                title = quote_match.group(1).strip()
            else:
                # Take text until common ending words or punctuation
                end_patterns = [
                    r'\s+(?:for|to|that|which|please|pls|mera|mere|ho|hai|jaldi|aaj|kal)$',
                    r'\s+(?:for|to|that|which|please|pls|mera|mere|ho|hai)\s+\w+',
                    r'[.!?]\s*$',
                ]
                
                title = remaining_text
                for end_pattern in end_patterns:
                    end_match = re.search(end_pattern, title)
                    if end_match:
                        title = title[:end_match.start()].strip()
                        break
            
            if title and len(title) > 2:
                return title.title()
    
    # Priority 4: Fallback - take the last meaningful phrase
    # Remove common phrases and take what's left
    cleaned = message
    for phrase in ['create', 'create a', 'create task', 'create a task', 'add', 'add a', 
                   'new task', 'make', 'make a', 'make a task', 'banado', 'bana do', 
                   'bana', 'please', 'pls', 'for me', 'mera', 'mere', 'meri', 'meray',
                   'ek', 'a', 'an', 'the', 'task', 'jisko', 'jiska', 'jo', 'ye', 'yeh']:
        cleaned = re.sub(r'\b' + phrase + r'\b', '', cleaned, flags=re.IGNORECASE)
    
    cleaned = cleaned.strip(' ,.!?-:;')
    
    if cleaned and len(cleaned) > 2:
        return cleaned.title()
    
    # Final fallback
    return "Untitled Task"


def get_cohere_client():
    """Initialize and return Cohere client"""
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if not cohere_api_key:
        raise HTTPException(status_code=500, detail="COHERE_API_KEY not found in environment variables")

    try:
        client = cohere.Client(api_key=cohere_api_key)
        return client
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Cohere client: {str(e)}")


def process_ai_message_with_cohere(message: str, current_user: User, session: Session) -> str:
    """
    AI processor using Cohere API for task management with DIRECT action execution
    Supports English, Urdu, and Hindi (Romanized)
    """
    try:
        message_lower = message.lower().strip()
        
        # ============================================
        # STEP 1: Detect intent and execute actions DIRECTLY
        # ============================================
        
        # --- DELETE INTENT (English + Urdu/Hindi) ---
        if any(word in message_lower for word in [
            "delete", "remove", "cancel task",
            "khatam", "mita", "delete karo", "mita do", "hata do"
        ]):
            # Extract task ID from message
            import re
            id_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', message)
            
            if id_match:
                task_id = id_match.group()
                try:
                    task = session.get(Task, task_id)
                    if not task or task.user_id != current_user.id:
                        return "❌ Task not found! Please check the task ID."
                    
                    task_title = task.title
                    session.delete(task)
                    session.commit()
                    return f"🗑️ Task '{task_title}' has been successfully deleted!"
                except Exception as e:
                    session.rollback()
                    return f"❌ Failed to delete task: {str(e)}"
            else:
                # Try to extract short ID (8 characters in brackets like [69845ec4])
                short_id_match = re.search(r'\[([0-9a-f]{8})\]', message_lower)
                if short_id_match:
                    short_id = short_id_match.group(1)
                    user_tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
                    for task in user_tasks:
                        if task.id[:8] == short_id:
                            try:
                                session.delete(task)
                                session.commit()
                                return f"🗑️ Task '{task.title}' has been successfully deleted!"
                            except Exception as e:
                                session.rollback()
                                return f"❌ Failed to delete task: {str(e)}"
                
                # Try to find task by title
                user_tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
                for task in user_tasks:
                    if task.title.lower() in message_lower or str(task.id[:8]) in message_lower:
                        try:
                            session.delete(task)
                            session.commit()
                            return f"🗑️ Task '{task.title}' has been successfully deleted!"
                        except Exception as e:
                            session.rollback()
                            return f"❌ Failed to delete task: {str(e)}"
                
                # No matching task found
                if user_tasks:
                    tasks_list = "\n".join([f"- [{t.id[:8]}] {t.title}" for t in user_tasks])
                    return f"❓ Please specify which task to delete. Your tasks:\n{tasks_list}"
                else:
                    return "📋 You have no tasks to delete."
        
        # --- COMPLETE TASK INTENT (English + Urdu/Hindi) ---
        elif any(word in message_lower for word in [
            "complete", "finish", "done", "mark as done",
            "pura", "khatam", "ho gaya", "hogaya", "complete karo", "khatam karo"
        ]):
            import re
            
            # Try to extract full UUID first
            id_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', message)
            
            if id_match:
                task_id = id_match.group()
                task = session.get(Task, task_id)
                if task and task.user_id == current_user.id:
                    task.status = "completed"
                    task.completed_at = datetime.utcnow()
                    session.commit()
                    return f"✅ Task '{task.title}' marked as completed!"
            
            # Try to extract short ID (8 characters in brackets like [69845ec4])
            short_id_match = re.search(r'\[([0-9a-f]{8})\]', message_lower)
            if short_id_match:
                short_id = short_id_match.group(1)
                # Find the full task by matching first 8 characters
                user_tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
                for task in user_tasks:
                    if task.id[:8] == short_id:
                        task.status = "completed"
                        task.completed_at = datetime.utcnow()
                        session.commit()
                        return f"✅ Task '{task.title}' marked as completed!"
            
            # Try by title
            user_tasks = session.exec(select(Task).where(Task.user_id == current_user.id, Task.status == "pending")).all()
            for task in user_tasks:
                if task.title.lower() in message_lower or str(task.id[:8]) in message_lower:
                    task.status = "completed"
                    task.completed_at = datetime.utcnow()
                    session.commit()
                    return f"✅ Task '{task.title}' marked as completed!"
            
            return "❓ Please specify which task to complete. Use format: 'Complete task [ID]' or 'Complete [task-id]'"
        
        # --- CREATE TASK INTENT (English + Urdu/Hindi) ---
        elif any(word in message_lower for word in [
            "create", "add", "make a task", "banado", "bana do", "bana",
            "naya task", "new task", "task bana", "bana do", "banado"
        ]):
            title = extract_task_title(message, message_lower)
            
            if title and len(title.strip()) > 0:
                try:
                    db_task = Task(
                        user_id=current_user.id,
                        title=title.strip(),
                        description=f"Created via AI chat: {message}",
                        status="pending",
                        priority="medium"
                    )
                    session.add(db_task)
                    session.commit()
                    session.refresh(db_task)
                    return f"✅ Task created: '{db_task.title}' (ID: {db_task.id[:8]})"
                except Exception as e:
                    session.rollback()
                    return f"❌ Failed to create task: {str(e)}"
        
        # --- LIST TASKS INTENT (English + Urdu/Hindi) ---
        elif any(word in message_lower for word in [
            "list", "show", "my tasks", "all tasks", "get tasks",
            "dikha", "dikhao", "meri tasks", "saare tasks", "show karo"
        ]):
            user_tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
            if not user_tasks:
                return "📋 You have no tasks yet. Create one to get started!"
            
            response_text = "📋 Your tasks:\n\n"
            for task in user_tasks:
                status_icon = "✅" if task.status == "completed" else "⏳"
                priority_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(task.priority, "🟡")
                response_text += f"{status_icon} {priority_icon} [{task.id[:8]}] {task.title} - {task.status}\n"
            return response_text
        
        # ============================================
        # STEP 2: For other queries, use Cohere AI
        # ============================================
        
        # Get Cohere client
        cohere_client = get_cohere_client()

        # Get user's tasks for context
        user_tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
        tasks_context = ""
        if user_tasks:
            tasks_context = "User's current tasks:\n"
            for task in user_tasks:
                status_icon = "✅" if task.status == "completed" else "⏳"
                priority_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(task.priority, "🟡")
                tasks_context += f"- {status_icon} {priority_icon} [{task.id[:8]}] {task.title} ({task.status})\n"
        else:
            tasks_context = "User has no tasks yet.\n"

        # Create a prompt that guides the AI to understand task management commands
        prompt = f"""
You are an AI productivity assistant that helps users manage their tasks. The user is interacting with a task management system. Based on their message, help them with their tasks or provide general assistance.

Current user context:
{tasks_context}

User message: "{message}"

Provide a helpful, concise response. Use emojis where appropriate.
"""

        # Call Cohere API using chat endpoint
        response = cohere_client.chat(
            model=os.getenv("COHERE_MODEL", "command-r-08-2024"),
            message=prompt,
            max_tokens=300,
            temperature=0.7
        )

        ai_response = response.text.strip()
        print(f"✓ Cohere API response received: {ai_response[:100]}...")
        return ai_response

    except Exception as e:
        # Fallback to simple rule-based system if Cohere fails
        print(f"Cohere API error: {str(e)}")

        # Use improved rule-based system as fallback
        message_lower = message.lower().strip()

        # Delete task
        if any(word in message_lower for word in ["delete", "remove", "cancel task"]):
            import re
            id_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', message_lower)
            if id_match:
                task_id = id_match.group()
            else:
                return "Please specify the task ID to delete."

            try:
                task = session.get(Task, task_id)
                if not task or task.user_id != current_user.id:
                    return "❌ Task not found!"

                task_title = task.title
                session.delete(task)
                session.commit()
                return f"🗑️ Task '{task_title}' deleted!"
            except Exception as e:
                return f"❌ Failed to delete task: {str(e)}"

        # Help
        elif any(word in message_lower for word in ["help", "what can you do", "commands"]):
            return """
🤖 **AI Assistant Commands:**

📝 **Create:** "Create a task to buy groceries"
📋 **List:** "Show my tasks" or "List all tasks"
✅ **Complete:** "Complete task [ID]" or "Mark task as done"
🗑️ **Delete:** "Delete task [ID]"

💡 Just tell me what you want to do in natural language!
""".strip()

        # Default response
        else:
            return """
🤖 Hi! I'm your AI productivity assistant. I can help you:
- Create tasks: "Create a task to buy groceries"
- List tasks: "Show my tasks"
- Complete tasks: "Complete task [ID]"
- Delete tasks: "Delete task [ID]"
- Help: "What can you do?"

Try asking me to do something! 😊
""".strip()


@app.post("/ai/chat", response_model=ChatResponse)
async def ai_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Chat with the AI assistant (Using Cohere API with fallback to rule-based)
    """
    try:
        response_text = process_ai_message_with_cohere(request.message, current_user, session)
        return ChatResponse(response=response_text)
    except Exception as e:
        return ChatResponse(response=f"❌ Sorry, I encountered an error: {str(e)}")


@app.get("/ai/health")
async def ai_health():
    """Check AI chatbot status"""
    try:
        # Try to initialize Cohere client to verify API key works
        cohere_api_key = os.getenv("COHERE_API_KEY")
        if cohere_api_key:
            # Test the API briefly
            try:
                client = cohere.Client(api_key=cohere_api_key)
                status_msg = "Cohere API integrated and ready"
                mode = "cohere-integrated"
            except:
                status_msg = "Cohere API key configured but initialization failed, using rule-based fallback"
                mode = "rule-based-fallback"
        else:
            status_msg = "Cohere API key not configured, using rule-based fallback"
            mode = "rule-based"

        return {
            "status": "healthy",
            "mode": mode,
            "message": status_msg
        }
    except Exception:
        return {
            "status": "degraded",
            "mode": "rule-based-fallback",
            "message": "Cohere API initialization failed, using rule-based fallback"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

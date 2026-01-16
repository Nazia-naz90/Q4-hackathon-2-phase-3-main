from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager
from typing import List
from sqlmodel import Session, select, func
from database import create_db_and_tables, get_session
from models import Task, TaskCreate, TaskUpdate, TaskRead, User, UserCreate, UserRead, Token
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import uuid
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from pydantic import ValidationError
from fastapi.middleware.cors import CORSMiddleware
import sys
import importlib.util

# Load environment variables
load_dotenv()

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
        # Include user roles in the token payload for client-side verification
        token_data = {
            "sub": user.id,
            "user_id": user.id,
            "is_admin": user.is_admin,
            "is_user": user.is_user,
            "username": user.username,
            "email": user.email
        }
        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
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
        # Check for inappropriate terms in the task title before creating
        inappropriate_terms = ['duffer', 'idiot', 'stupid', 'dummy', 'fool', 'moron', 'jerk', 'asshole', 'dumb']
        task_title_lower = task.title.lower().strip()

        if any(term in task_title_lower for term in inappropriate_terms):
            raise HTTPException(status_code=400, detail="Task title contains inappropriate content")

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


# Chatbot endpoint
@app.post("/api/chatbot")
async def chatbot_endpoint(message: dict, current_user: User = Depends(get_current_user)):
    """
    Endpoint for the AI-powered Todo Chatbot using MCP
    Accepts a message from the frontend and returns a response from the MCP agent
    """
    try:
        # Validate input
        if not message or "message" not in message:
            raise HTTPException(status_code=400, detail="Message field is required")

        user_message = message.get("message", "")

        if not isinstance(user_message, str):
            raise HTTPException(status_code=400, detail="Message must be a string")

        # Check message length
        if len(user_message) > 1000:
            raise HTTPException(status_code=400, detail="Message too long. Please keep it under 1000 characters.")

        # Check for inappropriate terms before processing
        user_message_lower = user_message.lower().strip()
        inappropriate_terms = ['duffer', 'idiot', 'stupid', 'dummy', 'fool', 'moron', 'jerk', 'asshole', 'dumb']

        if any(term in user_message_lower for term in inappropriate_terms):
            return {"response": "I am AI Todo Assistant, you can add, update, or delete tasks by telling me what you'd like to do!"}

        # Check if OPENAI_API_KEY is available
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return {"response": "AI chatbot is not available because the OpenAI API key is not configured. Please contact the administrator to set the OPENAI_API_KEY environment variable."}

        # Import the TodoChatAgent from the mcp-server
        # We need to dynamically import to avoid circular imports
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-server'))

        # Load the agent module
        agent_spec = importlib.util.spec_from_file_location("test_agent_chat",
                                                           os.path.join(os.path.dirname(__file__), '..', 'mcp-server', 'test_agent_chat.py'))
        agent_module = importlib.util.module_from_spec(agent_spec)
        agent_spec.loader.exec_module(agent_module)

        # Create and use the agent
        agent = agent_module.TodoChatAgent()

        # Process the message and get response
        response = await agent.process_message(user_message, current_user.id)

        return {"response": response}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chatbot request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class UserBase(SQLModel):
    username: str
    email: str


class User(UserBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    hashed_password: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    is_admin: bool = Field(default=False)
    is_user: bool = Field(default=True)  # Default to true for regular users


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_admin: bool
    is_user: bool


class Token(SQLModel):
    access_token: str
    token_type: str
    user_id: str
    is_admin: bool
    is_user: bool


class TokenData(SQLModel):
    username: Optional[str] = None


class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"  # pending, completed
    priority: Optional[str] = "medium"  # low, medium, high
    due_date: Optional[datetime] = None


class Task(TaskBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    user_id: str = Field(index=True)  # Store user_id as string


class TaskCreate(TaskBase):
    # user_id is not required in the JSON body - it will be automatically assigned
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # pending, completed
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskRead(TaskBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
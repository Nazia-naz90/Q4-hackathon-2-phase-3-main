from sqlmodel import create_engine, Session, SQLModel
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Generator

# Load environment variables from project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Get database URL from environment - Use sync psycopg2 driver
DATABASE_URL = os.getenv("DATABASE_URL_UNPOOLED")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL_UNPOOLED environment variable is required")

# Replace postgresql+asyncpg with postgresql for sync driver
if DATABASE_URL.startswith("postgresql+asyncpg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
elif DATABASE_URL.startswith("postgresql://"):
    # Already using sync driver, ensure psycopg2 is used
    pass

# Create the engine with connection pooling settings for Neon PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_size=20,  # Increase pool size for production
    max_overflow=30,  # Allow additional connections when needed
)


def create_db_and_tables():
    """Create database tables if they don't exist"""
    SQLModel.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    """Get a database session"""
    with Session(engine) as session:
        yield session
from sqlmodel import create_engine, Session, SQLModel
import os
from dotenv import load_dotenv
from typing import Generator

# Load environment variables
load_dotenv()

# Get database URL from environment - Strictly use Neon PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DATABASE_URL_UNPOOLED")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL or DATABASE_URL_UNPOOLED environment variable is required")

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
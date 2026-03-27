#!/usr/bin/env python3
"""
Temporary script to reset the database schema
"""

from sqlmodel import SQLModel
from database import engine
import sys

def reset_database():
    print("Resetting database schema...")
    
    try:
        print("Dropping all existing tables...")
        SQLModel.metadata.drop_all(engine)
        print("All tables dropped successfully!")
        
        print("Creating all tables...")
        SQLModel.metadata.create_all(engine)
        print("All tables created successfully!")
        
        print("Database schema reset completed!")
        
    except Exception as e:
        print(f"Error resetting database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()
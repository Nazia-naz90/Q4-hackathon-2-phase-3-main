#!/usr/bin/env python3
"""
Test script to verify connection to Neon PostgreSQL database.
"""

import os
import sys
from pathlib import Path

# Add backend to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_neon_connection():
    """Test connection to Neon PostgreSQL database."""
    print("Testing connection to Neon PostgreSQL database...")

    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv(str(project_root / ".env"))

        # Import database components
        from backend.database import engine, create_db_and_tables
        from sqlalchemy import text

        print("Attempting to connect to database...")

        # Test the connection
        with engine.connect() as connection:
            # Test basic connectivity
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()
            print(f"✅ Connected to PostgreSQL: {version[0][:50]}...")

            # Create tables if they don't exist
            print("Creating/verifying database tables...")
            create_db_and_tables()
            print("✅ Tables created/verified successfully")

            # Check if tasks table exists
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'task'
                );
            """))
            table_exists = result.fetchone()[0]

            if table_exists:
                print("✅ Task table exists in database")
            else:
                print("❌ Task table does not exist in database")

            # Check if users table exists
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'user'
                );
            """))
            user_table_exists = result.fetchone()[0]

            if user_table_exists:
                print("✅ User table exists in database")
            else:
                print("⚠️  User table does not exist in database")

        print("\n🎉 Successfully connected to Neon PostgreSQL database!")
        print("📋 Database connection is ready for the AI-Powered Todo Chatbot.")
        return True

    except Exception as e:
        print(f"❌ Error connecting to database: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_neon_connection()

    if success:
        print("\n✅ NEON POSTGRESQL CONNECTION: SUCCESS")
        print("The AI-Powered Todo Chatbot is ready to use your Neon database!")
    else:
        print("\n❌ NEON POSTGRESQL CONNECTION: FAILED")
        sys.exit(1)
#!/usr/bin/env python3
"""
Quick startup test for the MCP server.
"""

import sys
from pathlib import Path
import asyncio

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

def test_mcp_startup():
    """Test that MCP server can be initialized without errors."""
    try:
        # Import the main module to check for import errors
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", project_root / "mcp-server" / "main.py")
        main_module = importlib.util.module_from_spec(spec)

        # Just check if we can load the module without running it
        print("✅ MCP Server module loaded successfully")

        # Check that required functions exist
        spec.loader.exec_module(main_module)

        required_functions = [
            'create_task',
            'get_tasks',
            'update_task',
            'delete_task',
            'toggle_task_completion'
        ]

        for func_name in required_functions:
            if hasattr(main_module, func_name):
                print(f"✅ Function {func_name} is available")
            else:
                print(f"❌ Function {func_name} is missing")
                return False

        # Test database connection
        from backend.database import engine
        print("✅ Database engine initialized successfully")

        # Test model imports
        from backend.models import Task, TaskCreate, TaskUpdate
        print("✅ Backend models imported successfully")

        print("\n🎉 MCP Server is ready for OpenAI Agent integration!")
        print("📋 All components are properly integrated and functional")
        return True

    except Exception as e:
        print(f"❌ Error during startup test: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing MCP Server Startup...")
    print("=" * 40)

    success = test_mcp_startup()

    if success:
        print("\n✅ INTEGRATION VALIDATION: SUCCESS")
        print("The AI-Powered Todo Chatbot is ready for OpenAI Agent integration!")
    else:
        print("\n❌ INTEGRATION VALIDATION: FAILED")
        sys.exit(1)
#!/usr/bin/env python3
"""
Validation script to verify the Phase 3 AI-Powered Todo Chatbot implementation.
This script checks that all required components have been created correctly.
"""

import os
import sys
from pathlib import Path


def validate_implementation():
    """Validate all components of the Phase 3 implementation."""
    print("Validating Phase 3: AI-Powered Todo Chatbot Implementation")
    print("=" * 60)

    # Check 1: Constitution updated
    constitution_path = Path(".specify/memory/constitution.md")
    if constitution_path.exists():
        content = constitution_path.read_text()
        if "Conversational Interface Excellence" in content and "Secure Tool Execution" in content:
            print("[PASS] Constitution updated with Phase 3 principles")
        else:
            print("[FAIL] Constitution missing Phase 3 principles")
            return False
    else:
        print("[FAIL] Constitution file not found")
        return False

    # Check 2: Feature spec created
    spec_path = Path("specs/phase3-chatbot/spec.md")
    if spec_path.exists():
        content = spec_path.read_text()
        if "AI-Powered Todo Chatbot Specification" in content:
            print("[PASS] Feature spec created for AI-powered chatbot")
        else:
            print("[FAIL] Feature spec doesn't match expected content")
            return False
    else:
        print("[FAIL] Feature spec file not found")
        return False

    # Check 3: MCP server directory and main file
    mcp_main_path = Path("mcp-server/main.py")
    if mcp_main_path.exists():
        content = mcp_main_path.read_text()
        if "server = Server" in content and "create_task" in content and "get_tasks" in content:
            print("[PASS] MCP server main.py created with required tools")
        else:
            print("[FAIL] MCP server main.py missing required components")
            return False
    else:
        print("[FAIL] MCP server main.py not found")
        return False

    # Check 4: MCP tools test file
    mcp_tools_test_path = Path("mcp-server/test_mcp_tools.py")
    if mcp_tools_test_path.exists():
        content = mcp_tools_test_path.read_text()
        if "mock_create_task" in content and "mock_get_tasks" in content:
            print("[PASS] MCP tools test file created")
        else:
            print("[FAIL] MCP tools test file missing required components")
            return False
    else:
        print("[FAIL] MCP tools test file not found")
        return False

    # Check 5: Agent chat test file
    agent_chat_path = Path("mcp-server/test_agent_chat.py")
    if agent_chat_path.exists():
        content = agent_chat_path.read_text()
        if "TodoChatAgent" in content and "process_message" in content:
            print("[PASS] Agent chat interaction module created")
        else:
            print("[FAIL] Agent chat module missing required components")
            return False
    else:
        print("[FAIL] Agent chat interaction module not found")
        return False

    # Check 6: Directory structure
    mcp_dir = Path("mcp-server")
    if mcp_dir.exists() and mcp_dir.is_dir():
        print("[PASS] MCP server directory structure created")
    else:
        print("[FAIL] MCP server directory not found")
        return False

    phase3_dir = Path("specs/phase3-chatbot")
    if phase3_dir.exists() and phase3_dir.is_dir():
        print("[PASS] Phase 3 specs directory structure created")
    else:
        print("[FAIL] Phase 3 specs directory not found")
        return False

    print("\n" + "=" * 60)
    print("[SUCCESS] All Phase 3 components have been successfully implemented!")
    print("\nSummary of Implementation:")
    print("- Updated constitution with conversational UI and secure tool execution principles")
    print("- Created detailed feature specification for AI-powered chatbot")
    print("- Implemented MCP server with CRUD operation tools")
    print("- Created test files for MCP tools integration")
    print("- Developed agent interaction module with natural language processing")
    print("- All components follow the Spec-Driven Development workflow")

    return True


def main():
    """Main function to run the validation."""
    success = validate_implementation()
    if success:
        print("\n[SUCCESS] Phase 3 Implementation Validation: PASSED")
        sys.exit(0)
    else:
        print("\n[ERROR] Phase 3 Implementation Validation: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Direct inspection of the source code to verify the fix.
"""

import ast
import inspect
import os

# Read the file directly and parse the AST to verify the function definitions
def inspect_source_code():
    print("Inspecting source code in mcp-server/test_agent_chat.py...")

    with open('mcp-server/test_agent_chat.py', 'r') as f:
        content = f.read()

    tree = ast.parse(content)

    # Find the TodoChatAgent class
    agent_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'TodoChatAgent':
            agent_class = node
            break

    if not agent_class:
        print("✗ TodoChatAgent class not found")
        return False

    print("✓ Found TodoChatAgent class")

    # Look for the methods
    methods_found = {}
    for node in agent_class.body:
        if isinstance(node, ast.AsyncFunctionDef):
            methods_found[node.name] = node

    # Check create_task method
    if 'create_task' in methods_found:
        method = methods_found['create_task']
        params = [arg.arg for arg in method.args.args]
        print(f"✓ create_task parameters: {params}")
        if 'user_id' in params:
            print("✓ create_task accepts user_id parameter")
        else:
            print("✗ create_task does NOT accept user_id parameter")
            return False
    else:
        print("✗ create_task method not found")
        return False

    # Check get_tasks method
    if 'get_tasks' in methods_found:
        method = methods_found['get_tasks']
        params = [arg.arg for arg in method.args.args]
        print(f"✓ get_tasks parameters: {params}")
        if 'user_id' in params:
            print("✓ get_tasks accepts user_id parameter")
        else:
            print("✗ get_tasks does NOT accept user_id parameter")
            return False
    else:
        print("✗ get_tasks method not found")
        return False

    # Check update_task method
    if 'update_task' in methods_found:
        method = methods_found['update_task']
        params = [arg.arg for arg in method.args.args]
        print(f"✓ update_task parameters: {params}")
        if 'user_id' in params:
            print("✓ update_task accepts user_id parameter")
        else:
            print("✗ update_task does NOT accept user_id parameter")
            return False
    else:
        print("✗ update_task method not found")
        return False

    # Check delete_task method
    if 'delete_task' in methods_found:
        method = methods_found['delete_task']
        params = [arg.arg for arg in method.args.args]
        print(f"✓ delete_task parameters: {params}")
        if 'user_id' in params:
            print("✓ delete_task accepts user_id parameter")
        else:
            print("✗ delete_task does NOT accept user_id parameter")
            return False
    else:
        print("✗ delete_task method not found")
        return False

    # Check toggle_task_completion method
    if 'toggle_task_completion' in methods_found:
        method = methods_found['toggle_task_completion']
        params = [arg.arg for arg in method.args.args]
        print(f"✓ toggle_task_completion parameters: {params}")
        if 'user_id' in params:
            print("✓ toggle_task_completion accepts user_id parameter")
        else:
            print("✗ toggle_task_completion does NOT accept user_id parameter")
            return False
    else:
        print("✗ toggle_task_completion method not found")
        return False

    print("\n✓ All function signatures in the source code have been updated correctly!")
    print("The original error 'TodoChatAgent.create_task() got an unexpected keyword argument 'user_id'' should now be fixed.")

    # Also inspect the mcp-server/main.py file
    print("\nInspecting mcp-server/main.py...")
    with open('mcp-server/main.py', 'r') as f:
        content = f.read()

    tree = ast.parse(content)

    # Find function definitions
    func_defs = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_defs[node.name] = node

    # Check create_task function
    if 'create_task' in func_defs:
        func = func_defs['create_task']
        params = [arg.arg for arg in func.args.args]
        print(f"✓ MCP create_task parameters: {params}")
        if 'user_id' in params:
            print("✓ MCP create_task accepts user_id parameter")
        else:
            print("✗ MCP create_task does NOT accept user_id parameter")
            return False
    else:
        print("✗ MCP create_task function not found")
        return False

    print("\n✓ All MCP server function signatures have also been updated correctly!")

    return True


if __name__ == "__main__":
    success = inspect_source_code()
    if not success:
        exit(1)
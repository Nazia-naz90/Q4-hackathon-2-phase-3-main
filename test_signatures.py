#!/usr/bin/env python3
"""
Simple test to verify that the function signatures have been updated correctly.
"""

import inspect
from mcp_server.test_agent_chat import TodoChatAgent


def test_function_signatures():
    """Test that the function signatures accept user_id parameter."""
    print("Testing function signatures...")

    agent = TodoChatAgent()

    # Check create_task method signature
    sig = inspect.signature(agent.create_task)
    params = list(sig.parameters.keys())
    print(f"create_task parameters: {params}")
    if 'user_id' in params:
        print("✓ create_task accepts user_id parameter")
    else:
        print("✗ create_task does NOT accept user_id parameter")
        return False

    # Check get_tasks method signature
    sig = inspect.signature(agent.get_tasks)
    params = list(sig.parameters.keys())
    print(f"get_tasks parameters: {params}")
    if 'user_id' in params:
        print("✓ get_tasks accepts user_id parameter")
    else:
        print("✗ get_tasks does NOT accept user_id parameter")
        return False

    # Check update_task method signature
    sig = inspect.signature(agent.update_task)
    params = list(sig.parameters.keys())
    print(f"update_task parameters: {params}")
    if 'user_id' in params:
        print("✓ update_task accepts user_id parameter")
    else:
        print("✗ update_task does NOT accept user_id parameter")
        return False

    # Check delete_task method signature
    sig = inspect.signature(agent.delete_task)
    params = list(sig.parameters.keys())
    print(f"delete_task parameters: {params}")
    if 'user_id' in params:
        print("✓ delete_task accepts user_id parameter")
    else:
        print("✗ delete_task does NOT accept user_id parameter")
        return False

    # Check toggle_task_completion method signature
    sig = inspect.signature(agent.toggle_task_completion)
    params = list(sig.parameters.keys())
    print(f"toggle_task_completion parameters: {params}")
    if 'user_id' in params:
        print("✓ toggle_task_completion accepts user_id parameter")
    else:
        print("✗ toggle_task_completion does NOT accept user_id parameter")
        return False

    print("\n✓ All function signatures have been updated correctly!")
    print("The original error 'TodoChatAgent.create_task() got an unexpected keyword argument 'user_id'' should now be fixed.")
    return True


if __name__ == "__main__":
    success = test_function_signatures()
    if not success:
        exit(1)
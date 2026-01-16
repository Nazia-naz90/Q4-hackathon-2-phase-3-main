#!/usr/bin/env python3
"""
Simple verification script to check that the updated prompts are in place.
"""

import os
import sys

# Read the system prompt directly from the file
def read_system_prompt():
    """Read the system prompt from the file without initializing the agent."""
    file_path = os.path.join(os.path.dirname(__file__), 'mcp-server', 'test_agent_chat.py')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the system prompt
    start_marker = 'self.system_prompt = """'
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("ERROR: Could not find system prompt in test_agent_chat.py")
        return None

    # Find the end by looking for the closing triple quotes
    start_idx = start_idx + len(start_marker)
    end_idx = content.find('"""', start_idx)

    if end_idx == -1:
        print("ERROR: Could not find end of system prompt")
        return None

    system_prompt = content[start_idx:end_idx]
    return system_prompt


def verify_updates():
    """Verify that the system prompt contains the updated content."""
    print("Verifying updated AI Todo Assistant prompts...")
    print("=" * 60)

    system_prompt = read_system_prompt()
    if not system_prompt:
        return False

    # Check for key improvements
    checks = [
        ("<UPDATE_RECOGNITION_RULES>", "Contains update recognition section"),
        ("Patterns indicating updates include:", "Has update pattern recognition"),
        ("Examples of update requests:", "Includes specific update examples"),
        ("UPDATE PRIORITY:", "Has priority rule for updates"),
        ("get_tasks to see the user's current tasks", "Mentions getting tasks before updates"),
        ("NEVER create a task that sounds like an update request", "Prohibits creating update-sounding tasks")
    ]

    all_passed = True
    for check, description in checks:
        if check in system_prompt:
            print(f"[OK] {description}")
        else:
            print(f"[MISSING] {description}")
            all_passed = False

    print("\nChecking for specific update recognition patterns...")
    update_patterns = [
        "update", "change", "modify", "adjust", "set", "make", "turn", "switch",
        "alter", "revise", "upgrade", "improve", "enhance"
    ]

    patterns_found = 0
    for pattern in update_patterns:
        if pattern in system_prompt:
            patterns_found += 1

    print(f"[OK] Found {patterns_found}/{len(update_patterns)} update recognition patterns")

    print("\nChecking for specific update examples...")
    example_checks = [
        "Update Client meeting to high priority",
        "Change the Client meeting task to high priority",
        "Modify Client meeting priority to high",
        "Set Client meeting priority to high"
    ]

    examples_found = 0
    for example in example_checks:
        if example in system_prompt:
            examples_found += 1

    print(f"[OK] Found {examples_found}/{len(example_checks)} specific update examples")

    print("\n" + "=" * 60)
    if all_passed and patterns_found >= 8 and examples_found >= 2:
        print("SUCCESS: All major improvements are present in the system prompt!")
        print("\nThe AI Todo Assistant should now properly:")
        print("- Recognize update requests like 'Update Client meeting to high priority'")
        print("- Call get_tasks first to identify existing tasks before updating")
        print("- Avoid creating tasks with update-sounding titles")
        print("- Handle update operations correctly instead of creating new tasks")
        return True
    else:
        print("FAILURE: Some updates are missing from the system prompt")
        return False


def compare_old_vs_new():
    """Show a comparison of the improvements made."""
    print("\nCOMPARISON OF IMPROVEMENTS:")
    print("=" * 40)
    print("BEFORE:")
    print("- Generic instruction: 'UPDATE/DELETE: Confirm the specific task before modifying.'")
    print("- No specific patterns for recognizing update requests")
    print("- No examples of how to identify update vs create requests")
    print("- AI could misinterpret 'Update X to Y' as a create request")

    print("\nAFTER:")
    print("- Dedicated <UPDATE_RECOGNITION_RULES> section")
    print("- Specific patterns: 'update', 'change', 'modify', 'adjust', 'set', etc.")
    print("- Specific phrases: 'to [value]', '[attribute] to [value]'")
    print("- Concrete examples: 'Update Client meeting to high priority'")
    print("- Instruction to call get_tasks first before updating")
    print("- Clear prohibition against creating update-sounding tasks")


if __name__ == "__main__":
    success = verify_updates()
    compare_old_vs_new()

    if success:
        print("\nPROMPTS SUCCESSFULLY UPDATED!")
        print("The AI Todo Assistant should now properly handle update requests.")
    else:
        print("\nSOME UPDATES ARE MISSING")
        print("Please check the implementation.")
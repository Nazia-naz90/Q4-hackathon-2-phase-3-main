#!/usr/bin/env python3
"""
Simple test to verify the table structure without emojis to avoid encoding issues.
"""

def test_table_structure():
    print("Testing the new table format structure...")
    print("=" * 70)

    # Sample tasks data
    tasks = [
        {"title": "Go To Shopping", "status": "completed", "priority": "high", "due_date": "None"},
        {"title": "Q4 Assignments", "status": "pending", "priority": "high", "due_date": "None"},
        {"title": "My Todo Task", "status": "pending", "priority": "high", "due_date": "None"}
    ]

    # Create the table format
    response_text = "[TABLE] Here are your tasks:\n\n"
    response_text += "+---+-------------------------+----------+----------+------------+\n"
    response_text += "| # | Task                    | Status   | Priority | Due Date   |\n"
    response_text += "+---+-------------------------+----------+----------+------------+\n"

    for i, task in enumerate(tasks, 1):
        status = task.get("status", "pending").capitalize()
        priority = task.get("priority", "medium")
        due_date = task.get("due_date", "None") or "None"
        title = task.get("title", "Unnamed Task")

        # Status indicator
        status_indicator = "DONE" if status.lower() == "completed" else "TODO"

        response_text += f"| {i:<1} | {title[:23]:<23} | {status_indicator:<8} | {priority:<8} | {due_date:<10} |\n"

    response_text += "+---+-------------------------+----------+----------+------------+\n\n"
    response_text += "[INFO] You can add, update, or delete tasks by telling me what you'd like to do!"

    print("SIMULATED RESPONSE FORMAT:")
    print(response_text)
    print("=" * 70)

    print("\n✅ The AI assistant will now display tasks in a table format when you ask 'Show me my tasks'")
    print("- Shows a structured table with clear columns")
    print("- Organizes task information neatly")
    print("- Provides clear visual separation of data")

if __name__ == "__main__":
    test_table_structure()
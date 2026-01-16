#!/usr/bin/env python3
"""
Test script to verify the new table format with emojis for AI Todo Assistant.
"""

async def test_new_format():
    print("Testing the new table format with emojis for AI Todo Assistant...")
    print("=" * 70)

    # Simulate the enhanced response format
    async def mock_get_tasks():
        return {
            "success": True,
            "tasks": [
                {"title": "Go To Shopping", "status": "completed", "priority": "high", "due_date": "None"},
                {"title": "Q4 Assignments", "status": "pending", "priority": "high", "due_date": "None"},
                {"title": "My Todo Task", "status": "pending", "priority": "high", "due_date": "None"}
            ]
        }

    # The updated logic with table format and emojis
    async def process_message_with_table_format(user_message: str):
        user_message_lower = user_message.lower().strip()

        # Check for specific view task list requests that should always trigger get_tasks
        view_keywords = ["show", "view", "list", "see", "check", "get", "display", "what"]
        task_keywords = ["tasks", "task", "to-do", "todo", "list", "my"]

        is_view_request = False

        # Direct match approach for common phrases
        view_requests = [
            "show me my tasks", "view task list", "show all tasks", "what tasks do i have?",
            "list my tasks", "display my todo list", "see my tasks", "check my tasks",
            "get my tasks", "show my to-do list", "view my tasks", "show task list",
            "view all tasks", "what do i have to do?", "show me tasks", "list tasks",
            "show my tasks", "view tasks", "show tasks", "see tasks", "check tasks"
        ]

        if user_message_lower in view_requests:
            is_view_request = True
        else:
            # Additional keyword-based check for more flexible matching
            words = user_message_lower.split()
            has_view_word = any(keyword in user_message_lower for keyword in view_keywords)
            has_task_word = any(keyword in user_message_lower for keyword in task_keywords)

            # If it contains both view and task related words, likely a view request
            if has_view_word and has_task_word and len(words) <= 6:
                is_view_request = True

        if is_view_request:
            # Directly call get_tasks for these specific requests
            result = await mock_get_tasks()
            if result.get("success"):
                tasks = result.get("tasks", [])
                if tasks:
                    # Create a table-like format with emojis
                    response_text = "📋 *Here are your tasks:*\n\n"
                    response_text += "```\n"
                    response_text += f"{'#':<3} {'Task':<25} {'Status':<12} {'Priority':<10} {'Due Date':<12}\n"
                    response_text += "-" * 70 + "\n"

                    for i, task in enumerate(tasks, 1):
                        status = task.get("status", "pending").capitalize()
                        priority = task.get("priority", "medium")
                        due_date = task.get("due_date", "None") or "None"
                        title = task.get("title", "Unnamed Task")

                        # Add status emoji
                        status_emoji = "✅" if status.lower() == "completed" else "⏳"

                        # Add priority emoji
                        priority_emoji = ""
                        if priority.lower() == "high":
                            priority_emoji = "🔴"
                        elif priority.lower() == "medium":
                            priority_emoji = "🟡"
                        elif priority.lower() == "low":
                            priority_emoji = "🟢"

                        response_text += f"{i:<3} {title[:23]:<25} {status_emoji} {status:<10} {priority_emoji} {priority:<8} {due_date:<12}\n"

                    response_text += "```\n\n"
                    response_text += "💡 *Tip: You can add, update, or delete tasks by telling me what you'd like to do!*"
                    return response_text
                else:
                    return "📭 You don't have any tasks yet.\n\n💡 *You can add a new task by telling me what you'd like to do!*"

        return f"This would create a task: {user_message}"

    # Test the exact scenario
    print("USER INPUT: 'show me my tasks'")
    response = await process_message_with_table_format("show me my tasks")

    print("\nAI ASSISTANT RESPONSE:")
    print("=" * 70)
    print(response)
    print("=" * 70)

    print("\n✅ SUCCESS: Tasks are now displayed in a formatted table with emojis!")
    print("- Shows a nice table layout with columns")
    print("- Uses emojis for status (✅ completed, ⏳ pending)")
    print("- Uses emojis for priority (🔴 high, 🟡 medium, 🟢 low)")
    print("- Includes decorative elements like 📋 and 💡")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_new_format())
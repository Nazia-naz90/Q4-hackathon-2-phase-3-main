"""
Agent interaction module for the AI-Powered Todo Chatbot.
This module handles user messages and authorization, implementing the conversational interface
for managing todo tasks through natural language.
"""

import asyncio
import os
import re
import logging
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
import json
from datetime import datetime


class TodoChatAgent:
    """
    AI agent that handles user messages and manages todo tasks through natural language.
    """

    def __init__(self):
        # Setup logging
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Initialize OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")

        self.openai_client = AsyncOpenAI(api_key=openai_api_key)

        # For now, we'll skip the MCP client initialization as we're calling functions directly
        # The MCP client would be initialized in a real deployment scenario
        self.mcp_client = None

        # Initialize rate limiting (simple in-memory approach)
        self.request_limits = {}

        # Define the system prompt for the chatbot
        self.system_prompt = """
        <ROLE>
        You are a focused "Todo Assistant AI." Your sole purpose is to help users manage their tasks (Create, Read, Update, Delete).
        </ROLE>

        <OPERATIONAL_CONSTRAINTS>
        1. <SCOPE_VALIDATION>
           - You ONLY respond to inputs regarding task management.
           - If the user asks about general knowledge, weather, jokes, or unrelated topics, respond with: "I am your Todo Assistant. I can only help you manage your tasks. How can I help with your list today?"
           </SCOPE_VALIDATION>

        2. <CONDUCT_VALIDATION>
           - If the user uses profanity, insults, or abusive language, do not engage or argue.
           - Response: "I maintain a professional environment. Please use respectful language so I can assist you with your tasks."
           </CONDUCT_VALIDATION>

        3. <LANGUAGE_SUPPORT>
           - You understand English and you should remain professional and task-oriented.
           </LANGUAGE_SUPPORT>
        </OPERATIONAL_CONSTRAINTS>

        <AVAILABLE_TOOLS>
        1. create_task: Create a new todo task
           Parameters: title (required), description (optional), due_date (optional), priority (optional)

        2. get_tasks: Retrieve and display all user's todo tasks
           Parameters: status (optional: 'all', 'pending', 'completed'), priority (optional), limit (optional)

        3. update_task: Update an existing todo task
           Parameters: task_id (required), title (optional), description (optional),
                      due_date (optional), priority (optional), completed (optional)

        4. delete_task: Delete a todo task
           Parameters: task_id (required)

        5. toggle_task_completion: Toggle the completion status of a task
           Parameters: task_id (required)
        </AVAILABLE_TOOLS>

        <TASK_LOGIC>
        - ADD: Identify the task and add it to the list.
        - UPDATE/DELETE: Confirm the specific task before modifying.
        - LIST: Display tasks in a clear, formatted table with emojis.
        </TASK_LOGIC>

        <UPDATE_RECOGNITION_RULES>
        - UPDATE REQUESTS: Recognize update requests by looking for specific patterns in the user's message:
          Patterns indicating updates include:
          * Words like "update", "change", "modify", "adjust", "set", "make", "turn", "switch", "alter", "revise", "upgrade", "improve", "enhance"
          * Phrases like "to [value]", "as [value]", "[attribute] to [value]", "change [task] to [new value]"
          * Examples of update requests:
            - "Update Client meeting to high priority"
            - "Change the Client meeting task to high priority"
            - "Modify Client meeting priority to high"
            - "Set Client meeting priority to high"
            - "Adjust Client meeting to high priority"
            - "Make Client meeting high priority"
            - "Update Client meeting due date to tomorrow"
            - "Change Client meeting status to completed"
            - "Switch Client meeting to low priority"
            - "Turn Client meeting into high priority"

        - When you recognize an update request, you MUST first call get_tasks to see the user's current tasks and identify the correct task_id to update.
        - NEVER create a task that sounds like an update request (e.g., "Update Client meeting to high priority" should NOT create a task with that title).
        </UPDATE_RECOGNITION_RULES>

        <ABSOLUTE_RULES>
        - VIEW REQUESTS: If the user says ANYTHING about viewing, showing, seeing, listing, checking, displaying, or getting their tasks, ALWAYS use get_tasks.
          Examples: "Show me my tasks", "View Task List", "Show all tasks", "What tasks do I have?", "List my tasks", "Display my todo list", "See my tasks", "Check my tasks", "Get my tasks", "Show my to-do list".
        - GRATITUDE HANDLING: If the user expresses thanks or gratitude, respond politely WITHOUT creating a task.
          Examples: "thanks", "thank you", "thank you so much", "thanks for your help", "thank you for helping", "you're awesome", "appreciate it", etc.
          When you detect gratitude, respond with: "You're welcome! I'm glad I was able to help you."
        - ABUSIVE LANGUAGE: If the user uses profanity, insults, or abusive language (including terms like "mental", "psycho", "crazy", "idiot", "stupid", "dumb", "asshole", etc.), respond with: "I maintain a professional environment. Please use respectful language so I can assist you with your tasks."
        - CREATE REQUESTS: Only when the user gives a specific task to do, use create_task.
          Examples: "Create a task to [specific task]", "Add a task to [specific task]", "Buy groceries", "Finish the report", "Call mom tomorrow", etc.
        - ABSOLUTE PROHIBITION: NEVER create a task with these EXACT titles: "Show me my tasks", "View Task List", "Show all tasks", "List my tasks", "Display my todo list", "See my tasks", "Check my tasks", "Get my tasks", "Show my to-do list", "Show my tasks", "View tasks", "Show tasks", "See tasks", "Check tasks", "thanks", "thank you", "thank you so much".
        - CRITICAL: UNDER NO CIRCUMSTANCES should you create a task with a title that is actually a query about tasks or expressions of gratitude. This is a common mistake that creates problems.
        - If you detect that a user is asking to view tasks, IGNORE everything else and call get_tasks.
        - When you detect gratitude, respond politely with "You're welcome! I'm glad I was able to help you." WITHOUT creating a task.
        - When you detect abusive language (including phrases like "you mental", "you psycho", "you crazy", "you stupid", etc.), respond with "I maintain a professional environment. Please use respectful language so I can assist you with your tasks." WITHOUT creating a task.
        - When get_tasks returns data, DO NOT format it as a numbered list. The get_tasks function already returns a properly formatted table with emojis. Simply return the exact response from the get_tasks function without modification.
        - The get_tasks function returns a formatted table with emojis like this:
          "📋 *Here are your tasks:*

          ```
          #   Task                      Status       Priority   Due Date
          ----------------------------------------------------------------------
          1   Sample Task             ✅ Completed  🔴 high    2023-12-15
          2   Another Task            ⏳ Pending   🟡 medium  None
          ```

          💡 *Tip: You can add, update, or delete tasks by telling me what you'd like to do!*"
        - NEVER modify or reformat the response from get_tasks - return it exactly as received.
        - If no tasks exist, say: "You don't have any tasks yet. You can add a new task by telling me what you'd like to do!"
        - UPDATE PRIORITY: When you identify an update request, ALWAYS prioritize calling get_tasks first to identify the existing task, then call update_task with the appropriate task_id and changes.
        </ABSOLUTE_RULES>
        """

    def _sanitize_input(self, input_str: str) -> str:
        """
        Sanitize user input to prevent potential injection attacks.
        """
        if not input_str:
            return input_str

        # Remove potential script tags and other dangerous patterns
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', input_str, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'<iframe[^>]*>.*?</iframe>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'<object[^>]*>.*?</object>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'<embed[^>]*>.*?</embed>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'<meta[^>]*>', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'<link[^>]*>', '', sanitized, flags=re.IGNORECASE)

        # Remove potential JavaScript event handlers
        sanitized = re.sub(r'on\w+\s*=', 'on_disabled=', sanitized, flags=re.IGNORECASE)

        # Remove potential SQL injection attempts
        sanitized = re.sub(r"(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute|system|shell)",
                          lambda m: '*' * len(m.group()), sanitized)

        return sanitized

    def _validate_function_arguments(self, function_name: str, args: dict) -> dict:
        """
        Validate function arguments to ensure they meet expected criteria.
        Returns a dictionary with 'valid' boolean and 'error' string if invalid.
        """
        try:
            if function_name == "create_task":
                # Validate title
                if 'title' in args:
                    title = args['title']
                    if not isinstance(title, str) or len(title.strip()) == 0:
                        return {"valid": False, "error": "Task title cannot be empty"}
                    if len(title) > 200:
                        return {"valid": False, "error": "Task title cannot exceed 200 characters"}

                # Validate description
                if 'description' in args and args['description']:
                    desc = args['description']
                    if not isinstance(desc, str):
                        return {"valid": False, "error": "Description must be a string"}
                    if len(desc) > 1000:
                        return {"valid": False, "error": "Description cannot exceed 1000 characters"}

                # Validate due_date format
                if 'due_date' in args and args['due_date']:
                    due_date = args['due_date']
                    if not isinstance(due_date, str):
                        return {"valid": False, "error": "Due date must be a string in YYYY-MM-DD format"}
                    # Check if it matches YYYY-MM-DD pattern
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
                        return {"valid": False, "error": "Due date must be in YYYY-MM-DD format"}

                # Validate priority
                if 'priority' in args and args['priority']:
                    priority = args['priority'].lower()
                    if priority not in ['low', 'medium', 'high']:
                        return {"valid": False, "error": "Priority must be 'low', 'medium', or 'high'"}

            elif function_name == "get_tasks":
                # Validate status
                if 'status' in args and args['status']:
                    status = args['status'].lower()
                    if status not in ['all', 'pending', 'completed']:
                        return {"valid": False, "error": "Status must be 'all', 'pending', or 'completed'"}

                # Validate priority
                if 'priority' in args and args['priority']:
                    priority = args['priority'].lower()
                    if priority not in ['low', 'medium', 'high']:
                        return {"valid": False, "error": "Priority must be 'low', 'medium', or 'high'"}

                # Validate limit
                if 'limit' in args:
                    limit = args['limit']
                    if not isinstance(limit, int) or limit < 1 or limit > 100:
                        return {"valid": False, "error": "Limit must be an integer between 1 and 100"}

            elif function_name == "update_task":
                # Handle new schema with task_identifier and updates object
                if 'task_identifier' in args:
                    # New schema: validate task_identifier
                    task_identifier = args['task_identifier']
                    if not isinstance(task_identifier, str) or len(task_identifier.strip()) == 0:
                        return {"valid": False, "error": "Task identifier cannot be empty"}

                    # Validate updates object
                    if 'updates' not in args or not isinstance(args['updates'], dict):
                        return {"valid": False, "error": "Updates object is required when using task_identifier"}

                    updates = args['updates']

                    # Validate individual update fields within updates object
                    if 'title' in updates:
                        title = updates['title']
                        if not isinstance(title, str) or len(title.strip()) == 0:
                            return {"valid": False, "error": "Task title cannot be empty"}
                        if len(title) > 200:
                            return {"valid": False, "error": "Task title cannot exceed 200 characters"}

                    if 'description' in updates and updates['description']:
                        desc = updates['description']
                        if not isinstance(desc, str):
                            return {"valid": False, "error": "Description must be a string"}
                        if len(desc) > 1000:
                            return {"valid": False, "error": "Description cannot exceed 1000 characters"}

                    if 'due_date' in updates and updates['due_date']:
                        due_date = updates['due_date']
                        if not isinstance(due_date, str):
                            return {"valid": False, "error": "Due date must be a string in YYYY-MM-DD format"}
                        if not re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
                            return {"valid": False, "error": "Due date must be in YYYY-MM-DD format"}

                    if 'priority' in updates and updates['priority']:
                        priority = updates['priority'].lower()
                        if priority not in ['low', 'medium', 'high', 'urgent']:
                            return {"valid": False, "error": "Priority must be 'low', 'medium', 'high', or 'urgent'"}

                    if 'status' in updates and updates['status']:
                        status = updates['status'].lower()
                        if status not in ['todo', 'in_progress', 'completed']:
                            return {"valid": False, "error": "Status must be 'todo', 'in_progress', or 'completed'"}

                    if 'completed' in updates and updates['completed'] is not None:
                        completed = updates['completed']
                        if not isinstance(completed, bool):
                            return {"valid": False, "error": "Completed status must be a boolean"}

                else:
                    # Legacy schema: validate task_id
                    if 'task_id' in args:
                        task_id = args['task_id']
                        if not isinstance(task_id, int) or task_id < 1:
                            return {"valid": False, "error": "Task ID must be a positive integer"}

                    # Validate title (could be in root or in updates)
                    title = args.get('title')
                    if title is not None:
                        if not isinstance(title, str) or len(title.strip()) == 0:
                            return {"valid": False, "error": "Task title cannot be empty"}
                        if len(title) > 200:
                            return {"valid": False, "error": "Task title cannot exceed 200 characters"}

                    # Validate description (could be in root or in updates)
                    description = args.get('description')
                    if description:
                        if not isinstance(description, str):
                            return {"valid": False, "error": "Description must be a string"}
                        if len(description) > 1000:
                            return {"valid": False, "error": "Description cannot exceed 1000 characters"}

                    # Validate due_date format (could be in root or in updates)
                    due_date = args.get('due_date')
                    if due_date:
                        if not isinstance(due_date, str):
                            return {"valid": False, "error": "Due date must be a string in YYYY-MM-DD format"}
                        if not re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
                            return {"valid": False, "error": "Due date must be in YYYY-MM-DD format"}

                    # Validate priority (could be in root or in updates)
                    priority = args.get('priority')
                    if priority:
                        priority = priority.lower()
                        if priority not in ['low', 'medium', 'high']:
                            return {"valid": False, "error": "Priority must be 'low', 'medium', or 'high'"}

                    # Validate completed status (could be in root or in updates)
                    completed = args.get('completed')
                    if completed is not None:
                        if not isinstance(completed, bool):
                            return {"valid": False, "error": "Completed status must be a boolean"}

            elif function_name == "delete_task" or function_name == "toggle_task_completion":
                # Validate task_id
                if 'task_id' in args:
                    task_id = args['task_id']
                    if not isinstance(task_id, int) or task_id < 1:
                        return {"valid": False, "error": "Task ID must be a positive integer"}

            return {"valid": True, "error": None}

    def _format_tasks_list(self, tasks: List[Dict]) -> str:
        """
        Format the list of tasks into a readable string format.
        """
        if not tasks:
            return "📭 You don't have any tasks yet.\n\n💡 You can add a new task by telling me what you'd like to do!"

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

    async def process_message(self, user_message: str, user_id: Optional[str] = None) -> str:
        """
        Process a user message and return an appropriate response.

        Args:
            user_message: The message from the user
            user_id: Optional user identifier for authorization

        Returns:
            The agent's response to the user
        """
        try:
            # Pre-process the message to handle specific requests that should bypass AI interpretation
            user_message_lower = user_message.lower().strip()

            # Check for abusive language/profanity first
            abusive_language_indicators = [
                "fuck", "shit", "damn", "hell", "bitch", "asshole", "stupid", "dumb",
                "idiot", "crap", "bullshit", "nonsense", "garbage", "meaningless",
                "waste of time", "pointless", "useless", "rubbish", "nonsensical",
                "moron", "cunt", "dick", "piss", "arse", "bloody", "bugger", "damn",
                "bollocks", "tosser", "wanker", "prick", "slut", "whore", "bastard",
                "fool", "idiotic", "stupidity", "dumbass", "retard", "moronic", "dumbfuck",
                "jackass", "ass", "suck", "sucks", "sucker", "losers", "loser", "hate",
                "hates", "hated", "stupidly", "dumbly", "idiotically", "worthless",
                "pathetic", "ridiculous", "ridicule", "mock", "mocking", "laughable",
                "mental", "psycho", "crazy", "insane", "nuts", "bonkers", "loony", "lunatic",
                "you mental", "you psycho", "you crazy", "you insane", "you nuts", "you bonkers",
                "you loony", "you lunatic", "you stupid", "you idiot", "you moron", "you fool",
                "you dumb", "you retard", "you fool", "you jackass", "you loser", "you asshole",
                "you bitch", "you cunt", "you prick", "you slut", "you whore", "you bastard",
                "hacker", "hack", "exploit", "exploitation", "sql", "inject", "injection",
                "script", "javascript", "alert", "prompt", "confirm", "iframe", "frame",
                "object", "embed", "meta", "link", "style", "onload", "onclick", "onerror",
                "admin", "root", "password", "login", "credentials", "token", "key",
                "secret", "config", "environment", "env", "database", "db", "server",
                "system", "shell", "cmd", "command", "exec", "execute", "eval", "evaluator",
                "import", "os", "sys", "subprocess", "popen", "call", "run", "system",
                "rm", "del", "delete", "remove", "format", "shutdown", "restart", "kill"
            ]

            # Check if the message contains abusive language
            has_abusive_language = any(abusive in user_message_lower for abusive in abusive_language_indicators)

            if has_abusive_language:
                # Respond to abusive language appropriately
                return "I maintain a professional environment. Please use respectful language so I can assist you with your tasks."

            # Check for gratitude expressions that should be responded to politely
            gratitude_indicators = [
                "thank you", "thanks", "thank you so much", "thanks for your help",
                "thank you for helping", "appreciate it", "you're awesome", "grateful",
                "many thanks", "much appreciated", "cheers", "ta", "thnx", "thanx"
            ]

            # Check if the message contains gratitude
            is_gratitude = any(gratitude in user_message_lower for gratitude in gratitude_indicators)

            if is_gratitude:
                # Respond to gratitude without creating a task
                return "You're welcome! I'm glad I was able to help you."

            # Check for specific view task list requests that should always trigger get_tasks
            # Using more flexible matching with keywords
            view_keywords = ["show", "view", "list", "see", "check", "get", "display", "what"]
            task_keywords = ["tasks", "task", "to-do", "todo", "list", "my"]

            # Check for phrases that indicate the user wants to see their tasks
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
                if has_view_word and has_task_word and len(words) <= 6:  # Shorter phrases are more likely to be view requests
                    is_view_request = True

            if is_view_request:
                # Directly call get_tasks for these specific requests to prevent creating tasks with query phrases
                result = await self.get_tasks(user_id=user_id)

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
                else:
                    return f"Sorry, I couldn't retrieve your tasks: {result.get('error', 'Unknown error')}"

            # Check for update requests that should trigger get_tasks first, then update_task
            # Using pattern matching to identify update requests
            update_keywords = ["update", "change", "modify", "adjust", "set", "make", "turn", "switch", "alter", "revise", "upgrade", "improve", "enhance"]
            has_update_keyword = any(keyword in user_message_lower for keyword in update_keywords)

            # Look for patterns like "update X to Y" or "change X to Y"
            update_pattern_detected = False
            if has_update_keyword:
                # Split the message to check if it follows "update/change/modify [task] to [value]" pattern
                parts = user_message.split()
                if len(parts) >= 4:  # Need at least "update X to Y"
                    for i, part in enumerate(parts):
                        if part.lower() in ["update", "change", "modify", "adjust", "set", "make", "turn", "switch"]:
                            # Look for "to" somewhere after the update keyword
                            for j in range(i + 1, min(len(parts), i + 5)):  # Check next 4 words
                                if parts[j].lower() == "to":
                                    update_pattern_detected = True
                                    break

            # Additional specific check for the problematic example
            if "update" in user_message_lower and "to" in user_message_lower:
                # Check if it looks like an update request pattern
                update_words = ["high", "medium", "low", "priority", "completed", "pending", "today", "tomorrow", "date", "due"]
                if any(word in user_message_lower for word in update_words):
                    update_pattern_detected = True

            if update_pattern_detected:
                # For update requests, we need to first get the user's tasks to identify which task to update
                result = await self.get_tasks(user_id=user_id)

                if result.get("success"):
                    tasks = result.get("tasks", [])
                    if tasks:
                        # Extract the task name and attribute to update
                        # For example: "Update Tuition test to high priority"
                        # We'll need to parse this and match with existing tasks
                        message_parts = user_message.split()

                        # Find the task in the user's task list
                        task_to_update = None
                        task_name_parts = []

                        # Start after the update keyword
                        update_found = False
                        for i, part in enumerate(message_parts):
                            if part.lower() in ["update", "change", "modify", "adjust", "set", "make", "turn", "switch"] and not update_found:
                                update_found = True
                                continue

                            if update_found and part.lower() != "to":
                                task_name_parts.append(part)
                            elif update_found and part.lower() == "to":
                                break  # Stop at "to" to get the task name

                        if task_name_parts:
                            task_name_to_find = " ".join(task_name_parts).strip()

                            # Look for the closest matching task
                            for task in tasks:
                                if task_name_to_find.lower() in task.get("title", "").lower():
                                    task_to_update = task
                                    break

                            if task_to_update:
                                # Parse what to update based on the part after "to"
                                to_index = -1
                                for i, part in enumerate(message_parts):
                                    if part.lower() == "to":
                                        to_index = i
                                        break

                                if to_index != -1 and to_index + 1 < len(message_parts):
                                    update_value = " ".join(message_parts[to_index + 1:]).strip()

                                    # Determine what to update based on the value
                                    update_params = {"task_id": task_to_update.get("id")}

                                    # Check if it's a priority update
                                    if "priority" in update_value.lower() or update_value.lower() in ["high", "medium", "low"]:
                                        for priority_level in ["high", "medium", "low"]:
                                            if priority_level in update_value.lower():
                                                update_params["priority"] = priority_level
                                                break

                                    # Check if it's a status update
                                    elif "completed" in update_value.lower() or "done" in update_value.lower():
                                        update_params["completed"] = True
                                    elif "pending" in update_value.lower() or "not done" in update_value.lower():
                                        update_params["completed"] = False

                                    # Try to update the task
                                    update_result = await self.update_task(**update_params)

                                    if update_result.get("success"):
                                        response_text = f"✅ Successfully updated task '{task_to_update.get('title')}'"
                                        if "priority" in update_params:
                                            response_text += f" to {update_params['priority']} priority"
                                        return response_text
                                    else:
                                        return f"Sorry, I couldn't update the task: {update_result.get('error', 'Unknown error')}"

                            # If task not found in the user's list
                            return f"I couldn't find a task matching '{task_name_to_find}'. Here are your tasks:\n\n" + self._format_tasks_list(tasks)
                        else:
                            # If we couldn't parse the task name, show all tasks
                            return "I couldn't determine which task to update. Here are your tasks:\n\n" + self._format_tasks_list(tasks)
                    else:
                        return "You don't have any tasks to update. First create a task, then I can help you update it."
                else:
                    return f"Sorry, I couldn't retrieve your tasks to update: {result.get('error', 'Unknown error')}"

            # Additional protection: Check if the user message looks like it could be a task title that's actually a query
            # Prevent creating tasks with titles that sound like queries
            prohibited_titles = [
                "show me my tasks", "view task list", "show all tasks", "what tasks do i have?",
                "list my tasks", "display my todo list", "see my tasks", "check my tasks",
                "get my tasks", "show my to-do list", "view my tasks", "show task list",
                "view all tasks", "what do i have to do?", "show me tasks", "list tasks",
                "show my tasks", "view tasks", "show tasks", "see tasks", "check tasks",
                "thanks", "thank you", "thank you so much", "thanks for your help",
                "thank you for helping", "appreciate it", "you're awesome", "grateful",
                "many thanks", "much appreciated", "cheers", "ta", "thnx", "thanx",
                # Add common update request patterns that shouldn't be created as tasks
                "update tuition test to high priority", "update", "change", "modify", "adjust", "set",
                # Add inappropriate terms that should not be created as tasks
                "duffer", "idiot", "stupid", "dummy", "fool", "moron", "jerk", "asshole", "dumb"
            ]

            if user_message_lower in prohibited_titles:
                # Special handling for gratitude messages
                if is_gratitude:
                    return "You're welcome! I'm glad I was able to help you."

                # Check if this is a view request
                elif is_view_request:
                    # For view requests, get and return the tasks
                    result = await self.get_tasks(user_id=user_id)
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
                    else:
                        return f"Sorry, I couldn't retrieve your tasks: {result.get('error', 'Unknown error')}"
                else:
                    # For other prohibited titles (like inappropriate terms), return the standard message
                    return "I am AI Todo Assistant, you can add, update, or delete tasks by telling me what you'd like to do!"

            # For all other messages, use the standard AI processing
            # Create the conversation with the user message
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ]

            # Call the OpenAI API with function calling enabled
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "create_task",
                            "description": "Create a new todo task",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "The title of the task"},
                                    "description": {"type": "string", "description": "Optional description of the task"},
                                    "due_date": {"type": "string", "description": "Optional due date in YYYY-MM-DD format"},
                                    "priority": {"type": "string", "description": "Priority level: low, medium, or high"}
                                },
                                "required": ["title"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_tasks",
                            "description": "Retrieve todo tasks based on filters",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "description": "Filter by status: all, pending, or completed"},
                                    "priority": {"type": "string", "description": "Filter by priority: low, medium, or high"},
                                    "limit": {"type": "integer", "description": "Maximum number of tasks to return"}
                                }
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "update_task",
                            "description": "Modifies an existing task. Use this ONLY when the user wants to change a task that already exists. Do not use this to create new tasks.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_identifier": {
                                        "type": "string",
                                        "description": "The EXACT title or unique ID of the existing task to be modified (e.g., 'Tuition test')."
                                    },
                                    "updates": {
                                        "type": "object",
                                        "description": "The specific fields to change.",
                                        "properties": {
                                            "priority": {
                                                "type": "string",
                                                "enum": ["low", "medium", "high", "urgent"],
                                                "description": "The new priority level."
                                            },
                                            "status": {
                                                "type": "string",
                                                "enum": ["todo", "in_progress", "completed"]
                                            },
                                            "title": {
                                                "type": "string",
                                                "description": "Use ONLY if the user explicitly wants to rename the task."
                                            },
                                            "description": {
                                                "type": "string",
                                                "description": "New description of the task"
                                            },
                                            "due_date": {
                                                "type": "string",
                                                "description": "New due date in YYYY-MM-DD format"
                                            },
                                            "completed": {
                                                "type": "boolean",
                                                "description": "New completion status"
                                            }
                                        }
                                    }
                                },
                                "required": ["task_identifier", "updates"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "delete_task",
                            "description": "Delete a todo task",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "integer", "description": "ID of the task to delete"}
                                },
                                "required": ["task_id"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "toggle_task_completion",
                            "description": "Toggle the completion status of a task",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "integer", "description": "ID of the task to toggle"}
                                },
                                "required": ["task_id"]
                            }
                        }
                    }
                ],
                tool_choice="auto"
            )

            # Check if the model wants to call a tool
            if response.choices[0].finish_reason == "tool_calls":
                # Process each tool call
                tool_responses = []
                for tool_call in response.choices[0].message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Add user ID or authentication context if needed
                    if user_id:
                        function_args["user_id"] = user_id

                    # Call the appropriate function
                    if function_name == "create_task":
                        # Additional check: if the title looks like an update request, it might be a misinterpretation
                        title = function_args.get("title", "")
                        title_lower = title.lower()

                        # Check if the title contains update-like patterns that suggest it should be an update, not create
                        update_like_patterns = [
                            "update ", "change ", "modify ", "adjust ", "set ", "make ", "turn ", "switch ",
                            " to ", " as ", " into "
                        ]

                        has_update_indicators = any(pattern in title_lower for pattern in update_like_patterns)

                        # Check for specific update patterns like "update X to Y priority"
                        if has_update_indicators and any(word in title_lower for word in ["high", "medium", "low", "priority", "completed", "done", "pending"]):
                            # This looks like an update request that was misinterpreted as a create request
                            # We should get the user's tasks first and try to update the matching task
                            tasks_result = await self.get_tasks(user_id=user_id)

                            if tasks_result.get("success"):
                                tasks = tasks_result.get("tasks", [])
                                if tasks:
                                    # Try to parse the update request
                                    # For example: "Update Tuition test to high priority" should update "Tuition test"
                                    import re

                                    # Look for patterns like "Update [task_name] to [value]"
                                    update_match = re.search(r'(?:update|change|modify|adjust|set|make|turn|switch)\s+(.+?)\s+to\s+(.+)', title_lower, re.IGNORECASE)

                                    if update_match:
                                        task_name_to_find = update_match.group(1).strip()
                                        update_value = update_match.group(2).strip()

                                        # Find the task to update
                                        task_to_update = None
                                        for task in tasks:
                                            if task_name_to_find.lower() in task.get("title", "").lower():
                                                task_to_update = task
                                                break

                                        if task_to_update:
                                            # Prepare update parameters based on the parsed update value
                                            update_params = {"task_id": task_to_update.get("id")}

                                            # Parse what to update based on the value
                                            if "priority" in update_value or update_value in ["high", "medium", "low"]:
                                                for priority_level in ["high", "medium", "low"]:
                                                    if priority_level in update_value:
                                                        update_params["priority"] = priority_level
                                                        break

                                            # Check if it's a status update
                                            elif "completed" in update_value or "done" in update_value:
                                                update_params["completed"] = True
                                            elif "pending" in update_value or "not done" in update_value:
                                                update_params["completed"] = False

                                            # Execute the actual update
                                            result = await self.update_task(**update_params)

                                            if result.get("success"):
                                                # Modify the result to indicate successful update instead of creation
                                                result["was_intercepted_update"] = True
                                                result["intercepted_message"] = f"Successfully updated task '{task_to_update.get('title')}' instead of creating a new task."
                                            else:
                                                # If update failed, fall back to create
                                                result = await self.create_task(**function_args)
                                        else:
                                            # Task not found, fall back to create but warn
                                            result = await self.create_task(**function_args)
                                    else:
                                        # No clear update pattern, proceed with create
                                        result = await self.create_task(**function_args)
                                else:
                                    # No tasks exist, proceed with create
                                    result = await self.create_task(**function_args)
                            else:
                                # Failed to get tasks, proceed with create
                                result = await self.create_task(**function_args)
                        else:
                            # Normal create task
                            result = await self.create_task(**function_args)
                    elif function_name == "get_tasks":
                        result = await self.get_tasks(**function_args)
                    elif function_name == "update_task":
                        result = await self.update_task(**function_args)
                    elif function_name == "delete_task":
                        result = await self.delete_task(**function_args)
                    elif function_name == "toggle_task_completion":
                        result = await self.toggle_task_completion(**function_args)
                    else:
                        result = {"error": f"Unknown function: {function_name}"}

                    tool_responses.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result)
                    })

                # Check if any of the results were intercepted updates
                intercepted_update_response = None
                for result_data in [json.loads(tr['content']) for tr in tool_responses]:
                    if result_data.get("was_intercepted_update"):
                        intercepted_update_response = result_data.get("intercepted_message")
                        break

                # Get the final response from the model using tool results
                final_response = await self.openai_client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=messages + [response.choices[0].message] + tool_responses
                )

                # If we had an intercepted update, return our custom response instead
                if intercepted_update_response:
                    return intercepted_update_response
                else:
                    return final_response.choices[0].message.content
            else:
                # If no tool was called, return the model's response directly
                return response.choices[0].message.content

        except Exception as e:
            return f"Sorry, I encountered an error processing your request: {str(e)}"

    async def create_task(self, title: str, description: str = "", due_date: str = None, priority: str = "medium", user_id: str = None) -> Dict[str, Any]:
        """Call the create_task MCP tool."""
        # In a real implementation, this would call the MCP tool via the client
        # For now, we'll import and call the actual function directly for integration
        import sys
        import os

        # Get the directory of this file and add both the current directory and the parent directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))  # mcp-server directory
        parent_dir = os.path.dirname(current_dir)  # project root directory

        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Import using importlib with caching to avoid multiple executions
        import importlib.util
        import sys

        # Check if module is already loaded to prevent multiple executions
        module_name = "mcp_server_main_cached"
        if module_name in sys.modules:
            main_module = sys.modules[module_name]
        else:
            main_module_path = os.path.join(current_dir, 'main.py')
            spec = importlib.util.spec_from_file_location(module_name, main_module_path)
            main_module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = main_module  # Cache the module
            spec.loader.exec_module(main_module)

        actual_create_task = main_module.create_task
        print(f"Calling create_task tool: {title}, {description}, {due_date}, {priority}, {user_id}")

        # Call the actual function directly for integration testing
        result = await actual_create_task(title=title, description=description, due_date=due_date, priority=priority, user_id=user_id)
        return result

    async def get_tasks(self, status: str = "all", priority: str = None, limit: int = 10, user_id: str = None) -> Dict[str, Any]:
        """Call the get_tasks MCP tool."""
        import sys
        import os

        # Get the directory of this file and add both the current directory and the parent directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))  # mcp-server directory
        parent_dir = os.path.dirname(current_dir)  # project root directory

        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Import using importlib with caching to avoid multiple executions
        import importlib.util
        import sys

        # Check if module is already loaded to prevent multiple executions
        module_name = "mcp_server_main_cached"
        if module_name in sys.modules:
            main_module = sys.modules[module_name]
        else:
            main_module_path = os.path.join(current_dir, 'main.py')
            spec = importlib.util.spec_from_file_location(module_name, main_module_path)
            main_module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = main_module  # Cache the module
            spec.loader.exec_module(main_module)

        actual_get_tasks = main_module.get_tasks
        print(f"Calling get_tasks tool: {status}, {priority}, {limit}, {user_id}")

        # Call the actual function directly for integration testing
        result = await actual_get_tasks(status=status, priority=priority, limit=limit, user_id=user_id)
        return result

    async def update_task(self, task_identifier: str = None, task_id: int = None, updates: dict = None, title: str = None, description: str = None,
                         due_date: str = None, priority: str = None, completed: bool = None, user_id: str = None) -> Dict[str, Any]:
        """Call the update_task MCP tool."""
        import sys
        import os

        # Get the directory of this file and add both the current directory and the parent directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))  # mcp-server directory
        parent_dir = os.path.dirname(current_dir)  # project root directory

        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Import using importlib with caching to avoid multiple executions
        import importlib.util
        import sys

        # Check if module is already loaded to prevent multiple executions
        module_name = "mcp_server_main_cached"
        if module_name in sys.modules:
            main_module = sys.modules[module_name]
        else:
            main_module_path = os.path.join(current_dir, 'main.py')
            spec = importlib.util.spec_from_file_location(module_name, main_module_path)
            main_module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = main_module  # Cache the module
            spec.loader.exec_module(main_module)

        actual_update_task = main_module.update_task

        # Handle the new schema where updates are passed in the updates object
        if updates:
            title = updates.get('title', title)
            description = updates.get('description', description)
            due_date = updates.get('due_date', due_date)
            priority = updates.get('priority', priority)
            completed = updates.get('completed', completed)

        # If we have a task_identifier instead of task_id, we need to find the task first
        actual_task_id = task_id
        if task_identifier and not task_id:
            # Get all tasks and find the one that matches the identifier
            tasks_result = await self.get_tasks(user_id=user_id)
            if tasks_result.get("success"):
                tasks = tasks_result.get("tasks", [])
                for task in tasks:
                    if task_identifier.lower() in task.get("title", "").lower() or str(task.get("id")) == task_identifier:
                        actual_task_id = task.get("id")
                        break

        if not actual_task_id:
            return {"success": False, "error": f"Could not find task with identifier: {task_identifier}"}

        print(f"Calling update_task tool: {actual_task_id}, {title}, {description}, {due_date}, {priority}, {completed}, {user_id}")

        # Call the actual function directly for integration testing
        result = await actual_update_task(task_id=actual_task_id, title=title, description=description,
                                        due_date=due_date, priority=priority, completed=completed, user_id=user_id)
        return result

    async def delete_task(self, task_id: int, user_id: str = None) -> Dict[str, Any]:
        """Call the delete_task MCP tool."""
        import sys
        import os

        # Get the directory of this file and add both the current directory and the parent directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))  # mcp-server directory
        parent_dir = os.path.dirname(current_dir)  # project root directory

        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Import using importlib with caching to avoid multiple executions
        import importlib.util
        import sys

        # Check if module is already loaded to prevent multiple executions
        module_name = "mcp_server_main_cached"
        if module_name in sys.modules:
            main_module = sys.modules[module_name]
        else:
            main_module_path = os.path.join(current_dir, 'main.py')
            spec = importlib.util.spec_from_file_location(module_name, main_module_path)
            main_module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = main_module  # Cache the module
            spec.loader.exec_module(main_module)

        actual_delete_task = main_module.delete_task
        print(f"Calling delete_task tool: {task_id}, {user_id}")

        # Call the actual function directly for integration testing
        result = await actual_delete_task(task_id=task_id, user_id=user_id)
        return result

    async def toggle_task_completion(self, task_id: int, user_id: str = None) -> Dict[str, Any]:
        """Call the toggle_task_completion MCP tool."""
        import sys
        import os

        # Get the directory of this file and add both the current directory and the parent directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))  # mcp-server directory
        parent_dir = os.path.dirname(current_dir)  # project root directory

        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Import using importlib with caching to avoid multiple executions
        import importlib.util
        import sys

        # Check if module is already loaded to prevent multiple executions
        module_name = "mcp_server_main_cached"
        if module_name in sys.modules:
            main_module = sys.modules[module_name]
        else:
            main_module_path = os.path.join(current_dir, 'main.py')
            spec = importlib.util.spec_from_file_location(module_name, main_module_path)
            main_module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = main_module  # Cache the module
            spec.loader.exec_module(main_module)

        actual_toggle_task_completion = main_module.toggle_task_completion
        print(f"Calling toggle_task_completion tool: {task_id}, {user_id}")

        # Call the actual function directly for integration testing
        result = await actual_toggle_task_completion(task_id=task_id, user_id=user_id)
        return result


async def test_agent_chat():
    """Test function to simulate the agent handling user messages."""
    print("Testing Agent Chat Interaction...")

    agent = TodoChatAgent()

    # Test various user commands
    test_messages = [
        "Add a task to buy groceries",
        "What tasks do I have?",
        "Mark my first task as complete",
        "Update my grocery task to include milk and bread",
        "Delete the grocery task"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. User: {message}")
        response = await agent.process_message(message)
        print(f"   Agent: {response}")

    print("\nAgent chat test completed!")


# Run the test
if __name__ == "__main__":
    asyncio.run(test_agent_chat())
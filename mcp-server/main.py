import asyncio
import json
import os
from typing import Dict, Any, List
from sqlmodel import Session, select
from backend.models import Task, TaskCreate, TaskUpdate
from backend.database import get_session, engine
from datetime import datetime
import uuid


def get_db_session():
    """Helper function to get database session"""
    return next(get_session())


# Flag to track if tables have already been created
_tables_created = False

def ensure_database_tables():
    """Ensure database tables are created (only once)"""
    global _tables_created
    if not _tables_created:
        try:
            from backend.database import create_db_and_tables
            create_db_and_tables()
            _tables_created = True
        except Exception as e:
            # If table is already defined, we can continue
            error_str = str(e).lower()
            if "already defined" in error_str or "extend_existing" in error_str or "table" in error_str and "already" in error_str:
                _tables_created = True
            else:
                raise e


# Define functions for Todo operations (without decorators to avoid MCP issues)
async def create_task(
    title: str,
    description: str = "",
    due_date: str = None,
    priority: str = "medium",
    user_id: str = None
) -> Dict[str, Any]:
    """
    Create a new todo task.

    Args:
        title: The title of the task
        description: Optional description of the task
        due_date: Optional due date in YYYY-MM-DD format
        priority: Priority level (low, medium, high) - defaults to medium
        user_id: Optional user ID to associate with the task

    Returns:
        Dict containing the created task details
    """
    try:
        # Ensure database tables exist
        ensure_database_tables()

        # Parse due date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                parsed_due_date = datetime.strptime(due_date, '%Y-%m-%d')

        # Create task data using the existing model
        task_data = TaskCreate(
            title=title,
            description=description,
            status="pending",  # Default to pending
            priority=priority,
            due_date=parsed_due_date
        )

        # Get database session and create the task
        with Session(engine) as db:
            # Use the provided user_id if available, otherwise generate a dummy one
            effective_user_id = user_id if user_id else str(uuid.uuid4())

            db_task = Task(
                user_id=effective_user_id,
                title=task_data.title,
                description=task_data.description,
                status=task_data.status,
                priority=task_data.priority,
                due_date=task_data.due_date
            )

            db.add(db_task)
            db.commit()
            db.refresh(db_task)

            return {
                "success": True,
                "task": {
                    "id": db_task.id,
                    "title": db_task.title,
                    "description": db_task.description,
                    "status": db_task.status,
                    "priority": db_task.priority,
                    "due_date": str(db_task.due_date) if db_task.due_date else None,
                    "created_at": str(db_task.created_at),
                    "user_id": db_task.user_id
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_tasks(
    status: str = "all",
    priority: str = None,
    limit: int = 10,
    user_id: str = None
) -> Dict[str, Any]:
    """
    Retrieve todo tasks based on filters.

    Args:
        status: Filter by status ('all', 'pending', 'completed') - defaults to 'all'
        priority: Filter by priority ('low', 'medium', 'high')
        limit: Maximum number of tasks to return - defaults to 10
        user_id: Optional user ID to filter tasks by user

    Returns:
        Dict containing list of tasks
    """
    try:
        # Ensure database tables exist
        ensure_database_tables()

        # Get database session and fetch tasks
        with Session(engine) as db:
            # Build query with filters
            query = select(Task)

            # Apply filters - filter by user_id if provided
            if user_id:
                query = query.where(Task.user_id == user_id)
            if status != "all":
                query = query.where(Task.status == status)
            if priority:
                query = query.where(Task.priority == priority)

            # Apply limit
            query = query.limit(limit)

            # Execute query
            tasks_result = db.exec(query).all()

            tasks = []
            for task in tasks_result:
                tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "due_date": str(task.due_date) if task.due_date else None,
                    "created_at": str(task.created_at),
                    "user_id": task.user_id
                })

            return {
                "success": True,
                "tasks": tasks,
                "count": len(tasks)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def update_task(
    task_id: str,
    title: str = None,
    description: str = None,
    due_date: str = None,
    priority: str = None,
    status: str = None,
    user_id: str = None
) -> Dict[str, Any]:
    """
    Update an existing todo task.

    Args:
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
        due_date: New due date (optional)
        priority: New priority (optional)
        status: New status (optional)
        user_id: Optional user ID to verify task ownership

    Returns:
        Dict containing the updated task details
    """
    try:
        # Ensure database tables exist
        ensure_database_tables()

        # Get database session
        with Session(engine) as db:
            # Get the existing task
            existing_task = db.get(Task, task_id)
            if not existing_task:
                return {
                    "success": False,
                    "error": f"Task with ID {task_id} not found"
                }

            # Verify user owns the task if user_id is provided
            if user_id and existing_task.user_id != user_id:
                return {
                    "success": False,
                    "error": f"Access denied: Task with ID {task_id} does not belong to user"
                }

            # Prepare update data
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if due_date is not None:
                try:
                    parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                except ValueError:
                    parsed_due_date = datetime.strptime(due_date, '%Y-%m-%d')
                update_data["due_date"] = parsed_due_date
            if priority is not None:
                update_data["priority"] = priority
            if status is not None:
                update_data["status"] = status

            # Update the task
            for field, value in update_data.items():
                setattr(existing_task, field, value)

            db.add(existing_task)
            db.commit()
            db.refresh(existing_task)

            return {
                "success": True,
                "task": {
                    "id": existing_task.id,
                    "title": existing_task.title,
                    "description": existing_task.description,
                    "status": existing_task.status,
                    "priority": existing_task.priority,
                    "due_date": str(existing_task.due_date) if existing_task.due_date else None,
                    "created_at": str(existing_task.created_at),
                    "user_id": existing_task.user_id
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def delete_task(task_id: str, user_id: str = None) -> Dict[str, Any]:
    """
    Delete a todo task.

    Args:
        task_id: ID of the task to delete
        user_id: Optional user ID to verify task ownership

    Returns:
        Dict containing success status
    """
    try:
        # Ensure database tables exist
        ensure_database_tables()

        # Get database session
        with Session(engine) as db:
            # Get the task to check if it exists
            task = db.get(Task, task_id)
            if not task:
                return {
                    "success": False,
                    "error": f"Task with ID {task_id} not found"
                }

            # Verify user owns the task if user_id is provided
            if user_id and task.user_id != user_id:
                return {
                    "success": False,
                    "error": f"Access denied: Task with ID {task_id} does not belong to user"
                }

            # Delete the task
            db.delete(task)
            db.commit()

            return {
                "success": True,
                "message": f"Task with ID {task_id} deleted successfully"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def toggle_task_completion(task_id: str, user_id: str = None) -> Dict[str, Any]:
    """
    Toggle the completion status of a todo task.

    Args:
        task_id: ID of the task to toggle
        user_id: Optional user ID to verify task ownership

    Returns:
        Dict containing the updated task details
    """
    try:
        # Ensure database tables exist
        ensure_database_tables()

        # Get database session
        with Session(engine) as db:
            # Get the existing task
            existing_task = db.get(Task, task_id)
            if not existing_task:
                return {
                    "success": False,
                    "error": f"Task with ID {task_id} not found"
                }

            # Verify user owns the task if user_id is provided
            if user_id and existing_task.user_id != user_id:
                return {
                    "success": False,
                    "error": f"Access denied: Task with ID {task_id} does not belong to user"
                }

            # Toggle the status between pending and completed
            new_status = "completed" if existing_task.status != "completed" else "pending"
            existing_task.status = new_status

            # Update completed_at timestamp if changing to completed
            if new_status == "completed" and existing_task.status != "completed":
                existing_task.completed_at = datetime.utcnow()
            elif new_status == "pending" and existing_task.status == "completed":
                existing_task.completed_at = None

            db.add(existing_task)
            db.commit()
            db.refresh(existing_task)

            return {
                "success": True,
                "task": {
                    "id": existing_task.id,
                    "title": existing_task.title,
                    "description": existing_task.description,
                    "status": existing_task.status,
                    "priority": existing_task.priority,
                    "due_date": str(existing_task.due_date) if existing_task.due_date else None,
                    "created_at": str(existing_task.created_at),
                    "user_id": existing_task.user_id
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# For MCP integration, we'll register the functions separately
def register_mcp_tools(server):
    """Register the functions as MCP tools with the server."""
    # Register each function as a tool
    server.tools.register(
        name="create_task",
        description="Create a new todo task",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The title of the task"},
                "description": {"type": "string", "description": "Optional description of the task"},
                "due_date": {"type": "string", "description": "Optional due date in YYYY-MM-DD format"},
                "priority": {"type": "string", "description": "Priority level (low, medium, high) - defaults to medium"},
                "user_id": {"type": "string", "description": "Optional user ID to associate with the task"}
            },
            "required": ["title"]
        }
    )(create_task)

    server.tools.register(
        name="get_tasks",
        description="Retrieve todo tasks based on filters",
        input_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Filter by status ('all', 'pending', 'completed') - defaults to 'all'"},
                "priority": {"type": "string", "description": "Filter by priority ('low', 'medium', 'high')"},
                "limit": {"type": "integer", "description": "Maximum number of tasks to return - defaults to 10"},
                "user_id": {"type": "string", "description": "Optional user ID to filter tasks by user"}
            }
        }
    )(get_tasks)

    server.tools.register(
        name="update_task",
        description="Update an existing todo task",
        input_schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "ID of the task to update"},
                "title": {"type": "string", "description": "New title (optional)"},
                "description": {"type": "string", "description": "New description (optional)"},
                "due_date": {"type": "string", "description": "New due date (optional)"},
                "priority": {"type": "string", "description": "New priority (optional)"},
                "status": {"type": "string", "description": "New status (optional)"},
                "user_id": {"type": "string", "description": "Optional user ID to verify task ownership"}
            },
            "required": ["task_id"]
        }
    )(update_task)

    server.tools.register(
        name="delete_task",
        description="Delete a todo task",
        input_schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "ID of the task to delete"},
                "user_id": {"type": "string", "description": "Optional user ID to verify task ownership"}
            },
            "required": ["task_id"]
        }
    )(delete_task)

    server.tools.register(
        name="toggle_task_completion",
        description="Toggle the completion status of a todo task",
        input_schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "ID of the task to toggle"},
                "user_id": {"type": "string", "description": "Optional user ID to verify task ownership"}
            },
            "required": ["task_id"]
        }
    )(toggle_task_completion)


async def main():
    """Main entry point for the MCP server."""
    from mcp.server import Server
    from mcp.server.stdio import stdio_server

    # Initialize the MCP server
    server = Server("todo-chatbot-agent")

    # Register tools with the server
    register_mcp_tools(server)

    # Start the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
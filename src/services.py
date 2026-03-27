from typing import Dict, List, Optional
from src.models import Task

# In-memory storage for tasks
_tasks: Dict[int, Task] = {}
_next_id: int = 1


def create_task(title: str, description: str) -> Task:
    """
    Creates a new task and saves it in memory.

    Args:
        title: The title of the task (must not be empty).
        description: The description of the task.

    Returns:
        The newly created Task object.

    Raises:
        ValueError: If the title is empty.
    """
    global _next_id

    if not title.strip():
        raise ValueError("Task title cannot be empty")

    task = Task(id=_next_id, title=title.strip(), description=description.strip())
    _tasks[task.id] = task
    _next_id += 1
    return task


def get_task_by_id(task_id: int) -> Optional[Task]:
    """
    Retrieves a single task by its ID.

    Args:
        task_id: The ID of the task to retrieve.

    Returns:
        The Task object if found, otherwise None.
    """
    return _tasks.get(task_id)


def get_all_tasks() -> List[Task]:
    """
    Retrieves all tasks.

    Returns:
        A list of all Task objects.
    """
    return list(_tasks.values())


def update_task(task_id: int, title: str, description: str) -> Optional[Task]:
    """
    Updates an existing task's title and description.

    Args:
        task_id: The ID of the task to update.
        title: The new title for the task.
        description: The new description for the task.

    Returns:
        The updated Task object if found, otherwise None.
    """
    task = get_task_by_id(task_id)
    if task:
        task.title = title.strip() if title.strip() else task.title
        task.description = description.strip() if description.strip() else task.description
        return task
    return None


def delete_task(task_id: int) -> bool:
    """
    Deletes a task by its ID.

    Args:
        task_id: The ID of the task to delete.

    Returns:
        True if the task was deleted, False otherwise.
    """
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def toggle_task_completion(task_id: int) -> Optional[Task]:
    """
    Toggles the 'completed' status of a task.

    Args:
        task_id: The ID of the task to toggle.

    Returns:
        The updated Task object if found, otherwise None.
    """
    task = get_task_by_id(task_id)
    if task:
        task.completed = not task.completed
        return task
    return None
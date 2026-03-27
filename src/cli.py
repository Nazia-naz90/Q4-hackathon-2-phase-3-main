from src import services


def _display_menu():
    """Prints the main menu options to the console."""
    print("\n--- To-Do List Menu ---")
    print("1. Add a new task")
    print("2. View all tasks")
    print("3. Update a task")
    print("4. Delete a task")
    print("5. Mark a task as complete")
    print("6. Exit")
    print("-----------------------")


def _handle_add_task():
    """Handles the UI flow for adding a new task."""
    print("\n--- Add a New Task ---")
    title = input("Enter task title: ")
    description = input("Enter task description: ")

    try:
        if title.strip():
            task = services.create_task(title, description)
            print(f"\n✅ Success: Task '{task.title}' (ID: {task.id}) was created.")
        else:
            print("\n❌ Error: Title cannot be empty.")
    except ValueError as e:
        print(f"\n❌ Error: {str(e)}")


def _handle_view_tasks():
    """Handles the UI flow for viewing all tasks."""
    print("\n--- All Tasks ---")
    tasks = services.get_all_tasks()
    if not tasks:
        print("No tasks yet. Why not add one?")
    else:
        for task in tasks:
            status = "✅ Done" if task.completed else "❌ Pending"
            print(f"[{status}] ID: {task.id} - {task.title}\n    Description: {task.description}\n")


def _handle_update_task():
    """Handles the UI flow for updating an existing task."""
    print("\n--- Update a Task ---")
    try:
        task_id = int(input("Enter the ID of the task to update: "))
        task = services.get_task_by_id(task_id)
        if not task:
            print("\n❌ Error: Task not found.")
            return

        print(f"Current title: {task.title}")
        new_title = input("Enter new title (or press Enter to keep current): ")

        print(f"Current description: {task.description}")
        new_description = input("Enter new description (or press Enter to keep current): ")

        # Only update if the user provided new input
        final_title = new_title if new_title.strip() else task.title
        final_description = new_description if new_description.strip() else task.description

        updated_task = services.update_task(task_id, final_title, final_description)
        if updated_task:
            print(f"\n✅ Success: Task {updated_task.id} was updated.")
        else:
            print("\n❌ Error: Failed to update task.")

    except ValueError:
        print("\n❌ Error: Invalid ID. Please enter a number.")


def _handle_delete_task():
    """Handles the UI flow for deleting a task."""
    print("\n--- Delete a Task ---")
    try:
        task_id = int(input("Enter the ID of the task to delete: "))
        if services.delete_task(task_id):
            print(f"\n✅ Success: Task {task_id} was deleted.")
        else:
            print("\n❌ Error: Task not found.")
    except ValueError:
        print("\n❌ Error: Invalid ID. Please enter a number.")


def _handle_toggle_completion():
    """Handles the UI flow for toggling a task's completion status."""
    print("\n--- Mark Task as Complete/Pending ---")
    try:
        task_id = int(input("Enter the ID of the task to toggle: "))
        task = services.toggle_task_completion(task_id)
        if task:
            status = "completed" if task.completed else "pending"
            print(f"\n✅ Success: Task {task.id} is now marked as {status}.")
        else:
            print("\n❌ Error: Task not found.")
    except ValueError:
        print("\n❌ Error: Invalid ID. Please enter a number.")


def main_loop():
    """The main entry point and loop for the CLI application."""
    while True:
        _display_menu()
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            _handle_add_task()
        elif choice == '2':
            _handle_view_tasks()
        elif choice == '3':
            _handle_update_task()
        elif choice == '4':
            _handle_delete_task()
        elif choice == '5':
            _handle_toggle_completion()
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("\n❌ Error: Invalid choice. Please enter a number between 1 and 6.")

        input("\nPress Enter to continue...")
# Todo Logic Specification - Phase 1

## Overview
This specification defines the core functionality for Phase 1 of the Todo CLI application. The primary goal is to establish the foundational logic for managing todo items with basic CRUD operations using in-memory storage.

## Scope
### In Scope
- Basic todo item creation with title and description
- Display of todo items in a list format
- Marking todo items as completed/incomplete
- Updating todo items (title and description)
- Deleting todo items
- Persistence of todo items (in-memory storage using dictionary)
- CLI menu interface with options for all operations
- Proper error handling and input validation
- Unique ID generation for each task

### Out of Scope
- User authentication and authorization
- Advanced filtering and search capabilities
- Due dates and reminders
- Priority levels
- Sub-tasks or nested todos
- Multi-user collaboration
- Offline synchronization
- Database persistence
- Web interface (command-line only for Phase 1)

## Functional Requirements

### 1. Todo Item Creation
- Users should be able to add a new todo item with a title
- Optionally, users can add a description
- Each todo item should have a unique identifier (auto-generated)
- New todos should be assigned an ID sequentially
- Empty titles should not be allowed
- After creation, show success message with task details

### 2. Todo Item Display
- Display all todos in a list format with ID, title, description, and completion status
- Show completion status as "✅ Done" or "❌ Pending"
- Show all task details when viewing
- If no tasks exist, show appropriate message

### 3. Todo Item Status Management
- Toggle completion status of a specific task by ID
- After toggling, show confirmation of new status
- Validate that the task exists before toggling

### 4. Todo Item Update
- Update existing todo's title and description by ID
- Allow partial updates (keep existing values if not provided)
- Validate that the task exists before updating
- Show confirmation after update

### 5. Todo Item Deletion
- Delete individual todo items by ID
- Validate that the task exists before deletion
- Show confirmation after deletion
- Handle invalid ID input gracefully

### 6. CLI Menu Interface
- Main menu with options: Add, View, Update, Delete, Toggle Completion, Exit
- Clear prompts for user input
- Input validation for numeric IDs
- Error messages for invalid inputs
- Loop back to menu after each operation

## Data Model

### Task Object
- id: int (unique identifier, auto-generated)
- title: str (required, non-empty)
- description: str (optional, can be empty)
- completed: bool (default False)

### Storage
- Use in-memory dictionary `_tasks: Dict[int, Task]` for storage
- Use global `_next_id: int` for auto-incrementing ID generation

## Non-Functional Requirements

### Performance
- Operations should be instantaneous (in-memory storage)
- CLI interface should respond within 100ms
- Menu navigation should be smooth

### Usability
- Clear menu options with numbered choices
- Intuitive prompts for user input
- Helpful error messages for invalid inputs
- Consistent formatting of task display

### Reliability
- Data persists during the session in memory
- No data loss during normal operations
- Proper error handling for invalid inputs
- Input validation to prevent empty titles

### Error Handling
- Handle invalid numeric inputs gracefully
- Show appropriate error messages when task not found
- Prevent creation of tasks with empty titles
- Handle all edge cases with proper user feedback

## User Stories

### As a user, I want to:
1. Add a new todo item so that I can track tasks I need to complete
2. View all my todos so that I can see what I need to do
3. Mark todos as complete so that I can keep track of what I've done
4. Update my todos so that I can modify their details
5. Delete todos that are no longer relevant
6. Use a simple menu interface so that I can navigate the application easily

## Acceptance Criteria

### For Todo Creation:
- [ ] Form exists to add new todo items via CLI
- [ ] New todos are assigned unique sequential IDs
- [ ] Empty todo titles are not allowed (validation required)
- [ ] Success message shows task details after creation
- [ ] Task appears in the list when viewing all tasks

### For Todo Display:
- [ ] All todos are displayed in a list with ID, title, description and status
- [ ] Each todo shows its completion status clearly
- [ ] Appropriate message displays when no tasks exist
- [ ] Format is consistent and readable

### For Todo Status:
- [ ] Can toggle completion status by entering task ID
- [ ] Confirmation message shows new status after toggle
- [ ] System validates task exists before toggling
- [ ] Updated status reflects in subsequent displays

### For Todo Update:
- [ ] Can update title and description by entering task ID
- [ ] System allows partial updates (keep existing values)
- [ ] Confirmation message shows update success
- [ ] System validates task exists before updating

### For Todo Deletion:
- [ ] Can delete individual todos by entering task ID
- [ ] Confirmation message shows deletion success
- [ ] System validates task exists before deletion
- [ ] Deleted task no longer appears in list

### For CLI Interface:
- [ ] Main menu displays all available options
- [ ] Menu options are numbered 1-6 for easy selection
- [ ] Invalid menu choices are handled gracefully
- [ ] Invalid numeric inputs are handled with error messages
- [ ] Application loops back to menu after each operation
- [ ] Exit option properly terminates the application

## Technical Implementation Requirements

### Code Structure
- Use Python 3.13+ standards
- Implement with proper type hints (e.g., `Dict[int, Task]`, `List[Task]`, `Optional[Task]`)
- Separate concerns: CLI interface, business logic, and data models in different modules
- Use dataclasses for the Task model
- Implement proper error handling with try/catch blocks

### Modules Required
1. `src/models.py` - Contains the Task dataclass
2. `src/services.py` - Contains all business logic functions
3. `src/cli.py` - Contains CLI interface and menu logic
4. `main.py` - Entry point that calls the CLI main loop

### Functions Required in Services Layer
- `create_task(title: str, description: str) -> Task` - Creates a new task
- `get_task_by_id(task_id: int) -> Optional[Task]` - Retrieves a specific task
- `get_all_tasks() -> List[Task]` - Retrieves all tasks
- `update_task(task_id: int, title: str, description: str) -> Optional[Task]` - Updates a task
- `delete_task(task_id: int) -> bool` - Deletes a task
- `toggle_task_completion(task_id: int) -> Optional[Task]` - Toggles completion status

### Error Handling Requirements
- Validate numeric inputs for task IDs
- Handle cases where tasks don't exist
- Prevent creation of tasks with empty titles
- Provide clear error messages to users

## Future Considerations
- Database integration for persistence
- User authentication system
- Advanced features like due dates, categories, and sharing
- Web interface in addition to CLI
- API endpoints for mobile applications
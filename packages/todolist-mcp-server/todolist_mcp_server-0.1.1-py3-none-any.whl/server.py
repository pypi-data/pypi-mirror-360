import logging
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from typing_extensions import TypedDict

# Type definitions
TodoStatus = Literal["pending", "in_progress", "completed"]
TodoPriority = Literal["high", "medium", "low"]


class TodoItem(TypedDict):
    content: str
    id: str
    priority: TodoPriority
    status: TodoStatus


# Setup logging
logger = logging.getLogger(__name__)

# TodoList data storage - using in-memory storage
_todos: list[dict[str, Any]] = []


def load_todos() -> list[dict[str, Any]]:
    """Load todos from memory"""
    return _todos.copy()


def validate_todo(todo: dict[str, Any]) -> None:
    """Validate a single todo item"""
    required_fields = ["content", "id", "priority", "status"]
    for field in required_fields:
        if field not in todo:
            raise ValueError(f"Missing required field: {field}")

    if not todo["content"].strip():
        raise ValueError("Content cannot be empty")

    if todo["priority"] not in ["high", "medium", "low"]:
        raise ValueError(f"Invalid priority: {todo['priority']}")

    if todo["status"] not in ["pending", "in_progress", "completed"]:
        raise ValueError(f"Invalid status: {todo['status']}")


def validate_todos(todos: list[dict[str, Any]]) -> None:
    """Validate all todos and check for duplicate IDs"""
    ids = set()
    for todo in todos:
        validate_todo(todo)
        if todo["id"] in ids:
            raise ValueError(f"Duplicate ID: {todo['id']}")
        ids.add(todo["id"])


def save_todos(todos: list[dict[str, Any]]) -> None:
    """Save todos to memory and auto-clear if all completed"""
    global _todos
    _todos = todos.copy()  # Keep as dict for now, validation ensures correct structure
    logger.info(f"Saved {len(_todos)} todos")

    # Check if all tasks are completed, if so clear the list
    if _todos and all(todo["status"] == "completed" for todo in _todos):
        _todos.clear()
        logger.info("Auto-cleared completed todos")


# Create FastMCP server
app = FastMCP("TodoList Server")


@app.tool()
def todo_read() -> list[dict[str, Any]]:
    """Use this tool to read the current to-do list for the session. This tool should be used proactively and frequently to ensure that you are aware of
    the status of the current task list. You should make use of this tool as often as possible, especially in the following situations:
    - At the beginning of conversations to see what's pending
    - Before starting new tasks to prioritize work
    - When the user asks about previous tasks or plans
    - Whenever you're uncertain about what to do next
    - After completing tasks to update your understanding of remaining work
    - After every few messages to ensure you're on track

    Usage:
    - This tool takes in no parameters. So leave the input blank or empty. DO NOT include a dummy object, placeholder string or a key like "input" or "empty". LEAVE IT BLANK.
    - Returns a list of todo items with their status, priority, and content
    - Use this information to track progress and plan next steps
    - If no todos exist yet, an empty list will be returned"""
    return load_todos()


@app.tool()
def todo_write(todos: list[dict[str, Any]]) -> str:
    """Use this tool to create and manage a structured task list for your current coding session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user.
    It also helps the user understand the progress of the task and overall progress of their requests.

    ## When to Use This Tool
    Use this tool proactively in these scenarios:

    1. Complex multi-step tasks - When a task requires 3 or more distinct steps or actions
    2. Non-trivial and complex tasks - Tasks that require careful planning or multiple operations
    3. User explicitly requests todo list - When the user directly asks you to use the todo list
    4. User provides multiple tasks - When users provide a list of things to be done (numbered or comma-separated)
    5. After receiving new instructions - Immediately capture user requirements as todos
    6. When you start working on a task - Mark it as in_progress BEFORE beginning work. Ideally you should only have one todo as in_progress at a time
    7. After completing a task - Mark it as completed and add any new follow-up tasks discovered during implementation

    ## When NOT to Use This Tool

    Skip using this tool when:
    1. There is only a single, straightforward task
    2. The task is trivial and tracking it provides no organizational benefit
    3. The task can be completed in less than 3 trivial steps
    4. The task is purely conversational or informational

    NOTE that you should not use this tool if there is only one trivial task to do. In this case you are better off just doing the task directly.

    ## Task States and Management

    1. **Task States**: Use these states to track progress:
       - pending: Task not yet started
       - in_progress: Currently working on (limit to ONE task at a time)
       - completed: Task finished successfully

    2. **Task Management**:
       - Update task status in real-time as you work
       - Mark tasks complete IMMEDIATELY after finishing (don't batch completions)
       - Only have ONE task in_progress at any time
       - Complete current tasks before starting new ones
       - Remove tasks that are no longer relevant from the list entirely

    3. **Task Completion Requirements**:
       - ONLY mark a task as completed when you have FULLY accomplished it
       - If you encounter errors, blockers, or cannot finish, keep the task as in_progress
       - When blocked, create a new task describing what needs to be resolved
       - Never mark a task as completed if:
         - Tests are failing
         - Implementation is partial
         - You encountered unresolved errors
         - You couldn't find necessary files or dependencies

    4. **Task Breakdown**:
       - Create specific, actionable items
       - Break complex tasks into smaller, manageable steps
       - Use clear, descriptive task names

    When in doubt, use this tool. Being proactive with task management demonstrates attentiveness and ensures you complete all requirements successfully.

    Args:
        todos: The updated todo list. Each todo item must contain:
            - content: Task description (string, minimum 1 character)
            - id: Unique task identifier (string)
            - priority: Priority level ("high", "medium", "low")
            - status: Task status ("pending", "in_progress", "completed")

    Returns:
        Success message or auto-clear notification if all tasks completed"""
    try:
        validate_todos(todos)
        save_todos(todos)

        # Check if the list was cleared
        if not _todos:
            return "All tasks completed! Todo list has been automatically cleared."

        return "Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable"
    except ValueError as e:
        return f"Validation error: {e!s}"


def main():
    """Main entry point for the MCP server"""
    app.run()


if __name__ == "__main__":
    main()

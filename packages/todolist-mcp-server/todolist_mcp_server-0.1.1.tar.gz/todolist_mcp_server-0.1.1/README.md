# TodoList MCP Server

A Model Context Protocol (MCP) server for managing todo lists with intelligent task tracking and auto-clear functionality.

## Features

- **In-memory todo storage** with session-based persistence
- **Intelligent auto-clear** - automatically clears completed tasks
- **Task validation** with duplicate ID prevention
- **Priority levels** (high, medium, low) and status tracking
- **MCP-compliant** tools for seamless integration

## Installation

### Requirements
- Python 3.12+
- Poetry (recommended) or pip

### Setup
```bash
# Clone the repository
git clone https://github.com/hicaosen/todolist.git
cd todolist

# Install dependencies
poetry install
# or with pip
pip install -e .
```

## Usage

### Running the Server
```bash
# Using the installed script
todolist-mcp-server

# Or directly with Python
python -m src.server
```

### MCP Tools

The server provides two main tools:

#### `todo_read`
Returns the current todo list. Use frequently to track progress.

```python
# No parameters required
todos = todo_read()
```

#### `todo_write`
Creates and manages todo items. Use for complex multi-step tasks.

```python
todos = [
    {
        "id": "task-1",
        "content": "Implement user authentication",
        "priority": "high",
        "status": "pending"
    },
    {
        "id": "task-2", 
        "content": "Write unit tests",
        "priority": "medium",
        "status": "in_progress"
    }
]
todo_write(todos)
```

### Todo Item Structure

Each todo item must contain:
- `id`: Unique string identifier
- `content`: Task description (non-empty string)
- `priority`: One of "high", "medium", "low"
- `status`: One of "pending", "in_progress", "completed"

### Auto-Clear Behavior

When all todos reach "completed" status, the list automatically clears to maintain a clean workspace.

## Development

### Code Quality Tools
```bash
# Lint code
ruff check

# Format code
ruff format

# Type checking
pyright
```

### Project Structure
```
todolist/
├── src/
│   ├── __init__.py
│   └── server.py          # Main MCP server implementation
├── pyproject.toml         # Project configuration
├── poetry.lock           # Dependency lock file
└── README.md
```

## Configuration

The server uses the following configuration:
- **Line length**: 88 characters
- **Python version**: 3.12+
- **Code style**: Ruff with comprehensive rule set
- **Type checking**: Pyright with strict mode

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.
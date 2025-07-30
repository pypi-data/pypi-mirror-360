# TodoList MCP Server

A Model Context Protocol (MCP) server for managing todo lists with stdio communication.

## Features

- **TodoRead**: Read all todos from the todo list (no parameters required)
- **TodoWrite**: Write/update todos to the todo list
- **In-Memory Storage**: Data stored in memory with auto-clear feature
- **Task Management**: Support for priorities and status tracking
- **Auto-Clear Feature**: Automatically clears completed tasks when all todos are done
- **Stdio Communication**: Compatible with MCP clients via stdio

## Installation

### From Source
```bash
git clone <repository-url>
cd todolist
pip install -e .
```

### Via uvx (Recommended)
```bash
uvx todolist-mcp-server
```

## Usage

### As MCP Server
```bash
todolist-mcp-server
```

### With Claude Desktop
Add to your Claude Desktop MCP configuration:

**If installed locally:**
```json
{
  "mcpServers": {
    "todolist": {
      "command": "todolist-mcp-server",
      "args": []
    }
  }
}
```

**If using uvx (recommended):**
```json
{
  "mcpServers": {
    "todolist": {
      "command": "uvx",
      "args": ["todolist-mcp-server"]
    }
  }
}
```

## Tools

### TodoRead
- **Description**: Read all todos from the todo list
- **Parameters**: None (leave empty)
- **Returns**: List of todo items with their status, priority, and content

### TodoWrite
- **Description**: Write/update todos to the todo list
- **Parameters**: 
  - `todos`: Array of todo items
- **Returns**: Success message

## Todo Item Structure

Each todo item must contain:
- `content`: Task description (string)
- `id`: Unique task identifier (string)
- `priority`: Priority level ("high", "medium", "low")
- `status`: Task status ("pending", "in_progress", "completed")

### Example Todo Item
```json
{
  "content": "Complete MCP server development",
  "id": "1",
  "priority": "high",
  "status": "completed"
}
```

## Development

### Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (using poetry or pip)
# Poetry method:
pip install poetry
poetry install

# Or use pip directly:
pip install -e .
```

### Testing
```bash
# Run the server
todolist-mcp-server

# Test with MCP client or Claude Desktop
```

## Data Storage

Todo items are stored in memory during the MCP server session. When all tasks are marked as completed, the todo list is automatically cleared. This design ensures a clean workspace for new task cycles.
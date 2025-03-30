# Kanban Board Application

A simple, locally-hosted Kanban board application for personal task management, with Cursor MCP integration.

## Features

- **Project Management**: Create, view, edit, and delete projects
- **Ticket Management**: Create and manage tickets with types (bug, story, spike)
- **Kanban Board View**: Visual board with drag-and-drop functionality
- **MCP Integration**: Integrate with Cursor for automatic ticket creation and updates
- **DORA Metrics**: Track development performance metrics

## Technology Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, JavaScript, and Tailwind CSS
- **Database**: SQLite (local)

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd kanban
   ```

2. Create a virtual environment and activate it:
   ```
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows, use: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install flask_migrate httpx fastmcp
   ```

4. Initialize the database:
   ```
   flask init-db
   ```

5. Run the application (two components need to be started):
   
   In one terminal:
   ```
   FLASK_APP=run.py FLASK_DEBUG=1 flask run --port 5050
   ```
   
   In another terminal:
   ```
   python kanban_mcp_server.py
   ```
   
   Alternatively, start both components at once:
   ```
   python start.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5050
   ```

## Python Version Compatibility

This application has been tested with Python 3.13.2. If you're using conda for Python management, ensure you activate the appropriate environment in your `.zshrc` file, but create a separate venv for this application to avoid dependency conflicts.

## Cursor MCP Integration

To integrate with Cursor's MCP:

1. Open the Kanban board application
2. Navigate to Settings
3. Configure the MCP server settings
4. In Cursor, add the MCP server with your local application URL

## Testing

Run the test suite:

```
pytest
```

For end-to-end tests:

```
pytest tests/e2e
```

## Project Structure

```
kanban/
├── app/
│   ├── models/         # Database models
│   ├── controllers/    # Route controllers
│   ├── services/       # Business logic
│   ├── templates/      # HTML templates
│   └── static/         # Static assets (CSS/JS)
├── tests/              # Test suite
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## License

MIT 
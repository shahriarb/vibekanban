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
   python -m venv venv
   source venv/bin/activate   # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   flask init-db
   ```

5. Run the application:
   ```
   flask run
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

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
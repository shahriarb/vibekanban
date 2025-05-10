# VibeKanban 🚦🤖

**Bring clarity to your agent-powered coding!**

Welcome to VibeKanban — a simple, modern Kanban board that's not just for you, but for your AI agents too! 

✨ **Track your work. Give your agent context. See what's happening, every step of the way.**

---

## Why VibeKanban? 🤔

Ever wondered what your agent is actually doing when you ask it to fix a bug or build a feature? VibeKanban bridges the gap between human workflow and agent automation:

- 📝 **Visual Kanban Board** — Organize your projects and tickets with a clean, drag-and-drop interface.
- 🤖 **Agent Integration (MCP Server)** — Let your AI agent create, update, and follow tickets, just like a real teammate.
- 📊 **Metrics & Insights** — Track deployment rates, bug frequency, and more to see how you (and your agent) are vibing.
- ⚡ **Instant Setup** — One script and you're ready to go!

---

## Features

- **Project Management**: Create, view, edit, and delete projects
- **Ticket Management**: Create and manage tickets with types (bug, story, task, spike) and priorities (low, medium, high, critical)
- **Kanban Board View**: Visual board with drag-and-drop functionality
- **MCP Integration**: Integrate with Cursor for automatic ticket creation and updates
- **DORA Metrics**: Track development performance metrics

## Technology Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, JavaScript, and Tailwind CSS
- **Database**: SQLite (local)

## Quick Setup (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/shahriarb/vibekanban.git
   cd vibekanban
   ```

2. Run the setup script:
   ```
   ./setup.sh
   ```
   This script will create a virtual environment, install dependencies, and set up the database.

3. Start the application:
   ```
   ./run.sh
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5050
   ```

## Manual Setup

If you prefer to set up manually or are experiencing issues with the scripts:

1. Clone the repository:
   ```
   git clone https://github.com/shahriarb/vibekanban.git
   cd vibekanban
   ```

2. Create a virtual environment and activate it:
   ```
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows, use: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database and migrations:

   If this is your first time setting up the project, run:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
   This will create the database tables based on the current models.

   If you already have a `migrations/` folder, you only need to run:
   ```
   flask db upgrade
   ```

5. Run the application manually:
   ```
   python run.py
   ```

## Python Version Compatibility

This application has been tested with Python 3.13.2. If you're using conda for Python management, ensure you activate the appropriate environment in your `.zshrc` file, but create a separate venv for this application to avoid dependency conflicts.

## Cursor MCP Integration

To integrate with Cursor's MCP:

1. Make sure the application is running
2. In Cursor, go to Cursor Settings > MCP Servers > Add New Global MCP server


In Cursor MCP settings:
- Name: KanbanBoard
- Type: Command 
- Command: /full/path/to/.venv/bin/python /full/path/to/kanban_mcp_server.py


### Using the KanbanBoard MCP

Once configured, you can use commands like:
- `@KanbanBoard get kanban status` - View ticket counts by state
- `@KanbanBoard list projects` - List all projects
- `@KanbanBoard list tickets` - List all tickets
- `@KanbanBoard create ticket` - Create a new ticket with specified type and priority
- `@KanbanBoard update ticket state` - Update a ticket's state
- `@KanbanBoard add comment` - Add a comment to a ticket

### Example Rules to use the MCP server in Cursor


```
You are an AI assistant specialized in software development design and architecture.

Note: Please use @KanbanBoard MCP to document your work in each step. The project_id is <ADD_PROJECT_NUMBER>.
That's a crucial part of the process.

For each feature or improvment request:
- Evaluate the request's complexity to determine if it should be a single ticket or broken into multiple tickets.

- Break Down Subtasks: Identify subtasks for frontend, backend, database, and testing and create them in the @KanbanBoard

- Determine Dependencies: Establish any task dependencies upfront and document them in the @KanbanBoard

- Define Acceptance Criteria: Set clear criteria for each task and document in the @KanbanBoard

- Tailor Testing Methods: For each subtask, define appropriate testing methods. For example, backend tasks might include API tests with tools like Postman or CURL, while frontend tasks might require unit tests with frameworks like Jest. Document the Test Steps in the @KanbanBoard.

- Ticket Flexibility: Allow flexibility to adjust the number of tickets based on ongoing discoveries during development.

- Prioritization: After all tasks defined follow these rules to set the priority for each task:
     - Assess urgency and impact to prioritize critical bugs and high-impact features.
    - Address tasks with dependencies first to unblock other work.
    - Prioritize tasks delivering significant business value.
    - Balance effort and complexity for practical progress.
Set the priority in the @KanbanBoard

- Development: Follow defined acceptance criteria for each task.
    Conduct task-specific testing (unit, integration, end-to-end).

- Ticket Flexibility: Remain flexible to add tasks during development if required.

For each Bug report:
- Create a ticket with the type of 'bug' and add the information I shared with you in the @KanbanBoard. Set clear criteria about what should be fixed and set the priority as high or critical based on the bug's impact.

- Evaluate the reason bug is happening and add findings as the comment to the ticket in the @KanbanBoard.

- Move the ticket to 'in progress' state in the @KanbanBoard and start fixing the bug based on defined criteria.
    
- Move the ticket to 'done' state in the @KanbanBoard when the bug is fixed.
```

## License

MIT
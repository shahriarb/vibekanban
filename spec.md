# Kanban Board Specification

## 1. Overview
- Local Kanban board web application for task management.
- Backend: Python with Flask.
- Frontend: HTML and JavaScript.
- Integration with MCP protocol for agent communication.
- Single-user application for personal use running locally.

## 2. Features
- **Projects Management:** Create, update, delete projects.
- **Tickets:** 
  - Create tickets with types: `bug`, `story`, `spike`.
  - Ticket states: `backlog`, `in progress`, `done`.
  - Ticket content includes: `what`, `why`, `acceptance criteria`.
  - Automatic tracking of creation date and completion date.
- **MCP Integration:**
  - REST API endpoints for Cursor MCP communication.
  - Allow Cursor to create and update tickets in Yolo mode.
  - Track development progress visually.
- **Metrics:**
  - Implementation of DORA metrics for project tracking.
  - Visual representation of development performance.

## 3. Backend Design

### Database: SQLite

#### Tables:
- **Projects**: ID, name, description.
- **Tickets**: ID, project_id, type, state, what, why, acceptance_criteria, created_date, completed_date.
- **TicketTypes**: ID, name (bug, story, spike).
- **TicketStates**: ID, name (backlog, in progress, done).
- **Metrics**: ID, ticket_id, lead_time, change_failure (boolean).

### Flask Routes:
- `/projects`: 
  - **POST**: Create a new project.
  - **GET**: List all projects.
  - **PUT**: Update a project.
  - **DELETE**: Delete a project.
- `/tickets`: 
  - **POST**: Create a new ticket.
  - **GET**: List all tickets for a project.
  - **PUT**: Update a ticket (including state transitions).
  - **DELETE**: Delete a ticket.
- `/mcp`: 
  - **POST**: Create tickets from Cursor.
  - **PUT**: Update ticket status from Cursor.
  - **GET**: Retrieve ticket information for Cursor.
- `/metrics`:
  - **GET**: Retrieve DORA metrics data.

## 4. Frontend Design

### HTML Pages:
- **Project Dashboard**:
  - A page that lists all projects with options to create, edit, or delete them.
  - Form for creating a new project with fields for name and description.
- **Ticket Board**:
  - A Kanban-style board with columns for ticket states: backlog, in progress, done.
  - Drag-and-drop functionality for moving tickets between columns.
  - Form to create a new ticket with fields for type, what, why, and acceptance criteria.
- **Metrics Dashboard**:
  - Display of DORA metrics data.
  - Visualizations for:
    - Deployment Frequency
    - Lead Time for Changes
    - Change Failure Rate
    - Time to Restore Service

### JavaScript:
- Use fetch or XMLHttpRequest to interact with the Flask backend.
- Handle form submissions for creating projects and tickets.
- Update the UI dynamically based on API responses.
- Implement drag-and-drop functionality for the Kanban board.
- Render metrics visualizations using a charting library.

## 5. MCP Integration
- REST endpoints for Cursor to interact with.
- Support for Cursor to create tickets during Yolo mode development.
- Allow Cursor to move tickets between states as development progresses.
- Provide status updates to Cursor about current tickets.

## 6. MCP Settings
- Create a settings page or section where you can:
  - Configure the application to work as an MCP server for Cursor.
  - Input necessary connection parameters.
  - Save these settings so they can be used for API calls.
  - This can be a simple form that updates a config file or stores the details in your database. 
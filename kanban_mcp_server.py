from typing import Dict, List, Any, Optional
import sys
import os
from mcp.server.fastmcp import FastMCP

# Import database models and setup
from app import create_app, db
from app.models.project import Project
from app.models.ticket import Ticket
from app.models.comments import Comment

# Initialize FastMCP server
mcp = FastMCP("kanban-board")

# Create app context for database access
app = create_app()
app_context = app.app_context()

# Database access functions
def get_projects_from_db():
    """Get all projects directly from the database."""
    print("Accessing database directly for projects", file=sys.stderr)
    
    try:
        # Query all projects
        projects = Project.query.all()
        
        if not projects:
            print("No projects found in database", file=sys.stderr)
            return "No projects found."
        
        print(f"Found {len(projects)} projects in database", file=sys.stderr)
        
        # Convert projects to dictionaries for formatting
        project_dicts = [project.to_dict() for project in projects]
        
        # Format the result string
        result = "Projects:\n\n"
        for project in project_dicts:
            result += f"ID: {project['id']}\n"
            result += f"Name: {project['name']}\n"
            result += f"Description: {project['description']}\n"
            result += f"Tickets: {project.get('ticket_count', 0)}\n\n"
        
        return result
    except Exception as e:
        print(f"Error accessing database: {str(e)}", file=sys.stderr)
        return f"Error fetching projects: {str(e)}"

def get_tickets_from_db(project_id=None):
    """Get tickets directly from the database, optionally filtered by project."""
    print(f"Accessing database directly for tickets (project_id={project_id})", file=sys.stderr)
    
    try:
        # Build query
        query = Ticket.query
        if project_id:
            query = query.filter_by(project_id=project_id)
            
        tickets = query.all()
        
        if not tickets:
            return "No tickets found."
            
        # Format the result
        result = f"Tickets{f' for Project {project_id}' if project_id else ''}:\n\n"
        for ticket in tickets:
            ticket_dict = ticket.to_dict()
            result += f"ID: {ticket_dict['id']}\n"
            result += f"What: {ticket_dict['what']}\n"
            result += f"State: {ticket_dict.get('state_name', 'Unknown')}\n"
            result += f"Type: {ticket_dict.get('type_name', 'Unknown')}\n"
            if ticket_dict.get('why'):
                result += f"Why: {ticket_dict['why']}\n"
            result += "\n"
            
        return result
    except Exception as e:
        print(f"Error accessing database: {str(e)}", file=sys.stderr)
        return f"Error fetching tickets: {str(e)}"

def create_ticket_in_db(project_id, what, why=None, acceptance_criteria=None, test_steps=None, ticket_type=2):
    """Create a new ticket directly in the database."""
    print(f"Creating ticket in database: {what}", file=sys.stderr)
    
    try:
        # Find the project
        project = Project.query.get(project_id)
        if not project:
            return f"Error: Project with ID {project_id} not found."
            
        # Create ticket
        ticket = Ticket(
            project_id=project_id,
            what=what,
            why=why,
            acceptance_criteria=acceptance_criteria,
            test_steps=test_steps,
            type=ticket_type,  # Use the provided ticket_type parameter
            state=1,  # Default to 'backlog'
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return f"Successfully created ticket #{ticket.id}: {ticket.what}"
    except Exception as e:
        db.session.rollback()
        print(f"Error creating ticket: {str(e)}", file=sys.stderr)
        return f"Error creating ticket: {str(e)}"

def update_ticket_state_in_db(ticket_id, state_name):
    """Update a ticket's state directly in the database."""
    print(f"Updating ticket #{ticket_id} state to '{state_name}'", file=sys.stderr)
    
    try:
        # Find the ticket
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return f"Error: Ticket with ID {ticket_id} not found."
            
        # Map state name to state ID
        state_map = {"backlog": 1, "in progress": 2, "done": 3, "on hold": 4}
        state_id = state_map.get(state_name.lower())
        
        if not state_id:
            return f"Error: Invalid state '{state_name}'. Valid states are: backlog, in progress, done, on hold"
            
        # Update ticket state
        ticket.state = state_id
        
        # If marking as done, set completed date
        if state_id == 3:  # done
            from datetime import datetime
            ticket.completed_date = datetime.utcnow()
            
        db.session.commit()
        
        return f"Successfully updated ticket #{ticket_id} to state '{state_name}'"
    except Exception as e:
        db.session.rollback()
        print(f"Error updating ticket state: {str(e)}", file=sys.stderr)
        return f"Error updating ticket state: {str(e)}"

def add_comment_to_db(ticket_id, content):
    """Add a comment to a ticket directly in the database."""
    print(f"Adding comment to ticket #{ticket_id}", file=sys.stderr)
    
    try:
        # Find the ticket
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return f"Error: Ticket with ID {ticket_id} not found."
            
        # Create comment
        comment = Comment(
            ticket_id=ticket_id,
            content=content
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return f"Successfully added comment to ticket #{ticket_id}"
    except Exception as e:
        db.session.rollback()
        print(f"Error adding comment: {str(e)}", file=sys.stderr)
        return f"Error adding comment: {str(e)}"

def get_kanban_status_from_db():
    """Get Kanban board status directly from the database."""
    print("Getting Kanban status from database", file=sys.stderr)
    
    try:
        # Get all projects
        projects = Project.query.all()
        project_dicts = [project.to_dict() for project in projects]
        
        # Get all tickets
        tickets = Ticket.query.all()
        
        # Count tickets by state
        state_names = {1: "backlog", 2: "in progress", 3: "done", 4: "on hold"}
        states = {state_name: 0 for state_name in state_names.values()}
        
        for ticket in tickets:
            state_name = state_names.get(ticket.state)
            if state_name:
                states[state_name] += 1
                
        # Format the result
        status_text = "Kanban Board Status:\n\n"
        status_text += f"Total Tickets: {len(tickets)}\n\n"
        
        status_text += "Tickets by State:\n"
        for state, count in states.items():
            status_text += f"- {state}: {count}\n"
        
        status_text += "\nProjects:\n"
        for project in project_dicts:
            status_text += f"- {project['name']}: {project.get('ticket_count', 0)} tickets\n"
        
        return status_text
    except Exception as e:
        print(f"Error getting Kanban status: {str(e)}", file=sys.stderr)
        return f"Error getting Kanban status: {str(e)}"

# MCP Tool Implementations
@mcp.tool()
async def get_kanban_status() -> str:
    """
    Get the current status of the Kanban board, including ticket counts by state and project.

    Returns:
        str: A formatted string summarizing the total number of tickets, ticket counts by state (backlog, in progress, done, on hold), and a breakdown of tickets per project.

    Usage:
        Use this tool to get a high-level overview of the Kanban board's current state, which is useful for reporting, dashboards, or monitoring progress across all projects.
    """
    with app_context:
        return get_kanban_status_from_db()

@mcp.tool()
async def create_ticket(project_id: int, what: str, why: str = None, 
                       acceptance_criteria: str = None, test_steps: str = None,
                       ticket_type: int = 2) -> str:
    """
    Create a new ticket in the Kanban board.

    Args:
        project_id (int): The ID of the project this ticket belongs to.
        what (str): Description of what needs to be done (ticket summary).
        why (str, optional): Explanation of why this ticket is important.
        acceptance_criteria (str, optional): Criteria for considering this ticket done.
        test_steps (str, optional): Steps to test this ticket.
        ticket_type (int, optional): Type of ticket (1: bug, 2: story, etc.). Defaults to 2 (story).

    Returns:
        str: A confirmation message with the new ticket's ID and summary, or an error message if creation fails.

    Usage:
        Use this tool to add new work items, bugs, or stories to a project. Provide as much detail as possible for clarity and traceability. The ticket will be created in the 'backlog' state by default.
    """
    with app_context:
        return create_ticket_in_db(project_id, what, why, acceptance_criteria, test_steps, ticket_type)

@mcp.tool()
async def update_ticket_state(ticket_id: int, state: str) -> str:
    """
    Update a ticket's state in the Kanban board.

    Args:
        ticket_id (int): The ID of the ticket to update.
        state (str): The new state name (e.g., 'backlog', 'in progress', 'done', 'on hold').

    Returns:
        str: A confirmation message if the update is successful, or an error message if the ticket or state is invalid.

    Usage:
        Use this tool to move a ticket between workflow states. This is essential for tracking progress and managing work in the Kanban process.
    """
    with app_context:
        return update_ticket_state_in_db(ticket_id, state)

@mcp.tool()
async def list_projects() -> str:
    """
    List all projects in the Kanban board.

    Returns:
        str: A formatted list of all projects, including their IDs, names, descriptions, and ticket counts.

    Usage:
        Use this tool to discover available projects and their basic information. Useful for selecting a project before creating or listing tickets.
    """
    print("list_projects tool called", file=sys.stderr)
    with app_context:
        return get_projects_from_db()

@mcp.tool()
async def list_tickets(project_id: Optional[int] = None) -> str:
    """
    List tickets, optionally filtered by project.

    Args:
        project_id (int, optional): The ID of the project to filter tickets by. If not provided, lists all tickets across all projects.

    Returns:
        str: A formatted list of tickets, including their IDs, summaries, states, and types. If filtered by project, only tickets for that project are shown.

    Usage:
        Use this tool to review the current work items, bugs, or stories in a project or across all projects. Helpful for planning, triage, or reporting.
    """
    with app_context:
        return get_tickets_from_db(project_id)

@mcp.tool()
async def add_comment(ticket_id: int, content: str) -> str:
    """
    Add a comment to a ticket.

    Args:
        ticket_id (int): The ID of the ticket to comment on.
        content (str): The comment text to add.

    Returns:
        str: A confirmation message if the comment is added successfully, or an error message if the ticket is not found.

    Usage:
        Use this tool to add clarifications, updates, or discussion to a ticket. Comments are useful for collaboration and documenting decisions or progress.
    """
    with app_context:
        return add_comment_to_db(ticket_id, content)

# Run the server
if __name__ == "__main__":
    print("Starting Kanban MCP Server...", file=sys.stderr)
    print("Using direct database access instead of HTTP", file=sys.stderr)
    try:
        # Push the application context
        app_context.push()
        
        # Run the MCP server with stdio transport for Cursor
        mcp.run(transport='stdio')
    except Exception as e:
        print(f"Error starting MCP server: {str(e)}", file=sys.stderr)
    finally:
        # Clean up the application context
        app_context.pop()  
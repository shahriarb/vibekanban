from typing import Dict, List, Any, Optional
import httpx
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("kanban-board")

# Base URL for your Flask application
BASE_URL = "http://127.0.0.1:5050"

# Helper function for making API requests to your Flask app
async def make_api_request(method: str, endpoint: str, data: Dict = None) -> Dict:
    """Make a request to the Kanban API with proper error handling."""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            if method.lower() == "get":
                response = await client.get(url, headers=headers, timeout=10.0)
            elif method.lower() == "post":
                response = await client.post(url, headers=headers, json=data, timeout=10.0)
            elif method.lower() == "put":
                response = await client.put(url, headers=headers, json=data, timeout=10.0)
            elif method.lower() == "delete":
                response = await client.delete(url, headers=headers, timeout=10.0)
            else:
                return {"error": f"Unsupported method: {method}"}
                
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# MCP Tool Implementations
@mcp.tool()
async def get_kanban_status() -> str:
    """Get the current status of the Kanban board, including ticket counts by state."""
    data = await make_api_request("get", "/mcp/status")
    
    if "error" in data:
        return f"Error fetching Kanban status: {data['error']}"
    
    states = data.get("states", {})
    projects = data.get("projects", [])
    total_tickets = data.get("total_tickets", 0)
    
    status_text = "Kanban Board Status:\n\n"
    status_text += f"Total Tickets: {total_tickets}\n\n"
    
    status_text += "Tickets by State:\n"
    for state, count in states.items():
        status_text += f"- {state}: {count}\n"
    
    status_text += "\nProjects:\n"
    for project in projects:
        status_text += f"- {project['name']}: {project.get('ticket_count', 0)} tickets\n"
    
    return status_text

@mcp.tool()
async def create_ticket(project_id: int, what: str, why: str = None, 
                       acceptance_criteria: str = None, test_steps: str = None) -> str:
    """Create a new ticket in the Kanban board.

    Args:
        project_id: The ID of the project this ticket belongs to
        what: Description of what needs to be done
        why: Optional explanation of why this ticket is important
        acceptance_criteria: Optional criteria for considering this ticket done
        test_steps: Optional steps to test this ticket
    """
    ticket_data = {
        "project_id": project_id,
        "what": what,
        "why": why,
        "acceptance_criteria": acceptance_criteria,
        "test_steps": test_steps
    }
    
    # Remove None values
    ticket_data = {k: v for k, v in ticket_data.items() if v is not None}
    
    response = await make_api_request("post", "/mcp/create-ticket", ticket_data)
    
    if "error" in response:
        return f"Error creating ticket: {response['error']}"
    
    return f"Successfully created ticket #{response['id']}: {response['what']}"

@mcp.tool()
async def update_ticket_state(ticket_id: int, state: str) -> str:
    """Update a ticket's state in the Kanban board.

    Args:
        ticket_id: The ID of the ticket to update
        state: The new state name (e.g., 'backlog', 'in progress', 'done')
    """
    response = await make_api_request("put", f"/mcp/update-ticket/{ticket_id}", {"state": state})
    
    if "error" in response:
        return f"Error updating ticket state: {response['error']}"
    
    return f"Successfully updated ticket #{ticket_id} to state '{state}'"

@mcp.tool()
async def list_projects() -> str:
    """List all projects in the Kanban board."""
    response = await make_api_request("get", "/projects/")
    
    if "error" in response:
        return f"Error fetching projects: {response['error']}"
    
    if not response:
        return "No projects found."
    
    result = "Projects:\n\n"
    for project in response:
        result += f"ID: {project['id']}\n"
        result += f"Name: {project['name']}\n"
        result += f"Description: {project['description']}\n"
        result += f"Tickets: {project.get('ticket_count', 0)}\n\n"
    
    return result

@mcp.tool()
async def list_tickets(project_id: Optional[int] = None) -> str:
    """List tickets, optionally filtered by project.

    Args:
        project_id: Optional ID of the project to filter tickets by
    """
    endpoint = "/tickets/"
    if project_id:
        endpoint += f"?project_id={project_id}"
    
    response = await make_api_request("get", endpoint)
    
    if "error" in response:
        return f"Error fetching tickets: {response['error']}"
    
    if not response:
        return "No tickets found."
    
    result = f"Tickets{f' for Project {project_id}' if project_id else ''}:\n\n"
    for ticket in response:
        result += f"ID: {ticket['id']}\n"
        result += f"What: {ticket['what']}\n"
        result += f"State: {ticket.get('state_name', 'Unknown')}\n"
        result += f"Type: {ticket.get('type_name', 'Unknown')}\n"
        if ticket.get('why'):
            result += f"Why: {ticket['why']}\n"
        result += "\n"
    
    return result

@mcp.tool()
async def add_comment(ticket_id: int, content: str) -> str:
    """Add a comment to a ticket.

    Args:
        ticket_id: The ID of the ticket to comment on
        content: The comment text
    """
    response = await make_api_request("post", f"/api/v1/tickets/{ticket_id}/comments", {"content": content})
    
    if "error" in response:
        return f"Error adding comment: {response['error']}"
    
    return f"Successfully added comment to ticket #{ticket_id}"

# Run the server
if __name__ == "__main__":
    print("Starting Kanban MCP Server...")
    mcp.run(transport='stdio') 
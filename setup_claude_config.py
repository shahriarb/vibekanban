import os
import json
import pathlib

def setup_claude_config():
    """
    Create or update the Claude for Desktop configuration file
    to point to our Kanban board as a custom tool.
    """
    # Determine the Claude config directory
    home_dir = pathlib.Path.home()
    
    if os.name == 'posix':  # macOS or Linux
        config_dir = home_dir / "Library" / "Application Support" / "Claude"
    elif os.name == 'nt':  # Windows
        config_dir = home_dir / "AppData" / "Roaming" / "Claude"
    else:
        print(f"Unsupported operating system: {os.name}")
        return
    
    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Config file path
    config_file = config_dir / "claude_desktop_config.json"
    
    # Read existing config if it exists
    existing_config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
                print("Loaded existing Claude configuration.")
        except json.JSONDecodeError:
            print("Existing config file is invalid JSON. Creating a new one.")
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Update the config for our kanban-board
    if 'customTools' not in existing_config:
        existing_config['customTools'] = {}
    
    existing_config['customTools']['kanban-board'] = {
        "capabilities": ["mcp"],  # Indicate that this is a custom MCP tool
        "title": "Kanban Board",
        "description": "Kanban Board for project and task management",
        "baseUrl": "http://localhost:5050/mcp",
        "apiPath": "/tools",  # Path to get tool descriptions
        "actions": [
            {
                "id": "get_status",
                "title": "Get Kanban Status",
                "description": "Get the current status of the Kanban board"
            },
            {
                "id": "list_projects",
                "title": "List Projects",
                "description": "List all projects in the Kanban board"
            },
            {
                "id": "list_tickets",
                "title": "List Tickets",
                "description": "List tickets in the Kanban board"
            },
            {
                "id": "create_ticket",
                "title": "Create Ticket",
                "description": "Create a new ticket in the Kanban board"
            },
            {
                "id": "update_ticket_state",
                "title": "Update Ticket State",
                "description": "Update a ticket's state in the Kanban board"
            },
            {
                "id": "add_comment",
                "title": "Add Comment",
                "description": "Add a comment to a ticket"
            }
        ]
    }
    
    # Save the updated config
    with open(config_file, 'w') as f:
        json.dump(existing_config, f, indent=2)
    
    print(f"Claude for Desktop configuration saved to: {config_file}")
    print("Now you can start the Kanban Board and use it as a tool in Claude for Desktop!")

if __name__ == "__main__":
    setup_claude_config() 
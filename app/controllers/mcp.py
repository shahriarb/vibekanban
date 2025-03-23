"""
MCP controller for integration with Cursor.
"""
from typing import Dict, List, Tuple, Union
from flask import Blueprint, jsonify, request, render_template, current_app
from app import db
from app.models.project import Project
from app.models.ticket import Ticket, TicketType, TicketState
from app.models.mcp_config import MCPConfig

bp = Blueprint('mcp', __name__, url_prefix='/mcp')

@bp.route('/', methods=['GET'])
def mcp_root() -> Dict:
    """
    Root MCP endpoint - provides basic status and API information.
    
    Returns:
        A JSON response with MCP status and available endpoints.
    """
    return jsonify({
        'status': 'online',
        'name': 'Kanban Board MCP',
        'version': '1.0',
        'endpoints': {
            'GET /': 'This status information',
            'GET /config': 'Get current MCP configuration',
            'POST /config': 'Update MCP configuration',
            'GET /status': 'Get Kanban board status',
            'POST /create-ticket': 'Create a new ticket',
            'PUT /update-ticket/<id>': 'Update a ticket state'
        }
    })

@bp.route('/config', methods=['GET'])
def get_config() -> Dict:
    """
    Get the current MCP configuration.
    
    Returns:
        A JSON response with the MCP configuration.
    """
    config = MCPConfig.get_config()
    
    if not config:
        return jsonify({
            'enabled': False,
            'endpoint_url': None,
            'api_key': None
        })
        
    return jsonify(config.to_dict())

@bp.route('/config', methods=['POST'])
def update_config() -> Dict:
    """
    Update the MCP configuration.
    
    Returns:
        A JSON response with the updated MCP configuration.
    """
    data = request.get_json()
    config = MCPConfig.save_config(data)
    return jsonify(config.to_dict())

@bp.route('/settings', methods=['GET'])
def settings() -> str:
    """
    Render the MCP settings page.
    
    Returns:
        The rendered HTML template for the MCP settings.
    """
    return render_template('mcp/settings.html')

@bp.route('/create-ticket', methods=['POST'])
def create_ticket() -> Tuple[Dict, int]:
    """
    Create a new ticket from Cursor in Yolo mode.
    
    Returns:
        A JSON response with the created ticket data and a 201 status code.
    """
    data = request.get_json()
    
    # Validate required fields
    if not data.get('project_id'):
        return jsonify({'error': 'Project ID is required'}), 400
    if not data.get('what'):
        return jsonify({'error': 'Ticket description (what) is required'}), 400
    
    # Set default type to 'story' if not provided
    if not data.get('type'):
        story_type = TicketType.query.filter_by(name='story').first()
        if story_type:
            data['type'] = story_type.id
        else:
            return jsonify({'error': 'No ticket types defined in the system'}), 500
    
    # Set default state to 'backlog' if not provided
    if not data.get('state'):
        backlog_state = TicketState.query.filter_by(name='backlog').first()
        if backlog_state:
            data['state'] = backlog_state.id
        else:
            return jsonify({'error': 'No ticket states defined in the system'}), 500
    
    # Create the ticket
    ticket = Ticket.from_dict(data)
    db.session.add(ticket)
    db.session.commit()
    
    return jsonify(ticket.to_dict()), 201

@bp.route('/update-ticket/<int:ticket_id>', methods=['PUT'])
def update_ticket_state(ticket_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Update a ticket's state from Cursor.
    
    Args:
        ticket_id: The ID of the ticket to update.
        
    Returns:
        A JSON response with the updated ticket data, or an error if not found.
    """
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
        
    data = request.get_json()
    
    # Only allow state updates via this endpoint
    if 'state' in data:
        # Get the state by name if a string is provided, or by ID if an integer
        if isinstance(data['state'], str):
            state = TicketState.query.filter_by(name=data['state']).first()
            if not state:
                return jsonify({'error': f"Invalid state name: {data['state']}"}), 400
            ticket.update_state(state.id)
        else:
            # Assume it's an ID
            ticket.update_state(data['state'])
    
    db.session.commit()
    
    return jsonify(ticket.to_dict())

@bp.route('/status', methods=['GET'])
def get_status() -> Dict:
    """
    Get the status of the Kanban board for Cursor.
    
    Returns:
        A JSON response with the status information.
    """
    # Get counts of tickets by state
    states = TicketState.query.all()
    state_counts = {}
    
    for state in states:
        count = Ticket.query.filter_by(state=state.id).count()
        state_counts[state.name] = count
    
    # Get project information
    projects = Project.query.all()
    project_info = [project.to_dict() for project in projects]
    
    return jsonify({
        'states': state_counts,
        'projects': project_info,
        'total_tickets': Ticket.query.count()
    }) 
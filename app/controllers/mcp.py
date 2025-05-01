"""
MCP controller for integration with Cursor.

This controller implements a simplified version of the Model Context Protocol
to provide integration with Cursor and other AI assistants. It exposes
endpoints that follow MCP concepts of tools and resources.
"""
from typing import Dict, List, Tuple, Union
from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models.project import Project
from app.models.ticket import Ticket, TicketType, TicketState
from app.models.comments import Comment

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
        'capabilities': {
            'tools': True,  # We support tool execution
            'resources': False,  # We don't support resource access
            'prompts': False,  # We don't support prompt templates
        },
        'endpoints': {
            'GET /': 'This status information',
            'GET /status': 'Get Kanban board status',
            'POST /create-ticket': 'Create a new ticket',
            'PUT /update-ticket/<id>': 'Update a ticket state',
            'GET /tools': 'Get available tools',
            'GET /projects': 'List all projects',
            'GET /tickets': 'List all tickets',
            'POST /comments/<ticket_id>': 'Add a comment to a ticket'
        }
    })

@bp.route('/tools', methods=['GET'])
def get_tools() -> Dict:
    """
    Get available MCP tools.
    
    Returns:
        A JSON response with the available tools.
    """
    tools = [
        {
            'name': 'get_status',
            'description': 'Get the current status of the Kanban board',
            'endpoint': '/mcp/status',
            'method': 'GET',
            'parameters': []
        },
        {
            'name': 'create_ticket',
            'description': 'Create a new ticket in the Kanban board',
            'endpoint': '/mcp/create-ticket',
            'method': 'POST',
            'parameters': [
                {'name': 'project_id', 'type': 'integer', 'required': True, 'description': 'The ID of the project this ticket belongs to'},
                {'name': 'what', 'type': 'string', 'required': True, 'description': 'Description of what needs to be done'},
                {'name': 'why', 'type': 'string', 'required': False, 'description': 'Explanation of why this ticket is important'},
                {'name': 'acceptance_criteria', 'type': 'string', 'required': False, 'description': 'Criteria for considering this ticket done'},
                {'name': 'test_steps', 'type': 'string', 'required': False, 'description': 'Steps to test this ticket'}
            ]
        },
        {
            'name': 'update_ticket_state',
            'description': 'Update a ticket\'s state in the Kanban board',
            'endpoint': '/mcp/update-ticket/{ticket_id}',
            'method': 'PUT',
            'parameters': [
                {'name': 'ticket_id', 'type': 'integer', 'required': True, 'description': 'The ID of the ticket to update'},
                {'name': 'state', 'type': 'string', 'required': True, 'description': 'The new state name (e.g., \'backlog\', \'in progress\', \'done\')'}
            ]
        },
        {
            'name': 'list_projects',
            'description': 'List all projects in the Kanban board',
            'endpoint': '/mcp/projects',
            'method': 'GET',
            'parameters': []
        },
        {
            'name': 'list_tickets',
            'description': 'List tickets, optionally filtered by project',
            'endpoint': '/mcp/tickets',
            'method': 'GET',
            'parameters': [
                {'name': 'project_id', 'type': 'integer', 'required': False, 'description': 'The ID of the project to filter tickets by'}
            ]
        },
        {
            'name': 'add_comment',
            'description': 'Add a comment to a ticket',
            'endpoint': '/mcp/comments/{ticket_id}',
            'method': 'POST',
            'parameters': [
                {'name': 'ticket_id', 'type': 'integer', 'required': True, 'description': 'The ID of the ticket to comment on'},
                {'name': 'content', 'type': 'string', 'required': True, 'description': 'The comment text'}
            ]
        }
    ]
    
    return jsonify(tools)

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

@bp.route('/projects', methods=['GET'])
def get_projects() -> Dict:
    """
    Get all projects for MCP integration.
    
    Returns:
        A JSON response with all projects.
    """
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects])

@bp.route('/tickets', methods=['GET'])
def get_tickets() -> Dict:
    """
    Get tickets for MCP integration, optionally filtered by project.
    
    Returns:
        A JSON response with tickets data.
    """
    project_id = request.args.get('project_id', type=int)
    
    query = Ticket.query
    
    if project_id:
        query = query.filter_by(project_id=project_id)
        
    tickets = query.all()
    return jsonify([ticket.to_dict() for ticket in tickets])

@bp.route('/comments/<int:ticket_id>', methods=['POST'])
def add_comment(ticket_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Add a comment to a ticket for MCP integration.
    
    Args:
        ticket_id: The ID of the ticket to comment on.
        
    Returns:
        A JSON response with the created comment data.
    """
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
        
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Comment content is required'}), 400
        
    comment = Comment(
        ticket_id=ticket_id,
        content=data['content']
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'id': comment.id,
        'ticket_id': comment.ticket_id,
        'content': comment.content,
        'created_date': comment.created_date.isoformat() if comment.created_date else None,
        'updated_date': comment.updated_date.isoformat() if comment.updated_date else None
    }), 201 
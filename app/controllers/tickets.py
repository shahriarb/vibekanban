"""
Tickets controller for handling ticket-related routes.
"""
from typing import Dict, List, Tuple, Union
from datetime import datetime
from flask import Blueprint, jsonify, request, render_template, current_app
from app import db
from app.models.project import Project
from app.models.ticket import Ticket, TicketType, TicketState, TicketPriority
from app.models.metric import Metric

bp = Blueprint('tickets', __name__, url_prefix='/tickets')

@bp.route('/', methods=['GET'])
def get_tickets() -> Union[str, Tuple[Dict, int]]:
    """
    Get tickets, optionally filtered by project.
    
    Returns:
        If requested as JSON, returns a JSON response with tickets data.
        If requested as HTML, returns the tickets board HTML page.
    """
    project_id = request.args.get('project_id', type=int)
    
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        # API request, return JSON
        query = Ticket.query
        
        if project_id:
            query = query.filter_by(project_id=project_id)
            
        tickets = query.all()
        return jsonify([ticket.to_dict() for ticket in tickets])
    
    # Web request, return the board HTML
    return render_template('tickets/board.html', project_id=project_id)

@bp.route('/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Get a specific ticket by ID.
    
    Args:
        ticket_id: The ID of the ticket to retrieve.
        
    Returns:
        A JSON response with the ticket data, or 404 if not found.
    """
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
        
    return jsonify(ticket.to_dict())

@bp.route('/', methods=['POST'])
def create_ticket() -> Tuple[Dict, int]:
    """
    Create a new ticket.
    
    Returns:
        A JSON response with the created ticket data and a 201 status code.
    """
    data = request.get_json()
    
    # Validate required fields
    if not data.get('project_id'):
        return jsonify({'error': 'Project ID is required'}), 400
    if not data.get('what'):
        return jsonify({'error': 'Ticket description (what) is required'}), 400
    if not data.get('type'):
        return jsonify({'error': 'Ticket type is required'}), 400
    
    # Check if the project exists
    project = Project.query.get(data['project_id'])
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # If state is not provided, use the first state (typically 'backlog')
    if not data.get('state'):
        first_state = TicketState.query.filter_by(name='backlog').first()
        if first_state:
            data['state'] = first_state.id
        else:
            return jsonify({'error': 'No ticket states defined in the system'}), 500
    
    # Create the ticket
    ticket = Ticket.from_dict(data)
    db.session.add(ticket)
    db.session.commit()
    
    return jsonify(ticket.to_dict()), 201

@bp.route('/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Update an existing ticket.
    
    Args:
        ticket_id: The ID of the ticket to update.
        
    Returns:
        A JSON response with the updated ticket data, or an error if not found.
    """
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
        
    data = request.get_json()
    old_state = ticket.state
    was_done = ticket.completed_date is not None
    
    # Update fields
    if 'project_id' in data:
        # Check if the project exists
        project = Project.query.get(data['project_id'])
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        ticket.project_id = data['project_id']
        
    if 'type' in data:
        ticket.type = data['type']
    if 'priority' in data:
        ticket.priority = data['priority'] if data['priority'] else None
    if 'what' in data:
        ticket.what = data['what']
    if 'why' in data:
        ticket.why = data['why']
    if 'acceptance_criteria' in data:
        ticket.acceptance_criteria = data['acceptance_criteria']
    if 'test_steps' in data:
        ticket.test_steps = data['test_steps']
    
    # State transition requires special handling
    if 'state' in data and data['state'] != old_state:
        # Update the state and set/reset completed_date as needed
        ticket.update_state(data['state'])
        
        # If moving to 'done', calculate and record lead time
        new_state = TicketState.query.get(data['state'])
        if new_state and new_state.name == 'done' and not was_done:
            # Calculate lead time in minutes
            lead_time = None
            if ticket.created_date and ticket.completed_date:
                lead_time = int((ticket.completed_date - ticket.created_date).total_seconds() / 60)
                
            # Record metrics
            metric = Metric(
                ticket_id=ticket.id,
                lead_time=lead_time,
                deployment_date=datetime.utcnow()
            )
            db.session.add(metric)
    
    db.session.commit()
    
    return jsonify(ticket.to_dict())

@bp.route('/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Delete a ticket.
    
    Args:
        ticket_id: The ID of the ticket to delete.
        
    Returns:
        A JSON response confirming deletion, or an error if not found.
    """
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
        
    db.session.delete(ticket)
    db.session.commit()
    
    return jsonify({'message': f'Ticket {ticket_id} deleted successfully'})

@bp.route('/board', methods=['GET'])
def board() -> str:
    """
    Render the tickets board page.
    
    Returns:
        The rendered HTML template for the tickets board.
    """
    project_id = request.args.get('project_id', type=int)
    return render_template('tickets/board.html', project_id=project_id)

@bp.route('/types', methods=['GET'])
def get_ticket_types() -> Dict:
    """
    Get all ticket types.
    
    Returns:
        A JSON response with all ticket types.
    """
    types = TicketType.query.all()
    return jsonify([t.to_dict() for t in types])

@bp.route('/states', methods=['GET'])
def get_ticket_states() -> Dict:
    """
    Get all ticket states.
    
    Returns:
        A JSON response with all ticket states.
    """
    states = TicketState.query.all()
    return jsonify([s.to_dict() for s in states])

@bp.route('/priorities', methods=['GET'])
def get_ticket_priorities() -> Dict:
    """
    Get all ticket priorities.
    
    Returns:
        A JSON response with all ticket priorities.
    """
    priorities = TicketPriority.query.all()
    return jsonify([p.to_dict() for p in priorities]) 
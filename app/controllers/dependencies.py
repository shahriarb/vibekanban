"""
Dependencies controller for handling dependency-related routes.
"""
from typing import Dict, List, Tuple, Union
from flask import Blueprint, jsonify, request, render_template
from app import db
from app.models.ticket import Ticket

bp = Blueprint('dependencies', __name__, url_prefix='/dependencies')

@bp.route('/<int:ticket_id>', methods=['GET'])
def get_dependencies(ticket_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Get all dependencies for a ticket.
    
    Args:
        ticket_id: The ID of the ticket to get dependencies for.
        
    Returns:
        A JSON response with the ticket's dependencies, or 404 if not found.
    """
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    dependencies = [t.to_dict() for t in ticket.dependencies]
    dependents = [t.to_dict() for t in ticket.dependents]
    
    return jsonify({
        'ticket_id': ticket_id,
        'dependencies': dependencies,
        'dependents': dependents,
        'all_dependencies_resolved': ticket.get_all_dependencies_resolved()
    })

@bp.route('/<int:ticket_id>/add/<int:dependency_id>', methods=['POST'])
def add_dependency(ticket_id: int, dependency_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Add a dependency to a ticket.
    
    Args:
        ticket_id: The ID of the ticket to add a dependency to.
        dependency_id: The ID of the ticket to add as a dependency.
        
    Returns:
        A JSON response confirming the addition, or an error if not found.
    """
    ticket = Ticket.query.get(ticket_id)
    dependency = Ticket.query.get(dependency_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    if not dependency:
        return jsonify({'error': 'Dependency ticket not found'}), 404
    
    if ticket.id == dependency.id:
        return jsonify({'error': 'A ticket cannot depend on itself'}), 400
    
    # Check for circular dependencies
    if dependency.has_dependency(ticket):
        return jsonify({'error': 'Adding this dependency would create a circular dependency'}), 400
    
    # Add the dependency
    ticket.add_dependency(dependency)
    db.session.commit()
    
    return jsonify({
        'message': f'Ticket {dependency_id} added as dependency to Ticket {ticket_id}',
        'ticket': ticket.to_dict()
    })

@bp.route('/<int:ticket_id>/remove/<int:dependency_id>', methods=['DELETE'])
def remove_dependency(ticket_id: int, dependency_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Remove a dependency from a ticket.
    
    Args:
        ticket_id: The ID of the ticket to remove a dependency from.
        dependency_id: The ID of the ticket to remove as a dependency.
        
    Returns:
        A JSON response confirming the removal, or an error if not found.
    """
    ticket = Ticket.query.get(ticket_id)
    dependency = Ticket.query.get(dependency_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    if not dependency:
        return jsonify({'error': 'Dependency ticket not found'}), 404
    
    # Remove the dependency
    ticket.remove_dependency(dependency)
    db.session.commit()
    
    return jsonify({
        'message': f'Ticket {dependency_id} removed as dependency from Ticket {ticket_id}',
        'ticket': ticket.to_dict()
    }) 
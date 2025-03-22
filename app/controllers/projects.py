"""
Projects controller for handling project-related routes.
"""
from typing import Dict, List, Tuple, Union
from flask import Blueprint, jsonify, request, render_template, current_app
from app import db
from app.models.project import Project

bp = Blueprint('projects', __name__, url_prefix='/projects')

@bp.route('/', methods=['GET'])
def get_projects() -> Union[str, Tuple[Dict, int]]:
    """
    Get all projects.
    
    Returns:
        If requested as JSON, returns a JSON response with the projects data.
        If requested as HTML, returns the projects dashboard HTML page.
    """
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        # API request, return JSON
        projects = Project.query.all()
        return jsonify([project.to_dict() for project in projects])
    
    # Web request, return the dashboard HTML
    return render_template('projects/dashboard.html')

@bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Get a specific project by ID.
    
    Args:
        project_id: The ID of the project to retrieve.
        
    Returns:
        A JSON response with the project data, or 404 if not found.
    """
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
        
    return jsonify(project.to_dict())

@bp.route('/', methods=['POST'])
def create_project() -> Tuple[Dict, int]:
    """
    Create a new project.
    
    Returns:
        A JSON response with the created project data and a 201 status code.
    """
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'Project name is required'}), 400
        
    # Create the project
    project = Project.from_dict(data)
    db.session.add(project)
    db.session.commit()
    
    return jsonify(project.to_dict()), 201

@bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Update an existing project.
    
    Args:
        project_id: The ID of the project to update.
        
    Returns:
        A JSON response with the updated project data, or an error if not found.
    """
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
        
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
        
    db.session.commit()
    
    return jsonify(project.to_dict())

@bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Delete a project.
    
    Args:
        project_id: The ID of the project to delete.
        
    Returns:
        A JSON response confirming deletion, or an error if not found.
    """
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
        
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': f'Project {project_id} deleted successfully'})

@bp.route('/dashboard', methods=['GET'])
def dashboard() -> str:
    """
    Render the projects dashboard page.
    
    Returns:
        The rendered HTML template for the projects dashboard.
    """
    return render_template('projects/dashboard.html') 
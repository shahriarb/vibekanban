from typing import List, Optional
from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models.comments import Comment
from app.models.ticket import Ticket

bp = Blueprint('comments', __name__, url_prefix='/api/v1')

@bp.route('/tickets/<int:ticket_id>/comments', methods=['GET'])
def get_ticket_comments(ticket_id: int) -> tuple[dict, int]:
    """
    Get all comments for a specific ticket.

    Args:
        ticket_id (int): The ID of the ticket.

    Returns:
        tuple[dict, int]: A tuple containing the response data and status code.
    """
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        comments = Comment.query.filter_by(ticket_id=ticket_id).all()
        return jsonify([{
            'id': comment.id,
            'ticket_id': comment.ticket_id,
            'content': comment.content,
            'created_date': comment.created_date.isoformat(),
            'updated_date': comment.updated_date.isoformat() if comment.updated_date else None
        } for comment in comments])
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/tickets/<int:ticket_id>/comments', methods=['POST'])
def create_comment(ticket_id: int) -> tuple[dict, int]:
    """
    Create a new comment for a specific ticket.

    Args:
        ticket_id (int): The ID of the ticket.

    Returns:
        tuple[dict, int]: A tuple containing the response data and status code.
    """
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
            
        comment = Comment(
            ticket_id=ticket_id,
            content=data['content'],
            created_date=datetime.utcnow()
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'id': comment.id,
            'ticket_id': comment.ticket_id,
            'content': comment.content,
            'created_date': comment.created_date.isoformat(),
            'updated_date': comment.updated_date.isoformat() if comment.updated_date else None
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id: int) -> tuple[dict, int]:
    """
    Update an existing comment.

    Args:
        comment_id (int): The ID of the comment to update.

    Returns:
        tuple[dict, int]: A tuple containing the response data and status code.
    """
    try:
        comment = Comment.query.get_or_404(comment_id)
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
            
        comment.content = data['content']
        comment.updated_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': comment.id,
            'ticket_id': comment.ticket_id,
            'content': comment.content,
            'created_date': comment.created_date.isoformat(),
            'updated_date': comment.updated_date.isoformat() if comment.updated_date else None
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id: int) -> tuple[dict, int]:
    """
    Delete a comment.

    Args:
        comment_id (int): The ID of the comment to delete.

    Returns:
        tuple[dict, int]: A tuple containing the response data and status code.
    """
    try:
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        return '', 204
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 
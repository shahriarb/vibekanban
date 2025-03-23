"""
Attachments controller for handling file uploads and downloads.
"""
from typing import Dict, List, Tuple, Union
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, request, current_app, send_file, abort
from app import db
from app.models.ticket import Ticket
from app.models.attachment import Attachment

bp = Blueprint('attachments', __name__, url_prefix='/attachments')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'csv', 'xlsx', 'docx'}

def allowed_file(filename: str) -> bool:
    """
    Check if a file has an allowed extension.
    
    Args:
        filename: The name of the file to check.
        
    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/ticket/<int:ticket_id>', methods=['POST'])
def upload_file(ticket_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Upload a file to attach to a ticket.
    
    Args:
        ticket_id: The ID of the ticket to attach the file to.
        
    Returns:
        A JSON response with the attachment data, or an error if upload failed.
    """
    # Check if ticket exists
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    # If the user does not select a file, the browser submits an
    # empty file without a filename
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Make filename secure to prevent directory traversal attacks
        filename = secure_filename(file.filename)
        
        # Create a unique filename to avoid name collisions
        now = datetime.utcnow()
        unique_filename = f"{now.strftime('%Y%m%d%H%M%S')}_{filename}"
        
        # Make sure the upload directory exists
        upload_dir = os.path.join(current_app.static_folder, 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # Save the file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Create an attachment record in the database
        attachment = Attachment(
            ticket_id=ticket_id,
            filename=filename,
            file_path=os.path.join('uploads', unique_filename),
            file_type=file.content_type,
            file_size=os.path.getsize(file_path)
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return jsonify(attachment.to_dict()), 201
    
    return jsonify({'error': 'File type not allowed'}), 400

@bp.route('/ticket/<int:ticket_id>', methods=['GET'])
def get_ticket_attachments(ticket_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Get all attachments for a ticket.
    
    Args:
        ticket_id: The ID of the ticket to get attachments for.
        
    Returns:
        A JSON response with all the attachments for the ticket, or an error if not found.
    """
    # Check if ticket exists
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    attachments = Attachment.query.filter_by(ticket_id=ticket_id).all()
    return jsonify([attachment.to_dict() for attachment in attachments])

@bp.route('/<int:attachment_id>', methods=['GET'])
def download_file(attachment_id: int):
    """
    Download an attachment file.
    
    Args:
        attachment_id: The ID of the attachment to download.
        
    Returns:
        The file to download, or an error if not found.
    """
    attachment = Attachment.query.get(attachment_id)
    if not attachment:
        return jsonify({'error': 'Attachment not found'}), 404
    
    file_path = os.path.join(current_app.static_folder, attachment.file_path)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found on server'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=attachment.filename,
        mimetype=attachment.file_type
    )

@bp.route('/<int:attachment_id>', methods=['DELETE'])
def delete_attachment(attachment_id: int) -> Union[Dict, Tuple[Dict, int]]:
    """
    Delete an attachment.
    
    Args:
        attachment_id: The ID of the attachment to delete.
        
    Returns:
        A JSON response confirming deletion, or an error if not found.
    """
    attachment = Attachment.query.get(attachment_id)
    if not attachment:
        return jsonify({'error': 'Attachment not found'}), 404
    
    # Delete the file from the server
    file_path = os.path.join(current_app.static_folder, attachment.file_path)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            current_app.logger.error(f"Error deleting file: {e}")
    
    # Delete the attachment record
    db.session.delete(attachment)
    db.session.commit()
    
    return jsonify({'message': f'Attachment {attachment_id} deleted successfully'}) 
"""
Attachment model for the Kanban board application.
"""
from typing import Dict
from datetime import datetime
from app import db

class Attachment(db.Model):
    """
    Attachment model representing a file attached to a ticket.
    
    Attributes:
        id: The unique identifier for the attachment.
        ticket_id: The ID of the ticket this attachment belongs to.
        filename: The original filename of the attachment.
        file_path: The path where the file is stored on the server.
        file_type: The MIME type of the file.
        file_size: The size of the file in bytes.
        uploaded_date: The date and time when the file was uploaded.
    """
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    uploaded_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """
        Convert the attachment to a dictionary.
        
        Returns:
            Dict: A dictionary representation of the attachment.
        """
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'uploaded_date': self.uploaded_date.isoformat() if self.uploaded_date else None
        } 
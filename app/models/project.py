"""
Project model for the Kanban board application.
"""
from typing import Dict, List, Optional
from datetime import datetime
from app import db

class Project(db.Model):
    """
    Project model representing a collection of related tickets.
    
    Attributes:
        id: The unique identifier for the project.
        name: The name of the project.
        description: A detailed description of the project.
        created_date: The date and time when the project was created.
    """
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with tickets
    tickets = db.relationship('Ticket', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict:
        """
        Convert the project to a dictionary.
        
        Returns:
            Dict: A dictionary representation of the project.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'ticket_count': len(self.tickets) if self.tickets else 0
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Project':
        """
        Create a new Project instance from a dictionary.
        
        Args:
            data: Dictionary containing project data.
            
        Returns:
            Project: A new Project instance.
        """
        return Project(
            name=data.get('name'),
            description=data.get('description')
        ) 
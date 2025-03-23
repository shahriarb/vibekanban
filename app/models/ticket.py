"""
Ticket models for the Kanban board application.
"""
from typing import Dict, List, Optional
from datetime import datetime
from app import db

class TicketType(db.Model):
    """
    Ticket type model representing the different types a ticket can have.
    
    Attributes:
        id: The unique identifier for the ticket type.
        name: The name of the ticket type (e.g., 'bug', 'story', 'spike').
    """
    __tablename__ = 'ticket_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    tickets = db.relationship('Ticket', backref='type_info', lazy=True)
    
    def to_dict(self) -> Dict:
        """
        Convert the ticket type to a dictionary.
        
        Returns:
            Dict: A dictionary representation of the ticket type.
        """
        return {
            'id': self.id,
            'name': self.name
        }

class TicketState(db.Model):
    """
    Ticket state model representing the different states a ticket can be in.
    
    Attributes:
        id: The unique identifier for the ticket state.
        name: The name of the ticket state (e.g., 'backlog', 'in progress', 'done').
    """
    __tablename__ = 'ticket_states'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    tickets = db.relationship('Ticket', backref='state_info', lazy=True)
    
    def to_dict(self) -> Dict:
        """
        Convert the ticket state to a dictionary.
        
        Returns:
            Dict: A dictionary representation of the ticket state.
        """
        return {
            'id': self.id,
            'name': self.name
        }

class Ticket(db.Model):
    """
    Ticket model representing a task in the Kanban board.
    
    Attributes:
        id: The unique identifier for the ticket.
        project_id: The ID of the project this ticket belongs to.
        type: The ID of the ticket type.
        state: The ID of the ticket state.
        what: Description of what the ticket is about.
        why: Explanation of why this ticket is important.
        acceptance_criteria: Criteria for considering this ticket done.
        created_date: The date and time when the ticket was created.
        completed_date: The date and time when the ticket was completed.
    """
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    type = db.Column(db.Integer, db.ForeignKey('ticket_types.id'), nullable=False)
    state = db.Column(db.Integer, db.ForeignKey('ticket_states.id'), nullable=False)
    what = db.Column(db.Text, nullable=False)
    why = db.Column(db.Text, nullable=True)
    acceptance_criteria = db.Column(db.Text, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime, nullable=True)
    
    # Relationship with metrics
    metrics = db.relationship('Metric', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    # Relationship with attachments
    attachments = db.relationship('Attachment', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict:
        """
        Convert the ticket to a dictionary.
        
        Returns:
            Dict: A dictionary representation of the ticket.
        """
        return {
            'id': self.id,
            'project_id': self.project_id,
            'type': self.type,
            'type_name': self.type_info.name if self.type_info else None,
            'state': self.state,
            'state_name': self.state_info.name if self.state_info else None,
            'what': self.what,
            'why': self.why,
            'acceptance_criteria': self.acceptance_criteria,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'attachments': [attachment.to_dict() for attachment in self.attachments] if self.attachments else []
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Ticket':
        """
        Create a new Ticket instance from a dictionary.
        
        Args:
            data: Dictionary containing ticket data.
            
        Returns:
            Ticket: A new Ticket instance.
        """
        return Ticket(
            project_id=data.get('project_id'),
            type=data.get('type'),
            state=data.get('state'),
            what=data.get('what'),
            why=data.get('why'),
            acceptance_criteria=data.get('acceptance_criteria')
        )
    
    def update_state(self, new_state_id: int) -> None:
        """
        Update the state of the ticket and set completed_date if moved to 'done'.
        
        Args:
            new_state_id: The ID of the new state.
        """
        self.state = new_state_id
        
        # Check if the new state is 'done'
        state = TicketState.query.get(new_state_id)
        if state and state.name == 'done':
            # Set the completed date when moved to 'done'
            if not self.completed_date:
                self.completed_date = datetime.utcnow()
        else:
            # Reset completed date if moved away from 'done'
            self.completed_date = None 
"""
Metric model for tracking DORA metrics in the Kanban board.
"""
from typing import Dict, List, Optional
from datetime import datetime
from app import db

class Metric(db.Model):
    """
    Metric model for tracking development performance metrics (DORA).
    
    Attributes:
        id: The unique identifier for the metric.
        ticket_id: The ID of the ticket this metric is associated with.
        lead_time: Time (in minutes) from ticket creation to completion.
        change_failure: Boolean indicating if the change resulted in a failure.
        deployment_date: When the associated change was deployed.
        restoration_time: Time (in minutes) to restore service after a failure.
    """
    __tablename__ = 'metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    lead_time = db.Column(db.Integer, nullable=True)  # in minutes
    change_failure = db.Column(db.Boolean, default=False)
    deployment_date = db.Column(db.DateTime, nullable=True)
    restoration_time = db.Column(db.Integer, nullable=True)  # in minutes
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """
        Convert the metric to a dictionary.
        
        Returns:
            Dict: A dictionary representation of the metric.
        """
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'lead_time': self.lead_time,
            'change_failure': self.change_failure,
            'deployment_date': self.deployment_date.isoformat() if self.deployment_date else None,
            'restoration_time': self.restoration_time,
            'record_date': self.record_date.isoformat() if self.record_date else None
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Metric':
        """
        Create a new Metric instance from a dictionary.
        
        Args:
            data: Dictionary containing metric data.
            
        Returns:
            Metric: A new Metric instance.
        """
        return Metric(
            ticket_id=data.get('ticket_id'),
            lead_time=data.get('lead_time'),
            change_failure=data.get('change_failure', False),
            deployment_date=data.get('deployment_date'),
            restoration_time=data.get('restoration_time')
        ) 
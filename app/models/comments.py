from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app import db

from app.models.base import Base

class Comment(Base):
    """Model for ticket comments.
    
    Attributes:
        id: The unique identifier for the comment
        ticket_id: The ID of the ticket this comment belongs to
        content: The text content of the comment
        created_date: When the comment was created
        updated_date: When the comment was last updated
        ticket: The relationship to the parent ticket
    """
    
    __tablename__ = 'comments'
    __table_args__ = {'extend_existing': True}
    
    id: int = Column(Integer, primary_key=True)
    ticket_id: int = Column(Integer, ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
    content: str = Column(Text, nullable=False)
    created_date: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_date: Optional[datetime] = Column(DateTime, nullable=True)
    
    # Relationship to parent ticket
    ticket = relationship("Ticket", back_populates="comments")

    def __repr__(self) -> str:
        return f'<Comment {self.id} for Ticket {self.ticket_id}>' 
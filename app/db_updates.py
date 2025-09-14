"""
Database update utilities for Kanban application.
Ensures required data states exist at startup.
"""

from app import db
from app.models.ticket import TicketState


def ensure_archived_state_exists() -> None:
    """
    Ensure the 'archived' state exists in the ticket_states table.
    This function is idempotent and safe to call at startup.
    """
    if not TicketState.query.filter_by(name="archived").first():
        archived_state = TicketState(name="archived")
        db.session.add(archived_state)
        db.session.commit()

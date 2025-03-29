"""
Flask CLI commands for the Kanban application.
"""
import click
from flask.cli import with_appcontext
from app import db
from app.models.project import Project
from app.models.ticket import Ticket, TicketType, TicketState

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database and create tables."""
    # Create all tables
    db.create_all()
    
    # Insert default ticket types if they don't exist
    types = ['bug', 'story', 'spike']
    for type_name in types:
        if not TicketType.query.filter_by(name=type_name).first():
            ticket_type = TicketType(name=type_name)
            db.session.add(ticket_type)
    
    # Insert default ticket states if they don't exist
    states = ['backlog', 'in progress', 'on hold', 'done']
    for state_name in states:
        if not TicketState.query.filter_by(name=state_name).first():
            ticket_state = TicketState(name=state_name)
            db.session.add(ticket_state)
    
    # Commit changes
    db.session.commit()
    
    click.echo('Database initialized with default values.') 
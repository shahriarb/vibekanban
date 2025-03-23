from app import db
from app.models.project import Project
from app.models.ticket import TicketType, TicketState, TicketPriority

def seed_data():
    """Seed the database with initial data."""
    # Seed ticket types if they don't exist
    if TicketType.query.count() == 0:
        types = [
            {'name': 'bug'},
            {'name': 'story'},
            {'name': 'task'},
            {'name': 'spike'}
        ]
        
        for type_data in types:
            ticket_type = TicketType(**type_data)
            db.session.add(ticket_type)
        
        db.session.commit()
        print("Ticket types seeded successfully.")
    
    # Seed ticket priorities if they don't exist
    if TicketPriority.query.count() == 0:
        priorities = [
            {'name': 'low'},
            {'name': 'medium'},
            {'name': 'high'},
            {'name': 'critical'}
        ]
        
        for priority_data in priorities:
            ticket_priority = TicketPriority(**priority_data)
            db.session.add(ticket_priority)
        
        db.session.commit()
        print("Ticket priorities seeded successfully.")
    
    # Seed ticket states if they don't exist
    if TicketState.query.count() == 0:
        states = [
            {'name': 'backlog'},
            {'name': 'in progress'},
            {'name': 'review'},
            {'name': 'done'}
        ]
        
        for state_data in states:
            ticket_state = TicketState(**state_data)
            db.session.add(ticket_state)
        
        db.session.commit()
        print("Ticket states seeded successfully.")
    
    # Seed a default project if none exists
    if Project.query.count() == 0:
        project = Project(
            name="Default Project",
            description="A default project to get started with."
        )
        db.session.add(project)
        db.session.commit()
        print("Default project seeded successfully.") 
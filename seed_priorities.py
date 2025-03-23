from app import create_app
from app.models.ticket import TicketPriority
from app import db

def seed_priorities():
    """Seed the ticket priorities."""
    app = create_app()
    with app.app_context():
        # Check if priorities already exist
        if TicketPriority.query.count() == 0:
            # Create priorities
            priorities = [
                {'name': 'low'},
                {'name': 'medium'},
                {'name': 'high'},
                {'name': 'critical'}
            ]
            
            # Add priorities to the database
            for priority_data in priorities:
                priority = TicketPriority(**priority_data)
                db.session.add(priority)
            
            # Commit the changes
            db.session.commit()
            print("Ticket priorities seeded successfully.")
        
        # Print current priorities
        priorities = TicketPriority.query.all()
        print(f"Current priorities: {[p.name for p in priorities]}")

if __name__ == "__main__":
    seed_priorities() 
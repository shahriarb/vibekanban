"""
Entry point for the Kanban application.
"""

from app import create_app
from app.seeders import seed_data
from app.db_updates import ensure_archived_state_exists

app = create_app()

if __name__ == "__main__":
    # Seed data
    with app.app_context():
        seed_data()
        ensure_archived_state_exists()

    app.run(debug=True, host="0.0.0.0", port=5050)

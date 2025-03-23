from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy

def get_db() -> SQLAlchemy:
    """
    Get the database instance.

    Returns:
        SQLAlchemy: The database instance.
    """
    if 'db' not in g:
        g.db = current_app.extensions['sqlalchemy'].db
    return g.db 
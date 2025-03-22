"""
Kanban Board Application

A simple Kanban board for task management with Cursor MCP integration.
"""
import os
from datetime import datetime
from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app(test_config=None):
    """Create and configure the Flask application instance."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Apply CORS settings for local development
    CORS(app)
    
    # Configure the application
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'kanban.sqlite')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Handle proxy headers for proper IP detection
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database with app
    db.init_app(app)

    # Register CLI commands
    from app.commands import init_db_command
    app.cli.add_command(init_db_command)

    # Register blueprints
    from app.controllers import projects, tickets, mcp, metrics
    app.register_blueprint(projects.bp)
    app.register_blueprint(tickets.bp)
    app.register_blueprint(mcp.bp)
    app.register_blueprint(metrics.bp)
    
    # Add context processor for template variables
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Set up the index route
    @app.route('/')
    def index():
        """Redirect to the projects dashboard."""
        return redirect(url_for('projects.dashboard'))

    return app 
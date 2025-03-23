"""
Kanban Board Application

A simple Kanban board for task management with Cursor MCP integration.
"""
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
import os
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    """
    Create and configure the Flask application.

    Args:
        test_config (dict, optional): Test configuration to override default config. Defaults to None.

    Returns:
        Flask: Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Set SQLAlchemy configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(app.instance_path, "kanban.sqlite")}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    
    # Configure static files for development
    if app.debug:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)
    
    # Apply CORS settings for local development
    CORS(app)
    
    # Configure SQLAlchemy
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Apply the ProxyFix middleware
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    # Register blueprints
    from app.controllers import projects, tickets, attachments, comments, metrics, mcp, dependencies
    
    app.register_blueprint(projects.bp)
    app.register_blueprint(tickets.bp)
    app.register_blueprint(attachments.bp)
    app.register_blueprint(comments.bp)
    app.register_blueprint(metrics.bp)
    app.register_blueprint(mcp.bp)
    app.register_blueprint(dependencies.bp)
    
    # Add context processor for template variables
    @app.context_processor
    def inject_globals():
        """
        Inject global variables into all templates.

        Returns:
            dict: Dictionary containing global variables.
        """
        return {
            'app_name': 'Kanban Board',
            'app_version': '1.0.0',
            'now': datetime.utcnow()
        }

    # Set up the index route
    @app.route('/')
    def index():
        """Redirect to the projects dashboard."""
        return redirect(url_for('projects.dashboard'))
    
    return app 
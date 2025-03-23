from app import db

class Base(db.Model):
    """Base model class that all other models will inherit from.
    
    This class provides common functionality and ensures consistent behavior
    across all models in the application.
    """
    
    __abstract__ = True 
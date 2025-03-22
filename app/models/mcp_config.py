"""
MCP Configuration model for integrating with Cursor.
"""
from typing import Dict, Optional
from app import db

class MCPConfig(db.Model):
    """
    MCP Configuration model for integrating with Cursor.
    
    Attributes:
        id: The unique identifier for the configuration.
        endpoint_url: The URL of the MCP endpoint.
        api_key: API key for authentication if needed.
        enabled: Whether MCP integration is enabled.
    """
    __tablename__ = 'mcp_config'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint_url = db.Column(db.String(255), nullable=True)
    api_key = db.Column(db.String(255), nullable=True)
    enabled = db.Column(db.Boolean, default=False)
    
    def to_dict(self) -> Dict:
        """
        Convert the MCP configuration to a dictionary.
        
        Returns:
            Dict: A dictionary representation of the MCP configuration.
        """
        return {
            'id': self.id,
            'endpoint_url': self.endpoint_url,
            'api_key': self.api_key,
            'enabled': self.enabled
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'MCPConfig':
        """
        Create a new MCPConfig instance from a dictionary.
        
        Args:
            data: Dictionary containing MCP configuration data.
            
        Returns:
            MCPConfig: A new MCPConfig instance.
        """
        return MCPConfig(
            endpoint_url=data.get('endpoint_url'),
            api_key=data.get('api_key'),
            enabled=data.get('enabled', False)
        )
    
    @staticmethod
    def get_config() -> Optional['MCPConfig']:
        """
        Get the current MCP configuration.
        
        Returns:
            Optional[MCPConfig]: The current MCP configuration, or None if not set.
        """
        return MCPConfig.query.first()
    
    @staticmethod
    def save_config(data: Dict) -> 'MCPConfig':
        """
        Save or update the MCP configuration.
        
        Args:
            data: Dictionary containing MCP configuration data.
            
        Returns:
            MCPConfig: The updated or created MCP configuration.
        """
        config = MCPConfig.get_config()
        
        if config:
            # Update existing config
            config.endpoint_url = data.get('endpoint_url', config.endpoint_url)
            config.api_key = data.get('api_key', config.api_key)
            config.enabled = data.get('enabled', config.enabled)
        else:
            # Create new config
            config = MCPConfig.from_dict(data)
            db.session.add(config)
            
        db.session.commit()
        return config 
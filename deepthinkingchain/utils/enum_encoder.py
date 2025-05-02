"""
Utility classes for JSON serialization.

This module contains utility classes for JSON serialization,
including an encoder for Enum types.
"""

import json
from enum import Enum
from deepthinkingchain.constants import AgentType

class EnumEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Enum types.
    
    This encoder converts Enum values to their string representation
    for proper JSON serialization.
    """
    
    def default(self, obj):
        """Convert the object to a JSON serializable format.
        
        Args:
            obj: The object to serialize
            
        Returns:
            A JSON serializable representation of the object
        """
        if isinstance(obj, Enum):
            return obj.name
        return super().default(obj) 
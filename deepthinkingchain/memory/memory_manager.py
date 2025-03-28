"""
Memory Manager for the Deep Thinking Chain.

This module contains the MemoryManager class which is responsible for 
storing and retrieving analysis state.
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Set

# Set up logging
logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages memory storage and retrieval for Deep Thinking Chain."""
    
    def __init__(self, memory_id: str, memory_dir: str = "memory"):
        """Initialize a MemoryManager.
        
        Args:
            memory_id: Unique identifier for this memory instance
            memory_dir: Directory to use for memory storage
        """
        self.memory_id = memory_id
        self.memory_dir = memory_dir
        
        # Create memory directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)
        
        # Initialize memory structure
        self.memory = {
            "memory_id": memory_id,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "iterations": [],
            "completion_percentage": 0,
            "completion_time": None,
            "current_focus": "financial_performance",
            "completed_focus_areas": [],
            "required_focus_areas": [
                "financial_performance",
                "competitive_analysis",
                "growth_prospects",
                "risk_assessment"
            ]
        }
        
        # Load existing memory if it exists
        self.memory_file = os.path.join(memory_dir, f"{memory_id}_memory.json")
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    self.memory = json.load(f)
                logger.info(f"Loaded existing memory from {self.memory_file}")
            except Exception as e:
                logger.error(f"Error loading memory: {str(e)}")
    
    def get_memory(self) -> Dict[str, Any]:
        """Get the current memory state.
        
        Returns:
            Dictionary containing the full memory state
        """
        return self.memory
    
    def update_memory(self, data: Dict[str, Any]) -> bool:
        """Update memory with new data.
        
        Args:
            data: Dictionary of key-value pairs to update in memory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update memory with new data
            self.memory.update(data)
            
            # Save to disk
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error updating memory: {str(e)}")
            return False
    
    def add_iteration(self, iteration_type: Any, data: Dict[str, Any]) -> bool:
        """Add a new iteration to memory.
        
        Args:
            iteration_type: Type of the iteration
            data: Dictionary containing iteration data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add type information to data
            data["type"] = str(iteration_type)
            
            # Add to iterations list
            self.memory["iterations"].append(data)
            
            # Save to disk
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error adding iteration: {str(e)}")
            return False
    
    def update_focus_area(self, focus_area: str, completed: bool = True) -> bool:
        """Update the status of a focus area.
        
        Args:
            focus_area: Name of the focus area to update
            completed: Whether the focus area is completed
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if completed:
                # Add to completed areas if not already there
                if focus_area not in self.memory["completed_focus_areas"]:
                    self.memory["completed_focus_areas"].append(focus_area)
            else:
                # Remove from completed areas if present
                if focus_area in self.memory["completed_focus_areas"]:
                    self.memory["completed_focus_areas"].remove(focus_area)
            
            # Calculate completion percentage
            total_areas = len(self.memory["required_focus_areas"])
            completed_areas = len(self.memory["completed_focus_areas"])
            if total_areas > 0:
                self.memory["completion_percentage"] = int((completed_areas / total_areas) * 100)
            
            # Save to disk
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error updating focus area: {str(e)}")
            return False
    
    def construct_parameters(self, placeholders: Optional[Set[str]] = None) -> Dict[str, Any]:
        """Construct a dictionary of parameters from memory for template filling.
        
        Args:
            placeholders: Optional set of placeholder names to construct parameters for
            
        Returns:
            Dictionary of parameter values
        """
        # Basic parameters that are always available
        params = {
            "memory_id": self.memory_id,
            "completion_percentage": self.memory["completion_percentage"],
            "current_focus": self.memory["current_focus"],
        }
        
        # Add iterations information
        if "iterations" in self.memory and self.memory["iterations"]:
            params["iteration_count"] = len(self.memory["iterations"])
            params["last_iteration"] = self.memory["iterations"][-1]
        
        return params 
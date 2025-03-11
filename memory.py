"""
Memory Manager for the Deep Thinking Chain.

This module contains the MemoryManager class which is responsible for loading,
updating, and saving memory for each analysis cycle in the DeepThinkingChain project.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import time


class MemoryManager:
    """Manages memory operations for the DeepThinkingChain analysis process.
    
    This class provides methods to load, update, and save memory for each analysis cycle,
    ensuring persistence of analysis state across runs and iterations.
    """
    
    def __init__(self, symbol: str, memory_dir: str = "memory"):
        """Initialize the MemoryManager for a specific stock symbol.
        
        Args:
            symbol: The stock symbol being analyzed (e.g., 'NVDA')
            memory_dir: Directory where memory files are stored (default: 'memory')
        """
        self.symbol = symbol.upper()
        self.memory_dir = memory_dir
        self.memory_file = f"{memory_dir}/{self.symbol}_memory.json"
        self.memory = {}
        
        # Create memory directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)
        
        # Initialize or load memory
        self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from disk if it exists, otherwise initialize a new memory structure.
        
        Returns:
            Dict containing the memory data
        """
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    self.memory = json.load(f)
                print(f"📂 Loaded existing memory for {self.symbol}")
            except json.JSONDecodeError:
                print(f"⚠️ Error loading memory file. Creating new memory.")
                self._initialize_memory()
        else:
            self._initialize_memory()
        
        return self.memory
    
    def _initialize_memory(self) -> Dict[str, Any]:
        """Initialize a new memory structure for the analysis process.
        
        Returns:
            Dict containing the initialized memory structure
        """
        self.memory = {
            "symbol": self.symbol,
            "iterations": [],
            "current_focus": "financial_performance",
            "required_focus_areas": [
                "financial_performance",
                "competitive_analysis",
                "growth_prospects",
                "risk_assessment"
            ],
            "completed_focus_areas": [],
            "start_time": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "completion_percentage": 0
        }
        self.save_memory()
        print(f"📝 Created new memory for {self.symbol}")
        return self.memory
    
    def save_memory(self) -> bool:
        """Save the current memory state to disk.
        
        Returns:
            Boolean indicating success or failure
        """
        try:
            # Update the last_updated timestamp
            self.memory["last_updated"] = datetime.now().isoformat()
            
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ Error saving memory: {str(e)}")
            return False
    
    def get_memory(self) -> Dict[str, Any]:
        """Get the current memory state.
        
        Returns:
            Dict containing the current memory data
        """
        return self.memory
    
    def update_memory(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update the memory with new data.
        
        Args:
            updates: Dict containing the updates to apply to the memory
            
        Returns:
            Dict containing the updated memory data
        """
        # Update the memory with the new data
        for key, value in updates.items():
            self.memory[key] = value
        
        # Save the updated memory
        self.save_memory()
        
        return self.memory
    
    def add_iteration(self, iteration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new iteration to the memory.
        
        Args:
            iteration_data: Dict containing the iteration data
            
        Returns:
            Dict containing the updated memory data
        """
        # Ensure iterations list exists
        if "iterations" not in self.memory:
            self.memory["iterations"] = []
        
        # Add timestamp if not present
        if "timestamp" not in iteration_data:
            iteration_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Add the iteration data
        self.memory["iterations"].append(iteration_data)
        
        # Update completion percentage
        self._update_completion_percentage()
        
        # Save the updated memory
        self.save_memory()
        
        return self.memory
    
    def update_focus_area(self, focus_area: str, completed: bool = True) -> Dict[str, Any]:
        """Update the current focus area and optionally mark it as completed.
        
        Args:
            focus_area: The focus area to set as current
            completed: Whether to mark the focus area as completed
            
        Returns:
            Dict containing the updated memory data
        """
        # Update current focus
        self.memory["current_focus"] = focus_area
        
        # Mark as completed if specified
        if completed and focus_area not in self.memory.get("completed_focus_areas", []):
            if "completed_focus_areas" not in self.memory:
                self.memory["completed_focus_areas"] = []
            self.memory["completed_focus_areas"].append(focus_area)
        
        # Update completion percentage
        self._update_completion_percentage()
        
        # Save the updated memory
        self.save_memory()
        
        return self.memory
    
    def _update_completion_percentage(self) -> float:
        """Update the analysis completion percentage based on iterations and focus areas.
        
        Returns:
            Float representing the completion percentage
        """
        required_areas = self.memory.get("required_focus_areas", [])
        completed_areas = self.memory.get("completed_focus_areas", [])
        iterations = self.memory.get("iterations", [])
        max_iterations = self.memory.get("max_iterations", 5)
        
        # Base percentage on completed focus areas and iteration count
        if not required_areas:
            area_percentage = 0
        else:
            area_percentage = (len(completed_areas) / len(required_areas)) * 100
        
        # Factor in iteration count (each iteration contributes up to 20%)
        iteration_percentage = min(len(iterations) / max_iterations * 20, 20)
        
        # Combine the two factors
        total_percentage = min(area_percentage * 0.8 + iteration_percentage, 100)
        
        # Update memory
        self.memory["completion_percentage"] = round(total_percentage, 1)
        
        return self.memory["completion_percentage"]
    
    def get_latest_iteration(self) -> Optional[Dict[str, Any]]:
        """Get the most recent iteration data.
        
        Returns:
            Dict containing the latest iteration data, or None if no iterations exist
        """
        iterations = self.memory.get("iterations", [])
        if iterations:
            return iterations[-1]
        return None
    
    def get_all_analyses(self) -> List[Dict[str, Any]]:
        """Get all analyses from all iterations.
        
        Returns:
            List of analysis results from all iterations
        """
        analyses = []
        for iteration in self.memory.get("iterations", []):
            if "analysis" in iteration:
                analyses.append(iteration["analysis"])
        return analyses
    
    def clear_memory(self) -> bool:
        """Clear the memory and start fresh.
        
        Returns:
            Boolean indicating success or failure
        """
        try:
            self._initialize_memory()
            return True
        except Exception as e:
            print(f"⚠️ Error clearing memory: {str(e)}")
            return False
    
    def export_memory(self, export_file: Optional[str] = None) -> str:
        """Export the memory to a JSON file.
        
        Args:
            export_file: Path to the export file (default: None, uses timestamp)
            
        Returns:
            Path to the exported file
        """
        if export_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = f"exports/{self.symbol}_memory_{timestamp}.json"
        
        # Create exports directory if it doesn't exist and the path has a directory
        directory = os.path.dirname(export_file)
        if directory:  # Only create directory if there is one in the path
            os.makedirs(directory, exist_ok=True)
        
        try:
            with open(export_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            print(f"📤 Exported memory to {export_file}")
            return export_file
        except Exception as e:
            print(f"⚠️ Error exporting memory: {str(e)}")
            return ""


if __name__ == "__main__":
    # Example usage
    import sys
    
    # Get symbol from command line argument or use default
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    
    # Initialize memory manager
    memory_manager = MemoryManager(symbol)
    
    # Print current memory
    print("\nCurrent Memory:")
    print(json.dumps(memory_manager.get_memory(), indent=2))
    
    # Add a test iteration
    test_iteration = {
        "iteration": 1,
        "focus": "financial_performance",
        "analysis": {
            "analysis_type": "financial_performance",
            "symbol": symbol,
            "sentiment": "positive",
            "confidence": "high",
            "key_points": ["Strong revenue growth", "High profit margins"]
        }
    }
    
    memory_manager.add_iteration(test_iteration)
    
    # Update focus area
    memory_manager.update_focus_area("competitive_analysis")
    
    # Print updated memory
    print("\nUpdated Memory:")
    print(json.dumps(memory_manager.get_memory(), indent=2))
    
    print(f"\nMemory saved to: {memory_manager.memory_file}") 
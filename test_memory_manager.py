"""
Test script for the MemoryManager class.

This script demonstrates the functionality of the MemoryManager class,
including loading, updating, and saving memory for analysis cycles.
"""

import os
import json
from memory import MemoryManager

def test_memory_manager():
    """Test the core functionality of the MemoryManager class."""
    
    # Test initialization
    print("\n=== Testing MemoryManager Initialization ===")
    symbol = "TEST"
    
    # Clean up any existing test memory file
    memory_file = f"memory/{symbol}_memory.json"
    if os.path.exists(memory_file):
        os.remove(memory_file)
        print(f"Removed existing test memory file: {memory_file}")
    
    # Initialize memory manager
    memory_manager = MemoryManager(symbol)
    print(f"Initialized MemoryManager for {symbol}")
    
    # Get initial memory state
    memory = memory_manager.get_memory()
    print("\nInitial Memory State:")
    print(f"Symbol: {memory['symbol']}")
    print(f"Current Focus: {memory['current_focus']}")
    print(f"Required Focus Areas: {memory['required_focus_areas']}")
    print(f"Completed Focus Areas: {memory['completed_focus_areas']}")
    print(f"Completion Percentage: {memory['completion_percentage']}%")
    
    # Test updating memory
    print("\n=== Testing Memory Updates ===")
    
    # Update max iterations
    memory_manager.update_memory({"max_iterations": 4})
    print("Updated max_iterations to 4")
    
    # Add an iteration
    iteration_data = {
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
    
    memory_manager.add_iteration(iteration_data)
    print("Added iteration 1 (financial_performance)")
    
    # Update focus area
    memory_manager.update_focus_area("competitive_analysis")
    print("Updated focus area to competitive_analysis")
    
    # Add another iteration
    iteration_data = {
        "iteration": 2,
        "focus": "competitive_analysis",
        "analysis": {
            "analysis_type": "competitive_analysis",
            "symbol": symbol,
            "sentiment": "neutral",
            "confidence": "medium",
            "key_points": ["Strong market position", "Increasing competition"]
        }
    }
    
    memory_manager.add_iteration(iteration_data)
    print("Added iteration 2 (competitive_analysis)")
    
    # Get updated memory state
    memory = memory_manager.get_memory()
    print("\nUpdated Memory State:")
    print(f"Symbol: {memory['symbol']}")
    print(f"Current Focus: {memory['current_focus']}")
    print(f"Required Focus Areas: {memory['required_focus_areas']}")
    print(f"Completed Focus Areas: {memory['completed_focus_areas']}")
    print(f"Completion Percentage: {memory['completion_percentage']}%")
    print(f"Number of Iterations: {len(memory['iterations'])}")
    
    # Test getting latest iteration
    latest = memory_manager.get_latest_iteration()
    print("\nLatest Iteration:")
    print(f"Iteration: {latest['iteration']}")
    print(f"Focus: {latest['focus']}")
    print(f"Analysis Type: {latest['analysis']['analysis_type']}")
    print(f"Sentiment: {latest['analysis']['sentiment']}")
    
    # Test getting all analyses
    analyses = memory_manager.get_all_analyses()
    print(f"\nRetrieved {len(analyses)} analyses")
    
    # Test exporting memory
    export_file = memory_manager.export_memory("exports/test_export.json")
    print(f"Exported memory to {export_file}")
    
    # Test clearing memory
    memory_manager.clear_memory()
    memory = memory_manager.get_memory()
    print("\nAfter Clearing Memory:")
    print(f"Symbol: {memory['symbol']}")
    print(f"Current Focus: {memory['current_focus']}")
    print(f"Completed Focus Areas: {memory['completed_focus_areas']}")
    print(f"Completion Percentage: {memory['completion_percentage']}%")
    print(f"Number of Iterations: {len(memory['iterations'])}")
    
    # Clean up
    if os.path.exists(memory_file):
        os.remove(memory_file)
    if os.path.exists("exports/test_export.json"):
        os.remove("exports/test_export.json")
    if os.path.exists("exports"):
        try:
            os.rmdir("exports")
        except:
            pass
    
    print("\n=== Memory Manager Test Complete ===")

if __name__ == "__main__":
    test_memory_manager() 
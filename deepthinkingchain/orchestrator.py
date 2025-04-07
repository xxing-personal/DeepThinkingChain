"""
Orchestrator for the Deep Thinking Chain.

This module contains the DeepThinkingChain class which coordinates the agents
and workflow for multi-agent investment analysis.
"""

import json
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import agents
from deepthinkingchain.agents.tool_agent import ToolAgent
from deepthinkingchain.agents.analysis_agent import AnalysisAgent
from deepthinkingchain.agents.planning_agent import PlanningAgent
from deepthinkingchain.agents.summarization_agent import SummarizationAgent

# Import memory manager
from deepthinkingchain.memory import MemoryManager
from deepthinkingchain.constants import AgentType


class DeepThinkingChain:
    """Orchestrates multi-agent investment analysis cycles for a given stock symbol."""

    def __init__(self, symbol: str, max_iterations: int = 5):
        """Initialize DeepThinkingChain with the target investment symbol.
        
        Args:
            symbol: The stock symbol to analyze (e.g., 'NVDA')
            max_iterations: Maximum number of analysis iterations to perform
        """
        self.symbol = symbol.upper()
        self.max_iterations = max_iterations
        self.iteration = 0
        self.analyses = []
        
        # Initialize agents
        self.tool_agent = ToolAgent()
        self.analysis_agent = AnalysisAgent()
        self.planning_agent = PlanningAgent()
        self.summarization_agent = SummarizationAgent()
        
        # Create necessary directories
        os.makedirs('results', exist_ok=True)
        
        # Initialize memory manager
        self.memory_manager = MemoryManager(symbol)
        
        # Update memory with max iterations
        self.memory_manager.update_memory({"max_iterations": max_iterations})
    
    def run(self, verbose: bool = True) -> Dict[str, Any]:
        """Run the Deep Thinking Chain analysis workflow.
        
        This method orchestrates the multi-agent workflow by:
        1. Starting with the Analysis agent
        2. Alternating between Analysis, Planning and Tool agents as needed
        3. Finishing with the Summarization agent
        
        Args:
            verbose: Whether to print progress to console
        
        Returns:
            Dict containing the final analysis results
        """
        if verbose:
            print(f"Starting Deep Thinking Chain analysis for {self.symbol}")
            
        start_time = datetime.now()
        self.iteration = 0
        current_step = "analysis"  # Start with analysis agent
        last_result = None
        
        # Main workflow loop
        while self.iteration < self.max_iterations:
            self.iteration += 1
            
            if verbose:
                print(f"\nIteration {self.iteration}/{self.max_iterations}: Running {current_step}")
            
            # Execute the current step based on the workflow
            if current_step == "analysis":
                # Run analysis agent
                analysis_result = self.analysis_agent.run(last_result)
                last_result = analysis_result
                self.analyses.append(analysis_result)
                
                # Store the analysis in memory
                self.memory_manager.add_iteration(AgentType.ANALYSIS, analysis_result)
                
                # Get the next step from the agent
                current_step = self.analysis_agent.get_next_step()
                
            elif current_step == "planning":
                # Run planning agent to determine next steps
                planning_result = self.planning_agent.run(last_result)
                last_result = planning_result
                
                # Store the planning result in memory
                self.memory_manager.add_iteration(AgentType.PLANNING, planning_result)
                
                # Get the next step from the agent
                current_step = self.planning_agent.get_next_step()
                
                # Check if we should continue or finish
                if current_step == "finish" or not planning_result.get("continue_analysis", True):
                    break
                    
            elif current_step == "tool":
                # Run tool agent to gather information
                tool_result = self.tool_agent.run(last_result)
                last_result = tool_result
                
                # Store the tool result in memory
                self.memory_manager.add_iteration(AgentType.TOOL, tool_result)
                
                # Get the next step from the agent
                current_step = self.tool_agent.get_next_step()
                
            elif current_step == "summary":
                # Skip to summary phase
                break
                
            else:
                if verbose:
                    print(f"Unknown step: {current_step}. Defaulting to analysis.")
                current_step = "analysis"
                
            # Optional: Save interim results
            self._save_interim_results()
            
        # Run final summarization
        if verbose:
            print("\nGenerating final summary...")
            
        summary_result = self.summarization_agent.generate_summary(
            symbol=self.symbol,
            analyses=self.analyses,
            iterations=self.iteration
        )
        
        # Store the summary in memory
        self.memory_manager.add_iteration(AgentType.SUMMARY, summary_result)
        
        # Save final results
        final_results = {
            "symbol": self.symbol,
            "iterations": self.iteration,
            "analyses": self.analyses,
            "summary": summary_result,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "execution_time_seconds": (datetime.now() - start_time).total_seconds()
        }
        
        self._save_final_results(final_results)
        
        if verbose:
            print(f"\nAnalysis complete. Performed {self.iteration} iterations.")
            print(f"Results saved to: results/{self.symbol}_analysis.json")
            
        return final_results
    
    def _save_interim_results(self) -> None:
        """Save intermediate results after each iteration."""
        interim_file = f"results/{self.symbol}_interim.json"
        with open(interim_file, 'w') as f:
            json.dump({
                "symbol": self.symbol,
                "iteration": self.iteration,
                "analyses": self.analyses,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
    
    def _save_final_results(self, results: Dict[str, Any]) -> None:
        """Save the final analysis results to a JSON file.
        
        Args:
            results: The results dictionary to save
        """
        results_file = f"results/{self.symbol}_analysis.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
  
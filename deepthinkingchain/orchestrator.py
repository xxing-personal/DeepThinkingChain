"""
Orchestrator for the Deep Thinking Chain.

This module contains the DeepThinkingChain class which coordinates the agents
and workflow for multi-agent investment analysis.
"""

import json
import os
import time
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import uuid

# Import agents
from deepthinkingchain.agents.tool_agent import ToolAgent
from deepthinkingchain.agents.analysis_agent import AnalysisAgent
from deepthinkingchain.agents.planning_agent import PlanningAgent
from deepthinkingchain.agents.summarization_agent import SummarizationAgent
from deepthinkingchain.agents.intent_analysis_agent import IntentAnalysisAgent

# Import memory manager
from deepthinkingchain.memory import MemoryManager
from deepthinkingchain.constants import AgentType
from deepthinkingchain.tools.register_tools import register_tools
from deepthinkingchain.utils.enum_encoder import EnumEncoder

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepThinkingChain:
    """Orchestrates multi-agent investment analysis cycles for a given stock symbol."""

    def __init__(self, user_input: str, max_iterations: int = 30, session_id: str = None):
        """Initialize DeepThinkingChain with the user input query.
        
        Args:
            user_input: The user's input query to analyze
            max_iterations: Maximum number of analysis iterations to perform
            session_id: Optional session ID to use (creates a new one if not provided)
        """
        self.user_input = user_input
        self.max_iterations = max_iterations
        self.iteration = 0
        self.analyses = []
        
        # Generate a unique ID for this analysis session if not provided
        self.session_id = session_id if session_id else str(uuid.uuid4())
        
        # Extract a topic name from user input (for file naming)
        # If user_input is too long, just use first few words
        if len(user_input) > 50:
            self.topic = user_input[:50].strip().replace(' ', '_')
        else:
            self.topic = user_input.strip().replace(' ', '_')
        
        # Initialize agents - create only the ones we need when we need them
        self._agents = {}
        
        # Initialize tool registry
        self.tools = register_tools()
        
        # Create necessary directories
        os.makedirs('results', exist_ok=True)
        
        # Initialize memory manager
        self.memory_manager = MemoryManager(self.session_id)
        
        # Populate initial data
        self.memory_manager.ensure_field("data.max_iterations", max_iterations)
        self.memory_manager.ensure_field("data.user_input", user_input)
        self.memory_manager.ensure_field("data.topic", self.topic)
        
        # Map step names to agent handlers
        self._step_handlers = {
            "intent_analysis": self._handle_intent_analysis,
            "analysis": self._handle_analysis,
            "planning": self._handle_planning,
            "tool": self._handle_tool,
            "summary": self._handle_summary
        }
    
    def run(self, verbose: bool = True) -> Dict[str, Any]:
        """Run the Deep Thinking Chain analysis workflow.
        
        This method orchestrates the multi-agent workflow by:
        1. Starting with the Intent Analysis agent to understand the user's query
        2. Alternating between Analysis, Planning and Tool agents as needed
        3. Finishing with the Summarization agent
        
        Args:
            verbose: Whether to print progress to console
        
        Returns:
            Dict containing the final analysis results
        """
        if verbose:
            print(f"Starting Deep Thinking Chain analysis for {self.topic}")
            
        start_time = datetime.now()
        self.iteration = 0
        current_step = "intent_analysis"  # Start with intent analysis agent
        last_result = None
        
        # Main workflow loop
        while self.iteration < self.max_iterations and current_step:
            if current_step == "finish" or current_step == "summary":
                break
            
            self.iteration += 1
            
            if verbose:
                print(f"\nIteration {self.iteration}/{self.max_iterations}: Running {current_step}")
            
            # Execute the current step based on the workflow
            handler = self._step_handlers.get(current_step)
            if not handler:
                logger.warning(f"Unknown step: {current_step}. Defaulting to analysis.")
                current_step = "analysis"
                handler = self._step_handlers["analysis"]

            result, next_step = handler(last_result)
            last_result = result
            current_step = next_step
     
            self._save_interim_results()
            
        # Run final summarization
        if verbose:
            print("\nGenerating final summary...")
        
        # Get the analysis results from memory
        analyses = self.memory_manager.ensure_field("data.iterations", [])
        analysis_results = [entry["data"] for entry in analyses 
                           if entry["type"] == str(AgentType.ANALYSIS)]
        
        # Run the summarization agent
        summary_agent = self._get_agent("summary")
        summary_result = summary_agent.generate_summary(
            analyses=analysis_results,
            topic=self.topic,
            iterations=self.iteration
        )
        
        # Final completion time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Save final results
        final_results = {
            "session_id": self.session_id,
            "topic": self.topic,
            "iterations": self.iteration,
            "summary": summary_result,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "execution_time_seconds": execution_time
        }
        
        self._save_final_results(final_results)
        
        if verbose:
            print(f"\nAnalysis complete. Performed {self.iteration} iterations.")
            print(f"Results saved to: results/{self.topic}_analysis.json")
            
        return final_results
    
    def _save_interim_results(self) -> None:
        """Save intermediate results after each iteration."""
        interim_file = f"results/{self.topic}_interim.json"
        
        # Get iterations from memory manager
        memory_data = self.memory_manager.get_memory()
        
        # Create a streamlined version for the interim file
        interim_data = {
            "session_id": self.session_id,
            "topic": self.topic,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "timestamp": datetime.now().isoformat(),
            "memory": memory_data
        }
        
        with open(interim_file, 'w') as f:
            json.dump(interim_data, f, indent=2, cls=EnumEncoder)
    
    def _save_final_results(self, results: Dict[str, Any]) -> None:
        """Save the final analysis results to a JSON file.
        
        Args:
            results: The results dictionary to save
        """
        results_file = f"results/{self.topic}_analysis.json"
        
        # Enhance results with the full memory state
        full_results = {
            **results,
            "memory": self.memory_manager.get_memory()
        }
        
        with open(results_file, 'w') as f:
            json.dump(full_results, f, indent=2, cls=EnumEncoder)
    
    def _get_agent(self, agent_type: str):
        """Get or create an agent of the specified type.
        
        This method implements lazy initialization for agents,
        creating them only when needed.
        
        Args:
            agent_type: The type of agent to get or create
            
        Returns:
            The agent instance
        """
        if agent_type not in self._agents:
            if agent_type == "intent_analysis":
                self._agents[agent_type] = IntentAnalysisAgent(memory_manager=self.memory_manager)
            elif agent_type == "analysis":
                self._agents[agent_type] = AnalysisAgent(memory_manager=self.memory_manager)
            elif agent_type == "planning":
                self._agents[agent_type] = PlanningAgent(memory_manager=self.memory_manager)
            elif agent_type == "tool":
                self._agents[agent_type] = ToolAgent(memory_manager=self.memory_manager)
            elif agent_type == "summary":
                self._agents[agent_type] = SummarizationAgent(memory_manager=self.memory_manager)
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
                
        return self._agents[agent_type]
    
    def _handle_intent_analysis(self, last_result: Any) -> Dict[str, Any]:
        """Handle the intent analysis step.
        
        Args:
            last_result: Result from the previous step
            
        Returns:
            Result from the intent analysis agent and the next step
        """
        agent = self._get_agent("intent_analysis")
        intent_result = agent.run(self.user_input)
        next_step = agent.get_next_step() or "analysis"
        
        return intent_result, next_step
    
    def _handle_analysis(self, last_result: Any) -> Dict[str, Any]:
        """Handle the analysis step.
        
        Args:
            last_result: Result from the previous step
            
        Returns:
            Result from the analysis agent and the next step
        """
        agent = self._get_agent("analysis")
        analysis_result = agent.run(last_result)
        self.analyses.append(analysis_result)
        
        next_step = agent.get_next_step() or "planning"
        return analysis_result, next_step
    
    def _handle_planning(self, last_result: Any) -> Dict[str, Any]:
        """Handle the planning step.
        
        Args:
            last_result: Result from the previous step
            
        Returns:
            Result from the planning agent and the next step
        """
        agent = self._get_agent("planning")
        planning_result = agent.run(last_result)
        
        next_step = agent.get_next_step()
        
        # Check if we should continue or finish
        if next_step == "finish" or not planning_result.get("continue_analysis", True):
            next_step = "summary"
            
        return planning_result, next_step
    
    def _handle_tool(self, last_result: Any) -> Dict[str, Any]:
        """Handle the tool step.
        
        Args:
            last_result: Result from the previous step
            
        Returns:
            Result from the tool agent and the next step
        """
        agent = self._get_agent("tool")
        tool_result = agent.run(last_result)
        
        next_step = agent.get_next_step() or "analysis"
        return tool_result, next_step
    
    def _handle_summary(self, last_result: Any) -> Dict[str, Any]:
        """Handle the summary step.
        
        Args:
            last_result: Result from the previous step
            
        Returns:
            Result from the summary agent and None as the next step
        """
        # This is a special case that ends the workflow
        return None, None
  
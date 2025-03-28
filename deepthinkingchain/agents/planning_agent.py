"""
Planning Agent for the Deep Thinking Chain.

This module contains the PlanningAgent class which is responsible for
determining next steps in the analysis workflow.
"""

import logging
import time
from typing import Dict, Any, List, Optional

from deepthinkingchain.agents.agent_base import Agent
from deepthinkingchain.model import Model
from deepthinkingchain.constants import AgentType

# Set up logging
logger = logging.getLogger(__name__)

class PlanningAgent(Agent):
    """Agent for planning next steps in the analysis workflow."""
    
    def __init__(self, prompt_template_name: str = "planning", model_name: str = None):
        """Initialize the PlanningAgent.
        
        Args:
            prompt_template_name: Name of the template to use (defaults to "planning")
            model_name: Name of the model to use
        """
        # Initialize the base Agent class
        super().__init__(prompt_template_name=prompt_template_name, model_name=model_name)
        
        # Set the agent type
        self.agent_type = AgentType.PLANNING
        
        # Update metadata
        self.metadata.update({
            "agent_type": self.agent_type
        })
        
        # Initialize model for generating text
        self.model = Model(model=model_name)
    
    def _run(self, analysis_result: Dict[str, Any], iteration: int, max_iterations: int,
            completed_focus_areas: List[str], required_focus_areas: List[str]) -> Dict[str, Any]:
        """Run the planning process to determine next steps.
        
        This is a stub implementation for the demo.
        
        Args:
            analysis_result: Results of the last analysis step
            iteration: Current iteration number
            max_iterations: Maximum number of iterations allowed
            completed_focus_areas: List of focus areas already completed
            required_focus_areas: List of focus areas that must be completed
            
        Returns:
            Dictionary containing the planning results
        """
        logger.info(f"Planning next steps for iteration {iteration}/{max_iterations}")
        
        # Determine if we should continue or stop
        continue_analysis = iteration < max_iterations
        
        # Find next focus area (if any remain)
        remaining_focus_areas = [area for area in required_focus_areas if area not in completed_focus_areas]
        if remaining_focus_areas and continue_analysis:
            next_focus = remaining_focus_areas[0]
        else:
            next_focus = None
            continue_analysis = False
        
        # This is a stub - would normally use a model to intelligently plan next steps
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "continue_analysis": continue_analysis,
            "next_focus": next_focus,
            "reasoning": f"Stub planning logic: {len(remaining_focus_areas)} focus areas remaining",
            "completion_percentage": min(100, int(((iteration) / max_iterations) * 100))
        }
    
    def plan_next(self, analysis_result: Dict[str, Any], iteration: int, max_iterations: int,
                 completed_focus_areas: List[str], required_focus_areas: List[str]) -> Dict[str, Any]:
        """Public method to plan the next steps in the analysis workflow.
        
        Args:
            analysis_result: Results of the last analysis step
            iteration: Current iteration number
            max_iterations: Maximum number of iterations allowed
            completed_focus_areas: List of focus areas already completed
            required_focus_areas: List of focus areas that must be completed
            
        Returns:
            Dictionary containing the planning results
        """
        return self.run(analysis_result, iteration, max_iterations, completed_focus_areas, required_focus_areas) 
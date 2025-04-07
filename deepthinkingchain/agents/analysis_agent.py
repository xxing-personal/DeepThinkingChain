"""
Analysis Agent for the Deep Thinking Chain.

This module contains the AnalysisAgent class which is responsible for analyzing
financial data and extracting investment insights.
"""

import json
import os
import time
import logging
import re
from typing import Dict, Any, Optional, List, Union

# Import the base Agent class
from deepthinkingchain.agents.agent_base import Agent

# Import helper functions
from deepthinkingchain.prompts.prompt_template import format_data_for_prompt
from deepthinkingchain.memory import MemoryManager
from deepthinkingchain.model import Model
from deepthinkingchain.constants import AgentType

# Set up logging
logger = logging.getLogger(__name__)

class AnalysisAgent(Agent):
    """Agent performing detailed analysis and extraction of insights from raw financial data."""
    
    def __init__(self,  prompt_template_name: str = "generic_analysis", 
                 memory_manager: Optional[Union[str, MemoryManager]] = None, 
                 model_name: str = None):
        """Initialize the AnalysisAgent with model configuration.
        
        Args:
            text_to_analyze: The text to analyze.
            prompt_template_name: The template to use for analysis. Defaults to "generic_analysis".
            memory_manager: Optional memory manager for saving agent results
            model_name: The model to use for analysis. Defaults to "gpt-3.5-turbo".
        """
        # Initialize the base Agent class
        super().__init__(prompt_template_name=prompt_template_name, 
                         memory_manager=memory_manager, 
                         model_name=model_name)
        # Set the agent type
        self.agent_type = AgentType.ANALYSIS
        
        # Set the next step for this agent type
        self.set_next_step("planning")
        
        # Update metadata
        self.metadata.update({
            "agent_type": self.agent_type
        })
        
        # Initialize model for generating text
        self.model = Model(model_name)
    
    def _run(self, last_step_result: Union[str, Dict[str, Any], None] = None) -> Dict[str, Any]:
        """Run the analysis on provided financial data.
        
        Args:
            last_step_result: Results from the previous step or raw data to analyze
            
        Returns:
            Dictionary containing the analysis results
        """
        try:
            logger.info("Running analysis agent")
            
            # Format the last step result for inclusion in the prompt
            if last_step_result is None:
                last_step_result_str = "No previous data available."
            elif isinstance(last_step_result, str):
                last_step_result_str = last_step_result
            elif isinstance(last_step_result, dict):
                last_step_result_str = format_data_for_prompt(last_step_result)
            else:
                # Try to convert to string if not a recognized type
                last_step_result_str = str(last_step_result)
                
            # Process the template with the formatted last step result
            prompt = self.process_template(last_step_result=last_step_result_str)
            
            # Generate analysis using the model
            response = self.model.generate_json(prompt=prompt)
            
            # Ensure we have the expected result structure
            if not isinstance(response, dict):
                logger.warning(f"Expected dict response, got {type(response)}")
                # Convert to dict if possible
                if hasattr(response, '__dict__'):
                    response = response.__dict__
                else:
                    response = {"error": "Invalid response format"}
            
            # Ensure we have a result key
            if "result" not in response:
                response = {"result": response}
                
            # Add metadata
            response["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            response["agent_type"] = self.agent_type
            
            # Store next step from response if available
            if "next_step" in response:
                self.set_next_step(response["next_step"])
                
            return response
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return {
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "agent_type": self.agent_type,
                "status": "error"
            }
 

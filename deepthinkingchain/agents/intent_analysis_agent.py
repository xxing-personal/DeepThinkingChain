"""
Intent Analysis Agent for the Deep Thinking Chain.

This module contains the IntentAnalysisAgent class which is responsible for analyzing
user queries and extracting intent and parameters.
"""

import json
import time
import logging
from typing import Dict, Any, List, Optional

from deepthinkingchain.agents.agent_base import Agent
from deepthinkingchain.model import Model
from deepthinkingchain.constants import AgentType

# Set up logging
logger = logging.getLogger(__name__)

class IntentAnalysisAgent(Agent):
    """Agent for analyzing user input to determine intent and extract parameters."""
    
    def __init__(self, prompt_template_name: str = "intent_analysis", model_name: str = None):
        """Initialize the IntentAnalysisAgent.
        
        Args:
            prompt_template_name: Name of the template to use (defaults to "intent_analysis")
            model_name: Name of the model to use
        """
        # Initialize the base Agent class
        super().__init__(prompt_template_name=prompt_template_name, model_name=model_name)
        
        # Set the agent type
        self.agent_type = AgentType.USER_INTENT
        
        # Update metadata
        self.metadata.update({
            "agent_type": self.agent_type
        })
        
        # Initialize model for generating text
        self.model = Model(model=model_name)
    
    def _run(self, user_input: str) -> Dict[str, Any]:
        """Run the intent analysis on user input.
        
        Args:
            user_input: The user's input text to analyze
            
        Returns:
            Dictionary containing the analysis results
        """
        try:
            # Process the template
            prompt = self.process_template(user_input=user_input)
            
            # Generate analysis using the model
            response = self.model.generate_json(prompt=prompt)
            
            # Ensure we have the expected keys in the response
            if not isinstance(response, dict):
                logger.warning(f"Expected dict response, got {type(response)}")
                # Convert to dict if possible
                if hasattr(response, '__dict__'):
                    response = response.__dict__
                else:
                    response = {"intent": "unknown", "parameters": {}, "error": "Invalid response format"}
            
            if "intent" not in response:
                response["intent"] = "unknown"
            
            if "parameters" not in response:
                response["parameters"] = {}
            
            # Add timestamp
            response["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            return response
            
        except Exception as e:
            logger.error(f"Error during intent analysis: {str(e)}")
            return {
                "intent": "error",
                "parameters": {},
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """Public method to analyze user intent from input text.
        
        Args:
            user_input: The user's input text to analyze
            
        Returns:
            Dictionary containing the detected intent and parameters
        """
        return self.run(user_input) 
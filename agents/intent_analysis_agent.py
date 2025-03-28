"""
Intent Analysis Agent for the Deep Thinking Chain.

This module contains the IntentAnalysisAgent class which is responsible for analyzing
and classifying user intents to guide the financial analysis process.
"""

import time
import logging
import os
import sys
from typing import Dict, Any, Optional, List, Union


from agents.agent_base import Agent

# Import helper functions and required components
from model import Model
from memory import MemoryManager
from constants import AgentType

# Set up logging
logger = logging.getLogger(__name__)

class IntentAnalysisAgent(Agent):
    """Agent performing analysis of user intents to guide financial analysis."""
    
    def __init__(self, prompt_template_name: str = "intent_analysis", 
                 memory_manager: Optional[Union[str, MemoryManager]] = None, 
                 model_name: str = None):
        """Initialize the IntentAnalysisAgent with model configuration.
        
        Args:
            prompt_template_name: The template to use for analysis. Defaults to "intent_analysis".
            memory_manager: Optional memory manager for saving agent results
            model_name: The model to use for analysis.
        """
        # Initialize the base Agent class
        super().__init__(prompt_template_name=prompt_template_name, 
                         memory_manager=memory_manager, 
                         model_name=model_name)
        
        # Set the agent type
        self.agent_type = AgentType.PLANNING
        
        # Update metadata
        self.metadata.update({
            "agent_type": self.agent_type
        })
        
        # Initialize model for generating text
        self.model = Model(model=model_name)
    
    def _run(self, user_query: str) -> Dict[str, Any]:
        """Run the intent analysis agent to determine the user's financial analysis intent.
        
        Args:
            user_query: The user's query or request
            
        Returns:
            A dictionary containing the analysis results
        """
        try:
            # Process the template with the user query
            prompt = self.process_template(user_query=user_query)
            
            # Use the Model class to analyze the intent
            response = self.model.generate_json(prompt=prompt)
            
            # Add user query to the response
            result = response
            result['user_query'] = user_query
            result['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
            result['status'] = 'success'
            
            # Add a summary for the result
            if 'primary_intent' in result:
                result['summary'] = f"Analyzed user intent: {result.get('primary_intent', 'financial_analysis')}"
            else:
                result['summary'] = f"Analyzed query: {user_query[:50]}..."
                
            return result
                
        except Exception as e:
            logger.error(f"Error during intent analysis: {str(e)}")
            
            # Return an error result
            return {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "status": "failed",
                "user_query": user_query
            }
    
    def analyze_intent(self, user_query: str) -> Dict[str, Any]:
        """Public method to analyze a user query (wrapper around run).
        
        Args:
            user_query: The user's query or request
            
        Returns:
            A dictionary containing the analysis results
        """
        return self.run(user_query)
    
    def _format_response_to_str(self, response: Dict[str, Any]) -> str:
        """Format the response to a human-readable string.
        
        Args:
            response: The response from the model
            
        Returns:
            A formatted string representation of the response
        """
        return f"The goal for the deep research is {response['user_query']}\n" + response.get('intent_analysis', '')

 

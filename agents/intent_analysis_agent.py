"""
Intent Analysis Agent for the Deep Thinking Chain.

This module contains the IntentAnalysisAgent class which is responsible for analyzing
and classifying user intents to guide the financial analysis process.
"""

import json
import os
import time
import re
from typing import Dict, Any, Optional, List, Union, Tuple
from dotenv import load_dotenv

# Import the prompt manager and helper functions
from prompts.prompt_manager import PromptManager
from prompts.prompt_template import PromptTemplate

# Import the Model class
from model import Model

# Import the MemoryManager class
from memory import MemoryManager, Question
from constants import AgentType

# Load environment variables
load_dotenv()

# Initialize the prompt manager with both templates and template directories
PROMPTS_DIR = os.path.dirname(os.path.dirname(__file__))
prompt_manager = PromptManager(PROMPTS_DIR)

class IntentAnalysisAgent:
    """Agent performing analysis of user intents to guide financial analysis."""
    
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", template_name: str = "intent_analysis"):
        """Initialize the IntentAnalysisAgent with model configuration.
        
        Args:
            model_name: The model to use for analysis. Defaults to "gpt-3.5-turbo".
            template_name: The template to use for analysis. Defaults to "intent_analysis".
        """
        # Initialize the Model class
        self.model = Model(model=model_name)
        self.model_name = model_name
        
        # Use a default template if the specified one doesn't exist
        self.template_name = template_name
        self.template = prompt_manager.get_template(template_name)
        
        # Create a simple default template if none exists
        if not self.template:
            self._create_default_template()
    
    def analyze_intent(self, user_query: str, memory: Optional[MemoryManager] = None) -> Dict[str, Any]:
        """Analyze a user query to determine their financial analysis intent.
        
        Args:
            user_query: The user's query or request
            memory: Optional MemoryManager instance to store results
            
        Returns:
            A dictionary containing the analysis results
        """
            # Instead of using the template's format method, construct the prompt directly
        prompt = self.template.format(user_query=user_query)
            
            
            # Use the Model class to analyze the intent
        response = self.model.generate_json(
                prompt=prompt
        )
        response['user_query'] = user_query
        if 'follow_up_questions' in response:
            pass
            
        
    def _format_response_to_str(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format the response to a string.
        
        Args:
            response: The response from the model
        """
        return f"The goal for the deep research is {response['user_query']}\n" + response['intent_analysis']

    def _save_to_memory(self, memory: MemoryManager, intent_data: Dict[str, Any]) -> None:
        """Save intent analysis results to memory.
        
        Args:
            memory: MemoryManager instance
            intent_data: Intent analysis results
        """
        # Add the intent analysis as a new iteration in memory
        iteration_data = {
            "type": IterationType.PLANNING.value,
            "timestamp": intent_data["timestamp"],
            "intent_analysis": intent_data,
            "summary": f"Analyzed user intent: {intent_data.get('primary_intent', 'financial_analysis')}"
        }
        
        memory.add_iteration(AgentType.PLANNING, iteration_data)
    
 

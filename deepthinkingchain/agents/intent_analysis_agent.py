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
    
    def __init__(self, prompt_template_name: str = "intent_analysis", model_name: str = "anthropic/claude-3-opus-20240229", memory_manager=None):
        """Initialize the IntentAnalysisAgent.
        
        Args:
            prompt_template_name: Name of the template to use (defaults to "intent_analysis")
            model_name: Name of the model to use
            memory_manager: Optional memory manager for saving agent results
        """
        # Initialize the base Agent class
        super().__init__(prompt_template_name=prompt_template_name, model_name=model_name, memory_manager=memory_manager)
        
        # Set the agent type
        self.agent_type = AgentType.USER_INTENT
        
        # Set the next step for this agent type
        self.set_next_step("planning")
        
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
            # Store user input in memory
            if self.memory_manager:
                self.memory_manager.update_memory({"user_intent": user_input})
            
            # Process the template
            prompt = self.process_template(user_input=user_input)
            logger.debug(f"Generated prompt: {prompt}")
            
            # Generate analysis using the model
            logger.debug(f"Calling model.generate_json with prompt: {prompt}")
            response = self.model.generate_json(prompt=prompt)
            logger.debug(f"Raw model response: {response}")
            
            # Handle error responses
            if isinstance(response, dict) and "error" in response:
                logger.error(f"Model returned error: {response['error']}")
                return {
                    "intent": "error",
                    "parameters": {},
                    "required_tools": [],
                    "confidence": 0.0,
                    "next_step": "planning",
                    "error": response["error"],
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # Ensure we have the expected keys in the response
            if not isinstance(response, dict):
                logger.warning(f"Expected dict response, got {type(response)}: {response}")
                # Convert to dict if possible
                if hasattr(response, '__dict__'):
                    response = response.__dict__
                    logger.debug(f"Converted response to dict: {response}")
                else:
                    response = {"intent": "unknown", "parameters": {}, "error": "Invalid response format"}
            
            # Create a default response structure
            result = {
                "intent": "unknown",
                "parameters": {},
                "required_tools": [],
                "confidence": 0.0,
                "next_step": "planning",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Update with any valid fields from the response
            if isinstance(response.get("intent"), str):
                result["intent"] = response["intent"]
            else:
                logger.warning(f"Invalid intent in response: {response.get('intent')}")
            
            if isinstance(response.get("parameters"), dict):
                result["parameters"] = response["parameters"]
            else:
                logger.warning(f"Invalid parameters in response: {response.get('parameters')}")
            
            if isinstance(response.get("required_tools"), list):
                result["required_tools"] = response["required_tools"]
            else:
                logger.warning(f"Invalid required_tools in response: {response.get('required_tools')}")
            
            if isinstance(response.get("confidence"), (int, float)):
                result["confidence"] = float(response["confidence"])
            else:
                logger.warning(f"Invalid confidence in response: {response.get('confidence')}")
            
            if isinstance(response.get("next_step"), str):
                result["next_step"] = response["next_step"]
                self.set_next_step(response["next_step"])
            else:
                logger.warning(f"Invalid next_step in response: {response.get('next_step')}")
            
            logger.info(f"Intent analysis result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error during intent analysis: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception args: {e.args}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "intent": "error",
                "parameters": {},
                "required_tools": [],
                "confidence": 0.0,
                "next_step": "planning",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

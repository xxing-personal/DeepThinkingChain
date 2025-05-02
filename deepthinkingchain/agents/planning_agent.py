"""
Planning Agent for the Deep Thinking Chain.

This module contains the PlanningAgent class which is responsible for
determining next steps in the analysis workflow.
"""

import json
import os
import time
import logging
import re
from typing import Dict, Any, List, Optional, Union

from deepthinkingchain.agents.agent_base import Agent
from deepthinkingchain.prompts.prompt_template import format_data_for_prompt
from deepthinkingchain.memory import MemoryManager
from deepthinkingchain.model import Model
from deepthinkingchain.constants import AgentType
from deepthinkingchain.tools.tool_manager import ToolManager

# Set up logging
logger = logging.getLogger(__name__)

class PlanningAgent(Agent):
    """Agent for planning next steps in the analysis workflow."""
    
    def __init__(self, prompt_template_name: str = "planning", model_name: str = "anthropic/claude-3-opus-20240229", memory_manager=None):
        """Initialize the PlanningAgent.
        
        Args:
            prompt_template_name: Name of the template to use (defaults to "planning")
            model_name: Name of the model to use
            memory_manager: Optional memory manager for saving agent results
        """
        # Initialize the base Agent class
        super().__init__(prompt_template_name=prompt_template_name, model_name=model_name, memory_manager=memory_manager)
        
        # Set the agent type
        self.agent_type = AgentType.PLANNING
        
        # Initialize available tools
        self.available_tools = [
            "stock_data_fetcher",
            "technical_analysis",
            "fundamental_analysis",
            "news_analysis",
            "sentiment_analysis"
        ]
        
        # Update metadata
        self.metadata.update({
            "agent_type": self.agent_type
        })
        
        # Initialize model for generating text
        self.model = Model(model=model_name)
        
        # Store tool manager for access to tools
        self.tool_manager = ToolManager()
        
        # get existing completeness percentage
        if self.memory_manager is not None:
            self.initial_completeness_percent = self.memory_manager.get_completeness_percent()
        else:
            self.initial_completeness_percent = 0.0
    
    def _run(self, user_input: str) -> Dict[str, Any]:
        """Run the planning process.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Dictionary containing the planning results
        """
        try:
            # Get the last result from memory
            last_result = self.memory_manager.get_latest_iteration() if self.memory_manager else None
            logger.debug(f"Last result from memory: {last_result}")
            
            # Process the template
            prompt = self.process_template(last_result=last_result, tools=self.available_tools)
            logger.debug(f"Generated prompt: {prompt}")
            
            # Generate plan using the model
            logger.debug(f"Calling model.generate_json with prompt: {prompt}")
            response = self.model.generate_json(prompt=prompt)
            logger.debug(f"Raw model response: {response}")
            
            # Handle error responses
            if isinstance(response, dict) and "error" in response:
                logger.error(f"Model returned error: {response['error']}")
                return {
                    "next_action": "error",
                    "rational": response["error"],
                    "question": [],
                    "completeness_percent": 0.0,
                    "required_tools": [],
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
                    response = {
                        "next_action": "error",
                        "rational": "Invalid response format",
                        "question": [],
                        "completeness_percent": 0.0,
                        "required_tools": []
                    }
            
            # Create a default response structure
            result = {
                "next_action": "error",
                "rational": "",
                "question": [],
                "completeness_percent": 0.0,
                "required_tools": [],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Update with any valid fields from the response
            if isinstance(response.get("next_action"), str):
                result["next_action"] = response["next_action"]
            else:
                logger.warning(f"Invalid next_action in response: {response.get('next_action')}")
            
            if isinstance(response.get("rational"), str):
                result["rational"] = response["rational"]
            else:
                logger.warning(f"Invalid rational in response: {response.get('rational')}")
            
            if isinstance(response.get("question"), list):
                result["question"] = response["question"]
            else:
                logger.warning(f"Invalid question in response: {response.get('question')}")
            
            if isinstance(response.get("completeness_percent"), (int, float)):
                result["completeness_percent"] = float(response["completeness_percent"])
            else:
                logger.warning(f"Invalid completeness_percent in response: {response.get('completeness_percent')}")
            
            if isinstance(response.get("required_tools"), list):
                result["required_tools"] = response["required_tools"]
            else:
                logger.warning(f"Invalid required_tools in response: {response.get('required_tools')}")
            
            # Update next step based on next_action
            if result["next_action"] == "finish":
                self.set_next_step("summarize")
            elif result["next_action"] == "tool":
                self.set_next_step("tool_execution")
            elif result["next_action"] == "analysis":
                self.set_next_step("analysis")
            else:
                self.set_next_step("planning")
            
            logger.info(f"Planning result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error during planning: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception args: {e.args}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "next_action": "error",
                "rational": str(e),
                "question": [],
                "completeness_percent": 0.0,
                "required_tools": [],
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def set_next_step(self, step: str) -> None:
        """Set the next step in the analysis workflow.
        
        Args:
            step: The name of the next step
        """
        self.memory_manager.set_next_step(step)
    
    def plan_next(self) -> Dict[str, Any]:
        """Public method to plan the next steps in the analysis workflow.
        
        Returns:
            Dictionary containing the planning results
        """
        return self.run()
    
   
    
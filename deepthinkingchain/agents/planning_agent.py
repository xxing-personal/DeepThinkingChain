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
    
    def __init__(self, prompt_template_name: str = "planning", 
                 memory_manager: Optional[Union[str, MemoryManager]] = None,
                 tool_manager: Optional[ToolManager] = None,
                 model_name: str = None):
        """Initialize the PlanningAgent.
        
        Args:
            prompt_template_name: Name of the template to use (defaults to "planning")
            memory_manager: Optional memory manager for saving agent results
            tool_manager: Optional tool manager for handling tools
            model_name: Name of the model to use
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
        self.model = Model(model_name)
        
        # Store tool manager for access to tools
        self.tool_manager = tool_manager
        
        # Initialize iteration counter
        self.iteration = 0
        
        # get existing completeness percentage
        if self.memory_manager is not None:
            self.initial_completeness_percent = self.memory_manager.get_completeness_percent()
        else:
            self.initial_completeness_percent = 0.0
    
    def _run(self, last_step_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the planning process to determine next steps.
        
        Args:
            last_step_result: The results from the previous step (usually analysis)
            
        Returns:
            Dictionary containing the planning results
        """
        try:
            self.iteration += 1
            # Get tool descriptions using the tool manager
            tool_descriptions = {}
            if self.tool_manager:
                tool_descriptions = self.tool_manager.get_tool_descriptions()
            
            # Add tool descriptions and last step results to template parameters
            template_params = {
                "tools": tool_descriptions,
                "last_result": last_step_result
            }
                
            # Process the template with parameters
            prompt = self.process_template(**template_params)
            
            # Use the Model class to generate the plan
            response = self.model.generate(
                prompt=prompt,
            )
            
            # Parse the response
            return self._parse_response(response)
                
        except Exception as e:
            logger.error(f"Error during planning: {str(e)}")
            
            # Return an error result
            return {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "status": "failed",
                "continue_analysis": False,
                "reasoning": f"Error occurred: {str(e)}",
                "completion_percentage": self.initial_completeness_percent
            }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the response from the model into a structured format.
        
        Args:
            response: The string response from the model
            
        Returns:
            A dictionary containing the structured planning results
        """
        # Initialize default result structure
        result = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "continue_analysis": True,
            "reasoning": "No reasoning provided",
            "questions": [],
            "next_action": "None",
            "status": "success",
            "completion_percentage": getattr(self, 'initial_completeness_percent', 0)
        }
        
        try:
            # Try to extract and parse JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}')
            
            if json_start != -1 and json_end != -1:
                # Try to parse the JSON
                try:
                    json_str = response[json_start:json_end+1]
                    parsed_data = json.loads(json_str)
                    
                    # Extract content (either from "result" field or the whole response)
                    content = parsed_data.get("result", parsed_data)
                    
                    # Update result with parsed data
                    result.update({
                        "continue_analysis": content.get("next_action", "") != "finish",
                        "reasoning": content.get("rational", content.get("thinking", result["reasoning"])),
                        "questions": content.get("question", []),
                        "next_action": content.get("next_action", "None"),
                        "completion_percentage": content.get("completeness_percent", result["completion_percentage"])
                    })
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON: {str(e)}")
                    result.update({
                        "reasoning": "Fallback planning logic due to JSON parsing error",
                        "status": "partial_success",
                        "raw_response": response
                    })
            else:
                # No JSON found in the response
                logger.warning("No JSON content found in response")
                result.update({
                    "reasoning": "Fallback planning logic due to missing JSON content",
                    "status": "partial_success",
                    "raw_response": response
                })
                
        except Exception as e:
            # General exception handling
            logger.error(f"Error parsing response: {str(e)}")
            result.update({
                "error": f"Failed to parse response: {str(e)}",
                "raw_response": response,
                "status": "failed",
                "reasoning": f"Error parsing response: {str(e)}"
            })
        
        # Save result to memory if available
        if hasattr(self, 'memory_manager') and self.memory_manager is not None:
            try:
                self.memory_manager.add_iteration(self.agent_type, {
                    "planning_result": result,
                    "timestamp": result["timestamp"],
                    "agent_type": self.agent_type,
                    **({"error": result["error"]} if "error" in result else {})
                })
                logger.info(f"Added {result['status']} planning result to memory")
            except Exception as mem_err:
                logger.error(f"Failed to update memory with result: {str(mem_err)}")
        
        # Set the next step based on the planning output
        next_action = result.get("next_action", "").lower()
        continue_analysis = result.get("continue_analysis", True)
        
        if not continue_analysis or next_action == "finish":
            # If analysis is complete, set next step to summarization
            self.set_next_step("summary")
        else:
            # If analysis should continue, set appropriate next step based on next_action
            if next_action in ["tool", "tools"]:
                self.set_next_step("tool")
            else:
                # Default to analysis for continuing the process
                self.set_next_step("analysis")
                
        logger.info(f"Planning agent set next step to: {self.get_next_step()}")
        
        return result
    
    def plan_next(self) -> Dict[str, Any]:
        """Public method to plan the next steps in the analysis workflow.
        
        Returns:
            Dictionary containing the planning results
        """
        return self.run()
    
   
    
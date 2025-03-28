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
        
        # Update metadata
        self.metadata.update({
            "agent_type": self.agent_type
        })
        
        # Initialize model for generating text
        self.model = Model(model=model_name)
    
    def _run(self, last_step_result: Union[str, Dict[str, Any], None] = None) -> Dict[str, Any]:
        """Run the analysis agent to analyze financial data and extract insights.
        
        Args:
            last_step_result: Data from the last step to be analyzed, either as formatted string or dict
            
        Returns:
            A dictionary containing the analysis results
        """
        try:
            # Process the template using additional parameters from last step result
            additional_params = {}
            if last_step_result is not None:
                if isinstance(last_step_result, dict):
                    additional_params["last_step_result"] = format_data_for_prompt(last_step_result)
                else:
                    additional_params["last_step_result"] = str(last_step_result)
            else:
                additional_params["last_step_result"] = "No previous results available."
                
            # Process the template
            prompt = self.process_template(**additional_params)
            
            # Use the Model class to analyze the data
            response = self.model.generate(
                prompt=prompt,
            )
            
            # Parse the response
            return self._parse_response(response)
                
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            
            # Return an error result
            return {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "status": "failed"
            }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the response from the model into a structured format that matches the expected template.
        
        Args:
            response: The string response from the model
            
        Returns:
            A dictionary containing the structured analysis results
        """
        try:
            # Look for JSON content in the response
            json_start = response.find('{')
            json_end = response.rfind('}')
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end+1]
                try:
                    parsed_data = json.loads(json_str)
                    
                    # Extract the main result content
                    if "result" in parsed_data:
                        result = parsed_data["result"]
                    else:
                        result = parsed_data
                                        
                    # Check for completeness percentage and ensure it's a number
                    if "completeness_percent" in result:
                        try:
                            # Convert string percentage to number if needed
                            if isinstance(result["completeness_percent"], str):
                                # Remove % sign if present
                                result["completeness_percent"] = result["completeness_percent"].replace("%", "").strip()
                                result["completeness_percent"] = float(result["completeness_percent"])
                        except ValueError:
                            logger.warning("Could not parse completeness_percent as a number")
                            result["completeness_percent"] = 0
                    
                    # Update memory with this result if a memory manager is available
                    if hasattr(self, 'memory_manager') and self.memory_manager is not None:
                        self.memory_manager.add_iteration(self.agent_type, {
                            "analysis_result": result,
                            "timestamp": result["timestamp"],
                            "agent_type": self.agent_type
                        })
                        logger.info("Added analysis result to memory")
                    
                    return result
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON: {str(e)}")
                    # Fall back to text parsing
            
            # If JSON parsing failed, create a basic structure
            logger.warning("JSON parsing failed, creating basic structure")
            result = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "partial_success",
                "raw_response": response,
                "thinking": "Analysis completed, but structured output was not available.",
                "summary": response[:500] + "..." if len(response) > 500 else response,
                "completeness_percent": 0,
                "questions": []
            }
            
            # Update memory with this partial result if a memory manager is available
            if hasattr(self, 'memory_manager') and self.memory_manager is not None:
                self.memory_manager.add_iteration(self.agent_type, {
                    "analysis_result": result,
                    "timestamp": result["timestamp"],
                    "agent_type": self.agent_type
                })
                logger.info("Added partial analysis result to memory")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            error_result = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": f"Failed to parse response: {str(e)}",
                "raw_response": response,
                "status": "failed"
            }
            
            # Still try to update memory with error information
            if hasattr(self, 'memory_manager') and self.memory_manager is not None:
                try:
                    self.memory_manager.add_iteration(self.agent_type, {
                        "analysis_result": error_result,
                        "timestamp": error_result["timestamp"],
                        "agent_type": self.agent_type,
                        "error": str(e)
                    })
                    logger.info("Added error information to memory")
                except Exception as mem_err:
                    logger.error(f"Failed to update memory with error: {str(mem_err)}")
            
            return error_result
                
    def analyze(self, data: Dict[str, Any], focus: str = "general", symbol: str = None) -> Dict[str, Any]:
        """Public method to analyze financial data with a specific focus.
        
        Args:
            data: Dictionary containing the financial data to analyze
            focus: The focus area of the analysis (e.g., "financial_performance", "competitive_analysis")
            symbol: Optional stock symbol being analyzed
            
        Returns:
            A dictionary containing the analysis results
        """
        try:
            # Add focus and symbol to the data if provided
            if focus:
                data["focus"] = focus
            if symbol:
                data["symbol"] = symbol
                
            # Run the analysis
            results = self.run(data)
            
            # Make sure timestamp is in the results
            if "timestamp" not in results:
                results["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
                
            # Make sure analysis_type is set based on focus
            if "analysis_type" not in results:
                results["analysis_type"] = focus
                
            # Make sure symbol is included 
            if symbol and "symbol" not in results:
                results["symbol"] = symbol
                
            return results
            
        except Exception as e:
            logger.error(f"Error during analyze call: {str(e)}")
            
            # Return basic error structure
            return {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "analysis_type": focus,
                "symbol": symbol,
                "error": str(e),
                "status": "failed"
            } 
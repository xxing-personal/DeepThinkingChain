"""
Tool Agent for the Deep Thinking Chain.

This module contains the ToolAgent class which is responsible for executing 
tools and retrieving external data.
"""

import logging
import json
import time
from typing import Dict, Any, Optional, List, Union

from deepthinkingchain.agents.agent_base import Agent
from deepthinkingchain.constants import AgentType
# Set up logging
logger = logging.getLogger(__name__)
class ToolAgent(Agent):
    """Agent responsible for managing and executing a specific tool."""
    
    def __init__(self, 
                 tools_name: str = None,
                 tools_params: Dict[str, Any] = None,
                 ):
        """Initialize the ToolAgent with a specific tool.
        
        Args:
            prompt_template_name: The template to use for tool execution.
            memory_manager: Optional memory manager for saving agent results
            model_name: The model to use (not needed for tool agent).
            tools_name: Name of the specific tool to load.
            tools_params: Parameters to use with the tool.
        """
        # Initialize the base Agent class
        super().__init__()
        
        # Set the agent type
        self.agent_type = AgentType.TOOL
        
        # Set the next step for this agent type
        self.set_next_step("analysis")
        
        # Update metadata
        self.metadata.update({
            "agent_type": self.agent_type
        })
        
        # Store tool parameters
        self.tool_params = tools_params or {}
        
        # Load the specific tool if provided
        if tools_name:
            self._load_specific_tool(tools_name)
        else:
            # Keep existing functionality if no specific tool is requested
            self.tool_categories = {}
            self.default_tools = {}
            self._load_tools()
    
    def _load_specific_tool(self, tool_name: str):
        """Load a specific tool by name.
        
        Args:
            tool_name: The name of the tool to load
        """
        try:
            # Import the register_tools function
            from register_tools import register_tools
            
            # Get the tool manager instance with registered tools
            tool_manager = register_tools()
            
            # Get all tools by name
            all_tools = tool_manager.get_tools_by_name()
            
            # Check if the requested tool exists
            if tool_name in all_tools:
                # Store only the requested tool
                self.tools = {tool_name: all_tools[tool_name]}
                logger.info(f"Loaded specific tool: {tool_name}")
                
                # Update metadata with tool information
                self.metadata.update({
                    "tool_name": tool_name,
                    "tool_params": self.tool_params
                })
            else:
                logger.error(f"Tool '{tool_name}' not found in registered tools.")
                available_tools = list(all_tools.keys())
                logger.error(f"Available tools: {available_tools}")
        except ImportError as e:
            logger.error(f"Error loading tool '{tool_name}': {e}")
            logger.error("Make sure the register_tools.py file is in your Python path.")
    
    def _load_tools(self):
        """Dynamically load all tool classes from the tools directory."""
        try:
            # Import the register_tools function
            from register_tools import register_tools
            
            # Get the tool manager instance with registered tools
            tool_manager = register_tools()
            
            # Get all registered tools
            self.tools = tool_manager.get_tools_by_name()
            self.tool_categories = tool_manager.get_tools_by_category()
            self.default_tools = tool_manager.get_default_tools()
            
            logger.info(f"Loaded {len(self.tools)} tools across {len(self.tool_categories)} categories.")
        except ImportError as e:
            logger.error(f"Error loading tools: {e}")
            logger.error("Make sure the register_tools.py file is in your Python path.")
    
    def _run(self, **kwargs) -> Dict[str, Any]:
        """Run the tool agent to execute the specified tool.
        
        Args:
            **kwargs: Additional parameters to pass to the tool (overrides init params)
            
        Returns:
            A dictionary containing the tool execution results
        """
        try:
            # If no tools loaded, return error
            if not self.tools:
                return {
                    "status": "failed",
                    "error": "No tools loaded. Please specify a valid tool name during initialization.",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # For single tool mode
            if len(self.tools) == 1:
                tool_name = list(self.tools.keys())[0]
                tool = self.tools[tool_name]
                
                # Combine parameters from initialization with any new parameters
                combined_params = {**self.tool_params, **kwargs}
                
                # Execute the tool
                tool_result = tool(**combined_params)
                
                # Format the result
                result = {
                    "tool_name": tool_name,
                    "parameters": combined_params,
                    "result": tool_result,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "success",
                    "summary": f"Executed tool '{tool_name}' with parameters"
                }
                
                return result
            
            # If multiple tools are loaded but no specific tool name provided in kwargs
            if "tool_name" not in kwargs:
                return {
                    "status": "failed",
                    "error": "Multiple tools loaded but no tool_name specified in parameters.",
                    "available_tools": list(self.tools.keys()),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # Extract tool name from kwargs and remove it from params
            tool_name = kwargs.pop("tool_name")
            
            # Check if the tool exists
            if tool_name not in self.tools:
                return {
                    "status": "failed",
                    "error": f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # Get the tool
            tool = self.tools[tool_name]
            
            # Execute the tool
            tool_result = tool(**kwargs)
            
            # Format the result
            result = {
                "tool_name": tool_name,
                "parameters": kwargs,
                "result": tool_result,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "success",
                "summary": f"Executed tool '{tool_name}' with {len(kwargs)} parameters"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool: {str(e)}")
            
            # Return an error result
            tool_name = list(self.tools.keys())[0] if len(self.tools) == 1 else kwargs.get("tool_name", "unknown")
            return {
                "tool_name": tool_name,
                "parameters": kwargs,
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "failed"
            }
    
    def list_tools(self) -> List[str]:
        """List all available tools.
        
        Returns:
            List of available tool names
        """
        return list(self.tools.keys())
    
    def list_categories(self) -> List[str]:
        """List all available tool categories.
        
        Returns:
            List of available tool categories
        """
        return list(getattr(self, 'tool_categories', {}).keys())
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """Get all tools in a specific category.
        
        Args:
            category: The category to get tools for
            
        Returns:
            List of tool names in the category
        """
        return getattr(self, 'tool_categories', {}).get(category, [])
    
    def get_tool_description(self, tool_name: str = None) -> str:
        """Get the description of a specific tool.
        
        Args:
            tool_name: Name of the tool. If None, uses the loaded tool.
            
        Returns:
            String description of the tool
        """
        if tool_name is None and len(self.tools) == 1:
            tool_name = list(self.tools.keys())[0]
            
        tool = self.tools.get(tool_name)
        if tool:
            return tool.description
        return f"No description available for tool '{tool_name}'"
    
    def get_tool_inputs(self, tool_name: str = None) -> Dict[str, Dict[str, Any]]:
        """Get the input parameters for a specific tool.
        
        Args:
            tool_name: Name of the tool. If None, uses the loaded tool.
            
        Returns:
            Dictionary of input parameters and their descriptions
        """
        if tool_name is None and len(self.tools) == 1:
            tool_name = list(self.tools.keys())[0]
            
        tool = self.tools.get(tool_name)
        if tool:
            return tool.inputs
        return {}
    
    def execute_tool(self, **kwargs) -> Dict[str, Any]:
        """Execute the loaded tool with the provided parameters.
        
        Args:
            **kwargs: Additional parameters to pass to the tool
            
        Returns:
            Dict containing the tool's response
        """
        return self.run(**kwargs)
    
    def execute_default_tool(self, category: str, **kwargs) -> Dict[str, Any]:
        """Execute the default tool for a category.
        
        Args:
            category: The category to execute the default tool for
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Dict containing the tool's response
        """
        # Check if the category has a default tool
        default_tools = getattr(self, 'default_tools', {})
        if category not in default_tools:
            return {
                "status": "failed",
                "error": f"No default tool for category '{category}'. Available categories: {list(default_tools.keys())}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Get the default tool name
        default_tool_name = default_tools[category]
        
        # Execute the default tool
        return self.execute_tool(tool_name=default_tool_name, **kwargs)
    
   
    def _format_response_to_str(self, response: Dict[str, Any]) -> str:
        """Format the response to a human-readable string.
        
        Args:
            response: The response from the tool execution
            
        Returns:
            A formatted string representation of the response
        """
        if 'error' in response:
            return f"Error executing tool: {response['error']}"
        
        tool_name = response.get('tool_name', 'unknown')
        result = response.get('result', {})
        
        return f"Tool '{tool_name}' execution result:\n{json.dumps(result, indent=2)}"

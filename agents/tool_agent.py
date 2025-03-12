import os
import importlib
import inspect
from typing import Dict, Any, Optional, List, Union, Callable, Type
import json
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class ToolAgent:
    """Agent responsible for managing and executing various tools."""
    
    def __init__(self):
        """Initialize the ToolAgent with tool registry."""
        self.tools = {}  # Dictionary to store tools by name
        self.tool_categories = {}  # Dictionary to store tools by category
        self.default_tools = {}  # Dictionary to store default tools for each category
        
        # Load tools from the tools directory
        self._load_tools()
    
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
            
            print(f"Loaded {len(self.tools)} tools across {len(self.tool_categories)} categories.")
        except ImportError as e:
            print(f"Error loading tools: {e}")
            print("Make sure the register_tools.py file is in your Python path.")
    
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
        return list(self.tool_categories.keys())
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """Get all tools in a specific category.
        
        Args:
            category: The category to get tools for
            
        Returns:
            List of tool names in the category
        """
        return self.tool_categories.get(category, [])
    
    def get_tool_description(self, tool_name: str) -> str:
        """Get the description of a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            String description of the tool
        """
        tool = self.tools.get(tool_name)
        if tool:
            return tool.description
        return f"No description available for tool '{tool_name}'"
    
    def get_tool_inputs(self, tool_name: str) -> Dict[str, Dict[str, Any]]:
        """Get the input parameters for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary of input parameters and their descriptions
        """
        tool = self.tools.get(tool_name)
        if tool:
            return tool.inputs
        return {}
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a specific tool by name with the provided parameters.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Dict containing the tool's response
            
        Raises:
            ValueError: If the tool is not found
        """
        # Check if the tool exists
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"}
        
        # Get the tool
        tool = self.tools[tool_name]
        
        try:
            # Execute the tool
            return tool(**kwargs)
        except Exception as e:
            return {"error": f"Error executing tool '{tool_name}': {str(e)}"}
    
    def execute_default_tool(self, category: str, **kwargs) -> Dict[str, Any]:
        """Execute the default tool for a category.
        
        Args:
            category: The category to execute the default tool for
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Dict containing the tool's response
            
        Raises:
            ValueError: If the category has no default tool
        """
        # Check if the category has a default tool
        if category not in self.default_tools:
            return {"error": f"No default tool for category '{category}'. Available categories: {list(self.default_tools.keys())}"}
        
        # Get the default tool name
        default_tool_name = self.default_tools[category]
        
        # Execute the default tool
        return self.execute_tool(default_tool_name, **kwargs)
    
    def get_tools_prompt(self) -> str:
        """Get a formatted prompt describing all available tools.
        
        Returns:
            String prompt describing all available tools
        """
        prompt = "Available tools:\n\n"
        
        for category in sorted(self.tool_categories.keys()):
            prompt += f"Category: {category}\n"
            
            for tool_name in sorted(self.tool_categories[category]):
                tool = self.tools[tool_name]
                prompt += f"  - {tool_name}: {tool.description}\n"
            
            prompt += "\n"
        
        return prompt


if __name__ == "__main__":
    import sys
    
    # Initialize the agent
    agent = ToolAgent()
    
    # Display available tools
    print(agent.get_tools_prompt())
    
    # Check if a tool name was provided
    if len(sys.argv) > 1:
        tool_name = sys.argv[1]
        
        # Check if the tool exists
        if tool_name in agent.list_tools():
            # Get the tool inputs
            inputs = agent.get_tool_inputs(tool_name)
            
            # Build the arguments
            kwargs = {}
            for i, (param_name, param_info) in enumerate(inputs.items(), 2):
                if param_info.get("required", False) and i < len(sys.argv):
                    kwargs[param_name] = sys.argv[i]
            
            # Execute the tool
            result = agent.execute_tool(tool_name, **kwargs)
            print(json.dumps(result, indent=2))
        else:
            print(f"Tool '{tool_name}' not found. Available tools: {agent.list_tools()}")
    else:
        print("Usage: python tool_agent.py <tool_name> [<arg1> <arg2> ...]")

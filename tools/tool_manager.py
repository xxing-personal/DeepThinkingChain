"""
Tool Manager for DeepThinkingChain.

This module contains the ToolManager class that manages all tools in the DeepThinkingChain project.
"""

from typing import Dict, List, Union, Any, Optional
import inspect
import os
import importlib.util
import sys

from tools.tool import Tool

class ToolManager:
    """
    A class to manage tools in the DeepThinkingChain project.
    
    The ToolManager keeps track of all available tools and provides methods to access them.
    It also supports setting default tools for different categories.
    """
    
    def __init__(self):
        """Initialize the ToolManager."""
        self.tools: Dict[str, Tool] = {}
        self.default_tools: Dict[str, str] = {}  # category -> tool_name
        
    def add_tool(self, tool: Tool):
        """
        Add a tool to the manager.
        
        Args:
            tool: The tool to add
        """
        self.tools[tool.name] = tool
        
    def get_tool_names(self) -> List[str]:
        """
        Get the names of all registered tools.
        
        Returns:
            List[str]: List of tool names
        """
        return list(self.tools.keys())
    
    def get_tool_by_name(self, name: str) -> Optional[Tool]:
        """
        Get a tool by its name.
        
        Args:
            name: The name of the tool to get
            
        Returns:
            Tool: The requested tool, or None if not found
        """
        return self.tools.get(name)
    
    def get_default_tool(self, category: str) -> Optional[Tool]:
        """
        Get the default tool for a category.
        
        Args:
            category: The category to get the default tool for
            
        Returns:
            Tool: The default tool for the category, or None if not set
        """
        tool_name = self.default_tools.get(category)
        if tool_name:
            return self.get_tool_by_name(tool_name)
        return None
    
    def set_default_tool(self, category: str, tool_name: str):
        """
        Set the default tool for a category.
        
        Args:
            category: The category to set the default tool for
            tool_name: The name of the tool to set as default
        """
        if tool_name in self.tools:
            self.default_tools[category] = tool_name
    
    def get_tools(self, names_or_categories: Union[str, List[str]]) -> Dict[str, Tool]:
        """
        Get tools by name or category.
        
        Args:
            names_or_categories: Tool name(s) or category(ies) to get
            
        Returns:
            Dict[str, Tool]: Dictionary of tools, keyed by name
        """
        if isinstance(names_or_categories, str):
            names_or_categories = [names_or_categories]
            
        result = {}
        
        for name_or_category in names_or_categories:
            # Check if it's a tool name
            tool = self.get_tool_by_name(name_or_category)
            if tool:
                result[name_or_category] = tool
                continue
                
            # Check if it's a category
            for tool_name, tool in self.tools.items():
                if tool.category == name_or_category:
                    result[tool_name] = tool
                    
        return result
    
    def get_tools_by_category(self, category: str) -> Dict[str, Tool]:
        """
        Get all tools in a specific category.
        
        Args:
            category: The category to get tools for
            
        Returns:
            Dict[str, Tool]: Dictionary of tools in the category, keyed by name
        """
        return {name: tool for name, tool in self.tools.items() if tool.category == category}
    
    def get_categories(self) -> List[str]:
        """
        Get all available categories.
        
        Returns:
            List[str]: List of unique categories
        """
        return list(set(tool.category for tool in self.tools.values()))
    
    def load_tools_from_directory(self, directory: str):
        """
        Load tools from Python files in a directory.
        
        Args:
            directory: The directory to load tools from
        """
        if not os.path.exists(directory):
            return
            
        for filename in os.listdir(directory):
            if not filename.endswith('.py') or filename == '__init__.py':
                continue
                
            module_path = os.path.join(directory, filename)
            module_name = os.path.splitext(filename)[0]
            
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None or spec.loader is None:
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # Find Tool subclasses in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and issubclass(obj, Tool) and 
                        obj is not Tool and not name.startswith('_')):
                        try:
                            tool = obj()
                            self.add_tool(tool)
                        except Exception as e:
                            print(f"Error loading tool {name} from {filename}: {e}")
                            
            except Exception as e:
                print(f"Error loading module {module_name}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool manager to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the tool manager
        """
        return {
            "tools": {name: tool.to_dict() for name, tool in self.tools.items()},
            "default_tools": self.default_tools,
            "categories": self.get_categories()
        }
    
    def get_tools_prompt(self) -> str:
        """
        Generate a prompt describing all available tools.
        
        Returns:
            str: A formatted string describing all tools
        """
        prompt = "# Available Tools\n\n"
        
        for category in sorted(self.get_categories()):
            category_tools = self.get_tools_by_category(category)
            if not category_tools:
                continue
                
            prompt += f"## {category.capitalize()} Tools\n\n"
            
            for tool_name in sorted(category_tools.keys()):
                tool = category_tools[tool_name]
                prompt += tool.tool_prompt() + "\n\n"
                
        return prompt


def main():
    """Example usage of the ToolManager."""
    # Create an instance of ToolManager
    manager = ToolManager()
    
    # Create a simple example tool
    class ExampleTool(Tool):
        name = "example_tool"
        description = "An example tool that adds two numbers."
        inputs = {
            "a": {"type": "int", "description": "First number", "required": True},
            "b": {"type": "int", "description": "Second number", "required": True}
        }
        output_type = "int"
        capabilities = "Can add two integers together."
        category = "math"
        
        def forward(self, a: int, b: int) -> int:
            return a + b
    
    # Add the tool to the manager
    manager.add_tool(ExampleTool())
    
    # Create a tool from a function
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return a * b
    
    multiply_tool = Tool.from_function(
        multiply,
        name="multiply_tool",
        description="A tool that multiplies two numbers.",
        category="math",
        output_type="int"
    )
    
    manager.add_tool(multiply_tool)
    
    # Set default tool for math category
    manager.set_default_tool("math", "multiply_tool")
    
    # Print available tools
    print(manager.get_tools_prompt())
    
    # Use a tool
    example_tool = manager.get_tool_by_name("example_tool")
    if example_tool:
        result = example_tool(a=5, b=3)
        print(f"5 + 3 = {result}")
    
    # Use the default math tool
    default_math_tool = manager.get_default_tool("math")
    if default_math_tool:
        result = default_math_tool(a=5, b=3)
        print(f"5 * 3 = {result}")


if __name__ == "__main__":
    main() 
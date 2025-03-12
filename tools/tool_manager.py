"""
Tool Manager for DeepThinkingChain.

This module contains the ToolManager class for managing tools.
"""

from typing import Dict, Any, List, Optional, Type
from tools.tool import Tool

class ToolManager:
    """Manager for registering and retrieving tools."""
    
    def __init__(self):
        """Initialize the tool manager."""
        self.tools_by_name = {}  # Dict[str, Tool]
        self.tools_by_category = {}  # Dict[str, List[str]]
        self.default_tools = {}  # Dict[str, str]
    
    def add_tool(self, tool: Tool) -> None:
        """
        Register a tool with the manager.
        
        Args:
            tool: The tool to register
        """
        # Register by name
        self.tools_by_name[tool.name] = tool
        
        # Register by category
        if tool.category not in self.tools_by_category:
            self.tools_by_category[tool.category] = []
        
        if tool.name not in self.tools_by_category[tool.category]:
            self.tools_by_category[tool.category].append(tool.name)
    
    def get_tool_by_name(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            name: The name of the tool to get
            
        Returns:
            The tool, or None if not found
        """
        return self.tools_by_name.get(name)
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """
        Get all tools in a category.
        
        Args:
            category: The category to get tools for
            
        Returns:
            List of tool names in the category
        """
        return self.tools_by_category.get(category, [])
    
    def set_default_tool(self, category: str, tool_name: str) -> None:
        """
        Set the default tool for a category.
        
        Args:
            category: The category to set the default tool for
            tool_name: The name of the default tool
        """
        if tool_name not in self.tools_by_name:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        if category not in self.tools_by_category:
            self.tools_by_category[category] = []
        
        self.default_tools[category] = tool_name
    
    def get_default_tool(self, category: str) -> Optional[Tool]:
        """
        Get the default tool for a category.
        
        Args:
            category: The category to get the default tool for
            
        Returns:
            The default tool, or None if not found
        """
        if category not in self.default_tools:
            return None
        
        tool_name = self.default_tools[category]
        return self.get_tool_by_name(tool_name)
    
    def get_tools_by_name(self) -> Dict[str, Tool]:
        """
        Get all tools by name.
        
        Returns:
            Dict mapping tool names to tools
        """
        return self.tools_by_name
    
    def get_tools_by_category(self) -> Dict[str, List[str]]:
        """
        Get all tools by category.
        
        Returns:
            Dict mapping categories to lists of tool names
        """
        return self.tools_by_category
    
    def get_default_tools(self) -> Dict[str, str]:
        """
        Get all default tools.
        
        Returns:
            Dict mapping categories to default tool names
        """
        return self.default_tools
    
    def get_tools_prompt(self) -> str:
        """
        Get a formatted prompt describing all available tools.
        
        Returns:
            String prompt describing all available tools
        """
        prompt = "Available tools:\n\n"
        
        for category in sorted(self.tools_by_category.keys()):
            prompt += f"Category: {category}\n"
            
            for tool_name in sorted(self.tools_by_category[category]):
                tool = self.tools_by_name[tool_name]
                prompt += f"  - {tool_name}: {tool.description}\n"
            
            if category in self.default_tools:
                prompt += f"  Default: {self.default_tools[category]}\n"
            
            prompt += "\n"
        
        return prompt 
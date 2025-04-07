"""
Base Tool class for DeepThinkingChain.

This module contains the base Tool class that all tools should inherit from.
"""

from typing import Dict, Any, Callable, Optional, Type, get_type_hints
import inspect

class Tool:
    """
    A base class for the functions used by the DeepThinkingChain agents. Subclass this and implement the `forward` method as well as the
    following class attributes:

    - **name** (`str`) -- A performative name for your tool.
    - **description** (`str`) -- A short description of what your tool does, the inputs it expects and the output(s) it will return.
    - **inputs** (`Dict[str, Dict[str, Union[str, type, bool]]]`) -- A dict describing the expected inputs.
    - **output_type** (`str`) -- A string indicating the type of output returned by the tool.
    - **capabilities** (`str`) -- A description of the tool's capabilities.
    """

    name = "base_tool"  # Tool name (should be overridden by subclasses)
    description = "Base tool class"  # Tool description (should be overridden by subclasses)
    inputs = {}  # Tool input parameters (should be overridden by subclasses)
    output_type = "any"  # Tool output type (should be overridden by subclasses)
    capabilities = "Base tool capabilities"  # Tool capabilities (should be overridden by subclasses)
    category = "misc"  # Tool category (should be overridden by subclasses)

    def __init__(self):
        """Initialize the tool."""
        # Validate that required attributes are set
        if self.name == "base_tool":
            raise ValueError("Tool name must be set")
        if self.description == "Base tool class":
            raise ValueError("Tool description must be set")
        if not self.inputs:
            raise ValueError("Tool inputs must be set")
        if self.output_type == "any":
            raise ValueError("Tool output type must be set")
        if self.capabilities == "Base tool capabilities":
            raise ValueError("Tool capabilities must be set")
        if self.category == "misc":
            raise ValueError("Tool category must be set")

    def __call__(self, **kwargs) -> Any:
        """
        Call the tool with the given parameters.
        
        Args:
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Any: The result of the tool execution
        """
        # Validate required parameters
        for param_name, param_info in self.inputs.items():
            if param_info.get("required", False) and param_name not in kwargs:
                raise ValueError(f"Required parameter '{param_name}' not provided")
        
        # Call the forward method
        return self.forward(**kwargs)

    def forward(self, **kwargs) -> Any:
        """
        Execute the tool with the given parameters.
        
        This method should be overridden by subclasses.
        
        Args:
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Any: The result of the tool execution
        """
        raise NotImplementedError("Tool.forward() must be implemented by subclasses")

    def tool_prompt(self) -> str:
        """
        Generate a prompt for this tool.
        
        Returns:
            str: A formatted string describing the tool
        """
        prompt = f"### {self.name}\n\n"
        prompt += f"{self.description}\n\n"
        
        if self.inputs:
            prompt += "**Inputs:**\n\n"
            for param_name, param_info in self.inputs.items():
                required = " (required)" if param_info.get("required", False) else ""
                prompt += f"- `{param_name}`: {param_info.get('description', '')}{required}\n"
            prompt += "\n"
        
        prompt += f"**Output Type:** {self.output_type}\n\n"
        prompt += f"**Capabilities:** {self.capabilities}\n"
        
        return prompt

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the tool
        """
        return {
            "name": self.name,
            "description": self.description,
            "inputs": self.inputs,
            "output_type": self.output_type,
            "capabilities": self.capabilities,
            "category": self.category
        }

    @classmethod
    def from_function(cls, func: Callable, name: str, description: str, category: str, output_type: str) -> 'Tool':
        """
        Create a tool from a function.
        
        Args:
            func: The function to create a tool from
            name: The name of the tool
            description: The description of the tool
            category: The category of the tool
            output_type: The output type of the tool
            
        Returns:
            Tool: A new tool instance
        """
        # Get function signature
        sig = inspect.signature(func)
        
        # Get function docstring
        doc = inspect.getdoc(func) or ""
        
        # Get function type hints
        type_hints = get_type_hints(func)
        
        # Create inputs dictionary
        inputs = {}
        for param_name, param in sig.parameters.items():
            if param.kind == param.POSITIONAL_ONLY:
                continue
            
            param_type = type_hints.get(param_name, Any).__name__
            required = param.default == param.empty
            
            inputs[param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}",
                "required": required
            }
        
        # Create a new Tool subclass
        tool_cls = type(name, (cls,), {
            "name": name,
            "description": description,
            "inputs": inputs,
            "output_type": output_type,
            "capabilities": doc,
            "category": category,
            "forward": lambda self, **kwargs: func(**kwargs)
        })
        
        # Create and return an instance of the new class
        return tool_cls() 
"""
Base Tool class for DeepThinkingChain.

This module contains the base Tool class that all tools in the DeepThinkingChain project should inherit from.
"""

from typing import Dict, Union, Any, List, Optional, Callable
import inspect
import json

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

    name: str = ""
    description: str = ""
    inputs: Dict[str, Dict[str, Union[str, type, bool]]] = {}
    output_type: str = ""
    capabilities: str = ""
    category: str = "general"

    def __init__(self, *args, **kwargs):
        """Initialize the tool."""
        self.setup()

    def setup(self):
        """
        Setup method called during initialization.
        Override this method to perform any necessary setup for your tool.
        """
        pass

    def forward(self, *args, **kwargs) -> Any:
        """
        The main implementation of the tool. Override this method in your subclass.
        
        Returns:
            Any: The result of the tool's operation
        """
        raise NotImplementedError("Subclasses must implement the forward method")

    def __call__(self, *args, sanitize_inputs_outputs: bool = False, **kwargs) -> Any:
        """
        Call the tool with the given arguments.
        
        Args:
            *args: Positional arguments to pass to the forward method
            sanitize_inputs_outputs: Whether to sanitize inputs and outputs
            **kwargs: Keyword arguments to pass to the forward method
            
        Returns:
            Any: The result of the tool's operation
        """
        # Validate inputs if needed
        if sanitize_inputs_outputs:
            # Implement input sanitization logic here
            pass
        
        # Call the forward method
        result = self.forward(*args, **kwargs)
        
        # Sanitize outputs if needed
        if sanitize_inputs_outputs:
            # Implement output sanitization logic here
            pass
        
        return result

    def tool_prompt(self) -> str:
        """
        Generate a prompt describing how to use this tool.
        
        Returns:
            str: A formatted string describing the tool's usage
        """
        prompt = f"Tool: {self.name}\n"
        prompt += f"Description: {self.description}\n"
        
        if self.inputs:
            prompt += "Inputs:\n"
            for param_name, param_info in self.inputs.items():
                param_type = param_info.get("type", "Any")
                param_desc = param_info.get("description", "")
                required = param_info.get("required", True)
                req_str = "required" if required else "optional"
                prompt += f"  - {param_name} ({param_type}, {req_str}): {param_desc}\n"
        
        prompt += f"Output: {self.output_type}\n"
        prompt += f"Capabilities: {self.capabilities}\n"
        
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
    def from_function(cls, func: Callable, name: Optional[str] = None, description: Optional[str] = None, 
                     category: str = "general", output_type: Optional[str] = None) -> 'Tool':
        """
        Create a Tool from a function.
        
        Args:
            func: The function to convert to a tool
            name: Optional name for the tool (defaults to function name)
            description: Optional description (defaults to function docstring)
            category: Category for the tool
            output_type: Output type description
            
        Returns:
            Tool: A Tool instance wrapping the function
        """
        class FunctionTool(cls):
            def forward(self, *args, **kwargs):
                return func(*args, **kwargs)
        
        tool = FunctionTool()
        tool.name = name or func.__name__
        tool.description = description or inspect.getdoc(func) or ""
        tool.category = category
        
        # Extract input parameters from function signature
        sig = inspect.signature(func)
        tool.inputs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
                
            param_type = "Any"
            if param.annotation != inspect.Parameter.empty:
                param_type = str(param.annotation)
                if param_type.startswith("<class '") and param_type.endswith("'>"):
                    param_type = param_type[8:-2]
            
            required = param.default == inspect.Parameter.empty
            
            tool.inputs[param_name] = {
                "type": param_type,
                "description": "",
                "required": required
            }
        
        # Set output type
        if output_type:
            tool.output_type = output_type
        elif func.__annotations__.get("return"):
            return_type = func.__annotations__["return"]
            tool.output_type = str(return_type)
            if tool.output_type.startswith("<class '") and tool.output_type.endswith("'>"):
                tool.output_type = tool.output_type[8:-2]
        else:
            tool.output_type = "Any"
        
        return tool 
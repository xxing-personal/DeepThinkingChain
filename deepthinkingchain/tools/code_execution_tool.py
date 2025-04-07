"""
Code Execution Tool for DeepThinkingChain.

This module provides a tool for securely executing Python code snippets
within the DeepThinkingChain project.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional

from tools.tool import Tool
from sandbox.secure_executor import SecureExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CodeExecutionTool(Tool):
    """Tool for securely executing Python code snippets."""
    
    name = "code_executor"
    description = "Executes Python code snippets in a secure, sandboxed environment."
    inputs = {
        "code": {
            "type": "str",
            "description": "The Python code to execute",
            "required": True
        },
        "timeout": {
            "type": "int",
            "description": "Maximum execution time in seconds",
            "required": False
        },
        "allowed_imports": {
            "type": "list",
            "description": "List of module names that are permitted to be imported",
            "required": False
        }
    }
    output_type = "dict"
    capabilities = "Executes Python code with security restrictions on imports, execution time, and resource usage."
    category = "code_execution"
    
    def __init__(self, allowed_imports: Optional[List[str]] = None, 
                 default_timeout: int = 5,
                 max_memory_mb: int = 100):
        """
        Initialize the code execution tool.
        
        Args:
            allowed_imports: List of module names that are permitted to be imported
            default_timeout: Default maximum execution time in seconds
            max_memory_mb: Maximum memory usage allowed in MB
        """
        self.default_allowed_imports = allowed_imports or SecureExecutor.DEFAULT_ALLOWED_IMPORTS
        self.default_timeout = default_timeout
        self.max_memory_mb = max_memory_mb
        super().__init__()
    
    def forward(self, code: str, timeout: Optional[int] = None, 
                allowed_imports: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute the provided Python code snippet securely.
        
        Args:
            code: The Python code to execute
            timeout: Maximum execution time in seconds (overrides default if provided)
            allowed_imports: List of module names that are permitted to be imported (overrides default if provided)
            
        Returns:
            dict: A dictionary containing the execution result or error information
        """
        # Use provided values or defaults
        execution_timeout = timeout if timeout is not None else self.default_timeout
        imports_list = allowed_imports if allowed_imports is not None else self.default_allowed_imports
        
        # Create a secure executor
        executor = SecureExecutor(
            allowed_imports=imports_list,
            execution_timeout=execution_timeout,
            max_memory_mb=self.max_memory_mb
        )
        
        # Log the execution attempt
        logger.info(f"Executing code with timeout={execution_timeout}s and {len(imports_list)} allowed imports")
        
        # Execute the code
        result = executor.run(code)
        
        # Log the execution result
        if result["success"]:
            logger.info("Code execution completed successfully")
        else:
            logger.warning(f"Code execution failed: {result.get('error', 'Unknown error')}")
        
        return result


def main():
    """Example usage of the CodeExecutionTool."""
    # Create a code execution tool
    code_tool = CodeExecutionTool(
        allowed_imports=["math", "random", "datetime", "time"],
        default_timeout=10
    )
    
    # Example 1: Simple calculation
    print("Example 1: Simple calculation")
    code1 = """
import math
from datetime import datetime

# Calculate the area of a circle
radius = 5
area = math.pi * radius ** 2

# Get current time
now = datetime.now()
formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

print(f"Area of circle with radius {radius}: {area:.2f}")
print(f"Current time: {formatted_time}")

# Store the result for return
_ = {"area": area, "time": formatted_time}
"""
    result1 = code_tool(code=code1)
    print(f"Success: {result1['success']}")
    print(f"Output: {result1['output']}")
    print(f"Result: {result1['result']}")
    print(f"Error: {result1['error']}")
    print()
    
    # Example 2: Unauthorized import
    print("Example 2: Unauthorized import")
    code2 = """
import os  # This should be blocked
print("Current directory:", os.getcwd())
"""
    result2 = code_tool(code=code2)
    print(f"Success: {result2['success']}")
    print(f"Error: {result2['error']}")
    print()
    
    # Example 3: Custom timeout and imports
    print("Example 3: Custom timeout and imports")
    code3 = """
import time
import random

# Generate random numbers
numbers = [random.randint(1, 100) for _ in range(5)]
print(f"Random numbers: {numbers}")

# Sleep for a short time
print("Sleeping for 1 second...")
time.sleep(1)
print("Done sleeping")

_ = {"numbers": numbers}
"""
    result3 = code_tool(
        code=code3,
        timeout=2,
        allowed_imports=["random", "time"]
    )
    print(f"Success: {result3['success']}")
    print(f"Output: {result3['output']}")
    print(f"Result: {result3['result']}")
    print()


if __name__ == "__main__":
    main() 
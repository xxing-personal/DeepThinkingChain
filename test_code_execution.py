"""
Test script for the Python Code Execution Tool.

This script demonstrates how to use the CodeExecutionTool to securely execute
Python code snippets within the DeepThinkingChain project.
"""

import os
import sys
import logging
from tools.tool_manager import ToolManager
from tools.code_execution_tool import CodeExecutionTool
from sandbox.secure_executor import SecureExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_secure_executor_directly():
    """Test the SecureExecutor class directly."""
    print("\n=== Testing SecureExecutor Directly ===")
    
    # Create a secure executor
    executor = SecureExecutor(
        allowed_imports=["math", "random", "datetime", "time"],
        execution_timeout=5
    )
    
    # Example 1: Safe code with math operations
    print("\nExample 1: Safe code with math operations")
    code1 = """
import math

# Calculate the area of a circle
radius = 5
area = math.pi * radius ** 2

print(f"Area of circle with radius {radius}: {area:.2f}")

# Store the result for return
_ = {"radius": radius, "area": area}
"""
    result1 = executor.run(code1)
    print(f"Success: {result1['success']}")
    print(f"Output: {result1['output']}")
    print(f"Result: {result1['result']}")
    print(f"Error: {result1['error']}")
    
    # Example 2: Unsafe code with unauthorized import
    print("\nExample 2: Unsafe code with unauthorized import")
    code2 = """
import os  # This should be blocked
print("Current directory:", os.getcwd())
"""
    result2 = executor.run(code2)
    print(f"Success: {result2['success']}")
    print(f"Error: {result2['error']}")
    
    # Example 3: Code that times out
    print("\nExample 3: Code that times out")
    code3 = """
import time
for i in range(10):
    print(f"Iteration {i}")
    time.sleep(1)
"""
    result3 = executor.run(code3)
    print(f"Success: {result3['success']}")
    print(f"Output: {result3['output']}")
    print(f"Error: {result3['error']}")
    
    return all([result1['success'], not result2['success'], not result3['success']])


def test_code_execution_tool():
    """Test the CodeExecutionTool class."""
    print("\n=== Testing CodeExecutionTool ===")
    
    # Create a code execution tool
    code_tool = CodeExecutionTool(
        allowed_imports=["math", "random", "datetime", "time", "statistics"],
        default_timeout=5
    )
    
    # Example 1: Data analysis with statistics
    print("\nExample 1: Data analysis with statistics")
    code1 = """
import random
import statistics

# Generate random data
data = [random.randint(1, 100) for _ in range(20)]

# Calculate statistics
mean = statistics.mean(data)
median = statistics.median(data)
stdev = statistics.stdev(data)

print(f"Data: {data}")
print(f"Mean: {mean:.2f}")
print(f"Median: {median:.2f}")
print(f"Standard Deviation: {stdev:.2f}")

# Store the result for return
_ = {
    "data": data,
    "statistics": {
        "mean": mean,
        "median": median,
        "stdev": stdev
    }
}
"""
    result1 = code_tool(code=code1)
    print(f"Success: {result1['success']}")
    print(f"Output: {result1['output']}")
    print(f"Result: {result1['result']}")
    
    # Example 2: Custom timeout and imports
    print("\nExample 2: Custom timeout and imports")
    code2 = """
import time
import math

# Calculate square roots
numbers = list(range(1, 11))
roots = [math.sqrt(n) for n in numbers]

print(f"Numbers: {numbers}")
print(f"Square roots: {[round(r, 2) for r in roots]}")

# Sleep for a short time
print("Sleeping for 1 second...")
time.sleep(1)
print("Done sleeping")

_ = {"numbers": numbers, "roots": roots}
"""
    result2 = code_tool(
        code=code2,
        timeout=3,
        allowed_imports=["math", "time"]
    )
    print(f"Success: {result2['success']}")
    print(f"Output: {result2['output']}")
    print(f"Result: {result2['result']}")
    
    return all([result1['success'], result2['success']])


def test_tool_manager_integration():
    """Test integration with ToolManager."""
    print("\n=== Testing ToolManager Integration ===")
    
    # Create a tool manager
    tool_manager = ToolManager()
    
    # Add the code execution tool
    code_tool = CodeExecutionTool(
        allowed_imports=["math", "random", "datetime", "time", "statistics"],
        default_timeout=5
    )
    tool_manager.add_tool(code_tool)
    
    # Check if the tool is available
    print(f"Available tools: {tool_manager.get_tool_names()}")
    print(f"Tool categories: {tool_manager.get_categories()}")
    
    # Get the tool by name
    retrieved_tool = tool_manager.get_tool_by_name("code_executor")
    if retrieved_tool:
        print(f"Retrieved tool: {retrieved_tool.name}")
        print(f"Tool description: {retrieved_tool.description}")
        print(f"Tool capabilities: {retrieved_tool.capabilities}")
        
        # Execute code using the retrieved tool
        code = """
import random
import math

# Generate random numbers and calculate their square roots
numbers = [random.randint(1, 100) for _ in range(5)]
roots = [math.sqrt(n) for n in numbers]

print(f"Numbers: {numbers}")
print(f"Square roots: {[round(r, 2) for r in roots]}")

_ = {"numbers": numbers, "roots": roots}
"""
        result = retrieved_tool(code=code)
        print(f"\nExecution result:")
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print(f"Result: {result['result']}")
        
        return result['success']
    else:
        print("Tool not found in ToolManager")
        return False


def main():
    """Run all tests."""
    print("Python Code Execution Tool Tests")
    print("===============================")
    
    # Run tests
    executor_success = test_secure_executor_directly()
    tool_success = test_code_execution_tool()
    manager_success = test_tool_manager_integration()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"SecureExecutor: {'✅ Passed' if executor_success else '❌ Failed'}")
    print(f"CodeExecutionTool: {'✅ Passed' if tool_success else '❌ Failed'}")
    print(f"ToolManager Integration: {'✅ Passed' if manager_success else '❌ Failed'}")
    
    if executor_success and tool_success and manager_success:
        print("\nAll tests passed! The Python Code Execution Tool is working correctly.")
    else:
        print("\nSome tests failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 
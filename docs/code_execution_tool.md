# Python Code Execution Tool

## Overview

The Python Code Execution Tool enables agents within the DeepThinkingChain project to generate and execute Python code snippets dynamically. This functionality allows agents to perform complex computations, automate tasks, and interact with various tools programmatically, all within a secure environment.

## Components

The code execution tool consists of two main components:

1. **SecureExecutor**: A class that executes Python code snippets in a sandboxed environment with security restrictions.
2. **CodeExecutionTool**: A tool class that integrates with the DeepThinkingChain tools framework and uses the SecureExecutor to run code.

## Features

- **Secure Code Execution**: Executes Python code in a controlled environment with restrictions on imports, execution time, and resource usage.
- **Import Whitelisting**: Only allows importing modules from a predefined list of safe modules.
- **Execution Timeouts**: Prevents infinite loops or long-running processes by enforcing time limits.
- **AST-based Security Checks**: Analyzes the code's abstract syntax tree to detect potentially unsafe operations before execution.
- **Output Capture**: Captures both the printed output and the return value of the executed code.
- **Error Handling**: Provides detailed error information when code execution fails.

## Usage

### Basic Usage

```python
from tools.code_execution_tool import CodeExecutionTool

# Create a code execution tool with default settings
code_tool = CodeExecutionTool()

# Execute a simple code snippet
result = code_tool(code="""
import math

# Calculate the area of a circle
radius = 5
area = math.pi * radius ** 2

print(f"Area of circle with radius {radius}: {area:.2f}")

# Store the result for return
_ = {"radius": radius, "area": area}
""")

# Check the execution result
if result["success"]:
    print("Code executed successfully!")
    print(f"Output: {result['output']}")
    print(f"Result: {result['result']}")
else:
    print(f"Execution failed: {result['error']}")
```

### Advanced Usage

```python
# Create a code execution tool with custom settings
code_tool = CodeExecutionTool(
    allowed_imports=["math", "random", "datetime", "statistics"],
    default_timeout=10,
    max_memory_mb=200
)

# Execute code with custom parameters
result = code_tool(
    code="""
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
""",
    timeout=5,  # Override the default timeout
    allowed_imports=["random", "statistics"]  # Override the default allowed imports
)
```

### Integration with ToolManager

```python
from tools.tool_manager import ToolManager
from tools.code_execution_tool import CodeExecutionTool

# Create a tool manager
tool_manager = ToolManager()

# Add the code execution tool
code_tool = CodeExecutionTool()
tool_manager.add_tool(code_tool)

# Get the tool by name
code_executor = tool_manager.get_tool_by_name("code_executor")

# Execute code using the retrieved tool
result = code_executor(code="print('Hello, world!')")
```

## Security Considerations

Executing arbitrary code poses significant security risks. The Python Code Execution Tool implements several security measures to mitigate these risks:

1. **Restricted Imports**: Only allows importing modules from a predefined list of safe modules.
2. **AST Analysis**: Analyzes the code's abstract syntax tree to detect potentially unsafe operations before execution.
3. **Execution Timeouts**: Implements timeouts to prevent infinite loops or long-running processes.
4. **Restricted Builtins**: Limits access to potentially dangerous built-in functions like `eval`, `exec`, and `open`.
5. **Secure Import Function**: Uses a custom `__import__` function that only allows importing whitelisted modules.

## Default Allowed Imports

By default, the following modules are allowed to be imported:

- `math`: Mathematical functions
- `random`: Random number generation
- `datetime`: Date and time manipulation
- `time`: Time-related functions
- `json`: JSON encoding and decoding
- `re`: Regular expressions
- `collections`: Container datatypes
- `itertools`: Iterator functions
- `functools`: Higher-order functions
- `operator`: Standard operators as functions
- `statistics`: Statistical functions
- `decimal`: Decimal fixed point and floating point arithmetic
- `fractions`: Rational numbers
- `numpy`: Numerical computing
- `pandas`: Data analysis and manipulation
- `matplotlib`: Data visualization
- `seaborn`: Statistical data visualization

## Extending the Tool

You can extend the functionality of the code execution tool by:

1. **Adding More Allowed Imports**: Customize the list of allowed imports based on your specific needs.
2. **Implementing Additional Security Checks**: Add more security checks to the `_check_code_safety` method.
3. **Adding Resource Monitoring**: Implement more sophisticated resource monitoring to prevent resource exhaustion.

## Example Use Cases

1. **Data Analysis**: Perform statistical analysis on financial data.
2. **Algorithmic Trading**: Implement and test trading algorithms.
3. **Visualization**: Generate charts and graphs for data visualization.
4. **Machine Learning**: Train and evaluate simple machine learning models.
5. **Financial Calculations**: Perform complex financial calculations like NPV, IRR, etc.

## Limitations

1. **No File System Access**: The tool does not allow reading from or writing to the file system.
2. **No Network Access**: The tool does not allow making network requests.
3. **Limited Resources**: The tool enforces limits on execution time and memory usage.
4. **No Subprocess Creation**: The tool does not allow creating subprocesses or executing system commands.
5. **No Access to Environment Variables**: The tool does not provide access to environment variables.

## Conclusion

The Python Code Execution Tool provides a powerful yet secure way for agents to execute Python code dynamically. By implementing robust security measures, it enables agents to perform complex computations without compromising the security of the system. 
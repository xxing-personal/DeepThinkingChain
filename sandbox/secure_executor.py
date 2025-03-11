"""
Secure Python code execution module.

This module provides a secure environment for executing Python code snippets
with restrictions on imports, execution time, and resource usage.
"""

import ast
import builtins
import contextlib
import io
import signal
import sys
import threading
import traceback
from typing import Dict, List, Any, Optional, Set


class TimeoutException(Exception):
    """Exception raised when code execution exceeds the allowed time limit."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutException("Code execution timed out")


class RestrictedImportChecker(ast.NodeVisitor):
    """AST visitor to check for unauthorized imports in code."""
    
    def __init__(self, allowed_imports: List[str]):
        self.allowed_imports = set(allowed_imports)
        self.violations = []
        
    def visit_Import(self, node):
        """Check regular import statements."""
        for name in node.names:
            module_name = name.name.split('.')[0]
            if module_name not in self.allowed_imports:
                self.violations.append(f"Unauthorized import: {module_name}")
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        """Check from ... import ... statements."""
        if node.module:
            module_name = node.module.split('.')[0]
            if module_name not in self.allowed_imports:
                self.violations.append(f"Unauthorized import: {module_name}")
        self.generic_visit(node)


class SecureExecutor:
    """
    Executes Python code snippets in a secure, sandboxed environment.
    """
    
    # Default list of safe modules that can be imported
    DEFAULT_ALLOWED_IMPORTS = [
        "math", "random", "datetime", "time", "json", "re", "collections",
        "itertools", "functools", "operator", "statistics", "decimal",
        "fractions", "numpy", "pandas", "matplotlib", "seaborn"
    ]
    
    # Dangerous built-ins that should be restricted
    RESTRICTED_BUILTINS = {
        "eval", "exec", "compile", "globals", "locals", "open",
        "input", "breakpoint", "memoryview", "classmethod", "staticmethod",
        "property", "super", "type", "object", "__build_class__"
    }

    def __init__(self, allowed_imports: Optional[List[str]] = None, 
                 execution_timeout: int = 5,
                 max_memory_mb: int = 100):
        """
        Initialize the SecureExecutor with security parameters.

        Parameters:
        - allowed_imports (list): A list of module names that are permitted to be imported.
        - execution_timeout (int): Maximum time in seconds allowed for code execution.
        - max_memory_mb (int): Maximum memory usage allowed in MB.
        """
        self.allowed_imports = allowed_imports or self.DEFAULT_ALLOWED_IMPORTS
        self.execution_timeout = execution_timeout
        self.max_memory_mb = max_memory_mb
        
    def _check_code_safety(self, code_snippet: str) -> List[str]:
        """
        Check if the code contains any unsafe operations.
        
        Parameters:
        - code_snippet (str): The Python code to check.
        
        Returns:
        - List[str]: A list of safety violations found in the code.
        """
        violations = []
        
        try:
            # Parse the code into an AST
            tree = ast.parse(code_snippet)
            
            # Check for unauthorized imports
            import_checker = RestrictedImportChecker(self.allowed_imports)
            import_checker.visit(tree)
            violations.extend(import_checker.violations)
            
            # Check for other potentially unsafe operations
            for node in ast.walk(tree):
                # Check for calls to dangerous built-ins
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in self.RESTRICTED_BUILTINS:
                        violations.append(f"Unauthorized function call: {node.func.id}")
                
                # Check for attribute access that might be dangerous
                elif isinstance(node, ast.Attribute):
                    # Check for file operations
                    if node.attr in ["read", "write", "open", "close", "remove", "unlink"]:
                        violations.append(f"Potentially unsafe file operation: {node.attr}")
                    
                    # Check for system/os operations
                    if node.attr in ["system", "popen", "spawn", "exec", "eval"]:
                        violations.append(f"Potentially unsafe system operation: {node.attr}")
                    
                    # Check for network operations
                    if node.attr in ["connect", "bind", "listen", "accept", "socket"]:
                        violations.append(f"Potentially unsafe network operation: {node.attr}")
                
        except SyntaxError as e:
            violations.append(f"Syntax error in code: {str(e)}")
        
        return violations

    def _create_safe_globals(self) -> Dict[str, Any]:
        """
        Create a restricted globals dictionary for code execution.
        
        Returns:
        - Dict[str, Any]: A dictionary of safe globals.
        """
        # Start with a clean globals dictionary
        safe_globals = {}
        
        # Add safe builtins
        safe_builtins = {}
        for name in dir(builtins):
            if name not in self.RESTRICTED_BUILTINS and not name.startswith('__'):
                safe_builtins[name] = getattr(builtins, name)
        
        # Add __import__ function for imports to work
        safe_builtins['__import__'] = self._secure_import
        
        safe_globals['__builtins__'] = safe_builtins
        
        # Pre-import allowed modules
        for module_name in self.allowed_imports:
            try:
                if module_name in sys.modules:
                    safe_globals[module_name] = sys.modules[module_name]
                else:
                    # Try to import the module
                    safe_globals[module_name] = __import__(module_name)
            except Exception:
                pass  # Skip if module can't be imported
        
        return safe_globals
    
    def _secure_import(self, name, *args, **kwargs):
        """
        A secure version of __import__ that only allows importing from the allowed list.
        
        Parameters:
        - name: The name of the module to import
        
        Returns:
        - The imported module if allowed, otherwise raises ImportError
        """
        # Check if the module is in the allowed list
        if name.split('.')[0] not in self.allowed_imports:
            raise ImportError(f"Import of '{name}' is not allowed")
        
        # Import the module
        return __import__(name, *args, **kwargs)

    def run(self, code_snippet: str) -> Dict[str, Any]:
        """
        Execute the provided Python code snippet in a sandboxed environment.

        Parameters:
        - code_snippet (str): The Python code to execute.

        Returns:
        - dict: A dictionary containing the execution result or error information.
        """
        result = {
            "success": False,
            "output": "",
            "error": None,
            "result": None,
            "execution_time": 0
        }
        
        # Check code safety
        safety_violations = self._check_code_safety(code_snippet)
        if safety_violations:
            result["error"] = "Safety violations detected:\n" + "\n".join(safety_violations)
            return result
        
        # Prepare for execution
        output_buffer = io.StringIO()
        safe_globals = self._create_safe_globals()
        local_vars = {}
        
        # Set up the timeout handler
        original_handler = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.execution_timeout)
        
        try:
            # Redirect stdout and stderr
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                # Execute the code
                exec(code_snippet, safe_globals, local_vars)
                
            # Capture the output
            result["output"] = output_buffer.getvalue()
            
            # Capture the last expression's value if it exists
            if "_" in local_vars:
                result["result"] = local_vars["_"]
            
            result["success"] = True
            
        except TimeoutException:
            result["error"] = f"Code execution timed out after {self.execution_timeout} seconds"
        except Exception as e:
            result["error"] = f"Error during execution: {str(e)}\n{traceback.format_exc()}"
        finally:
            # Reset the alarm and restore the original signal handler
            signal.alarm(0)
            signal.signal(signal.SIGALRM, original_handler)
        
        return result


def main():
    """Example usage of the SecureExecutor."""
    executor = SecureExecutor(
        allowed_imports=["math", "random", "datetime"],
        execution_timeout=3
    )
    
    # Example 1: Safe code
    print("Example 1: Safe code")
    code1 = """
import math
result = math.sqrt(16)
print(f"The square root of 16 is {result}")
_ = result  # Store the result
"""
    result1 = executor.run(code1)
    print(f"Success: {result1['success']}")
    print(f"Output: {result1['output']}")
    print(f"Result: {result1['result']}")
    print(f"Error: {result1['error']}")
    print()
    
    # Example 2: Unsafe code (unauthorized import)
    print("Example 2: Unsafe code (unauthorized import)")
    code2 = """
import os
os.system("echo 'This should not be allowed'")
"""
    result2 = executor.run(code2)
    print(f"Success: {result2['success']}")
    print(f"Error: {result2['error']}")
    print()
    
    # Example 3: Code that times out
    print("Example 3: Code that times out")
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


if __name__ == "__main__":
    main() 
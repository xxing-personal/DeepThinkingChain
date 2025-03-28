"""
Basic import tests for DeepThinkingChain.

This ensures that the package can be imported correctly and
the main classes are available.
"""

import unittest

class TestImports(unittest.TestCase):
    """Test case for verifying that imports work correctly."""
    
    def test_package_imports(self):
        """Verify that main package components can be imported."""
        # Import the main package
        import deepthinkingchain
        
        # Verify version is available
        self.assertIsNotNone(deepthinkingchain.__version__)
        
        # Import and check main components
        from deepthinkingchain import DeepThinkingChain, Model, MemoryManager
        self.assertIsNotNone(DeepThinkingChain)
        self.assertIsNotNone(Model)
        self.assertIsNotNone(MemoryManager)
        
        # Test enum imports
        from deepthinkingchain import AgentType, TaskState, OutputFormat, ExecutionMode
        self.assertIsNotNone(AgentType)
        self.assertIsNotNone(TaskState)
        self.assertIsNotNone(OutputFormat)
        self.assertIsNotNone(ExecutionMode)
        
        print("✅ All imports successful!")


if __name__ == "__main__":
    unittest.main() 
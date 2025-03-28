#!/usr/bin/env python3
"""
Simple test script to verify that imports are working correctly
after the package refactoring.
"""

import sys
print(f"Python version: {sys.version}")

# Test importing the main package
try:
    import deepthinkingchain
    print(f"✅ Successfully imported deepthinkingchain {deepthinkingchain.__version__}")
except Exception as e:
    print(f"❌ Failed to import deepthinkingchain: {str(e)}")

# Test importing the main components
try:
    from deepthinkingchain import DeepThinkingChain, Model, MemoryManager
    print("✅ Successfully imported DeepThinkingChain, Model, and MemoryManager")
except Exception as e:
    print(f"❌ Failed to import main components: {str(e)}")

# Test importing constants
try:
    from deepthinkingchain import AgentType, TaskState, OutputFormat, ExecutionMode
    print("✅ Successfully imported constants")
except Exception as e:
    print(f"❌ Failed to import constants: {str(e)}")

# Test importing prompts
try:
    from deepthinkingchain.prompts import PromptTemplate, PromptManager, format_data_for_prompt
    print("✅ Successfully imported prompts")
except Exception as e:
    print(f"❌ Failed to import prompts: {str(e)}")

# Test creating a simple model
try:
    model = Model(model="o3-mini")
    print("✅ Successfully created a Model instance")
except Exception as e:
    print(f"❌ Failed to create Model instance: {str(e)}")

print("\nImport test complete!") 
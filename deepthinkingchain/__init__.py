"""
DeepThinkingChain - A multi-agent system for deep analytical thinking chains
"""

__version__ = "0.1.0"

from deepthinkingchain.orchestrator import DeepThinkingChain
from deepthinkingchain.model import Model
from deepthinkingchain.memory import MemoryManager
from deepthinkingchain.constants import AgentType, TaskState, OutputFormat, ExecutionMode
from deepthinkingchain.prompts import PromptTemplate, PromptManager, format_data_for_prompt

__all__ = [
    "DeepThinkingChain",
    "Model",
    "MemoryManager",
    "AgentType",
    "TaskState", 
    "OutputFormat",
    "ExecutionMode",
    "PromptTemplate",
    "PromptManager",
    "format_data_for_prompt"
] 
"""
Constants module for the Deep Thinking Chain.

This module contains constants and enumerations used throughout the Deep Thinking Chain system.
"""

from enum import Enum, auto

class AgentType(Enum):
    """Types of agents in the system."""
    GENERIC = auto()
    TOOL = auto()
    ANALYSIS = auto()
    PLANNING = auto()
    SUMMARY = auto()
    USER_INTENT = auto()
    
    def __str__(self):
        return self.name.lower()

class TaskState(Enum):
    """States for tasks in the system."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    
    def __str__(self):
        return self.name.lower()

class OutputFormat(Enum):
    """Output formats supported by the system."""
    TEXT = auto()
    JSON = auto()
    MARKDOWN = auto()
    HTML = auto()
    
    def __str__(self):
        return self.name.lower()

class ExecutionMode(Enum):
    """Execution modes for the system."""
    SEQUENTIAL = auto()
    PARALLEL = auto()
    
    def __str__(self):
        return self.name.lower()

__all__ = [
    'AgentType',
    'TaskState',
    'OutputFormat',
    'ExecutionMode'
] 
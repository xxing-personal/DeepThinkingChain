"""
Constants for the Deep Thinking Chain.

This module contains constant definitions for agent types, system states,
and other configuration values used throughout the system.
"""

from enum import Enum, auto

# Agent Types
class AgentType(str, Enum):
    """Enum for different agent types in the Deep Thinking Chain system."""
    
    USER_INTENT = "user_intent"
    ANALYSIS = "analysis"
    TOOL = "tool"
    SUMMARY = "summary"
    PLANNING = "planning"
    GENERIC = "generic"


# Task states
class TaskState(str, Enum):
    """Enum for different task states in the Deep Thinking Chain system."""
    
    PENDING = "pending"           # Task is waiting to be processed
    IN_PROGRESS = "in_progress"   # Task is currently being processed
    COMPLETED = "completed"       # Task has been completed successfully
    FAILED = "failed"             # Task has failed
    BLOCKED = "blocked"           # Task is blocked by dependencies

# Output formats
class OutputFormat(str, Enum):
    """Enum for different output formats."""
    
    JSON = "json"                 # JSON formatted output
    MARKDOWN = "markdown"         # Markdown formatted output
    TEXT = "text"                 # Plain text output
    CODE = "code"                 # Code output

# Chain execution modes
class ExecutionMode(str, Enum):
    """Enum for different execution modes of the thinking chain."""
    
    SEQUENTIAL = "sequential"     # Execute steps sequentially
    PARALLEL = "parallel"         # Execute steps in parallel where possible
    DYNAMIC = "dynamic"           # Dynamically decide execution strategy

# Default timeout values (in seconds)
DEFAULT_STEP_TIMEOUT = 60         # Default timeout for a single step
DEFAULT_CHAIN_TIMEOUT = 300       # Default timeout for the entire chain
MAX_CHAIN_ITERATIONS = 10         # Maximum iterations for a chain

# Memory management
MAX_CONTEXT_LENGTH = 8192         # Maximum length of context to maintain
SUMMARY_THRESHOLD = 4096          # Threshold at which to summarize context 
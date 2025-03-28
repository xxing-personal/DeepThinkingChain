"""
Prompts package for the Deep Thinking Chain.

This package contains classes for managing prompt templates used throughout
the Deep Thinking Chain system.
"""

from deepthinkingchain.prompts.prompt_template import PromptTemplate, format_data_for_prompt
from deepthinkingchain.prompts.prompt_manager import PromptManager

__all__ = ['PromptTemplate', 'PromptManager', 'format_data_for_prompt'] 
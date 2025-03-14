"""
Prompt templates for the Analysis Agent.

This module contains functions for generating prompts for the Analysis Agent
to analyze financial data and extract investment insights using the prompt template system.
"""

import os
from typing import Dict, Any, List
from .prompt_manager import PromptManager

# Initialize the prompt manager with the templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
prompt_manager = PromptManager(TEMPLATES_DIR)

def format_data_for_prompt(data: Dict[str, Any]) -> str:
    """
    Format a data dictionary into a string suitable for inclusion in a prompt.
    
    Args:
        data: Dictionary containing data to format
        
    Returns:
        Formatted string representation of the data
    """
    formatted_data = ""
    for key, value in data.items():
        if isinstance(value, dict):
            formatted_data += f"\n## {key.replace('_', ' ').title()}\n"
            for sub_key, sub_value in value.items():
                formatted_data += f"{sub_key}: {sub_value}\n"
        elif isinstance(value, list):
            formatted_data += f"\n## {key.replace('_', ' ').title()}\n"
            for item in value:
                if isinstance(item, dict):
                    formatted_data += "\n"
                    for item_key, item_value in item.items():
                        formatted_data += f"{item_key}: {item_value}\n"
                else:
                    formatted_data += f"- {item}\n"
        else:
            formatted_data += f"{key}: {value}\n"
    
    return formatted_data

def format_analyses_for_prompt(analyses: List[Dict[str, Any]]) -> str:
    """
    Format a list of analyses into a string suitable for inclusion in a prompt.
    
    Args:
        analyses: List of analysis dictionaries to format
        
    Returns:
        Formatted string representation of the analyses
    """
    formatted_analyses = ""
    for i, analysis in enumerate(analyses):
        formatted_analyses += f"\n## Analysis {i+1}: {analysis.get('analysis_type', 'General')}\n"
        
        # Add key insights
        if 'insights' in analysis:
            formatted_analyses += "\nKey Insights:\n"
            formatted_analyses += analysis['insights']
        
        # Add key points if available
        if 'key_points' in analysis and analysis['key_points']:
            formatted_analyses += "\n\nKey Points:\n"
            for point in analysis['key_points']:
                formatted_analyses += f"- {point}\n"
        
        # Add sentiment and confidence
        if 'sentiment' in analysis:
            formatted_analyses += f"\nSentiment: {analysis.get('sentiment', 'Neutral')}\n"
        if 'confidence' in analysis:
            formatted_analyses += f"Confidence: {analysis.get('confidence', 'Medium')}\n"
        
        formatted_analyses += "\n" + "-"*50 + "\n"
    
    return formatted_analyses

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

def initial_analysis_prompt(data: Dict[str, Any], symbol: str = None) -> str:
    """
    Generate a prompt for initial financial analysis of a company.
    
    This function creates a prompt for the first analysis iteration, focusing on
    general financial performance and business overview.
    
    Args:
        data: Financial data for the company to be analyzed
        symbol: The stock symbol of the company. If None, will try to extract from data.
        
    Returns:
        str: Formatted prompt for initial analysis
    """
    if symbol is None and 'symbol' in data:
        symbol = data.get('symbol')
    elif symbol is None:
        symbol = "the company"
    
    # Format the data for the prompt
    formatted_data = format_data_for_prompt(data)
    
    # Use the financial_analysis template
    return prompt_manager.format_template(
        "financial_analysis",
        symbol=symbol,
        data=formatted_data
    )

def detailed_analysis_prompt(data: Dict[str, Any], focus: str, symbol: str = None) -> str:
    """
    Generate a prompt for detailed analysis with a specific focus.
    
    This function creates a prompt for subsequent analysis iterations, focusing on
    specific aspects like competitive analysis, growth prospects, or risk assessment.
    
    Args:
        data: Financial data for the company to be analyzed
        focus: The focus area for analysis ('competitive', 'growth', 'risk')
        symbol: The stock symbol of the company. If None, will try to extract from data.
        
    Returns:
        str: Formatted prompt for detailed analysis
    """
    if symbol is None and 'symbol' in data:
        symbol = data.get('symbol')
    elif symbol is None:
        symbol = "the company"
    
    # Format the data for the prompt
    formatted_data = format_data_for_prompt(data)
    
    # Select the appropriate template based on the focus
    template_name = "financial_analysis"  # default
    if focus.lower() == 'competitive':
        template_name = "competitive_analysis"
    elif focus.lower() == 'growth':
        template_name = "growth_analysis"
    elif focus.lower() == 'risk':
        template_name = "risk_assessment"
    
    # Use the selected template
    return prompt_manager.format_template(
        template_name,
        symbol=symbol,
        data=formatted_data
    )

def planning_prompt(analyses: List[Dict[str, Any]], symbol: str = None) -> str:
    """
    Generate a prompt for planning the next steps in the analysis process.
    
    This function creates a prompt for the planning agent to determine whether
    to continue with further analysis or proceed to summarization.
    
    Args:
        analyses: List of previous analysis results
        symbol: The stock symbol of the company
        
    Returns:
        str: Formatted prompt for planning
    """
    if symbol is None and analyses and 'symbol' in analyses[0]:
        symbol = analyses[0].get('symbol')
    elif symbol is None:
        symbol = "the company"
    
    # Format the analyses for the prompt
    formatted_analyses = format_analyses_for_prompt(analyses)
    
    # Use the planning template
    return prompt_manager.format_template(
        "planning_template",
        symbol=symbol,
        analyses=formatted_analyses
    )

def summary_prompt(analyses: List[Dict[str, Any]], symbol: str = None) -> str:
    """
    Generate a prompt for summarizing multiple analyses into a comprehensive recommendation.
    
    This function creates a prompt for the summarization agent to synthesize multiple
    analyses into a final investment recommendation.
    
    Args:
        analyses: List of previous analysis results
        symbol: The stock symbol of the company
        
    Returns:
        str: Formatted prompt for summarization
    """
    if symbol is None and analyses and 'symbol' in analyses[0]:
        symbol = analyses[0].get('symbol')
    elif symbol is None:
        symbol = "the company"
    
    # Format the analyses for the prompt
    formatted_analyses = format_analyses_for_prompt(analyses)
    
    # Use the summary template
    return prompt_manager.format_template(
        "summary_template",
        symbol=symbol,
        analyses=formatted_analyses
    )

# For backward compatibility
def get_template_by_focus(focus: str) -> str:
    """
    Get the appropriate template based on the focus area.
    
    This function is provided for backward compatibility with code that
    might expect to access templates directly.
    
    Args:
        focus: The focus area ('financial', 'competitive', 'growth', 'risk')
        
    Returns:
        str: The template string for the specified focus
    """
    template_name = "financial_analysis"
    if focus.lower() == 'competitive':
        template_name = "competitive_analysis"
    elif focus.lower() == 'growth':
        template_name = "growth_analysis"
    elif focus.lower() == 'risk':
        template_name = "risk_assessment"
    
    template = prompt_manager.get_template(template_name)
    if template:
        return template.template_str
    return ""

#!/usr/bin/env python3
"""
Example script demonstrating how to use the prompt template system.

This script shows how to create, load, and use prompt templates for
generating prompts with dynamic content.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the prompts package
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompts import PromptTemplate, PromptManager


def create_templates_example():
    """Example of creating templates programmatically."""
    print("=== Creating Templates Example ===")
    
    # Create a template
    analysis_template = PromptTemplate(
        name="stock_analysis",
        template_str="Analyze the stock {symbol} focusing on {focus_area}. Consider the following factors: {factors}.",
        description="Template for stock analysis prompts"
    )
    
    # Get placeholders
    placeholders = analysis_template.get_placeholders()
    print(f"Required placeholders: {placeholders}")
    
    # Format the template
    formatted = analysis_template.format(
        symbol="AAPL",
        focus_area="financial performance",
        factors="revenue growth, profit margins, debt levels"
    )
    print(f"\nFormatted template:\n{formatted}")
    
    # Validate values
    values = {
        "symbol": "NVDA",
        "focus_area": "competitive analysis"
    }
    is_valid = analysis_template.validate_values(values)
    print(f"\nValues valid: {is_valid}")
    
    # Get missing placeholders
    missing = analysis_template.get_missing_placeholders(values)
    print(f"Missing placeholders: {missing}")


def prompt_manager_example():
    """Example of using the PromptManager."""
    print("\n=== Prompt Manager Example ===")
    
    # Create a prompt manager
    manager = PromptManager()
    
    # Add templates
    manager.add_template(PromptTemplate(
        name="stock_analysis",
        template_str="Analyze the stock {symbol} focusing on {focus_area}. Consider the following factors: {factors}.",
        description="Template for stock analysis prompts"
    ))
    
    manager.add_template(PromptTemplate(
        name="market_summary",
        template_str="Provide a summary of the {market} market for {date}, highlighting {highlight_count} key events.",
        description="Template for market summary prompts"
    ))
    
    # Get all template names
    template_names = manager.get_all_template_names()
    print(f"Available templates: {template_names}")
    
    # Format a template
    formatted = manager.format_template(
        "stock_analysis",
        symbol="AAPL",
        focus_area="financial performance",
        factors="revenue growth, profit margins, debt levels"
    )
    print(f"\nFormatted template:\n{formatted}")
    
    # Save templates to files
    templates_dir = os.path.join(os.path.dirname(__file__), "example_output")
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    saved = manager.save_all_templates(templates_dir)
    print(f"\nSaved {saved} templates to '{templates_dir}' directory")


def load_templates_example():
    """Example of loading templates from files."""
    print("\n=== Loading Templates Example ===")
    
    # Path to templates directory
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    
    # Create a prompt manager with templates directory
    manager = PromptManager(templates_dir)
    
    # Get all template names
    template_names = manager.get_all_template_names()
    print(f"Loaded templates: {template_names}")
    
    # Format a template if available
    if "stock_analysis" in template_names:
        formatted = manager.format_template(
            "stock_analysis",
            symbol="NVDA",
            focus_area="growth prospects",
            factors="market share, innovation pipeline, competitive positioning",
            detail_level="detailed",
            time_period="last 2 quarters"
        )
        print(f"\nFormatted stock analysis template:\n{formatted}")
    
    if "market_summary" in template_names:
        formatted = manager.format_template(
            "market_summary",
            market="US tech",
            date="2023-Q2",
            highlight_count="5",
            sector="semiconductor",
            metric_type="performance"
        )
        print(f"\nFormatted market summary template:\n{formatted}")


if __name__ == "__main__":
    # Run the examples
    create_templates_example()
    prompt_manager_example()
    
    # Only run this if the templates directory exists
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    if os.path.exists(templates_dir):
        load_templates_example()
    else:
        print(f"\nNote: Templates directory '{templates_dir}' not found. Skipping loading example.")
        print(f"Create the directory and add template JSON files to test loading functionality.") 
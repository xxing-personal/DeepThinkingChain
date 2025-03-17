"""
Prompt templates for the Analysis Agent.

This module contains functions for generating prompts for the Analysis Agent
to analyze financial data and extract investment insights using the prompt template system.
"""

import os
import json
import re
import sys
from typing import Dict, Any, List, Optional, Set, Tuple

# Add the parent directory to sys.path if running as a script
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # Try relative import first (when imported as a module)
    from .prompt_manager import PromptManager
except ImportError:
    # Fall back to absolute import (when run as a script)
    from prompts.prompt_manager import PromptManager

# Initialize the prompt manager with the templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
TMP_DIR = os.path.join(os.path.dirname(__file__), "tmp")
prompt_manager = PromptManager(TEMPLATES_DIR)

# Create tmp directory if it doesn't exist
os.makedirs(TMP_DIR, exist_ok=True)

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

def template_to_markdown(template_path: str) -> str:
    """
    Convert a template JSON file to a markdown file and save it to the /tmp folder.
    
    Args:
        template_path: Path to the template JSON file
        
    Returns:
        Path to the created markdown file
    """
    try:
        # Load the template JSON
        with open(template_path, 'r') as f:
            template_data = json.load(f)
        
        # Extract template components
        name = template_data.get('name', os.path.basename(template_path).split('.')[0])
        template_str = template_data.get('template', '')
        output_format = template_data.get('output_format', '')
        placeholders = template_data.get('placeholders', [])
        
        # Create markdown content
        markdown_content = f"# {name}\n\n"

        # Add template section
        markdown_content += template_str
        markdown_content += "\n\n"
        
        # Add output format section if available
        if output_format:
            markdown_content += "## Output Format\n\n```\n"
            markdown_content += output_format
            markdown_content += "\n```\n"
        
        # Save to markdown file in /tmp folder
        output_path = os.path.join(TMP_DIR, f"{name}.md")
        with open(output_path, 'w') as f:
            f.write(markdown_content)
        
        print(f"Template converted to markdown and saved to {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error converting template to markdown: {e}")
        return ""

def markdown_to_template(markdown_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert a markdown file to a template JSON file.
    
    Args:
        markdown_path: Path to the markdown file
        output_path: Optional path where the JSON file will be saved. If not provided,
                     it will be saved in the templates directory with the same name.
        
    Returns:
        Path to the created JSON file
    """
    try:
        # Read the markdown file
        with open(markdown_path, 'r') as f:
            markdown_content = f.read()
        
        # Extract name from the title (first h1)
        name_match = re.search(r'^# (.+)$', markdown_content, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else os.path.basename(markdown_path).split('.')[0]
        
        # Extract template content
        template_match = re.search(r'## Template\s*```\s*([\s\S]*?)\s*```', markdown_content)
        if template_match:
            template_str = template_match.group(1).strip()
        else:
            # If no Template section is found, extract all content between the first section and Output Format
            first_section_match = re.search(r'^##\s+(.+?)$', markdown_content, re.MULTILINE)
            if first_section_match:
                first_section_title = first_section_match.group(0)
                output_format_section = re.search(r'## Output Format', markdown_content)
                
                if output_format_section:
                    # Extract content from first section to just before Output Format
                    start_idx = markdown_content.find(first_section_title)
                    end_idx = output_format_section.start()
                    template_str = markdown_content[start_idx:end_idx].strip()
                else:
                    # If no Output Format section, extract all content after the first section
                    start_idx = markdown_content.find(first_section_title)
                    template_str = markdown_content[start_idx:].strip()
            else:
                template_str = ""
        
        # Extract output format if available
        output_format_match = re.search(r'## Output Format\s*```\s*([\s\S]*?)\s*```', markdown_content)
        output_format = output_format_match.group(1).strip() if output_format_match else ""
        
        placeholders = extract_placeholders_from_template(template_str)
        
        # Create template data
        template_data = {
            "name": name,
            "template": template_str,
            "placeholders": list(placeholders)  # Convert set to list for JSON serialization
        }
        
        if output_format:
            template_data["output_format"] = output_format
        
        # Determine output path
        if not output_path:
            output_path = os.path.join(TEMPLATES_DIR, f"{name.lower().replace(' ', '_')}_template.json")
        
        # Save to JSON file
        with open(output_path, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        print(f"Markdown converted to template and saved to {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error converting markdown to template: {e}")
        return ""

def extract_placeholders_from_template(template_str: str) -> Set[str]:
    """
    Extract all placeholders from a template string.
    
    Args:
        template_str: Template string with placeholders in curly braces
        
    Returns:
        Set of placeholder names
    """
    pattern = r'\{([^{}]*)\}'
    placeholders = set(re.findall(pattern, template_str))
    return placeholders


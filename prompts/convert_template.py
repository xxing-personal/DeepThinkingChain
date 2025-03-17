#!/usr/bin/env python3
"""
Script to convert a markdown template to a JSON template.
"""

import os
import re
import json
import argparse
from typing import Dict, Any, Set, Tuple


def extract_placeholders_from_template(template_str: str) -> Set[str]:
    """Extract all placeholders from the template string.
    
    Args:
        template_str: String with placeholders in curly braces ({placeholder})
        
    Returns:
        Set of placeholder names found in the template
    """
    # Find all strings within curly braces
    pattern = r'\{([^{}]*)\}'
    placeholders = set(re.findall(pattern, template_str))
    return placeholders


def extract_output_format(markdown_content: str) -> str:
    """Extract the output format from the markdown content.
    
    Args:
        markdown_content: The markdown content
        
    Returns:
        The output format string
    """
    output_format_match = re.search(r'## Output:\s*\n(.*?)(?:\n\n|$)', markdown_content, re.DOTALL)
    if output_format_match:
        output_format = output_format_match.group(1).strip()
        # If the output format starts with a format specifier (like "json"), remove it
        format_lines = output_format.split('\n', 1)
        if len(format_lines) > 1:
            return format_lines[1].strip()
        return output_format
    return ""


def extract_template_content(markdown_content: str) -> str:
    """Extract the template content from the markdown content.
    
    Args:
        markdown_content: The markdown content
        
    Returns:
        The template content
    """
    # Extract title
    title_match = re.search(r'^# (.*?)$', markdown_content, re.MULTILINE)
    title = title_match.group(1) if title_match else ""
    
    # Find the position after the title
    start_pos = title_match.end() if title_match else 0
    
    # Find the position of the Output Format section
    output_format_pos = markdown_content.find("## Output:", start_pos)
    if output_format_pos == -1:
        # If no Output Format section, use the entire content after the title
        return markdown_content[start_pos:].strip()
    
    # Extract the content between the title and the Output Format section
    return markdown_content[start_pos:output_format_pos].strip()


def markdown_to_template(markdown_file: str) -> Dict[str, Any]:
    """Convert a markdown file to a template.
    
    Args:
        markdown_file: Path to the markdown file
        
    Returns:
        Dictionary containing the template data
    """
    with open(markdown_file, 'r') as f:
        markdown_content = f.read()
    
    # Extract title
    title_match = re.search(r'^# (.*?)$', markdown_content, re.MULTILINE)
    name = title_match.group(1) if title_match else os.path.basename(markdown_file).split('.')[0]
    
    # Extract template content
    template_content = extract_template_content(markdown_content)
    
    # Extract output format
    output_format = extract_output_format(markdown_content)
    
    # Extract placeholders
    placeholders = extract_placeholders_from_template(template_content)
    
    # Create template data
    template_data = {
        "name": name,
        "template": template_content,
        "placeholders": list(placeholders),
        "output_format": output_format
    }
    
    return template_data


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Convert a markdown template to a JSON template.')
    parser.add_argument('markdown_file', help='Path to the markdown template file')
    parser.add_argument('--output', '-o', help='Path to the output JSON file')
    
    args = parser.parse_args()
    
    try:
        template_data = markdown_to_template(args.markdown_file)
        
        output_file = args.output
        if not output_file:
            output_file = os.path.splitext(args.markdown_file)[0] + '.json'
        
        with open(output_file, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        print(f"Successfully converted {args.markdown_file} to {output_file}")
    
    except Exception as e:
        print(f"Error converting markdown to template: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 
"""
Prompt Template Manager for the Deep Thinking Chain.

This module contains the PromptTemplate class which is responsible for managing
prompt templates with placeholders and providing methods to work with them.
"""

import re
import json
import os
from typing import List, Optional, Dict, Any, Set
import uuid
import logging

logger = logging.getLogger(__name__)

class PromptTemplate:
    """Manages prompt templates with placeholders.

    This class provides methods to work with prompt templates, including
    extracting placeholders and formatting templates with values.
    """

    def __init__(self, template_str: str, name: str = None, output_format: Optional[str] = None, description: Optional[str] = None):
        """Initialize a PromptTemplate.

        Args:
            name: Identifier for the template
            template_str: String with placeholders in curly braces ({placeholder})
            output_format: Optional format specification for the expected output structure
            description: Optional short description of template usage
        """
        self.template_str = template_str
        if output_format:
            self.output_format = output_format
        else:
            self.output_format = self._extract_output_format(template_str)
        self.name = name or "template_" + str(uuid.uuid4())
        self.description = description or f"Template for {name}"
        self._placeholders = self._extract_placeholders()

    def __str__(self) -> str:
        """String representation of the template.

        Returns:
            String with template name and description
        """
        return f"{self.name}: {self.description}"

    def __repr__(self) -> str:
        """Detailed representation of the template.

        Returns:
            String with template details including placeholders
        """
        placeholders_str = ", ".join(self._placeholders) if self._placeholders else "none"
        return f"PromptTemplate(name='{self.name}', placeholders=[{placeholders_str}], description='{self.description}')"

    @classmethod
    def from_json(cls, json_data: str) -> 'PromptTemplate':
        """Create a PromptTemplate from a JSON file.

        Args:
            json_data: Dictionary containing template data

        """ 
        return cls(template_str=json_data['template_str'],
                   name=json_data['name'],
                   output_format=json_data['output_format'],
                   description=json_data['description'])

    @classmethod
    def from_json_file(cls, json_file: str) -> 'PromptTemplate':
        """Create a PromptTemplate from a JSON file.

        Args:
            json_file: Path to the JSON file
        """
        json_data = json.load(open(json_file))
        return cls.from_json(json_data)

    @classmethod
    def from_markdown(cls, markdown_file: str) -> 'PromptTemplate':
        """Create a PromptTemplate from a Markdown dictionary.

        Args:
            markdown_file: Path to the Markdown file
        """
        name = os.path.basename(markdown_file).split('.')[0]
        markdown_data = open(markdown_file).read()
        return cls(template_str=markdown_data, name=name)

    def _extract_placeholders(self) -> Set[str]:
        """Extract all placeholders from the template string.

        Returns:
            Set of placeholder names found in the template
        """
        # Find all strings within curly braces
        pattern = r'\{([^{}]*)\}'
        placeholders = set(re.findall(pattern, self.template_str))
        return placeholders

    def _extract_output_format(self) -> str:
        """Extract the output format from the string. assuming string is in markdown format

        Returns:
            The output format string
        """
        output_format_match = re.search(r'## Output:\s*\n(.*?)(?:\n\n|$)', self.template_str, re.DOTALL)
        if output_format_match:
            output_format = output_format_match.group(1).strip()
            # If the output format starts with a format specifier (like "json"), remove it
            format_lines = output_format.split('\n', 1)
            if len(format_lines) > 1:
                return format_lines[1].strip()
            return output_format
        logger.warning(f"No output format found in the template: {self.template_str}")
        return ""

    def get_placeholders(self) -> Set[str]:
        """Get all placeholders required by this template.

        Returns:
            Set of placeholder names
        """
        return self._placeholders
    
    def get_output_format(self) -> Dict[str, Any]:
        """Get the output format from the template.
        Returns:
            The output format string
        """
        return self.output_format
    
    def format(self, **kwargs) -> str:
        """Format the template by replacing placeholders with provided values.

        Args:
            **kwargs: Key-value pairs where keys are placeholder names and values are replacements

        Returns:
            Formatted string with placeholders replaced by values

        Raises:
            KeyError: If a required placeholder is missing from kwargs
        """
        # Check if all required placeholders are provided
        missing = self._placeholders - set(kwargs.keys())
        if missing:
            logger.warning(f"Missing required placeholders: {', '.join(missing)}")
            for i in missing:
                kwargs[i] = " "
        # Format the template
        formatted_template = self.template_str.format(**kwargs)

        # Add output format if provided
        if self.output_format:
            formatted_template += f"\n\n## Output:\n{self.output_format}"

        return formatted_template

# helper function to format data for prompt

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


"""
Prompt Template Manager for the Deep Thinking Chain.

This module contains the PromptTemplate class which is responsible for managing
prompt templates with placeholders and providing methods to work with them.
"""

import re
import json
import os
from typing import List, Optional, Dict, Any, Set


class PromptTemplate:
    """Manages prompt templates with placeholders.
    
    This class provides methods to work with prompt templates, including
    extracting placeholders and formatting templates with values.
    """
    
    def __init__(self, name: str, template_str: str, output_format: Optional[str] = None, description: Optional[str] = None):
        """Initialize a PromptTemplate.
        
        Args:
            name: Identifier for the template
            template_str: String with placeholders in curly braces ({placeholder})
            output_format: Optional format specification for the expected output structure
            description: Optional short description of template usage
        """
        self.name = name
        self.template_str = template_str
        self.output_format = output_format or ""
        self.description = description or f"Template for {name}"
        self._placeholders = self._extract_placeholders()
    
    def _extract_placeholders(self) -> Set[str]:
        """Extract all placeholders from the template string.
        
        Returns:
            Set of placeholder names found in the template
        """
        # Find all strings within curly braces
        pattern = r'\{([^{}]*)\}'
        placeholders = set(re.findall(pattern, self.template_str))
        return placeholders
    
    def get_placeholders(self) -> Set[str]:
        """Get all placeholders required by this template.
        
        Returns:
            Set of placeholder names
        """
        return self._placeholders
    
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
            raise KeyError(f"Missing required placeholders: {', '.join(missing)}")
        
        # Format the template
        formatted_template = self.template_str.format(**kwargs)
        
        # Add output format if provided
        if self.output_format:
            formatted_template += f"\n\n## Output:\n{self.output_format}"
            
        return formatted_template
    
    def validate_values(self, values: Dict[str, Any]) -> bool:
        """Validate if the provided values contain all required placeholders.
        
        Args:
            values: Dictionary of values to check
            
        Returns:
            True if all required placeholders are present, False otherwise
        """
        return self._placeholders.issubset(set(values.keys()))
    
    def get_missing_placeholders(self, values: Dict[str, Any]) -> Set[str]:
        """Get placeholders that are missing from the provided values.
        
        Args:
            values: Dictionary of values to check
            
        Returns:
            Set of placeholder names that are missing
        """
        return self._placeholders - set(values.keys())
    
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
    
    def extract_output_to_dict(self, output: str) -> Dict[str, Any]:
        """Extract the output from the template into a structured dictionary.
        
        This method parses the output from the LLM response based on the expected output format
        and converts it into a structured dictionary for easier processing.
        
        Args:
            output: String output from the LLM
            
        Returns:
            Dictionary containing the structured output
            
        Raises:
            ValueError: If the output cannot be parsed according to the expected format
        """
        # Remove any leading/trailing whitespace
        output = output.strip()
        
        # Try to extract JSON from the output
        try:
            # Find JSON content between triple backticks if present
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', output)
            if json_match:
                json_str = json_match.group(1)
            else:
                # If not in code blocks, try to find JSON between curly braces
                json_match = re.search(r'(\{[\s\S]*\})', output)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Use the entire output as a last resort
                    json_str = output
            
            # Parse the JSON string
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON output: {e}")
    
    
def load_template_from_json(file_path: str) -> PromptTemplate:
    """Load a template from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        PromptTemplate instance created from the JSON file
        
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file is not valid JSON
        KeyError: If the JSON does not contain required fields
    """
    with open(file_path, 'r') as f:
        template_data = json.load(f)
    
    # Extract required fields
    name = template_data.get('name', os.path.basename(file_path).split('.')[0])
    template_str = template_data.get('template', '')
    output_format = template_data.get('output_format', None)
    description = template_data.get('description', None)
    
    return PromptTemplate(name, template_str, output_format, description)


def main():
    """Demonstrate how to use the PromptTemplate class."""
    # Example 1: Load a template from a JSON file
    try:
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'generic_analysis_template.json')
        template = load_template_from_json(template_path)
        
        print(f"Loaded template: {template}")
        print(f"Required placeholders: {template.get_placeholders()}")
        
        # Example values for the placeholders
        values = {
            "goal": "To understand the impact of climate change on marine ecosystems",
            "user_intent": "Research how rising ocean temperatures affect coral reefs",
            "summary": "Previous research has shown that rising ocean temperatures affect coral reefs.",
            "current_question": "What are the main factors causing coral bleaching?",
            "last_iteration": "Used web search to find information about coral bleaching",
            "last_step_result": "A recent study found that 30% of coral species are now endangered due to bleaching events."
        }
        
        # Check if all required placeholders are provided
        if template.validate_values(values):
            # Format the template with the values
            formatted_prompt = template.format(**values)
            print("\nFormatted prompt:")
            print("-" * 80)
            print(formatted_prompt)
            print("-" * 80)
            
            # Example of how to parse a response
            print("\nExample of parsing a response:")
            example_response = """
            ```json
            {
              "result": {
                "thinking": "The last_step_result provides information about coral bleaching and endangerment rates. This directly relates to the overall goal of understanding climate change impacts on marine ecosystems.",
                "summary": "Coral bleaching is accelerating with 30% of species now endangered. [source](https://example.org/coral-study)",
                "QA": [
                  {
                    "question": "What are the main factors causing coral bleaching?",
                    "answer": "The main factors are rising ocean temperatures and ocean acidification."
                  }
                ]
              }
            }
            ```
            """
            
            try:
                # Parse the response
                parsed_response = template.extract_output_to_dict(example_response)
                print("Parsed response:")
                print(json.dumps(parsed_response, indent=2))
            except Exception as e:
                print(f"Error parsing response: {e}")
        else:
            missing = template.get_missing_placeholders(values)
            print(f"Missing placeholders: {missing}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Create a template directly
    print("\nExample 2: Creating a template directly")
    simple_template = PromptTemplate(
        name="simple_greeting",
        template_str="Hello, {name}! Welcome to {place}.",
        description="A simple greeting template"
    )
    
    print(f"Simple template: {simple_template}")
    print(f"Required placeholders: {simple_template.get_placeholders()}")
    
    # Format the simple template
    formatted_simple = simple_template.format(name="Alice", place="Wonderland")
    print(f"Formatted simple template: {formatted_simple}")


if __name__ == "__main__":
    main()
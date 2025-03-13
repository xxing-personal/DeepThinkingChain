"""
Prompt Manager for the Deep Thinking Chain.

This module contains the PromptManager class which is responsible for managing
collections of prompt templates and providing methods to work with them.
"""

import os
import json
from typing import Dict, List, Optional, Any, Set
from .prompt_template import PromptTemplate


class PromptManager:
    """Manages collections of prompt templates.
    
    This class provides methods to load, retrieve, and use prompt templates
    for various parts of the Deep Thinking Chain system.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """Initialize a PromptManager.
        
        Args:
            templates_dir: Optional directory path where template files are stored
        """
        self.templates: Dict[str, PromptTemplate] = {}
        self.templates_dir = templates_dir
        
        # Load templates from directory if provided
        if templates_dir and os.path.exists(templates_dir):
            self.load_templates_from_directory(templates_dir)
    
    def add_template(self, template: PromptTemplate) -> None:
        """Add a template to the manager.
        
        Args:
            template: PromptTemplate object to add
        """
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name.
        
        Args:
            name: Name of the template to retrieve
            
        Returns:
            PromptTemplate if found, None otherwise
        """
        return self.templates.get(name)
    
    def remove_template(self, name: str) -> bool:
        """Remove a template by name.
        
        Args:
            name: Name of the template to remove
            
        Returns:
            True if template was removed, False if not found
        """
        if name in self.templates:
            del self.templates[name]
            return True
        return False
    
    def get_all_template_names(self) -> List[str]:
        """Get names of all available templates.
        
        Returns:
            List of template names
        """
        return list(self.templates.keys())
    
    def format_template(self, name: str, **kwargs) -> str:
        """Format a template with provided values.
        
        Args:
            name: Name of the template to format
            **kwargs: Values to use for formatting
            
        Returns:
            Formatted template string
            
        Raises:
            KeyError: If template not found or missing placeholders
        """
        template = self.get_template(name)
        if not template:
            raise KeyError(f"Template '{name}' not found")
        
        return template.format(**kwargs)
    
    def load_templates_from_directory(self, directory: str) -> int:
        """Load templates from JSON files in a directory.
        
        Args:
            directory: Directory path containing template JSON files
            
        Returns:
            Number of templates loaded
        """
        count = 0
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'r') as f:
                        template_data = json.load(f)
                        
                    # Create template from data
                    template = PromptTemplate(
                        name=template_data.get('name', os.path.splitext(filename)[0]),
                        template_str=template_data.get('template', ''),
                        description=template_data.get('description', None)
                    )
                    
                    self.add_template(template)
                    count += 1
                except Exception as e:
                    print(f"Error loading template from {filepath}: {str(e)}")
        
        return count
    
    def save_template_to_file(self, name: str, directory: Optional[str] = None) -> bool:
        """Save a template to a JSON file.
        
        Args:
            name: Name of the template to save
            directory: Directory to save to (defaults to self.templates_dir)
            
        Returns:
            True if saved successfully, False otherwise
        """
        template = self.get_template(name)
        if not template:
            return False
        
        save_dir = directory or self.templates_dir
        if not save_dir:
            return False
        
        os.makedirs(save_dir, exist_ok=True)
        
        filepath = os.path.join(save_dir, f"{name}.json")
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'name': template.name,
                    'template': template.template_str,
                    'description': template.description,
                    'placeholders': list(template.get_placeholders())
                }, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving template to {filepath}: {str(e)}")
            return False
    
    def save_all_templates(self, directory: Optional[str] = None) -> int:
        """Save all templates to JSON files.
        
        Args:
            directory: Directory to save to (defaults to self.templates_dir)
            
        Returns:
            Number of templates saved successfully
        """
        count = 0
        for name in self.get_all_template_names():
            if self.save_template_to_file(name, directory):
                count += 1
        return count


# Example usage
if __name__ == "__main__":
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
    if not os.path.exists("example_templates"):
        os.makedirs("example_templates")
    
    saved = manager.save_all_templates("example_templates")
    print(f"\nSaved {saved} templates to 'example_templates' directory") 
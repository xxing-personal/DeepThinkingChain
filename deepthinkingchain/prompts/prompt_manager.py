"""
Prompt Manager for the Deep Thinking Chain.

This module contains the PromptManager class which is responsible for managing
collections of prompt templates and providing methods to work with them.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any, Set
from deepthinkingchain.prompts.prompt_template import PromptTemplate


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
    
    
    def load_template_from_markdown(self, filepath: str) -> Optional[PromptTemplate]:
        """Load a template from a markdown file.
        
        Args:
            filepath: Path to the markdown file
            
        Returns:
            PromptTemplate if loaded successfully, None otherwise
        """
        try:
            # Extract template data from markdown
            template = PromptTemplate.from_markdown(filepath)
            self.add_template(template)
            return template
        except Exception as e:
            print(f"Error loading template from {filepath}: {str(e)}")
            return None
    
    def load_template_from_json(self, filepath: str) -> Optional[PromptTemplate]:
        """Load a template from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            PromptTemplate if loaded successfully, None otherwise
        """
        try:
            template = PromptTemplate.from_json(filepath)
            self.add_template(template)
            return template
        except Exception as e:
            print(f"Error loading template from {filepath}: {str(e)}")
            return None
    
    def load_templates_from_directory(self, directory: str) -> int:
        """Load templates from JSON and markdown files in a directory.
        
        Args:
            directory: Directory path containing template JSON and markdown files
            
        Returns:
            Number of templates loaded
        """
        count = 0
        
        # Make sure directory exists
        if not os.path.exists(directory):
            print(f"Warning: Template directory {directory} does not exist")
            return count
            
        # First check for subdirectories
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            # If there's a templates directory, load JSON templates from it
            if os.path.isdir(item_path) and item == "templates":
                print(f"Loading templates from {item_path}")
                for filename in os.listdir(item_path):
                    if filename.endswith('.json'):
                        file_path = os.path.join(item_path, filename)
                        if self.load_template_from_json(file_path):
                            count += 1
            
            # If there's a template directory, load markdown templates from it
            if os.path.isdir(item_path) and item == "template":
                print(f"Loading templates from {item_path}")
                for filename in os.listdir(item_path):
                    if filename.endswith('.md'):
                        file_path = os.path.join(item_path, filename)
                        if self.load_template_from_markdown(file_path):
                            count += 1
        
        # Also load JSON and markdown files from the main directory
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            # Skip directories
            if os.path.isdir(filepath):
                continue
                
            # Handle JSON templates
            if filename.endswith('.json'):
                if self.load_template_from_json(filepath):
                    count += 1
            
            # Handle markdown templates
            elif filename.endswith('.md'):
                if self.load_template_from_markdown(filepath):
                    count += 1
        
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
                    'output_format': template.output_format,
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
            Number of templates saved
        """
        save_dir = directory or self.templates_dir
        if not save_dir:
            return 0
        
        count = 0
        for name in self.templates:
            if self.save_template_to_file(name, save_dir):
                count += 1
        
        return count 
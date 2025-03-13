"""
Prompt Template Manager for the Deep Thinking Chain.

This module contains the PromptTemplate class which is responsible for managing
prompt templates with placeholders and providing methods to work with them.
"""

import re
from typing import List, Optional, Dict, Any, Set


class PromptTemplate:
    """Manages prompt templates with placeholders.
    
    This class provides methods to work with prompt templates, including
    extracting placeholders and formatting templates with values.
    """
    
    def __init__(self, name: str, template_str: str, description: Optional[str] = None):
        """Initialize a PromptTemplate.
        
        Args:
            name: Identifier for the template
            template_str: String with placeholders in curly braces ({placeholder})
            description: Optional short description of template usage
        """
        self.name = name
        self.template_str = template_str
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
        return self.template_str.format(**kwargs)
    
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


# Example usage
if __name__ == "__main__":
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
# Prompt Template System

This directory contains a flexible prompt template system for the DeepThinkingChain project. The system allows for easy management of prompt templates with placeholders, making it simple to create, load, and use dynamic prompts throughout the application.

## Overview

The prompt template system consists of two main components:

1. **PromptTemplate**: A class that represents a single prompt template with placeholders.
2. **PromptManager**: A class that manages collections of prompt templates, with functionality to load templates from files and save templates to files.

## Features

- **Placeholder Detection**: Automatically extracts placeholders from template strings
- **Template Validation**: Validates that all required placeholders are provided
- **JSON Storage**: Templates can be stored in and loaded from JSON files
- **Dynamic Formatting**: Easy formatting of templates with variable values
- **Error Handling**: Clear error messages when required placeholders are missing
- **Template Collections**: Manage multiple templates with a single manager

## Directory Structure

```
prompts/
├── __init__.py             # Package initialization
├── prompt_template.py      # PromptTemplate class definition
├── prompt_manager.py       # PromptManager class definition
├── analysis_prompts.py     # Analysis prompt generation functions
├── example.py              # Example usage script
├── test_analysis_prompts.py # Test script for analysis prompts
├── README.md               # This file
└── templates/              # Directory for template JSON files
    ├── stock_analysis.json        # Example template for stock analysis
    ├── market_summary.json        # Example template for market summaries
    ├── financial_analysis.json    # Template for financial analysis
    ├── competitive_analysis.json  # Template for competitive analysis
    ├── growth_analysis.json       # Template for growth analysis
    ├── risk_assessment.json       # Template for risk assessment
    ├── summary_template.json      # Template for investment summary
    └── planning_template.json     # Template for planning next steps
```

## Usage

### Creating Templates Programmatically

```python
from prompts import PromptTemplate

# Create a template
template = PromptTemplate(
    name="stock_analysis",
    template_str="Analyze the stock {symbol} focusing on {focus_area}. Consider the following factors: {factors}.",
    description="Template for stock analysis prompts"
)

# Get required placeholders
placeholders = template.get_placeholders()  # Returns {"symbol", "focus_area", "factors"}

# Format the template
formatted = template.format(
    symbol="AAPL",
    focus_area="financial performance",
    factors="revenue growth, profit margins, debt levels"
)
```

### Using the PromptManager

```python
from prompts import PromptManager, PromptTemplate

# Create a prompt manager
manager = PromptManager()

# Add templates
manager.add_template(PromptTemplate(
    name="stock_analysis",
    template_str="Analyze the stock {symbol} focusing on {focus_area}.",
    description="Template for stock analysis prompts"
))

# Format a template
formatted = manager.format_template(
    "stock_analysis", 
    symbol="AAPL", 
    focus_area="financial performance"
)
```

### Loading Templates from JSON Files

```python
from prompts import PromptManager

# Create a prompt manager with templates directory
manager = PromptManager("path/to/templates")

# Get all template names
template_names = manager.get_all_template_names()

# Format a template
formatted = manager.format_template(
    "stock_analysis",
    symbol="NVDA",
    focus_area="growth prospects",
    factors="market share, innovation pipeline",
    detail_level="detailed",
    time_period="last 2 quarters"
)
```

### Template JSON Format

Templates are stored in JSON files with the following structure:

```json
{
  "name": "stock_analysis",
  "template": "Analyze the stock {symbol} focusing on {focus_area}. Consider the following factors: {factors}.",
  "description": "Template for stock analysis prompts",
  "placeholders": ["symbol", "focus_area", "factors"]
}
```

## Analysis Prompts

The `analysis_prompts.py` module provides functions for generating prompts for the Analysis Agent using the prompt template system. It includes:

### Key Functions

- `initial_analysis_prompt(data, symbol)`: Generates a prompt for initial financial analysis
- `detailed_analysis_prompt(data, focus, symbol)`: Generates a prompt for focused analysis (competitive, growth, risk)
- `planning_prompt(analyses, symbol)`: Generates a prompt for planning next steps
- `summary_prompt(analyses, symbol)`: Generates a prompt for summarizing analyses into a recommendation

### Helper Functions

- `format_data_for_prompt(data)`: Formats a data dictionary into a string for inclusion in a prompt
- `format_analyses_for_prompt(analyses)`: Formats a list of analyses into a string for inclusion in a prompt
- `get_template_by_focus(focus)`: Gets the appropriate template string based on focus area (for backward compatibility)

### Example Usage

```python
from prompts import analysis_prompts

# Sample data
data = {
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "financial_metrics": {
        "revenue_growth": "15%",
        "profit_margin": "25%"
    }
}

# Generate initial analysis prompt
initial_prompt = analysis_prompts.initial_analysis_prompt(data)

# Generate focused analysis prompt
growth_prompt = analysis_prompts.detailed_analysis_prompt(data, focus="growth")

# Generate planning prompt
planning_prompt = analysis_prompts.planning_prompt(previous_analyses, symbol="AAPL")

# Generate summary prompt
summary_prompt = analysis_prompts.summary_prompt(all_analyses, symbol="AAPL")
```

## Example Script

The `example.py` script demonstrates how to use the prompt template system. Run it with:

```bash
python prompts/example.py
```

## Testing

The `test_analysis_prompts.py` script tests the functionality of the analysis_prompts module with the new template system. Run it with:

```bash
python prompts/test_analysis_prompts.py
```

## Integration with DeepThinkingChain

The prompt template system is used throughout the DeepThinkingChain project to generate prompts for various agents:

- **ToolAgent**: For generating data retrieval prompts
- **AnalysisAgent**: For generating analysis prompts based on focus areas
- **PlanningAgent**: For generating planning prompts
- **SummarizationAgent**: For generating summary prompts

By using templates, we ensure consistency in prompt structure while allowing for dynamic content based on the specific analysis context. 
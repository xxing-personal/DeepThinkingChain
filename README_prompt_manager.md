# Enhanced Prompt Manager

## Overview

The enhanced Prompt Manager provides functionality to load and manage templates for the Deep Thinking Chain. It supports both JSON and markdown template formats, making it easier to create and maintain templates.

## Key Features

- **Multiple Format Support**: Load templates from both JSON and markdown files
- **Directory Structure**: Automatically loads templates from the following locations:
  - `templates/` directory (JSON files)
  - `template/` directory (markdown files)
  - Root directory (both JSON and markdown files)
- **Placeholder Extraction**: Automatically extracts placeholders from template text
- **Output Format Support**: Supports structured output formats (JSON)
- **Template Validation**: Validates if all required placeholders are provided
- **Template Formatting**: Format templates with values for placeholders
- **Response Parsing**: Parse responses based on the template's output format

## Template Formats

### JSON Template Format

JSON templates have the following structure:

```json
{
  "name": "template_name",
  "template": "Template text with {placeholder1} and {placeholder2}.",
  "output_format": "{\n  \"result\": \"<!-- Result here -->\"\n}",
  "description": "Template description",
  "placeholders": ["placeholder1", "placeholder2"]
}
```

### Markdown Template Format

Markdown templates have the following structure:

```markdown
# Template Name

## Description (or any other sections)

Template text with {placeholder1} and {placeholder2}.

## Output:
json
{
  "result": "<!-- Result here -->"
}
```

The markdown format is easier to read and write, making it more user-friendly for template creation.

## Usage

### Initialize the Prompt Manager

```python
from prompts.prompt_manager import PromptManager

# Initialize with a directory containing templates
manager = PromptManager("path/to/templates")

# Or initialize without a directory and load templates manually
manager = PromptManager()
```

### Load Templates

```python
# Load from a directory
manager.load_templates_from_directory("path/to/templates")

# Load from a markdown file
template = manager.load_template_from_markdown("path/to/template.md")

# Load from a JSON file
template = manager.load_template_from_json("path/to/template.json")
```

### Use Templates

```python
# Get a template by name
template = manager.get_template("template_name")

# Format a template with values
formatted = manager.format_template(
    "template_name",
    placeholder1="value1",
    placeholder2="value2"
)

# Or format directly from a template object
formatted = template.format(placeholder1="value1", placeholder2="value2")

# Parse a response
response = """
```json
{
  "result": "This is the result"
}
```
"""
parsed = template.extract_output_to_dict(response)
```

### Save Templates

```python
# Save a template to a JSON file
manager.save_template_to_file("template_name", "path/to/output/directory")

# Save all templates
manager.save_all_templates("path/to/output/directory")
```

## Benefits

1. **Ease of Creation**: Markdown templates are easier to create and maintain than JSON templates
2. **Automatic Placeholder Detection**: Automatically detects placeholders in template text
3. **Flexible Directory Structure**: Supports loading templates from various locations
4. **Structured Output**: Supports structured output formats for easy parsing
5. **Validation**: Validates templates to ensure all required placeholders are provided

## Example Templates

The system comes with several example templates:

- `smartphone_analysis`: Template for analyzing smartphone market trends
- `generic_analysis`: Template for generic deep research analysis 
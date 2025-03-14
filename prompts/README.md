# Prompt Templates

This directory contains the prompt template system for the Deep Thinking Chain project. The template system allows you to define, manage, and use structured prompts with placeholders.

## Directory Structure

- `templates/`: Contains JSON template files
- `tmp/`: Temporary directory for markdown conversions
- `prompt_template.py`: Core template class and utilities
- `prompt_manager.py`: Manager for loading and accessing templates
- `prompt_helper.py`: Helper functions for working with templates
- `template_cli.py`: Command-line interface for template conversion
- `template_example.py`: Example script demonstrating template utilities

## Template Format

Templates are stored as JSON files with the following structure:

```json
{
  "name": "template_name",
  "template": "Template string with {placeholders}",
  "placeholders": ["placeholder1", "placeholder2"],
  "output_format": "Optional output format specification"
}
```

## Template Utilities

### Converting Templates to Markdown

You can convert template JSON files to markdown for easier editing:

```bash
# From the project root directory
python -m prompts.template_cli to-markdown path/to/template.json

# Or directly from the prompts directory
cd prompts
./template_cli.py to-markdown path/to/template.json
```

This will create a markdown file in the `tmp/` directory with the following structure:

```markdown
# Template Name

## Placeholders

- `{placeholder1}`
- `{placeholder2}`

## Template

```
Template string with {placeholders}
```

## Output Format

```
Output format specification
```
```

### Converting Markdown to Templates

You can convert markdown files back to template JSON:

```bash
# From the project root directory
python -m prompts.template_cli to-template path/to/template.md --output path/to/output.json

# Or directly from the prompts directory
cd prompts
./template_cli.py to-template path/to/template.md --output path/to/output.json
```

If no output path is specified, the template will be saved in the `templates/` directory.

### Running the Example Script

You can run the example script to see the template utilities in action:

```bash
# From the project root directory
python -m prompts.template_example

# Or directly from the prompts directory
cd prompts
./template_example.py
```

### Programmatic Usage

You can use the template utilities programmatically:

```python
from prompts.prompt_helper import template_to_markdown, markdown_to_template

# Convert template to markdown
markdown_path = template_to_markdown("path/to/template.json")

# Convert markdown to template
template_path = markdown_to_template("path/to/template.md", "path/to/output.json")
```

See `template_example.py` for more detailed examples.

## Using Templates in Code

Templates can be loaded and used in code:

```python
from prompts.prompt_manager import PromptManager

# Initialize the prompt manager
prompt_manager = PromptManager("path/to/templates")

# Get a template
template = prompt_manager.get_template("template_name")

# Format a template with values
formatted = template.format(
    placeholder1="value1",
    placeholder2="value2"
)
```

## Creating New Templates

You can create new templates either:

1. Directly as JSON files in the `templates/` directory
2. By creating markdown files and converting them to JSON
3. Programmatically using the `create_template` function

The markdown approach is recommended for creating and editing templates as it's more human-readable. 
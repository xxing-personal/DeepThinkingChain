#!/usr/bin/env python3
"""
Example script demonstrating how to use the template conversion functions.

This script shows how to convert templates to markdown and back,
as well as how to create and edit templates programmatically.
"""

import os
import sys

# Add the parent directory to sys.path to allow importing from the prompts package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompts.prompt_helper import template_to_markdown, markdown_to_template

def main():
    """Run the template conversion examples."""
    # Get the path to the templates directory
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    
    # Example 1: Convert a template to markdown
    print("Example 1: Converting a template to markdown")
    template_path = os.path.join(templates_dir, "generic_analysis_template.json")
    markdown_path = template_to_markdown(template_path)
    print(f"Template converted to markdown: {markdown_path}")
    print()
    
    # Example 2: Convert the markdown back to a template
    print("Example 2: Converting markdown back to a template")
    new_template_path = markdown_to_template(
        markdown_path, 
        os.path.join(templates_dir, "generic_analysis_copy_template.json")
    )
    print(f"Markdown converted to template: {new_template_path}")
    print()
    
    # Example 3: Create a new template from scratch
    print("Example 3: Creating a new template from scratch")
    
    # Create a simple markdown file
    tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")
    custom_md_path = os.path.join(tmp_dir, "custom_template.md")
    
    with open(custom_md_path, 'w') as f:
        f.write("""# Custom Template

## Placeholders

- `{input_text}`
- `{max_tokens}`
- `{temperature}`

## Template

```
You are a helpful assistant. Please respond to the following input:

Input: {input_text}

Remember to keep your response concise and helpful.
Maximum tokens: {max_tokens}
Temperature: {temperature}
```

## Output Format

```
<response>
    <!-- Your response here -->
</response>
```
""")
    
    # Convert the markdown to a template
    custom_template_path = markdown_to_template(
        custom_md_path,
        os.path.join(templates_dir, "custom_template.json")
    )
    print(f"Custom template created: {custom_template_path}")

if __name__ == "__main__":
    main() 
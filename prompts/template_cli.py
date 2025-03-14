#!/usr/bin/env python3
"""
Command-line interface for working with prompt templates.

This script provides a command-line interface for converting between
template JSON files and markdown files, as well as printing and editing templates.
"""

import os
import sys
import argparse

# Add the parent directory to sys.path to allow importing from the prompts package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompts.prompt_helper import template_to_markdown, markdown_to_template

def main():
    """Main entry point for the template CLI."""
    parser = argparse.ArgumentParser(description="Template conversion utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # to-markdown command
    to_md_parser = subparsers.add_parser("to-markdown", help="Convert template JSON to markdown")
    to_md_parser.add_argument("template_path", help="Path to the template JSON file")
    
    # to-template command
    to_template_parser = subparsers.add_parser("to-template", help="Convert markdown to template JSON")
    to_template_parser.add_argument("markdown_path", help="Path to the markdown file")
    to_template_parser.add_argument("--output", "-o", help="Output path for the template JSON file")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == "to-markdown":
        output_path = template_to_markdown(args.template_path)
        if output_path:
            print(f"Template converted to markdown: {output_path}")
        else:
            print("Failed to convert template to markdown")
            return 1
    
    elif args.command == "to-template":
        output_path = markdown_to_template(args.markdown_path, args.output)
        if output_path:
            print(f"Markdown converted to template: {output_path}")
        else:
            print("Failed to convert markdown to template")
            return 1
    
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
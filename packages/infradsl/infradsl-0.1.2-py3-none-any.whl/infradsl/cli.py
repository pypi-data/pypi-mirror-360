#!/usr/bin/env python3
"""
InfraDSL CLI Entry Point

This file serves as the main entry point for the InfraDSL CLI.
The actual implementation has been refactored into modular components
in the cli/ directory for better maintainability.

Previous monolithic structure (1,359 lines):
- Mixed CLI commands, output formatting, file loading, and templates

New modular structure:
- cli/commands.py: CLI command implementations (~300 lines)
- cli/output_formatters.py: Output formatting utilities (~400 lines)  
- cli/file_loader.py: Infrastructure file loading (~150 lines)
- cli/template_generator.py: Template generation (~500 lines)

Benefits of refactoring:
- Single Responsibility Principle: Each module has one clear purpose
- Easier Testing: Smaller, focused modules are easier to unit test
- Better Maintainability: Changes are isolated to specific concerns
- Improved Readability: Developers can focus on specific functionality
- Parallel Development: Multiple developers can work on different modules
"""

# Import the main CLI function from the refactored commands module
from .cli.commands import cli

if __name__ == '__main__':
    cli()
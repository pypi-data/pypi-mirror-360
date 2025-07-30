"""
InfraDSL CLI Module

This module contains the refactored CLI components that were previously
in a single large cli.py file. The components are now organized as:

- commands.py: All CLI command implementations
- output_formatters.py: Output formatting and printing utilities  
- file_loader.py: Infrastructure file loading and execution
- template_generator.py: Project template and example generation

This modular structure makes the CLI more maintainable and testable.
"""

from .commands import cli, register_preview_resource
from .output_formatters import (
    print_success, print_warning, print_error, print_info, print_header,
    show_progress, format_output, auto_format_results, display_preview_summary
)
from .file_loader import (
    load_infrastructure_file, load_infrastructure_file_with_mode,
    validate_infrastructure_file, get_default_infrastructure_file
)
from .template_generator import get_template_content, create_project_structure

__all__ = [
    # Main CLI entry point
    'cli',
    
    # Command utilities
    'register_preview_resource',
    
    # Output formatting
    'print_success', 'print_warning', 'print_error', 'print_info', 'print_header',
    'show_progress', 'format_output', 'auto_format_results', 'display_preview_summary',
    
    # File loading
    'load_infrastructure_file', 'load_infrastructure_file_with_mode',
    'validate_infrastructure_file', 'get_default_infrastructure_file',
    
    # Template generation
    'get_template_content', 'create_project_structure'
]
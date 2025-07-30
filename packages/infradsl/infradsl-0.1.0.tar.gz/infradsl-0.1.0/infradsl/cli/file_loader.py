"""
Infrastructure File Loader

This module handles loading and executing infrastructure files with different modes
(preview, apply, destroy). It manages the module execution and provider injection.
"""

import os
import sys
import click
import importlib.util
from typing import Any


def load_infrastructure_file(file_path: str) -> Any:
    """Load and execute an infrastructure file"""
    try:
        # Create a spec from the file path
        spec = importlib.util.spec_from_file_location("infrastructure", file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load file: {file_path}")

        # Create a new module based on the spec
        module = importlib.util.module_from_spec(spec)

        # Add our providers to the module's global namespace
        _inject_providers(module)

        # Execute the module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        click.echo(f"Error loading infrastructure file: {str(e)}", err=True)
        sys.exit(1)


def load_infrastructure_file_with_mode(file_path: str, mode: str = "apply") -> Any:
    """Load and execute an infrastructure file with a specific mode (preview, apply, or destroy)"""
    try:
        # Set the INFRA_MODE environment variable so components can detect the mode
        os.environ['INFRA_MODE'] = mode

        # Read the file content
        with open(file_path, 'r') as f:
            file_content = f.read()

        # Replace method calls based on mode
        file_content = _transform_file_content(file_content, mode)

        # Create a spec from the file path
        spec = importlib.util.spec_from_file_location("infrastructure", file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load file: {file_path}")

        # Create a new module based on the spec
        module = importlib.util.module_from_spec(spec)

        # Add our providers to the module's global namespace
        _inject_providers(module)

        # Execute the modified content
        exec(file_content, module.__dict__)
        return module
    except Exception as e:
        click.echo(f"Error loading infrastructure file: {str(e)}", err=True)
        sys.exit(1)
    finally:
        # Clean up the environment variable
        if 'INFRA_MODE' in os.environ:
            del os.environ['INFRA_MODE']


def _inject_providers(module: Any) -> None:
    """Inject cloud providers into the module namespace"""
    try:
        from infradsl.providers.digitalocean import DigitalOcean
        from infradsl.providers.googlecloud import GoogleCloud
        from infradsl.providers.aws import AWS
        
        module.DigitalOcean = DigitalOcean
        module.GoogleCloud = GoogleCloud
        module.AWS = AWS
    except ImportError as e:
        click.echo(f"Warning: Could not import some providers: {str(e)}", err=True)


def _transform_file_content(content: str, mode: str) -> str:
    """Transform file content based on the execution mode"""
    if mode == "preview":
        # Replace .create() with .preview()
        content = content.replace('.create()', '.preview()')
    elif mode == "destroy":
        # Replace .create() with .destroy()
        content = content.replace('.create()', '.destroy()')
    # For 'apply' mode, keep .create() as-is
    
    return content


def validate_infrastructure_file(file_path: str) -> bool:
    """Validate that the infrastructure file exists and is readable"""
    if not os.path.exists(file_path):
        click.echo(f"Error: Infrastructure file not found: {file_path}", err=True)
        return False
    
    if not os.path.isfile(file_path):
        click.echo(f"Error: Path is not a file: {file_path}", err=True)
        return False
    
    if not file_path.endswith('.py'):
        click.echo(f"Warning: File does not have .py extension: {file_path}", err=True)
    
    try:
        with open(file_path, 'r') as f:
            f.read()
        return True
    except Exception as e:
        click.echo(f"Error: Cannot read file {file_path}: {str(e)}", err=True)
        return False


def get_default_infrastructure_file() -> str:
    """Get the default infrastructure file path"""
    # Look for common infrastructure file names in the current directory
    candidates = [
        'main.py',
        'infrastructure.py',
        'infra.py',
        'deploy.py'
    ]
    
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    
    # If no default found, suggest main.py
    return 'main.py'


def list_infrastructure_files(directory: str = ".") -> list:
    """List potential infrastructure files in the given directory"""
    import glob
    
    # Common patterns for infrastructure files
    patterns = [
        "main.py",
        "infrastructure.py", 
        "infra.py",
        "deploy.py",
        "*infra*.py",
        "*deploy*.py"
    ]
    
    files = []
    for pattern in patterns:
        matches = glob.glob(os.path.join(directory, pattern))
        files.extend(matches)
    
    # Remove duplicates and sort
    return sorted(list(set(files)))


def check_file_syntax(file_path: str) -> bool:
    """Check if the file has valid Python syntax"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Try to compile the content
        compile(content, file_path, 'exec')
        return True
    except SyntaxError as e:
        click.echo(f"Syntax error in {file_path}:")
        click.echo(f"  Line {e.lineno}: {e.text.strip() if e.text else ''}")
        click.echo(f"  {' ' * (e.offset - 1 if e.offset else 0)}^")
        click.echo(f"  {e.msg}")
        return False
    except Exception as e:
        click.echo(f"Error checking syntax of {file_path}: {str(e)}")
        return False
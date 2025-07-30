"""
CLI Commands

This module contains all the command implementations for the InfraDSL CLI.
Each command is a separate function that handles a specific operation.
"""

import os
import sys
import click
import importlib
from dotenv import load_dotenv
from datetime import datetime
from typing import Any

from .output_formatters import (
    print_success, print_warning, print_error, print_info, print_header,
    show_progress, format_output, auto_format_results, display_preview_summary,
    show_spinner, show_progress_bar
)
from .file_loader import load_infrastructure_file, load_infrastructure_file_with_mode
from .template_generator import create_project_structure
from .template_commands import template_cli, generate_shortcut
from .daemon_commands import daemon_cli
from .registry_commands import registry_cli

# Global variable to collect preview information
_preview_resources = []


def register_preview_resource(provider: str, resource_type: str, name: str, details: list = None):
    """Register a resource that will be created"""
    global _preview_resources
    
    _preview_resources.append({
        'provider': provider,
        'type': resource_type,
        'name': name,
        'details': details or []
    })


@click.group()
def cli():
    """InfraDSL - Rails-like infrastructure management for modern clouds
    
    🚀 Deploy infrastructure with Rails-like simplicity
    ☁️  Supports AWS, Google Cloud, and DigitalOcean
    ⚡ Get started: infradsl init --interactive
    
    Examples:
        infradsl init staging aws          # Create new AWS project
        infradsl init --interactive        # Interactive project setup
        infradsl preview main.py           # Preview changes
        infradsl apply main.py             # Deploy infrastructure
        infradsl destroy main.py           # Clean up resources
        infradsl doctor                    # Check your setup
    """
    pass


@cli.command()
@click.argument('environment', type=str, required=False)
@click.argument('provider', type=click.Choice(['aws', 'gcp', 'digitalocean']), required=False)
@click.option('--path', '-p', default='.', help='Project path (default: current directory)')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing files')
@click.option('--interactive', '-i', is_flag=True, help='Run in interactive mode')
def init(environment: str, provider: str, path: str, force: bool, interactive: bool):
    """Initialize a new InfraDSL project with cloud provider templates
    
    Examples:
        infradsl init staging aws
        infradsl init production gcp --path ./my-project
        infradsl init development digitalocean
        infradsl init --interactive
    """
    
    if interactive or (not environment and not provider):
        # Interactive mode
        print_header("🚀 Welcome to InfraDSL!")
        print_info("Let's create your first infrastructure project together.")
        print_info("I'll ask you a few questions to get started.")
        
        # Get environment
        if not environment:
            print_info("\n📋 What environment are you setting up?")
            environment = click.prompt(
                "Environment name",
                type=click.Choice(['development', 'staging', 'production', 'custom']),
                default='development'
            )
            if environment == 'custom':
                environment = click.prompt("Enter custom environment name")
        
        # Get provider
        if not provider:
            print_info("\n☁️  Which cloud provider would you like to use?")
            provider = click.prompt(
                "Cloud provider",
                type=click.Choice(['aws', 'gcp', 'digitalocean']),
                default='aws'
            )
        
        # Get project path
        project_path = os.path.join(path, f"{environment}-{provider}")
        custom_path = click.prompt(
            f"Project path (default: {project_path})",
            default=project_path
        )
        if custom_path != project_path:
            project_path = custom_path
        
        # Confirm setup
        print_header("Project Summary")
        print_info(f"📁 Project: {project_path}")
        print_info(f"☁️  Provider: {provider.upper()}")
        print_info(f"🌍 Environment: {environment}")
        
        if not click.confirm("\nDoes this look correct?"):
            print_info("Setup cancelled. Run 'infradsl init --interactive' to try again.")
            return
    
    else:
        # Non-interactive mode
        project_path = os.path.join(path, f"{environment}-{provider}")
    
    # Check if directory already exists
    if os.path.exists(project_path) and not force:
        print_error(f"Directory '{project_path}' already exists!")
        print_info("Use --force to overwrite existing files.")
        return
    
    # Create project structure
    try:
        show_progress_bar(f"Creating {provider.upper()} project structure")
        create_project_structure(project_path, provider, environment)
        
        print_success("🎉 InfraDSL project initialized successfully!")
        print_header("Project Details")
        print_info(f"📁 Project: {project_path}")
        print_info(f"☁️  Provider: {provider.upper()}")
        print_info(f"🌍 Environment: {environment}")
        
        print_header("Next Steps")
        print_info(f"1. cd {project_path}")
        print_info(f"2. Edit .env with your {provider.upper()} credentials")
        print_info(f"3. infradsl preview main.py")
        print_info(f"4. infradsl apply main.py")
        
        print_info(f"📚 Examples available in examples/ directory")
        print_info(f"📖 Read README.md for detailed instructions")
        
        # Show provider-specific tips
        if provider == 'aws':
            print_warning("💡 AWS Tip: Make sure you have AWS CLI configured or set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY")
        elif provider == 'gcp':
            print_warning("💡 GCP Tip: Run 'gcloud auth application-default login' or set GOOGLE_APPLICATION_CREDENTIALS")
        elif provider == 'digitalocean':
            print_warning("💡 DigitalOcean Tip: Set your DO_API_TOKEN environment variable")
        
        # Show helpful commands
        print_header("Quick Commands")
        print_info(f"cd {project_path}")
        print_info("infradsl doctor  # Check your setup")
        print_info("infradsl preview main.py  # See what will be created")
        print_info("infradsl apply main.py  # Deploy your infrastructure")
        
    except Exception as e:
        print_error(f"Error initializing project: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--env', '-e', help='Path to .env file', type=click.Path(exists=True))
def preview(path: str, env: str):
    """Preview an infrastructure configuration without creating resources"""
    
    # Load environment variables silently
    if env:
        load_dotenv(env)
    else:
        # Look for .env in the same directory as the infrastructure file
        env_path = os.path.join(os.path.dirname(path), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)

    # Initialize preview collection
    global _preview_resources
    _preview_resources = []

    # Load the infrastructure file with preview mode
    module = load_infrastructure_file_with_mode(path, "preview")
    
    # Display preview summary only if resources were registered
    # (Individual resource classes handle their own preview display)
    if _preview_resources:
        display_preview_summary()
    
    # Auto-format results
    auto_format_results(module)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--env', '-e', help='Path to .env file', type=click.Path(exists=True))
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt')
def apply(path: str, env: str, yes: bool):
    """Apply an infrastructure configuration"""
    
    # Load environment variables silently
    if env:
        load_dotenv(env)
    else:
        # Look for .env in the same directory as the infrastructure file
        env_path = os.path.join(os.path.dirname(path), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)

    if not yes:
        print_warning("⚠️  This will create/modify/remove real cloud resources and may incur costs.")
        
        if not click.confirm("Do you want to continue?"):
            print_info("Operation cancelled.")
            return

    start_time = datetime.now()

    # Load and execute the infrastructure file
    module = load_infrastructure_file_with_mode(path, "apply")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n✅ Infrastructure changes applied in {duration:.1f} seconds!")
    
    # Show next steps  
    print("\n💡 Next steps:")
    print("   🔍 Check status: infradsl status")
    print("   🗑️  Clean up: infradsl destroy") 
    print("   📚 Read docs: https://docs.infradsl.dev")


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--env', '-e', help='Path to .env file', type=click.Path(exists=True))
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt')
def destroy(path: str, env: str, yes: bool):
    """Destroy infrastructure resources"""
    print_header("🗑️  InfraDSL Destroy Mode")
    
    # Load environment variables
    if env:
        show_progress_bar(f"Loading environment from {env}")
        load_dotenv(env)
    else:
        # Look for .env in the same directory as the infrastructure file
        env_path = os.path.join(os.path.dirname(path), '.env')
        if os.path.exists(env_path):
            show_progress_bar("Loading environment from .env file")
            load_dotenv(env_path)
        else:
            print_warning("No .env file found - using system environment variables")

    print_info(f"📁 Destroying infrastructure from: {path}")
    
    if not yes:
        print_error("⚠️  This will permanently delete all resources created by this configuration.")
        print_warning("💸 This action cannot be undone and may affect running services!")
        
        if not click.confirm("Are you absolutely sure you want to continue?"):
            print_info("Operation cancelled.")
            return
        
        # Double confirmation for destructive operations
        if not click.confirm("Final confirmation: Delete all resources?"):
            print_info("Operation cancelled.")
            return

    show_progress_bar("🗑️  Destroying infrastructure resources")
    start_time = datetime.now()

    # Load and execute the infrastructure file with destroy mode
    module = load_infrastructure_file_with_mode(path, "destroy")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_success(f"✅ Infrastructure destroyed successfully in {duration:.1f} seconds!")
    
    # Show summary
    print_header("Cleanup Summary")
    print_info(f"⏱️  Duration: {duration:.1f} seconds")
    print_info(f"📁 Configuration: {path}")
    print_info("🗑️  All resources removed successfully")
    
    # Auto-format results
    auto_format_results(module)
    
    # Show next steps
    print_header("What's Next?")
    print_info("🔄 Recreate infrastructure: infradsl apply main.py")
    print_info("📚 Start a new project: infradsl init --interactive")
    print_info("💡 Learn more: https://docs.infradsl.dev")


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--env', '-e', help='Path to .env file', type=click.Path(exists=True))
def status(path: str, env: str):
    """Show current infrastructure status"""
    print_header("InfraDSL Status Check")
    
    # Load environment variables
    if env:
        show_progress(f"Loading environment from {env}")
        load_dotenv(env)
    else:
        # Look for .env in the same directory as the infrastructure file
        env_path = os.path.join(os.path.dirname(path), '.env')
        if os.path.exists(env_path):
            show_progress("Loading environment from .env file")
            load_dotenv(env_path)
        else:
            print_warning("No .env file found - using system environment variables")

    print_info(f"Checking status for: {path}")
    show_progress("Analyzing infrastructure state")

    try:
        # Load the infrastructure file
        module = load_infrastructure_file(path)
        
        # Look for result variables in the module
        resources_found = False
        for var_name, var_value in module.__dict__.items():
            if not var_name.startswith('_') and isinstance(var_value, dict):
                resources_found = True
                print_header(f"Resource: {var_name}")
                
                # Display resource status
                if 'status' in var_value:
                    status = var_value['status']
                    if status == 'running' or status == 'active':
                        print_success(f"Status: {status}")
                    elif status == 'stopped' or status == 'inactive':
                        print_warning(f"Status: {status}")
                    else:
                        print_info(f"Status: {status}")
                
                # Display key information
                for key, value in var_value.items():
                    if key not in ['status'] and value and value != 'N/A':
                        print_info(f"{key.replace('_', ' ').title()}: {value}")
        
        if not resources_found:
            print_warning("No infrastructure resources found in the configuration")
        else:
            print_success("Status check completed successfully!")
            
    except Exception as e:
        print_error(f"Error checking status: {str(e)}")
        sys.exit(1)


@cli.command()
def version():
    """Show InfraDSL version information"""
    try:
        from infradsl.__version__ import __version__, __description__, __url__
        print_header("InfraDSL Version Information")
        print_info(f"Version: {__version__}")
        print_info(__description__)
        print_info("Supports: AWS, Google Cloud, DigitalOcean")
        print_info(f"Website: {__url__}")
    except ImportError:
        print_error("Could not determine InfraDSL version")
        sys.exit(1)


@cli.command()
def doctor():
    """Diagnose common setup issues and provide solutions"""
    print_header("InfraDSL Doctor - System Diagnostics")
    
    issues_found = 0
    total_checks = 0
    
    # Check Python version
    total_checks += 1
    print_info("🔍 Checking Python version...")
    if sys.version_info >= (3, 8):
        print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ✓")
    else:
        print_error(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ✗")
        print_info("   InfraDSL requires Python 3.8 or higher")
        issues_found += 1
    
    # Check AWS credentials
    total_checks += 1
    print_info("🔍 Checking AWS credentials...")
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    if aws_access_key and aws_secret_key:
        print_success("AWS credentials found ✓")
    else:
        print_warning("AWS credentials not found ⚠️")
        print_info("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        print_info("   Or run: aws configure")
        issues_found += 1
    
    # Check Google Cloud credentials
    total_checks += 1
    print_info("🔍 Checking Google Cloud credentials...")
    gcp_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if gcp_creds and os.path.exists(gcp_creds):
        print_success("Google Cloud credentials found ✓")
    else:
        print_warning("Google Cloud credentials not found ⚠️")
        print_info("   Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print_info("   Or run: gcloud auth application-default login")
        issues_found += 1
    
    # Check DigitalOcean credentials
    total_checks += 1
    print_info("🔍 Checking DigitalOcean credentials...")
    do_token = os.getenv('DO_API_TOKEN')
    if do_token:
        print_success("DigitalOcean API token found ✓")
    else:
        print_warning("DigitalOcean API token not found ⚠️")
        print_info("   Set DO_API_TOKEN environment variable")
        print_info("   Get your token from: https://cloud.digitalocean.com/account/api/tokens")
        issues_found += 1
    
    # Check required packages
    total_checks += 1
    print_info("🔍 Checking required packages...")
    missing_packages = []
    required_packages = [
        ('boto3', 'boto3'),
        ('google.cloud.compute', 'google-cloud-compute'),
        ('pydo', 'pydo'),
        ('click', 'click'),
        ('colorama', 'colorama')
    ]
    
    for import_name, package_name in required_packages:
        try:
            importlib.import_module(import_name)
        except ModuleNotFoundError:
            missing_packages.append(package_name)
    
    if not missing_packages:
        print_success("All required packages installed ✓")
    else:
        print_error(f"Missing packages: {', '.join(missing_packages)} ✗")
        print_info("   Run: pip install infradsl")
        issues_found += 1
    
    # Summary
    print_header("Diagnosis Complete")
    if issues_found == 0:
        print_success("🎉 All systems operational! You're ready to deploy infrastructure.")
        print_info("   Try: infradsl init staging aws")
    else:
        print_warning(f"⚠️  Found {issues_found} potential issue(s) out of {total_checks} checks")
        print_info("   Fix the issues above before deploying infrastructure")
        print_info("   Run 'infradsl doctor' again after making changes")
    
    return issues_found


@cli.command()
def completion():
    """Generate shell completion script"""
    print_header("InfraDSL Shell Completion")
    print_info("Add this to your shell configuration file (.bashrc, .zshrc, etc.):")
    print_info("")
    
    if os.getenv('SHELL', '').endswith('zsh'):
        print_info("  eval \"$(infradsl completion)\"")
        print_info("")
        print_info("Or install manually:")
        print_info("  infradsl completion > ~/.zsh/completion/_infradsl")
    else:
        print_info("  eval \"$(infradsl completion)\"")
        print_info("")
        print_info("Or install manually:")
        print_info("  infradsl completion > ~/.bash_completion.d/infradsl")
    
    print_info("")
    print_info("Restart your shell or run 'source ~/.bashrc' to activate completion.")


# Add template marketplace commands
cli.add_command(template_cli)
cli.add_command(generate_shortcut)

# Add daemon monitoring commands
cli.add_command(daemon_cli)

# Add registry commands
cli.add_command(registry_cli)


if __name__ == '__main__':
    cli()
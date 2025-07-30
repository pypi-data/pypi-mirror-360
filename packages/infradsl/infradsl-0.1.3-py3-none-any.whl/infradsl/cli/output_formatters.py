"""
CLI Output Formatters

This module contains all the formatting and printing utilities for the InfraDSL CLI.
Handles colored output, progress indicators, and result formatting.
"""

import click
import time
from typing import Dict, Any

# Add color support for better UX
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback colors
    class Fore:
        GREEN = ""
        YELLOW = ""
        RED = ""
        BLUE = ""
        CYAN = ""
        WHITE = ""
    class Style:
        BRIGHT = ""
        RESET_ALL = ""


def print_success(message: str):
    """Print a success message with green color"""
    if COLORS_AVAILABLE:
        click.echo(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
    else:
        click.echo(f"✅ {message}")


def print_warning(message: str):
    """Print a warning message with yellow color"""
    if COLORS_AVAILABLE:
        click.echo(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")
    else:
        click.echo(f"⚠️  {message}")


def print_error(message: str):
    """Print an error message with red color"""
    if COLORS_AVAILABLE:
        click.echo(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")
    else:
        click.echo(f"❌ {message}")


def print_info(message: str):
    """Print an info message with blue color"""
    if COLORS_AVAILABLE:
        click.echo(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")
    else:
        click.echo(f"ℹ️  {message}")


def print_header(message: str):
    """Print a header message with cyan color"""
    if COLORS_AVAILABLE:
        click.echo(f"{Fore.CYAN}{Style.BRIGHT}{'='*50}{Style.RESET_ALL}")
        click.echo(f"{Fore.CYAN}{Style.BRIGHT}{message}{Style.RESET_ALL}")
        click.echo(f"{Fore.CYAN}{Style.BRIGHT}{'='*50}{Style.RESET_ALL}")
    else:
        click.echo("="*50)
        click.echo(message)
        click.echo("="*50)


def show_progress(message: str, duration: float = 1.0):
    """Show a progress message with spinner"""
    if COLORS_AVAILABLE:
        click.echo(f"{Fore.CYAN}🔄 {message}...{Style.RESET_ALL}")
    else:
        click.echo(f"🔄 {message}...")
    time.sleep(duration)


def format_output(result: Dict[str, Any]) -> None:
    """Format and display the output results"""
    if not result:
        print_warning("No result data available")
        return
    
    resource_type = result.get('resource_type', 'unknown')
    
    # Format based on resource type
    if resource_type == 'aws_ec2':
        _format_ec2_output(result)
    elif resource_type == 'aws_s3':
        _format_s3_output(result)
    elif resource_type == 'aws_rds':
        _format_rds_output(result)
    elif resource_type == 'aws_lambda':
        _format_lambda_output(result)
    elif resource_type == 'aws_ecs':
        _format_ecs_output(result)
    elif resource_type.startswith('gcp_'):
        format_google_cloud_output(result)
    else:
        _format_generic_output(result)


def format_google_cloud_output(result: Dict[str, Any]) -> None:
    """Format Google Cloud resource output"""
    if not result:
        print_warning("No Google Cloud result data available")
        return
    
    resource_type = result.get('resource_type', 'unknown')
    
    print_success(f"Google Cloud {resource_type.replace('gcp_', '').title()} Resource")
    
    # Common GCP output formatting
    if 'project_id' in result:
        print_info(f"Project ID: {result['project_id']}")
    
    if 'zone' in result:
        print_info(f"Zone: {result['zone']}")
    
    if 'region' in result:
        print_info(f"Region: {result['region']}")
    
    # Resource-specific formatting
    if resource_type == 'gcp_compute_engine':
        _format_gcp_vm_output(result)
    elif resource_type == 'gcp_cloud_storage':
        _format_gcp_storage_output(result)
    elif resource_type == 'gcp_cloud_sql':
        _format_gcp_sql_output(result)
    elif resource_type == 'gcp_cloud_run':
        _format_gcp_cloud_run_output(result)
    else:
        _format_generic_output(result)


def auto_format_results(module: Any) -> None:
    """Automatically format all results from the loaded module"""
    # This function scans the module for any results and formats them
    for attr_name in dir(module):
        attr_value = getattr(module, attr_name)
        if isinstance(attr_value, dict) and 'resource_type' in attr_value:
            format_output(attr_value)


def display_preview_summary():
    """Display a summary of all preview resources"""
    from .commands import _preview_resources  # Import here to avoid circular imports
    
    if not _preview_resources:
        print_info("No resources to preview")
        return
    
    print_header("Infrastructure Preview Summary")
    
    # Group resources by provider
    providers = {}
    for resource in _preview_resources:
        provider = resource.get('provider', 'unknown')
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(resource)
    
    total_resources = len(_preview_resources)
    
    for provider, resources in providers.items():
        print_provider_resources(provider, resources, get_provider_icon(provider))
    
    print_timeline_estimate(total_resources)
    print_info(f"Total resources to manage: {total_resources}")


def print_provider_resources(provider_name: str, resources: list, icon: str):
    """Print resources grouped by provider"""
    print_info(f"\n{icon} {provider_name.upper()} Resources ({len(resources)}):")
    
    for resource in resources:
        resource_type = resource.get('type', 'unknown')
        resource_name = resource.get('name', 'unnamed')
        action = resource.get('action', 'create')
        
        action_icon = get_action_icon(action)
        type_icon = get_resource_icon(resource_type)
        
        click.echo(f"  {action_icon} {type_icon} {resource_name} ({resource_type})")


def get_resource_icon(resource_type: str) -> str:
    """Get an icon for a resource type"""
    icons = {
        'ec2': '🖥️',
        'vm': '🖥️',
        's3': '📦',
        'storage': '📦',
        'rds': '🗄️',
        'database': '🗄️',
        'lambda': '⚡',
        'function': '⚡',
        'ecs': '🐳',
        'container': '🐳',
        'vpc': '🌐',
        'network': '🌐',
        'loadbalancer': '⚖️',
        'dns': '🌍',
        'certificate': '🔒',
        'secret': '🔐',
        'api_gateway': '🚪',
        'cloudfront': '🌐',
        'cdn': '🌐'
    }
    
    # Try to find a matching icon
    for key, icon in icons.items():
        if key in resource_type.lower():
            return icon
    
    return '📋'  # Default icon


def get_action_icon(action: str) -> str:
    """Get an icon for an action"""
    icons = {
        'create': '➕',
        'update': '🔄',
        'delete': '🗑️',
        'destroy': '🗑️',
        'keep': '✅',
        'skip': '⏭️'
    }
    return icons.get(action.lower(), '📋')


def get_provider_icon(provider: str) -> str:
    """Get an icon for a cloud provider"""
    icons = {
        'aws': '☁️',
        'gcp': '🌩️',
        'google': '🌩️',
        'digitalocean': '🌊',
        'do': '🌊',
        'azure': '🔷',
        'cloudflare': '🧡'
    }
    return icons.get(provider.lower(), '☁️')


def print_timeline_estimate(total_resources: int):
    """Print estimated timeline for infrastructure deployment"""
    # Rough estimates based on resource count
    if total_resources <= 5:
        estimate = "2-5 minutes"
    elif total_resources <= 15:
        estimate = "5-15 minutes"
    elif total_resources <= 30:
        estimate = "15-30 minutes"
    else:
        estimate = "30+ minutes"
    
    print_info(f"Estimated deployment time: {estimate}")


# Private helper functions for specific resource formatting
def _format_ec2_output(result: Dict[str, Any]):
    """Format EC2 instance output"""
    print_success("AWS EC2 Instance")
    if 'instance_id' in result:
        print_info(f"Instance ID: {result['instance_id']}")
    if 'instance_type' in result:
        print_info(f"Instance Type: {result['instance_type']}")
    if 'public_ip' in result:
        print_info(f"Public IP: {result['public_ip']}")
    if 'private_ip' in result:
        print_info(f"Private IP: {result['private_ip']}")


def _format_s3_output(result: Dict[str, Any]):
    """Format S3 bucket output"""
    print_success("AWS S3 Bucket")
    if 'bucket_name' in result:
        print_info(f"Bucket Name: {result['bucket_name']}")
    if 'region' in result:
        print_info(f"Region: {result['region']}")
    if 'website_url' in result:
        print_info(f"Website URL: {result['website_url']}")


def _format_rds_output(result: Dict[str, Any]):
    """Format RDS database output"""
    print_success("AWS RDS Database")
    if 'db_instance_identifier' in result:
        print_info(f"DB Instance: {result['db_instance_identifier']}")
    if 'endpoint' in result:
        print_info(f"Endpoint: {result['endpoint']}")
    if 'engine' in result:
        print_info(f"Engine: {result['engine']}")


def _format_lambda_output(result: Dict[str, Any]):
    """Format Lambda function output"""
    print_success("AWS Lambda Function")
    if 'function_name' in result:
        print_info(f"Function Name: {result['function_name']}")
    if 'function_arn' in result:
        print_info(f"Function ARN: {result['function_arn']}")
    if 'api_endpoint' in result:
        print_info(f"API Endpoint: {result['api_endpoint']}")


def _format_ecs_output(result: Dict[str, Any]):
    """Format ECS service output"""
    print_success("AWS ECS Service")
    if 'cluster_name' in result:
        print_info(f"Cluster: {result['cluster_name']}")
    if 'service_name' in result:
        print_info(f"Service: {result['service_name']}")
    if 'task_definition' in result:
        print_info(f"Task Definition: {result['task_definition']}")


def _format_gcp_vm_output(result: Dict[str, Any]):
    """Format GCP VM output"""
    if 'instance_name' in result:
        print_info(f"Instance Name: {result['instance_name']}")
    if 'machine_type' in result:
        print_info(f"Machine Type: {result['machine_type']}")
    if 'external_ip' in result:
        print_info(f"External IP: {result['external_ip']}")


def _format_gcp_storage_output(result: Dict[str, Any]):
    """Format GCP Storage output"""
    if 'bucket_name' in result:
        print_info(f"Bucket Name: {result['bucket_name']}")
    if 'location' in result:
        print_info(f"Location: {result['location']}")


def _format_gcp_sql_output(result: Dict[str, Any]):
    """Format GCP Cloud SQL output"""
    if 'instance_name' in result:
        print_info(f"Instance Name: {result['instance_name']}")
    if 'database_version' in result:
        print_info(f"Database Version: {result['database_version']}")
    if 'connection_name' in result:
        print_info(f"Connection Name: {result['connection_name']}")


def _format_gcp_cloud_run_output(result: Dict[str, Any]):
    """Format GCP Cloud Run output"""
    if 'service_name' in result:
        print_info(f"Service Name: {result['service_name']}")
    if 'service_url' in result:
        print_info(f"Service URL: {result['service_url']}")
    if 'revision' in result:
        print_info(f"Revision: {result['revision']}")


def _format_generic_output(result: Dict[str, Any]):
    """Generic output formatting for unknown resource types"""
    resource_type = result.get('resource_type', 'Resource')
    print_success(f"{resource_type.title()}")
    
    # Print key-value pairs, excluding debug/internal keys
    exclude_keys = {
        'resource_type', 'internal_state', 'metadata',
        'existing_distributions', 'existing_zones', 'discovery_data',
        'current_state', 'desired_state', 'raw_response', 'debug_info',
        'detailed_state', 'full_config', 'extended_metadata',
        'to_create', 'to_keep', 'to_remove', 'estimated_deployment_time',
        'estimated_monthly_cost', 'custom_domains_count', 'records_count',
        'origin_domain', 'validation_method', 'certificate_type', 'key_algorithm',
        'tags_count', 'zone_type'
    }
    
    # Only show essential user-facing information
    essential_keys = {'name', 'domain_name', 'distribution_id', 'zone_id', 'status', 'id'}
    
    for key, value in result.items():
        if key not in exclude_keys and not key.startswith('_'):
            # For large data structures, show count instead of full content
            if isinstance(value, (list, dict)) and len(str(value)) > 200:
                if isinstance(value, list):
                    print_info(f"{key.replace('_', ' ').title()}: {len(value)} items")
                elif isinstance(value, dict):
                    print_info(f"{key.replace('_', ' ').title()}: {len(value)} entries")
            elif key in essential_keys or len(str(value)) <= 100:
                print_info(f"{key.replace('_', ' ').title()}: {value}")


def show_spinner(message: str, task_func, *args, **kwargs):
    """Show a spinner while executing a task"""
    import threading
    import sys
    
    spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    spinning = True
    result = None
    exception = None
    
    def spin():
        i = 0
        while spinning:
            if COLORS_AVAILABLE:
                sys.stdout.write(f'\r{Fore.CYAN}{spinner_chars[i % len(spinner_chars)]} {message}...{Style.RESET_ALL}')
            else:
                sys.stdout.write(f'\r{spinner_chars[i % len(spinner_chars)]} {message}...')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
    
    def run_task():
        nonlocal result, exception
        try:
            result = task_func(*args, **kwargs)
        except Exception as e:
            exception = e
    
    # Start spinner thread
    spinner_thread = threading.Thread(target=spin)
    spinner_thread.daemon = True
    spinner_thread.start()
    
    # Run the actual task
    task_thread = threading.Thread(target=run_task)
    task_thread.start()
    task_thread.join()
    
    # Stop spinner
    spinning = False
    spinner_thread.join(timeout=0.1)
    
    # Clear the spinner line
    sys.stdout.write('\r' + ' ' * (len(message) + 10) + '\r')
    sys.stdout.flush()
    
    if exception:
        raise exception
    
    return result


def show_progress_bar(items, description="Processing"):
    """Show a progress bar for iterating over items"""
    try:
        from tqdm import tqdm
        return tqdm(items, desc=description, unit="item")
    except ImportError:
        # Fallback without progress bar
        print_info(f"{description}...")
        return items
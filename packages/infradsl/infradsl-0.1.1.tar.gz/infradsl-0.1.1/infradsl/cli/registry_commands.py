"""
InfraDSL Registry Commands

CLI commands for pushing templates to the InfraDSL registry
"""

import os
import sys
import json
import click
import importlib.util
from pathlib import Path
from typing import List, Optional, Dict, Any
import requests
from datetime import datetime

from .firebase_client import FirebaseClient

from .output_formatters import (
    print_success, print_warning, print_error, print_info, print_header,
    show_progress, show_spinner
)


def _validate_python_compatibility(template_name: str, class_name: str) -> bool:
    """Validate that template name and class name are Python-compatible"""
    
    # Check if class name is valid Python identifier and CamelCase
    if not class_name.isidentifier():
        print_error(f"❌ Class name '{class_name}' is not a valid Python identifier")
        return False
    
    if '-' in class_name or '_' in class_name:
        print_error(f"❌ Class name '{class_name}' should use CamelCase (e.g., 'BuildPush', not 'build-push' or 'build_push')")
        print_info("💡 Use CamelCase for Python compatibility: BuildPush, SimpleWebApp, ApiGateway")
        return False
    
    if not class_name[0].isupper():
        print_error(f"❌ Class name '{class_name}' should start with uppercase letter (CamelCase)")
        print_info(f"💡 Try: '{class_name.capitalize()}' instead of '{class_name}'")
        return False
    
    # Check if template name would cause import issues
    if not template_name.replace('-', '').replace('_', '').isalnum():
        print_error(f"❌ Template name '{template_name}' contains invalid characters")
        return False
    
    return True


def _suggest_proper_naming(template_name: str, class_name: str) -> dict:
    """Suggest proper naming conventions"""
    suggestions = {}
    
    # Suggest proper class name
    if '-' in class_name or '_' in class_name:
        # Convert kebab-case or snake_case to CamelCase
        words = class_name.replace('-', '_').split('_')
        suggested_class = ''.join(word.capitalize() for word in words)
        suggestions['class_name'] = suggested_class
    elif not class_name[0].isupper():
        suggestions['class_name'] = class_name.capitalize()
    
    # Template name can stay kebab-case for registry
    if not template_name:
        if 'class_name' in suggestions:
            # Convert CamelCase to kebab-case for template name
            import re
            suggested_template = re.sub(r'(?<!^)(?=[A-Z])', '-', suggestions['class_name']).lower()
            suggestions['template_name'] = suggested_template
    
    return suggestions


class RegistryClient:
    """Client for interacting with the InfraDSL registry via Firebase"""
    
    def __init__(self, registry_url: str = None):
        self.registry_url = registry_url or os.getenv('INFRADSL_REGISTRY_URL', 'https://registry.infradsl.dev')
        self.firebase_client = FirebaseClient(project_id="infradsl")
        self.workspace = None
    
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with Firebase"""
        try:
            print_info("🔥 Authenticating with Firebase...")
            
            # Get Firebase API key from config (loads from registry/.env)
            from .firebase_config import get_firebase_api_key
            api_key = get_firebase_api_key()
            
            if not api_key or api_key.startswith('AIzaSyBxRo_SuIf3gX7PSHYdSXVXt3rjEOGBHiA'):
                # Check if we're using the old placeholder key
                print_warning("⚠️  Firebase API key not properly configured")
                print_info("Please ensure your Firebase API key is set in registry/.env")
                return False
            
            # Authenticate with Firebase
            success = self.firebase_client.authenticate_with_api_key(api_key, email, password)
            
            if success:
                print_success("✅ Firebase authentication successful!")
                
                # Extract workspace from email domain
                if '@' in email:
                    domain = email.split('@')[1]
                    if domain == 'infradsl.dev':
                        self.workspace = 'infradsl'
                    else:
                        self.workspace = domain.split('.')[0]
                else:
                    self.workspace = 'personal'
                
                print_info(f"🏢 Workspace: {self.workspace}")
                return True
            else:
                return False
                
        except Exception as e:
            print_error(f"Authentication error: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication"""
        headers = {'Content-Type': 'application/json'}
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        return headers
    
    def publish_template(self, template_data: Dict[str, Any]) -> str:
        """Publish template to Firebase/Firestore"""
        try:
            print_info("📤 Publishing template to Firestore...")
            print_info(f"📦 Template: {template_data['name']}")
            print_info(f"🏢 Workspace: {self.workspace}")
            
            # Add workspace to template data
            template_data['workspace'] = self.workspace
            
            # Publish to Firebase
            template_id = self.firebase_client.publish_template(template_data)
            
            if template_id:
                print_success("✅ Template published to Firestore successfully!")
                return template_id
            else:
                raise Exception("Failed to publish template to Firestore")
                
        except Exception as e:
            raise Exception(f"Firebase error: {str(e)}")


@click.group(name='registry')
def registry_cli():
    """InfraDSL template registry commands"""
    pass


@registry_cli.command('login')
@click.option('--email', '-e', prompt=True, help='Email address')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Password')
@click.option('--registry-url', '-r', help='Registry URL (default: http://localhost:3000)')
def login_cmd(email: str, password: str, registry_url: Optional[str]):
    """Login to the InfraDSL registry"""
    try:
        client = RegistryClient(registry_url)
        
        print_info("🔐 Authenticating with InfraDSL registry...")
        
        if client.authenticate(email, password):
            print_success("✅ Successfully authenticated!")
            if client.workspace:
                print_info(f"📦 Active workspace: {client.workspace}")
            
            # Save credentials securely (simplified for demo)
            config_dir = Path.home() / '.infradsl'
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / 'registry.json'
            with open(config_file, 'w') as f:
                json.dump({
                    'registry_url': client.registry_url,
                    'firebase_project': 'infradsl',
                    'workspace': client.workspace,
                    'email': email,
                    'user_info': client.firebase_client.user_info,
                    'auth_token': client.firebase_client.auth_token,
                    'token': client.firebase_client.auth_token,  # For backward compatibility
                    'last_login': datetime.now().isoformat()
                }, f)
            
            print_info(f"📁 Credentials saved to {config_file}")
            
        else:
            print_error("❌ Authentication failed")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"❌ Login error: {str(e)}")
        sys.exit(1)


@registry_cli.command('push')
@click.argument('template_file', type=click.Path(exists=True))
@click.option('--name', '-n', help='Template name (auto-detected if not provided)')
@click.option('--description', '-d', help='Template description')
@click.option('--version', '-v', default='1.0.0', help='Template version')
@click.option('--visibility', default='workspace', 
              type=click.Choice(['private', 'workspace', 'public']),
              help='Template visibility')
@click.option('--category', '-c', default='resource',
              type=click.Choice(['compute', 'storage', 'network', 'database', 'serverless', 'security']),
              help='Template category')
@click.option('--provider', '-p', multiple=True, help='Supported provider(s)')
@click.option('--tag', '-t', multiple=True, help='Template tag(s)')
@click.option('--dry-run', is_flag=True, help='Show what would be pushed without actually pushing')
def push_cmd(template_file: str, name: Optional[str], description: Optional[str],
             version: str, visibility: str, category: str, provider: tuple,
             tag: tuple, dry_run: bool):
    """Push a template to the InfraDSL registry"""
    try:
        # Load template file
        template_path = Path(template_file)
        template_class = _load_template_class(template_path)
        
        # Get metadata from template class
        metadata = {}
        if hasattr(template_class, 'get_metadata'):
            metadata = template_class.get_metadata()
        
        # Validate Python compatibility
        class_name = template_class.__name__
        template_name = name or metadata.get('name', template_class.__name__.lower())
        
        if not _validate_python_compatibility(template_name, class_name):
            suggestions = _suggest_proper_naming(template_name, class_name)
            if suggestions:
                print_header("💡 Suggested fixes:")
                if 'class_name' in suggestions:
                    print_info(f"   Class name: {suggestions['class_name']}")
                if 'template_name' in suggestions:
                    print_info(f"   Template name: {suggestions['template_name']}")
                print_info("   Please update your template and try again.")
            sys.exit(1)
        
        # Override with command line arguments
        template_data = {
            'name': template_name,
            'display_name': metadata.get('display_name', name or template_class.__name__),
            'description': description or metadata.get('description', ''),
            'version': version,
            'visibility': visibility,
            'category': category,
            'providers': list(provider) or metadata.get('providers', []),
            'tags': list(tag) or metadata.get('tags', []),
            'requirements': metadata.get('requirements', {}),
            'source_code': _get_source_code(template_path),
            'class_name': class_name,
            'template_type': 'class'
        }
        
        if dry_run:
            print_header("🔍 Dry Run - Template would be pushed with:")
            print_info(f"📦 Name: {template_data['name']}")
            print_info(f"📝 Description: {template_data['description']}")
            print_info(f"🏷️  Version: {template_data['version']}")
            print_info(f"👁️  Visibility: {template_data['visibility']}")
            print_info(f"📂 Category: {template_data['category']}")
            print_info(f"☁️  Providers: {', '.join(template_data['providers'])}")
            print_info(f"🏷️  Tags: {', '.join(template_data['tags'])}")
            print_info(f"🐍 Class: {template_data['class_name']}")
            return
        
        # Load registry credentials
        config_file = Path.home() / '.infradsl' / 'registry.json'
        if not config_file.exists():
            print_error("❌ Not authenticated. Run 'infradsl registry login' first")
            sys.exit(1)
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Initialize client
        client = RegistryClient(config['registry_url'])
        if 'user_info' in config:
            client.firebase_client.user_info = config['user_info']
        if 'auth_token' in config:
            client.firebase_client.auth_token = config['auth_token']
            client.auth_token = config['auth_token']
        elif 'token' in config:
            client.firebase_client.auth_token = config['token']
            client.auth_token = config['token']
        client.workspace = config['workspace']
        
        # Push template
        print_header("📤 Publishing template to registry...")
        print_info("🚀 Uploading template data...")
        
        template_id = client.publish_template(template_data)
        
        workspace_prefix = f"{client.workspace}/" if client.workspace else ""
        print_success(f"✅ Template '{workspace_prefix}{template_data['name']}' published successfully!")
        print_info(f"🆔 Template ID: {template_id}")
        print_info(f"🏷️  Version: {template_data['version']}")
        
        if visibility == "public":
            print_info("🌍 Public template - visible to all users")
        elif visibility == "workspace":
            print_info("🏢 Workspace template - visible to workspace members")
        else:
            print_info("🔒 Private template - visible only to you")
        
        print_header("📋 Usage:")
        print_info(f"   infradsl registry install {workspace_prefix}{template_data['name']}")
        print_info(f"   from infradsl.templates import {template_data['class_name']}")
        
    except Exception as e:
        print_error(f"❌ Push error: {str(e)}")
        sys.exit(1)


@registry_cli.command('list')
@click.option('--workspace', '-w', help='List templates from specific workspace')
@click.option('--category', '-c', help='Filter by category')
@click.option('--provider', '-p', help='Filter by provider')
@click.option('--json', 'output_json', is_flag=True, help='Output in JSON format')
def list_cmd(workspace: Optional[str], category: Optional[str], provider: Optional[str], output_json: bool):
    """List available templates in the registry"""
    try:
        # Load registry credentials
        config_file = Path.home() / '.infradsl' / 'registry.json'
        if not config_file.exists():
            print_error("❌ Not authenticated. Run 'infradsl registry login' first")
            sys.exit(1)
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Initialize client
        client = RegistryClient(config['registry_url'])
        if 'user_info' in config:
            client.firebase_client.user_info = config['user_info']
        if 'auth_token' in config:
            client.firebase_client.auth_token = config['auth_token']
        client.workspace = config['workspace']
        
        # Get templates from Firestore
        search_workspace = workspace or client.workspace
        try:
            templates = client.firebase_client.get_templates(
                workspace=search_workspace,
                category=category
            )
            
            # Filter by provider if specified
            if provider:
                templates = [t for t in templates if provider in t.get('providers', [])]
                
        except Exception as e:
            print_warning(f"⚠️  Could not fetch from Firestore: {str(e)}")
            print_info("💡 Please login to the registry to see your templates...")
            
            # Apply filters for fallback
            if category:
                templates = [t for t in templates if t['category'] == category]
            if provider:
                templates = [t for t in templates if provider in t['providers']]
        
        if output_json:
            print(json.dumps(templates, indent=2))
            return
        
        if not templates:
            print_info("📭 No templates found")
            return
        
        print_header(f"📦 Found {len(templates)} template(s):")
        print_info("=" * 80)
        
        for template in templates:
            workspace_prefix = f"{template.get('workspaceId', template.get('workspace', ''))}/" if template.get('workspaceId') or template.get('workspace') else ""
            print_info(f"\n📦 {workspace_prefix}{template['name']}")
            print_info(f"   📝 {template['description']}")
            print_info(f"   📂 Category: {template['category']}")
            print_info(f"   ☁️  Providers: {', '.join(template['providers'])}")
            print_info(f"   🏷️  Tags: {', '.join(template.get('tags', []))}")
            print_info(f"   🏷️  Version: {template['version']}")
            print_info(f"   👁️  Visibility: {template.get('visibility', 'unknown')}")
        
    except Exception as e:
        print_error(f"❌ List error: {str(e)}")
        sys.exit(1)


@registry_cli.command('install')
@click.argument('template_name')
@click.option('--version', '-v', default='latest', help='Template version')
@click.option('--path', '-p', default='.', help='Installation path')
def install_cmd(template_name: str, version: str, path: str):
    """Install a template from the registry"""
    try:
        # Load registry credentials
        config_file = Path.home() / '.infradsl' / 'registry.json'
        if not config_file.exists():
            print_error("❌ Not authenticated. Run 'infradsl registry login' first")
            sys.exit(1)
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Initialize client
        client = RegistryClient(config['registry_url'])
        if 'user_info' in config:
            client.firebase_client.user_info = config['user_info']
        if 'auth_token' in config:
            client.firebase_client.auth_token = config['auth_token']
        client.workspace = config['workspace']
        
        # Extract workspace and template name
        if '/' in template_name:
            workspace_name, template_simple_name = template_name.split('/', 1)
        else:
            workspace_name = client.workspace
            template_simple_name = template_name
        
        # Try to get template from Firestore
        try:
            template = client.firebase_client.get_template(template_simple_name, workspace_name)
            
            if not template:
                print_error(f"❌ Template '{template_name}' not found in Firestore")
                sys.exit(1)
                
        except Exception as e:
            print_warning(f"⚠️  Could not fetch from Firestore: {str(e)}")
            print_info("💡 Using fallback to local templates...")
            
            # Fallback to demo templates
            template_file_map = {
                'infradsl/simple-vm': 'simple_vm.py',
                'infradsl/simple-webapp': 'simple_webapp.py'
            }
            
            if template_name not in template_file_map:
                print_error(f"❌ Template '{template_name}' not found")
                print_info("Available templates: infradsl/simple-vm, infradsl/simple-webapp")
                sys.exit(1)
            
            # Read template source from local file
            template_source_file = Path(__file__).parent.parent.parent.parent / 'company' / 'infradsl' / 'templates' / template_file_map[template_name]
            
            if not template_source_file.exists():
                print_error(f"❌ Template source file not found: {template_source_file}")
                sys.exit(1)
            
            with open(template_source_file, 'r') as f:
                source_code = f.read()
            
            # Create template info
            template = {
                'name': template_name.split('/')[-1],
                'version': version,
                'description': 'Local template from InfraDSL company registry',
                'className': 'SimpleVM' if 'vm' in template_name else 'SimpleWebApp',
                'sourceCode': source_code
            }
        
        # Create local file
        install_dir = Path(path) / '.infradsl' / 'templates'
        install_dir.mkdir(parents=True, exist_ok=True)
        
        template_file = install_dir / f"{template['name']}.py"
        
        # Write template to file
        with open(template_file, 'w') as f:
            f.write(f"# Template: {template['name']}\n")
            f.write(f"# Version: {template.get('version', 'latest')}\n")
            f.write(f"# Description: {template.get('description', 'Template from InfraDSL registry')}\n")
            f.write(f"# Downloaded: {datetime.now().isoformat()}\n\n")
            f.write(template.get('sourceCode', template.get('source_code', '')))
        
        print_success(f"✅ Template '{template['name']}' installed successfully!")
        print_info(f"📁 Location: {template_file}")
        print_info(f"🏷️  Version: {template.get('version', 'latest')}")
        
        print_header("📋 Usage:")
        class_name = template.get('className', template.get('class_name', template['name'].title()))
        print_info(f"   from .infradsl.templates.{template['name'].replace('-', '_')} import {class_name}")
        
    except Exception as e:
        print_error(f"❌ Install error: {str(e)}")
        sys.exit(1)


@registry_cli.command('delete')
@click.argument('template_name')
@click.option('--workspace', '-w', help='Workspace containing the template')
@click.option('--version', '-v', help='Specific version to delete (default: all versions)')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def delete_cmd(template_name: str, workspace: Optional[str], version: Optional[str], force: bool):
    """Delete a template from the registry"""
    try:
        # Load registry credentials
        config_file = Path.home() / '.infradsl' / 'registry.json'
        if not config_file.exists():
            print_error("❌ Not authenticated. Run 'infra registry login' first")
            sys.exit(1)
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Initialize client
        client = RegistryClient(config['registry_url'])
        if 'user_info' in config:
            client.firebase_client.user_info = config['user_info']
        if 'auth_token' in config:
            client.firebase_client.auth_token = config['auth_token']
        client.workspace = config['workspace']
        
        # Determine workspace and template name
        if '/' in template_name:
            workspace_name, template_simple_name = template_name.split('/', 1)
        else:
            workspace_name = workspace or client.workspace
            template_simple_name = template_name
        
        # Check if user has permission to delete from this workspace
        if workspace_name != client.workspace and client.workspace != 'infradsl':
            print_error(f"❌ You don't have permission to delete from workspace '{workspace_name}'")
            print_info(f"💡 You can only delete templates from your workspace: '{client.workspace}'")
            sys.exit(1)
        
        # Get template info before deletion
        try:
            template = client.firebase_client.get_template(template_simple_name, workspace_name)
            if not template:
                print_error(f"❌ Template '{workspace_name}/{template_simple_name}' not found")
                sys.exit(1)
        except Exception as e:
            print_error(f"❌ Failed to find template: {str(e)}")
            sys.exit(1)
        
        # Show template info
        print_header(f"🗑️  Template Deletion")
        print_info(f"📦 Template: {workspace_name}/{template_simple_name}")
        print_info(f"📝 Description: {template.get('description', 'No description')}")
        print_info(f"🏷️  Version: {template.get('version', 'unknown')}")
        print_info(f"👁️  Visibility: {template.get('visibility', 'unknown')}")
        print_info(f"🏢 Workspace: {workspace_name}")
        
        # Confirmation prompt (unless --force)
        if not force:
            print_header("⚠️  WARNING")
            print_warning("This action cannot be undone!")
            print_warning("All users will lose access to this template.")
            
            if not click.confirm("\nAre you sure you want to delete this template?"):
                print_info("❌ Deletion cancelled")
                return
        
        # Delete the template
        print_info("🗑️  Deleting template...")
        
        success = client.firebase_client.delete_template(template_simple_name, workspace_name, version)
        
        if success:
            print_success(f"✅ Template '{workspace_name}/{template_simple_name}' deleted successfully!")
            if version:
                print_info(f"🏷️  Deleted version: {version}")
            else:
                print_info("🏷️  Deleted all versions")
        else:
            print_error("❌ Failed to delete template")
            sys.exit(1)
        
    except Exception as e:
        print_error(f"❌ Delete error: {str(e)}")
        sys.exit(1)


def _load_template_class(template_path: Path):
    """Load template class from Python file"""
    spec = importlib.util.spec_from_file_location("template_module", template_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find template class (look for classes defined in this module, not imported)
    template_classes = []
    for name, obj in vars(module).items():
        if (isinstance(obj, type) and 
            not name.startswith('_') and 
            obj.__module__ == module.__name__):
            template_classes.append(obj)
    
    if not template_classes:
        raise ValueError("No template class found in file")
    
    # Prefer classes that have get_metadata method
    for cls in template_classes:
        if hasattr(cls, 'get_metadata'):
            return cls
    
    return template_classes[0]


def _get_source_code(template_path: Path) -> str:
    """Get source code from template file"""
    with open(template_path, 'r') as f:
        return f.read()
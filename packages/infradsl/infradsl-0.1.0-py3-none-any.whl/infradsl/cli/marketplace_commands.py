"""
InfraDSL Marketplace - CLI Commands

CLI interface for the InfraDSL marketplace registry operations including
authentication, template management, workspace operations, and publishing.
"""

import os
import sys
import json
import click
import importlib
from pathlib import Path
from typing import List, Optional

from ..marketplace.registry_client import RegistryClient, RegistryError, AuthenticationError
from ..marketplace.company_templates import create_company_template_loader


@click.group(name='marketplace')
def marketplace_cli():
    """InfraDSL marketplace and template registry commands"""
    pass


@marketplace_cli.command('login')
@click.option('--workspace', '-w', help='Workspace to authenticate with')
@click.option('--email', '-e', help='Email address')
def login_cmd(workspace: Optional[str], email: Optional[str]):
    """Authenticate with the InfraDSL marketplace"""
    try:
        client = RegistryClient(workspace=workspace)
        
        if client.login(email=email, interactive=True):
            if workspace:
                click.echo(f"✅ Authenticated with workspace '{workspace}'")
            else:
                click.echo("✅ Authenticated as individual user")
        else:
            click.echo("❌ Authentication failed")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Authentication error: {e}")
        sys.exit(1)


@marketplace_cli.command('logout')
def logout_cmd():
    """Logout from the marketplace"""
    client = RegistryClient()
    client.logout()


@marketplace_cli.command('whoami')
def whoami_cmd():
    """Show current authentication status"""
    try:
        client = RegistryClient()
        
        if not client.current_user:
            click.echo("❌ Not authenticated")
            click.echo("Run 'infradsl marketplace login' to authenticate")
            return
        
        click.echo("👤 Current User:")
        click.echo(f"   Email: {client.current_user.get('email', 'Unknown')}")
        click.echo(f"   Name: {client.current_user.get('name', 'Unknown')}")
        click.echo(f"   ID: {client.current_user.get('uid', 'Unknown')}")
        
        if client.workspace_info:
            click.echo(f"\n🏢 Workspace:")
            click.echo(f"   Name: {client.workspace_info.display_name}")
            click.echo(f"   ID: {client.workspace_info.name}")
            click.echo(f"   Members: {client.workspace_info.member_count}")
            click.echo(f"   Templates: {client.workspace_info.template_count}")
            click.echo(f"   Tier: {client.workspace_info.subscription_tier}")
        
    except Exception as e:
        click.echo(f"❌ Error getting user info: {e}")


@marketplace_cli.command('search')
@click.argument('query', required=False)
@click.option('--category', '-c', help='Filter by category')
@click.option('--provider', '-p', multiple=True, help='Filter by provider(s)')
@click.option('--tag', '-t', multiple=True, help='Filter by tag(s)')
@click.option('--workspace', '-w', help='Search within specific workspace')
@click.option('--limit', '-l', default=20, help='Maximum results to return')
@click.option('--json', 'output_json', is_flag=True, help='Output in JSON format')
def search_cmd(query: Optional[str], category: Optional[str], provider: tuple,
               tag: tuple, workspace: Optional[str], limit: int, output_json: bool):
    """Search for templates in the marketplace"""
    try:
        client = RegistryClient(workspace=workspace)
        
        # Search templates
        templates = client.search_templates(
            query=query or "",
            category=category or "",
            providers=list(provider),
            tags=list(tag),
            limit=limit
        )
        
        if output_json:
            # Output JSON format
            template_data = []
            for template in templates:
                template_data.append({
                    'id': template.id,
                    'name': template.name,
                    'display_name': template.display_name,
                    'description': template.description,
                    'workspace': template.workspace_id,
                    'category': template.category,
                    'providers': template.providers,
                    'tags': template.tags,
                    'version': template.latest_version,
                    'downloads': template.downloads,
                    'rating': template.rating,
                    'created_at': template.created_at.isoformat(),
                    'updated_at': template.updated_at.isoformat()
                })
            
            click.echo(json.dumps(template_data, indent=2))
            return
        
        # Human-readable output
        if not templates:
            click.echo("No templates found matching your criteria")
            return
        
        click.echo(f"📋 Found {len(templates)} template(s):")
        click.echo("=" * 60)
        
        for template in templates:
            workspace_prefix = ""
            if template.workspace_id:
                # Get workspace name for display
                workspace_prefix = f"{workspace}/" if workspace else "workspace/"
            
            click.echo(f"\n📦 {workspace_prefix}{template.name}")
            click.echo(f"   {template.description}")
            click.echo(f"   Category: {template.category}")
            click.echo(f"   Providers: {', '.join(template.providers)}")
            if template.tags:
                click.echo(f"   Tags: {', '.join(template.tags)}")
            click.echo(f"   Version: {template.latest_version}")
            click.echo(f"   Downloads: {template.downloads:,}")
            if template.rating > 0:
                stars = "⭐" * int(template.rating)
                click.echo(f"   Rating: {stars} ({template.rating:.1f})")
        
    except Exception as e:
        click.echo(f"❌ Search error: {e}")
        sys.exit(1)


@marketplace_cli.command('show')
@click.argument('template_ref')
@click.option('--version', '-v', default='latest', help='Template version')
@click.option('--source', '-s', is_flag=True, help='Show source code')
@click.option('--json', 'output_json', is_flag=True, help='Output in JSON format')
def show_cmd(template_ref: str, version: str, source: bool, output_json: bool):
    """Show detailed information about a template"""
    try:
        # Determine workspace from template reference
        workspace = None
        if '/' in template_ref:
            workspace = template_ref.split('/')[0]
        
        client = RegistryClient(workspace=workspace)
        template_data = client.get_template(template_ref, version)
        
        template = template_data['template']
        version_info = template_data['version']
        
        if output_json:
            click.echo(json.dumps({
                'template': template,
                'version': version_info,
                'source_code': template_data['source_code'] if source else None
            }, indent=2, default=str))
            return
        
        # Human-readable output
        click.echo(f"📦 {template['display_name']}")
        click.echo("=" * 60)
        click.echo(f"Name: {template['name']}")
        click.echo(f"Description: {template['description']}")
        click.echo(f"Category: {template['category']}")
        click.echo(f"Type: {template['template_type']}")
        click.echo(f"Visibility: {template['visibility']}")
        click.echo(f"Providers: {', '.join(template['providers'])}")
        
        if template['tags']:
            click.echo(f"Tags: {', '.join(template['tags'])}")
        
        click.echo(f"\n📊 Statistics:")
        stats = template['usage_stats']
        click.echo(f"   Downloads: {stats['total_downloads']:,}")
        click.echo(f"   Weekly downloads: {stats['weekly_downloads']:,}")
        click.echo(f"   Unique users: {stats['unique_users']:,}")
        if stats['average_rating'] > 0:
            stars = "⭐" * int(stats['average_rating'])
            click.echo(f"   Rating: {stars} ({stats['average_rating']:.1f}/5 from {stats['total_ratings']} reviews)")
        
        click.echo(f"\n🏷️  Version Information:")
        click.echo(f"   Current version: {version}")
        click.echo(f"   Latest version: {template['version_info']['latest_version']}")
        click.echo(f"   Total versions: {template['version_info']['total_versions']}")
        click.echo(f"   Created: {version_info['created_at']}")
        
        if version_info['changelog']:
            click.echo(f"   Changelog: {version_info['changelog']}")
        
        click.echo(f"\n⚙️  Requirements:")
        reqs = template['requirements']
        click.echo(f"   InfraDSL: {reqs['min_infradsl_version']}+")
        click.echo(f"   Python: {reqs['python_version']}")
        
        if source:
            click.echo(f"\n📄 Source Code:")
            click.echo("-" * 60)
            source_code = template_data['source_code']['python_class']
            click.echo(source_code)
        
    except Exception as e:
        click.echo(f"❌ Error getting template: {e}")
        sys.exit(1)


@marketplace_cli.command('install')
@click.argument('template_ref')
@click.option('--version', '-v', default='latest', help='Template version')
@click.option('--name', '-n', help='Local name for the template')
@click.option('--force', '-f', is_flag=True, help='Force overwrite existing template')
def install_cmd(template_ref: str, version: str, name: Optional[str], force: bool):
    """Install a template locally for use"""
    try:
        # Determine workspace from template reference
        workspace = None
        if '/' in template_ref:
            workspace = template_ref.split('/')[0]
        
        client = RegistryClient(workspace=workspace)
        template_data = client.get_template(template_ref, version)
        
        # Determine local installation path
        local_name = name or template_ref.replace('/', '_')
        install_dir = Path.cwd() / '.infradsl' / 'templates'
        install_dir.mkdir(parents=True, exist_ok=True)
        
        template_file = install_dir / f"{local_name}.py"
        
        if template_file.exists() and not force:
            click.echo(f"❌ Template '{local_name}' already exists")
            click.echo("Use --force to overwrite or --name to use a different name")
            sys.exit(1)
        
        # Write template source code to file
        source_code = template_data['source_code']['python_class']
        with open(template_file, 'w') as f:
            f.write(f"# Template: {template_ref}\n")
            f.write(f"# Version: {version}\n")
            f.write(f"# Installed: {datetime.utcnow().isoformat()}\n\n")
            
            # Add dependencies as imports
            for dep in template_data['source_code'].get('dependencies', []):
                f.write(f"{dep}\n")
            
            f.write("\n")
            f.write(source_code)
        
        click.echo(f"✅ Installed template '{template_ref}' as '{local_name}'")
        click.echo(f"📁 Location: {template_file}")
        click.echo(f"\n💡 Usage:")
        click.echo(f"   from .infradsl.templates.{local_name} import TemplateClass")
        
    except Exception as e:
        click.echo(f"❌ Installation error: {e}")
        sys.exit(1)


@marketplace_cli.command('publish')
@click.argument('template_file')
@click.option('--name', '-n', help='Template name (auto-detected if not provided)')
@click.option('--description', '-d', help='Template description')
@click.option('--version', '-v', default='1.0.0', help='Template version')
@click.option('--visibility', default='workspace', 
              type=click.Choice(['private', 'workspace', 'public']),
              help='Template visibility')
@click.option('--category', '-c', default='resource',
              type=click.Choice(['resource', 'pattern', 'blueprint', 'component']),
              help='Template category')
@click.option('--provider', '-p', multiple=True, help='Supported provider(s)')
@click.option('--tag', '-t', multiple=True, help='Template tag(s)')
@click.option('--workspace', '-w', help='Publish to specific workspace')
@click.option('--dry-run', is_flag=True, help='Show what would be published without actually publishing')
def publish_cmd(template_file: str, name: Optional[str], description: Optional[str],
               version: str, visibility: str, category: str, provider: tuple,
               tag: tuple, workspace: Optional[str], dry_run: bool):
    """Publish a template to the marketplace"""
    try:
        # Validate template file exists
        template_path = Path(template_file)
        if not template_path.exists():
            click.echo(f"❌ Template file not found: {template_file}")
            sys.exit(1)
        
        # Load and validate template class
        template_class = _load_template_class(template_path)
        
        # Auto-detect template name if not provided
        if not name:
            name = template_class.__name__.lower().replace('_', '-')
        
        # Prompt for description if not provided
        if not description:
            description = click.prompt("Template description")
        
        if dry_run:
            click.echo("🔍 Dry run - would publish:")
            click.echo(f"   Name: {name}")
            click.echo(f"   Description: {description}")
            click.echo(f"   Version: {version}")
            click.echo(f"   Visibility: {visibility}")
            click.echo(f"   Category: {category}")
            click.echo(f"   Providers: {list(provider)}")
            click.echo(f"   Tags: {list(tag)}")
            click.echo(f"   Workspace: {workspace or 'personal'}")
            click.echo(f"   Class: {template_class.__name__}")
            return
        
        # Initialize registry client
        client = RegistryClient(workspace=workspace)
        
        # Ensure authenticated
        if not client.current_user:
            click.echo("❌ Not authenticated. Run 'infradsl marketplace login' first")
            sys.exit(1)
        
        # Publish template
        template_id = client.publish_template(
            template_class=template_class,
            name=name,
            description=description,
            version=version,
            visibility=visibility,
            category=category,
            providers=list(provider),
            tags=list(tag)
        )
        
        workspace_prefix = f"{workspace}/" if workspace else ""
        click.echo(f"✅ Published template '{workspace_prefix}{name}' version {version}")
        click.echo(f"📦 Template ID: {template_id}")
        
        if visibility == "public":
            click.echo(f"🌍 Public template - visible to all users")
        elif visibility == "workspace":
            click.echo(f"🏢 Workspace template - visible to workspace members")
        else:
            click.echo(f"🔒 Private template - visible only to you")
        
    except Exception as e:
        click.echo(f"❌ Publishing error: {e}")
        sys.exit(1)


@marketplace_cli.command('workspace')
@click.argument('action', type=click.Choice(['create', 'list', 'info', 'members']))
@click.argument('workspace_name', required=False)
@click.option('--display-name', help='Workspace display name')
@click.option('--description', help='Workspace description')
def workspace_cmd(action: str, workspace_name: Optional[str], display_name: Optional[str],
                 description: Optional[str]):
    """Manage workspaces"""
    try:
        client = RegistryClient()
        
        if action == "create":
            if not workspace_name:
                workspace_name = click.prompt("Workspace name (URL-safe)")
            
            if not display_name:
                display_name = click.prompt("Display name")
            
            if not description:
                description = click.prompt("Description", default="")
            
            workspace_id = client.create_workspace(
                name=workspace_name,
                display_name=display_name,
                description=description
            )
            
            click.echo(f"✅ Created workspace '{display_name}' ({workspace_name})")
            click.echo(f"🆔 Workspace ID: {workspace_id}")
            click.echo(f"\n💡 Usage:")
            click.echo(f"   infradsl marketplace login --workspace {workspace_name}")
            
        elif action == "list":
            # This would list user's workspaces
            click.echo("📋 Your Workspaces:")
            click.echo("(This would list workspaces from user profile)")
            
        elif action == "info":
            if not workspace_name:
                workspace_name = click.prompt("Workspace name")
            
            # Show workspace information
            click.echo(f"🏢 Workspace: {workspace_name}")
            click.echo("(This would show workspace details)")
            
        elif action == "members":
            if not workspace_name:
                workspace_name = click.prompt("Workspace name")
            
            # Show workspace members
            click.echo(f"👥 Members of {workspace_name}:")
            click.echo("(This would list workspace members)")
        
    except Exception as e:
        click.echo(f"❌ Workspace error: {e}")
        sys.exit(1)


@marketplace_cli.command('import')
@click.argument('template_ref')
@click.option('--version', '-v', default='latest', help='Template version')
@click.option('--alias', '-a', help='Import alias name')
@click.option('--example', '-e', is_flag=True, help='Show usage example')
def import_cmd(template_ref: str, version: str, alias: Optional[str], example: bool):
    """Import a template for use in your code"""
    try:
        # Determine workspace from template reference
        workspace = None
        if '/' in template_ref:
            workspace = template_ref.split('/')[0]
        
        client = RegistryClient(workspace=workspace)
        
        # Get template information
        template_data = client.get_template(template_ref, version)
        template = template_data['template']
        
        # Generate import statement
        if workspace:
            import_name = alias or template['name'].replace('-', '_')
            import_statement = f"from infradsl.marketplace.{workspace} import {import_name}"
        else:
            import_name = alias or template['name'].replace('-', '_')
            import_statement = f"from infradsl.marketplace import {import_name}"
        
        click.echo("📦 Template Import Information:")
        click.echo("=" * 50)
        click.echo(f"Template: {template['display_name']}")
        click.echo(f"Version: {version}")
        click.echo(f"Category: {template['category']}")
        click.echo(f"\n📋 Import Statement:")
        click.echo(f"   {import_statement}")
        
        if example:
            click.echo(f"\n💡 Usage Example:")
            click.echo(f"   # Import the template")
            click.echo(f"   {import_statement}")
            click.echo(f"")
            click.echo(f"   # Use the template")
            click.echo(f"   resource = {import_name}('my-resource')")
            click.echo(f"   resource.create()")
        
        # Record usage analytics
        client._record_usage(template['id'], version, "import")
        
    except Exception as e:
        click.echo(f"❌ Import error: {e}")
        sys.exit(1)


def _load_template_class(template_path: Path):
    """Load template class from Python file"""
    import importlib.util
    
    # Load module from file
    spec = importlib.util.spec_from_file_location("template_module", template_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find template class (look for classes that might be templates)
    template_classes = []
    for name, obj in vars(module).items():
        if isinstance(obj, type) and not name.startswith('_'):
            # Check if it looks like a template class
            if hasattr(obj, '__bases__') and len(obj.__bases__) > 0:
                template_classes.append(obj)
    
    if not template_classes:
        raise ValueError("No template class found in file")
    
    if len(template_classes) > 1:
        # If multiple classes, look for one that seems like the main template
        for cls in template_classes:
            if any(base.__name__.endswith(('VM', 'Database', 'Storage', 'Resource')) 
                   for base in cls.__bases__):
                return cls
        
        # If no clear main class, use the first one
        return template_classes[0]
    
    return template_classes[0]


# Add marketplace commands to main CLI
def register_marketplace_commands(cli_group):
    """Register marketplace commands with the main CLI"""
    cli_group.add_command(marketplace_cli)
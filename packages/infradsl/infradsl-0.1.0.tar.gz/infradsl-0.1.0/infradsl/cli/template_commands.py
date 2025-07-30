"""
InfraDSL Template Marketplace CLI Commands

CLI interface for template discovery, generation, and management.
"""

import sys
import click
from typing import Dict, Any, Optional
from ..core.template_engine import get_marketplace, TemplateParameter


@click.group(name='template')
def template_cli():
    """Template marketplace commands"""
    pass


@template_cli.command('search')
@click.option('--query', '-q', help='Search query')
@click.option('--category', '-c', help='Filter by category')
@click.option('--provider', '-p', help='Filter by provider')
@click.option('--featured', '-f', is_flag=True, help='Show only featured templates')
def search_templates(query: str = "", category: str = "", provider: str = "", featured: bool = False):
    """Search for templates in the marketplace"""
    marketplace = get_marketplace()
    results = marketplace.search_templates(query, category, provider, featured)
    
    if not results:
        print("🔍 No templates found matching your criteria")
        return
    
    print(f"🔍 Search Results: {len(results)} template(s) found")
    print()
    
    for template_registry in results[:10]:  # Show top 10 results
        metadata = template_registry.metadata
        
        # Display template info
        featured_badge = "🌟 FEATURED" if metadata.featured else ""
        enterprise_badge = "💎 ENTERPRISE" if metadata.pricing_type == "enterprise" else ""
        
        badges = " ".join(filter(None, [featured_badge, enterprise_badge]))
        
        print(f"📦 {metadata.name} (⭐ {metadata.rating}, {metadata.downloads:,} downloads) {badges}")
        print(f"   {metadata.description}")
        print(f"   🏷️  Category: {metadata.category} | Providers: {', '.join(metadata.providers)}")
        
        if metadata.pricing_type != "free":
            price_text = f"${metadata.price}/month" if metadata.pricing_type == "subscription" else f"${metadata.price}"
            print(f"   💰 {price_text}")
        
        print()


@template_cli.command('browse')
@click.option('--category', '-c', help='Browse by category')
@click.option('--provider', '-p', help='Browse by provider')
@click.option('--trending', '-t', is_flag=True, help='Show trending templates')
@click.option('--featured', '-f', is_flag=True, help='Show featured templates')
def browse_templates(category: str = "", provider: str = "", trending: bool = False, featured: bool = False):
    """Browse templates by category or provider"""
    marketplace = get_marketplace()
    
    if category:
        print(f"📂 Category: {category}")
        results = marketplace.search_templates(category=category)
    elif provider:
        print(f"☁️ Provider: {provider}")
        results = marketplace.search_templates(provider=provider)
    elif trending:
        print(f"📈 Trending Templates")
        results = marketplace.search_templates()
        results = sorted(results, key=lambda x: x.metadata.downloads, reverse=True)[:5]
    elif featured:
        print(f"🌟 Featured Templates")
        results = marketplace.search_templates(featured=True)
    else:
        print(f"📚 All Templates")
        results = marketplace.search_templates()
    
    if not results:
        print("No templates found")
        return
    
    print()
    for template_registry in results:
        metadata = template_registry.metadata
        print(f"📦 {metadata.name} - {metadata.description}")
        print(f"   ⭐ {metadata.rating}/5 | {metadata.downloads:,} downloads | {', '.join(metadata.providers)}")
        print()


@template_cli.command('info')
@click.argument('template_name')
def template_info(template_name: str):
    """Show detailed information about a template"""
    marketplace = get_marketplace()
    template = marketplace.get_template(template_name)
    
    if not template:
        print(f"❌ Template '{template_name}' not found")
        return
    
    metadata = template.metadata
    
    print(f"📦 Template: {metadata.name} v{metadata.version}")
    print(f"👤 Author: {metadata.author}")
    print(f"📝 Description: {metadata.description}")
    print(f"🏷️  Category: {metadata.category}")
    print(f"📄 License: {metadata.license}")
    print()
    
    print(f"⭐ Rating: {metadata.rating}/5 ({metadata.reviews} reviews)")
    print(f"📥 Downloads: {metadata.downloads:,}")
    print(f"☁️ Providers: {', '.join(metadata.providers)}")
    print()
    
    if metadata.pricing_type != "free":
        price_text = f"${metadata.price}/month" if metadata.pricing_type == "subscription" else f"${metadata.price}"
        print(f"💰 Price: {price_text}")
        print()
    
    if metadata.intelligence_enabled:
        print(f"🧠 Intelligence Features:")
        print(f"   ✅ Drift detection: {'Enabled' if metadata.drift_detection else 'Disabled'}")
        print(f"   🛡️ Auto-remediation: {metadata.auto_remediation}")
        print(f"   🎓 Learning mode: {'Available' if metadata.learning_mode else 'Not available'}")
        print()
    
    if metadata.tags:
        print(f"🏷️  Tags: {', '.join(metadata.tags)}")
        print()
    
    print(f"⚙️  Parameters:")
    for param in metadata.parameters:
        required_text = "required" if param.required else "optional"
        default_text = f" (default: {param.default})" if param.default is not None else ""
        print(f"   • {param.name} ({param.type}, {required_text}): {param.description}{default_text}")
    
    print()
    print(f"🚀 Generate: infra generate {template_name}")


@template_cli.command('generate')
@click.argument('template_name')
@click.option('--interactive', '-i', is_flag=True, help='Interactive parameter input')
@click.option('--output', '-o', default='.', help='Output directory')
def generate_template(template_name: str, interactive: bool = False, output: str = '.'):
    """Generate infrastructure code from a template"""
    marketplace = get_marketplace()
    template = marketplace.get_template(template_name)
    
    if not template:
        print(f"❌ Template '{template_name}' not found")
        print()
        print("💡 Search for templates with: infra template search")
        return
    
    metadata = template.metadata
    config = {}
    
    if interactive:
        print(f"🚀 InfraDSL Template Generator")
        print(f"📦 Template: {metadata.description} v{metadata.version}")
        print(f"⭐ Rating: {metadata.rating}/5 ({metadata.reviews} reviews) | {metadata.downloads:,} downloads")
        print()
        
        if metadata.intelligence_enabled:
            print(f"✅ Intelligence Features:")
            print(f"   🧠 Drift detection enabled")
            print(f"   🛡️ Auto-remediation ({metadata.auto_remediation})")
            print(f"   🎓 Learning mode available")
            print()
        
        print(f"📋 Configuration:")
        
        # Collect parameters interactively
        for param in metadata.parameters:
            prompt_text = f"? {param.description}"
            
            if param.type == "string":
                if param.required:
                    value = click.prompt(prompt_text, type=str)
                else:
                    value = click.prompt(prompt_text, type=str, default=param.default or "", show_default=True)
                config[param.name] = value
                
            elif param.type == "integer":
                if param.required:
                    value = click.prompt(prompt_text, type=int)
                else:
                    value = click.prompt(prompt_text, type=int, default=param.default or 0, show_default=True)
                config[param.name] = value
                
            elif param.type == "boolean":
                default_value = param.default if param.default is not None else False
                value = click.confirm(prompt_text, default=default_value)
                config[param.name] = value
                
            elif param.type == "select" and param.options:
                # Show available options
                if "all" in param.options:
                    options = param.options["all"]
                else:
                    # Provider-specific options would need provider selection first
                    options = list(param.options.values())[0] if param.options else []
                
                if options:
                    print(f"   Options: {', '.join(options)}")
                    while True:
                        value = click.prompt(prompt_text, type=str, default=param.default)
                        if value in options:
                            config[param.name] = value
                            break
                        else:
                            print(f"   Invalid option. Choose from: {', '.join(options)}")
                else:
                    value = click.prompt(prompt_text, type=str, default=param.default or "")
                    config[param.name] = value
        
        # Ask for provider if not specified
        if "provider" not in config:
            print(f"   Available providers: {', '.join(metadata.providers)}")
            while True:
                provider = click.prompt("? Provider", type=str, default=metadata.providers[0])
                if provider in metadata.providers:
                    config["provider"] = provider
                    break
                else:
                    print(f"   Invalid provider. Choose from: {', '.join(metadata.providers)}")
        
        print()
    else:
        # Use defaults for non-interactive mode
        config = {
            "app_name": "my-app",
            "provider": metadata.providers[0],
            "environment": "production"
        }
        
        for param in metadata.parameters:
            if param.default is not None:
                config[param.name] = param.default
    
    # Generate the template
    success = marketplace.generate_template(template_name, config, output)
    
    if success:
        print()
        print(f"🎮 Intelligence configured with auto-remediation support!")
        print()
        print(f"💡 Next steps:")
        print(f"   1. Review generated files")
        print(f"   2. Run: infra preview <generated-file>")
        print(f"   3. Deploy: infra apply <generated-file>")
    else:
        print(f"❌ Failed to generate template")
        sys.exit(1)


@template_cli.command('categories')
def list_categories():
    """List all template categories"""
    marketplace = get_marketplace()
    categories = marketplace.list_categories()
    
    print("📂 Available Categories:")
    for category in categories:
        print(f"   • {category}")
    
    print()
    print("💡 Browse category: infra template browse --category <name>")


@template_cli.command('providers')
def list_providers():
    """List all supported providers"""
    marketplace = get_marketplace()
    providers = marketplace.list_providers()
    
    print("☁️ Supported Providers:")
    for provider in providers:
        print(f"   • {provider}")
    
    print()
    print("💡 Browse provider: infra template browse --provider <name>")


# Alias commands for convenience
@click.command('generate')
@click.argument('template_name')
@click.option('--interactive', '-i', is_flag=True, help='Interactive parameter input')
@click.option('--output', '-o', default='.', help='Output directory')
def generate_shortcut(template_name: str, interactive: bool = False, output: str = '.'):
    """Generate infrastructure code from a template (shortcut)"""
    # This is a shortcut that can be called directly as 'infra generate'
    generate_template.callback(template_name, interactive, output)


# Export commands
__all__ = ['template_cli', 'generate_shortcut']
"""
BuildPush - Universal Template Builder and Publisher

This module provides a simplified, Rails-like interface for creating and
publishing InfraDSL templates to the registry.
"""

import os
import sys
import json
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class BuildPush:
    """
    Universal template builder and pusher for InfraDSL registry.
    
    Example:
        BuildPush(
            resources=["webapp", "database", "redis"],
            name="full-stack-app",
            description="Complete web application stack",
            tags=["production", "scalable"]
        )
    """
    
    def __init__(self,
                 resources: List[str],
                 name: str = None,
                 description: str = None,
                 tags: List[str] = None,
                 version: str = "1.0.0",
                 visibility: str = "workspace",
                 auto_push: bool = True):
        """
        Initialize BuildPush with resource configuration.
        
        Args:
            resources: List of resource names or paths to include
            name: Template name (auto-generated if not provided)
            description: Template description
            tags: List of tags for the template
            version: Template version (default: 1.0.0)
            visibility: Template visibility - private, workspace, or public (default: workspace)
            auto_push: Automatically push to registry after building (default: True)
        """
        self.resources = resources
        self.name = name or self._generate_name(resources)
        self.description = description or self._generate_description(resources)
        self.tags = tags or self._generate_tags(resources)
        self.version = version
        self.visibility = visibility
        self.auto_push = auto_push
        
        # Auto-detect providers and categories
        self.providers = self._detect_providers(resources)
        self.categories = self._detect_categories(resources)
        
        # Build and optionally push
        if auto_push:
            self.build_and_push()
        else:
            self.build()
    
    def _generate_name(self, resources: List[str]) -> str:
        """Generate a template name from resources"""
        if len(resources) == 1:
            return f"{resources[0]}-template"
        elif len(resources) <= 3:
            return "-".join(resources) + "-stack"
        else:
            return "multi-resource-stack"
    
    def _generate_description(self, resources: List[str]) -> str:
        """Generate a description from resources, checking for markdown docs first"""
        # Check if we have markdown documentation for any of the resources
        template_docs = self._find_template_docs(resources)
        if template_docs:
            return template_docs.get('description', self._default_description(resources))
        
        return self._default_description(resources)
    
    def _default_description(self, resources: List[str]) -> str:
        """Generate default description from resources"""
        if len(resources) == 1:
            return f"InfraDSL template for {resources[0]}"
        else:
            return f"InfraDSL stack with {', '.join(resources)}"
    
    def _find_template_docs(self, resources: List[str]) -> Dict[str, Any]:
        """Find and parse markdown documentation for resources"""
        # Look for markdown files in common template locations
        search_paths = [
            Path(__file__).parent.parent.parent.parent / 'company' / 'infradsl' / 'templates',
            Path.cwd() / 'templates',
            Path.cwd() / 'docs'
        ]
        
        for resource in resources:
            for search_path in search_paths:
                md_file = search_path / f"{resource.replace('-', '_')}.md"
                if md_file.exists():
                    return self._parse_markdown_template(md_file)
                
                # Also try exact match
                md_file = search_path / f"{resource}.md"
                if md_file.exists():
                    return self._parse_markdown_template(md_file)
        
        return {}
    
    def _parse_markdown_template(self, md_file: Path) -> Dict[str, Any]:
        """Parse markdown template file for metadata"""
        try:
            content = md_file.read_text()
            metadata = {}
            
            lines = content.split('\n')
            
            # Parse frontmatter-style metadata at the top
            for line in lines[:20]:  # Only check first 20 lines
                line = line.strip()
                
                if line.startswith('**Category:**'):
                    metadata['category'] = line.replace('**Category:**', '').strip().lower()
                elif line.startswith('**Providers:**'):
                    providers = line.replace('**Providers:**', '').strip()
                    metadata['providers'] = [p.strip().lower() for p in providers.split(',')]
                elif line.startswith('**Version:**'):
                    metadata['version'] = line.replace('**Version:**', '').strip()
                elif line.startswith('**Author:**'):
                    metadata['author'] = line.replace('**Author:**', '').strip()
                elif line.startswith('## Description'):
                    # Find the description paragraph
                    desc_lines = []
                    i = lines.index(line) + 1
                    while i < len(lines) and not lines[i].startswith('##'):
                        if lines[i].strip():
                            desc_lines.append(lines[i].strip())
                        i += 1
                    metadata['description'] = ' '.join(desc_lines)
            
            # Extract tags from the end of the file
            tags_section = content.split('## Tags')
            if len(tags_section) > 1:
                tags_text = tags_section[-1].strip()
                # Extract tags from backticks
                import re
                tags = re.findall(r'`([^`]+)`', tags_text)
                metadata['tags'] = tags
            
            return metadata
            
        except Exception as e:
            print(f"⚠️  Warning: Could not parse {md_file}: {e}")
            return {}
    
    def _generate_tags(self, resources: List[str]) -> List[str]:
        """Generate tags from resources, checking markdown docs first"""
        # Check if we have markdown documentation with tags
        template_docs = self._find_template_docs(resources)
        if template_docs and 'tags' in template_docs:
            return template_docs['tags']
        
        # Fall back to auto-generation
        tags = []
        
        # Add resource-specific tags
        for resource in resources:
            if "web" in resource.lower() or "app" in resource.lower():
                tags.extend(["webapp", "frontend"])
            if "database" in resource.lower() or "db" in resource.lower():
                tags.extend(["database", "storage"])
            if "api" in resource.lower():
                tags.extend(["api", "backend"])
            if "redis" in resource.lower() or "cache" in resource.lower():
                tags.extend(["cache", "performance"])
            if "queue" in resource.lower() or "worker" in resource.lower():
                tags.extend(["queue", "async"])
        
        # Remove duplicates
        return list(set(tags))
    
    def _detect_providers(self, resources: List[str]) -> List[str]:
        """Auto-detect cloud providers from resources, checking markdown docs first"""
        # Check if we have markdown documentation with providers
        template_docs = self._find_template_docs(resources)
        if template_docs and 'providers' in template_docs:
            return template_docs['providers']
        
        # Fall back to auto-detection
        providers = set()
        
        for resource in resources:
            # Check if resource is a file path
            if os.path.exists(resource):
                content = Path(resource).read_text()
            else:
                # Assume it's a resource name, check common patterns
                content = resource.lower()
            
            # Detect providers from content
            if any(keyword in content for keyword in ["ec2", "s3", "rds", "lambda", "aws"]):
                providers.add("aws")
            if any(keyword in content for keyword in ["gcp", "gke", "cloud_run", "bigquery", "googlecloud"]):
                providers.add("gcp")
            if any(keyword in content for keyword in ["droplet", "spaces", "digitalocean", "do_"]):
                providers.add("digitalocean")
        
        # Default to all providers if none detected
        return list(providers) if providers else ["aws", "gcp", "digitalocean"]
    
    def _detect_categories(self, resources: List[str]) -> List[str]:
        """Auto-detect categories from resources, checking markdown docs first"""
        # Check if we have markdown documentation with category
        template_docs = self._find_template_docs(resources)
        if template_docs and 'category' in template_docs:
            return [template_docs['category']]
        
        # Fall back to auto-detection
        categories = set()
        
        category_patterns = {
            "compute": ["vm", "ec2", "droplet", "instance", "server", "container"],
            "storage": ["s3", "storage", "bucket", "spaces", "disk", "volume"],
            "network": ["vpc", "subnet", "firewall", "load_balancer", "cdn", "dns"],
            "database": ["rds", "postgres", "mysql", "mongodb", "redis", "cache", "db"],
            "serverless": ["lambda", "function", "cloud_run", "api_gateway"],
            "security": ["iam", "firewall", "security_group", "ssl", "certificate"]
        }
        
        for resource in resources:
            resource_lower = resource.lower()
            for category, patterns in category_patterns.items():
                if any(pattern in resource_lower for pattern in patterns):
                    categories.add(category)
        
        # Default to compute if no category detected
        return list(categories) if categories else ["compute"]
    
    def build(self) -> Dict[str, Any]:
        """Build the template configuration"""
        print(f"🔨 Building template: {self.name}")
        
        # Create template structure
        template_data = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "visibility": self.visibility,
            "providers": self.providers,
            "categories": self.categories,
            "tags": self.tags,
            "resources": self.resources,
            "created_at": datetime.now().isoformat(),
            "author": os.getenv("USER", "unknown")
        }
        
        # Generate template code
        template_code = self._generate_template_code()
        template_data["source_code"] = template_code
        
        print(f"✅ Template built successfully!")
        print(f"📦 Name: {self.name}")
        print(f"📝 Description: {self.description}")
        print(f"☁️  Providers: {', '.join(self.providers)}")
        print(f"📂 Categories: {', '.join(self.categories)}")
        print(f"🏷️  Tags: {', '.join(self.tags)}")
        
        return template_data
    
    def _validate_python_naming(self, class_name: str) -> bool:
        """Validate that the generated class name is Python-compatible"""
        if not class_name.isidentifier():
            print(f"❌ Generated class name '{class_name}' is not a valid Python identifier")
            return False
        
        if '-' in class_name or '_' in class_name:
            print(f"❌ Generated class name '{class_name}' should use CamelCase")
            return False
        
        if not class_name[0].isupper():
            print(f"❌ Generated class name '{class_name}' should start with uppercase letter")
            return False
        
        return True
    
    def _generate_template_code(self) -> str:
        """Generate the template Python code"""
        imports = []
        class_body = []
        
        # Generate imports based on resources
        for resource in self.resources:
            if os.path.exists(resource):
                # It's a file, parse it to extract imports
                content = Path(resource).read_text()
                # Simple import extraction (could be enhanced)
                for line in content.split('\n'):
                    if line.strip().startswith('from infradsl') or line.strip().startswith('import infradsl'):
                        imports.append(line.strip())
            else:
                # It's a resource name, generate standard import
                imports.append(f"from infradsl.resources import {resource.title()}")
        
        # Remove duplicate imports
        imports = list(set(imports))
        
        # Generate class code - ensure it's CamelCase and Python-compatible
        class_name = "".join(word.title() for word in self.name.replace("-", "_").split("_"))
        
        # Validate the generated class name
        if not self._validate_python_naming(class_name):
            # Try to fix common issues
            class_name = ''.join(word.capitalize() for word in self.name.replace('-', '_').split('_'))
            if not self._validate_python_naming(class_name):
                # Fall back to a safe name
                class_name = "GeneratedTemplate"
                print(f"⚠️  Using fallback class name: {class_name}")
        
        print(f"🐍 Generated Python class: {class_name}")
        
        template_code = f'''"""
{self.description}

Auto-generated by InfraDSL BuildPush
"""

{chr(10).join(imports)}


class {class_name}:
    """
    {self.description}
    
    Resources:
    {chr(10).join(f"    - {r}" for r in self.resources)}
    """
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.config = kwargs
        self._setup_resources()
    
    def _setup_resources(self):
        """Initialize all resources"""
        # TODO: Add resource initialization based on template
        pass
    
    def create(self):
        """Create all resources"""
        print(f"🚀 Creating {{self.name}} stack...")
        # TODO: Add resource creation logic
        print(f"✅ Stack {{self.name}} created successfully!")
    
    def destroy(self):
        """Destroy all resources"""
        print(f"🗑️  Destroying {{self.name}} stack...")
        # TODO: Add resource destruction logic
        print(f"✅ Stack {{self.name}} destroyed successfully!")
    
    @staticmethod
    def get_metadata():
        """Return template metadata"""
        return {{
            "name": "{self.name}",
            "description": "{self.description}",
            "providers": {self.providers},
            "tags": {self.tags},
            "version": "{self.version}"
        }}
'''
        
        return template_code
    
    def push(self, template_data: Dict[str, Any] = None):
        """Push the template to the registry"""
        if not template_data:
            template_data = self.build()
        
        print(f"\n📤 Pushing template to registry...")
        
        # Save template to temporary file
        temp_file = Path(f"/tmp/{self.name}.py")
        temp_file.write_text(template_data["source_code"])
        
        # Use the primary category for the push command
        primary_category = self.categories[0] if self.categories else "compute"
        
        # Build infra registry push command
        cmd = [
            "infra", "registry", "push", str(temp_file),
            "--name", self.name,
            "--description", self.description,
            "--version", self.version,
            "--visibility", self.visibility,
            "--category", primary_category
        ]
        
        # Add providers
        for provider in self.providers:
            cmd.extend(["--provider", provider])
        
        # Add tags
        for tag in self.tags:
            cmd.extend(["--tag", tag])
        
        print(f"🔧 Command: {' '.join(cmd)}")
        
        # Execute push command
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Template pushed successfully!")
                print(result.stdout)
            else:
                print(f"❌ Push failed!")
                print(result.stderr)
                sys.exit(1)
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
    
    def build_and_push(self):
        """Build and push the template in one step"""
        template_data = self.build()
        self.push(template_data)


# Convenience function
def build_push(resources: List[str], **kwargs):
    """
    Convenience function to build and push a template.
    
    Example:
        build_push(["webapp", "database"], name="my-app", tags=["production"])
    """
    return BuildPush(resources, **kwargs)

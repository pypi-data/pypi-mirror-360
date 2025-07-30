"""
InfraDSL Registry - Dynamic Template Imports

This module enables direct imports from the registry without manual installation:
    from infradsl.registry.infradsl import SimpleVM
    from infradsl.registry.company import ProductionDB, GameService

Templates are automatically fetched from the registry on first import and cached locally.
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from typing import Any, Optional
import requests
from datetime import datetime


class RegistryImporter:
    """Dynamic importer for registry templates"""
    
    def __init__(self):
        self.registry_url = os.getenv('INFRADSL_REGISTRY_URL', 'http://localhost:5174')
        self.cache_dir = Path.home() / '.infradsl' / 'registry_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.auth_config = self._load_auth_config()
    
    def _load_auth_config(self) -> Optional[dict]:
        """Load authentication config if available"""
        config_file = Path.home() / '.infradsl' / 'registry.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return None
    
    def _get_template_from_registry(self, workspace: str, template_name: str) -> dict:
        """Fetch template from registry (Firestore or fallback to local)"""
        try:
            # Try to get from Firestore first
            from ..cli.firebase_client import FirebaseClient
            
            # Load auth info if available
            config_file = Path.home() / '.infradsl' / 'registry.json'
            firebase_client = None
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                firebase_client = FirebaseClient(project_id="infradsl")
                if 'user_info' in config:
                    firebase_client.user_info = config['user_info']
                    firebase_client.auth_token = config['user_info'].get('idToken')
                
                # Try to get template from Firestore
                template = firebase_client.get_template(template_name, workspace)
                if template:
                    return {
                        'name': template_name,
                        'workspace': workspace,
                        'version': template.get('version', '1.0.0'),
                        'source_code': template.get('sourceCode', ''),
                        'class_name': template.get('className', template_name.title()),
                        'description': template.get('description', f'Registry template: {template_name}'),
                        'cached_at': datetime.now().isoformat()
                    }
        
        except Exception as e:
            print(f"⚠️  Could not fetch from Firestore: {str(e)}")
        
        # Fallback to local demo templates
        template_file_map = {
            'simple-vm': 'simple_vm.py',
            'simple-webapp': 'simple_webapp.py'
        }
        
        if template_name in template_file_map:
            # Load from local company templates
            templates_dir = Path(__file__).parent.parent.parent.parent / 'company' / 'infradsl' / 'templates'
            template_file = templates_dir / template_file_map[template_name]
            
            if template_file.exists():
                with open(template_file, 'r') as f:
                    source_code = f.read()
                
                # Try to load metadata from DESCRIPTION.md
                metadata = self._load_description_metadata(templates_dir)
                
                return {
                    'name': template_name,
                    'workspace': workspace,
                    'version': metadata.get('version', '1.0.0'),
                    'source_code': source_code,
                    'class_name': 'SimpleVM' if 'vm' in template_name else 'SimpleWebApp',
                    'description': metadata.get('description', f'Registry template: {template_name}'),
                    'category': metadata.get('category', 'general'),
                    'providers': metadata.get('providers', ['gcp']),
                    'tags': metadata.get('tags', []),
                    'cached_at': datetime.now().isoformat()
                }
        
        # Fallback error
        raise ImportError(f"Template '{workspace}/{template_name}' not found in registry")
    
    def _load_description_metadata(self, templates_dir: Path) -> dict:
        """Load metadata from DESCRIPTION.md file"""
        description_file = templates_dir / 'DESCRIPTION.md'
        metadata = {}
        
        if not description_file.exists():
            return metadata
        
        try:
            with open(description_file, 'r') as f:
                content = f.read()
            
            # Parse frontmatter-style metadata
            lines = content.split('\n')
            in_metadata = False
            
            for line in lines:
                line = line.strip()
                
                # Look for metadata patterns
                if line.startswith('**Category:**'):
                    metadata['category'] = line.replace('**Category:**', '').strip().lower()
                elif line.startswith('**Providers:**'):
                    providers = line.replace('**Providers:**', '').strip()
                    metadata['providers'] = [p.strip().lower() for p in providers.split(',')]
                elif line.startswith('**Version:**'):
                    metadata['version'] = line.replace('**Version:**', '').strip()
                elif line.startswith('## Description'):
                    # Find the description paragraph
                    desc_lines = []
                    i = lines.index(line) + 1
                    while i < len(lines) and not lines[i].startswith('##'):
                        if lines[i].strip():
                            desc_lines.append(lines[i].strip())
                        i += 1
                    metadata['description'] = ' '.join(desc_lines)
                elif line.startswith('`') and line.endswith('`'):
                    # Extract tags
                    tags_line = line.replace('`', '').replace(',', ' ')
                    metadata['tags'] = [tag.strip() for tag in tags_line.split() if tag.strip()]
        
        except Exception as e:
            print(f"⚠️  Warning: Could not parse DESCRIPTION.md: {e}")
        
        return metadata
    
    def _cache_template(self, workspace: str, template_name: str, template_data: dict):
        """Cache template locally for faster subsequent imports"""
        cache_file = self.cache_dir / f"{workspace}_{template_name}.py"
        
        with open(cache_file, 'w') as f:
            f.write(f"# Registry Template: {workspace}/{template_name}\n")
            f.write(f"# Version: {template_data['version']}\n")
            f.write(f"# Cached: {template_data['cached_at']}\n")
            f.write(f"# Auto-generated from InfraDSL Registry\n\n")
            f.write(template_data['source_code'])
        
        return cache_file
    
    def _load_cached_template(self, workspace: str, template_name: str) -> Optional[Path]:
        """Load template from cache if available and recent"""
        cache_file = self.cache_dir / f"{workspace}_{template_name}.py"
        
        if cache_file.exists():
            # Check if cache is recent (within 1 hour for demo)
            mtime = cache_file.stat().st_mtime
            now = datetime.now().timestamp()
            if (now - mtime) < 3600:  # 1 hour cache
                return cache_file
        
        return None
    
    def get_template_class(self, workspace: str, template_name: str) -> type:
        """Get template class, fetching from registry if needed"""
        # Try cache first
        cached_file = self._load_cached_template(workspace, template_name)
        
        if not cached_file:
            # Fetch from registry and cache
            template_data = self._get_template_from_registry(workspace, template_name)
            cached_file = self._cache_template(workspace, template_name, template_data)
            print(f"📦 Fetched {workspace}/{template_name} from registry")
        else:
            print(f"⚡ Using cached {workspace}/{template_name}")
        
        # Load the template class from cached file
        spec = importlib.util.spec_from_file_location(f"{workspace}_{template_name}", cached_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the template class
        # First, look for classes with get_metadata (backward compatibility)
        for name, obj in vars(module).items():
            if (isinstance(obj, type) and 
                not name.startswith('_') and 
                hasattr(obj, 'get_metadata')):
                return obj
        
        # Then look for classes that have template-like methods (create, preview, destroy)
        # Prioritize classes with "Simple" or template-like names
        template_classes = []
        for name, obj in vars(module).items():
            if (isinstance(obj, type) and 
                not name.startswith('_') and
                hasattr(obj, 'create') and 
                hasattr(obj, 'preview') and
                name not in ['MockCloudRun', 'MockVm', 'GoogleCloud']):  # Exclude mock classes
                template_classes.append((name, obj))
        
        # Sort by priority: Simple* classes first, then others
        template_classes.sort(key=lambda x: (0 if x[0].startswith('Simple') else 1, x[0]))
        
        if template_classes:
            return template_classes[0][1]
        
        # Fallback to first non-mock class found
        for name, obj in vars(module).items():
            if (isinstance(obj, type) and 
                not name.startswith('_') and
                name not in ['MockCloudRun', 'GoogleCloud']):
                return obj
        
        raise ImportError(f"No template class found in {workspace}/{template_name}")


# Global registry importer instance
_registry_importer = RegistryImporter()


class WorkspaceModule:
    """Dynamic module for workspace templates"""
    
    def __init__(self, workspace_name: str):
        self.workspace_name = workspace_name
        self._templates = {}
    
    def __getattr__(self, template_name: str) -> type:
        """Dynamically import template class on first access"""
        if template_name.startswith('_'):
            raise AttributeError(f"'{self.workspace_name}' has no attribute '{template_name}'")
        
        # Special case for BuildPush - import directly without registry lookup
        if template_name == 'BuildPush':
            from .build_push import BuildPush
            return BuildPush
        
        # Convert CamelCase to kebab-case for registry lookup
        registry_name = self._camel_to_kebab(template_name)
        
        if registry_name not in self._templates:
            self._templates[registry_name] = _registry_importer.get_template_class(
                self.workspace_name, registry_name
            )
        
        return self._templates[registry_name]
    
    def _camel_to_kebab(self, name: str) -> str:
        """Convert CamelCase to kebab-case"""
        # Handle specific mappings first
        mappings = {
            'SimpleVM': 'simple-vm',
            'SimpleWebApp': 'simple-webapp',
            'BuildPush': 'build-push'
        }
        
        if name in mappings:
            return mappings[name]
        
        # General camel to kebab conversion
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()
    
    def __dir__(self):
        """Return available template names for tab completion"""
        return ['SimpleVM', 'SimpleWebApp', 'BuildPush']


# Create workspace modules dynamically
class RegistryModule:
    """Main registry module that creates workspace submodules on demand"""
    
    def __getattr__(self, workspace_name: str):
        """Create workspace module on first access"""
        if workspace_name.startswith('_'):
            raise AttributeError(f"module has no attribute '{workspace_name}'")
        
        return WorkspaceModule(workspace_name)


# Install workspace modules directly in sys.modules for easier imports
def _setup_workspace_modules():
    """Setup workspace modules for direct imports"""
    base_module_name = __name__
    
    # Create common workspace modules
    workspaces = ['infradsl', 'company', 'enterprise']
    
    for workspace in workspaces:
        module_name = f"{base_module_name}.{workspace}"
        if module_name not in sys.modules:
            sys.modules[module_name] = WorkspaceModule(workspace)

# Setup workspace modules on import
_setup_workspace_modules()

# Export BuildPush for easy access
from .build_push import BuildPush, build_push

__all__ = ['BuildPush', 'build_push']

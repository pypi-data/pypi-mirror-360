"""
InfraDSL Marketplace

Company-specific template registry with workspace isolation and intelligent inheritance.

This module provides:
- Registry client for authentication and template management
- Company template inheritance system
- Workspace isolation similar to Slack
- CLI commands for marketplace operations

Example Usage:
    # Individual user
    from infradsl.marketplace import RegistryClient
    
    client = RegistryClient()
    client.login()
    templates = client.search_templates("web server")
    
    # Workspace user
    client = RegistryClient(workspace="nolimitcity")
    client.login()
    
    # Use company templates
    from infradsl.marketplace.nolimitcity import ProdVM
    vm = ProdVM("web-server-1")
    vm.create()
"""

from .registry_client import (
    RegistryClient,
    RegistryError,
    AuthenticationError,
    PermissionError,
    TemplateNotFoundError,
    TemplateInfo,
    WorkspaceInfo
)

from .company_templates import (
    CompanyTemplateBase,
    CompanyPolicy,
    CompanyStandard,
    NolimitCityBase,
    NolimitCityProdVM,
    NolimitCityDevVM,
    create_company_template_loader
)

from .firestore_schema import (
    FirestoreCollections,
    TemplateVisibility,
    UserRole,
    TemplateType,
    FIRESTORE_SECURITY_RULES,
    FIRESTORE_INDEXES
)

# Version information
__version__ = "1.0.0"
__author__ = "InfraDSL Team"

# Convenience imports for common use cases
def login(workspace=None):
    """Quick authentication helper"""
    client = RegistryClient(workspace=workspace)
    return client.login()

def search(query="", workspace=None, **kwargs):
    """Quick template search helper"""
    client = RegistryClient(workspace=workspace)
    return client.search_templates(query=query, **kwargs)

def get_template(template_ref, version="latest", workspace=None):
    """Quick template retrieval helper"""
    if '/' in template_ref and not workspace:
        workspace = template_ref.split('/')[0]
    
    client = RegistryClient(workspace=workspace)
    return client.get_template(template_ref, version)

def import_template(template_ref, version="latest", workspace=None):
    """Quick template import helper"""
    if '/' in template_ref and not workspace:
        workspace = template_ref.split('/')[0]
    
    client = RegistryClient(workspace=workspace)
    return client.import_template(template_ref, version)

# Dynamic workspace loaders
def __getattr__(name):
    """
    Enable dynamic workspace access like:
    from infradsl.marketplace import nolimitcity
    ProdVM = nolimitcity.ProdVM
    """
    if name.islower() and not name.startswith('_'):
        # This looks like a workspace name
        return create_company_template_loader(name)
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Export all public symbols
__all__ = [
    # Client classes
    'RegistryClient',
    'TemplateInfo',
    'WorkspaceInfo',
    
    # Exception classes
    'RegistryError',
    'AuthenticationError', 
    'PermissionError',
    'TemplateNotFoundError',
    
    # Template system
    'CompanyTemplateBase',
    'CompanyPolicy',
    'CompanyStandard',
    'NolimitCityBase',
    'NolimitCityProdVM',
    'NolimitCityDevVM',
    'create_company_template_loader',
    
    # Schema definitions
    'FirestoreCollections',
    'TemplateVisibility',
    'UserRole',
    'TemplateType',
    
    # Convenience functions
    'login',
    'search',
    'get_template',
    'import_template',
]
"""
AWS Security Group Resource - Entry Point

This file serves as the main entry point for the AWS Security Group resource.
The implementation is organized into modular components in the security_group/ 
directory for better maintainability.

Modular structure:
- security_group/security_group_core.py: Core SecurityGroup class with main functionality
- security_group/security_group_discovery.py: Security group discovery and management
- security_group/security_group_lifecycle.py: Lifecycle operations (create/update/destroy)
- security_group/security_group_configuration.py: Chainable configuration methods

The SecurityGroup class combines all functionality through multiple inheritance,
providing a Rails-like interface for firewall management.
"""

# Import the main SecurityGroup class from the refactored module
from .security_group.security_group import SecurityGroup

# For backwards compatibility, ensure all existing imports still work
__all__ = ['SecurityGroup']
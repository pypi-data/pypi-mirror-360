"""
AWS RDS Resource - Refactored Entry Point

This file serves as the main entry point for the AWS RDS resource.
The actual implementation has been refactored into modular components
in the rds/ directory for better maintainability.

Previous monolithic structure:
- Mixed core functionality, discovery, lifecycle, and configuration

New modular structure:
- rds/rds_core.py: Core RDS class with main functionality
- rds/rds_discovery.py: RDS instance discovery and management
- rds/rds_lifecycle.py: Lifecycle operations (create/update/destroy)
- rds/rds_configuration.py: Chainable configuration methods

The RDS class now combines all functionality through multiple inheritance,
providing the same interface as before but with much better organization.
"""

# Import the main RDS class from the refactored module
from .rds import RDS

# For backwards compatibility, ensure all existing imports still work
__all__ = ['RDS']

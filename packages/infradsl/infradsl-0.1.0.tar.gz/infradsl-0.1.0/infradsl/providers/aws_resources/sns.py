"""
AWS SNS Resource - Refactored Entry Point

This file serves as the main entry point for the AWS SNS resource.
The actual implementation has been refactored into modular components
in the sns/ directory for better maintainability.

Previous monolithic structure:
- Mixed core functionality, discovery, lifecycle, and configuration

New modular structure:
- sns/sns_core.py: Core SNS class with main functionality
- sns/sns_discovery.py: Topic discovery and management
- sns/sns_lifecycle.py: Lifecycle operations (create/update/destroy)
- sns/sns_configuration.py: Chainable configuration methods

The SNS class now combines all functionality through multiple inheritance,
providing the same interface as before but with much better organization.
"""

# Import the main SNS class from the refactored module
from .sns import SNS

# For backwards compatibility, ensure all existing imports still work
__all__ = ['SNS'] 
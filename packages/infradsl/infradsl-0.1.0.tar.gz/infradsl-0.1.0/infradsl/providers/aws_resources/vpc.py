"""
AWS VPC Resource - Entry Point

This file serves as the main entry point for the AWS VPC resource.
The actual implementation is organized into modular components
in the vpc/ directory for better maintainability.

VPC structure:
- vpc/vpc_core.py: Core VPC class with main functionality
- vpc/vpc_discovery.py: VPC discovery and management
- vpc/vpc_lifecycle.py: Lifecycle operations (create/update/destroy)
- vpc/vpc_configuration.py: Chainable configuration methods

The VPC class combines all functionality through multiple inheritance,
providing a complete interface for AWS Virtual Private Cloud management.
"""

# Import the main VPC class from the modular implementation
from .vpc.vpc import VPC

# For backwards compatibility, ensure all existing imports still work
__all__ = ['VPC']
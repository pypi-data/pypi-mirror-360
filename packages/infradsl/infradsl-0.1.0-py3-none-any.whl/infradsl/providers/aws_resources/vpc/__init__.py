"""
VPC Module

This module contains the AWS VPC components organized as:

- vpc_core.py: Core VPC class with main functionality
- vpc_discovery.py: VPC discovery and management
- vpc_lifecycle.py: Lifecycle operations (create/update/destroy)
- vpc_configuration.py: Chainable configuration methods

This modular structure makes the VPC resource more maintainable and testable.
The main VPC class combines all functionality through multiple inheritance.
"""

# Import the comprehensive VPC implementation
from .vpc import VPC


__all__ = ['VPC']
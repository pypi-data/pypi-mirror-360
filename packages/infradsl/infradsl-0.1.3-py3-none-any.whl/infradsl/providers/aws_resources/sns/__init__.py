"""
SNS Module (Refactored)

This module contains the refactored SNS components that were previously
in a single large sns.py file. The components are now organized as:

- sns_core.py: Core SNS class with main functionality
- sns_discovery.py: Topic discovery and management
- sns_lifecycle.py: Lifecycle operations (create/update/destroy)
- sns_configuration.py: Chainable configuration methods

This modular structure makes the SNS resource more maintainable and testable.
The main SNS class combines all functionality through multiple inheritance.
"""

# Import the comprehensive SNS implementation
from .sns import SNS


__all__ = ['SNS'] 
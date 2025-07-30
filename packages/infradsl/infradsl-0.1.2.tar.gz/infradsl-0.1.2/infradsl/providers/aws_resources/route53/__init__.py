"""
Route53 Module (Refactored)

This module contains the refactored Route53 components that were previously
in a single large route53.py file. The components are now organized as:

- route53_core.py: Core Route53 class with main functionality
- route53_discovery.py: Hosted zone and record discovery/management
- route53_lifecycle.py: Lifecycle operations (create/update/destroy)
- route53_configuration.py: Chainable configuration methods

This modular structure makes the Route53 resource more maintainable and testable.
The main Route53 class combines all functionality through multiple inheritance.
"""

# Import the comprehensive Route53 implementation
from .route53 import Route53


__all__ = ['Route53'] 
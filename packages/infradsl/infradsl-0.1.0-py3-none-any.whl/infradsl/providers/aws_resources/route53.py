"""
AWS Route53 Resource - Refactored Entry Point

This file serves as the main entry point for the AWS Route53 resource.
The actual implementation has been refactored into modular components
in the route53/ directory for better maintainability.

Previous monolithic structure:
- Mixed core functionality, discovery, lifecycle, and configuration

New modular structure:
- route53/route53_core.py: Core Route53 class with main functionality
- route53/route53_discovery.py: Hosted zone and record discovery/management
- route53/route53_lifecycle.py: Lifecycle operations (create/update/destroy)
- route53/route53_configuration.py: Chainable configuration methods

The Route53 class now combines all functionality through multiple inheritance,
providing the same interface as before but with much better organization.
"""

# Import the main Route53 class from the refactored module
from .route53.route53 import Route53

# For backwards compatibility, ensure all existing imports still work
__all__ = ['Route53']

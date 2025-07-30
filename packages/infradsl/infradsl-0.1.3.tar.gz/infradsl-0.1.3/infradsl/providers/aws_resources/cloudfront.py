"""
AWS CloudFront Resource - Refactored Entry Point

This file serves as the main entry point for the AWS CloudFront resource.
The actual implementation has been refactored into modular components
in the cloudfront/ directory for better maintainability.

Previous monolithic structure:
- Mixed core functionality, discovery, lifecycle, and configuration

New modular structure:
- cloudfront/cloudfront_core.py: Core CloudFront class with main functionality
- cloudfront/cloudfront_discovery.py: Distribution discovery and management
- cloudfront/cloudfront_lifecycle.py: Lifecycle operations (create/update/destroy)
- cloudfront/cloudfront_configuration.py: Chainable configuration methods

The CloudFront class now combines all functionality through multiple inheritance,
providing the same interface as before but with much better organization.
"""

# Import the main CloudFront class from the refactored module
from .cloudfront.cloudfront import CloudFront

# For backwards compatibility, ensure all existing imports still work
__all__ = ['CloudFront']

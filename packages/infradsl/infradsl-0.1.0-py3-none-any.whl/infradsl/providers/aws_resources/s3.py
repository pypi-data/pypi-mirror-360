"""
AWS S3 Resource - Refactored Entry Point

This file serves as the main entry point for the AWS S3 resource.
The actual implementation has been refactored into modular components
in the s3/ directory for better maintainability.

Previous monolithic structure:
- Mixed core functionality, discovery, lifecycle, and configuration

New modular structure:
- s3/s3_core.py: Core S3 class with main functionality
- s3/s3_discovery.py: Bucket discovery and management
- s3/s3_lifecycle.py: Lifecycle operations (create/update/destroy)
- s3/s3_configuration.py: Chainable configuration methods

The S3 class now combines all functionality through multiple inheritance,
providing the same interface as before but with much better organization.
"""

# Import the main S3 class from the refactored module
from .s3.s3 import S3

# For backwards compatibility, ensure all existing imports still work
__all__ = ['S3']

"""
S3 Module (Refactored)

This module contains the refactored S3 components that were previously
in a single large s3.py file. The components are now organized as:

- s3_core.py: Core S3 class with main functionality
- s3_discovery.py: S3 bucket discovery and management
- s3_lifecycle.py: Lifecycle operations (create/update/destroy)
- s3_configuration.py: Chainable configuration methods

This modular structure makes the S3 resource more maintainable and testable.
The main S3 class combines all functionality through multiple inheritance.
"""

from .s3_core import S3Core
from .s3_discovery import S3DiscoveryMixin
from .s3_lifecycle import S3LifecycleMixin
from .s3_configuration import S3ConfigurationMixin


class S3(S3Core, S3DiscoveryMixin, S3LifecycleMixin, S3ConfigurationMixin):
    """
    Complete AWS S3 Resource
    
    This class combines all S3 functionality through multiple inheritance.
    """
    def __init__(self, name: str):
        """Initialize S3 with all capabilities"""
        super().__init__(name)


__all__ = ['S3'] 
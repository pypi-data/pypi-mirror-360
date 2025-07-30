"""
CloudFront Module (Refactored)

This module contains the refactored CloudFront components that were previously
in a single large cloudfront.py file. The components are now organized as:

- cloudfront_core.py: Core CloudFront class with main functionality
- cloudfront_discovery.py: CloudFront distribution discovery and management
- cloudfront_lifecycle.py: Lifecycle operations (create/update/destroy)
- cloudfront_configuration.py: Chainable configuration methods

This modular structure makes the CloudFront resource more maintainable and testable.
The main CloudFront class combines all functionality through multiple inheritance.
"""

from .cloudfront_core import CloudFrontCore
from .cloudfront_discovery import CloudFrontDiscoveryMixin
from .cloudfront_lifecycle import CloudFrontLifecycleMixin
from .cloudfront_configuration import CloudFrontConfigurationMixin


class CloudFront(CloudFrontCore, CloudFrontDiscoveryMixin, CloudFrontLifecycleMixin, CloudFrontConfigurationMixin):
    """
    Complete AWS CloudFront Resource
    
    This class combines all CloudFront functionality through multiple inheritance.
    """
    def __init__(self, name: str):
        """Initialize CloudFront with all capabilities"""
        super().__init__(name)


__all__ = ['CloudFront'] 
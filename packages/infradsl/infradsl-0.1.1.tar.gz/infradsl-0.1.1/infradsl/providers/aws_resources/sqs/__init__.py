"""
SQS Module (Refactored)

This module contains the refactored SQS components that were previously
in a single large sqs.py file. The components are now organized as:

- sqs_core.py: Core SQS class with main functionality
- sqs_discovery.py: Queue discovery and management
- sqs_lifecycle.py: Lifecycle operations (create/update/destroy)
- sqs_configuration.py: Chainable configuration methods

This modular structure makes the SQS resource more maintainable and testable.
The main SQS class combines all functionality through multiple inheritance.
"""

from .sqs_core import SQSCore
from .sqs_discovery import SQSDiscoveryMixin
from .sqs_lifecycle import SQSLifecycleMixin
from .sqs_configuration import SQSConfigurationMixin


class SQS(SQSCore, SQSDiscoveryMixin, SQSLifecycleMixin, SQSConfigurationMixin):
    """
    Complete AWS SQS Resource
    
    This class combines all SQS functionality through multiple inheritance.
    """
    def __init__(self, name: str):
        """Initialize SQS with all capabilities"""
        super().__init__(name)


__all__ = ['SQS'] 
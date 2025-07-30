"""
AWS SQS Resource - Refactored Entry Point

This file serves as the main entry point for the AWS SQS resource.
The actual implementation has been refactored into modular components
in the sqs/ directory for better maintainability.

Previous monolithic structure:
- Mixed core functionality, discovery, lifecycle, and configuration

New modular structure:
- sqs/sqs_core.py: Core SQS class with main functionality
- sqs/sqs_discovery.py: Queue discovery and management
- sqs/sqs_lifecycle.py: Lifecycle operations (create/update/destroy)
- sqs/sqs_configuration.py: Chainable configuration methods

The SQS class now combines all functionality through multiple inheritance,
providing the same interface as before but with much better organization.
"""

# Import the main SQS class from the refactored module
from .sqs.sqs import SQS

# For backwards compatibility, ensure all existing imports still work
__all__ = ['SQS'] 
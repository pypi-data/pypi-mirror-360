"""
CertificateManager Module (Refactored)

This module contains the refactored CertificateManager components that were previously
in a single large certificate_manager.py file. The components are now organized as:

- certificate_manager_core.py: Core CertificateManager class with main functionality
- certificate_manager_discovery.py: Certificate discovery and management
- certificate_manager_lifecycle.py: Lifecycle operations (create/update/destroy)
- certificate_manager_configuration.py: Chainable configuration methods

This modular structure makes the CertificateManager resource more maintainable and testable.
The main CertificateManager class combines all functionality through multiple inheritance.
"""

# Import the comprehensive CertificateManager implementation
from .certificate_manager import CertificateManager


__all__ = ['CertificateManager'] 
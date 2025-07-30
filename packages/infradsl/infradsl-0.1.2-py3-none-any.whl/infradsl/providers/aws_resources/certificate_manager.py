"""
AWS CertificateManager Resource - Refactored Entry Point

This file serves as the main entry point for the AWS CertificateManager resource.
The actual implementation has been refactored into modular components
in the certificate_manager/ directory for better maintainability.

Previous monolithic structure:
- Mixed core functionality, discovery, lifecycle, and configuration

New modular structure:
- certificate_manager/certificate_manager_core.py: Core CertificateManager class with main functionality
- certificate_manager/certificate_manager_discovery.py: Certificate discovery and management
- certificate_manager/certificate_manager_lifecycle.py: Lifecycle operations (create/update/destroy)
- certificate_manager/certificate_manager_configuration.py: Chainable configuration methods

The CertificateManager class now combines all functionality through multiple inheritance,
providing the same interface as before but with much better organization.
"""

# Import the main CertificateManager class from the refactored module
from .certificate_manager.certificate_manager import CertificateManager

# For backwards compatibility, ensure all existing imports still work
__all__ = ['CertificateManager'] 
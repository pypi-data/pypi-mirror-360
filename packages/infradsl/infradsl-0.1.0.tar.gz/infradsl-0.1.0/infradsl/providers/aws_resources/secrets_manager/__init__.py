"""
SecretsManager Module (Refactored)

This module contains the refactored SecretsManager components that were previously
in a single large secrets_manager.py file. The components are now organized as:

- secrets_manager_core.py: Core SecretsManager class with main functionality
- secrets_manager_discovery.py: Secret discovery and management
- secrets_manager_lifecycle.py: Lifecycle operations (create/update/destroy)
- secrets_manager_configuration.py: Chainable configuration methods

This modular structure makes the SecretsManager resource more maintainable and testable.
The main SecretsManager class combines all functionality through multiple inheritance.
"""

from .secrets_manager_core import SecretsManagerCore
from .secrets_manager_discovery import SecretsManagerDiscoveryMixin
from .secrets_manager_lifecycle import SecretsManagerLifecycleMixin
from .secrets_manager_configuration import SecretsManagerConfigurationMixin


from typing import Dict, Any

class SecretsManager(SecretsManagerCore, SecretsManagerDiscoveryMixin, SecretsManagerLifecycleMixin, SecretsManagerConfigurationMixin):
    """
    Complete AWS SecretsManager Resource
    
    This class combines all SecretsManager functionality through multiple inheritance.
    """
    def __init__(self, name: str):
        """Initialize SecretsManager with all capabilities"""
        super().__init__(name)


__all__ = ['SecretsManager'] 
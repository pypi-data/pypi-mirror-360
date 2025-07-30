"""
Security Resources Package
"""

# Use the new modular implementation
from .secret_manager_new import SecretManager

__all__ = [
    'SecretManager',
]

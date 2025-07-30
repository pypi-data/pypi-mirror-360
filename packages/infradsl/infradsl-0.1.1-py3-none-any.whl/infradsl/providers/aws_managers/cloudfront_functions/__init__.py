"""
AWS CloudFront Functions Manager Package

Modular management of CloudFront Functions for edge computing.
Handles function creation, deployment, and association with distributions.
"""

from .manager import CloudFrontFunctionsManager
from .functions import CloudFrontFunctionsCore
from .associations import CloudFrontFunctionAssociations

__all__ = [
    'CloudFrontFunctionsManager',
    'CloudFrontFunctionsCore', 
    'CloudFrontFunctionAssociations'
]
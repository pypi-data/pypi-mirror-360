"""
Google Cloud Compute Managers

This module contains managers for Google Cloud compute services like Cloud Functions,
Compute Engine VMs, and related compute resources.
"""

from .cloud_functions_manager import CloudFunctionsManager, FunctionConfig

__all__ = ['CloudFunctionsManager', 'FunctionConfig']

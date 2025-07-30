"""
Compute Resources Package
"""

from .vm_new import Vm
from .vm_group import VmGroup
from .cloud_run_new import CloudRun
# Use the new modular implementation
from .gke_new import GKE
from .cloud_functions_new import CloudFunctions
from .app_engine_new import AppEngine

__all__ = [
    'Vm',
    'VmGroup',
    'CloudRun',
    'GKE',
    'CloudFunctions',
    'AppEngine',
]

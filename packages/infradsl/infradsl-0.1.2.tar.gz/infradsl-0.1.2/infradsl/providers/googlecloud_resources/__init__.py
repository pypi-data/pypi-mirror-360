"""
Google Cloud Resources Package

This package contains individual resource components for Google Cloud Platform,
following a component-based architecture similar to React components.
"""

from .auth_service import GcpAuthenticationService
from .base_resource import BaseGcpResource
from .compute import *
from .storage import *
from .networking import *
from .security import *
from .firebase import *
from .cicd.cloud_build_new import CloudBuild

__all__ = [
    # Core services
    'GcpAuthenticationService',
    'BaseGcpResource',

    # Compute
    'Vm',
    'VmGroup',
    'CloudRun',
    'GKE',
    'CloudFunctions',
    'AppEngine',

    # Storage
    'Storage',
    'CloudSQL',
    'BigQuery',
    'Memorystore',
    'CloudSpanner',
    'PersistentDisk',

    # Networking
    'LoadBalancer',
    'create_load_balancer',
    'CloudDNS',
    'DNS',
    'APIGateway',
    'CertificateManager',
    'PubSub',
    'CloudCdn',

    # Security
    'SecretManager',

    # Firebase
    'FirebaseHosting',
    'FirebaseAuth',
    'Firestore',
    'FirebaseFunctions',
    'FirebaseStorage',
    
    # CI/CD
    'CloudBuild',
]

# Version info
__version__ = '1.1.0'
__author__ = 'InfraDSL Team'


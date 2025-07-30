"""
Google Cloud Managers

This module contains all managers for Google Cloud Platform services, organized by
service category. Each manager handles the low-level API interactions for their
respective Google Cloud services, following Rails-like conventions.

Service Categories:
- Analytics: BigQuery and data analytics services
- Compute: Cloud Functions, Compute Engine, GKE, and compute resources
- Database: Cloud SQL, Firestore, and database services
- Storage: Cloud Storage buckets and object management
- Load Balancer: Load balancing and traffic management
"""

# Core managers
from .gcp_client import GcpClient
from .status_reporter import GcpStatusReporter

# Service-specific managers
from .analytics import BigQueryManager
from .compute import CloudFunctionsManager, FunctionConfig
from .database import CloudSQLManager
from .storage import BucketManager

# Other managers (direct imports for backward compatibility)
from .vm_manager import VmManager
from .gke_manager import GkeManager
from .cloud_run_manager import CloudRunManager
from .firewall_manager import GcpFirewallManager
from .load_balancer_manager import GcpLoadBalancerManager
from .health_check_manager import GcpHealthCheckManager
from .artifact_registry_manager import ArtifactRegistryManager
from .service_manager import GcpServiceManager

__all__ = [
    # Core
    'GcpClient',
    'GcpStatusReporter',

    # Analytics
    'BigQueryManager',

    # Compute
    'CloudFunctionsManager',
    'FunctionConfig',

    # Database
    'CloudSQLManager',

    # Storage
    'BucketManager',

    # Other services
    'VmManager',
    'GkeManager',
    'CloudRunManager',
    'GcpFirewallManager',
    'GcpLoadBalancerManager',
    'GcpHealthCheckManager',
    'ArtifactRegistryManager',
    'GcpServiceManager',
]

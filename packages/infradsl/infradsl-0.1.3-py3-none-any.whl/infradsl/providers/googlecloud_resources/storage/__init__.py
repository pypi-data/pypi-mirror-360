"""
Storage Resources Package
"""

# Use the new modular implementations
from .storage_new import Storage
from .cloudsql_new import CloudSQL
from .bigquery import BigQuery
from .memorystore_new import Memorystore
from .cloud_spanner_new import CloudSpanner, create_cloud_spanner, create_development_spanner, create_production_spanner, create_global_spanner, create_cost_optimized_spanner
from .persistent_disk_new import PersistentDisk, create_persistent_disk, create_boot_disk, create_data_disk, create_database_disk, create_backup_disk, create_regional_disk, create_shared_disk

__all__ = [
    'Storage',
    'CloudSQL',
    'BigQuery',
    'Memorystore',
    'CloudSpanner',
    'create_cloud_spanner',
    'create_development_spanner',
    'create_production_spanner',
    'create_global_spanner',
    'create_cost_optimized_spanner',
    'PersistentDisk',
    'create_persistent_disk',
    'create_boot_disk',
    'create_data_disk',
    'create_database_disk',
    'create_backup_disk',
    'create_regional_disk',
    'create_shared_disk',
]

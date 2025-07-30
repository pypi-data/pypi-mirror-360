"""
Google Cloud Persistent Disk Core Implementation

Core attributes and authentication for Google Cloud Persistent Disk.
Provides the foundation for the modular block storage service.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class PersistentDiskCore(BaseGcpResource):
    """
    Core class for Google Cloud Persistent Disk functionality.
    
    This class provides:
    - Basic Persistent Disk attributes and configuration
    - Authentication setup
    - Common utilities for disk operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """
        Initialize Persistent Disk core with disk name.
        
        Args:
            name: Disk name
        """
        super().__init__(name)
        
        # Core disk attributes
        self.disk_name = name
        self.disk_description = f"Persistent disk: {name}"
        self.disk_type = "persistent_disk"
        
        # Disk configuration
        self.project_id = None
        self.zone = "us-central1-a"
        self.region = None  # For regional disks
        self.size_gb = 100
        
        # Disk type configuration
        self.pd_type = "pd-standard"  # pd-standard, pd-ssd, pd-balanced, pd-extreme
        self.provisioned_iops = None  # For pd-extreme
        self.provisioned_throughput = None  # For pd-extreme
        
        # Source configuration
        self.source_image = None
        self.source_image_family = None
        self.source_snapshot = None
        self.source_disk = None
        
        # Performance configuration
        self.multi_writer = False
        self.enable_confidential_compute = False
        self.storage_pool = None
        
        # Security configuration
        self.encryption_key = None
        self.customer_encryption_key = None
        self.enable_deletion_protection = False
        
        # Replica configuration (for regional disks)
        self.replica_zones = []
        
        # Attachment configuration
        self.attached_instances = []
        self.interface = "SCSI"  # SCSI or NVME
        self.mode = "READ_WRITE"  # READ_WRITE or READ_ONLY
        self.auto_delete = False
        self.boot = False
        
        # State tracking
        self.disk_exists = False
        self.disk_created = False
        self.disk_state = None
        self.deployment_status = None
        
        # Labels and metadata
        self.disk_labels = {}
        self.disk_annotations = {}
        
        # Cost tracking
        self.estimated_monthly_cost = "$15.00/month"
        
    def _initialize_managers(self):
        """Initialize disk specific managers"""
        self.compute_client = None
        self.disks_client = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            from google.cloud import compute_v1
            
            self.compute_client = compute_v1.InstancesClient()
            self.disks_client = compute_v1.DisksClient()
            
            # Set project ID from GCP client if available
            if hasattr(self.gcp_client, 'project'):
                self.project_id = self.gcp_client.project
                
        except Exception as e:
            print(f"⚠️  Persistent Disk setup note: {str(e)}")
            
    def _validate_disk_type(self, disk_type: str) -> bool:
        """Validate if disk type is valid"""
        valid_types = [
            "pd-standard",
            "pd-ssd", 
            "pd-balanced",
            "pd-extreme"
        ]
        return disk_type in valid_types
        
    def _validate_size(self, size_gb: int, disk_type: str) -> bool:
        """Validate disk size for given type"""
        size_limits = {
            "pd-standard": (10, 65536),    # 10 GB to 64 TB
            "pd-ssd": (10, 65536),         # 10 GB to 64 TB
            "pd-balanced": (10, 65536),    # 10 GB to 64 TB
            "pd-extreme": (500, 65536)     # 500 GB to 64 TB
        }
        
        min_size, max_size = size_limits.get(disk_type, (10, 65536))
        return min_size <= size_gb <= max_size
        
    def _validate_zone(self, zone: str) -> bool:
        """Validate if zone is valid"""
        # Simplified validation - real implementation would check with API
        return zone and "-" in zone and len(zone.split("-")) >= 3
        
    def _validate_interface(self, interface: str) -> bool:
        """Validate disk interface"""
        valid_interfaces = ["SCSI", "NVME"]
        return interface in valid_interfaces
        
    def _validate_mode(self, mode: str) -> bool:
        """Validate disk mode"""
        valid_modes = ["READ_WRITE", "READ_ONLY"]
        return mode in valid_modes
        
    def _get_disk_type_from_config(self) -> str:
        """Determine disk type from configuration"""
        # Check by PD type
        if self.pd_type == "pd-extreme":
            return "extreme_performance"
        elif self.pd_type == "pd-ssd":
            return "high_performance"
        elif self.pd_type == "pd-balanced":
            return "balanced_performance"
        elif self.pd_type == "pd-standard":
            return "standard_storage"
            
        # Check by size
        if self.size_gb >= 10000:  # 10TB+
            return "large_storage"
        elif self.size_gb >= 1000:  # 1TB+
            return "medium_storage"
        else:
            return "small_storage"
            
    def _estimate_disk_cost(self) -> float:
        """Estimate monthly cost for Persistent Disk"""
        # Persistent Disk pricing (per GB per month)
        pricing = {
            "pd-standard": 0.040,    # $0.040/GB/month
            "pd-balanced": 0.100,    # $0.100/GB/month  
            "pd-ssd": 0.170,         # $0.170/GB/month
            "pd-extreme": 0.650      # $0.650/GB/month
        }
        
        base_cost = self.size_gb * pricing.get(self.pd_type, 0.040)
        
        # Regional disk premium (2x cost)
        if self.region:
            base_cost *= 2
            
        # Snapshot storage (estimated 20% of disk size)
        snapshot_cost = self.size_gb * 0.2 * 0.026  # $0.026/GB/month for snapshots
        
        # Provisioned IOPS cost (for pd-extreme)
        iops_cost = 0
        if self.pd_type == "pd-extreme" and self.provisioned_iops:
            # Base IOPS included, additional IOPS cost extra
            base_iops = self.size_gb * 30  # 30 IOPS per GB included
            if self.provisioned_iops > base_iops:
                extra_iops = self.provisioned_iops - base_iops
                iops_cost = extra_iops * 0.0005 * 730  # $0.0005 per IOPS per hour
                
        total_cost = base_cost + snapshot_cost + iops_cost
        
        return total_cost
        
    def _fetch_current_disk_state(self) -> Dict[str, Any]:
        """Fetch current state of persistent disk"""
        try:
            if not self.disks_client or not self.project_id:
                return {
                    "exists": False,
                    "disk_name": self.disk_name,
                    "error": "Disks client not initialized or no project ID"
                }
                
            # Get disk info
            from google.cloud import compute_v1
            
            try:
                if self.region:
                    # Regional disk
                    request = compute_v1.GetRegionDiskRequest(
                        project=self.project_id,
                        region=self.region,
                        disk=self.disk_name
                    )
                    regional_disks_client = compute_v1.RegionDisksClient()
                    disk = regional_disks_client.get(request=request)
                else:
                    # Zonal disk
                    request = compute_v1.GetDiskRequest(
                        project=self.project_id,
                        zone=self.zone,
                        disk=self.disk_name
                    )
                    disk = self.disks_client.get(request=request)
                
                return {
                    "exists": True,
                    "disk_name": self.disk_name,
                    "disk_id": disk.id,
                    "size_gb": disk.size_gb,
                    "disk_type": disk.type.split("/")[-1],
                    "zone": disk.zone.split("/")[-1] if disk.zone else None,
                    "region": disk.region.split("/")[-1] if disk.region else None,
                    "status": disk.status,
                    "creation_timestamp": disk.creation_timestamp,
                    "labels": dict(disk.labels) if disk.labels else {},
                    "users": [user.split("/")[-1] for user in disk.users] if disk.users else []
                }
                
            except Exception as e:
                if "not found" in str(e).lower():
                    return {
                        "exists": False,
                        "disk_name": self.disk_name,
                        "project_id": self.project_id,
                        "reason": "Disk not found"
                    }
                else:
                    return {
                        "exists": False,
                        "disk_name": self.disk_name,
                        "error": str(e)
                    }
                    
        except Exception as e:
            return {
                "exists": False,
                "disk_name": self.disk_name,
                "error": str(e)
            }
            
    def _discover_existing_disks(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing persistent disks in the project"""
        existing_disks = {}
        
        try:
            if not self.disks_client or not self.project_id:
                return existing_disks
                
            from google.cloud import compute_v1
            
            # List zonal disks
            if self.zone:
                try:
                    request = compute_v1.ListDisksRequest(
                        project=self.project_id,
                        zone=self.zone
                    )
                    
                    disks = self.disks_client.list(request=request)
                    
                    for disk in disks:
                        disk_info = {
                            "disk_name": disk.name,
                            "disk_id": disk.id,
                            "size_gb": disk.size_gb,
                            "disk_type": disk.type.split("/")[-1],
                            "zone": disk.zone.split("/")[-1] if disk.zone else None,
                            "region": None,
                            "status": disk.status,
                            "creation_timestamp": str(disk.creation_timestamp)[:19] if disk.creation_timestamp else "unknown",
                            "labels": dict(disk.labels) if disk.labels else {},
                            "users": [user.split("/")[-1] for user in disk.users] if disk.users else [],
                            "is_regional": False
                        }
                        
                        existing_disks[disk.name] = disk_info
                        
                except Exception as e:
                    print(f"⚠️  Failed to list zonal disks: {str(e)}")
                    
            # List regional disks if region is specified
            if self.region:
                try:
                    regional_disks_client = compute_v1.RegionDisksClient()
                    request = compute_v1.ListRegionDisksRequest(
                        project=self.project_id,
                        region=self.region
                    )
                    
                    disks = regional_disks_client.list(request=request)
                    
                    for disk in disks:
                        disk_info = {
                            "disk_name": disk.name,
                            "disk_id": disk.id,
                            "size_gb": disk.size_gb,
                            "disk_type": disk.type.split("/")[-1],
                            "zone": None,
                            "region": disk.region.split("/")[-1] if disk.region else None,
                            "status": disk.status,
                            "creation_timestamp": str(disk.creation_timestamp)[:19] if disk.creation_timestamp else "unknown",
                            "labels": dict(disk.labels) if disk.labels else {},
                            "users": [user.split("/")[-1] for user in disk.users] if disk.users else [],
                            "is_regional": True,
                            "replica_zones": [zone.split("/")[-1] for zone in disk.replica_zones] if hasattr(disk, 'replica_zones') and disk.replica_zones else []
                        }
                        
                        existing_disks[disk.name] = disk_info
                        
                except Exception as e:
                    print(f"⚠️  Failed to list regional disks: {str(e)}")
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing disks: {str(e)}")
            
        return existing_disks
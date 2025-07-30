"""
Google Cloud Persistent Disk Configuration Mixin

Configuration methods for Google Cloud Persistent Disk.
Provides Rails-like method chaining for fluent disk configuration.
"""

from typing import Dict, Any, List, Optional, Union


class PersistentDiskConfigurationMixin:
    """
    Mixin for Google Cloud Persistent Disk configuration methods.
    
    This mixin provides:
    - Rails-like method chaining for fluent disk configuration
    - Disk type and performance configuration
    - Source and snapshot configuration
    - Security and encryption settings
    - Attachment and mounting options
    """
    
    # Project and Basic Configuration
    def project(self, project_id: str):
        """Set Google Cloud project ID"""
        self.project_id = project_id
        return self
        
    def zone(self, zone: str):
        """Set disk zone"""
        if not self._validate_zone(zone):
            raise ValueError(f"Invalid zone: {zone}")
        self.zone = zone
        self.region = None  # Clear region if setting zone
        return self
        
    def region(self, region: str):
        """Set disk region for regional persistent disk"""
        self.region = region
        self.zone = None  # Clear zone if setting region
        return self
        
    def description(self, description: str):
        """Set disk description"""
        self.disk_description = description
        return self
    
    # Size Configuration Methods
    def size(self, size_gb: int):
        """Set disk size in GB"""
        if not self._validate_size(size_gb, self.pd_type):
            raise ValueError(f"Invalid size {size_gb}GB for disk type {self.pd_type}")
        self.size_gb = size_gb
        return self
        
    def size_tb(self, size_tb: float):
        """Set disk size in TB"""
        return self.size(int(size_tb * 1024))
        
    def small_disk(self):
        """Configure small disk (100GB)"""
        return self.size(100)
        
    def medium_disk(self):
        """Configure medium disk (500GB)"""
        return self.size(500)
        
    def large_disk(self):
        """Configure large disk (1TB)"""
        return self.size_tb(1)
        
    def xlarge_disk(self):
        """Configure extra large disk (5TB)"""
        return self.size_tb(5)
        
    def huge_disk(self):
        """Configure huge disk (10TB)"""
        return self.size_tb(10)
    
    # Disk Type Configuration Methods
    def disk_type(self, pd_type: str):
        """Set persistent disk type"""
        if not self._validate_disk_type(pd_type):
            raise ValueError(f"Invalid disk type: {pd_type}")
        self.pd_type = pd_type
        return self
        
    def standard_disk(self):
        """Configure standard persistent disk (cheapest)"""
        return self.disk_type("pd-standard")
        
    def balanced_disk(self):
        """Configure balanced persistent disk (cost/performance balance)"""
        return self.disk_type("pd-balanced")
        
    def ssd_disk(self):
        """Configure SSD persistent disk (high performance)"""
        return self.disk_type("pd-ssd")
        
    def extreme_disk(self):
        """Configure extreme persistent disk (highest performance)"""
        return self.disk_type("pd-extreme")
    
    # Performance Configuration (for pd-extreme)
    def provisioned_iops(self, iops: int):
        """Set provisioned IOPS (pd-extreme only)"""
        if self.pd_type != "pd-extreme":
            print(f"⚠️  Provisioned IOPS only available for pd-extreme disks")
        self.provisioned_iops = iops
        return self
        
    def provisioned_throughput(self, throughput_mbps: int):
        """Set provisioned throughput in MB/s (pd-extreme only)"""
        if self.pd_type != "pd-extreme":
            print(f"⚠️  Provisioned throughput only available for pd-extreme disks")
        self.provisioned_throughput = throughput_mbps
        return self
        
    def high_iops(self):
        """Configure high IOPS for extreme disk"""
        if self.pd_type == "pd-extreme":
            max_iops = min(100000, self.size_gb * 100)  # Up to 100 IOPS per GB
            return self.provisioned_iops(max_iops)
        return self
        
    def max_throughput(self):
        """Configure maximum throughput for extreme disk"""
        if self.pd_type == "pd-extreme":
            max_throughput = min(4000, self.size_gb * 2)  # Up to 2 MB/s per GB
            return self.provisioned_throughput(max_throughput)
        return self
    
    # Source Configuration Methods
    def source_image(self, image_name: str, family: str = None):
        """Set source image for disk"""
        self.source_image = image_name
        if family:
            self.source_image_family = family
        return self
        
    def source_image_family(self, family: str):
        """Set source image family"""
        self.source_image_family = family
        return self
        
    def source_snapshot(self, snapshot_name: str):
        """Set source snapshot for disk"""
        self.source_snapshot = snapshot_name
        return self
        
    def source_disk(self, disk_name: str):
        """Set source disk for cloning"""
        self.source_disk = disk_name
        return self
        
    def blank_disk(self):
        """Create blank disk (no source)"""
        self.source_image = None
        self.source_image_family = None
        self.source_snapshot = None
        self.source_disk = None
        return self
    
    # Operating System Images
    def ubuntu_image(self, version: str = "2204-lts"):
        """Configure Ubuntu image"""
        return self.source_image_family(f"ubuntu-{version}")
        
    def debian_image(self, version: str = "11"):
        """Configure Debian image"""
        return self.source_image_family(f"debian-{version}")
        
    def centos_image(self, version: str = "8"):
        """Configure CentOS image"""
        return self.source_image_family(f"centos-{version}")
        
    def windows_image(self, version: str = "2022"):
        """Configure Windows Server image"""
        return self.source_image_family(f"windows-{version}")
        
    def container_optimized_image(self):
        """Configure Container-Optimized OS image"""
        return self.source_image_family("cos-stable")
    
    # Security Configuration Methods
    def encryption_key(self, key_name: str):
        """Set customer-managed encryption key"""
        self.encryption_key = key_name
        return self
        
    def customer_encryption_key(self, key: str):
        """Set customer-supplied encryption key"""
        self.customer_encryption_key = key
        return self
        
    def deletion_protection(self, enabled: bool = True):
        """Enable deletion protection"""
        self.enable_deletion_protection = enabled
        return self
        
    def confidential_compute(self, enabled: bool = True):
        """Enable confidential compute"""
        self.enable_confidential_compute = enabled
        return self
    
    # Multi-writer Configuration
    def multi_writer(self, enabled: bool = True):
        """Enable multi-writer mode"""
        self.multi_writer = enabled
        return self
    
    # Regional Disk Configuration
    def regional_disk(self, region: str, replica_zones: List[str] = None):
        """Configure as regional disk"""
        self.region = region
        self.zone = None
        if replica_zones:
            self.replica_zones = replica_zones
        return self
        
    def multi_zone_disk(self, zone1: str, zone2: str):
        """Configure regional disk across two zones"""
        region = "-".join(zone1.split("-")[:-1])
        return self.regional_disk(region, [zone1, zone2])
    
    # Attachment Configuration Methods
    def interface(self, interface: str):
        """Set disk interface (SCSI or NVME)"""
        if not self._validate_interface(interface):
            raise ValueError(f"Invalid interface: {interface}")
        self.interface = interface
        return self
        
    def scsi_interface(self):
        """Use SCSI interface"""
        return self.interface("SCSI")
        
    def nvme_interface(self):
        """Use NVMe interface (higher performance)"""
        return self.interface("NVME")
        
    def mode(self, mode: str):
        """Set disk mode (READ_WRITE or READ_ONLY)"""
        if not self._validate_mode(mode):
            raise ValueError(f"Invalid mode: {mode}")
        self.mode = mode
        return self
        
    def read_write(self):
        """Set read-write mode"""
        return self.mode("READ_WRITE")
        
    def read_only(self):
        """Set read-only mode"""
        return self.mode("READ_ONLY")
        
    def auto_delete(self, enabled: bool = True):
        """Enable auto-delete when instance is deleted"""
        self.auto_delete = enabled
        return self
        
    def boot_disk(self, enabled: bool = True):
        """Set as boot disk"""
        self.boot = enabled
        return self
    
    # High-Level Configuration Patterns
    def development_disk(self):
        """Configure for development environment"""
        self.disk_labels["environment"] = "development"
        return (self
                .standard_disk()
                .small_disk()
                .auto_delete()
                .deletion_protection(False))
                
    def staging_disk(self):
        """Configure for staging environment"""
        self.disk_labels["environment"] = "staging"
        return (self
                .balanced_disk()
                .medium_disk()
                .auto_delete(False))
                
    def production_disk(self):
        """Configure for production environment"""
        self.disk_labels["environment"] = "production"
        return (self
                .ssd_disk()
                .large_disk()
                .auto_delete(False)
                .deletion_protection())
                
    def database_disk(self):
        """Configure for database workloads"""
        self.disk_labels["workload"] = "database"
        return (self
                .ssd_disk()
                .large_disk()
                .nvme_interface()
                .auto_delete(False)
                .deletion_protection())
                
    def high_performance_disk(self):
        """Configure for high performance workloads"""
        self.disk_labels["workload"] = "high_performance"
        return (self
                .extreme_disk()
                .xlarge_disk()
                .high_iops()
                .max_throughput()
                .nvme_interface()
                .deletion_protection())
                
    def backup_disk(self):
        """Configure for backup storage"""
        self.disk_labels["workload"] = "backup"
        return (self
                .standard_disk()
                .huge_disk()
                .read_write()
                .auto_delete(False))
                
    def boot_volume(self, os_type: str = "ubuntu"):
        """Configure as boot volume"""
        self.disk_labels["disk_type"] = "boot"
        disk = (self
                .balanced_disk()
                .size(50)  # 50GB boot disk
                .boot_disk()
                .auto_delete())
        
        # Set OS image
        if os_type.lower() == "ubuntu":
            disk.ubuntu_image()
        elif os_type.lower() == "debian":
            disk.debian_image()
        elif os_type.lower() == "centos":
            disk.centos_image()
        elif os_type.lower() == "windows":
            disk.windows_image()
        elif os_type.lower() == "cos":
            disk.container_optimized_image()
            
        return disk
        
    def data_volume(self):
        """Configure as data volume"""
        self.disk_labels["disk_type"] = "data"
        return (self
                .ssd_disk()
                .large_disk()
                .read_write()
                .auto_delete(False)
                .deletion_protection())
                
    def shared_volume(self):
        """Configure as shared volume"""
        self.disk_labels["disk_type"] = "shared"
        return (self
                .ssd_disk()
                .large_disk()
                .multi_writer()
                .read_write()
                .auto_delete(False))
                
    def cost_optimized_disk(self):
        """Configure for cost optimization"""
        self.disk_labels["optimization"] = "cost"
        return (self
                .standard_disk()
                .medium_disk()
                .scsi_interface()
                .auto_delete())
                
    def performance_optimized_disk(self):
        """Configure for performance optimization"""
        self.disk_labels["optimization"] = "performance"
        return (self
                .extreme_disk()
                .xlarge_disk()
                .high_iops()
                .nvme_interface()
                .deletion_protection())
    
    # Label and Metadata Configuration
    def label(self, key: str, value: str):
        """Add label to disk"""
        self.disk_labels[key] = value
        return self
        
    def labels(self, labels: Dict[str, str]):
        """Add multiple labels"""
        self.disk_labels.update(labels)
        return self
        
    def team(self, team_name: str):
        """Set team label"""
        return self.label("team", team_name)
        
    def cost_center(self, cost_center: str):
        """Set cost center label"""
        return self.label("cost-center", cost_center)
        
    def application(self, app_name: str):
        """Set application label"""
        return self.label("application", app_name)
        
    def version(self, version: str):
        """Set version label"""
        return self.label("version", version)
    
    # Helper Methods
    def get_disk_configuration(self) -> Dict[str, Any]:
        """Get disk configuration"""
        return {
            "disk_name": self.disk_name,
            "size_gb": self.size_gb,
            "disk_type": self.pd_type,
            "zone": self.zone,
            "region": self.region,
            "interface": self.interface,
            "mode": self.mode,
            "auto_delete": self.auto_delete,
            "boot": self.boot
        }
        
    def get_performance_specs(self) -> Dict[str, Any]:
        """Get performance specifications"""
        specs = {
            "disk_type": self.pd_type,
            "size_gb": self.size_gb
        }
        
        # Calculate performance based on disk type
        if self.pd_type == "pd-standard":
            specs.update({
                "max_iops_read": min(7500, self.size_gb * 0.75),
                "max_iops_write": min(15000, self.size_gb * 1.5),
                "max_throughput_read": min(1200, self.size_gb * 1.2),
                "max_throughput_write": min(1200, self.size_gb * 1.2)
            })
        elif self.pd_type == "pd-balanced":
            specs.update({
                "max_iops_read": min(80000, self.size_gb * 6),
                "max_iops_write": min(80000, self.size_gb * 6),
                "max_throughput_read": min(1200, self.size_gb * 1.2),
                "max_throughput_write": min(1200, self.size_gb * 1.2)
            })
        elif self.pd_type == "pd-ssd":
            specs.update({
                "max_iops_read": min(100000, self.size_gb * 30),
                "max_iops_write": min(100000, self.size_gb * 30),
                "max_throughput_read": min(1200, self.size_gb * 1.2),
                "max_throughput_write": min(1200, self.size_gb * 1.2)
            })
        elif self.pd_type == "pd-extreme":
            specs.update({
                "max_iops_read": self.provisioned_iops or min(100000, self.size_gb * 100),
                "max_iops_write": self.provisioned_iops or min(100000, self.size_gb * 100),
                "max_throughput_read": self.provisioned_throughput or min(4000, self.size_gb * 2),
                "max_throughput_write": self.provisioned_throughput or min(4000, self.size_gb * 2)
            })
            
        return specs
        
    def is_production_ready(self) -> bool:
        """Check if disk is production ready"""
        return (
            self.size_gb >= 100 and
            self.pd_type in ["pd-ssd", "pd-balanced", "pd-extreme"] and
            not self.auto_delete and
            self.enable_deletion_protection
        )
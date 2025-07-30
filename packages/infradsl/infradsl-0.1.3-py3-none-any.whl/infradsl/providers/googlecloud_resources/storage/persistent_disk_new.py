"""
Google Cloud Persistent Disk Complete Implementation

Complete Google Cloud Persistent Disk implementation combining core functionality,
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .persistent_disk_core import PersistentDiskCore
from .persistent_disk_configuration import PersistentDiskConfigurationMixin
from .persistent_disk_lifecycle import PersistentDiskLifecycleMixin


class PersistentDisk(PersistentDiskCore, PersistentDiskConfigurationMixin, PersistentDiskLifecycleMixin):
    """
    Complete Google Cloud Persistent Disk implementation.
    
    This class combines:
    - PersistentDiskCore: Basic disk attributes and authentication
    - PersistentDiskConfigurationMixin: Chainable configuration methods
    - PersistentDiskLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent disk configuration
    - Smart performance and cost optimization
    - Cross-Cloud Magic optimization
    - High-performance block storage with up to 64TB capacity
    - Multiple disk types: Standard, Balanced, SSD, Extreme
    - Regional disks for high availability
    - Multi-attach support for shared storage
    - Dynamic resizing without downtime
    - Built-in encryption and security features
    - NVMe interface for maximum performance
    - Automatic snapshots and backup
    
    Example:
        # Development disk
        dev_disk = PersistentDisk("dev-data")
        dev_disk.project("my-project").development_disk()
        dev_disk.zone("us-central1-a").ubuntu_image()
        dev_disk.create()
        
        # Production database disk
        db_disk = PersistentDisk("prod-database")
        db_disk.project("my-project").database_disk()
        db_disk.zone("us-central1-a").size_tb(2)
        db_disk.create()
        
        # High-performance disk
        perf_disk = PersistentDisk("performance-disk")
        perf_disk.project("my-project").high_performance_disk()
        perf_disk.zone("us-central1-a")
        perf_disk.create()
        
        # Regional disk for HA
        ha_disk = PersistentDisk("ha-storage")
        ha_disk.project("my-project").production_disk()
        ha_disk.regional_disk("us-central1", ["us-central1-a", "us-central1-b"])
        ha_disk.create()
        
        # Boot disk
        boot_disk = PersistentDisk("vm-boot")
        boot_disk.project("my-project").boot_volume("ubuntu")
        boot_disk.zone("us-central1-a")
        boot_disk.create()
        
        # Shared storage
        shared_disk = PersistentDisk("shared-storage")
        shared_disk.project("my-project").shared_volume()
        shared_disk.zone("us-central1-a").size_tb(5)
        shared_disk.create()
        
        # Cost-optimized backup disk
        backup_disk = PersistentDisk("backup-storage")
        backup_disk.project("my-project").backup_disk()
        backup_disk.zone("us-central1-a")
        backup_disk.create()
        
        # Cross-Cloud Magic optimization
        optimized_disk = PersistentDisk("optimized-disk")
        optimized_disk.project("my-project").zone("us-central1-a")
        optimized_disk.size_tb(1).optimize_for("performance")
        optimized_disk.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Google Cloud Persistent Disk with disk name.
        
        Args:
            name: Disk name
        """
        # Initialize all parent classes
        PersistentDiskCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Persistent Disk"""
        disk_type = self._get_disk_type_from_config()
        location = self.region if self.region else self.zone
        location_type = "region" if self.region else "zone"
        status = "created" if self.disk_created else "configured"
        
        return (f"PersistentDisk(name='{self.disk_name}', "
                f"type='{self.pd_type}', "
                f"size='{self.size_gb}GB', "
                f"{location_type}='{location}', "
                f"interface='{self.interface}', "
                f"project='{self.project_id}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Persistent Disk configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze disk configuration
        disk_features = []
        if self.boot:
            disk_features.append("boot_disk")
        if self.multi_writer:
            disk_features.append("multi_writer")
        if self.enable_deletion_protection:
            disk_features.append("deletion_protection")
        if self.enable_confidential_compute:
            disk_features.append("confidential_compute")
        if self.region:
            disk_features.append("regional_disk")
        if self.auto_delete:
            disk_features.append("auto_delete")
            
        # Analyze performance
        performance_specs = self.get_performance_specs()
        
        # Analyze source configuration
        source_info = {
            "source_image": self.source_image,
            "source_image_family": self.source_image_family,
            "source_snapshot": self.source_snapshot,
            "source_disk": self.source_disk,
            "blank_disk": not any([self.source_image, self.source_image_family, 
                                   self.source_snapshot, self.source_disk])
        }
        
        summary = {
            "disk_name": self.disk_name,
            "project_id": self.project_id,
            "disk_description": self.disk_description,
            "disk_type": self._get_disk_type_from_config(),
            
            # Disk configuration
            "size_gb": self.size_gb,
            "size_tb": round(self.size_gb / 1024, 2),
            "pd_type": self.pd_type,
            "zone": self.zone,
            "region": self.region,
            "is_regional": bool(self.region),
            
            # Performance configuration
            "performance": performance_specs,
            "interface": self.interface,
            "mode": self.mode,
            
            # Source configuration
            "source": source_info,
            
            # Attachment configuration
            "attachment": {
                "boot": self.boot,
                "auto_delete": self.auto_delete,
                "multi_writer": self.multi_writer
            },
            
            # Security configuration
            "security": {
                "deletion_protection": self.enable_deletion_protection,
                "confidential_compute": self.enable_confidential_compute,
                "encryption_key": self.encryption_key,
                "customer_encryption_key": bool(self.customer_encryption_key)
            },
            
            # Features analysis
            "disk_features": disk_features,
            "is_production_ready": self.is_production_ready(),
            
            # Labels and metadata
            "labels": self.disk_labels,
            "label_count": len(self.disk_labels),
            "annotations": self.disk_annotations,
            
            # State
            "state": {
                "exists": self.disk_exists,
                "created": self.disk_created,
                "disk_state": self.disk_state,
                "deployment_status": self.deployment_status
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_disk_cost():,.2f}",
            "cost_per_gb": f"${self._estimate_disk_cost() / self.size_gb:.4f}"
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\\n💾 Google Cloud Persistent Disk Configuration: {self.disk_name}")
        print(f"   📁 Project: {self.project_id}")
        print(f"   📝 Description: {self.disk_description}")
        print(f"   🎯 Disk Type: {self._get_disk_type_from_config().replace('_', ' ').title()}")
        
        # Disk configuration
        print(f"\\n💿 Disk Configuration:")
        print(f"   📏 Size: {self.size_gb:,} GB ({self.size_gb/1024:.1f} TB)")
        print(f"   💿 Type: {self.pd_type}")
        
        if self.region:
            print(f"   🌍 Region: {self.region}")
            if self.replica_zones:
                print(f"      └─ 🔄 Replica zones: {', '.join(self.replica_zones)}")
        else:
            print(f"   📍 Zone: {self.zone}")
            
        # Performance configuration
        performance = self.get_performance_specs()
        print(f"\\n⚡ Performance Specifications:")
        print(f"   📊 Max Read IOPS: {performance['max_iops_read']:,}")
        print(f"   📊 Max Write IOPS: {performance['max_iops_write']:,}")
        print(f"   🚀 Max Read Throughput: {performance['max_throughput_read']:,} MB/s")
        print(f"   🚀 Max Write Throughput: {performance['max_throughput_write']:,} MB/s")
        
        if self.pd_type == "pd-extreme":
            if self.provisioned_iops:
                print(f"   ⚡ Provisioned IOPS: {self.provisioned_iops:,}")
            if self.provisioned_throughput:
                print(f"   🚀 Provisioned Throughput: {self.provisioned_throughput:,} MB/s")
                
        # Source configuration
        print(f"\\n🖼️  Source Configuration:")
        if self.source_image:
            print(f"   🖼️  Source Image: {self.source_image}")
        elif self.source_image_family:
            print(f"   👨‍👩‍👧‍👦 Image Family: {self.source_image_family}")
        elif self.source_snapshot:
            print(f"   📸 Source Snapshot: {self.source_snapshot}")
        elif self.source_disk:
            print(f"   💿 Source Disk: {self.source_disk}")
        else:
            print(f"   🆕 Blank Disk: No source")
            
        # Attachment configuration
        print(f"\\n🔌 Attachment Configuration:")
        print(f"   🔌 Interface: {self.interface}")
        print(f"   📖 Mode: {self.mode}")
        print(f"   🥾 Boot Disk: {'✅ Yes' if self.boot else '❌ No'}")
        print(f"   🗑️  Auto Delete: {'✅ Yes' if self.auto_delete else '❌ No'}")
        print(f"   👥 Multi-writer: {'✅ Yes' if self.multi_writer else '❌ No'}")
        
        # Security configuration
        print(f"\\n🔒 Security Configuration:")
        print(f"   🔒 Deletion Protection: {'✅ Enabled' if self.enable_deletion_protection else '❌ Disabled'}")
        print(f"   🛡️  Confidential Compute: {'✅ Enabled' if self.enable_confidential_compute else '❌ Disabled'}")
        if self.encryption_key:
            print(f"   🔐 Encryption: 🔑 Customer-managed ({self.encryption_key})")
        elif self.customer_encryption_key:
            print(f"   🔐 Encryption: 🔑 Customer-supplied")
        else:
            print(f"   🔐 Encryption: 🔒 Google-managed")
            
        # Labels
        if self.disk_labels:
            print(f"\\n🏷️  Labels ({len(self.disk_labels)}):")
            for key, value in list(self.disk_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.disk_labels) > 5:
                print(f"   • ... and {len(self.disk_labels) - 5} more")
                
        # Production readiness
        production_ready = self.is_production_ready()
        print(f"\\n🚀 Production Readiness: {'✅ Ready' if production_ready else '⚠️  Needs optimization'}")
        if not production_ready:
            issues = []
            if self.size_gb < 100:
                issues.append("Small disk size")
            if self.pd_type == "pd-standard":
                issues.append("Standard disk type")
            if self.auto_delete:
                issues.append("Auto-delete enabled")
            if not self.enable_deletion_protection:
                issues.append("No deletion protection")
                
            for issue in issues[:3]:
                print(f"   ⚠️  {issue}")
                
        # Cost estimate
        cost = self._estimate_disk_cost()
        print(f"\\n💰 Cost Estimate:")
        print(f"   💰 Monthly: ${cost:,.2f}")
        print(f"   📊 Per GB: ${cost / self.size_gb:.4f}/month")
        
        # Disk type pricing
        pricing_info = {
            "pd-standard": "$0.040/GB/month",
            "pd-balanced": "$0.100/GB/month", 
            "pd-ssd": "$0.170/GB/month",
            "pd-extreme": "$0.650/GB/month"
        }
        print(f"   💿 {self.pd_type}: {pricing_info.get(self.pd_type, 'Unknown')}")
        
        # Console and URLs
        if self.project_id:
            print(f"\\n🌐 Console:")
            print(f"   🔗 https://console.cloud.google.com/compute/disks?project={self.project_id}")
            
        # Disk capabilities
        print(f"\\n💾 Persistent Disk Capabilities:")
        print(f"   ├─ 📈 Up to 64TB capacity per disk")
        print(f"   ├─ 🚀 Up to 100,000 IOPS (pd-extreme)")
        print(f"   ├─ 🌍 Regional disks for high availability")
        print(f"   ├─ 👥 Multi-attach support")
        print(f"   ├─ 🔄 Dynamic resizing without downtime")
        print(f"   ├─ 📸 Automatic snapshots and backup")
        print(f"   ├─ 🛡️  Built-in encryption at rest")
        print(f"   └─ ⚡ NVMe interface support")
    
    def get_status(self) -> Dict[str, Any]:
        """Get disk status for backwards compatibility"""
        return {
            "disk_name": self.disk_name,
            "project_id": self.project_id,
            "size_gb": self.size_gb,
            "disk_type": self.pd_type,
            "zone": self.zone,
            "region": self.region,
            "is_regional": bool(self.region),
            "interface": self.interface,
            "mode": self.mode,
            "boot": self.boot,
            "auto_delete": self.auto_delete,
            "multi_writer": self.multi_writer,
            "deletion_protection": self.enable_deletion_protection,
            "is_production_ready": self.is_production_ready(),
            "deployment_status": self.deployment_status,
            "estimated_cost": f"${self._estimate_disk_cost():,.2f}/month"
        }


# Convenience function for creating Persistent Disks
def create_persistent_disk(name: str) -> PersistentDisk:
    """
    Create a new Persistent Disk.
    
    Args:
        name: Disk name
        
    Returns:
        PersistentDisk instance
    """
    return PersistentDisk(name)


# Pattern-specific convenience functions
def create_boot_disk(name: str, project_id: str, zone: str, os_type: str = "ubuntu") -> PersistentDisk:
    """Create a boot disk with OS image"""
    disk = PersistentDisk(name)
    disk.project(project_id).zone(zone).boot_volume(os_type)
    return disk


def create_data_disk(name: str, project_id: str, zone: str, size_tb: float = 1) -> PersistentDisk:
    """Create a data disk for applications"""
    disk = PersistentDisk(name)
    disk.project(project_id).zone(zone).data_volume().size_tb(size_tb)
    return disk


def create_database_disk(name: str, project_id: str, zone: str, size_tb: float = 2) -> PersistentDisk:
    """Create a high-performance disk for databases"""
    disk = PersistentDisk(name)
    disk.project(project_id).zone(zone).database_disk().size_tb(size_tb)
    return disk


def create_backup_disk(name: str, project_id: str, zone: str, size_tb: float = 10) -> PersistentDisk:
    """Create a cost-optimized disk for backups"""
    disk = PersistentDisk(name)
    disk.project(project_id).zone(zone).backup_disk().size_tb(size_tb)
    return disk


def create_regional_disk(name: str, project_id: str, region: str, size_tb: float = 1) -> PersistentDisk:
    """Create a regional disk for high availability"""
    disk = PersistentDisk(name)
    disk.project(project_id).regional_disk(region).production_disk().size_tb(size_tb)
    return disk


def create_shared_disk(name: str, project_id: str, zone: str, size_tb: float = 5) -> PersistentDisk:
    """Create a shared disk with multi-writer support"""
    disk = PersistentDisk(name)
    disk.project(project_id).zone(zone).shared_volume().size_tb(size_tb)
    return disk


# Export the class for easy importing
__all__ = [
    'PersistentDisk',
    'create_persistent_disk',
    'create_boot_disk',
    'create_data_disk',
    'create_database_disk',
    'create_backup_disk',
    'create_regional_disk',
    'create_shared_disk'
]
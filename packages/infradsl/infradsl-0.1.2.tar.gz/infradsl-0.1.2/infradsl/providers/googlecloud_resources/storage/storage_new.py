"""
GCP Cloud Storage Complete Implementation

Combines all Cloud Storage functionality through multiple inheritance:
- StorageCore: Core attributes and authentication
- StorageConfigurationMixin: Chainable configuration methods  
- StorageLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from .storage_core import StorageCore
from .storage_configuration import StorageConfigurationMixin
from .storage_lifecycle import StorageLifecycleMixin


class Storage(StorageLifecycleMixin, StorageConfigurationMixin, StorageCore):
    """
    Complete GCP Cloud Storage implementation for object storage.
    
    This class combines:
    - Bucket configuration methods (storage classes, versioning, lifecycle)
    - Bucket lifecycle management (create, destroy, preview)
    - File upload and static website hosting
    - CORS and access control
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize Storage instance for bucket management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$0.20/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._cdn_enabled = False
        self._cdn_config = {}
        self._backup_retention_days = None
        
    def validate_configuration(self):
        """Validate the current Cloud Storage configuration"""
        errors = []
        warnings = []
        
        # Validate bucket name
        if not self.bucket_name:
            errors.append("Bucket name is required")
        elif not self._is_valid_bucket_name(self.bucket_name):
            errors.append("Invalid bucket name format")
        
        # Validate location
        if self.location and not self._is_valid_location(self.location):
            warnings.append(f"Unusual location: {self.location}")
        
        # Validate storage class
        if not self._is_valid_storage_class(self.storage_class):
            errors.append(f"Invalid storage class: {self.storage_class}")
        
        # Validate lifecycle rules
        for rule in self.lifecycle_rules:
            if not rule.get("id"):
                errors.append("Lifecycle rule missing ID")
        
        # Validate website configuration
        if hasattr(self, '_website_config') and self.public_access_prevention != "inherited":
            warnings.append("Website hosting enabled but bucket is private - may not be accessible")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_bucket_info(self):
        """Get complete information about the Cloud Storage bucket"""
        return {
            'bucket_name': self.bucket_name,
            'location': self.location,
            'bucket_url': self.bucket_url,
            'bucket_arn': self.bucket_arn,
            'website_url': self.website_url,
            'storage_class': self.storage_class,
            'public_access_prevention': self.public_access_prevention,
            'versioning_enabled': self.versioning_enabled,
            'lifecycle_rules_count': len(self.lifecycle_rules),
            'cors_rules_count': len(self.cors_rules),
            'files_to_upload': len(self._files_to_upload),
            'directories_to_upload': len(self._directories_to_upload),
            'labels_count': len(self.bucket_labels),
            'bucket_exists': self.bucket_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'cdn_enabled': self._cdn_enabled
        }
    
    def clone(self, new_name: str):
        """Create a copy of this bucket with a new name"""
        cloned_bucket = Storage(new_name)
        cloned_bucket.bucket_name = new_name
        cloned_bucket.location = self.location
        cloned_bucket.storage_class = self.storage_class
        cloned_bucket.public_access_prevention = self.public_access_prevention
        cloned_bucket.versioning_enabled = self.versioning_enabled
        cloned_bucket.lifecycle_rules = self.lifecycle_rules.copy()
        cloned_bucket.cors_rules = self.cors_rules.copy()
        cloned_bucket.bucket_labels = self.bucket_labels.copy()
        cloned_bucket._files_to_upload = self._files_to_upload.copy()
        cloned_bucket._directories_to_upload = self._directories_to_upload.copy()
        return cloned_bucket
    
    def export_configuration(self):
        """Export bucket configuration for backup or migration"""
        return {
            'metadata': {
                'bucket_name': self.bucket_name,
                'location': self.location,
                'storage_class': self.storage_class,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'public_access_prevention': self.public_access_prevention,
                'versioning_enabled': self.versioning_enabled,
                'lifecycle_rules': self.lifecycle_rules,
                'cors_rules': self.cors_rules,
                'retention_period': self.retention_period,
                'optimization_priority': self._optimization_priority,
                'cdn_enabled': self._cdn_enabled,
                'backup_retention_days': self._backup_retention_days
            },
            'labels': self.bucket_labels,
            'uploads': {
                'files': self._files_to_upload,
                'directories': self._directories_to_upload
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import bucket configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.public_access_prevention = config.get('public_access_prevention', 'enforced')
            self.versioning_enabled = config.get('versioning_enabled', False)
            self.lifecycle_rules = config.get('lifecycle_rules', [])
            self.cors_rules = config.get('cors_rules', [])
            self.retention_period = config.get('retention_period')
            self._optimization_priority = config.get('optimization_priority')
            self._cdn_enabled = config.get('cdn_enabled', False)
            self._backup_retention_days = config.get('backup_retention_days')
        
        if 'labels' in config_data:
            self.bucket_labels = config_data['labels']
        
        if 'uploads' in config_data:
            uploads = config_data['uploads']
            self._files_to_upload = uploads.get('files', [])
            self._directories_to_upload = uploads.get('directories', [])
        
        return self
    
    def optimize_for(self, priority: str):
        """Use Cross-Cloud Magic to optimize for cost/performance/reliability
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        self._optimization_priority = priority
        
        print(f"🎯 Cross-Cloud Magic: Optimizing Cloud Storage for {priority}")
        
        # Apply GCP-specific optimizations
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective storage")
            if self.storage_class == "STANDARD":
                print("   💡 Suggestion: Consider NEARLINE for infrequently accessed data")
                print("   💡 Suggestion: Consider COLDLINE for archival data")
            print("   💡 Lifecycle rules can automatically transition to cheaper storage classes")
            
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance storage")
            if self.storage_class != "STANDARD":
                print("   💡 Switching to STANDARD storage class for optimal performance")
                self.storage_class = "STANDARD"
            if self.location in ["US", "EU", "ASIA"]:
                print("   💡 Multi-region storage provides better global performance")
            
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable storage")
            if not self.versioning_enabled:
                print("   💡 Enabling versioning for data protection")
                self.versioning_enabled = True
            if self.location not in ["US", "EU", "ASIA"]:
                print("   💡 Consider multi-region storage for higher availability")
            
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant storage")
            if self.public_access_prevention != "enforced":
                print("   💡 Enforcing private access for compliance")
                self.public_access_prevention = "enforced"
            if not self.retention_period:
                print("   💡 Consider setting retention policy for compliance")
        
        return self


# Convenience functions for creating Storage instances
def create_bucket(name: str, location: str = None, storage_class: str = "STANDARD") -> Storage:
    """Create a new Cloud Storage bucket with basic configuration"""
    bucket = Storage(name)
    bucket.bucket(name)
    if location:
        bucket.region(location)
    bucket.storage(storage_class)
    return bucket

def create_static_website(name: str, location: str = None) -> Storage:
    """Create a bucket configured for static website hosting"""
    bucket = Storage(name)
    bucket.bucket(name).static_website().cdn(True).optimize_for("performance")
    if location:
        bucket.region(location)
    return bucket

def create_backup_bucket(name: str, retention_days: int = 30) -> Storage:
    """Create a bucket optimized for backups"""
    bucket = Storage(name)
    bucket.bucket(name).backup_bucket().backup_retention(retention_days).optimize_for("reliability")
    return bucket

def create_data_lake(name: str, location: str = None) -> Storage:
    """Create a bucket optimized for data lake storage"""
    bucket = Storage(name)
    bucket.bucket(name).storage("NEARLINE").lifecycle(90, "transition", "COLDLINE").optimize_for("cost")
    if location:
        bucket.region(location)
    return bucket
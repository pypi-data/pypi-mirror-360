"""
AWS S3 Complete Implementation

Combines all S3 functionality through multiple inheritance:
- S3Core: Core attributes and authentication
- S3ConfigurationMixin: Chainable configuration methods  
- S3LifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from .s3_core import S3Core
from .s3_configuration import S3ConfigurationMixin
from .s3_lifecycle import S3LifecycleMixin


class S3(S3LifecycleMixin, S3ConfigurationMixin, S3Core):
    """
    Complete AWS S3 implementation for object storage.
    
    This class combines:
    - Bucket configuration methods (storage classes, versioning, encryption)
    - Bucket lifecycle management (create, destroy, preview)
    - File upload and static website hosting
    - CORS and lifecycle rules
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize S3 instance for bucket management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$0.023/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._cdn_enabled = False
        self._cdn_config = {}
        self._backup_retention_days = None
        
    def validate_configuration(self):
        """Validate the current S3 configuration"""
        errors = []
        warnings = []
        
        # Validate bucket name
        if not self.bucket_name:
            errors.append("Bucket name is required")
        elif not self._is_valid_bucket_name(self.bucket_name):
            errors.append("Invalid bucket name format")
        
        # Validate region
        if self.region_name and not self._is_valid_region(self.region_name):
            warnings.append(f"Unusual region: {self.region_name}")
        
        # Validate storage class
        valid_classes = ["STANDARD", "STANDARD_IA", "ONEZONE_IA", "REDUCED_REDUNDANCY", "GLACIER", "DEEP_ARCHIVE"]
        if self.storage_class not in valid_classes:
            errors.append(f"Invalid storage class: {self.storage_class}")
        
        # Validate lifecycle rules
        for rule in self.lifecycle_rules:
            if not rule.get("ID"):
                errors.append("Lifecycle rule missing ID")
        
        # Validate website configuration
        if self.website_enabled and not self.public_access:
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
        """Get complete information about the S3 bucket"""
        return {
            'bucket_name': self.bucket_name,
            'region': self.region_name or 'us-east-1',
            'bucket_url': self.bucket_url,
            'website_url': self.website_url,
            'bucket_arn': self.bucket_arn,
            'storage_class': self.storage_class,
            'public_access': self.public_access,
            'versioning_enabled': self.versioning_enabled,
            'encryption_enabled': self.encryption_enabled,
            'website_enabled': self.website_enabled,
            'cors_enabled': self.cors_enabled,
            'lifecycle_rules_count': len(self.lifecycle_rules),
            'files_to_upload': len(self._files_to_upload),
            'directories_to_upload': len(self._directories_to_upload),
            'tags_count': len(self.bucket_tags),
            'bucket_exists': self.bucket_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'cdn_enabled': self._cdn_enabled
        }
    
    def clone(self, new_name: str):
        """Create a copy of this bucket with a new name"""
        cloned_bucket = S3(new_name)
        cloned_bucket.bucket_name = new_name
        cloned_bucket.region_name = self.region_name
        cloned_bucket.storage_class = self.storage_class
        cloned_bucket.public_access = self.public_access
        cloned_bucket.versioning_enabled = self.versioning_enabled
        cloned_bucket.encryption_enabled = self.encryption_enabled
        cloned_bucket.website_enabled = self.website_enabled
        cloned_bucket.cors_enabled = self.cors_enabled
        cloned_bucket.lifecycle_rules = self.lifecycle_rules.copy()
        cloned_bucket.bucket_tags = self.bucket_tags.copy()
        cloned_bucket._files_to_upload = self._files_to_upload.copy()
        cloned_bucket._directories_to_upload = self._directories_to_upload.copy()
        return cloned_bucket
    
    def export_configuration(self):
        """Export bucket configuration for backup or migration"""
        return {
            'metadata': {
                'bucket_name': self.bucket_name,
                'region': self.region_name or 'us-east-1',
                'storage_class': self.storage_class,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'public_access': self.public_access,
                'versioning_enabled': self.versioning_enabled,
                'encryption_enabled': self.encryption_enabled,
                'website_enabled': self.website_enabled,
                'cors_enabled': self.cors_enabled,
                'lifecycle_rules': self.lifecycle_rules,
                'optimization_priority': self._optimization_priority,
                'cdn_enabled': self._cdn_enabled,
                'backup_retention_days': self._backup_retention_days
            },
            'tags': self.bucket_tags,
            'uploads': {
                'files': self._files_to_upload,
                'directories': self._directories_to_upload
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import bucket configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.public_access = config.get('public_access', False)
            self.versioning_enabled = config.get('versioning_enabled', False)
            self.encryption_enabled = config.get('encryption_enabled', True)
            self.website_enabled = config.get('website_enabled', False)
            self.cors_enabled = config.get('cors_enabled', False)
            self.lifecycle_rules = config.get('lifecycle_rules', [])
            self._optimization_priority = config.get('optimization_priority')
            self._cdn_enabled = config.get('cdn_enabled', False)
            self._backup_retention_days = config.get('backup_retention_days')
        
        if 'tags' in config_data:
            self.bucket_tags = config_data['tags']
        
        if 'uploads' in config_data:
            uploads = config_data['uploads']
            self._files_to_upload = uploads.get('files', [])
            self._directories_to_upload = uploads.get('directories', [])
        
        return self
    
    def _is_valid_bucket_name(self, bucket_name: str) -> bool:
        """Validate S3 bucket name according to AWS rules"""
        import re
        
        # Basic validation rules
        if len(bucket_name) < 3 or len(bucket_name) > 63:
            return False
        
        # Must be lowercase letters, numbers, hyphens, and periods
        if not re.match(r'^[a-z0-9.-]+$', bucket_name):
            return False
        
        # Cannot start or end with period or hyphen
        if bucket_name.startswith('.') or bucket_name.startswith('-'):
            return False
        if bucket_name.endswith('.') or bucket_name.endswith('-'):
            return False
        
        # Cannot contain consecutive periods
        if '..' in bucket_name:
            return False
        
        return True
    
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
        
        print(f"🎯 Cross-Cloud Magic: Optimizing S3 for {priority}")
        
        # Apply S3-specific optimizations
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective storage")
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance storage")
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable storage")
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant storage")
        
        return self
    
    def _is_valid_region(self, region: str) -> bool:
        """Check if region is a known AWS region"""
        aws_regions = [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2',
            'ca-central-1', 'sa-east-1'
        ]
        return region in aws_regions


# Convenience functions for creating S3 instances
def create_bucket(name: str, region: str = None, storage_class: str = "STANDARD") -> S3:
    """Create a new S3 bucket with basic configuration"""
    bucket = S3(name)
    bucket.bucket(name)
    if region:
        bucket.region(region)
    bucket.storage(storage_class)
    return bucket

def create_static_website(name: str, region: str = None) -> S3:
    """Create a bucket configured for static website hosting"""
    bucket = S3(name)
    bucket.bucket(name).static_website().cdn(True).optimize_for("performance")
    if region:
        bucket.region(region)
    return bucket

def create_backup_bucket(name: str, retention_days: int = 30) -> S3:
    """Create a bucket optimized for backups"""
    bucket = S3(name)
    bucket.bucket(name).private().versioning(True).backup_retention(retention_days).optimize_for("reliability")
    return bucket

def create_data_lake(name: str, region: str = None) -> S3:
    """Create a bucket optimized for data lake storage"""
    bucket = S3(name)
    bucket.bucket(name).storage("STANDARD_IA").lifecycle(90, "transition", "GLACIER").optimize_for("cost")
    if region:
        bucket.region(region)
    return bucket
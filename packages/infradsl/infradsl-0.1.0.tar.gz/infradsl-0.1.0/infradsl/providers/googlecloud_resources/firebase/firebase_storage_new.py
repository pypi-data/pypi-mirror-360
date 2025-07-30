"""
Firebase Storage Complete Implementation

Complete Firebase Storage implementation combining core functionality, 
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .firebase_storage_core import FirebaseStorageCore
from .firebase_storage_configuration import FirebaseStorageConfigurationMixin
from .firebase_storage_lifecycle import FirebaseStorageLifecycleMixin


class FirebaseStorage(FirebaseStorageCore, FirebaseStorageConfigurationMixin, FirebaseStorageLifecycleMixin):
    """
    Complete Firebase Storage implementation.
    
    This class combines:
    - FirebaseStorageCore: Basic storage attributes and authentication
    - FirebaseStorageConfigurationMixin: Chainable configuration methods
    - FirebaseStorageLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent storage configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Complete file storage solution (upload, download, security, CDN)
    - Storage patterns (media, documents, backups, user uploads, static assets)
    - Security features (Firebase Security Rules, access control)
    - Performance optimization (CDN, caching, compression, image transformations)
    - Lifecycle management (retention, archiving, automatic deletion)
    - Upload configuration (file types, size limits, thumbnails)
    - Environment-specific settings (development, staging, production)
    
    Example:
        # Media storage
        media = FirebaseStorage("media-storage")
        media.project("my-firebase-project").media_storage()
        media.create()
        
        # Document storage with strict security
        docs = FirebaseStorage("documents")
        docs.project("my-project").document_storage()
        docs.strict_security_rules()
        docs.create()
        
        # User uploads with thumbnails
        uploads = FirebaseStorage("user-uploads")
        uploads.project("my-project").user_uploads()
        uploads.thumbnail_generation().image_optimization()
        uploads.create()
        
        # Backup storage with archival
        backups = FirebaseStorage("backups")
        backups.project("my-project").backup_storage()
        backups.archive_after_days(30).delete_after_days(365)
        backups.create()
        
        # Static assets with CDN
        assets = FirebaseStorage("static-assets")
        assets.project("my-project").static_assets()
        assets.public_read().cdn().compression()
        assets.create()
        
        # Custom configuration
        storage = FirebaseStorage("custom-storage")
        storage.project("my-project").location("us-west1")
        storage.storage_class("NEARLINE").authenticated_read()
        storage.cors_allow_all().versioning().lifecycle_rule()
        storage.max_upload_size_mb(100).allow_images().allow_videos()
        storage.thumbnail_generation().cache_images().cdn()
        storage.monitoring().logging()
        storage.create()
        
        # Production-ready configuration
        prod = FirebaseStorage("production-storage")
        prod.project("prod-project").production()
        prod.strict_security_rules().monitoring().versioning()
        prod.create()
        
        # Cross-Cloud Magic optimization
        optimized = FirebaseStorage("optimized-storage")
        optimized.project("my-project").media_storage()
        optimized.optimize_for("performance")
        optimized.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Firebase Storage with storage name.
        
        Args:
            name: Storage name (used for bucket naming and identification)
        """
        # Initialize all parent classes
        FirebaseStorageCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Firebase Storage instance"""
        storage_type = self._get_storage_type_from_config()
        access_type = "public" if self.public_access else "authenticated" if self.authenticated_read else "private"
        security_info = "custom rules" if self.has_security_rules() else "default rules"
        status = "configured" if self.firebase_project_id else "unconfigured"
        
        return (f"FirebaseStorage(name='{self.storage_name}', "
                f"type='{storage_type}', "
                f"access='{access_type}', "
                f"security='{security_info}', "
                f"bucket='{self.get_bucket_name()}', "
                f"project='{self.firebase_project_id}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Firebase Storage configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze storage configuration
        storage_features = []
        if self.public_access:
            storage_features.append("public_access")
        if self.authenticated_read:
            storage_features.append("authenticated_read")
        if self.has_security_rules():
            storage_features.append("security_rules")
        if self.cors_enabled:
            storage_features.append("cors")
        if self.versioning_enabled:
            storage_features.append("versioning")
        if self.cdn_enabled:
            storage_features.append("cdn")
        if self.compression_enabled:
            storage_features.append("compression")
        
        # Categorize by storage purpose
        storage_categories = []
        storage_type = self._get_storage_type_from_config()
        if "media" in storage_type:
            storage_categories.append("media_storage")
        elif "document" in storage_type:
            storage_categories.append("document_storage")
        elif "backup" in storage_type:
            storage_categories.append("backup_storage")
        elif "user" in storage_type:
            storage_categories.append("user_uploads")
        elif "static" in storage_type:
            storage_categories.append("static_assets")
        elif "archive" in storage_type:
            storage_categories.append("archive_storage")
        
        # Analyze performance features
        performance_features = []
        if self.cdn_enabled:
            performance_features.append("cdn")
        if self.compression_enabled:
            performance_features.append("compression")
        if self.has_caching_configured():
            performance_features.append("caching")
        if self.thumbnail_generation:
            performance_features.append("thumbnails")
        if len(self.image_transformations) > 0:
            performance_features.append("image_transformations")
        
        # Security analysis
        security_features = []
        if self.has_security_rules():
            security_features.append("security_rules")
        if not self.public_access:
            security_features.append("private_access")
        if self.uniform_bucket_level_access:
            security_features.append("uniform_access")
        if self.versioning_enabled:
            security_features.append("versioning")
        if self.retention_policy:
            security_features.append("retention_policy")
        
        summary = {
            "storage_name": self.storage_name,
            "bucket_name": self.get_bucket_name(),
            "firebase_project_id": self.firebase_project_id,
            "storage_description": self.storage_description,
            "storage_type": storage_type,
            "storage_categories": storage_categories,
            
            # Storage configuration
            "location": self.location,
            "storage_class": self.storage_class,
            
            # Access configuration
            "public_access": self.public_access,
            "public_read": self.public_read,
            "authenticated_read": self.authenticated_read,
            "uniform_bucket_level_access": self.uniform_bucket_level_access,
            
            # Security configuration
            "security_features": security_features,
            "has_security_rules": self.has_security_rules(),
            "security_rules_file": self.security_rules_file,
            "default_security_rules": self.default_security_rules,
            
            # CORS configuration
            "cors_enabled": self.cors_enabled,
            "cors_origins": self.cors_origins,
            "cors_methods": self.cors_methods,
            "cors_headers": self.cors_headers,
            
            # Lifecycle configuration
            "lifecycle_rules": self.lifecycle_rules,
            "lifecycle_rule_count": len(self.lifecycle_rules),
            "versioning_enabled": self.versioning_enabled,
            "retention_policy": self.retention_policy,
            
            # Performance configuration
            "performance_features": performance_features,
            "cdn_enabled": self.cdn_enabled,
            "compression_enabled": self.compression_enabled,
            "cache_control": self.cache_control,
            "cache_rule_count": len(self.cache_control),
            
            # Upload configuration
            "max_upload_size": self.max_upload_size,
            "allowed_file_types": self.allowed_file_types,
            "file_type_count": len(self.allowed_file_types),
            "thumbnail_generation": self.thumbnail_generation,
            "image_transformations": self.image_transformations,
            
            # Monitoring configuration
            "logging_enabled": self.logging_enabled,
            "monitoring_enabled": self.monitoring_enabled,
            "notifications": self.notifications,
            "notification_count": len(self.notifications),
            
            # Features analysis
            "storage_features": storage_features,
            "has_lifecycle_rules": self.has_lifecycle_rules(),
            "has_cors_configured": self.has_cors_configured(),
            "has_caching_configured": self.has_caching_configured(),
            "has_monitoring_enabled": self.has_monitoring_enabled(),
            "is_production_ready": self.is_production_ready(),
            
            # Labels and metadata
            "labels": self.storage_labels,
            "label_count": len(self.storage_labels),
            "annotations": self.storage_annotations,
            
            # State
            "state": {
                "exists": self.bucket_exists,
                "created": self.bucket_created,
                "bucket_state": self.bucket_state,
                "deployment_status": self.deployment_status
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_firebase_storage_cost():.2f}",
            "is_free_tier": self._estimate_firebase_storage_cost() == 0.0
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\\n🔥 Firebase Storage Configuration: {self.storage_name}")
        print(f"   📁 Firebase Project: {self.firebase_project_id}")
        print(f"   📁 Bucket: gs://{self.get_bucket_name()}")
        print(f"   📝 Description: {self.storage_description}")
        print(f"   🎯 Storage Type: {self._get_storage_type_from_config().replace('_', ' ').title()}")
        
        # Storage configuration
        print(f"\\n📁 Storage Configuration:")
        print(f"   📍 Location: {self.location}")
        print(f"   💾 Storage Class: {self.storage_class}")
        
        # Access configuration
        print(f"\\n🔒 Access Configuration:")
        print(f"   🌐 Public Access: {'✅ Enabled' if self.public_access else '❌ Disabled'}")
        print(f"   👁️  Public Read: {'✅ Enabled' if self.public_read else '❌ Disabled'}")
        print(f"   🔐 Authenticated Read: {'✅ Enabled' if self.authenticated_read else '❌ Disabled'}")
        print(f"   🛡️  Uniform Access: {'✅ Enabled' if self.uniform_bucket_level_access else '❌ Disabled'}")
        
        # Security configuration
        print(f"\\n🔒 Security Configuration:")
        if self.has_security_rules():
            if self.security_rules_file:
                print(f"   📄 Rules File: {self.security_rules_file}")
            else:
                print(f"   📝 Custom Rules: ✅ Configured")
        else:
            print(f"   📝 Security Rules: {'✅ Default (auth required)' if self.default_security_rules else '❌ None'}")
        
        if self.cors_enabled:
            print(f"   🌍 CORS: ✅ Enabled")
            if self.cors_origins == ["*"]:
                print(f"      🌐 Origins: All (*)")
            else:
                print(f"      🌐 Origins: {len(self.cors_origins)} configured")
                for origin in self.cors_origins[:3]:
                    print(f"         • {origin}")
                if len(self.cors_origins) > 3:
                    print(f"         • ... and {len(self.cors_origins) - 3} more")
        else:
            print(f"   🌍 CORS: ❌ Disabled")
        
        # Lifecycle configuration
        print(f"\\n⏰ Lifecycle Configuration:")
        if len(self.lifecycle_rules) > 0:
            print(f"   📋 Rules: {len(self.lifecycle_rules)}")
            for i, rule in enumerate(self.lifecycle_rules[:3]):
                action = rule.get('action', 'unknown')
                condition = rule.get('condition', {})
                
                if 'age' in condition:
                    print(f"      • {action} after {condition['age']} days")
                elif 'storageClass' in condition:
                    print(f"      • Move to {condition['storageClass']}")
                else:
                    print(f"      • {action}")
            
            if len(self.lifecycle_rules) > 3:
                print(f"      • ... and {len(self.lifecycle_rules) - 3} more rules")
        else:
            print(f"   📋 Rules: None")
        
        print(f"   🔄 Versioning: {'✅ Enabled' if self.versioning_enabled else '❌ Disabled'}")
        
        if self.retention_policy:
            retention_days = int(self.retention_policy['retentionPeriod']) // 86400
            print(f"   🔒 Retention: {retention_days} days")
        else:
            print(f"   🔒 Retention: None")
        
        # Performance configuration
        print(f"\\n🚀 Performance Configuration:")
        print(f"   🌍 CDN: {'✅ Enabled' if self.cdn_enabled else '❌ Disabled'}")
        print(f"   🗜️  Compression: {'✅ Enabled' if self.compression_enabled else '❌ Disabled'}")
        
        cache_rules = len(self.cache_control)
        print(f"   📦 Cache Rules: {cache_rules}")
        if cache_rules > 0:
            for pattern, rule in list(self.cache_control.items())[:3]:
                max_age_hours = rule['max_age'] // 3600 if rule['max_age'] >= 3600 else 0
                if max_age_hours > 0:
                    print(f"      • {pattern}: {max_age_hours}h")
                else:
                    print(f"      • {pattern}: {rule['max_age']}s")
            if cache_rules > 3:
                print(f"      • ... and {cache_rules - 3} more rules")
        
        # Upload configuration
        print(f"\\n📤 Upload Configuration:")
        if self.max_upload_size:
            size_mb = self.max_upload_size // (1024 * 1024)
            print(f"   📏 Max Size: {size_mb} MB")
        else:
            print(f"   📏 Max Size: Unlimited")
        
        if self.allowed_file_types:
            print(f"   📄 File Types ({len(self.allowed_file_types)}):") 
            for file_type in self.allowed_file_types[:5]:
                print(f"      • {file_type}")
            if len(self.allowed_file_types) > 5:
                print(f"      • ... and {len(self.allowed_file_types) - 5} more")
        else:
            print(f"   📄 File Types: All allowed")
        
        print(f"   🖼️  Thumbnails: {'✅ Enabled' if self.thumbnail_generation else '❌ Disabled'}")
        
        if len(self.image_transformations) > 0:
            print(f"   🎨 Image Transformations: {len(self.image_transformations)}")
        
        # Monitoring configuration
        monitoring_features = []
        if self.logging_enabled:
            monitoring_features.append("Logging")
        if self.monitoring_enabled:
            monitoring_features.append("Monitoring")
        if len(self.notifications) > 0:
            monitoring_features.append(f"{len(self.notifications)} Notifications")
        
        if monitoring_features:
            print(f"\\n📊 Monitoring: {', '.join(monitoring_features)}")
        
        # Labels
        if self.storage_labels:
            print(f"\\n🏷️  Labels ({len(self.storage_labels)}):")
            for key, value in list(self.storage_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.storage_labels) > 5:
                print(f"   • ... and {len(self.storage_labels) - 5} more")
        
        # Production readiness
        production_ready = self.is_production_ready()
        print(f"\\n🚀 Production Readiness: {'✅ Ready' if production_ready else '⚠️  Needs optimization'}")
        if not production_ready:
            issues = []
            if not self.has_security_rules():
                issues.append("No security rules")
            if not self.has_monitoring_enabled():
                issues.append("No monitoring")
            if self.public_access:
                issues.append("Public access enabled")
            if self.cors_enabled and self.cors_origins == ["*"]:
                issues.append("CORS allows all origins")
            
            for issue in issues[:3]:
                print(f"   ⚠️  {issue}")
        
        # Cost
        cost = self._estimate_firebase_storage_cost()
        if cost > 0:
            print(f"\\n💰 Estimated Cost: ${cost:.2f}/month")
        else:
            print(f"\\n💰 Cost: Free tier")
        
        # Console link
        if self.firebase_project_id:
            print(f"\\n🌐 Firebase Console:")
            print(f"   🔗 https://console.firebase.google.com/project/{self.firebase_project_id}/storage/")
    
    def analyze_security(self) -> Dict[str, Any]:
        """
        Analyze Firebase Storage security configuration and provide recommendations.
        
        Returns:
            Dict containing security analysis and recommendations
        """
        analysis = {
            "security_score": 0,
            "max_score": 100,
            "recommendations": [],
            "security_features": [],
            "vulnerabilities": []
        }
        
        # Security rules analysis
        if self.has_security_rules():
            analysis["security_score"] += 30
            analysis["security_features"].append("Security rules configured")
        else:
            analysis["vulnerabilities"].append("No custom security rules")
            analysis["recommendations"].append("Configure Firebase Security Rules")
        
        # Access control analysis
        if not self.public_access:
            analysis["security_score"] += 20
            analysis["security_features"].append("Private access")
        else:
            analysis["vulnerabilities"].append("Public access enabled")
            analysis["recommendations"].append("Disable public access unless required")
        
        # Authentication analysis
        if self.authenticated_read and not self.public_read:
            analysis["security_score"] += 15
            analysis["security_features"].append("Authentication required")
        
        # Uniform bucket-level access
        if self.uniform_bucket_level_access:
            analysis["security_score"] += 10
            analysis["security_features"].append("Uniform bucket-level access")
        
        # CORS analysis
        if self.cors_enabled:
            if self.cors_origins == ["*"]:
                analysis["vulnerabilities"].append("CORS allows all origins")
                analysis["recommendations"].append("Restrict CORS origins")
            else:
                analysis["security_score"] += 10
                analysis["security_features"].append("CORS properly configured")
        else:
            analysis["security_score"] += 5
            analysis["security_features"].append("CORS disabled")
        
        # Versioning for recovery
        if self.versioning_enabled:
            analysis["security_score"] += 10
            analysis["security_features"].append("Versioning enabled")
        
        # Monitoring for security insights
        if self.has_monitoring_enabled():
            analysis["security_score"] += 5
            analysis["security_features"].append("Monitoring enabled")
        
        return analysis
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze Firebase Storage performance configuration and provide recommendations.
        
        Returns:
            Dict containing performance analysis and recommendations
        """
        analysis = {
            "performance_score": 0,
            "max_score": 100,
            "recommendations": [],
            "performance_features": [],
            "bottlenecks": []
        }
        
        # CDN analysis
        if self.cdn_enabled:
            analysis["performance_score"] += 25
            analysis["performance_features"].append("CDN enabled")
        else:
            analysis["bottlenecks"].append("CDN disabled")
            analysis["recommendations"].append("Enable CDN for faster global access")
        
        # Compression analysis
        if self.compression_enabled:
            analysis["performance_score"] += 20
            analysis["performance_features"].append("Compression enabled")
        else:
            analysis["bottlenecks"].append("Compression disabled")
            analysis["recommendations"].append("Enable compression for faster uploads")
        
        # Caching analysis
        if self.has_caching_configured():
            analysis["performance_score"] += 20
            analysis["performance_features"].append("Caching rules configured")
        else:
            analysis["bottlenecks"].append("No caching rules")
            analysis["recommendations"].append("Configure caching for better performance")
        
        # Storage class analysis
        if self.storage_class == "STANDARD":
            analysis["performance_score"] += 15
            analysis["performance_features"].append("Standard storage class")
        else:
            analysis["bottlenecks"].append(f"Non-standard storage class: {self.storage_class}")
            analysis["recommendations"].append("Consider STANDARD storage for better performance")
        
        # Image optimization analysis
        if self.thumbnail_generation:
            analysis["performance_score"] += 10
            analysis["performance_features"].append("Thumbnail generation")
        
        if len(self.image_transformations) > 0:
            analysis["performance_score"] += 10
            analysis["performance_features"].append("Image transformations")
        
        return analysis
    
    # Utility methods for backwards compatibility
    def get_status(self) -> Dict[str, Any]:
        """Get storage status for backwards compatibility"""
        return {
            "storage_name": self.storage_name,
            "bucket_name": self.get_bucket_name(),
            "firebase_project_id": self.firebase_project_id,
            "storage_type": self._get_storage_type_from_config(),
            "location": self.location,
            "storage_class": self.storage_class,
            "public_access": self.public_access,
            "has_security_rules": self.has_security_rules(),
            "cors_enabled": self.cors_enabled,
            "lifecycle_rule_count": len(self.lifecycle_rules),
            "versioning_enabled": self.versioning_enabled,
            "cdn_enabled": self.cdn_enabled,
            "has_caching_configured": self.has_caching_configured(),
            "has_monitoring_enabled": self.has_monitoring_enabled(),
            "is_production_ready": self.is_production_ready(),
            "estimated_cost": f"${self._estimate_firebase_storage_cost():.2f}/month"
        }


# Convenience function for creating Firebase Storage instances
def create_firebase_storage(name: str) -> FirebaseStorage:
    """
    Create a new Firebase Storage instance.
    
    Args:
        name: Storage name
        
    Returns:
        FirebaseStorage instance
    """
    return FirebaseStorage(name)


# Export the class for easy importing
__all__ = ['FirebaseStorage', 'create_firebase_storage']
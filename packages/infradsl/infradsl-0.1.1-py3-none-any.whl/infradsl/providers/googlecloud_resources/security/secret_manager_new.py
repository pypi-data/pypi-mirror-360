"""
GCP Secret Manager Complete Implementation

Complete Secret Manager implementation combining core functionality, 
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .secret_manager_core import SecretManagerCore
from .secret_manager_configuration import SecretManagerConfigurationMixin
from .secret_manager_lifecycle import SecretManagerLifecycleMixin


class SecretManager(SecretManagerCore, SecretManagerConfigurationMixin, SecretManagerLifecycleMixin):
    """
    Complete Google Cloud Secret Manager implementation.
    
    This class combines:
    - SecretManagerCore: Basic secret attributes and authentication
    - SecretManagerConfigurationMixin: Chainable configuration methods
    - SecretManagerLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Common credential patterns (database, API keys, OAuth, etc.)
    - Automatic versioning and rotation
    - IAM access control integration
    - Multi-region replication support
    - Cost estimation and compliance patterns
    
    Example:
        # Database credentials with rotation
        secret = SecretManager("db-credentials")
        secret.postgresql_database("localhost", "user", "pass", "mydb")
        secret.production().quarterly_rotation()
        secret.create()
        
        # API key with multi-region replication
        secret = SecretManager("stripe-key")
        secret.stripe_keys("pk_test_123", "sk_test_456", "whsec_789")
        secret.multi_region(["us-central1", "europe-west1"])
        secret.create()
        
        # Cross-Cloud Magic optimization
        secret = SecretManager("compliance-secret")
        secret.oauth_credentials("client123", "secret456")
        secret.optimize_for("compliance")
        secret.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Secret Manager with secret name.
        
        Args:
            name: Secret name (must be valid GCP secret name)
        """
        # Initialize all parent classes
        SecretManagerCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Secret Manager instance"""
        status = "configured" if self.has_value() else "unconfigured"
        replication = f"{self.replication_policy}"
        if self.replication_policy == "user_managed" and self.replica_locations:
            replication += f" ({len(self.replica_locations)} regions)"
        
        rotation = "enabled" if self.rotation_enabled else "disabled"
        
        return (f"SecretManager(name='{self.secret_name}', "
                f"type='{self.secret_type}', "
                f"status='{status}', "
                f"replication='{replication}', "
                f"rotation='{rotation}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Secret Manager configuration.
        
        Returns:
            Dict containing all configuration details
        """
        summary = {
            "secret_name": self.secret_name,
            "secret_type": self.secret_type,
            "description": self.secret_description,
            "has_value": self.has_value(),
            "value_type": self.get_value_type(),
            
            # Replication
            "replication": {
                "policy": self.replication_policy,
                "locations": self.replica_locations,
                "location_count": len(self.replica_locations) if self.replica_locations else 0
            },
            
            # Rotation
            "rotation": {
                "enabled": self.rotation_enabled,
                "period_seconds": self.rotation_period,
                "period_days": self.rotation_period // 86400 if self.rotation_period else None,
                "next_time": self.next_rotation_time,
                "topic": self.rotation_topic
            },
            
            # Security
            "security": {
                "kms_key": self.kms_key_name,
                "access_identities": self.allowed_access_identities,
                "access_count": len(self.allowed_access_identities)
            },
            
            # Version management
            "versions": {
                "max_versions": self.max_versions,
                "aliases": self.version_aliases,
                "destroy_ttl": self.version_destroy_ttl
            },
            
            # Metadata
            "labels": self.secret_labels,
            "annotations": self.secret_annotations,
            "label_count": len(self.secret_labels),
            
            # State
            "state": {
                "exists": self.secret_exists,
                "created": self.secret_created,
                "resource_name": self.secret_resource_name,
                "version_name": self.secret_version_name,
                "current_version": self.current_version,
                "total_versions": self.total_versions
            },
            
            # Cost
            "estimated_monthly_cost": self._calculate_secret_manager_cost()
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\n🔐 Secret Manager Configuration: {self.secret_name}")
        print(f"   🏷️  Type: {self.secret_type.replace('_', ' ').title()}")
        print(f"   📝 Description: {self.secret_description}")
        print(f"   💾 Has Value: {'✅ Yes' if self.has_value() else '❌ No'}")
        
        # Replication
        print(f"\n🌍 Replication:")
        print(f"   📋 Policy: {self.replication_policy.replace('_', ' ').title()}")
        if self.replication_policy == "user_managed" and self.replica_locations:
            print(f"   📍 Locations ({len(self.replica_locations)}):")
            for location in self.replica_locations:
                print(f"      • {location}")
        elif self.replication_policy == "automatic":
            print(f"   📍 Locations: Global (automatic)")
        
        # Rotation
        print(f"\n🔄 Rotation:")
        print(f"   📋 Status: {'✅ Enabled' if self.rotation_enabled else '❌ Disabled'}")
        if self.rotation_enabled and self.rotation_period:
            days = self.rotation_period // 86400
            print(f"   📅 Period: {days} days")
            if self.rotation_topic:
                print(f"   📢 Topic: {self.rotation_topic}")
        
        # Security
        if self.kms_key_name or self.allowed_access_identities:
            print(f"\n🔒 Security:")
            if self.kms_key_name:
                print(f"   🔐 Encryption: Customer-managed ({self.kms_key_name})")
            else:
                print(f"   🔐 Encryption: Google-managed")
            
            if self.allowed_access_identities:
                print(f"   👥 Access Identities ({len(self.allowed_access_identities)}):")
                for identity in self.allowed_access_identities[:3]:
                    print(f"      • {identity}")
                if len(self.allowed_access_identities) > 3:
                    print(f"      • ... and {len(self.allowed_access_identities) - 3} more")
        
        # Version management
        if self.max_versions or self.version_aliases or self.version_destroy_ttl:
            print(f"\n📦 Version Management:")
            if self.max_versions:
                print(f"   🔢 Max Versions: {self.max_versions}")
            if self.version_aliases:
                print(f"   🏷️  Aliases: {', '.join(self.version_aliases.keys())}")
            if self.version_destroy_ttl:
                print(f"   ⏰ Destroy TTL: {self.version_destroy_ttl}")
        
        # Labels
        if self.secret_labels:
            print(f"\n🏷️  Labels ({len(self.secret_labels)}):")
            for key, value in list(self.secret_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.secret_labels) > 5:
                print(f"   • ... and {len(self.secret_labels) - 5} more")
        
        # Cost
        print(f"\n💰 Estimated Cost: {self._calculate_secret_manager_cost()}")
        
        # State
        if self.secret_exists:
            print(f"\n📊 State:")
            print(f"   ✅ Exists: {self.secret_exists}")
            print(f"   🆔 Resource: {self.secret_resource_name}")
            if self.current_version:
                print(f"   📦 Current Version: {self.current_version}")
    
    def analyze_security(self) -> Dict[str, Any]:
        """
        Analyze security configuration and provide recommendations.
        
        Returns:
            Dict containing security analysis and recommendations
        """
        analysis = {
            "security_score": 0,
            "max_score": 100,
            "recommendations": [],
            "compliance": {
                "encryption": False,
                "access_control": False,
                "rotation": False,
                "versioning": False,
                "audit": False
            },
            "risk_factors": []
        }
        
        # Encryption analysis
        if self.kms_key_name:
            analysis["security_score"] += 20
            analysis["compliance"]["encryption"] = True
        else:
            analysis["recommendations"].append("Consider using customer-managed encryption keys for enhanced security")
        
        # Access control analysis
        if self.allowed_access_identities:
            analysis["security_score"] += 20
            analysis["compliance"]["access_control"] = True
        else:
            analysis["recommendations"].append("Configure specific access identities instead of relying on project-level permissions")
            analysis["risk_factors"].append("No explicit access control configured")
        
        # Rotation analysis
        if self.rotation_enabled:
            analysis["security_score"] += 20
            analysis["compliance"]["rotation"] = True
            
            if self.rotation_period and self.rotation_period <= 30 * 86400:  # 30 days
                analysis["security_score"] += 10
            elif self.rotation_period and self.rotation_period > 365 * 86400:  # 1 year
                analysis["recommendations"].append("Consider shorter rotation period for better security")
        else:
            analysis["recommendations"].append("Enable automatic rotation for better security posture")
            analysis["risk_factors"].append("No automatic rotation configured")
        
        # Version management analysis
        if self.max_versions and self.max_versions > 1:
            analysis["security_score"] += 10
            analysis["compliance"]["versioning"] = True
        else:
            analysis["recommendations"].append("Configure version limits for better secret lifecycle management")
        
        # Audit analysis (based on labels and configuration)
        if "audit" in self.secret_labels or "compliance" in self.secret_labels:
            analysis["security_score"] += 10
            analysis["compliance"]["audit"] = True
        else:
            analysis["recommendations"].append("Add audit and compliance labels for better governance")
        
        # Replication analysis
        if self.replication_policy == "user_managed":
            analysis["security_score"] += 10
        
        # Secret type specific recommendations
        if self.secret_type == "database":
            if not self.rotation_enabled:
                analysis["risk_factors"].append("Database credentials without rotation pose security risk")
        elif self.secret_type == "api_key":
            if not self.rotation_enabled:
                analysis["risk_factors"].append("API keys should be rotated regularly")
        
        # Environment specific recommendations
        env_label = self.secret_labels.get("environment", "").lower()
        if env_label == "production":
            if not self.rotation_enabled:
                analysis["risk_factors"].append("Production secrets should have rotation enabled")
            if not self.kms_key_name:
                analysis["recommendations"].append("Production secrets should use customer-managed encryption")
        
        return analysis
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze performance configuration and provide recommendations.
        
        Returns:
            Dict containing performance analysis and recommendations
        """
        analysis = {
            "performance_score": 0,
            "max_score": 100,
            "recommendations": [],
            "latency_factors": [],
            "cost_factors": []
        }
        
        # Replication analysis
        if self.replication_policy == "automatic":
            analysis["performance_score"] += 40
        elif self.replication_policy == "user_managed":
            if len(self.replica_locations) >= 3:
                analysis["performance_score"] += 35
            elif len(self.replica_locations) == 2:
                analysis["performance_score"] += 25
            else:
                analysis["performance_score"] += 15
                analysis["recommendations"].append("Consider multiple regions for better availability")
        
        # Version management impact
        if self.max_versions:
            if self.max_versions <= 5:
                analysis["performance_score"] += 20
            elif self.max_versions <= 10:
                analysis["performance_score"] += 15
            else:
                analysis["performance_score"] += 10
                analysis["cost_factors"].append(f"High version limit ({self.max_versions}) increases storage costs")
        
        # Access pattern optimization
        if self.version_aliases:
            analysis["performance_score"] += 15
        else:
            analysis["recommendations"].append("Use version aliases for better access pattern optimization")
        
        # Regional considerations
        if self.replication_policy == "user_managed" and self.replica_locations:
            unique_regions = set(location.split('-')[0] for location in self.replica_locations)
            if len(unique_regions) > 1:
                analysis["performance_score"] += 15
            
            # Check for common high-performance regions
            high_perf_regions = ["us-central1", "us-east1", "europe-west1"]
            if any(region in self.replica_locations for region in high_perf_regions):
                analysis["performance_score"] += 10
        
        # Rotation impact
        if self.rotation_enabled and self.rotation_period:
            if self.rotation_period <= 7 * 86400:  # Weekly
                analysis["latency_factors"].append("Very frequent rotation may impact performance")
            elif self.rotation_period >= 365 * 86400:  # Yearly
                analysis["recommendations"].append("Consider more frequent rotation for better security-performance balance")
        
        return analysis
    
    # Utility methods for backwards compatibility with existing SecretManager class
    def update_secret(self, new_value: Union[str, dict, bytes]) -> Dict[str, Any]:
        """Add a new version with updated value - backwards compatibility"""
        return self.add_version(new_value)
    
    def _get_secret_type(self) -> str:
        """Get secret type for backwards compatibility"""
        return self.secret_type
    
    def _estimate_monthly_cost(self) -> str:
        """Get estimated monthly cost for backwards compatibility"""
        return f"${self._estimate_secret_manager_cost():.3f}/month"


# Convenience function for creating Secret Manager instances
def create_secret_manager(name: str) -> SecretManager:
    """
    Create a new Secret Manager instance.
    
    Args:
        name: Secret name
        
    Returns:
        SecretManager instance
    """
    return SecretManager(name)


# Export the class for easy importing
__all__ = ['SecretManager', 'create_secret_manager']
"""
DigitalOcean Database Complete Implementation

Complete DigitalOcean Managed Database implementation combining core functionality, 
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .database_core import DatabaseCore
from .database_configuration import DatabaseConfigurationMixin
from .database_lifecycle import DatabaseLifecycleMixin


class Database(DatabaseCore, DatabaseConfigurationMixin, DatabaseLifecycleMixin):
    """
    Complete DigitalOcean Managed Database implementation.
    
    This class combines:
    - DatabaseCore: Basic database attributes and authentication
    - DatabaseConfigurationMixin: Chainable configuration methods
    - DatabaseLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent database configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Complete managed database support (PostgreSQL, MySQL, Redis)
    - High availability with multi-node clusters
    - Security features (private networks, firewall rules, backups)
    - Performance optimization (sizing, storage, caching)
    - Common database patterns (web app, cache, analytics, session store)
    - Environment-specific configurations (development, staging, production)
    
    Example:
        # Simple PostgreSQL database
        db = Database("my-app-db")
        db.postgresql().development()
        db.create()
        
        # Production database with high availability
        db = Database("prod-db")
        db.postgresql().production().private_network("vpc-uuid")
        db.create()
        
        # Redis cache
        cache = Database("app-cache")
        cache.redis().cache_database().region("nyc3")
        cache.create()
        
        # MySQL database with custom configuration
        db = Database("mysql-db")
        db.mysql().size("db-s-4vcpu-8gb").nodes(2)
        db.backup_enabled(True).monitoring(True)
        db.create()
        
        # Analytics database
        analytics = Database("analytics-db")
        analytics.postgresql().analytics_database()
        analytics.size("db-s-8vcpu-32gb").storage(500)
        analytics.create()
        
        # Session store
        sessions = Database("session-store")
        sessions.redis().session_store()
        sessions.private_network("vpc-uuid")
        sessions.create()
        
        # Custom configuration
        db = Database("custom-db")
        db.postgresql("13").region("sfo3").size("db-s-2vcpu-4gb")
        db.nodes(2).backup_hour(3).point_in_time_recovery(True)
        db.maintenance_window("sunday", "02:00")
        db.monitoring(True).alerts(True)
        db.trusted_sources(["10.0.0.0/8", "192.168.1.0/24"])
        db.label("environment", "staging").tag("web-app")
        db.create()
        
        # Cross-Cloud Magic optimization
        db = Database("optimized-db")
        db.postgresql().web_app_database()
        db.optimize_for("cost")  # Will suggest best size/region for cost
        db.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize DigitalOcean Database with database name.
        
        Args:
            name: Database name
        """
        # Initialize all parent classes
        DatabaseCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Database instance"""
        database_type = self._get_database_type_from_config()
        engine_names = {"pg": "PostgreSQL", "mysql": "MySQL", "redis": "Redis"}
        engine_display = engine_names.get(self.engine, self.engine)
        ha_info = f"{self.num_nodes} nodes" if self.num_nodes > 1 else "single node"
        status = "configured" if self.database_name else "unconfigured"
        
        return (f"Database(name='{self.database_name}', "
                f"engine='{engine_display}', "
                f"type='{database_type}', "
                f"size='{self.size}', "
                f"ha='{ha_info}', "
                f"region='{self.region}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Database configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze database configuration
        database_features = []
        if self.num_nodes > 1:
            database_features.append("high_availability")
        if self.backup_enabled:
            database_features.append("backup")
        if self.point_in_time_recovery:
            database_features.append("point_in_time_recovery")
        if self.private_network_uuid:
            database_features.append("private_network")
        if self.monitoring_enabled:
            database_features.append("monitoring")
        if self.alerts_enabled:
            database_features.append("alerts")
        
        # Categorize by database purpose
        database_categories = []
        database_type = self._get_database_type_from_config()
        if "cache" in database_type:
            database_categories.append("cache")
        elif "analytics" in database_type:
            database_categories.append("analytics")
        elif "session" in database_type:
            database_categories.append("session_store")
        elif "web" in database_type or "microservice" in database_type:
            database_categories.append("application_database")
        elif "enterprise" in database_type:
            database_categories.append("enterprise")
        
        # Security analysis
        security_features = []
        if self.private_network_uuid:
            security_features.append("private_network")
        if len(self.trusted_sources) > 0:
            security_features.append("trusted_sources")
        if len(self.firewall_rules) > 0:
            security_features.append("firewall_rules")
        if self.backup_enabled:
            security_features.append("backup")
        
        # Parse size information
        size_info = self._parse_size_string(self.size)
        
        summary = {
            "database_name": self.database_name,
            "database_description": self.database_description,
            "database_type": database_type,
            "database_categories": database_categories,
            
            # Engine configuration
            "engine": self.engine,
            "engine_display": {"pg": "PostgreSQL", "mysql": "MySQL", "redis": "Redis"}.get(self.engine, self.engine),
            "version": self.version or "latest",
            
            # Instance configuration
            "size": self.size,
            "vcpus": size_info["vcpus"],
            "memory_gb": size_info["memory_gb"],
            "num_nodes": self.num_nodes,
            "region": self.region,
            "storage_size_gb": self.storage_size_mib // 1024 if self.storage_size_mib else None,
            
            # High availability
            "is_highly_available": self.num_nodes > 1,
            "cluster_size": self.num_nodes,
            
            # Network configuration
            "network": {
                "private_network": self.private_network_uuid is not None,
                "private_network_uuid": self.private_network_uuid,
                "trusted_sources_count": len(self.trusted_sources),
                "trusted_sources": self.trusted_sources,
                "firewall_rules_count": len(self.firewall_rules),
                "firewall_rules": self.firewall_rules
            },
            
            # Security configuration
            "security_features": security_features,
            "has_private_network": self.private_network_uuid is not None,
            "has_firewall_rules": len(self.firewall_rules) > 0,
            "has_trusted_sources": len(self.trusted_sources) > 0,
            
            # Backup configuration
            "backup": {
                "enabled": self.backup_enabled,
                "hour": self.backup_hour,
                "point_in_time_recovery": self.point_in_time_recovery
            },
            
            # Monitoring configuration
            "monitoring": {
                "enabled": self.monitoring_enabled,
                "alerts": self.alerts_enabled,
                "alert_policies": self.alert_policy
            },
            
            # Maintenance configuration
            "maintenance": self.maintenance_window,
            
            # Engine-specific configuration
            "engine_config": {},
            
            # Features analysis
            "database_features": database_features,
            "has_high_availability": self.num_nodes > 1,
            "has_backup": self.backup_enabled,
            "has_monitoring": self.monitoring_enabled,
            "is_production_ready": self._is_production_ready(),
            
            # Labels and metadata
            "tags": self.database_tags,
            "tag_count": len(self.database_tags),
            "labels": self.database_labels,
            "annotations": self.database_annotations,
            
            # State
            "state": {
                "exists": self.database_exists,
                "created": self.database_created,
                "status": self.database_status,
                "connection_info": self.connection_info
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_database_cost():.2f}",
            "cost_breakdown": self._get_cost_breakdown()
        }
        
        # Add engine-specific config
        if self.engine == "redis":
            summary["engine_config"] = {
                "eviction_policy": self.eviction_policy,
                "redis_config": self.redis_config
            }
        elif self.engine == "mysql":
            summary["engine_config"] = {
                "sql_mode": self.sql_mode,
                "mysql_config": self.mysql_config
            }
        elif self.engine == "pg":
            summary["engine_config"] = {
                "postgres_config": self.postgres_config
            }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        engine_names = {"pg": "PostgreSQL", "mysql": "MySQL", "redis": "Redis"}
        engine_display = engine_names.get(self.engine, self.engine)
        
        print(f"\\n🗄️  DigitalOcean Database Configuration: {self.database_name}")
        print(f"   📝 Description: {self.database_description}")
        print(f"   🎯 Database Type: {self._get_database_type_from_config().replace('_', ' ').title()}")
        
        # Engine configuration
        print(f"\\n🔧 Engine Configuration:")
        print(f"   📊 Engine: {engine_display}")
        if self.version:
            print(f"   🔖 Version: {self.version}")
        else:
            print(f"   🔖 Version: Latest")
        
        # Instance configuration
        size_info = self._parse_size_string(self.size)
        print(f"\\n💻 Instance Configuration:")
        print(f"   💾 Size: {self.size}")
        print(f"   ⚡ vCPUs: {size_info['vcpus']}")
        print(f"   🧠 Memory: {size_info['memory_gb']} GB")
        print(f"   🔢 Nodes: {self.num_nodes}")
        print(f"   📍 Region: {self.region}")
        
        if self.storage_size_mib:
            storage_gb = self.storage_size_mib // 1024
            print(f"   💽 Custom Storage: {storage_gb} GB")
        
        # High availability
        if self.num_nodes > 1:
            print(f"\\n🔄 High Availability:")
            print(f"   ✅ Enabled ({self.num_nodes} nodes)")
            print(f"   🛡️  Automatic failover")
        else:
            print(f"\\n🔄 High Availability: ❌ Disabled (single node)")
        
        # Network configuration
        print(f"\\n🌐 Network Configuration:")
        if self.private_network_uuid:
            print(f"   🔒 Private Network: {self.private_network_uuid}")
        else:
            print(f"   🌍 Network: Public")
        
        if self.trusted_sources:
            print(f"   🛡️  Trusted Sources ({len(self.trusted_sources)}):")
            for source in self.trusted_sources[:3]:
                print(f"      • {source}")
            if len(self.trusted_sources) > 3:
                print(f"      • ... and {len(self.trusted_sources) - 3} more")
        
        if self.firewall_rules:
            print(f"   🔥 Firewall Rules: {len(self.firewall_rules)}")
        
        # Backup configuration
        print(f"\\n💾 Backup Configuration:")
        print(f"   📦 Automatic Backup: {'✅ Enabled' if self.backup_enabled else '❌ Disabled'}")
        if self.backup_enabled:
            print(f"      ⏰ Daily at: {self.backup_hour:02d}:00 UTC")
        print(f"   🕐 Point-in-Time Recovery: {'✅ Enabled' if self.point_in_time_recovery else '❌ Disabled'}")
        
        # Monitoring configuration
        print(f"\\n📊 Monitoring Configuration:")
        print(f"   📈 Monitoring: {'✅ Enabled' if self.monitoring_enabled else '❌ Disabled'}")
        print(f"   🚨 Alerts: {'✅ Enabled' if self.alerts_enabled else '❌ Disabled'}")
        
        if self.alert_policy:
            print(f"   📋 Alert Policies:")
            for metric, policy in self.alert_policy.items():
                print(f"      • {metric}: {policy['comparison']} {policy['threshold']}")
        
        # Maintenance window
        print(f"\\n🔧 Maintenance:")
        day = self.maintenance_window["day"].title()
        hour = self.maintenance_window["hour"]
        print(f"   🗓️  Window: {day} at {hour} UTC")
        
        # Engine-specific configuration
        if self.engine == "redis" and self.eviction_policy:
            print(f"\\n🗄️  Redis Configuration:")
            print(f"   🔄 Eviction Policy: {self.eviction_policy}")
        
        if self.engine == "mysql" and self.sql_mode:
            print(f"\\n🗄️  MySQL Configuration:")
            print(f"   ⚙️  SQL Mode: {self.sql_mode}")
        
        # Tags and labels
        if self.database_tags:
            print(f"\\n🏷️  Tags ({len(self.database_tags)}):")
            for tag in self.database_tags[:5]:
                print(f"   • {tag}")
            if len(self.database_tags) > 5:
                print(f"   • ... and {len(self.database_tags) - 5} more")
        
        if self.database_labels:
            print(f"\\n📋 Labels ({len(self.database_labels)}):")
            for key, value in list(self.database_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.database_labels) > 5:
                print(f"   • ... and {len(self.database_labels) - 5} more")
        
        # Production readiness
        production_ready = self._is_production_ready()
        print(f"\\n🚀 Production Readiness: {'✅ Ready' if production_ready else '⚠️  Needs attention'}")
        if not production_ready:
            issues = self._get_production_issues()
            for issue in issues[:3]:
                print(f"   ⚠️  {issue}")
        
        # Cost
        cost = self._estimate_database_cost()
        print(f"\\n💰 Estimated Cost: ${cost:.2f}/month")
        
        # Console link
        print(f"\\n🌐 DigitalOcean Console:")
        print(f"   🔗 https://cloud.digitalocean.com/databases/")
    
    def _is_production_ready(self) -> bool:
        """Check if database is production ready"""
        issues = self._get_production_issues()
        return len(issues) == 0
    
    def _get_production_issues(self) -> List[str]:
        """Get list of production readiness issues"""
        issues = []
        
        if not self.backup_enabled:
            issues.append("Backup not enabled")
        
        if not self.monitoring_enabled:
            issues.append("Monitoring not enabled")
        
        if self.num_nodes == 1 and "production" in self.database_tags:
            issues.append("Single node for production database")
        
        if not self.private_network_uuid and "production" in self.database_tags:
            issues.append("Not in private network")
        
        if len(self.trusted_sources) == 0 and not self.private_network_uuid:
            issues.append("No trusted sources configured")
        
        return issues
    
    # Utility methods for backwards compatibility
    def get_status(self) -> Dict[str, Any]:
        """Get database status for backwards compatibility"""
        return {
            "database_name": self.database_name,
            "engine": self.engine,
            "version": self.version,
            "size": self.size,
            "region": self.region,
            "num_nodes": self.num_nodes,
            "database_type": self._get_database_type_from_config(),
            "has_high_availability": self.num_nodes > 1,
            "has_backup": self.backup_enabled,
            "has_monitoring": self.monitoring_enabled,
            "has_private_network": self.private_network_uuid is not None,
            "is_production_ready": self._is_production_ready(),
            "estimated_cost": f"${self._estimate_database_cost():.2f}/month"
        }


# Convenience function for creating Database instances
def create_database(name: str) -> Database:
    """
    Create a new Database instance.
    
    Args:
        name: Database name
        
    Returns:
        Database instance
    """
    return Database(name)


# Export the class for easy importing
__all__ = ['Database', 'create_database']
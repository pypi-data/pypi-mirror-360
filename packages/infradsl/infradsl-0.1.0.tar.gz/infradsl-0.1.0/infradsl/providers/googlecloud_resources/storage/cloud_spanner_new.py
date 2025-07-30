"""
Google Cloud Spanner Complete Implementation

Complete Google Cloud Spanner implementation combining core functionality,
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .cloud_spanner_core import CloudSpannerCore
from .cloud_spanner_configuration import CloudSpannerConfigurationMixin
from .cloud_spanner_lifecycle import CloudSpannerLifecycleMixin


class CloudSpanner(CloudSpannerCore, CloudSpannerConfigurationMixin, CloudSpannerLifecycleMixin):
    """
    Complete Google Cloud Spanner implementation.
    
    This class combines:
    - CloudSpannerCore: Basic Spanner attributes and authentication
    - CloudSpannerConfigurationMixin: Chainable configuration methods
    - CloudSpannerLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent Spanner configuration
    - Smart state management and cost optimization
    - Cross-Cloud Magic optimization
    - Globally distributed, horizontally scalable database
    - Multi-region and regional configurations
    - ACID transactions with external consistency
    - SQL interface with strong consistency
    - Automatic scaling and high availability
    - Enterprise-grade security and encryption
    - Backup and point-in-time recovery
    
    Example:
        # Development instance
        dev_db = CloudSpanner("dev-database")
        dev_db.project("my-project").development_instance()
        dev_db.database("app_db")
        dev_db.create()
        
        # Production multi-region instance
        prod_db = CloudSpanner("prod-database")
        prod_db.project("my-project").production_instance()
        prod_db.multi_region_us().large_instance()
        prod_db.database("main_db").database("analytics_db")
        prod_db.create()
        
        # High-performance instance
        perf_db = CloudSpanner("performance-db")
        perf_db.project("my-project").enterprise_instance()
        perf_db.global_instance().monitoring()
        perf_db.transactional_database("transactions")
        perf_db.create()
        
        # Cost-optimized instance
        cost_db = CloudSpanner("cost-optimized")
        cost_db.project("my-project").cost_optimized_instance()
        cost_db.processing_units(100).regional()
        cost_db.database("small_db")
        cost_db.create()
        
        # Microservices databases
        micro_db = CloudSpanner("microservices-db")
        micro_db.project("my-project").medium_instance()
        micro_db.microservices_databases(["user", "order", "payment"])
        micro_db.create()
        
        # Analytical workload
        analytics_db = CloudSpanner("analytics")
        analytics_db.project("my-project").large_instance()
        analytics_db.analytical_database("data_warehouse")
        analytics_db.query_insights().monitoring()
        analytics_db.create()
        
        # Cross-Cloud Magic optimization
        optimized_db = CloudSpanner("optimized-database")
        optimized_db.project("my-project").medium_instance()
        optimized_db.optimize_for("performance")
        optimized_db.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Google Cloud Spanner with instance name.
        
        Args:
            name: Spanner instance name
        """
        # Initialize all parent classes
        CloudSpannerCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Cloud Spanner instance"""
        spanner_type = self._get_spanner_type_from_config()
        capacity = f"{self.node_count} nodes" if self.node_count else f"{self.processing_units} units"
        status = "configured" if self.project_id else "unconfigured"
        
        return (f"CloudSpanner(name='{self.instance_name}', "
                f"type='{spanner_type}', "
                f"config='{self.instance_config}', "
                f"capacity='{capacity}', "
                f"databases={len(self.databases)}, "
                f"project='{self.project_id}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Cloud Spanner configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze Spanner configuration
        spanner_features = []
        if self.multi_region:
            spanner_features.append("multi_region")
        if self.backup_enabled:
            spanner_features.append("backup_enabled")
        if self.point_in_time_recovery:
            spanner_features.append("point_in_time_recovery")
        if self.monitoring_enabled:
            spanner_features.append("monitoring")
        if self.query_insights:
            spanner_features.append("query_insights")
        if self.deletion_protection:
            spanner_features.append("deletion_protection")
        if self.customer_managed_encryption:
            spanner_features.append("customer_managed_encryption")
            
        # Analyze databases
        database_info = {
            "databases": [db["database_id"] for db in self.databases],
            "database_count": len(self.databases),
            "default_database": self.default_database
        }
        
        # Compute capacity analysis
        capacity_info = self.get_compute_capacity()
        capacity_info.update({
            "estimated_qps": self.get_estimated_qps(),
            "multi_region": self.is_multi_region()
        })
        
        summary = {
            "instance_name": self.instance_name,
            "instance_id": self.instance_id or self.instance_name,
            "project_id": self.project_id,
            "display_name": self.display_name,
            "instance_description": self.instance_description,
            "spanner_type": self._get_spanner_type_from_config(),
            
            # Instance configuration
            "instance_config": self.instance_config,
            "capacity": capacity_info,
            
            # Database configuration
            "databases": database_info,
            
            # Security configuration
            "security": {
                "deletion_protection": self.deletion_protection,
                "customer_managed_encryption": self.customer_managed_encryption,
                "encryption_config": self.encryption_config
            },
            
            # Backup configuration
            "backup": {
                "backup_enabled": self.backup_enabled,
                "backup_retention_period": self.backup_retention_period,
                "point_in_time_recovery": self.point_in_time_recovery
            },
            
            # Monitoring configuration
            "monitoring": {
                "monitoring_enabled": self.monitoring_enabled,
                "alerting_enabled": self.alerting_enabled,
                "query_insights": self.query_insights
            },
            
            # Features analysis
            "spanner_features": spanner_features,
            "is_multi_region": self.is_multi_region(),
            "is_production_ready": self.is_production_ready(),
            
            # Labels and metadata
            "labels": self.spanner_labels,
            "label_count": len(self.spanner_labels),
            "annotations": self.spanner_annotations,
            
            # State
            "state": {
                "exists": self.instance_exists,
                "created": self.instance_created,
                "instance_state": self.instance_state,
                "deployment_status": self.deployment_status
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_spanner_cost():,.2f}",
            "cost_per_hour": f"${self._estimate_spanner_cost() / 730:.2f}"
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\\n🗄️  Google Cloud Spanner Configuration: {self.instance_name}")
        print(f"   📁 Project: {self.project_id}")
        print(f"   🆔 Instance ID: {self.instance_id or self.instance_name}")
        if self.display_name:
            print(f"   📝 Display Name: {self.display_name}")
        print(f"   📝 Description: {self.instance_description}")
        print(f"   🎯 Spanner Type: {self._get_spanner_type_from_config().replace('_', ' ').title()}")
        
        # Instance configuration
        print(f"\\n🌍 Instance Configuration:")
        print(f"   🌍 Config: {self.instance_config}")
        print(f"   🌐 Multi-Region: {'✅ Yes' if self.is_multi_region() else '❌ No'}")
        
        # Compute capacity
        print(f"\\n⚡ Compute Capacity:")
        if self.node_count:
            print(f"   🖥️  Nodes: {self.node_count}")
            print(f"   📊 Estimated QPS: {self.get_estimated_qps():,}")
        else:
            print(f"   ⚡ Processing Units: {self.processing_units}")
            print(f"   📊 Estimated QPS: {self.get_estimated_qps():,}")
            
        # Database configuration
        print(f"\\n🗄️  Database Configuration:")
        if self.databases:
            print(f"   🗄️  Databases ({len(self.databases)}):")
            for db in self.databases[:5]:
                db_id = db["database_id"]
                retention = db.get("version_retention_period", "1h")
                print(f"      • {db_id} (retention: {retention})")
                if db_id == self.default_database:
                    print(f"        └─ 🔵 Default database")
            if len(self.databases) > 5:
                print(f"      • ... and {len(self.databases) - 5} more")
                
            if self.default_database:
                print(f"   🔵 Default: {self.default_database}")
        else:
            print(f"   🗄️  Databases: None configured")
            
        # Security configuration
        print(f"\\n🔒 Security Configuration:")
        print(f"   🔒 Deletion Protection: {'✅ Enabled' if self.deletion_protection else '❌ Disabled'}")
        if self.customer_managed_encryption:
            print(f"   🔐 Encryption: 🔑 Customer-managed")
            if self.encryption_config:
                print(f"      └─ Key: {self.encryption_config.get('kms_key_name', 'Not specified')}")
        else:
            print(f"   🔐 Encryption: 🔒 Google-managed")
            
        # Backup configuration
        print(f"\\n💾 Backup Configuration:")
        print(f"   💾 Backup: {'✅ Enabled' if self.backup_enabled else '❌ Disabled'}")
        if self.backup_enabled:
            print(f"   ⏰ Retention: {self.backup_retention_period}")
        print(f"   🔄 Point-in-Time Recovery: {'✅ Enabled' if self.point_in_time_recovery else '❌ Disabled'}")
        
        # Monitoring configuration
        monitoring_features = []
        if self.monitoring_enabled:
            monitoring_features.append("Monitoring")
        if self.alerting_enabled:
            monitoring_features.append("Alerting")
        if self.query_insights:
            monitoring_features.append("Query Insights")
            
        if monitoring_features:
            print(f"\\n📊 Monitoring: {', '.join(monitoring_features)}")
        else:
            print(f"\\n📊 Monitoring: ❌ Disabled")
            
        # Labels
        if self.spanner_labels:
            print(f"\\n🏷️  Labels ({len(self.spanner_labels)}):")
            for key, value in list(self.spanner_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.spanner_labels) > 5:
                print(f"   • ... and {len(self.spanner_labels) - 5} more")
                
        # Production readiness
        production_ready = self.is_production_ready()
        print(f"\\n🚀 Production Readiness: {'✅ Ready' if production_ready else '⚠️  Needs optimization'}")
        if not production_ready:
            issues = []
            if self.node_count and self.node_count < 3:
                issues.append("Less than 3 nodes")
            if self.processing_units and self.processing_units < 300:
                issues.append("Less than 300 processing units")
            if not self.backup_enabled:
                issues.append("Backups disabled")
            if not self.monitoring_enabled:
                issues.append("Monitoring disabled")
            if not self.deletion_protection:
                issues.append("No deletion protection")
                
            for issue in issues[:3]:
                print(f"   ⚠️  {issue}")
                
        # Cost estimate
        cost = self._estimate_spanner_cost()
        print(f"\\n💰 Cost Estimate:")
        print(f"   💰 Monthly: ${cost:,.2f}")
        print(f"   ⏰ Hourly: ${cost / 730:.2f}")
        
        # Console and URLs
        if self.project_id:
            print(f"\\n🌐 Console:")
            print(f"   🔗 https://console.cloud.google.com/spanner/instances?project={self.project_id}")
            
        # Spanner capabilities
        print(f"\\n🗄️  Cloud Spanner Capabilities:")
        print(f"   ├─ 🌍 Global consistency and ACID transactions")
        print(f"   ├─ 📈 Horizontal scaling (up to 10,000+ nodes)")
        print(f"   ├─ 🔄 Automatic multi-region replication")
        print(f"   ├─ 📊 99.999% availability SLA")
        print(f"   ├─ 🚀 Low-latency reads and writes globally")
        print(f"   └─ 🛠️  SQL interface with ANSI SQL support")
    
    def get_status(self) -> Dict[str, Any]:
        """Get Spanner status for backwards compatibility"""
        return {
            "instance_name": self.instance_name,
            "instance_id": self.instance_id or self.instance_name,
            "project_id": self.project_id,
            "instance_config": self.instance_config,
            "node_count": self.node_count,
            "processing_units": self.processing_units,
            "multi_region": self.is_multi_region(),
            "database_count": len(self.databases),
            "databases": [db["database_id"] for db in self.databases],
            "backup_enabled": self.backup_enabled,
            "monitoring_enabled": self.monitoring_enabled,
            "deletion_protection": self.deletion_protection,
            "is_production_ready": self.is_production_ready(),
            "deployment_status": self.deployment_status,
            "estimated_cost": f"${self._estimate_spanner_cost():,.2f}/month",
            "estimated_qps": self.get_estimated_qps()
        }


# Convenience function for creating Cloud Spanner instances
def create_cloud_spanner(name: str) -> CloudSpanner:
    """
    Create a new Cloud Spanner instance.
    
    Args:
        name: Spanner instance name
        
    Returns:
        CloudSpanner instance
    """
    return CloudSpanner(name)


# Pattern-specific convenience functions
def create_development_spanner(name: str, project_id: str) -> CloudSpanner:
    """Create a development Spanner instance"""
    spanner = CloudSpanner(name)
    spanner.project(project_id).development_instance()
    return spanner


def create_production_spanner(name: str, project_id: str) -> CloudSpanner:
    """Create a production Spanner instance"""
    spanner = CloudSpanner(name)
    spanner.project(project_id).production_instance()
    return spanner


def create_global_spanner(name: str, project_id: str) -> CloudSpanner:
    """Create a global multi-region Spanner instance"""
    spanner = CloudSpanner(name)
    spanner.project(project_id).high_availability_instance()
    return spanner


def create_cost_optimized_spanner(name: str, project_id: str) -> CloudSpanner:
    """Create a cost-optimized Spanner instance"""
    spanner = CloudSpanner(name)
    spanner.project(project_id).cost_optimized_instance()
    return spanner


# Export the class for easy importing
__all__ = [
    'CloudSpanner',
    'create_cloud_spanner',
    'create_development_spanner',
    'create_production_spanner',
    'create_global_spanner',
    'create_cost_optimized_spanner'
]
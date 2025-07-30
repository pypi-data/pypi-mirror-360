"""
Google Cloud Spanner Configuration Mixin

Configuration methods for Google Cloud Spanner.
Provides Rails-like method chaining for fluent Spanner configuration.
"""

from typing import Dict, Any, List, Optional, Union


class CloudSpannerConfigurationMixin:
    """
    Mixin for Google Cloud Spanner configuration methods.
    
    This mixin provides:
    - Rails-like method chaining for fluent Spanner configuration
    - Instance and database configuration
    - Scaling and performance configuration
    - Multi-region and replication setup
    - Security and encryption configuration
    - Backup and recovery configuration
    """
    
    # Project and Instance Configuration
    def project(self, project_id: str):
        """Set Google Cloud project ID"""
        self.project_id = project_id
        return self
        
    def instance_id(self, instance_id: str):
        """Set Spanner instance ID"""
        self.instance_id = instance_id
        return self
        
    def display_name(self, display_name: str):
        """Set display name for the instance"""
        self.display_name = display_name
        return self
        
    def description(self, description: str):
        """Set instance description"""
        self.instance_description = description
        return self
    
    # Instance Configuration Methods
    def instance_config(self, config: str):
        """Set instance configuration"""
        if not self._validate_instance_config(config):
            raise ValueError(f"Invalid instance configuration: {config}")
        self.instance_config = config
        self.multi_region = "multi" in config or any(region in config for region in ["nam", "eur", "asia"])
        return self
        
    def regional(self, region: str = "us-central1"):
        """Configure as regional instance"""
        return self.instance_config(f"regional-{region}")
        
    def multi_region_us(self):
        """Configure as multi-region US"""
        return self.instance_config("nam3")
        
    def multi_region_europe(self):
        """Configure as multi-region Europe"""
        return self.instance_config("eur3")
        
    def multi_region_asia(self):
        """Configure as multi-region Asia"""
        return self.instance_config("asia1")
        
    def global_instance(self):
        """Configure as global multi-region instance"""
        return self.instance_config("nam-eur-asia1")
    
    # Scaling Configuration Methods
    def nodes(self, node_count: int):
        """Set number of nodes"""
        if not self._validate_node_count(node_count):
            raise ValueError(f"Invalid node count: {node_count}")
        self.node_count = node_count
        self.processing_units = None  # Clear processing units if using nodes
        return self
        
    def processing_units(self, units: int):
        """Set processing units (alternative to nodes)"""
        if not self._validate_processing_units(units):
            raise ValueError(f"Invalid processing units: {units}")
        self.processing_units = units
        self.node_count = None  # Clear node count if using processing units
        return self
        
    def small_instance(self):
        """Configure small instance (1 node or 100 processing units)"""
        return self.nodes(1)
        
    def medium_instance(self):
        """Configure medium instance (3 nodes)"""
        return self.nodes(3)
        
    def large_instance(self):
        """Configure large instance (5 nodes)"""
        return self.nodes(5)
        
    def enterprise_instance(self):
        """Configure enterprise instance (10 nodes)"""
        return self.nodes(10)
        
    def auto_scaling(self, min_units: int = 100, max_units: int = 1000):
        """Configure auto-scaling with processing units"""
        # Note: Auto-scaling requires processing units, not nodes
        self.processing_units(min_units)
        self.auto_scaling_enabled = True
        self.auto_scaling_min = min_units
        self.auto_scaling_max = max_units
        return self
    
    # Database Configuration Methods
    def database(self, database_id: str, **options):
        """Add a database to the instance"""
        database_config = {
            "database_id": database_id,
            "version_retention_period": options.get("retention_period", "1h"),
            "encryption_config": options.get("encryption_config"),
            "default_leader": options.get("default_leader")
        }
        self.databases.append(database_config)
        
        if self.default_database is None:
            self.default_database = database_id
            
        return self
        
    def default_database(self, database_id: str):
        """Set the default database"""
        # Add database if not already added
        if not any(db["database_id"] == database_id for db in self.databases):
            self.database(database_id)
        self.default_database = database_id
        return self
        
    def multiple_databases(self, database_ids: List[str]):
        """Add multiple databases"""
        for db_id in database_ids:
            self.database(db_id)
        return self
    
    # Security Configuration Methods
    def deletion_protection(self, enabled: bool = True):
        """Enable or disable deletion protection"""
        self.deletion_protection = enabled
        return self
        
    def customer_managed_encryption(self, key_name: str):
        """Enable customer-managed encryption"""
        self.customer_managed_encryption = True
        self.encryption_config = {
            "kms_key_name": key_name
        }
        return self
        
    def google_managed_encryption(self):
        """Use Google-managed encryption (default)"""
        self.customer_managed_encryption = False
        self.encryption_config = None
        return self
    
    # Backup Configuration Methods
    def backup_enabled(self, enabled: bool = True):
        """Enable or disable backups"""
        self.backup_enabled = enabled
        return self
        
    def backup_retention(self, retention_period: str = "7d"):
        """Set backup retention period"""
        self.backup_retention_period = retention_period
        return self
        
    def point_in_time_recovery(self, enabled: bool = True):
        """Enable point-in-time recovery"""
        self.point_in_time_recovery = enabled
        return self
    
    # Monitoring Configuration Methods
    def monitoring(self, enabled: bool = True):
        """Enable monitoring"""
        self.monitoring_enabled = enabled
        return self
        
    def alerting(self, enabled: bool = True):
        """Enable alerting"""
        self.alerting_enabled = enabled
        return self
        
    def query_insights(self, enabled: bool = True):
        """Enable query insights"""
        self.query_insights = enabled
        return self
    
    # High-Level Configuration Patterns
    def development_instance(self):
        """Configure for development environment"""
        self.spanner_labels["environment"] = "development"
        return (self
                .small_instance()
                .regional()
                .backup_retention("1d")
                .deletion_protection(False))
                
    def staging_instance(self):
        """Configure for staging environment"""
        self.spanner_labels["environment"] = "staging"
        return (self
                .medium_instance()
                .regional()
                .backup_retention("3d")
                .monitoring())
                
    def production_instance(self):
        """Configure for production environment"""
        self.spanner_labels["environment"] = "production"
        return (self
                .large_instance()
                .multi_region_us()
                .backup_retention("30d")
                .point_in_time_recovery()
                .monitoring()
                .alerting()
                .deletion_protection())
                
    def high_availability_instance(self):
        """Configure for high availability"""
        self.spanner_labels["availability"] = "high"
        return (self
                .enterprise_instance()
                .global_instance()
                .backup_retention("90d")
                .point_in_time_recovery()
                .monitoring()
                .alerting())
                
    def cost_optimized_instance(self):
        """Configure for cost optimization"""
        self.spanner_labels["optimization"] = "cost"
        return (self
                .processing_units(100)  # Minimum
                .regional()
                .backup_retention("1d")
                .deletion_protection(False))
                
    def performance_optimized_instance(self):
        """Configure for performance"""
        self.spanner_labels["optimization"] = "performance"
        return (self
                .enterprise_instance()
                .multi_region_us()
                .monitoring()
                .query_insights())
    
    # Database Pattern Methods
    def transactional_database(self, database_id: str = "main"):
        """Configure for OLTP workloads"""
        self.spanner_labels["workload"] = "transactional"
        return self.database(database_id, retention_period="1h")
        
    def analytical_database(self, database_id: str = "analytics"):
        """Configure for analytical workloads"""
        self.spanner_labels["workload"] = "analytical"
        return self.database(database_id, retention_period="24h")
        
    def microservices_databases(self, service_names: List[str]):
        """Configure databases for microservices"""
        self.spanner_labels["architecture"] = "microservices"
        for service in service_names:
            self.database(f"{service}_db")
        return self
        
    def multi_tenant_database(self, database_id: str = "multi_tenant"):
        """Configure for multi-tenant application"""
        self.spanner_labels["tenancy"] = "multi-tenant"
        return self.database(database_id, retention_period="7d")
    
    # Label and Metadata Configuration
    def label(self, key: str, value: str):
        """Add label to Spanner instance"""
        self.spanner_labels[key] = value
        return self
        
    def labels(self, labels: Dict[str, str]):
        """Add multiple labels"""
        self.spanner_labels.update(labels)
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
    def get_compute_capacity(self) -> Dict[str, Any]:
        """Get compute capacity configuration"""
        if self.processing_units:
            return {
                "processing_units": self.processing_units
            }
        else:
            return {
                "node_count": self.node_count
            }
            
    def is_multi_region(self) -> bool:
        """Check if instance is multi-region"""
        return self.multi_region
        
    def is_production_ready(self) -> bool:
        """Check if instance is production ready"""
        return (
            (self.node_count >= 3 or (self.processing_units and self.processing_units >= 300)) and
            self.backup_enabled and
            self.monitoring_enabled and
            self.deletion_protection
        )
        
    def get_estimated_qps(self) -> int:
        """Get estimated queries per second capacity"""
        if self.processing_units:
            # Rough estimate: 100 processing units = ~1000 QPS
            return (self.processing_units / 100) * 1000
        else:
            # Rough estimate: 1 node = ~2000 QPS
            return self.node_count * 2000
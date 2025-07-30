"""
GCP Cloud SQL Complete Implementation

Combines all Cloud SQL functionality through multiple inheritance:
- CloudSQLCore: Core attributes and authentication
- CloudSQLConfigurationMixin: Chainable configuration methods  
- CloudSQLLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from typing import Dict, Any
from .cloudsql_core import CloudSQLCore
from .cloudsql_configuration import CloudSQLConfigurationMixin
from .cloudsql_lifecycle import CloudSQLLifecycleMixin


class CloudSQL(CloudSQLLifecycleMixin, CloudSQLConfigurationMixin, CloudSQLCore):
    """
    Complete GCP Cloud SQL implementation for managed databases.
    
    This class combines:
    - Database configuration methods (engine, tier, storage, availability)
    - Database lifecycle management (create, destroy, preview)
    - Security and networking configuration
    - Backup and maintenance settings
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize CloudSQL instance for database management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$25.76/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._workload_type = None
        self._monitoring_enabled = True
        self._auto_scaling_enabled = False
    
    # Properties for backward compatibility and easier access
    @property
    def database_name(self):
        """Get database name"""
        return self.db_database_name
    
    @property
    def username(self):
        """Get username"""
        return self.db_username
        
    @property
    def password(self):
        """Get password"""
        return self.db_password
        
    def validate_configuration(self):
        """Validate the current Cloud SQL configuration"""
        errors = []
        warnings = []
        
        # Validate instance name
        if not self.instance_name:
            errors.append("Instance name is required")
        
        # Validate database version
        if not self._is_valid_database_version(self.database_version):
            errors.append(f"Invalid database version: {self.database_version}")
        
        # Validate machine tier
        if not self._is_valid_tier(self.db_tier):
            errors.append(f"Invalid machine tier: {self.db_tier}")
        
        # Validate region
        if not self._is_valid_region(self.db_region):
            warnings.append(f"Unusual region: {self.db_region}")
        
        # Validate disk configuration
        if self.disk_size_gb < 10:
            errors.append("Minimum disk size is 10 GB")
        
        if not self._is_valid_disk_type(self.disk_type):
            errors.append(f"Invalid disk type: {self.disk_type}")
        
        # Validate availability type
        if not self._is_valid_availability_type(self.availability_type):
            errors.append(f"Invalid availability type: {self.availability_type}")
        
        # Validate SSL mode
        if not self._is_valid_ssl_mode(self.ssl_mode):
            errors.append(f"Invalid SSL mode: {self.ssl_mode}")
        
        # Validate maintenance window
        if not (1 <= self.maintenance_window_day <= 7):
            errors.append("Maintenance window day must be between 1 and 7")
        
        if not (0 <= self.maintenance_window_hour <= 23):
            errors.append("Maintenance window hour must be between 0 and 23")
        
        # Security warnings
        if self.public_ip and not self.authorized_networks:
            warnings.append("Public IP enabled without authorized networks - consider adding network restrictions")
        
        if self.ssl_mode == "ALLOW":
            warnings.append("SSL not required - consider enabling SSL for security")
        
        if not self.deletion_protection:
            warnings.append("Deletion protection disabled - consider enabling for production databases")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_database_info(self):
        """Get complete information about the Cloud SQL database"""
        return {
            'instance_name': self.instance_name,
            'database_version': self.database_version,
            'engine': self._get_database_engine(),
            'version': self._get_engine_version(),
            'tier': self.db_tier,
            'region': self.db_region,
            'zone': self.db_zone,
            'connection_name': self.connection_name,
            'database_name': self.database_name,
            'username': self.username,
            'disk_size_gb': self.disk_size_gb,
            'disk_type': self.disk_type,
            'disk_autoresize': self.disk_autoresize,
            'availability_type': self.availability_type,
            'backup_enabled': self.backup_enabled,
            'backup_start_time': self.backup_start_time,
            'deletion_protection': self.deletion_protection,
            'ssl_mode': self.ssl_mode,
            'public_ip': self.public_ip,
            'authorized_networks_count': len(self.authorized_networks),
            'database_flags_count': len(self.database_flags),
            'labels_count': len(self.db_labels),
            'insights_enabled': self.insights_enabled,
            'maintenance_window_day': self.maintenance_window_day,
            'maintenance_window_hour': self.maintenance_window_hour,
            'instance_exists': self.instance_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'workload_type': self._workload_type
        }
    
    def clone(self, new_name: str):
        """Create a copy of this database with a new name"""
        cloned_db = CloudSQL(new_name)
        cloned_db.instance_name = new_name
        cloned_db.database_version = self.database_version
        cloned_db.db_tier = self.db_tier
        cloned_db.db_region = self.db_region
        cloned_db.db_zone = self.db_zone
        cloned_db.database_name = self.database_name
        cloned_db.username = self.username
        cloned_db.password = self.password
        cloned_db.disk_size_gb = self.disk_size_gb
        cloned_db.disk_type = self.disk_type
        cloned_db.disk_autoresize = self.disk_autoresize
        cloned_db.availability_type = self.availability_type
        cloned_db.backup_enabled = self.backup_enabled
        cloned_db.backup_start_time = self.backup_start_time
        cloned_db.deletion_protection = self.deletion_protection
        cloned_db.authorized_networks = self.authorized_networks.copy()
        cloned_db.ssl_mode = self.ssl_mode
        cloned_db.public_ip = self.public_ip
        cloned_db.database_flags = self.database_flags.copy()
        cloned_db.db_labels = self.db_labels.copy()
        cloned_db.insights_enabled = self.insights_enabled
        cloned_db.maintenance_window_day = self.maintenance_window_day
        cloned_db.maintenance_window_hour = self.maintenance_window_hour
        return cloned_db
    
    def export_configuration(self):
        """Export database configuration for backup or migration"""
        return {
            'metadata': {
                'instance_name': self.instance_name,
                'database_version': self.database_version,
                'engine': self._get_database_engine(),
                'region': self.db_region,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'tier': self.db_tier,
                'zone': self.db_zone,
                'database_name': self.database_name,
                'username': self.username,
                'disk_size_gb': self.disk_size_gb,
                'disk_type': self.disk_type,
                'disk_autoresize': self.disk_autoresize,
                'availability_type': self.availability_type,
                'backup_enabled': self.backup_enabled,
                'backup_start_time': self.backup_start_time,
                'deletion_protection': self.deletion_protection,
                'authorized_networks': self.authorized_networks,
                'ssl_mode': self.ssl_mode,
                'public_ip': self.public_ip,
                'database_flags': self.database_flags,
                'labels': self.db_labels,
                'insights_enabled': self.insights_enabled,
                'maintenance_window_day': self.maintenance_window_day,
                'maintenance_window_hour': self.maintenance_window_hour,
                'optimization_priority': self._optimization_priority,
                'workload_type': self._workload_type,
                'monitoring_enabled': self._monitoring_enabled,
                'auto_scaling_enabled': self._auto_scaling_enabled
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import database configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.db_tier = config.get('tier', 'db-f1-micro')
            self.db_zone = config.get('zone')
            self.database_name = config.get('database_name', 'app_production')
            self.username = config.get('username', 'app_user')
            self.disk_size_gb = config.get('disk_size_gb', 20)
            self.disk_type = config.get('disk_type', 'PD_SSD')
            self.disk_autoresize = config.get('disk_autoresize', True)
            self.availability_type = config.get('availability_type', 'ZONAL')
            self.backup_enabled = config.get('backup_enabled', True)
            self.backup_start_time = config.get('backup_start_time', '03:00')
            self.deletion_protection = config.get('deletion_protection', True)
            self.authorized_networks = config.get('authorized_networks', [])
            self.ssl_mode = config.get('ssl_mode', 'REQUIRE')
            self.public_ip = config.get('public_ip', False)
            self.database_flags = config.get('database_flags', {})
            self.db_labels = config.get('labels', {})
            self.insights_enabled = config.get('insights_enabled', False)
            self.maintenance_window_day = config.get('maintenance_window_day', 7)
            self.maintenance_window_hour = config.get('maintenance_window_hour', 4)
            self._optimization_priority = config.get('optimization_priority')
            self._workload_type = config.get('workload_type')
            self._monitoring_enabled = config.get('monitoring_enabled', True)
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', False)
        
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
        
        print(f"🎯 Cross-Cloud Magic: Optimizing Cloud SQL for {priority}")
        
        # Apply GCP-specific optimizations
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective database")
            # Use smaller tier if not already optimized
            if self.db_tier in ["db-n1-standard-4", "db-n1-standard-8"]:
                print("   💡 Reducing machine tier for cost savings")
                self.db_tier = "db-n1-standard-2"
            # Use zonal instead of regional for cost savings
            if self.availability_type == "REGIONAL":
                print("   💡 Switching to zonal availability for cost savings")
                self.availability_type = "ZONAL"
            # Use HDD for non-performance critical workloads
            if self.disk_type == "PD_SSD" and self._workload_type not in ["oltp", "api"]:
                print("   💡 Switching to HDD storage for cost savings")
                self.disk_type = "PD_HDD"
            
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance database")
            # Ensure SSD storage
            if self.disk_type == "PD_HDD":
                print("   💡 Switching to SSD storage for better performance")
                self.disk_type = "PD_SSD"
            # Enable query insights for performance monitoring
            if not self.insights_enabled:
                print("   💡 Enabling query insights for performance monitoring")
                self.insights_enabled = True
            # Add performance-oriented database flags
            if 'POSTGRES' in self.database_version:
                self.database_flags.update({
                    "shared_buffers": "256MB",
                    "effective_cache_size": "1GB",
                    "checkpoint_completion_target": "0.9"
                })
                print("   💡 Applied PostgreSQL performance optimizations")
            
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable database")
            # Enable high availability
            if self.availability_type == "ZONAL":
                print("   💡 Enabling regional high availability")
                self.availability_type = "REGIONAL"
            # Enable backups if not already enabled
            if not self.backup_enabled:
                print("   💡 Enabling automated backups")
                self.backup_enabled = True
            # Enable deletion protection
            if not self.deletion_protection:
                print("   💡 Enabling deletion protection")
                self.deletion_protection = True
            # Require SSL
            if self.ssl_mode == "ALLOW":
                print("   💡 Requiring SSL for security")
                self.ssl_mode = "REQUIRE"
            
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant database")
            # Disable public IP
            if self.public_ip:
                print("   💡 Disabling public IP access for compliance")
                self.public_ip = False
            # Require SSL with verification
            if self.ssl_mode in ["ALLOW", "REQUIRE"]:
                print("   💡 Enabling SSL with CA verification")
                self.ssl_mode = "VERIFY_CA"
            # Enable query insights for auditing
            if not self.insights_enabled:
                print("   💡 Enabling query insights for audit logging")
                self.insights_enabled = True
            # Add compliance labels
            self.db_labels.update({
                "compliance": "enabled",
                "data-classification": "regulated"
            })
            print("   💡 Added compliance labels")
        
        return self
    
    def optimize_workload(self, workload_type: str):
        """Optimize database for specific workload patterns"""
        valid_workloads = ["web", "api", "analytics", "oltp", "olap", "mixed"]
        if workload_type not in valid_workloads:
            raise ValueError(f"Workload type must be one of: {valid_workloads}")
        
        self._workload_type = workload_type
        
        print(f"🎯 Optimizing for {workload_type} workload")
        
        if workload_type == "web":
            self.web_app_db()
        elif workload_type == "api":
            self.api_db()
        elif workload_type == "analytics":
            self.olap_db()
        elif workload_type == "oltp":
            self.oltp_db()
        elif workload_type == "olap":
            self.olap_db()
        elif workload_type == "mixed":
            # Balanced configuration
            self.database_flags.update({
                "max_connections": "200",
                "shared_buffers": "256MB",
                "effective_cache_size": "2GB"
            })
        
        return self
    
    def enable_monitoring(self, enabled: bool = True):
        """Enable comprehensive monitoring and alerting"""
        self._monitoring_enabled = enabled
        if enabled:
            self.insights_enabled = True
            print("📊 Comprehensive monitoring enabled")
            print("   💡 Query insights activated")
            print("   💡 Performance monitoring configured")
        return self
    
    def enable_auto_scaling(self, enabled: bool = True):
        """Enable automatic storage scaling"""
        self._auto_scaling_enabled = enabled
        if enabled:
            self.disk_autoresize = True
            print("📈 Auto-scaling enabled for storage")
        return self
    
    def create_read_replica(self, replica_name: str, region: str = None):
        """Create a read replica of this database"""
        replica = self.clone(replica_name)
        replica.instance_name = replica_name
        replica.read_replica_db()
        if region:
            replica.region(region)
        
        print(f"📖 Read replica configuration created: {replica_name}")
        return replica


# Convenience functions for creating CloudSQL instances
def create_postgres_db(name: str, version: str = "15", tier: str = "small") -> CloudSQL:
    """Create a PostgreSQL database with common configuration"""
    db = CloudSQL(name)
    db.instance(name).postgres(version)
    if tier == "micro":
        db.micro()
    elif tier == "small":
        db.small()
    elif tier == "standard":
        db.standard()
    elif tier == "large":
        db.large()
    return db

def create_mysql_db(name: str, version: str = "8.0", tier: str = "small") -> CloudSQL:
    """Create a MySQL database with common configuration"""
    db = CloudSQL(name)
    db.instance(name).mysql(version)
    if tier == "micro":
        db.micro()
    elif tier == "small":
        db.small()
    elif tier == "standard":
        db.standard()
    elif tier == "large":
        db.large()
    return db

def create_web_app_db(name: str, engine: str = "postgres") -> CloudSQL:
    """Create a database optimized for web applications"""
    db = CloudSQL(name)
    if engine == "postgres":
        db.postgres().production_db().optimize_workload("web")
    else:
        db.mysql().production_db().optimize_workload("web")
    return db

def create_analytics_db(name: str) -> CloudSQL:
    """Create a database optimized for analytics workloads"""
    db = CloudSQL(name)
    db.postgres().analytics_db().optimize_workload("analytics")
    return db

def create_dev_db(name: str, engine: str = "postgres") -> CloudSQL:
    """Create a development database"""
    db = CloudSQL(name)
    if engine == "postgres":
        db.postgres().development_db()
    else:
        db.mysql().development_db()
    return db
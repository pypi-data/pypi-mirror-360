"""
AWS RDS Complete Implementation

Combines all RDS functionality through multiple inheritance:
- RDSCore: Core attributes and authentication
- RDSConfigurationMixin: Chainable configuration methods  
- RDSLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from .rds_core import RDSCore
from .rds_configuration import RDSConfigurationMixin
from .rds_lifecycle import RDSLifecycleMixin


class RDS(RDSLifecycleMixin, RDSConfigurationMixin, RDSCore):
    """
    Complete AWS RDS implementation for managed relational databases.
    
    This class combines:
    - Database configuration methods (engines, instance classes, storage)
    - Database lifecycle management (create, destroy, preview)
    - Backup and maintenance scheduling
    - Multi-AZ deployment and read replicas
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize RDS instance for database management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$30.66/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._read_replicas_configured = False
        self._monitoring_configured = False
        
    def validate_configuration(self):
        """Validate the current RDS configuration"""
        errors = []
        warnings = []
        
        # Validate instance identifier
        if not self.instance_id and not self.name:
            errors.append("Instance identifier is required")
        elif self.instance_id and not self._is_valid_instance_id(self.instance_id):
            errors.append("Invalid instance identifier format")
        
        # Validate database engine
        valid_engines = [
            "mysql", "postgres", "mariadb", "oracle-ee", "oracle-se2", "oracle-se1", "oracle-se",
            "sqlserver-ee", "sqlserver-se", "sqlserver-ex", "sqlserver-web",
            "aurora-mysql", "aurora-postgresql"
        ]
        if self.engine and self.engine not in valid_engines:
            warnings.append(f"Unusual database engine: {self.engine}")
        
        # Validate instance class
        if self.db_instance_class:
            valid_instance_families = ["db.t3", "db.t4g", "db.m5", "db.m6i", "db.r5", "db.r6g", "db.x1e", "db.z1d"]
            if not any(self.db_instance_class.startswith(family) for family in valid_instance_families):
                warnings.append(f"Unusual instance class: {self.db_instance_class}")
        
        # Validate storage
        if self.allocated_storage:
            if self.allocated_storage < 20:
                errors.append("Minimum allocated storage is 20 GB")
            elif self.allocated_storage > 65536:
                errors.append("Maximum allocated storage is 65536 GB (64 TB)")
        
        # Validate storage type
        if self.storage_type and self.storage_type not in ["gp2", "gp3", "io1", "io2", "standard"]:
            errors.append(f"Invalid storage type: {self.storage_type}")
        
        # Validate backup retention
        if self.backup_retention_period is not None:
            if not (0 <= self.backup_retention_period <= 35):
                errors.append("Backup retention period must be between 0 and 35 days")
        
        # Validate master username
        if self.master_username:
            if len(self.master_username) < 1 or len(self.master_username) > 63:
                errors.append("Master username must be 1-63 characters")
        
        # Validate port
        if self.db_port:
            if not (1150 <= self.db_port <= 65535):
                errors.append("Port must be between 1150 and 65535")
        
        # Security validations
        if self.publicly_accessible:
            warnings.append("Database is publicly accessible - consider security implications")
        
        if not self.storage_encrypted:
            warnings.append("Storage encryption is disabled - consider enabling for security")
        
        if self.backup_retention_period == 0:
            warnings.append("Automated backups are disabled - consider enabling for data protection")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_database_info(self):
        """Get complete information about the RDS database"""
        return {
            'instance_id': self.db_instance_id or self.name,
            'engine': self.engine,
            'instance_class': self.db_instance_class,
            'allocated_storage': self.allocated_storage,
            'storage_type': self.storage_type,
            'master_username': self.master_username,
            'database_name': self.database_name,
            'port': self.db_port,
            'endpoint': self.endpoint,
            'status': self.status,
            'multi_az': self.multi_az,
            'publicly_accessible': self.publicly_accessible,
            'storage_encrypted': self.storage_encrypted,
            'kms_key_id': self.kms_key_id,
            'backup_retention_period': self.backup_retention_period,
            'backup_window': self.backup_window,
            'maintenance_window': self.maintenance_window,
            'auto_minor_version_upgrade': self.auto_minor_version_upgrade,
            'vpc_security_groups_count': len(self.vpc_security_groups),
            'subnet_group': self.subnet_group,
            'parameter_group': self.parameter_group,
            'option_group': self.option_group,
            'tags_count': len(self.tags),
            'instance_exists': self.instance_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'read_replicas_configured': self._read_replicas_configured,
            'monitoring_configured': self._monitoring_configured
        }
    
    def clone(self, new_name: str):
        """Create a copy of this database with a new name"""
        cloned_db = RDS(new_name)
        cloned_db.db_instance_id = new_name
        cloned_db.engine = self.engine
        cloned_db.db_instance_class = self.db_instance_class
        cloned_db.allocated_storage = self.allocated_storage
        cloned_db.storage_type = self.storage_type
        cloned_db.master_username = self.master_username
        cloned_db.master_password = self.master_password
        cloned_db.database_name = self.database_name
        cloned_db.db_port = self.db_port
        cloned_db.vpc_security_groups = self.vpc_security_groups.copy()
        cloned_db.subnet_group = self.subnet_group
        cloned_db.parameter_group = self.parameter_group
        cloned_db.option_group = self.option_group
        cloned_db.backup_retention_period = self.backup_retention_period
        cloned_db.backup_window = self.backup_window
        cloned_db.maintenance_window = self.maintenance_window
        cloned_db.multi_az = self.multi_az
        cloned_db.publicly_accessible = self.publicly_accessible
        cloned_db.auto_minor_version_upgrade = self.auto_minor_version_upgrade
        cloned_db.storage_encrypted = self.storage_encrypted
        cloned_db.kms_key_id = self.kms_key_id
        cloned_db.tags = self.tags.copy()
        return cloned_db
    
    def export_configuration(self):
        """Export database configuration for backup or migration"""
        return {
            'metadata': {
                'instance_id': self.db_instance_id or self.name,
                'engine': self.engine,
                'instance_class': self.db_instance_class,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'allocated_storage': self.allocated_storage,
                'storage_type': self.storage_type,
                'master_username': self.master_username,
                'database_name': self.database_name,
                'port': self.db_port,
                'vpc_security_groups': self.vpc_security_groups,
                'subnet_group': self.subnet_group,
                'parameter_group': self.parameter_group,
                'option_group': self.option_group,
                'backup_retention_period': self.backup_retention_period,
                'backup_window': self.backup_window,
                'maintenance_window': self.maintenance_window,
                'multi_az': self.multi_az,
                'publicly_accessible': self.publicly_accessible,
                'auto_minor_version_upgrade': self.auto_minor_version_upgrade,
                'storage_encrypted': self.storage_encrypted,
                'kms_key_id': self.kms_key_id,
                'optimization_priority': self._optimization_priority,
                'read_replicas_configured': self._read_replicas_configured,
                'monitoring_configured': self._monitoring_configured
            },
            'tags': self.tags
        }
    
    def import_configuration(self, config_data: dict):
        """Import database configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.allocated_storage = config.get('allocated_storage')
            self.storage_type = config.get('storage_type', 'gp2')
            self.master_username = config.get('master_username')
            self.database_name = config.get('database_name')
            self.port = config.get('port')
            self.vpc_security_groups = config.get('vpc_security_groups', [])
            self.subnet_group = config.get('subnet_group')
            self.parameter_group = config.get('parameter_group')
            self.option_group = config.get('option_group')
            self.backup_retention_period = config.get('backup_retention_period')
            self.backup_window = config.get('backup_window')
            self.maintenance_window = config.get('maintenance_window')
            self.multi_az = config.get('multi_az', False)
            self.publicly_accessible = config.get('publicly_accessible', False)
            self.auto_minor_version_upgrade = config.get('auto_minor_version_upgrade', True)
            self.storage_encrypted = config.get('storage_encrypted', True)
            self.kms_key_id = config.get('kms_key_id')
            self._optimization_priority = config.get('optimization_priority')
            self._read_replicas_configured = config.get('read_replicas_configured', False)
            self._monitoring_configured = config.get('monitoring_configured', False)
        
        if 'tags' in config_data:
            self.tags = config_data['tags']
        
        return self
    
    def _is_valid_instance_id(self, instance_id: str) -> bool:
        """Validate RDS instance identifier according to AWS rules"""
        import re
        
        # Instance identifier can be 1-63 characters
        if len(instance_id) < 1 or len(instance_id) > 63:
            return False
        
        # Must start with a letter
        if not instance_id[0].isalpha():
            return False
        
        # Must contain only letters, numbers, and hyphens
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9-]*$', instance_id):
            return False
        
        # Cannot end with a hyphen
        if instance_id.endswith('-'):
            return False
        
        # Cannot contain consecutive hyphens
        if '--' in instance_id:
            return False
        
        return True
    
    def read_replica(self, replica_id: str):
        """Configure a read replica for this database
        
        Args:
            replica_id: Identifier for the read replica
            
        Returns:
            Self for method chaining
        """
        print(f"📖 Configuring read replica: {replica_id}")
        self._read_replicas_configured = True
        
        # Add read replica configuration
        if not hasattr(self, '_read_replicas'):
            self._read_replicas = []
        
        self._read_replicas.append({
            'replica_id': replica_id,
            'source_db': self.db_instance_id or self.name
        })
        
        return self
    
    def monitoring(self, enabled: bool = True, enhanced: bool = False):
        """Configure database monitoring
        
        Args:
            enabled: Whether to enable basic monitoring
            enhanced: Whether to enable enhanced monitoring
            
        Returns:
            Self for method chaining
        """
        self._monitoring_configured = enabled
        
        if enabled:
            print("📊 Enabling database monitoring")
            if enhanced:
                print("   📊 Enhanced monitoring enabled")
        else:
            print("📊 Disabling database monitoring")
        
        return self
    
    def auto_scaling(self, enabled: bool = True, max_capacity: int = None):
        """Configure auto-scaling for Aurora databases
        
        Args:
            enabled: Whether to enable auto-scaling
            max_capacity: Maximum capacity for auto-scaling
            
        Returns:
            Self for method chaining
        """
        if self.engine and self.engine.startswith('aurora'):
            print(f"🔄 Configuring Aurora auto-scaling: {'enabled' if enabled else 'disabled'}")
            if enabled and max_capacity:
                print(f"   🔄 Maximum capacity: {max_capacity}")
        else:
            print("⚠️  Auto-scaling is only available for Aurora databases")
        
        return self


# Convenience functions for creating RDS instances
def create_database(name: str, engine: str, instance_class: str = "db.t3.micro", storage_gb: int = 20) -> RDS:
    """Create a new RDS database with basic configuration"""
    db = RDS(name)
    db.instance_id(name).engine(engine).instance_class(instance_class).storage(storage_gb)
    return db

def create_postgresql(name: str, instance_class: str = "db.t3.small", storage_gb: int = 20) -> RDS:
    """Create a PostgreSQL database"""
    db = RDS(name)
    db.instance_id(name).postgresql().instance_class(instance_class).storage(storage_gb).port(5432)
    return db

def create_mysql(name: str, instance_class: str = "db.t3.small", storage_gb: int = 20) -> RDS:
    """Create a MySQL database"""
    db = RDS(name)
    db.instance_id(name).mysql().instance_class(instance_class).storage(storage_gb).port(3306)
    return db

def create_aurora_cluster(name: str, engine: str = "aurora-postgresql") -> RDS:
    """Create an Aurora cluster"""
    db = RDS(name)
    db.instance_id(name).engine(engine).instance_class("db.r5.large")
    if engine == "aurora-postgresql":
        db.port(5432)
    else:
        db.port(3306)
    return db

def create_production_database(name: str, engine: str, instance_class: str = "db.m5.large") -> RDS:
    """Create a production-ready database with best practices"""
    db = RDS(name)
    db.instance_id(name).engine(engine).instance_class(instance_class)
    db.storage(100, "gp3").multi_az(True).backup(30).encryption(True)
    db.private_subnet().monitoring(True, enhanced=True)
    return db
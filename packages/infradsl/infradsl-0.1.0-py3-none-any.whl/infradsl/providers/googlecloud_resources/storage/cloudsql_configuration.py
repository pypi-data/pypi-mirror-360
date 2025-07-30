"""
GCP Cloud SQL Configuration Mixin

Chainable configuration methods for Google Cloud SQL databases.
Provides Rails-like method chaining for fluent database configuration.
"""

from typing import Dict, Any, List, Optional


class CloudSQLConfigurationMixin:
    """
    Mixin for Cloud SQL database configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Database engine and version selection
    - Machine tier and performance settings
    - Storage configuration
    - High availability and backup settings
    - Security and network configuration
    """
    
    def instance(self, name: str):
        """Set instance name (Rails-like method chaining)"""
        self.instance_name = name
        return self
        
    def engine(self, database_version: str):
        """Set database engine version (e.g., 'POSTGRES_15', 'MYSQL_8_0')"""
        if not self._is_valid_database_version(database_version):
            print(f"⚠️  Warning: Unusual database version '{database_version}' - verify this is supported")
        self.database_version = database_version
        return self
        
    def postgres(self, version: str = "15"):
        """Configure PostgreSQL database (Rails convention)"""
        self.database_version = f"POSTGRES_{version}"
        return self
        
    def mysql(self, version: str = "8.0"):
        """Configure MySQL database (Rails convention)"""
        version_clean = version.replace(".", "_")
        self.database_version = f"MYSQL_{version_clean}"
        return self
        
    def sqlserver(self, version: str = "2019", edition: str = "STANDARD"):
        """Configure SQL Server database (Rails convention)"""
        self.database_version = f"SQLSERVER_{version}_{edition}"
        return self
        
    def tier(self, tier_name: str):
        """Set machine tier (e.g., 'db-f1-micro', 'db-n1-standard-1')"""
        if not self._is_valid_tier(tier_name):
            print(f"⚠️  Warning: Unusual tier '{tier_name}' - verify this is available")
        self.db_tier = tier_name
        return self
        
    def region(self, region_name: str):
        """Set database region (e.g., 'us-central1', 'europe-north1')"""
        if not self._is_valid_region(region_name):
            print(f"⚠️  Warning: Unusual region '{region_name}' - verify this is correct")
        self.db_region = region_name
        return self
        
    def zone(self, zone_name: str):
        """Set specific zone for zonal instances"""
        self.db_zone = zone_name
        return self
        
    def database(self, database_name: str):
        """Set the initial database name (Rails convention: app_production)"""
        self.db_database_name = database_name
        return self
        
    def username(self, username_name: str):
        """Set the database username (Rails convention: app_user)"""
        self.db_username = username_name
        return self
        
    def password(self, password_value: str):
        """Set the database password (auto-generated if not provided)"""
        self.db_password = password_value
        return self
        
    # Storage configuration
    def disk_size(self, size_gb: int):
        """Set disk size in GB"""
        if size_gb < 10:
            raise ValueError("Minimum disk size is 10 GB")
        self.disk_size_gb = size_gb
        return self
        
    def ssd(self):
        """Use SSD storage for better performance (Rails convention)"""
        self.disk_type = "PD_SSD"
        return self
        
    def hdd(self):
        """Use HDD storage for cost optimization (Rails convention)"""
        self.disk_type = "PD_HDD"
        return self
        
    def autoresize(self, enabled: bool = True):
        """Enable/disable automatic disk resize"""
        self.disk_autoresize = enabled
        return self
        
    # Machine tier convenience methods
    def micro(self):
        """Use micro tier for development (Rails convention)"""
        self.db_tier = "db-f1-micro"
        return self
        
    def small(self):
        """Use small tier for small workloads (Rails convention)"""
        self.db_tier = "db-n1-standard-1"
        return self
        
    def standard(self):
        """Use standard tier for production (Rails convention)"""
        self.db_tier = "db-n1-standard-2"
        return self
        
    def large(self):
        """Use large tier for high-traffic applications (Rails convention)"""
        self.db_tier = "db-n1-standard-4"
        return self
        
    def xlarge(self):
        """Use extra large tier for enterprise workloads (Rails convention)"""
        self.db_tier = "db-n1-standard-8"
        return self
        
    def custom(self, cpus: int, memory_gb: int):
        """Use custom machine configuration"""
        # Custom machine format: db-custom-{cpus}-{memory_mb}
        memory_mb = memory_gb * 1024
        self.db_tier = f"db-custom-{cpus}-{memory_mb}"
        return self
        
    # Availability and reliability
    def high_availability(self):
        """Enable regional high availability (Rails convention)"""
        self.availability_type = "REGIONAL"
        return self
        
    def zonal(self):
        """Use zonal configuration for cost savings (Rails convention)"""
        self.availability_type = "ZONAL"
        return self
        
    def backups(self, enabled: bool = True, start_time: str = "03:00"):
        """Configure automatic backups"""
        self.backup_enabled = enabled
        self.backup_start_time = start_time
        return self
        
    def no_backups(self):
        """Disable automatic backups (Rails convenience)"""
        return self.backups(False)
        
    def maintenance(self, day: int = 7, hour: int = 4):
        """Set maintenance window (day: 1=Monday, 7=Sunday; hour: 0-23)"""
        if not (1 <= day <= 7):
            raise ValueError("Day must be between 1 (Monday) and 7 (Sunday)")
        if not (0 <= hour <= 23):
            raise ValueError("Hour must be between 0 and 23")
        self.maintenance_window_day = day
        self.maintenance_window_hour = hour
        return self
        
    def deletion_protection(self, enabled: bool = True):
        """Enable/disable deletion protection"""
        self.deletion_protection = enabled
        return self
        
    def no_deletion_protection(self):
        """Disable deletion protection (Rails convenience)"""
        return self.deletion_protection(False)
        
    # Security and networking
    def ssl_required(self, required: bool = True):
        """Require SSL connections for security"""
        self.ssl_mode = "REQUIRE" if required else "ALLOW"
        return self
        
    def ssl_verify_ca(self):
        """Require SSL with CA verification"""
        self.ssl_mode = "VERIFY_CA"
        return self
        
    def ssl_verify_identity(self):
        """Require SSL with full identity verification"""
        self.ssl_mode = "VERIFY_IDENTITY"
        return self
        
    def public_ip(self, enabled: bool = True):
        """Enable/disable public IP access"""
        if enabled:
            print("⚠️  WARNING: Enabling public IP access exposes database to internet")
            print("   💡 Consider using private IP or authorized networks for security")
        self.public_ip = enabled
        return self
        
    def private_ip(self):
        """Use private IP only (Rails security convention)"""
        return self.public_ip(False)
        
    def authorized_network(self, cidr: str, name: str = None):
        """Add authorized network for database access"""
        network = {"value": cidr}
        if name:
            network["name"] = name
        self.authorized_networks.append(network)
        return self
        
    def allow_all_networks(self):
        """Allow access from all networks (WARNING: Insecure)"""
        print("⚠️  WARNING: Allowing access from all networks (0.0.0.0/0) is insecure")
        print("   💡 Consider using specific authorized networks instead")
        return self.authorized_network("0.0.0.0/0", "allow-all-WARNING")
        
    # Advanced configuration
    def insights(self, enabled: bool = True):
        """Enable/disable query insights and monitoring"""
        self.insights_enabled = enabled
        return self
        
    def labels(self, labels: Dict[str, str]):
        """Add labels for organization and billing"""
        self.db_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label (Rails convenience)"""
        self.db_labels[key] = value
        return self
        
    def flags(self, flags: Dict[str, str]):
        """Set custom database flags"""
        self.database_flags.update(flags)
        return self
        
    def flag(self, name: str, value: str):
        """Set individual database flag (Rails convenience)"""
        self.database_flags[name] = value
        return self
        
    # Rails-like environment configurations
    def development_db(self):
        """Configure for development environment (Rails convention)"""
        return (self.micro()
                .zonal()
                .ssd()
                .deletion_protection(False)
                .database("app_development")
                .backups(False)
                .insights(False))
                
    def staging_db(self):
        """Configure for staging environment (Rails convention)"""
        return (self.small()
                .zonal()
                .ssd()
                .deletion_protection(False)
                .database("app_staging")
                .backups(True)
                .insights(True))
                
    def production_db(self):
        """Configure for production environment (Rails convention)"""
        return (self.standard()
                .high_availability()
                .ssd()
                .autoresize(True)
                .backups(True)
                .deletion_protection(True)
                .database("app_production")
                .insights(True)
                .ssl_required(True))
                
    def analytics_db(self):
        """Configure for analytics workloads (Rails convention)"""
        return (self.large()
                .ssd()
                .disk_size(100)
                .zonal()  # Analytics can handle downtime for cost savings
                .database("analytics")
                .insights(True))
                
    def read_replica_db(self):
        """Configure as read replica (Rails convention)"""
        return (self.small()
                .zonal()
                .ssd()
                .no_backups()  # Read replicas don't need backups
                .deletion_protection(False)
                .database("app_production_replica"))
                
    # Performance and workload optimization
    def web_app_db(self):
        """Optimize for web application workloads"""
        self.database_flags.update({
            "max_connections": "100",
            "shared_preload_libraries": "pg_stat_statements",
            "log_statement": "all"
        })
        return self
        
    def api_db(self):
        """Optimize for API workloads"""
        self.database_flags.update({
            "max_connections": "200",
            "effective_cache_size": "1GB",
            "shared_buffers": "256MB"
        })
        return self
        
    def oltp_db(self):
        """Optimize for OLTP (Online Transaction Processing) workloads"""
        self.database_flags.update({
            "max_connections": "500",
            "checkpoint_completion_target": "0.9",
            "wal_buffers": "32MB"
        })
        return self
        
    def olap_db(self):
        """Optimize for OLAP (Online Analytical Processing) workloads"""
        self.database_flags.update({
            "work_mem": "256MB",
            "maintenance_work_mem": "1GB",
            "effective_cache_size": "4GB"
        })
        return self
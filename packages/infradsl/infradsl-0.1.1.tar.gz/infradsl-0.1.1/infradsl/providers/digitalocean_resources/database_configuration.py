"""
DigitalOcean Database Configuration Implementation

Configuration methods for DigitalOcean Managed Databases.
Provides chainable methods for fluent database configuration.
"""

from typing import Dict, Any, List, Optional, Union


class DatabaseConfigurationMixin:
    """
    Configuration methods for DigitalOcean Database.
    
    This mixin provides:
    - Chainable configuration methods for fluent API
    - Engine-specific configurations (PostgreSQL, MySQL, Redis)
    - Size and performance configuration
    - Network and security settings
    - Backup and maintenance configuration
    - Common database patterns and presets
    """
    
    # Engine configuration methods
    def postgresql(self, version: Optional[str] = None):
        """Configure as PostgreSQL database"""
        self.engine = "pg"
        if version:
            self.version = version
        return self
    
    def mysql(self, version: Optional[str] = None):
        """Configure as MySQL database"""
        self.engine = "mysql"
        if version:
            self.version = version
        return self
    
    def redis(self, version: Optional[str] = None):
        """Configure as Redis database"""
        self.engine = "redis"
        if version:
            self.version = version
        return self
    
    # Size and performance configuration
    def size(self, size: str):
        """Set database size (e.g., 'db-s-1vcpu-1gb', 'db-s-2vcpu-4gb')"""
        if not self._is_valid_size(size):
            raise ValueError(f"Invalid database size: {size}")
        self.size = size
        return self
    
    def region(self, region: str):
        """Set the region (e.g., 'nyc3', 'sfo3')"""
        if not self._is_valid_region(region):
            raise ValueError(f"Invalid region: {region}")
        self.region = region
        return self
    
    def nodes(self, num_nodes: int):
        """Set number of nodes (1-3, for high availability)"""
        if not isinstance(num_nodes, int) or num_nodes < 1 or num_nodes > 3:
            raise ValueError("Number of nodes must be between 1 and 3")
        self.num_nodes = num_nodes
        return self
    
    def storage(self, size_gb: int):
        """Set custom storage size in GB"""
        if size_gb < 1:
            raise ValueError("Storage size must be at least 1 GB")
        self.storage_size_mib = size_gb * 1024
        return self
    
    # Network configuration
    def private_network(self, vpc_uuid: str):
        """Place database in a private network/VPC"""
        self.private_network_uuid = vpc_uuid
        return self
    
    def trusted_sources(self, sources: List[str]):
        """Add trusted sources (IP addresses/ranges)"""
        self.trusted_sources = sources
        return self
    
    def add_trusted_source(self, source: str):
        """Add a single trusted source"""
        if source not in self.trusted_sources:
            self.trusted_sources.append(source)
        return self
    
    def firewall_rule(self, type: str, value: str):
        """Add firewall rule"""
        rule = {"type": type, "value": value}
        self.firewall_rules.append(rule)
        return self
    
    # Engine-specific configurations
    def eviction_policy(self, policy: str):
        """Set Redis eviction policy (allkeys-lru, volatile-lru, etc.)"""
        if self.engine != "redis":
            raise ValueError("Eviction policy can only be set for Redis databases")
        valid_policies = ["noeviction", "allkeys-lru", "volatile-lru", "allkeys-random", "volatile-random", "volatile-ttl"]
        if policy not in valid_policies:
            raise ValueError(f"Invalid eviction policy. Must be one of: {valid_policies}")
        self.eviction_policy = policy
        return self
    
    def sql_mode(self, mode: str):
        """Set MySQL SQL mode"""
        if self.engine != "mysql":
            raise ValueError("SQL mode can only be set for MySQL databases")
        self.sql_mode = mode
        return self
    
    def redis_maxmemory_policy(self, policy: str):
        """Set Redis maxmemory policy"""
        if self.engine != "redis":
            raise ValueError("Redis config can only be set for Redis databases")
        self.redis_config["maxmemory_policy"] = policy
        return self
    
    def postgres_shared_preload_libraries(self, libraries: List[str]):
        """Set PostgreSQL shared_preload_libraries"""
        if self.engine != "pg":
            raise ValueError("PostgreSQL config can only be set for PostgreSQL databases")
        self.postgres_config["shared_preload_libraries"] = libraries
        return self
    
    def mysql_innodb_buffer_pool_size(self, size_mb: int):
        """Set MySQL InnoDB buffer pool size"""
        if self.engine != "mysql":
            raise ValueError("MySQL config can only be set for MySQL databases")
        self.mysql_config["innodb_buffer_pool_size"] = f"{size_mb}M"
        return self
    
    # Backup and recovery configuration
    def backup_enabled(self, enabled: bool = True):
        """Enable or disable automatic backups"""
        self.backup_enabled = enabled
        return self
    
    def backup_hour(self, hour: int):
        """Set UTC hour for daily backups (0-23)"""
        if not isinstance(hour, int) or hour < 0 or hour > 23:
            raise ValueError("Backup hour must be between 0 and 23")
        self.backup_hour = hour
        return self
    
    def point_in_time_recovery(self, enabled: bool = True):
        """Enable point-in-time recovery"""
        self.point_in_time_recovery = enabled
        return self
    
    def restore_from_backup(self, backup_name: str):
        """Restore database from backup"""
        self.backup_restore = {
            "type": "backup",
            "name": backup_name
        }
        return self
    
    # Maintenance configuration
    def maintenance_window(self, day: str, hour: str):
        """Set maintenance window (day: monday-sunday, hour: HH:MM)"""
        valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if day.lower() not in valid_days:
            raise ValueError(f"Invalid day. Must be one of: {valid_days}")
        
        # Validate hour format
        try:
            hour_parts = hour.split(":")
            if len(hour_parts) != 2 or not (0 <= int(hour_parts[0]) <= 23) or not (0 <= int(hour_parts[1]) <= 59):
                raise ValueError()
        except:
            raise ValueError("Hour must be in HH:MM format (24-hour)")
        
        self.maintenance_window = {
            "day": day.lower(),
            "hour": hour
        }
        return self
    
    # Monitoring and alerts
    def monitoring(self, enabled: bool = True):
        """Enable or disable monitoring"""
        self.monitoring_enabled = enabled
        return self
    
    def alerts(self, enabled: bool = True):
        """Enable or disable alerts"""
        self.alerts_enabled = enabled
        return self
    
    def alert_policy(self, metric: str, threshold: float, comparison: str = "gt"):
        """Add alert policy"""
        if comparison not in ["gt", "lt", "eq", "gte", "lte"]:
            raise ValueError("Comparison must be one of: gt, lt, eq, gte, lte")
        
        self.alert_policy[metric] = {
            "threshold": threshold,
            "comparison": comparison
        }
        return self
    
    # Labels and metadata
    def tags(self, tags: List[str]):
        """Add tags to the database"""
        self.database_tags = tags
        return self
    
    def tag(self, tag: str):
        """Add a single tag"""
        if tag not in self.database_tags:
            self.database_tags.append(tag)
        return self
    
    def label(self, key: str, value: str):
        """Add a label"""
        self.database_labels[key] = value
        return self
    
    def annotate(self, key: str, value: str):
        """Add an annotation"""
        self.database_annotations[key] = value
        return self
    
    # Rails-like convenience methods
    def development(self):
        """Configure for development environment"""
        return (self.size("db-s-1vcpu-1gb")
                .nodes(1)
                .label("environment", "development")
                .tag("development"))
    
    def staging(self):
        """Configure for staging environment"""
        return (self.size("db-s-2vcpu-4gb")
                .nodes(1)
                .label("environment", "staging")
                .tag("staging"))
    
    def production(self):
        """Configure for production environment"""
        return (self.size("db-s-4vcpu-8gb")
                .nodes(3)
                .backup_enabled(True)
                .point_in_time_recovery(True)
                .monitoring(True)
                .alerts(True)
                .label("environment", "production")
                .tag("production"))
    
    # Database-specific patterns
    def cache_database(self):
        """Configure as Redis cache"""
        return (self.redis()
                .eviction_policy("allkeys-lru")
                .label("purpose", "cache")
                .tag("cache"))
    
    def session_store(self):
        """Configure as session storage"""
        return (self.redis()
                .eviction_policy("volatile-ttl")
                .label("purpose", "session")
                .tag("session-store"))
    
    def analytics_database(self):
        """Configure for analytics workloads"""
        return (self.postgresql()
                .size("db-s-4vcpu-8gb")
                .label("purpose", "analytics")
                .tag("analytics"))
    
    def web_app_database(self):
        """Configure for web application"""
        return (self.postgresql()
                .backup_enabled(True)
                .label("purpose", "web-app")
                .tag("web-application"))
    
    def microservice_database(self):
        """Configure for microservice"""
        return (self.postgresql()
                .size("db-s-2vcpu-4gb")
                .label("purpose", "microservice")
                .tag("microservice"))
    
    # Environment-specific presets
    def small_app(self):
        """Small application database"""
        return (self.postgresql()
                .size("db-s-1vcpu-1gb")
                .nodes(1)
                .label("size", "small"))
    
    def medium_app(self):
        """Medium application database"""
        return (self.postgresql()
                .size("db-s-2vcpu-4gb")
                .nodes(1)
                .backup_enabled(True)
                .label("size", "medium"))
    
    def large_app(self):
        """Large application database"""
        return (self.postgresql()
                .size("db-s-4vcpu-8gb")
                .nodes(2)
                .backup_enabled(True)
                .point_in_time_recovery(True)
                .monitoring(True)
                .label("size", "large"))
    
    def enterprise_app(self):
        """Enterprise application database"""
        return (self.postgresql()
                .size("db-s-8vcpu-32gb")
                .nodes(3)
                .backup_enabled(True)
                .point_in_time_recovery(True)
                .monitoring(True)
                .alerts(True)
                .label("size", "enterprise"))
    
    # Security configurations
    def secure_database(self):
        """Apply security best practices"""
        return (self.backup_enabled(True)
                .point_in_time_recovery(True)
                .monitoring(True)
                .alerts(True)
                .label("security", "high"))
    
    def public_database(self):
        """Configure for public access (development only)"""
        return (self.add_trusted_source("0.0.0.0/0")
                .label("access", "public")
                .tag("public-access"))
    
    def private_database(self):
        """Configure for private network access only"""
        return (self.label("access", "private")
                .tag("private-access"))
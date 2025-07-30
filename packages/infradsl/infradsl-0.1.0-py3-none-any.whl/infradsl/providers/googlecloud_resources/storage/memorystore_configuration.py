"""
GCP Memorystore Configuration Mixin

Chainable configuration methods for Google Cloud Memorystore Redis.
Provides Rails-like method chaining for fluent cache configuration.
"""

from typing import Dict, Any, List, Optional, Union


class MemorystoreConfigurationMixin:
    """
    Mixin for Memorystore configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Memory and performance configuration
    - Security settings (authentication, encryption)
    - Persistence and backup configuration
    - Read replicas and high availability
    - Redis parameter tuning
    - Network and maintenance settings
    - Common caching patterns and architectures
    """
    
    def description(self, description: str):
        """Set instance description"""
        self.instance_description = description
        return self
        
    def project(self, project_id: str):
        """Set project ID for Memorystore operations - Rails convenience"""
        self.project_id = project_id
        if self.project_id and self.region:
            self.instance_name = f"projects/{self.project_id}/locations/{self.region}/instances/{self.instance_id}"
        return self
        
    # Memory and performance configuration
    def memory_size(self, size_gb: int):
        """Set memory size in GB - chainable"""
        if not self._is_valid_memory_size(size_gb):
            print(f"⚠️  Warning: Invalid memory size '{size_gb}GB'. Must be between 1-300GB.")
        self.memory_size_gb = size_gb
        return self
        
    def memory(self, size_gb: int):
        """Alias for memory_size - Rails convenience"""
        return self.memory_size(size_gb)
    
    # Tier configuration
    def basic(self):
        """Configure for basic tier (single node) - chainable"""
        self.tier = 'BASIC'
        return self
        
    def standard_ha(self):
        """Configure for standard HA tier (high availability) - chainable"""
        self.tier = 'STANDARD_HA'
        return self
        
    def high_availability(self):
        """Alias for standard_ha - Rails convenience"""
        return self.standard_ha()
    
    # Redis version configuration
    def redis_version(self, version: str):
        """Set Redis version - chainable"""
        if not self._is_valid_redis_version(version):
            print(f"⚠️  Warning: Invalid Redis version '{version}'")
        self.redis_version = version.upper()
        return self
        
    def redis_7(self):
        """Use Redis 7.0 - Rails convenience"""
        return self.redis_version('REDIS_7_0')
        
    def redis_6(self):
        """Use Redis 6.x - Rails convenience"""
        return self.redis_version('REDIS_6_X')
        
    def redis_5(self):
        """Use Redis 5.0 - Rails convenience"""
        return self.redis_version('REDIS_5_0')
    
    # Location configuration
    def region(self, region: str):
        """Set region - chainable"""
        self.region = region
        if self.project_id and self.region:
            self.instance_name = f"projects/{self.project_id}/locations/{self.region}/instances/{self.instance_id}"
        return self
        
    def zone(self, zone: str):
        """Set zone (for basic tier) - chainable"""
        self.zone = zone
        return self
        
    def location(self, region: str, zone: str = None):
        """Set both region and zone - Rails convenience"""
        self.region(region)
        if zone:
            self.zone(zone)
        return self
    
    # Authentication configuration
    def auth_enabled(self, enabled: bool = True):
        """Enable/disable Redis AUTH - chainable"""
        self.auth_enabled = enabled
        return self
        
    def auth(self, enabled: bool = True):
        """Alias for auth_enabled - Rails convenience"""
        return self.auth_enabled(enabled)
        
    def no_auth(self):
        """Disable authentication - Rails convenience"""
        return self.auth_enabled(False)
        
    def auth_string(self, auth_string: str):
        """Set custom AUTH string - chainable"""
        self.auth_string = auth_string
        self.auth_enabled = True
        return self
    
    # Encryption configuration
    def encryption(self, mode: str = 'SERVER_AUTHENTICATION'):
        """Configure transit encryption - chainable"""
        valid_modes = ['DISABLED', 'SERVER_AUTHENTICATION']
        if mode.upper() not in valid_modes:
            print(f"⚠️  Warning: Invalid encryption mode '{mode}'. Valid: {valid_modes}")
        self.transit_encryption_mode = mode.upper()
        return self
        
    def encrypted(self):
        """Enable server authentication encryption - Rails convenience"""
        return self.encryption('SERVER_AUTHENTICATION')
        
    def no_encryption(self):
        """Disable transit encryption - chainable"""
        self.transit_encryption_mode = 'DISABLED'
        return self
    
    # Network configuration
    def network(self, network_name: str):
        """Set authorized network - chainable"""
        if not network_name.startswith('projects/'):
            self.authorized_network = f"projects/{self.project_id or 'PROJECT_ID'}/global/networks/{network_name}"
        else:
            self.authorized_network = network_name
        return self
        
    def vpc(self, network_name: str):
        """Alias for network - Rails convenience"""
        return self.network(network_name)
        
    def ip_range(self, cidr_range: str):
        """Set reserved IP range - chainable"""
        self.reserved_ip_range = cidr_range
        return self
        
    def private_ip(self, cidr_range: str):
        """Alias for ip_range - Rails convenience"""
        return self.ip_range(cidr_range)
    
    # Persistence configuration
    def persistence(self, enabled: bool = True, backup_schedule: str = "0 2 * * *"):
        """Configure Redis persistence - chainable"""
        if enabled:
            self.persistence_config = {
                'persistence_mode': 'RDB',
                'rdb_snapshot_period': 'TWENTY_FOUR_HOURS',
                'rdb_snapshot_start_time': backup_schedule
            }
        else:
            self.persistence_config = {'persistence_mode': 'DISABLED'}
        return self
        
    def enable_persistence(self, backup_schedule: str = "0 2 * * *"):
        """Enable persistence - Rails convenience"""
        return self.persistence(True, backup_schedule)
        
    def disable_persistence(self):
        """Disable persistence - Rails convenience"""
        return self.persistence(False)
        
    def backup_schedule(self, schedule: str):
        """Set backup schedule - Rails convenience"""
        if self.persistence_config.get('persistence_mode') != 'DISABLED':
            self.persistence_config['rdb_snapshot_start_time'] = schedule
        return self
        
    def daily_backup(self, hour: int = 2):
        """Daily backup at specified hour - Rails convenience"""
        return self.backup_schedule(f"0 {hour} * * *")
        
    def weekly_backup(self, day: str = "sunday", hour: int = 2):
        """Weekly backup - Rails convenience"""
        day_map = {
            'sunday': 0, 'monday': 1, 'tuesday': 2, 'wednesday': 3,
            'thursday': 4, 'friday': 5, 'saturday': 6
        }
        day_num = day_map.get(day.lower(), 0)
        return self.backup_schedule(f"0 {hour} * * {day_num}")
    
    # Maintenance configuration
    def maintenance_window(self, day: str, hour: int = 2):
        """Set maintenance window - chainable"""
        self.maintenance_policy = {
            'weekly_maintenance_window': [{
                'day': day.upper(),
                'start_time': {
                    'hours': hour,
                    'minutes': 0
                }
            }]
        }
        return self
        
    def maintenance_sunday(self, hour: int = 2):
        """Sunday maintenance window - Rails convenience"""
        return self.maintenance_window("SUNDAY", hour)
        
    def maintenance_saturday(self, hour: int = 2):
        """Saturday maintenance window - Rails convenience"""
        return self.maintenance_window("SATURDAY", hour)
    
    # Redis configuration
    def redis_config(self, key: str, value: str):
        """Set Redis configuration parameter - chainable"""
        self.redis_configs[key] = value
        return self
        
    def redis_configs(self, configs: Dict[str, str]):
        """Set multiple Redis configuration parameters - chainable"""
        self.redis_configs.update(configs)
        return self
        
    def max_memory_policy(self, policy: str = 'allkeys-lru'):
        """Set max memory policy - Rails convenience"""
        valid_policies = ['noeviction', 'allkeys-lru', 'volatile-lru', 'allkeys-random', 
                         'volatile-random', 'volatile-ttl', 'allkeys-lfu', 'volatile-lfu']
        if policy not in valid_policies:
            print(f"⚠️  Warning: Invalid max memory policy '{policy}'. Valid: {valid_policies}")
        return self.redis_config('maxmemory-policy', policy)
        
    def timeout(self, seconds: int = 0):
        """Set client timeout - Rails convenience"""
        return self.redis_config('timeout', str(seconds))
        
    def save_disabled(self):
        """Disable Redis SAVE - Rails convenience"""
        return self.redis_config('save', '')
    
    # Read replicas configuration
    def read_replicas(self, count: int = 1):
        """Enable read replicas - chainable"""
        if count > 0:
            self.read_replicas_mode = 'READ_REPLICAS_ENABLED'
            self.replica_count = count
        else:
            self.read_replicas_mode = 'READ_REPLICAS_DISABLED'
            self.replica_count = 0
        return self
        
    def enable_read_replicas(self, count: int = 1):
        """Enable read replicas - Rails convenience"""
        return self.read_replicas(count)
        
    def disable_read_replicas(self):
        """Disable read replicas - Rails convenience"""
        return self.read_replicas(0)
    
    # Labels and metadata
    def labels(self, labels: Dict[str, str]):
        """Add labels to the instance"""
        self.instance_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.instance_labels[key] = value
        return self
        
    def annotations(self, annotations: Dict[str, str]):
        """Add annotations to the instance"""
        self.instance_annotations.update(annotations)
        return self
        
    def annotation(self, key: str, value: str):
        """Add individual annotation - Rails convenience"""
        self.instance_annotations[key] = value
        return self
    
    # Common caching patterns
    def session_store(self):
        """Rails convenience: Configure for session storage"""
        return (self.memory_size(1)
                .standard_ha()
                .auth_enabled(True)
                .encrypted()
                .persistence(True)
                .label("purpose", "session-store")
                .label("critical", "high"))
                
    def application_cache(self):
        """Rails convenience: Configure for application caching"""
        return (self.memory_size(2)
                .standard_ha()
                .auth_enabled(True)
                .encrypted()
                .disable_persistence()  # Cache doesn't need persistence
                .max_memory_policy('allkeys-lru')
                .label("purpose", "app-cache")
                .label("critical", "medium"))
                
    def high_performance_cache(self):
        """Rails convenience: Configure for high-performance caching"""
        return (self.memory_size(16)
                .standard_ha()
                .auth_enabled(True)
                .encrypted()
                .read_replicas(2)
                .redis_configs({
                    'maxmemory-policy': 'allkeys-lru',
                    'timeout': '0'
                })
                .label("purpose", "high-performance")
                .label("critical", "high"))
                
    def simple_cache(self):
        """Rails convenience: Simple single-node cache"""
        return (self.memory_size(1)
                .basic()
                .auth_enabled(True)
                .max_memory_policy('allkeys-lru')
                .label("purpose", "simple-cache")
                .label("environment", "development"))
                
    def microservice_cache(self):
        """Rails convenience: Cache for microservices"""
        return (self.memory_size(4)
                .standard_ha()
                .auth_enabled(True)
                .encrypted()
                .read_replicas(1)
                .label("purpose", "microservice-cache")
                .label("pattern", "microservices"))
                
    def analytics_cache(self):
        """Rails convenience: Cache for analytics and real-time data"""
        return (self.memory_size(32)
                .standard_ha()
                .auth_enabled(True)
                .encrypted()
                .read_replicas(3)
                .persistence(True)
                .redis_configs({
                    'maxmemory-policy': 'volatile-lru',
                    'timeout': '300'  # 5 minute timeout
                })
                .label("purpose", "analytics")
                .label("data_type", "real_time"))
    
    # Environment-specific configurations
    def development(self):
        """Configure for development environment - Rails convention"""
        return (self.basic()
                .memory_size(1)
                .no_auth()
                .no_encryption()
                .disable_persistence()
                .label("environment", "development"))
                
    def staging(self):
        """Configure for staging environment - Rails convention"""
        return (self.standard_ha()
                .memory_size(2)
                .auth_enabled(True)
                .encrypted()
                .disable_persistence()
                .label("environment", "staging"))
                
    def production(self):
        """Configure for production environment - Rails convention"""
        return (self.standard_ha()
                .memory_size(8)
                .auth_enabled(True)
                .encrypted()
                .persistence(True)
                .read_replicas(1)
                .maintenance_sunday(3)
                .label("environment", "production"))
    
    # Performance patterns
    def low_latency(self):
        """Optimize for low latency - Rails convenience"""
        return (self.redis_configs({
                    'tcp-keepalive': '60',
                    'timeout': '0'
                })
                .label("optimization", "low_latency"))
                
    def high_throughput(self):
        """Optimize for high throughput - Rails convenience"""
        return (self.read_replicas(2)
                .redis_configs({
                    'maxmemory-policy': 'allkeys-lru',
                    'tcp-keepalive': '300'
                })
                .label("optimization", "high_throughput"))
                
    def memory_optimized(self):
        """Optimize for memory efficiency - Rails convenience"""
        return (self.redis_configs({
                    'maxmemory-policy': 'allkeys-lfu',
                    'hash-max-ziplist-entries': '512',
                    'hash-max-ziplist-value': '64'
                })
                .label("optimization", "memory_optimized"))
    
    # Security patterns
    def high_security(self):
        """Configure for high security requirements"""
        return (self.auth_enabled(True)
                .encrypted()
                .label("security", "high")
                .label("compliance", "required"))
                
    def compliance_ready(self):
        """Configure for compliance requirements"""
        return (self.high_security()
                .persistence(True)
                .label("compliance", "sox_pci")
                .label("audit", "required")
                .label("encryption", "required"))
                
    def enterprise_grade(self):
        """Configure for enterprise requirements"""
        return (self.production()
                .high_security()
                .compliance_ready()
                .label("tier", "enterprise"))
    
    # Industry-specific patterns
    def ecommerce_cache(self):
        """Rails convenience: E-commerce session and cart cache"""
        return (self.session_store()
                .memory_size(4)
                .read_replicas(1)
                .compliance_ready()
                .label("industry", "ecommerce")
                .label("data_type", "session_cart"))
                
    def gaming_cache(self):
        """Rails convenience: Gaming leaderboard and session cache"""
        return (self.high_performance_cache()
                .memory_size(8)
                .redis_configs({
                    'maxmemory-policy': 'volatile-lru',
                    'timeout': '0'
                })
                .label("industry", "gaming")
                .label("data_type", "leaderboard"))
                
    def financial_cache(self):
        """Rails convenience: Financial data cache"""
        return (self.enterprise_grade()
                .memory_size(16)
                .redis_configs({
                    'maxmemory-policy': 'noeviction',  # Never evict financial data
                    'timeout': '0'
                })
                .label("industry", "financial")
                .label("data_sensitivity", "high"))
                
    def iot_cache(self):
        """Rails convenience: IoT sensor data cache"""
        return (self.analytics_cache()
                .memory_size(64)
                .redis_configs({
                    'maxmemory-policy': 'volatile-ttl',
                    'timeout': '0'
                })
                .label("industry", "iot")
                .label("data_type", "sensor_telemetry"))
    
    # Utility methods
    def clear_configs(self):
        """Clear all Redis configurations"""
        self.redis_configs = {}
        return self
        
    def clear_labels(self):
        """Clear all labels"""
        self.instance_labels = {}
        return self
        
    def get_config_count(self) -> int:
        """Get the number of Redis configurations"""
        return len(self.redis_configs)
        
    def get_label_count(self) -> int:
        """Get the number of labels"""
        return len(self.instance_labels)
        
    def has_persistence(self) -> bool:
        """Check if persistence is enabled"""
        return self.persistence_config.get('persistence_mode', 'DISABLED') != 'DISABLED'
        
    def has_read_replicas(self) -> bool:
        """Check if read replicas are enabled"""
        return self.read_replicas_mode == 'READ_REPLICAS_ENABLED'
        
    def has_encryption(self) -> bool:
        """Check if encryption is enabled"""
        return self.transit_encryption_mode != 'DISABLED'
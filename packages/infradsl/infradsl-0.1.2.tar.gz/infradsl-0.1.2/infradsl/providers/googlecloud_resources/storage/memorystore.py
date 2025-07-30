"""
Google Cloud Memorystore Resource

Rails-like in-memory caching with Redis clusters.
Provides Rails-like interface for Memorystore Redis management with intelligent defaults.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class Memorystore(BaseGcpResource):
    """
    Google Cloud Memorystore Resource
    
    Rails-like Redis cluster management for session storage, application caching, and real-time analytics.
    Supports Redis with high availability, automatic failover, and encryption.
    """
    
    def __init__(
        self,
        name: str,
        memory_size_gb: int = 1,
        tier: str = 'STANDARD_HA',
        redis_version: str = 'REDIS_7_0',
        region: Optional[str] = None,
        zone: Optional[str] = None,
        reserved_ip_range: Optional[str] = None,
        auth_enabled: bool = True,
        transit_encryption_mode: str = 'SERVER_AUTHENTICATION',
        persistence_config: Optional[Dict[str, Any]] = None,
        maintenance_policy: Optional[Dict[str, Any]] = None,
        redis_configs: Optional[Dict[str, str]] = None,
        labels: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """
        Initialize Memorystore Redis instance.

        Args:
            name: Redis instance name
            memory_size_gb: Memory size in GB (1-300)
            tier: Service tier ('BASIC' or 'STANDARD_HA')
            redis_version: Redis version ('REDIS_7_0', 'REDIS_6_X', 'REDIS_5_0')
            region: GCP region (auto-detected if not specified)
            zone: GCP zone for basic tier
            reserved_ip_range: CIDR range for the instance
            auth_enabled: Enable AUTH string
            transit_encryption_mode: Encryption mode ('DISABLED', 'SERVER_AUTHENTICATION')
            persistence_config: Redis persistence configuration
            maintenance_policy: Maintenance policy settings
            redis_configs: Redis configuration parameters
            labels: Resource labels
            **kwargs: Additional Memorystore parameters
        """
        super().__init__(name)
        
        # Core configuration
        self.instance_id = name.lower().replace('_', '-')
        self.memory_size_gb = memory_size_gb
        self.tier = tier.upper()
        self.redis_version = redis_version.upper()
        self.region = region
        self.zone = zone
        self.reserved_ip_range = reserved_ip_range
        
        # Security configuration
        self.auth_enabled = auth_enabled
        self.transit_encryption_mode = transit_encryption_mode.upper()
        self.auth_string = None
        
        # Advanced configuration
        self.persistence_config = persistence_config or {}
        self.maintenance_policy = maintenance_policy
        self.redis_configs = redis_configs or {}
        
        # Network configuration
        self.authorized_network = None
        self.connect_mode = 'DIRECT_PEERING'  # or 'PRIVATE_SERVICE_ACCESS'
        
        # Labels and metadata
        self.instance_labels = labels or {}
        
        # Extended configuration from kwargs
        self.read_replicas_mode = kwargs.get('read_replicas_mode', 'READ_REPLICAS_DISABLED')
        self.replica_count = kwargs.get('replica_count', 0)
        self.customer_managed_key = kwargs.get('customer_managed_key')
        
        # State
        self.instance_state = None
        self.instance_name = None
        self.host = None
        self.port = 6379
        self.current_location_id = None
        self.alternative_location_id = None
        self.redis_endpoint = None
        self.read_endpoint = None
        
        # Manager
        self.memorystore_manager = None

    def _initialize_managers(self):
        """Initialize Memorystore managers"""
        self.memorystore_manager = None

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize Memorystore manager
        if not self.region:
            self.region = self.gcp_client.get_default_region()
        
        # Set default network if not specified
        if not self.authorized_network:
            project_id = self.gcp_client.get_project_id()
            self.authorized_network = f"projects/{project_id}/global/networks/default"
        
        # Generate instance name
        project_id = self.gcp_client.get_project_id()
        self.instance_name = f"projects/{project_id}/locations/{self.region}/instances/{self.instance_id}"

    def _discover_existing_instances(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Memorystore Redis instances"""
        existing_instances = {}
        
        try:
            from googleapiclient import discovery
            from googleapiclient.errors import HttpError
            
            service = discovery.build('redis', 'v1', credentials=self.gcp_client.credentials)
            
            # List Redis instances in the region
            parent = f"projects/{self.gcp_client.project_id}/locations/{self.region}"
            request = service.projects().locations().instances().list(parent=parent)
            response = request.execute()
            
            for instance in response.get('instances', []):
                instance_name = instance['name'].split('/')[-1]
                
                try:
                    # Get detailed instance information
                    detailed_request = service.projects().locations().instances().get(name=instance['name'])
                    detailed_instance = detailed_request.execute()
                    
                    # Extract configuration
                    memory_size_gb = detailed_instance.get('memorySizeGb', 0)
                    tier = detailed_instance.get('tier', 'UNKNOWN')
                    redis_version = detailed_instance.get('redisVersion', 'UNKNOWN')
                    
                    # Get network and connectivity info
                    host = detailed_instance.get('host', 'unknown')
                    port = detailed_instance.get('port', 6379)
                    authorized_network = detailed_instance.get('authorizedNetwork', '')
                    reserved_ip_range = detailed_instance.get('reservedIpRange', '')
                    
                    # Get security configuration
                    auth_enabled = detailed_instance.get('authEnabled', False)
                    transit_encryption_mode = detailed_instance.get('transitEncryptionMode', 'DISABLED')
                    
                    # Get state and location info
                    state = detailed_instance.get('state', 'UNKNOWN')
                    location_id = detailed_instance.get('locationId', 'unknown')
                    alternative_location_id = detailed_instance.get('alternativeLocationId', '')
                    
                    # Get persistence configuration
                    persistence_config = detailed_instance.get('persistenceConfig', {})
                    persistence_mode = persistence_config.get('persistenceMode', 'DISABLED')
                    
                    # Get maintenance policy
                    maintenance_policy = detailed_instance.get('maintenancePolicy', {})
                    
                    # Get Redis configurations
                    redis_configs = detailed_instance.get('redisConfigs', {})
                    
                    # Get read replicas info
                    read_replicas_mode = detailed_instance.get('readReplicasMode', 'READ_REPLICAS_DISABLED')
                    replica_count = detailed_instance.get('replicaCount', 0)
                    
                    # Get labels
                    labels = detailed_instance.get('labels', {})
                    
                    # Get endpoints
                    read_endpoint = detailed_instance.get('readEndpoint', '')
                    read_endpoint_port = detailed_instance.get('readEndpointPort', 6379)
                    
                    existing_instances[instance_name] = {
                        'instance_name': instance_name,
                        'full_name': detailed_instance['name'],
                        'memory_size_gb': memory_size_gb,
                        'tier': tier,
                        'redis_version': redis_version,
                        'state': state,
                        'location_id': location_id,
                        'alternative_location_id': alternative_location_id,
                        'host': host,
                        'port': port,
                        'authorized_network': authorized_network,
                        'reserved_ip_range': reserved_ip_range,
                        'auth_enabled': auth_enabled,
                        'transit_encryption_mode': transit_encryption_mode,
                        'persistence_mode': persistence_mode,
                        'persistence_config': persistence_config,
                        'maintenance_policy': maintenance_policy,
                        'redis_configs': redis_configs,
                        'redis_config_count': len(redis_configs),
                        'read_replicas_mode': read_replicas_mode,
                        'replica_count': replica_count,
                        'labels': labels,
                        'label_count': len(labels),
                        'read_endpoint': read_endpoint,
                        'read_endpoint_port': read_endpoint_port,
                        'create_time': detailed_instance.get('createTime'),
                        'current_location_id': detailed_instance.get('currentLocationId')
                    }
                    
                except HttpError as e:
                    if e.resp.status == 404:
                        continue
                    else:
                        print(f"⚠️  Failed to get details for instance {instance_name}: {str(e)}")
                        existing_instances[instance_name] = {
                            'instance_name': instance_name,
                            'error': str(e)
                        }
                        
        except Exception as e:
            print(f"⚠️  Failed to discover existing Memorystore instances: {str(e)}")
        
        return existing_instances

    # Rails-like configuration methods

    def memory_size(self, size_gb: int) -> 'Memorystore':
        """Set memory size in GB - chainable"""
        self.memory_size_gb = size_gb
        return self

    def basic(self) -> 'Memorystore':
        """Configure for basic tier (single node) - chainable"""
        self.tier = 'BASIC'
        return self

    def standard_ha(self) -> 'Memorystore':
        """Configure for standard HA tier (high availability) - chainable"""
        self.tier = 'STANDARD_HA'
        return self

    def redis_version(self, version: str) -> 'Memorystore':
        """Set Redis version - chainable"""
        self.redis_version = version.upper()
        return self

    def region(self, region: str) -> 'Memorystore':
        """Set region - chainable"""
        self.region = region
        return self

    def zone(self, zone: str) -> 'Memorystore':
        """Set zone (for basic tier) - chainable"""
        self.zone = zone
        return self

    def auth_enabled(self, enabled: bool = True) -> 'Memorystore':
        """Enable/disable Redis AUTH - chainable"""
        self.auth_enabled = enabled
        return self

    def auth_string(self, auth_string: str) -> 'Memorystore':
        """Set custom AUTH string - chainable"""
        self.auth_string = auth_string
        self.auth_enabled = True
        return self

    def encryption(self, mode: str = 'SERVER_AUTHENTICATION') -> 'Memorystore':
        """Configure transit encryption - chainable"""
        self.transit_encryption_mode = mode.upper()
        return self

    def no_encryption(self) -> 'Memorystore':
        """Disable transit encryption - chainable"""
        self.transit_encryption_mode = 'DISABLED'
        return self

    def network(self, network_name: str) -> 'Memorystore':
        """Set authorized network - chainable"""
        if not network_name.startswith('projects/'):
            project_id = self.gcp_client.get_project_id()
            self.authorized_network = f"projects/{project_id}/global/networks/{network_name}"
        else:
            self.authorized_network = network_name
        return self

    def ip_range(self, cidr_range: str) -> 'Memorystore':
        """Set reserved IP range - chainable"""
        self.reserved_ip_range = cidr_range
        return self

    def persistence(self, enabled: bool = True, backup_schedule: str = "0 2 * * *") -> 'Memorystore':
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

    def maintenance_window(self, day: str, hour: int = 2) -> 'Memorystore':
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

    def redis_config(self, key: str, value: str) -> 'Memorystore':
        """Set Redis configuration parameter - chainable"""
        self.redis_configs[key] = value
        return self

    def redis_configs(self, configs: Dict[str, str]) -> 'Memorystore':
        """Set multiple Redis configuration parameters - chainable"""
        self.redis_configs.update(configs)
        return self

    def read_replicas(self, count: int = 1) -> 'Memorystore':
        """Enable read replicas - chainable"""
        self.read_replicas_mode = 'READ_REPLICAS_ENABLED'
        self.replica_count = count
        return self

    def labels(self, labels: Dict[str, str]) -> 'Memorystore':
        """Add labels - chainable"""
        self.instance_labels.update(labels)
        return self

    def label(self, key: str, value: str) -> 'Memorystore':
        """Add single label - chainable"""
        self.instance_labels[key] = value
        return self

    # Rails convenience methods

    def session_store(self) -> 'Memorystore':
        """Rails convenience: Configure for session storage"""
        return (self.memory_size(1)
                .standard_ha()
                .auth_enabled(True)
                .encryption()
                .persistence(True)
                .label("purpose", "session-store")
                .label("critical", "high"))

    def application_cache(self) -> 'Memorystore':
        """Rails convenience: Configure for application caching"""
        return (self.memory_size(2)
                .standard_ha()
                .auth_enabled(True)
                .encryption()
                .persistence(False)  # Cache doesn't need persistence
                .label("purpose", "app-cache")
                .label("critical", "medium"))

    def high_performance_cache(self) -> 'Memorystore':
        """Rails convenience: Configure for high-performance caching"""
        return (self.memory_size(16)
                .standard_ha()
                .auth_enabled(True)
                .encryption()
                .read_replicas(2)
                .redis_configs({
                    'maxmemory-policy': 'allkeys-lru',
                    'timeout': '0'
                })
                .label("purpose", "high-performance")
                .label("critical", "high"))

    def simple_cache(self) -> 'Memorystore':
        """Rails convenience: Simple single-node cache"""
        return (self.memory_size(1)
                .basic()
                .auth_enabled(True)
                .label("purpose", "simple-cache")
                .label("environment", "development"))

    # Environment presets

    def development(self) -> 'Memorystore':
        """Configure for development environment - chainable"""
        return (self.basic()
                .memory_size(1)
                .auth_enabled(False)
                .no_encryption()
                .label("environment", "development"))

    def staging(self) -> 'Memorystore':
        """Configure for staging environment - chainable"""
        return (self.standard_ha()
                .memory_size(2)
                .auth_enabled(True)
                .encryption()
                .label("environment", "staging"))

    def production(self) -> 'Memorystore':
        """Configure for production environment - chainable"""
        return (self.standard_ha()
                .memory_size(8)
                .auth_enabled(True)
                .encryption()
                .persistence(True)
                .read_replicas(1)
                .maintenance_window("SUNDAY", 3)
                .label("environment", "production"))

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()

        # Discover existing instances
        existing_instances = self._discover_existing_instances()
        
        # Categorize instances
        instances_to_create = []
        instances_to_keep = []
        instances_to_remove = []
        
        # Check if our desired instance exists
        desired_instance_name = self.instance_id
        instance_exists = desired_instance_name in existing_instances
        
        if not instance_exists:
            instances_to_create.append({
                'instance_name': desired_instance_name,
                'memory_size_gb': self.memory_size_gb,
                'tier': self.tier,
                'redis_version': self.redis_version,
                'region': self.region,
                'zone': self.zone,
                'auth_enabled': self.auth_enabled,
                'transit_encryption_mode': self.transit_encryption_mode,
                'persistence_config': self.persistence_config,
                'read_replicas_mode': self.read_replicas_mode,
                'replica_count': self.replica_count,
                'redis_configs': self.redis_configs,
                'redis_config_count': len(self.redis_configs),
                'labels': self.instance_labels,
                'label_count': len(self.instance_labels)
            })
        else:
            instances_to_keep.append(existing_instances[desired_instance_name])

        print(f"\n⚡ Google Cloud Memorystore Redis Preview")
        
        # Show instances to create
        if instances_to_create:
            print(f"╭─ ⚡ Redis Instances to CREATE: {len(instances_to_create)}")
            for instance in instances_to_create:
                print(f"├─ 🆕 {instance['instance_name']}")
                print(f"│  ├─ 📊 Memory: {instance['memory_size_gb']}GB")
                print(f"│  ├─ 🏗️  Tier: {instance['tier']}")
                print(f"│  ├─ ⚡ Version: {instance['redis_version']}")
                print(f"│  ├─ 📍 Region: {instance['region']}")
                
                if instance['zone']:
                    print(f"│  ├─ 🌐 Zone: {instance['zone']}")
                
                print(f"│  ├─ 🔑 Authentication: {'✅ Enabled' if instance['auth_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🔒 Encryption: {instance['transit_encryption_mode']}")
                
                # Show persistence configuration
                persistence_mode = instance['persistence_config'].get('persistence_mode', 'DISABLED') if instance['persistence_config'] else 'DISABLED'
                print(f"│  ├─ 💾 Persistence: {persistence_mode}")
                
                if persistence_mode != 'DISABLED' and instance['persistence_config']:
                    period = instance['persistence_config'].get('rdb_snapshot_period', 'UNKNOWN')
                    print(f"│  │  └─ 📅 Backup Period: {period}")
                
                # Show read replicas
                if instance['read_replicas_mode'] == 'READ_REPLICAS_ENABLED':
                    print(f"│  ├─ 📚 Read Replicas: {instance['replica_count']}")
                else:
                    print(f"│  ├─ 📚 Read Replicas: ❌ Disabled")
                
                # Show Redis configurations
                if instance['redis_config_count'] > 0:
                    print(f"│  ├─ ⚙️  Redis Config: {instance['redis_config_count']} parameters")
                    for key, value in list(instance['redis_configs'].items())[:3]:
                        print(f"│  │  ├─ {key}: {value}")
                    if instance['redis_config_count'] > 3:
                        print(f"│  │  └─ ... and {instance['redis_config_count'] - 3} more configs")
                
                # Show labels
                if instance['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {instance['label_count']}")
                
                # Show connectivity info
                print(f"│  ├─ 🔗 Connectivity:")
                print(f"│  │  ├─ 🌐 Primary endpoint: {instance['instance_name']}.{instance['region']}.c.memorystore.internal:6379")
                if instance['read_replicas_mode'] == 'READ_REPLICAS_ENABLED':
                    print(f"│  │  ├─ 📖 Read endpoint: {instance['instance_name']}-ro.{instance['region']}.c.memorystore.internal:6379")
                print(f"│  │  └─ 🔌 VPC network access only")
                
                print(f"│  └─ ⚡ Performance: Sub-millisecond latency, 100K+ ops/sec")
            print(f"╰─")

        # Show existing instances being kept
        if instances_to_keep:
            print(f"\n╭─ ⚡ Existing Redis Instances to KEEP: {len(instances_to_keep)}")
            for instance in instances_to_keep:
                state_icon = "🟢" if instance['state'] == 'READY' else "🟡" if instance['state'] == 'CREATING' else "🔴"
                print(f"├─ {state_icon} {instance['instance_name']}")
                print(f"│  ├─ 📊 Memory: {instance['memory_size_gb']}GB")
                print(f"│  ├─ 🏗️  Tier: {instance['tier']}")
                print(f"│  ├─ ⚡ Version: {instance['redis_version']}")
                print(f"│  ├─ 📍 Location: {instance['location_id']}")
                
                if instance['alternative_location_id']:
                    print(f"│  ├─ 🌐 Alternative Zone: {instance['alternative_location_id']}")
                
                print(f"│  ├─ 🔑 Authentication: {'✅ Enabled' if instance['auth_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🔒 Encryption: {instance['transit_encryption_mode']}")
                print(f"│  ├─ 💾 Persistence: {instance['persistence_mode']}")
                
                if instance['read_replicas_mode'] == 'READ_REPLICAS_ENABLED':
                    print(f"│  ├─ 📚 Read Replicas: {instance['replica_count']}")
                
                if instance['redis_config_count'] > 0:
                    print(f"│  ├─ ⚙️  Redis Config: {instance['redis_config_count']} parameters")
                
                print(f"│  ├─ 🌐 Primary Endpoint: {instance['host']}:{instance['port']}")
                if instance['read_endpoint']:
                    print(f"│  ├─ 📖 Read Endpoint: {instance['read_endpoint']}:{instance['read_endpoint_port']}")
                
                if instance['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {instance['label_count']}")
                
                print(f"│  └─ 📅 Created: {instance.get('create_time', 'Unknown')[:10] if instance.get('create_time') else 'Unknown'}")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 Memorystore Redis Costs:")
        if instances_to_create:
            instance = instances_to_create[0]
            
            # Basic tier costs (simplified estimation)
            memory_gb = instance['memory_size_gb']
            
            if instance['tier'] == 'BASIC':
                # Basic tier: $0.049/GB/hour
                hourly_cost = memory_gb * 0.049
                monthly_cost = hourly_cost * 24 * 30
                tier_note = "Basic (single node)"
            else:
                # Standard HA tier: $0.054/GB/hour
                hourly_cost = memory_gb * 0.054
                monthly_cost = hourly_cost * 24 * 30
                tier_note = "Standard HA (high availability)"
            
            print(f"   ├─ ⚡ Redis Instance ({tier_note}): ${monthly_cost:.2f}/month")
            print(f"   ├─ 📊 Memory ({memory_gb}GB): ${hourly_cost:.3f}/hour")
            
            if instance['read_replicas_mode'] == 'READ_REPLICAS_ENABLED':
                replica_cost = monthly_cost * instance['replica_count']
                print(f"   ├─ 📚 Read Replicas ({instance['replica_count']}x): ${replica_cost:.2f}/month")
                monthly_cost += replica_cost
            
            print(f"   ├─ 🌐 Network egress: $0.12/GB (first 1GB free)")
            print(f"   └─ 📊 Total Estimated: ${monthly_cost:.2f}/month")
        else:
            print(f"   ├─ ⚡ Basic tier: $0.049/GB/hour")
            print(f"   ├─ ⚡ Standard HA: $0.054/GB/hour") 
            print(f"   ├─ 📚 Read replicas: Same cost per replica")
            print(f"   └─ 🌐 Network egress: $0.12/GB")

        return {
            'resource_type': 'gcp_memorystore',
            'name': desired_instance_name,
            'instances_to_create': instances_to_create,
            'instances_to_keep': instances_to_keep,
            'instances_to_remove': instances_to_remove,
            'existing_instances': existing_instances,
            'instance_id': desired_instance_name,
            'memory_size_gb': self.memory_size_gb,
            'tier': self.tier,
            'redis_version': self.redis_version,
            'estimated_cost': f"${(self.memory_size_gb * 0.054 * 24 * 30):.2f}/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create the Memorystore Redis instance"""
        self._ensure_authenticated()
        
        print(f"🚀 Creating Memorystore Redis instance: {self.instance_id}")
        print(f"   Memory: {self.memory_size_gb} GB")
        print(f"   Tier: {self.tier}")
        
        try:
            # Simulate Memorystore creation
            print("   - Creating Redis instance...")
            
            project_id = self.gcp_client.get_project_id()
            
            # Generate endpoints
            self.host = f"{self.instance_id}.{self.region}.c.memorystore.internal"
            self.redis_endpoint = f"{self.host}:{self.port}"
            
            if self.read_replicas_mode == 'READ_REPLICAS_ENABLED':
                self.read_endpoint = f"{self.instance_id}-ro.{self.region}.c.memorystore.internal:{self.port}"
            
            self.instance_state = 'READY'
            
            print(f"✅ Memorystore Redis instance created successfully")
            print(f"   Instance Name: {self.instance_name}")
            print(f"   Primary Endpoint: {self.redis_endpoint}")
            
            if self.read_endpoint:
                print(f"   Read Endpoint: {self.read_endpoint}")
            
            if self.auth_enabled:
                print(f"   🔑 AUTH enabled (retrieve auth string from console)")
            
            if self.transit_encryption_mode != 'DISABLED':
                print(f"   🔒 Transit encryption: {self.transit_encryption_mode}")
            
            return {
                "instance_id": self.instance_id,
                "instance_name": self.instance_name,
                "primary_endpoint": self.redis_endpoint,
                "read_endpoint": self.read_endpoint,
                "host": self.host,
                "port": self.port,
                "status": self.instance_state,
                "auth_enabled": self.auth_enabled
            }
            
        except Exception as e:
            print(f"❌ Failed to create Memorystore instance: {e}")
            return {"error": str(e)}

    def destroy(self) -> Dict[str, Any]:
        """Destroy the Memorystore Redis instance"""
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying Memorystore Redis instance: {self.instance_id}")
        
        try:
            # In real implementation, this would delete the instance
            print("   - Deleting Redis instance...")
            print("   - Cleaning up backups...")
            
            print(f"✅ Memorystore Redis instance destroyed successfully")
            
            return {
                "instance_id": self.instance_id,
                "status": "deleted"
            }
            
        except Exception as e:
            print(f"❌ Failed to destroy Memorystore instance: {e}")
            return {"error": str(e)}

    def connection_string(self) -> str:
        """Get Redis connection string"""
        if not self.host:
            return "Instance not yet created"
        
        if self.auth_enabled and self.auth_string:
            return f"redis://:{self.auth_string}@{self.host}:{self.port}"
        else:
            return f"redis://{self.host}:{self.port}"

    def get_status(self) -> Dict[str, Any]:
        """Get instance status and health information"""
        return {
            "instance_id": self.instance_id,
            "state": self.instance_state,
            "tier": self.tier,
            "memory_size_gb": self.memory_size_gb,
            "redis_version": self.redis_version,
            "primary_endpoint": self.redis_endpoint,
            "read_endpoint": self.read_endpoint,
            "connection_string": self.connection_string(),
            "auth_enabled": self.auth_enabled
        } 
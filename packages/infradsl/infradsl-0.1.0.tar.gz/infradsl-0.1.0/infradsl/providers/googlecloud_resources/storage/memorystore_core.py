"""
GCP Memorystore Core Implementation

Core attributes and authentication for Google Cloud Memorystore Redis.
Provides the foundation for the modular Redis cache management system.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class MemorystoreCore(BaseGcpResource):
    """
    Core class for Google Cloud Memorystore functionality.
    
    This class provides:
    - Basic Memorystore attributes and configuration
    - Authentication setup
    - Common utilities for Redis operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """Initialize Memorystore core with instance name"""
        super().__init__(name)
        
        # Core instance attributes
        self.instance_id = name.lower().replace('_', '-')
        self.instance_name = None
        self.memory_size_gb = 1
        self.tier = 'STANDARD_HA'  # BASIC or STANDARD_HA
        self.redis_version = 'REDIS_7_0'
        self.instance_description = f"Redis instance for {name}"
        
        # Location configuration
        self.region = None
        self.zone = None
        self.current_location_id = None
        self.alternative_location_id = None
        
        # Network configuration
        self.authorized_network = None
        self.reserved_ip_range = None
        self.connect_mode = 'DIRECT_PEERING'  # or 'PRIVATE_SERVICE_ACCESS'
        
        # Security configuration
        self.auth_enabled = True
        self.auth_string = None
        self.transit_encryption_mode = 'SERVER_AUTHENTICATION'  # DISABLED, SERVER_AUTHENTICATION
        self.customer_managed_key = None
        
        # Persistence configuration
        self.persistence_config = {}
        
        # Maintenance configuration
        self.maintenance_policy = None
        
        # Redis configuration
        self.redis_configs = {}
        
        # Read replicas configuration
        self.read_replicas_mode = 'READ_REPLICAS_DISABLED'
        self.replica_count = 0
        
        # Labels and metadata
        self.instance_labels = {}
        self.instance_annotations = {}
        
        # State tracking
        self.instance_exists = False
        self.instance_created = False
        self.instance_state = None
        self.deployment_status = None
        
        # Connection details
        self.host = None
        self.port = 6379
        self.redis_endpoint = None
        self.read_endpoint = None
        self.read_endpoint_port = 6379
        
        # Client references
        self.memorystore_client = None
        
        # Estimated costs
        self.estimated_monthly_cost = "$40.00/month"
        
    def _initialize_managers(self):
        """Initialize Memorystore-specific managers"""
        self.memorystore_client = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            from googleapiclient import discovery
            
            # Initialize client
            self.memorystore_client = discovery.build(
                'redis', 
                'v1', 
                credentials=self.gcp_client.credentials
            )
            
            # Set project context
            self.project_id = self.project_id or self.gcp_client.project_id
            
            # Set default region if not specified
            if not self.region:
                self.region = self.gcp_client.get_default_region()
            
            # Set default network if not specified
            if not self.authorized_network:
                self.authorized_network = f"projects/{self.project_id}/global/networks/default"
            
            # Generate resource names
            if self.project_id:
                self.instance_name = f"projects/{self.project_id}/locations/{self.region}/instances/{self.instance_id}"
                
        except Exception as e:
            print(f"⚠️  Failed to initialize Memorystore client: {str(e)}")
            
    def _is_valid_instance_name(self, name: str) -> bool:
        """Check if instance name is valid"""
        import re
        # Instance names must contain only lowercase letters, numbers, dashes
        pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
        return bool(re.match(pattern, name)) and 1 <= len(name) <= 40
        
    def _is_valid_memory_size(self, size_gb: int) -> bool:
        """Check if memory size is valid"""
        return 1 <= size_gb <= 300
        
    def _is_valid_redis_version(self, version: str) -> bool:
        """Check if Redis version is valid"""
        valid_versions = ["REDIS_7_0", "REDIS_6_X", "REDIS_5_0"]
        return version.upper() in valid_versions
        
    def _is_valid_tier(self, tier: str) -> bool:
        """Check if tier is valid"""
        valid_tiers = ["BASIC", "STANDARD_HA"]
        return tier.upper() in valid_tiers
        
    def _validate_instance_config(self, config: Dict[str, Any]) -> bool:
        """Validate instance configuration"""
        required_fields = ["instance_id", "memory_size_gb", "tier"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate instance name format
        if not self._is_valid_instance_name(config["instance_id"]):
            return False
            
        # Validate memory size
        if not self._is_valid_memory_size(config["memory_size_gb"]):
            return False
            
        # Validate tier
        if not self._is_valid_tier(config["tier"]):
            return False
            
        # Validate Redis version if provided
        if "redis_version" in config and not self._is_valid_redis_version(config["redis_version"]):
            return False
            
        return True
        
    def _get_instance_type_from_config(self) -> str:
        """Determine instance type from configuration"""
        labels = self.instance_labels
        
        # Check for purpose-based types
        purpose = labels.get("purpose", "").lower()
        if purpose:
            if "session" in purpose:
                return "session_store"
            elif "cache" in purpose:
                if "high-performance" in purpose:
                    return "high_performance_cache"
                elif "simple" in purpose:
                    return "simple_cache"
                else:
                    return "application_cache"
        
        # Check environment
        environment = labels.get("environment", "").lower()
        if environment:
            if environment == "development":
                return "development"
            elif environment == "staging":
                return "staging"
            elif environment == "production":
                return "production"
        
        # Check by tier and memory size
        if self.tier == "BASIC":
            if self.memory_size_gb <= 2:
                return "simple_cache"
            else:
                return "basic_cache"
        elif self.tier == "STANDARD_HA":
            if self.memory_size_gb >= 16:
                return "high_performance"
            elif self.read_replicas_mode == "READ_REPLICAS_ENABLED":
                return "read_replica_cluster"
            else:
                return "standard_ha"
        
        return "custom"
        
    def _estimate_memorystore_cost(self) -> float:
        """Estimate monthly cost for Memorystore usage"""
        # Memorystore pricing (simplified)
        
        memory_gb = self.memory_size_gb
        
        if self.tier == "BASIC":
            # Basic tier: $0.049/GB/hour
            hourly_cost = memory_gb * 0.049
        else:
            # Standard HA tier: $0.054/GB/hour
            hourly_cost = memory_gb * 0.054
        
        # Monthly cost (24 hours * 30 days)
        monthly_cost = hourly_cost * 24 * 30
        
        # Read replicas cost
        if self.read_replicas_mode == "READ_REPLICAS_ENABLED":
            replica_cost = monthly_cost * self.replica_count
            monthly_cost += replica_cost
        
        # Minimum charge
        if monthly_cost < 1.00:
            monthly_cost = 1.00
            
        return monthly_cost
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of Memorystore instance from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Check if instance exists
            try:
                request = self.memorystore_client.projects().locations().instances().get(
                    name=self.instance_name
                )
                instance = request.execute()
                instance_exists = True
            except Exception:
                instance_exists = False
                
            if not instance_exists:
                return {
                    "exists": False,
                    "instance_id": self.instance_id,
                    "instance_name": self.instance_name
                }
                
            # Get instance details
            current_state = {
                "exists": True,
                "instance_id": self.instance_id,
                "instance_name": instance.get("name", ""),
                "display_name": instance.get("displayName", ""),
                "memory_size_gb": instance.get("memorySizeGb", 0),
                "tier": instance.get("tier", "UNKNOWN"),
                "redis_version": instance.get("redisVersion", "UNKNOWN"),
                "state": instance.get("state", "UNKNOWN"),
                "location_id": instance.get("locationId", ""),
                "alternative_location_id": instance.get("alternativeLocationId", ""),
                "host": instance.get("host", ""),
                "port": instance.get("port", 6379),
                "authorized_network": instance.get("authorizedNetwork", ""),
                "reserved_ip_range": instance.get("reservedIpRange", ""),
                "auth_enabled": instance.get("authEnabled", False),
                "transit_encryption_mode": instance.get("transitEncryptionMode", "DISABLED"),
                "persistence_config": instance.get("persistenceConfig", {}),
                "maintenance_policy": instance.get("maintenancePolicy", {}),
                "redis_configs": instance.get("redisConfigs", {}),
                "read_replicas_mode": instance.get("readReplicasMode", "READ_REPLICAS_DISABLED"),
                "replica_count": instance.get("replicaCount", 0),
                "labels": instance.get("labels", {}),
                "read_endpoint": instance.get("readEndpoint", ""),
                "read_endpoint_port": instance.get("readEndpointPort", 6379),
                "create_time": instance.get("createTime", ""),
                "current_location_id": instance.get("currentLocationId", ""),
                "redis_endpoint": f"{instance.get('host', '')}:{instance.get('port', 6379)}" if instance.get('host') else ""
            }
            
            return current_state
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch Memorystore state: {str(e)}")
            return {
                "exists": False,
                "instance_id": self.instance_id,
                "instance_name": self.instance_name,
                "error": str(e)
            }
            
    def _discover_existing_instances(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing instances in the project"""
        existing_instances = {}
        
        try:
            parent = f"projects/{self.project_id}/locations/{self.region}"
            
            # List all instances in the region
            request = self.memorystore_client.projects().locations().instances().list(
                parent=parent
            )
            response = request.execute()
            
            for instance in response.get('instances', []):
                instance_name = instance['name'].split('/')[-1]
                
                try:
                    # Get detailed instance information
                    detailed_request = self.memorystore_client.projects().locations().instances().get(
                        name=instance['name']
                    )
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
                        'current_location_id': detailed_instance.get('currentLocationId'),
                        'redis_endpoint': f"{host}:{port}" if host != 'unknown' else ""
                    }
                    
                except Exception as e:
                    print(f"⚠️  Failed to get details for instance {instance_name}: {str(e)}")
                    existing_instances[instance_name] = {
                        'instance_name': instance_name,
                        'error': str(e)
                    }
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing instances: {str(e)}")
            
        return existing_instances
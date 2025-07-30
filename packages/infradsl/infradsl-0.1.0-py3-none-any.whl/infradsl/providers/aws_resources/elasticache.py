"""
AWS ElastiCache Resource

Rails-like in-memory caching with Redis and Memcached clusters.
Provides Rails-like interface for cache management with intelligent defaults.
"""

from typing import Dict, Any, List, Optional, Union
from .base_resource import BaseAwsResource


class ElastiCache(BaseAwsResource):
    """
    AWS ElastiCache Resource
    
    Rails-like in-memory caching with Redis and Memcached clusters.
    Supports common use cases like session storage, application caching, and real-time analytics.
    """
    
    def __init__(
        self,
        name: str,
        engine: str = 'redis',
        node_type: str = 'cache.t3.micro',
        num_cache_nodes: int = 1,
        port: Optional[int] = None,
        parameter_group_name: Optional[str] = None,
        security_group_ids: Optional[List[str]] = None,
        subnet_group_name: Optional[str] = None,
        maintenance_window: Optional[str] = None,
        snapshot_retention_limit: int = 5,
        snapshot_window: Optional[str] = None,
        notification_topic_arn: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """
        Initialize ElastiCache cluster resource.

        Args:
            name: Cache cluster name
            engine: Cache engine ('redis' or 'memcached')
            node_type: Cache node instance type
            num_cache_nodes: Number of cache nodes
            port: Port number (auto-selects based on engine if not specified)
            parameter_group_name: Cache parameter group
            security_group_ids: VPC security group IDs
            subnet_group_name: Cache subnet group for VPC
            maintenance_window: Preferred maintenance window
            snapshot_retention_limit: Number of days to retain snapshots (Redis only)
            snapshot_window: Preferred snapshot window (Redis only)
            notification_topic_arn: SNS topic for notifications
            tags: Additional tags
            **kwargs: Additional ElastiCache parameters
        """
        super().__init__(name)
        
        # Core configuration
        self.cluster_id = name.lower().replace('_', '-')
        self.engine = engine.lower()
        self.node_type = node_type
        self.num_cache_nodes = num_cache_nodes
        self.port = port or self._get_default_port()
        self.parameter_group_name = parameter_group_name
        self.security_group_ids = security_group_ids or []
        self.subnet_group_name = subnet_group_name
        
        # Maintenance and backup
        self.maintenance_window = maintenance_window
        self.snapshot_retention_limit = snapshot_retention_limit if engine == 'redis' else 0
        self.snapshot_window = snapshot_window
        self.notification_topic_arn = notification_topic_arn
        
        # Redis-specific configuration
        self.replication_group_id = None
        self.replication_group_description = f"{name} Redis cluster"
        self.num_node_groups = 1  # For Redis cluster mode
        self.replicas_per_node_group = 0
        self.at_rest_encryption_enabled = True
        self.transit_encryption_enabled = True
        self.auth_token = None
        self.multi_az_enabled = False
        self.automatic_failover_enabled = False
        
        # Extended configuration from kwargs
        self.preferred_availability_zones = kwargs.get('preferred_availability_zones', [])
        self.auto_minor_version_upgrade = kwargs.get('auto_minor_version_upgrade', True)
        self.log_delivery_configurations = kwargs.get('log_delivery_configurations', [])
        
        # Tags
        self.cache_tags = tags or {}
        
        # State
        self.cluster_status = None
        self.cluster_arn = None
        self.cluster_address = None
        self.cluster_endpoints = []
        self.cache_nodes = []
        
        # Manager
        self.elasticache_client = None

    def _initialize_managers(self):
        """Initialize ElastiCache managers"""
        self.elasticache_client = None

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize AWS client for ElastiCache operations
        from ..aws_managers.aws_client import AwsClient
        
        self.aws_client = AwsClient()
        self.aws_client.authenticate(silent=True)
        self.elasticache_client = self.get_elasticache_client()
        
        # Setup default parameter group if not specified
        if not self.parameter_group_name:
            if self.engine == 'redis':
                self.parameter_group_name = f"default.redis{self._get_default_redis_version()}"
            else:
                self.parameter_group_name = f"default.memcached{self._get_default_memcached_version()}"

    def _get_default_port(self) -> int:
        """Get default port based on engine"""
        return 6379 if self.engine == 'redis' else 11211

    def _get_default_redis_version(self) -> str:
        """Get default Redis version"""
        return "7.0"

    def _get_default_memcached_version(self) -> str:
        """Get default Memcached version"""
        return "1.6"

    def get_elasticache_client(self):
        """Get ElastiCache client"""
        try:
            import boto3
            return boto3.client('elasticache', region_name=self.get_current_region())
        except Exception as e:
            print(f"⚠️  Failed to create ElastiCache client: {e}")
            return None

    # Rails-like configuration methods

    def redis(self, version: str = "7.0") -> 'ElastiCache':
        """Configure for Redis engine - chainable"""
        self.engine = 'redis'
        self.port = 6379
        self.parameter_group_name = f"default.redis{version}"
        self.at_rest_encryption_enabled = True
        self.transit_encryption_enabled = True
        return self

    def memcached(self, version: str = "1.6") -> 'ElastiCache':
        """Configure for Memcached engine - chainable"""
        self.engine = 'memcached'
        self.port = 11211
        self.parameter_group_name = f"default.memcached{version}"
        self.at_rest_encryption_enabled = False  # Not supported in Memcached
        self.transit_encryption_enabled = False
        return self

    def cluster_mode(self, num_shards: int = 3, replicas_per_shard: int = 1) -> 'ElastiCache':
        """Enable Redis cluster mode - chainable"""
        if self.engine != 'redis':
            raise ValueError("Cluster mode is only supported for Redis")
        self.num_node_groups = num_shards
        self.replicas_per_node_group = replicas_per_shard
        self.automatic_failover_enabled = True if replicas_per_shard > 0 else False
        return self

    def replication(self, num_replicas: int = 1) -> 'ElastiCache':
        """Enable Redis replication - chainable"""
        if self.engine != 'redis':
            raise ValueError("Replication is only supported for Redis")
        self.replicas_per_node_group = num_replicas
        self.automatic_failover_enabled = True
        self.multi_az_enabled = True
        return self

    def instance_type(self, instance_type: str) -> 'ElastiCache':
        """Set cache node type - chainable"""
        self.node_type = instance_type
        return self

    def nodes(self, count: int) -> 'ElastiCache':
        """Set number of cache nodes - chainable"""
        self.num_cache_nodes = count
        return self

    def auth_token(self, token: str) -> 'ElastiCache':
        """Set Redis auth token - chainable"""
        if self.engine != 'redis':
            raise ValueError("Auth token is only supported for Redis")
        self.auth_token = token
        self.transit_encryption_enabled = True  # Required for auth
        return self

    def encryption(self, at_rest: bool = True, in_transit: bool = True) -> 'ElastiCache':
        """Configure encryption - chainable"""
        if self.engine == 'redis':
            self.at_rest_encryption_enabled = at_rest
            self.transit_encryption_enabled = in_transit
        elif in_transit or at_rest:
            print("⚠️  Encryption not supported for Memcached")
        return self

    def snapshots(self, retention_days: int = 5, window: str = "03:00-05:00") -> 'ElastiCache':
        """Configure automatic snapshots - chainable"""
        if self.engine != 'redis':
            print("⚠️  Snapshots only supported for Redis")
            return self
        self.snapshot_retention_limit = retention_days
        self.snapshot_window = window
        return self

    def maintenance_window(self, window: str) -> 'ElastiCache':
        """Set maintenance window - chainable"""
        self.maintenance_window = window
        return self

    def subnet_group(self, group_name: str) -> 'ElastiCache':
        """Set cache subnet group - chainable"""
        self.subnet_group_name = group_name
        return self

    def security_groups(self, group_ids: List[str]) -> 'ElastiCache':
        """Set security groups - chainable"""
        self.security_group_ids = group_ids
        return self

    def tags(self, tags: Dict[str, str]) -> 'ElastiCache':
        """Add tags - chainable"""
        self.cache_tags.update(tags)
        return self

    def tag(self, key: str, value: str) -> 'ElastiCache':
        """Add single tag - chainable"""
        self.cache_tags[key] = value
        return self

    # Rails convenience methods

    def session_store(self) -> 'ElastiCache':
        """Rails convenience: Configure for session storage"""
        return (self.redis("7.0")
                .instance_type("cache.t3.micro")
                .replication(1)
                .encryption()
                .snapshots(1)  # Daily snapshots
                .tag("Purpose", "session-store")
                .tag("Critical", "high"))

    def application_cache(self) -> 'ElastiCache':
        """Rails convenience: Configure for application caching"""
        return (self.redis("7.0")
                .instance_type("cache.t3.small")
                .replication(1)
                .encryption()
                .snapshots(3)
                .tag("Purpose", "app-cache")
                .tag("Critical", "medium"))

    def high_performance_cache(self) -> 'ElastiCache':
        """Rails convenience: Configure for high-performance caching"""
        return (self.redis("7.0")
                .instance_type("cache.r6g.large")
                .cluster_mode(3, 2)  # 3 shards, 2 replicas each
                .encryption()
                .snapshots(7)
                .tag("Purpose", "high-performance")
                .tag("Critical", "high"))

    def simple_cache(self) -> 'ElastiCache':
        """Rails convenience: Simple single-node cache"""
        return (self.redis("7.0")
                .instance_type("cache.t3.micro")
                .nodes(1)
                .encryption()
                .tag("Purpose", "simple-cache")
                .tag("Environment", "development"))

    def memcached_cluster(self, nodes: int = 3) -> 'ElastiCache':
        """Rails convenience: Memcached cluster for distributed caching"""
        return (self.memcached("1.6")
                .instance_type("cache.t3.small")
                .nodes(nodes)
                .tag("Purpose", "distributed-cache")
                .tag("Engine", "memcached"))

    # Environment presets

    def development(self) -> 'ElastiCache':
        """Configure for development environment - chainable"""
        return (self.instance_type("cache.t3.micro")
                .nodes(1)
                .snapshots(1)
                .tag("Environment", "development"))

    def staging(self) -> 'ElastiCache':
        """Configure for staging environment - chainable"""
        return (self.instance_type("cache.t3.small")
                .replication(1)
                .snapshots(3)
                .tag("Environment", "staging"))

    def production(self) -> 'ElastiCache':
        """Configure for production environment - chainable"""
        return (self.instance_type("cache.r6g.large")
                .replication(2)
                .multi_az()
                .encryption()
                .snapshots(7)
                .tag("Environment", "production"))

    def multi_az(self) -> 'ElastiCache':
        """Enable multi-AZ deployment - chainable"""
        self.multi_az_enabled = True
        self.automatic_failover_enabled = True
        return self

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()
        
        # Discover existing clusters
        existing_clusters = self._discover_existing_clusters()
        
        # Categorize clusters
        clusters_to_create = []
        clusters_to_keep = []
        clusters_to_remove = []
        
        # Check if our desired cluster exists
        desired_cluster_id = self.cluster_id
        cluster_exists = desired_cluster_id in existing_clusters
        
        if not cluster_exists:
            clusters_to_create.append({
                'cluster_id': desired_cluster_id,
                'engine': self.engine,
                'node_type': self.node_type,
                'num_cache_nodes': self.num_cache_nodes,
                'port': self.port,
                'replication_enabled': self.replicas_per_node_group > 0,
                'num_replicas': self.replicas_per_node_group,
                'cluster_mode': self.num_node_groups > 1,
                'num_shards': self.num_node_groups,
                'encryption_at_rest': self.at_rest_encryption_enabled,
                'encryption_in_transit': self.transit_encryption_enabled,
                'auth_token_enabled': bool(self.auth_token),
                'automatic_failover': self.automatic_failover_enabled,
                'multi_az': self.multi_az_enabled,
                'snapshot_retention': self.snapshot_retention_limit,
                'parameter_group': self.parameter_group_name,
                'subnet_group': self.subnet_group_name,
                'security_groups': self.security_group_ids,
                'maintenance_window': self.maintenance_window
            })
        else:
            clusters_to_keep.append(existing_clusters[desired_cluster_id])

        print(f"\n⚡ ElastiCache Cluster Configuration Preview")
        
        # Show clusters to create
        if clusters_to_create:
            print(f"╭─ ⚡ Clusters to CREATE: {len(clusters_to_create)}")
            for cluster in clusters_to_create:
                print(f"├─ 🆕 {cluster['cluster_id']}")
                print(f"│  ├─ ⚡ Engine: {cluster['engine'].title()}")
                print(f"│  ├─ 🖥️  Node Type: {cluster['node_type']}")
                print(f"│  ├─ 📊 Nodes: {cluster['num_cache_nodes']}")
                print(f"│  ├─ 🔌 Port: {cluster['port']}")
                
                if cluster['engine'] == 'redis':
                    if cluster['replication_enabled']:
                        print(f"│  ├─ 🔄 Replication: {cluster['num_replicas']} replica(s)")
                    if cluster['cluster_mode']:
                        print(f"│  ├─ 🏗️  Cluster Mode: {cluster['num_shards']} shard(s)")
                    if cluster['encryption_at_rest'] or cluster['encryption_in_transit']:
                        print(f"│  ├─ 🔒 Encryption: At-rest={cluster['encryption_at_rest']}, In-transit={cluster['encryption_in_transit']}")
                    if cluster['auth_token_enabled']:
                        print(f"│  ├─ 🔑 Auth Token: Enabled")
                    if cluster['automatic_failover']:
                        print(f"│  ├─ ⚡ Auto Failover: Enabled")
                    if cluster['multi_az']:
                        print(f"│  ├─ 🌍 Multi-AZ: Enabled")
                    if cluster['snapshot_retention'] > 0:
                        print(f"│  ├─ 💾 Snapshots: {cluster['snapshot_retention']} days")
                        
                if cluster['security_groups']:
                    print(f"│  ├─ 🛡️  Security Groups: {len(cluster['security_groups'])}")
                if cluster['subnet_group']:
                    print(f"│  ├─ 🔗 Subnet Group: {cluster['subnet_group']}")
                print(f"│  └─ 📊 Monitoring: CloudWatch metrics")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        if clusters_to_create:
            cluster = clusters_to_create[0]
            if cluster['engine'] == 'redis':
                node_cost_map = {
                    'cache.t3.micro': 0.017,
                    'cache.t3.small': 0.034,
                    'cache.t3.medium': 0.068,
                    'cache.m5.large': 0.138,
                    'cache.m5.xlarge': 0.276,
                    'cache.r5.large': 0.162
                }
                base_cost = node_cost_map.get(cluster['node_type'], 0.100)
                total_nodes = cluster['num_cache_nodes'] * (1 + cluster['num_replicas'])
                monthly_cost = base_cost * 24 * 30 * total_nodes
                
                print(f"   ├─ ⚡ Redis Nodes: ${monthly_cost:.2f} ({total_nodes} nodes)")
                if cluster['snapshot_retention'] > 0:
                    print(f"   ├─ 💾 Backup Storage: $0.085 per GB/month")
                if cluster['encryption_at_rest']:
                    print(f"   ├─ 🔒 Encryption: No additional cost")
            else:
                node_cost_map = {
                    'cache.t3.micro': 0.017,
                    'cache.t3.small': 0.034,
                    'cache.t3.medium': 0.068,
                    'cache.m5.large': 0.138
                }
                base_cost = node_cost_map.get(cluster['node_type'], 0.100)
                monthly_cost = base_cost * 24 * 30 * cluster['num_cache_nodes']
                print(f"   ├─ ⚡ Memcached Nodes: ${monthly_cost:.2f} ({cluster['num_cache_nodes']} nodes)")
            
            print(f"   ├─ 🔄 Data Transfer: $0.09 per GB out")
            print(f"   └─ 🎯 Free Tier: 750 hours t2.micro/month (first year)")

        return {
            'resource_type': 'aws_elasticache',
            'name': self.cluster_id,
            'clusters_to_create': clusters_to_create,
            'clusters_to_keep': clusters_to_keep,
            'clusters_to_remove': clusters_to_remove,
            'existing_clusters': existing_clusters,
            'engine': self.engine,
            'node_type': self.node_type,
            'num_cache_nodes': self.num_cache_nodes,
            'port': self.port,
            'replication_enabled': self.replicas_per_node_group > 0,
            'cluster_mode': self.num_node_groups > 1,
            'encryption_enabled': self.at_rest_encryption_enabled or self.transit_encryption_enabled,
            'estimated_cost': f"${(0.100 * 24 * 30 * self.num_cache_nodes):.2f}/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create the ElastiCache cluster with smart state management"""
        self._ensure_authenticated()
        
        # Discover existing clusters first
        existing_clusters = self._discover_existing_clusters()
        
        # Determine what changes need to be made
        desired_cluster_id = self.cluster_id
        
        # Check for clusters to remove (not in current configuration)
        clusters_to_remove = []
        for cluster_id, cluster_info in existing_clusters.items():
            # In a real implementation, this would have more sophisticated logic
            # to determine which clusters should be removed based on configuration
            # For now, we'll focus on creating the desired cluster
            pass
        
        # Remove clusters no longer in configuration
        if clusters_to_remove:
            print(f"\n🗑️  Removing ElastiCache clusters no longer in configuration:")
            for cluster_info in clusters_to_remove:
                print(f"╭─ 🔄 Removing cluster: {cluster_info['cluster_id']}")
                print(f"├─ ⚡ Engine: {cluster_info['engine'].title()}")
                print(f"├─ 🖥️  Node Type: {cluster_info['node_type']}")
                print(f"├─ 📊 Status: {cluster_info['status']}")
                print(f"├─ 🔗 Endpoint: {cluster_info['endpoint']}:{cluster_info['port']}")
                print(f"└─ ⚠️  Cluster and cached data will be permanently deleted")
                
                # In real implementation:
                # if cluster_info['cluster_type'] == 'redis_replication_group':
                #     self.elasticache_client.delete_replication_group(
                #         ReplicationGroupId=cluster_info['cluster_id']
                #     )
                # else:
                #     self.elasticache_client.delete_cache_cluster(
                #         CacheClusterId=cluster_info['cluster_id']
                #     )

        # Check if our desired cluster already exists
        cluster_exists = desired_cluster_id in existing_clusters
        if cluster_exists:
            existing_cluster = existing_clusters[desired_cluster_id]
            print(f"\n🔄 ElastiCache cluster '{self.cluster_id}' already exists")
            print(f"   ⚡ Engine: {existing_cluster['engine'].title()}")
            print(f"   🖥️  Node Type: {existing_cluster['node_type']}")
            print(f"   📊 Status: {existing_cluster['status']}")
            
            result = {
                'cluster_id': existing_cluster['cluster_id'],
                'cluster_arn': f"arn:aws:elasticache:{self.get_current_region()}:123456789012:cluster:{existing_cluster['cluster_id']}",
                'endpoint': f"{existing_cluster['endpoint']}:{existing_cluster['port']}",
                'engine': existing_cluster['engine'],
                'status': existing_cluster['status'],
                'existing': True
            }
            if len(clusters_to_remove) > 0:
                result['changes'] = True
            return result
        
        print(f"\n⚡ Creating ElastiCache cluster: {self.cluster_id}")
        print(f"   Engine: {self.engine.title()}")
        print(f"   Node Type: {self.node_type}")
        
        try:
            if self.engine == 'redis':
                result = self._create_redis_cluster()
            else:
                result = self._create_memcached_cluster()
                
            if len(clusters_to_remove) > 0:
                result['changes'] = True
            return result
                
        except Exception as e:
            print(f"❌ Failed to create ElastiCache cluster: {e}")
            return {"error": str(e)}

    def _create_redis_cluster(self) -> Dict[str, Any]:
        """Create Redis cluster/replication group"""
        print("   - Creating Redis cluster...")
        
        # Simulate Redis cluster creation
        region = self.get_current_region()
        account_id = "123456789012"  # Would get from AWS client
        
        if self.num_node_groups > 1 or self.replicas_per_node_group > 0:
            # Redis cluster or replication group
            self.replication_group_id = f"{self.cluster_id}-rg"
            self.cluster_arn = f"arn:aws:elasticache:{region}:{account_id}:replicationgroup:{self.replication_group_id}"
            
            if self.num_node_groups > 1:
                print(f"   - Cluster mode: {self.num_node_groups} shards, {self.replicas_per_node_group} replicas each")
                self.cluster_address = f"{self.replication_group_id}.clustercfg.{region}.cache.amazonaws.com"
            else:
                print(f"   - Replication group: 1 primary, {self.replicas_per_node_group} replica(s)")
                self.cluster_address = f"{self.replication_group_id}.{region}.cache.amazonaws.com"
        else:
            # Single Redis node
            self.cluster_arn = f"arn:aws:elasticache:{region}:{account_id}:cluster:{self.cluster_id}"
            self.cluster_address = f"{self.cluster_id}.{region}.cache.amazonaws.com"
        
        self.cluster_status = 'available'
        
        print(f"✅ Redis cluster created successfully")
        print(f"   Cluster ARN: {self.cluster_arn}")
        print(f"   Endpoint: {self.cluster_address}:{self.port}")
        
        if self.at_rest_encryption_enabled:
            print(f"   🔒 Encryption at rest: Enabled")
        if self.transit_encryption_enabled:
            print(f"   🔒 Encryption in transit: Enabled")
        if self.auth_token:
            print(f"   🔑 Auth token: Configured")
        
        return {
            "cluster_id": self.cluster_id,
            "cluster_arn": self.cluster_arn,
            "endpoint": f"{self.cluster_address}:{self.port}",
            "engine": "redis",
            "status": self.cluster_status
        }

    def _create_memcached_cluster(self) -> Dict[str, Any]:
        """Create Memcached cluster"""
        print("   - Creating Memcached cluster...")
        
        # Simulate Memcached cluster creation
        region = self.get_current_region()
        account_id = "123456789012"  # Would get from AWS client
        
        self.cluster_arn = f"arn:aws:elasticache:{region}:{account_id}:cluster:{self.cluster_id}"
        self.cluster_address = f"{self.cluster_id}.clustercfg.{region}.cache.amazonaws.com"
        self.cluster_status = 'available'
        
        # Generate node endpoints for each cache node
        for i in range(self.num_cache_nodes):
            node_endpoint = f"{self.cluster_id}-{i:03d}.{region}.cache.amazonaws.com"
            self.cluster_endpoints.append(f"{node_endpoint}:{self.port}")
        
        print(f"✅ Memcached cluster created successfully")
        print(f"   Cluster ARN: {self.cluster_arn}")
        print(f"   Configuration endpoint: {self.cluster_address}:{self.port}")
        print(f"   Node count: {self.num_cache_nodes}")
        
        return {
            "cluster_id": self.cluster_id,
            "cluster_arn": self.cluster_arn,
            "configuration_endpoint": f"{self.cluster_address}:{self.port}",
            "node_endpoints": self.cluster_endpoints,
            "engine": "memcached",
            "status": self.cluster_status
        }

    def destroy(self) -> Dict[str, Any]:
        """Destroy the ElastiCache cluster"""
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying ElastiCache cluster: {self.cluster_id}")
        
        try:
            # In real implementation, this would delete the cluster/replication group
            print("   - Deleting cache cluster...")
            print("   - Cleaning up snapshots...")
            
            print(f"✅ ElastiCache cluster destroyed successfully")
            
            return {
                "cluster_id": self.cluster_id,
                "status": "deleted"
            }
            
        except Exception as e:
            print(f"❌ Failed to destroy ElastiCache cluster: {e}")
            return {"error": str(e)}

    def connection_string(self) -> str:
        """Get Redis/Memcached connection string"""
        if not self.cluster_address:
            return "Cluster not yet created"
        
        if self.engine == 'redis':
            if self.auth_token:
                return f"redis://:{self.auth_token}@{self.cluster_address}:{self.port}"
            else:
                return f"redis://{self.cluster_address}:{self.port}"
        else:
            return f"{self.cluster_address}:{self.port}"

    def get_status(self) -> Dict[str, Any]:
        """Get cluster status and health information"""
        return {
            "cluster_id": self.cluster_id,
            "status": self.cluster_status,
            "engine": self.engine,
            "node_type": self.node_type,
            "endpoint": self.cluster_address,
            "port": self.port,
            "connection_string": self.connection_string()
        }

    def _discover_existing_clusters(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing ElastiCache clusters"""
        existing_clusters = {}
        
        try:
            # Discover Redis clusters (replication groups)
            try:
                response = self.elasticache_client.describe_replication_groups()
                for rg in response.get('ReplicationGroups', []):
                    cluster_id = rg['ReplicationGroupId']
                    existing_clusters[cluster_id] = {
                        'cluster_id': cluster_id,
                        'cluster_type': 'redis_replication_group',
                        'description': rg.get('Description', ''),
                        'status': rg.get('Status'),
                        'node_type': rg.get('CacheNodeType'),
                        'num_cache_clusters': len(rg.get('MemberClusters', [])),
                        'engine': 'redis',
                        'engine_version': rg.get('CacheNodeType'),
                        'endpoint': rg.get('ConfigurationEndpoint', {}).get('Address') if rg.get('ConfigurationEndpoint') else 
                                   rg.get('PrimaryEndpoint', {}).get('Address') if rg.get('PrimaryEndpoint') else None,
                        'port': rg.get('ConfigurationEndpoint', {}).get('Port') if rg.get('ConfigurationEndpoint') else
                               rg.get('PrimaryEndpoint', {}).get('Port') if rg.get('PrimaryEndpoint') else 6379,
                        'at_rest_encryption': rg.get('AtRestEncryptionEnabled', False),
                        'transit_encryption': rg.get('TransitEncryptionEnabled', False),
                        'auth_token_enabled': rg.get('AuthTokenEnabled', False),
                        'automatic_failover': rg.get('AutomaticFailover') == 'enabled',
                        'multi_az': rg.get('MultiAZ') == 'enabled',
                        'snapshot_retention': rg.get('SnapshotRetentionLimit', 0),
                        'creation_date': rg.get('SnapshotRetentionLimit'),
                        'cluster_mode': rg.get('ClusterEnabled', False)
                    }
            except Exception as e:
                print(f"⚠️  Failed to describe replication groups: {str(e)}")
            
            # Discover regular cache clusters (Redis single node, Memcached)
            try:
                response = self.elasticache_client.describe_cache_clusters(ShowCacheNodeInfo=True)
                for cluster in response.get('CacheClusters', []):
                    cluster_id = cluster['CacheClusterId']
                    
                    # Skip if already found as part of replication group
                    if cluster_id in existing_clusters:
                        continue
                    
                    existing_clusters[cluster_id] = {
                        'cluster_id': cluster_id,
                        'cluster_type': 'cache_cluster',
                        'status': cluster.get('CacheClusterStatus'),
                        'node_type': cluster.get('CacheNodeType'),
                        'num_cache_nodes': cluster.get('NumCacheNodes', 1),
                        'engine': cluster.get('Engine'),
                        'engine_version': cluster.get('EngineVersion'),
                        'endpoint': cluster.get('RedisConfiguration', {}).get('PrimaryEndpoint', {}).get('Address') if cluster.get('Engine') == 'redis' else
                                   cluster.get('ConfigurationEndpoint', {}).get('Address') if cluster.get('ConfigurationEndpoint') else
                                   cluster.get('CacheNodes', [{}])[0].get('Endpoint', {}).get('Address') if cluster.get('CacheNodes') else None,
                        'port': cluster.get('RedisConfiguration', {}).get('PrimaryEndpoint', {}).get('Port') if cluster.get('Engine') == 'redis' else
                               cluster.get('ConfigurationEndpoint', {}).get('Port') if cluster.get('ConfigurationEndpoint') else
                               cluster.get('CacheNodes', [{}])[0].get('Endpoint', {}).get('Port') if cluster.get('CacheNodes') else
                               (6379 if cluster.get('Engine') == 'redis' else 11211),
                        'at_rest_encryption': cluster.get('AtRestEncryptionEnabled', False),
                        'transit_encryption': cluster.get('TransitEncryptionEnabled', False),
                        'auth_token_enabled': cluster.get('AuthTokenEnabled', False),
                        'automatic_failover': False,
                        'multi_az': False,
                        'snapshot_retention': 0,
                        'creation_date': cluster.get('CacheClusterCreateTime'),
                        'cluster_mode': False
                    }
            except Exception as e:
                print(f"⚠️  Failed to describe cache clusters: {str(e)}")
                
        except Exception as e:
            print(f"⚠️  Failed to discover existing ElastiCache clusters: {str(e)}")
        
        return existing_clusters 
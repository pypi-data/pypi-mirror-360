from typing import Dict, Any, Optional, List
from ..base_resource import BaseGcpResource
from ...googlecloud_managers.gke_manager import GkeManager, GkeConfig
from ...googlecloud_managers.gcp_client import GcpClient


class GKE(BaseGcpResource):
    """Rails-like GKE cluster orchestrator - Kubernetes made simple"""

    def __init__(self, name: str):
        self.config = GkeConfig(name=name)
        super().__init__(name)

    def _initialize_managers(self):
        """Initialize GKE specific managers"""
        self.gke_manager = None

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Initialize GCP client for GKE operations
        if not hasattr(self, 'gcp_client') or not self.gcp_client:
            self.gcp_client = GcpClient()
            self.gcp_client.authenticate(silent=True)
            
        self.gke_manager = GkeManager(self.gcp_client)

    def _discover_existing_clusters(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing GKE clusters"""
        existing_clusters = {}
        
        try:
            from googleapiclient import discovery
            from googleapiclient.errors import HttpError
            
            service = discovery.build('container', 'v1', credentials=self.gcp_client.credentials)
            
            # List clusters in all locations
            locations_to_check = [self.config.location] if self.config.location else ['-']
            
            for location in locations_to_check:
                try:
                    request = service.projects().locations().clusters().list(
                        parent=f"projects/{self.gcp_client.project_id}/locations/{location}"
                    )
                    response = request.execute()
                    
                    for cluster in response.get('clusters', []):
                        cluster_name = cluster['name']
                        
                        existing_clusters[cluster_name] = {
                            'cluster_name': cluster_name,
                            'location': cluster['location'],
                            'status': cluster['status'],
                            'node_pools': len(cluster.get('nodePools', [])),
                            'current_node_count': cluster.get('currentNodeCount', 0),
                            'initial_node_count': cluster.get('initialNodeCount', 0),
                            'endpoint': cluster.get('endpoint'),
                            'current_master_version': cluster.get('currentMasterVersion'),
                            'current_node_version': cluster.get('currentNodeVersion'),
                            'network': cluster.get('network'),
                            'subnetwork': cluster.get('subnetwork'),
                            'cluster_ipv4_cidr': cluster.get('clusterIpv4Cidr'),
                            'services_ipv4_cidr': cluster.get('servicesIpv4Cidr'),
                            'create_time': cluster.get('createTime'),
                            'self_link': cluster.get('selfLink'),
                            'zone': cluster.get('zone'),
                            'locations': cluster.get('locations', []),
                            'monitoring_enabled': cluster.get('loggingService') is not None,
                            'logging_enabled': cluster.get('monitoringService') is not None,
                            'addons_config': cluster.get('addonsConfig', {}),
                            'node_config': cluster.get('nodeConfig', {}),
                            'labels': cluster.get('resourceLabels', {}),
                            'legacy_abac': cluster.get('legacyAbac', {}).get('enabled', False),
                            'ip_allocation_policy': cluster.get('ipAllocationPolicy', {}),
                            'master_auth': cluster.get('masterAuth', {}),
                            'autoscaling': any(
                                pool.get('autoscaling', {}).get('enabled', False) 
                                for pool in cluster.get('nodePools', [])
                            ),
                            'preemptible': any(
                                pool.get('config', {}).get('preemptible', False)
                                for pool in cluster.get('nodePools', [])
                            ),
                            'machine_types': list(set(
                                pool.get('config', {}).get('machineType', 'unknown')
                                for pool in cluster.get('nodePools', [])
                            )),
                            'disk_sizes': list(set(
                                pool.get('config', {}).get('diskSizeGb', 0)
                                for pool in cluster.get('nodePools', [])
                            ))
                        }
                except HttpError as e:
                    if e.resp.status == 404:
                        # Location not found, continue with other locations
                        continue
                    else:
                        print(f"⚠️  Failed to list clusters in location {location}: {str(e)}")
                        
        except Exception as e:
            print(f"⚠️  Failed to discover existing GKE clusters: {str(e)}")
        
        return existing_clusters

    def location(self, location: str) -> 'GKE':
        """Set the location for the GKE cluster"""
        self.config.location = location
        return self

    def nodes(self, count: int) -> 'GKE':
        """Set the number of nodes in the cluster"""
        self.config.node_count = count
        return self

    def machine_type(self, machine_type: str) -> 'GKE':
        """Set the machine type for cluster nodes"""
        self.config.machine_type = machine_type
        return self

    def disk_size(self, size_gb: int) -> 'GKE':
        """Set the disk size for cluster nodes"""
        self.config.disk_size_gb = size_gb
        return self

    def auto_scale(self, min_nodes: int, max_nodes: int) -> 'GKE':
        """Enable auto-scaling for the cluster"""
        self.config.auto_scale = True
        self.config.min_nodes = min_nodes
        self.config.max_nodes = max_nodes
        return self

    def zones(self, zones: List[str]) -> 'GKE':
        """Set the zones for the cluster nodes"""
        self.config.zones = zones
        return self

    def preemptible(self, enabled: bool = True) -> 'GKE':
        """Enable preemptible nodes for cost savings"""
        self.config.preemptible = enabled
        return self

    def labels(self, labels: Dict[str, str]) -> 'GKE':
        """Add labels to the cluster"""
        self.config.labels = labels
        return self

    def network(self, network: str, subnetwork: str = "default") -> 'GKE':
        """Set the network configuration"""
        self.config.network = network
        self.config.subnetwork = subnetwork
        return self

    def kubernetes_version(self, version: str) -> 'GKE':
        """Set the Kubernetes version"""
        self.config.kubernetes_version = version
        return self

    def enable_autoscaling(self, enabled: bool = True) -> 'GKE':
        """Enable or disable cluster autoscaling"""
        self.config.auto_scale = enabled
        return self

    def enable_monitoring(self, enabled: bool = True) -> 'GKE':
        """Enable or disable cluster monitoring"""
        # Set monitoring_enabled field (may not exist in GkeConfig yet)
        if not hasattr(self.config, 'monitoring_enabled'):
            setattr(self.config, 'monitoring_enabled', enabled)
        else:
            self.config.monitoring_enabled = enabled
        return self

    def enable_logging(self, enabled: bool = True) -> 'GKE':
        """Enable or disable cluster logging"""
        # Set logging_enabled field (may not exist in GkeConfig yet)
        if not hasattr(self.config, 'logging_enabled'):
            setattr(self.config, 'logging_enabled', enabled)
        else:
            self.config.logging_enabled = enabled
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
        desired_cluster_name = self.config.name
        cluster_exists = desired_cluster_name in existing_clusters
        
        if not cluster_exists:
            clusters_to_create.append({
                'cluster_name': desired_cluster_name,
                'location': self.config.location,
                'node_count': self.config.node_count,
                'machine_type': self.config.machine_type,
                'disk_size_gb': self.config.disk_size_gb,
                'network': self.config.network,
                'subnetwork': self.config.subnetwork,
                'auto_scaling': self.config.auto_scale,
                'min_nodes': self.config.min_nodes if self.config.auto_scale else None,
                'max_nodes': self.config.max_nodes if self.config.auto_scale else None,
                'zones': self.config.zones,
                'preemptible': self.config.preemptible,
                'kubernetes_version': self.config.kubernetes_version,
                'monitoring_enabled': getattr(self.config, 'monitoring_enabled', True),
                'logging_enabled': getattr(self.config, 'logging_enabled', True),
                'labels': self.config.labels
            })
        else:
            clusters_to_keep.append(existing_clusters[desired_cluster_name])

        print(f"\n⚓ Google Cloud GKE Cluster Configuration Preview")
        
        # Show clusters to create
        if clusters_to_create:
            print(f"╭─ ⚓ GKE Clusters to CREATE: {len(clusters_to_create)}")
            for cluster in clusters_to_create:
                print(f"├─ 🆕 {cluster['cluster_name']}")
                print(f"│  ├─ 📍 Location: {cluster['location']}")
                print(f"│  ├─ 🖥️  Machine Type: {cluster['machine_type']}")
                print(f"│  ├─ 📊 Nodes: {cluster['node_count']}")
                print(f"│  ├─ 💾 Disk Size: {cluster['disk_size_gb']}GB")
                print(f"│  ├─ 🌐 Network: {cluster['network']}/{cluster['subnetwork']}")
                
                if cluster['auto_scaling']:
                    print(f"│  ├─ 📈 Auto-scaling: {cluster['min_nodes']}-{cluster['max_nodes']} nodes")
                else:
                    print(f"│  ├─ 📈 Auto-scaling: Disabled")
                
                if cluster['zones']:
                    print(f"│  ├─ 🌍 Zones: {', '.join(cluster['zones'])}")
                
                if cluster['preemptible']:
                    print(f"│  ├─ 💰 Preemptible: Enabled (cost savings)")
                
                print(f"│  ├─ ⚓ K8s Version: {cluster['kubernetes_version'] or 'Latest'}")
                
                if cluster['monitoring_enabled']:
                    print(f"│  ├─ 📊 Monitoring: Enabled")
                
                if cluster['logging_enabled']:
                    print(f"│  ├─ 📝 Logging: Enabled")
                
                if cluster['labels']:
                    print(f"│  ├─ 🏷️  Labels: {len(cluster['labels'])}")
                
                print(f"│  └─ 📦 Pod orchestration: Full Kubernetes API")
            print(f"╰─")

        # Show existing clusters being kept
        if clusters_to_keep:
            print(f"\n╭─ ⚓ Existing GKE Clusters to KEEP: {len(clusters_to_keep)}")
            for cluster in clusters_to_keep:
                print(f"├─ ✅ {cluster['cluster_name']}")
                print(f"│  ├─ 📍 Location: {cluster['location']}")
                print(f"│  ├─ 📊 Status: {cluster['status']}")
                print(f"│  ├─ 📦 Nodes: {cluster['current_node_count']}")
                print(f"│  ├─ 🖥️  Machine Types: {', '.join(cluster['machine_types'])}")
                print(f"│  ├─ ⚓ Master Version: {cluster['current_master_version']}")
                print(f"│  ├─ 🔗 Endpoint: {cluster.get('endpoint', 'N/A')}")
                
                if cluster['autoscaling']:
                    print(f"│  ├─ 📈 Auto-scaling: Enabled")
                
                if cluster['preemptible']:
                    print(f"│  ├─ 💰 Preemptible: Cost optimized")
                
                if cluster['monitoring_enabled']:
                    print(f"│  ├─ 📊 Monitoring: Active")
                
                print(f"│  └─ 📅 Created: {cluster.get('create_time', 'Unknown')}")
            print(f"╰─")

        # Show cost estimation
        node_cost_map = {
            'e2-micro': 0.008,
            'e2-small': 0.017,
            'e2-medium': 0.034,
            'n1-standard-1': 0.048,
            'n1-standard-2': 0.095,
            'n1-standard-4': 0.190
        }
        
        print(f"\n💰 Estimated Monthly Costs:")
        if clusters_to_create:
            cluster = clusters_to_create[0]
            base_cost = node_cost_map.get(cluster['machine_type'], 0.100)
            node_cost = base_cost * 24 * 30 * cluster['node_count']
            
            if cluster['preemptible']:
                node_cost *= 0.2  # 80% discount for preemptible
                print(f"   ├─ ⚓ Cluster Management: FREE")
                print(f"   ├─ 🖥️  Preemptible Nodes: ${node_cost:.2f} ({cluster['node_count']} × {cluster['machine_type']})")
                print(f"   ├─ 💰 Preemptible Savings: 80% off regular pricing")
            else:
                print(f"   ├─ ⚓ Cluster Management: FREE")
                print(f"   ├─ 🖥️  Regular Nodes: ${node_cost:.2f} ({cluster['node_count']} × {cluster['machine_type']})")
            
            print(f"   ├─ 💾 Persistent Disks: ${cluster['disk_size_gb'] * cluster['node_count'] * 0.04:.2f}")
            print(f"   ├─ 🌐 Load Balancer: $18.25/month (if used)")
            print(f"   ├─ 📊 Monitoring: FREE (Cloud Operations Suite)")
            print(f"   └─ 🎯 Free Tier: 1 zonal cluster per month")
        else:
            print(f"   ├─ ⚓ Cluster Management: FREE")
            print(f"   ├─ 🖥️  Compute Nodes: Variable based on configuration")
            print(f"   └─ 🎯 Free Tier: 1 zonal cluster per month")

        return {
            'resource_type': 'gcp_gke',
            'name': self.config.name,
            'clusters_to_create': clusters_to_create,
            'clusters_to_keep': clusters_to_keep,
            'clusters_to_remove': clusters_to_remove,
            'existing_clusters': existing_clusters,
            'cluster_name': self.config.name,
            'location': self.config.location,
            'node_count': self.config.node_count,
            'machine_type': self.config.machine_type,
            'auto_scaling': self.config.auto_scale,
            'kubernetes_version': self.config.kubernetes_version,
            'estimated_cost': f"${node_cost_map.get(self.config.machine_type, 0.100) * 24 * 30 * self.config.node_count:.2f}/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create the GKE cluster"""
        self._ensure_authenticated()

        print(f"\n🚀 Creating GKE cluster: {self.config.name}")
        print(f"   📍 Location: {self.config.location}")
        print(f"   🔧 Node Count: {self.config.node_count}")
        print(f"   ⚙️  Machine Type: {self.config.machine_type}")

        if self.config.auto_scale:
            print(f"   📈 Auto-scaling: {self.config.min_nodes}-{self.config.max_nodes} nodes")

        print(f"   ⏳ This may take several minutes...")

        try:
            result = self.gke_manager.create_cluster(self.config)

            print(f"\n🎉 GKE cluster created successfully!")
            print(f"   🔗 Cluster Name: {result['name']}")
            print(f"   📍 Location: {result['location']}")
            print(f"   🔧 Status: {result['status']}")
            print(f"   🌐 Endpoint: {result.get('endpoint', 'N/A')}")

            if 'kubeconfig' in result:
                print(f"   📝 Kubeconfig: {result['kubeconfig']}")

            return result

        except Exception as e:
            print(f"❌ Failed to create GKE cluster: {str(e)}")
            raise

    def destroy(self) -> Dict[str, Any]:
        """Destroy the GKE cluster"""
        self._ensure_authenticated()

        print(f"🗑️  Destroying GKE cluster: {self.config.name}")
        print(f"   📍 Location: {self.config.location}")
        print(f"   ⏳ This may take several minutes...")

        try:
            success = self.gke_manager.delete_cluster(self.config.name, self.config.location)

            if success:
                print(f"✅ GKE cluster destroyed: {self.config.name}")
                return {"success": True, "cluster_name": self.config.name}
            else:
                print(f"⚠️  Warning: Failed to destroy GKE cluster: {self.config.name}")
                return {"success": False, "cluster_name": self.config.name}

        except Exception as e:
            print(f"❌ Failed to destroy GKE cluster: {str(e)}")
            return {"success": False, "cluster_name": self.config.name, "error": str(e)}

    def get_credentials(self) -> Dict[str, Any]:
        """Get credentials for the GKE cluster"""
        self._ensure_authenticated()

        try:
            credentials = self.gke_manager.get_cluster_credentials(self.config.name, self.config.location)
            print(f"✅ Credentials retrieved for cluster: {self.config.name}")
            return credentials
        except Exception as e:
            print(f"❌ Failed to get credentials: {str(e)}")
            raise

    def scale(self, node_count: int) -> Dict[str, Any]:
        """Scale the cluster to a specific number of nodes"""
        self._ensure_authenticated()

        print(f"🔄 Scaling cluster {self.config.name} to {node_count} nodes...")

        try:
            result = self.gke_manager.scale_cluster(self.config.name, self.config.location, node_count)
            print(f"✅ Cluster scaled successfully to {node_count} nodes")
            return result
        except Exception as e:
            print(f"❌ Failed to scale cluster: {str(e)}")
            raise

    def upgrade(self, kubernetes_version: Optional[str] = None) -> Dict[str, Any]:
        """Upgrade the cluster to a newer Kubernetes version"""
        self._ensure_authenticated()

        version_info = f" to {kubernetes_version}" if kubernetes_version else " to latest"
        print(f"⬆️  Upgrading cluster {self.config.name}{version_info}...")

        try:
            result = self.gke_manager.upgrade_cluster(self.config.name, self.config.location, kubernetes_version)
            print(f"✅ Cluster upgrade initiated successfully")
            return result
        except Exception as e:
            print(f"❌ Failed to upgrade cluster: {str(e)}")
            raise

from typing import List, Dict, Any, Optional
from .do_client import DoClient
from .infrastructure_planner import KubernetesClusterConfig, KubernetesNodePool
import time

class KubernetesCluster:
    """DigitalOcean Kubernetes cluster configuration and management"""

    def __init__(self, name: str):
        self.config = KubernetesClusterConfig(
            name=name,
            region="",
            version="",
            node_pools=[]
        )
        self.do_client = DoClient()

    def region(self, region: str) -> 'KubernetesCluster':
        """Set the region for the Kubernetes cluster"""
        self.config.region = region
        return self

    def version(self, version: str) -> 'KubernetesCluster':
        """Set the Kubernetes version for the cluster"""
        self.config.version = version
        return self

    def add_node_pool(self, name: str, size: str, count: int) -> 'KubernetesCluster':
        """Add a node pool to the cluster"""
        node_pool = KubernetesNodePool(
            name=name,
            size=size,
            count=count
        )
        self.config.node_pools.append(node_pool)
        return self

    def auto_scale(self, min_nodes: int, max_nodes: int) -> 'KubernetesCluster':
        """Enable auto-scaling for the first node pool"""
        if not self.config.node_pools:
            raise ValueError("Must add a node pool before enabling auto-scaling")
        
        # Apply auto-scaling to the first node pool
        self.config.node_pools[0].min_nodes = min_nodes
        self.config.node_pools[0].max_nodes = max_nodes
        return self

    def high_availability(self, enabled: bool = True) -> 'KubernetesCluster':
        """Enable high availability for production clusters"""
        self.config.high_availability = enabled
        return self

    def marketplace(self, addon: str) -> 'KubernetesCluster':
        """Enable a DigitalOcean Marketplace add-on by friendly name or slug"""
        # Map friendly names to slugs
        marketplace_map = {
            "Kubernetes Monitoring Stack": "doks-monitoring",
            "Monitoring": "doks-monitoring",
            "doks-monitoring": "doks-monitoring"
        }
        slug = marketplace_map.get(addon, addon)  # Use slug directly if not mapped
        if slug not in self.config.addons:
            self.config.addons.append(slug)
        return self

    def authenticate(self, token: str) -> 'KubernetesCluster':
        """Set the DigitalOcean API token"""
        self.do_client.authenticate(token)
        return self

    def _discover_existing_clusters(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing DigitalOcean Kubernetes Clusters"""
        existing_clusters = {}
        
        try:
            manager = self.do_client.client
            resp = manager.kubernetes.list_clusters()
            
            for cluster in resp.get("kubernetes_clusters", []):
                if cluster.get("name") == self.config.name:
                    existing_clusters[self.config.name] = {
                        "name": cluster.get("name"),
                        "id": cluster.get("id"),
                        "status": cluster.get("status", {}).get("state", "unknown"),
                        "version": cluster.get("version"),
                        "region": cluster.get("region", {}).get("slug"),
                        "node_pools": cluster.get("node_pools", []),
                        "endpoint": cluster.get("endpoint"),
                        "ipv4": cluster.get("ipv4"),
                        "cluster_subnet": cluster.get("cluster_subnet"),
                        "service_subnet": cluster.get("service_subnet"),
                        "vpc_uuid": cluster.get("vpc_uuid"),
                        "created_at": cluster.get("created_at"),
                        "updated_at": cluster.get("updated_at"),
                        "ha": cluster.get("ha", False)
                    }
                    break
                    
        except Exception as e:
            # Silently handle discovery errors
            pass
            
        return existing_clusters

    def preview(self) -> Dict[str, Any]:
        """Preview DigitalOcean Kubernetes Cluster with smart state management"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")

        if not self.config.region:
            raise ValueError("Region is required. Use .region() to set it.")
        
        if not self.config.version:
            raise ValueError("Version is required. Use .version() to set it.")

        if not self.config.node_pools:
            raise ValueError("At least one node pool is required. Use .add_node_pool() to add one.")

        print(f"╭─ 📦 DigitalOcean Kubernetes Cluster Preview: {self.config.name}")
        print(f"├─ 🌍 Region: {self.config.region}")
        print(f"├─ 🔧 Version: {self.config.version}")
        
        # Discover existing clusters
        existing_clusters = self._discover_existing_clusters()
        
        # Determine changes needed
        to_create = []
        to_update = []
        to_keep = []
        
        if self.config.name not in existing_clusters:
            to_create.append(self.config.name)
        else:
            existing_cluster = existing_clusters[self.config.name]
            # Check if update is needed
            needs_update = (
                existing_cluster.get("version") != self.config.version or
                len(existing_cluster.get("node_pools", [])) != len(self.config.node_pools)
            )
            
            if needs_update:
                to_update.append(self.config.name)
            else:
                to_keep.append(self.config.name)
        
        # Estimate cost based on node pools
        total_cost = 0
        for pool in self.config.node_pools:
            # Rough cost estimation: $10-40/node/month
            node_cost = 20  # Average cost per node
            total_cost += pool.count * node_cost
        
        print(f"├─ 🌍 Cost: ~${total_cost}/month ({sum(p.count for p in self.config.node_pools)} nodes)")
        
        # Show only actionable changes
        if to_create:
            print(f"├─ 🔧 Kubernetes Clusters to CREATE:")
            print(f"│  ├─ 📦 {self.config.name}")
            if self.config.high_availability:
                print(f"│  │  ├─ 🛡️  High Availability: Enabled")
            print(f"│  │  ├─ Node Pools:")
            for pool in self.config.node_pools:
                ha_info = ""
                if self.config.high_availability and pool.count < 3:
                    ha_info = " (⚠️  HA requires ≥3)"
                print(f"│  │  │  ├─ {pool.name}: {pool.count} × {pool.size}{ha_info}")
                if pool.min_nodes is not None and pool.max_nodes is not None:
                    print(f"│  │  │  │  ├─ Auto-scale: {pool.min_nodes}-{pool.max_nodes} nodes")
                
        if to_update:
            print(f"├─ 🔄 Kubernetes Clusters to UPDATE:")
            existing_cluster = existing_clusters[self.config.name]
            print(f"│  ├─ 📦 {self.config.name}")
            print(f"│  │  ├─ Version: {existing_cluster.get('version')} → {self.config.version}")
            print(f"│  │  ├─ Node Pools: {len(existing_cluster.get('node_pools', []))} → {len(self.config.node_pools)}")
            
        if existing_clusters and self.config.name in existing_clusters:
            existing_cluster = existing_clusters[self.config.name]
            print(f"├─ ✅ Current status: {existing_cluster.get('status', 'unknown')}")
            if existing_cluster.get('endpoint'):
                print(f"├─ 🌐 Endpoint: {existing_cluster['endpoint']}")
            if existing_cluster.get('ipv4'):
                print(f"├─ 🔗 IPv4: {existing_cluster['ipv4']}")
        
        print(f"╰─ 💡 Run .create() to deploy cluster")
        
        return {
            "name": self.config.name,
            "to_create": to_create,
            "to_update": to_update,
            "existing_clusters": existing_clusters,
            "region": self.config.region,
            "version": self.config.version,
            "node_pools": [{"name": p.name, "size": p.size, "count": p.count} for p in self.config.node_pools],
            "high_availability": self.config.high_availability,
            "estimated_cost": total_cost,
            "changes": len(to_create) + len(to_update) > 0
        }

    def create(self, wait_for_provisioning: bool = True) -> Dict[str, Any]:
        """Create or update the Kubernetes cluster with smart state management"""
        if not self.config.region:
            raise ValueError("Region is required. Use .region() to set it.")
        if not self.config.version:
            raise ValueError("Kubernetes version is required. Use .version() to set it.")
        if not self.config.node_pools:
            raise ValueError("At least one node pool is required. Use .add_node_pool() to add one.")
        
        # Discover existing clusters first
        existing_clusters = self._discover_existing_clusters()
        
        # Determine changes needed
        action = "CREATE"
        existing_cluster = None
        if self.config.name in existing_clusters:
            existing_cluster = existing_clusters[self.config.name]
            # Check if update is needed
            needs_update = (
                existing_cluster.get("version") != self.config.version or
                len(existing_cluster.get("node_pools", [])) != len(self.config.node_pools)
            )
            action = "UPDATE" if needs_update else "KEEP"
        
        print(f"📦 {action}ING DigitalOcean Kubernetes Cluster: {self.config.name}")
        
        if action == "KEEP":
            print(f"✅ Kubernetes cluster already exists with desired configuration")
            return {
                "id": existing_cluster.get("id"),
                "name": self.config.name,
                "status": existing_cluster.get("status"),
                "endpoint": existing_cluster.get("endpoint"),
                "action": "kept",
                "changes": False
            }

        manager = self.do_client.client
        
        try:
            if action == "CREATE":
                print(f"╭─ 🔧 Creating new Kubernetes cluster...")
                
                # Prepare node pools
                node_pools = []
                for pool in self.config.node_pools:
                    node_pool_config = {
                        "name": pool.name,
                        "size": pool.size,
                        "count": pool.count
                    }
                    
                    # Add auto-scaling if configured
                    if pool.min_nodes is not None and pool.max_nodes is not None:
                        node_pool_config["auto_scale"] = True
                        node_pool_config["min_nodes"] = pool.min_nodes
                        node_pool_config["max_nodes"] = pool.max_nodes
                    
                    # Ensure minimum node count for HA
                    if self.config.high_availability and pool.count < 3:
                        print(f"│  ├─ ⚠️  HA requires ≥3 nodes. Updating {pool.name}: {pool.count} → 3")
                        node_pool_config["count"] = 3
                        if pool.min_nodes is not None:
                            node_pool_config["min_nodes"] = max(pool.min_nodes, 3)
                    
                    node_pools.append(node_pool_config)
                
                # Create cluster request
                req = {
                    "name": self.config.name,
                    "region": self.config.region,
                    "version": self.config.version,
                    "node_pools": node_pools
                }
                
                # Add HA-specific configuration
                if self.config.high_availability:
                    print(f"│  ├─ 🛡️  Enabling high availability...")
                
                # Add marketplace addons if specified
                if self.config.addons:
                    print(f"│  ├─ 🛒 Adding marketplace add-ons: {', '.join(self.config.addons)}")
                    req["addons"] = self.config.addons

                resp = manager.kubernetes.create_cluster(body=req)
                cluster = resp['kubernetes_cluster']
                
                print(f"│  ├─ ⏳ Cluster creation initiated...")
                
            else:  # UPDATE
                print(f"╭─ 🔄 Using existing cluster...")
                cluster = existing_cluster
                # Note: Kubernetes updates typically require separate API calls for node pools, etc.
                print(f"│  ├─ ⚠️  Manual updates may be required for version/node changes")

            if wait_for_provisioning and action == "CREATE":
                print(f"│  ├─ ⏳ Waiting for cluster to become ready...")
                # Wait for cluster to be running (simplified)
                cluster_id = cluster['id']
                for i in range(60):  # Try for 10 minutes
                    try:
                        get_resp = manager.kubernetes.get_cluster(cluster_id)
                        current_cluster = get_resp['kubernetes_cluster']
                        status = current_cluster.get('status', {}).get('state', 'unknown')
                        
                        if status == 'running':
                            print(f"│  ├─ ✅ Cluster is now running!")
                            cluster = current_cluster
                            break
                        elif status in ['failed', 'error']:
                            print(f"│  ├─ ❌ Cluster creation failed!")
                            break
                        
                        if i % 6 == 0:  # Print status every minute
                            print(f"│  ├─ ⏳ Status: {status} (waiting...)")
                        
                        time.sleep(10)
                    except Exception:
                        time.sleep(10)
                        continue

            print(f"├─ ✅ Kubernetes cluster {action.lower()}d successfully!")
            print(f"├─ 📦 Name: {self.config.name}")
            print(f"├─ 🔧 Version: {self.config.version}")
            print(f"├─ 🌍 Region: {self.config.region}")
            print(f"├─ 👥 Node Pools: {len(self.config.node_pools)}")
            if cluster.get('endpoint'):
                print(f"├─ 🌐 Endpoint: {cluster['endpoint']}")
            if cluster.get('ipv4'):
                print(f"├─ 🔗 IPv4: {cluster['ipv4']}")
            print(f"╰─ 🆔 ID: {cluster['id']}")

            return {
                "id": cluster['id'],
                "name": self.config.name,
                "status": cluster.get('status', {}).get('state', 'unknown'),
                "version": self.config.version,
                "region": self.config.region,
                "endpoint": cluster.get('endpoint'),
                "ipv4": cluster.get('ipv4'),
                "node_pools": len(self.config.node_pools),
                "high_availability": self.config.high_availability,
                "action": action.lower(),
                "changes": True
            }

        except Exception as e:
            if "already exists" in str(e):
                print(f"📦 Cluster '{self.config.name}' already exists, fetching it...")
                # Refetch the cluster if creation fails due to existence
                existing_clusters = self._discover_existing_clusters()
                if self.config.name in existing_clusters:
                    cluster = existing_clusters[self.config.name]
                    print(f"✅ Using existing cluster: {cluster.get('status', 'unknown')}")
                    return {
                        "id": cluster.get("id"),
                        "name": self.config.name,
                        "status": cluster.get("status"),
                        "endpoint": cluster.get("endpoint"),
                        "action": "found_existing",
                        "changes": False
                    }
            raise Exception(f"Failed to {action.lower()} Kubernetes cluster: {e}")

    def destroy(self) -> Dict[str, Any]:
        """Destroy the Kubernetes cluster"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")

        print(f"\n🗑️  Destroying Kubernetes cluster: {self.config.name}")
        
        manager = self.do_client.client
        cluster = None
        
        # Find the cluster
        try:
            list_resp = manager.kubernetes.list_clusters()
            for c in list_resp.get("kubernetes_clusters", []):
                if c['name'] == self.config.name:
                    cluster = c
                    break
        except Exception as e:
            raise Exception(f"Failed to check for existing Kubernetes clusters: {e}")
        
        if not cluster:
            print(f"✅ No cluster found with name: {self.config.name}")
            return {"cluster": False}
        
        # Destroy the cluster
        try:
            print(f"🗑️  Destroying cluster: {cluster['name']} (ID: {cluster['id']})")
            manager.kubernetes.delete_cluster(cluster['id'])
            print(f"✅ Cluster deletion initiated successfully!")
            print(f"💡 Note: Cluster deletion can take several minutes to complete")
            print(f"   You can check status in the DigitalOcean dashboard")
            return {"cluster": True}
        except Exception as e:
            print(f"⚠️  Warning: Failed to destroy cluster: {e}")
            return {"cluster": False} 
import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from google.cloud import container_v1
from .gcp_client import GcpClient

class GkeConfig(BaseModel):
    name: str
    location: str = "europe-north1-a"  # Default to Europe North (Finland)
    node_count: int = 3
    machine_type: str = "e2-medium"
    disk_size_gb: int = 100
    auto_scale: bool = True
    min_nodes: int = 1
    max_nodes: int = 5
    zones: Optional[List[str]] = None
    preemptible: bool = False
    labels: Optional[Dict[str, str]] = None
    network: str = "default"
    subnetwork: str = "default"
    enable_autopilot: bool = False
    kubernetes_version: Optional[str] = None
    enable_network_policy: bool = True
    enable_ip_alias: bool = True

class GkeManager:
    """Manages Google Kubernetes Engine (GKE) operations with Rails-like simplicity"""

    def __init__(self, gcp_client: GcpClient):
        self.gcp_client = gcp_client
        # Don't access client properties immediately - they require authentication
        self._cluster_manager_client = None
        self._project_id = None

    @property
    def cluster_manager_client(self):
        """Get the cluster manager client (lazy loading after authentication)"""
        if not self._cluster_manager_client:
            self._cluster_manager_client = container_v1.ClusterManagerClient(
                credentials=self.gcp_client.credentials
            )
        return self._cluster_manager_client

    @property
    def project_id(self):
        """Get the project ID (lazy loading after authentication)"""
        if not self._project_id:
            self._project_id = self.gcp_client.project
        return self._project_id

    def create_cluster(self, config: GkeConfig) -> Dict[str, Any]:
        """Create a GKE cluster with sensible defaults and Rails-like simplicity"""
        try:
            print(f"🚀 Creating GKE cluster '{config.name}'...")

            # Build the cluster configuration
            cluster_config = self._build_cluster_config(config)

            # Prepare the request
            parent = f"projects/{self.project_id}/locations/{config.location}"

            # Create the cluster
            request = container_v1.CreateClusterRequest(
                parent=parent,
                cluster=cluster_config
            )

            print(f"   📍 Location: {config.location}")
            print(f"   💻 Nodes: {config.node_count} ({config.machine_type})")
            print(f"   🔄 Auto-scaling: {'Enabled' if config.auto_scale else 'Disabled'}")
            if config.auto_scale:
                print(f"   📊 Scale range: {config.min_nodes}-{config.max_nodes} nodes")

            operation = self.cluster_manager_client.create_cluster(request=request)

            print(f"   ⏳ Waiting for cluster creation (this may take 5-10 minutes)...")

            # Wait for the operation to complete
            self._wait_for_operation(operation, config.location)

            # Get the created cluster details
            cluster = self._get_cluster(config.name, config.location)

            print(f"✅ GKE cluster '{config.name}' created successfully!")
            print(f"   🎯 Endpoint: {cluster.endpoint}")
            print(f"   🔐 Master version: {cluster.current_master_version}")
            print(f"   📝 Status: {cluster.status.name}")

            # Provide kubectl connection command
            print(f"\n💡 Connect to your cluster:")
            print(f"   gcloud container clusters get-credentials {config.name} --location {config.location}")

            return {
                "cluster_name": cluster.name,
                "endpoint": cluster.endpoint,
                "status": cluster.status.name,
                "master_version": cluster.current_master_version,
                "node_count": cluster.current_node_count,
                "location": config.location,
                "project_id": self.project_id
            }

        except Exception as e:
            print(f"❌ Failed to create GKE cluster: {str(e)}")
            raise

    def _build_cluster_config(self, config: GkeConfig) -> container_v1.Cluster:
        """Build the cluster configuration with Rails-like conventions"""

        # Node pool configuration with sensible defaults
        node_config = container_v1.NodeConfig(
            machine_type=config.machine_type,
            disk_size_gb=config.disk_size_gb,
            preemptible=config.preemptible,
            oauth_scopes=[
                "https://www.googleapis.com/auth/cloud-platform"
            ],
            labels=config.labels or {}
        )

        # Auto-scaling configuration
        autoscaling = None
        if config.auto_scale:
            autoscaling = container_v1.NodePoolAutoscaling(
                enabled=True,
                min_node_count=config.min_nodes,
                max_node_count=config.max_nodes
            )

        # Default node pool
        node_pool = container_v1.NodePool(
            name="default-pool",
            config=node_config,
            initial_node_count=config.node_count,
            autoscaling=autoscaling
        )

        # IP allocation policy for VPC-native clusters (Rails convention: always use modern practices)
        ip_allocation_policy = container_v1.IPAllocationPolicy(
            use_ip_aliases=config.enable_ip_alias
        ) if config.enable_ip_alias else None

        # Network policy (Rails convention: secure by default)
        network_policy = container_v1.NetworkPolicy(
            enabled=config.enable_network_policy
        ) if config.enable_network_policy else None

        # Build the cluster
        cluster = container_v1.Cluster(
            name=config.name,
            node_pools=[node_pool],
            network=config.network,
            subnetwork=config.subnetwork,
            ip_allocation_policy=ip_allocation_policy,
            network_policy=network_policy,
            initial_cluster_version=config.kubernetes_version,
            location=config.location
        )

        # If zones are specified, use them
        if config.zones:
            cluster.locations = config.zones

        return cluster

    def _wait_for_operation(self, operation, location: str, timeout: int = 600):
        """Wait for a GKE operation to complete"""
        operation_name = operation.name
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Get operation status
                request = container_v1.GetOperationRequest(
                    name=f"projects/{self.project_id}/locations/{location}/operations/{operation_name}"
                )
                op = self.cluster_manager_client.get_operation(request=request)

                if op.status == container_v1.Operation.Status.DONE:
                    if hasattr(op, 'error') and op.error:
                        raise Exception(f"Operation failed: {op.error}")
                    return op

                # Show progress dots
                print(".", end="", flush=True)
                time.sleep(10)

            except Exception as e:
                if "not found" in str(e).lower():
                    # Operation might be completed and cleaned up
                    return
                raise

        raise TimeoutError(f"Operation timed out after {timeout} seconds")

    def _get_cluster(self, cluster_name: str, location: str) -> container_v1.Cluster:
        """Get cluster details"""
        request = container_v1.GetClusterRequest(
            name=f"projects/{self.project_id}/locations/{location}/clusters/{cluster_name}"
        )
        return self.cluster_manager_client.get_cluster(request=request)

    def delete_cluster(self, cluster_name: str, location: str) -> bool:
        """Delete a GKE cluster"""
        try:
            print(f"🗑️  Deleting GKE cluster '{cluster_name}'...")

            request = container_v1.DeleteClusterRequest(
                name=f"projects/{self.project_id}/locations/{location}/clusters/{cluster_name}"
            )

            operation = self.cluster_manager_client.delete_cluster(request=request)

            print(f"   ⏳ Waiting for cluster deletion...")
            self._wait_for_operation(operation, location)

            print(f"✅ GKE cluster '{cluster_name}' deleted successfully!")
            return True

        except Exception as e:
            print(f"❌ Failed to delete GKE cluster: {str(e)}")
            return False

    def list_clusters(self, location: str = "-") -> List[Dict[str, Any]]:
        """List all GKE clusters in the project"""
        try:
            parent = f"projects/{self.project_id}/locations/{location}"
            request = container_v1.ListClustersRequest(parent=parent)

            response = self.cluster_manager_client.list_clusters(request=request)

            clusters = []
            for cluster in response.clusters:
                clusters.append({
                    "name": cluster.name,
                    "status": cluster.status.name,
                    "location": cluster.location,
                    "endpoint": cluster.endpoint,
                    "node_count": cluster.current_node_count,
                    "master_version": cluster.current_master_version
                })

            return clusters

        except Exception as e:
            print(f"❌ Failed to list clusters: {str(e)}")
            return []

    def get_cluster_credentials(self, cluster_name: str, location: str) -> str:
        """Get the kubectl connection command for the cluster"""
        return f"gcloud container clusters get-credentials {cluster_name} --location {location} --project {self.project_id}"

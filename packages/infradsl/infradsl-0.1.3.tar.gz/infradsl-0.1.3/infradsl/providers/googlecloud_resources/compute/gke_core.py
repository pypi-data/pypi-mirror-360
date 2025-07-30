"""
GCP GKE Core Implementation

Core attributes and authentication for Google Kubernetes Engine (GKE).
Provides the foundation for the modular Kubernetes cluster system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class GKECore(BaseGcpResource):
    """
    Core class for Google Kubernetes Engine functionality.
    
    This class provides:
    - Basic cluster attributes and configuration
    - Authentication setup
    - Common utilities for Kubernetes operations
    - Node pool and networking management foundations
    """
    
    def __init__(self, name: str):
        """Initialize GKE core with cluster name"""
        super().__init__(name)
        
        # Core cluster attributes
        self.cluster_name = name
        self.cluster_description = f"GKE cluster for {name}"
        self.cluster_type = "standard"  # standard, autopilot
        
        # Location and region settings
        self.location = "us-central1-a"  # Zone or region
        self.location_type = "zonal"     # zonal, regional
        self.zones = []                  # Specific zones for regional clusters
        
        # Kubernetes configuration
        self.kubernetes_version = None  # Latest if None
        self.master_version = None
        self.node_version = None
        self.release_channel = "REGULAR"  # RAPID, REGULAR, STABLE, UNSPECIFIED
        
        # Node pool configuration
        self.node_pools = []
        self.initial_node_count = 3
        self.default_node_pool_enabled = True
        
        # Default node pool settings
        self.machine_type = "e2-medium"
        self.disk_size_gb = 100
        self.disk_type = "pd-standard"  # pd-standard, pd-ssd
        self.image_type = "COS_CONTAINERD"  # COS, COS_CONTAINERD, UBUNTU_CONTAINERD
        self.boot_disk_kms_key = None
        
        # Auto-scaling configuration
        self.auto_scaling_enabled = False
        self.min_node_count = 1
        self.max_node_count = 10
        self.enable_autoscaling = False
        
        # Auto-upgrade and auto-repair
        self.auto_upgrade = True
        self.auto_repair = True
        
        # Network configuration
        self.network = "default"
        self.subnetwork = "default"
        self.enable_ip_alias = True
        self.cluster_ipv4_cidr = None
        self.services_ipv4_cidr = None
        self.cluster_secondary_range_name = None
        self.services_secondary_range_name = None
        self.enable_private_nodes = False
        self.enable_private_endpoint = False
        self.master_ipv4_cidr_block = None
        
        # Security configuration
        self.enable_legacy_abac = False
        self.enable_network_policy = False
        self.enable_pod_security_policy = False
        self.enable_shielded_nodes = True
        self.enable_workload_identity = False
        self.workload_pool = None
        
        # Authentication and authorization
        self.master_auth_networks = []
        self.client_certificate_config = {"issue_client_certificate": False}
        self.enable_basic_auth = False
        self.master_username = None
        self.master_password = None
        
        # Monitoring and logging
        self.enable_cloud_logging = True
        self.logging_service = "logging.googleapis.com/kubernetes"
        self.enable_cloud_monitoring = True
        self.monitoring_service = "monitoring.googleapis.com/kubernetes"
        self.enable_network_policy_logging = False
        
        # Add-ons configuration
        self.http_load_balancing_disabled = False
        self.horizontal_pod_autoscaling_disabled = False
        self.kubernetes_dashboard_disabled = True
        self.network_policy_config_disabled = True
        self.dns_cache_config_enabled = False
        self.config_connector_config_enabled = False
        
        # Cost optimization
        self.preemptible_nodes = False
        self.spot_instances = False
        self.enable_autopilot = False
        
        # Maintenance configuration
        self.maintenance_window = None
        self.maintenance_exclusions = []
        
        # Resource labels and metadata
        self.cluster_labels = {}
        self.node_labels = {}
        self.node_tags = []
        self.node_taints = []
        
        # Service account configuration
        self.service_account = None
        self.oauth_scopes = [
            "https://www.googleapis.com/auth/devstorage.read_only",
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring",
            "https://www.googleapis.com/auth/servicecontrol",
            "https://www.googleapis.com/auth/service.management.readonly",
            "https://www.googleapis.com/auth/trace.append"
        ]
        
        # State tracking
        self.cluster_exists = False
        self.cluster_created = False
        self.cluster_ready = False
        
    def _initialize_managers(self):
        """Initialize GKE-specific managers"""
        # Will be set up after authentication
        self.gke_manager = None
        self.container_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Import here to avoid circular imports
        from ...googlecloud_managers.gke_manager import GkeManager
        
        self.gke_manager = GkeManager(self.gcp_client)
        
        # Set up project context
        self.project_id = self.project_id or self.gcp_client.project_id
        
    def _is_valid_location(self, location: str) -> bool:
        """Check if location is valid for GKE"""
        # GKE locations can be zones (e.g., us-central1-a) or regions (e.g., us-central1)
        valid_regions = [
            "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west3", "us-west4",
            "europe-north1", "europe-west1", "europe-west2", "europe-west3", "europe-west4", "europe-west6",
            "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2", "asia-northeast3",
            "asia-south1", "asia-southeast1", "asia-southeast2", "australia-southeast1"
        ]
        
        # Check if it's a region
        if location in valid_regions:
            return True
            
        # Check if it's a zone (region + zone suffix)
        for region in valid_regions:
            if location.startswith(f"{region}-") and len(location) > len(region) + 1:
                return True
                
        return False
        
    def _is_valid_machine_type(self, machine_type: str) -> bool:
        """Check if machine type is valid"""
        valid_types = [
            # E2 series (cost-optimized)
            "e2-micro", "e2-small", "e2-medium", "e2-standard-2", "e2-standard-4", "e2-standard-8", "e2-standard-16", "e2-standard-32",
            "e2-highmem-2", "e2-highmem-4", "e2-highmem-8", "e2-highmem-16",
            "e2-highcpu-2", "e2-highcpu-4", "e2-highcpu-8", "e2-highcpu-16", "e2-highcpu-32",
            
            # N1 series (balanced)
            "n1-standard-1", "n1-standard-2", "n1-standard-4", "n1-standard-8", "n1-standard-16", "n1-standard-32", "n1-standard-64", "n1-standard-96",
            "n1-highmem-2", "n1-highmem-4", "n1-highmem-8", "n1-highmem-16", "n1-highmem-32", "n1-highmem-64", "n1-highmem-96",
            "n1-highcpu-2", "n1-highcpu-4", "n1-highcpu-8", "n1-highcpu-16", "n1-highcpu-32", "n1-highcpu-64", "n1-highcpu-96",
            
            # N2 series (latest generation)
            "n2-standard-2", "n2-standard-4", "n2-standard-8", "n2-standard-16", "n2-standard-32", "n2-standard-48", "n2-standard-64", "n2-standard-80", "n2-standard-128",
            "n2-highmem-2", "n2-highmem-4", "n2-highmem-8", "n2-highmem-16", "n2-highmem-32", "n2-highmem-48", "n2-highmem-64", "n2-highmem-80", "n2-highmem-96", "n2-highmem-128",
            "n2-highcpu-2", "n2-highcpu-4", "n2-highcpu-8", "n2-highcpu-16", "n2-highcpu-32", "n2-highcpu-48", "n2-highcpu-64", "n2-highcpu-80", "n2-highcpu-96",
            
            # C2 series (compute-optimized)
            "c2-standard-4", "c2-standard-8", "c2-standard-16", "c2-standard-30", "c2-standard-60"
        ]
        return machine_type in valid_types
        
    def _is_valid_kubernetes_version(self, version: str) -> bool:
        """Check if Kubernetes version format is valid"""
        if not version:
            return True  # None/empty means latest
            
        # Version should be in format like "1.24", "1.24.8-gke.2000", etc.
        import re
        pattern = r'^(\d+\.\d+)(\.\d+)?(-gke\.\d+)?$'
        return bool(re.match(pattern, version))
        
    def _is_valid_release_channel(self, channel: str) -> bool:
        """Check if release channel is valid"""
        valid_channels = ["RAPID", "REGULAR", "STABLE", "UNSPECIFIED"]
        return channel in valid_channels
        
    def _is_valid_image_type(self, image_type: str) -> bool:
        """Check if node image type is valid"""
        valid_types = ["COS", "COS_CONTAINERD", "UBUNTU_CONTAINERD", "WINDOWS_LTSC", "WINDOWS_SAC"]
        return image_type in valid_types
        
    def _validate_cluster_config(self, config: Dict[str, Any]) -> bool:
        """Validate GKE cluster configuration"""
        required_fields = ["cluster_name", "location"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate location
        if not self._is_valid_location(config["location"]):
            return False
            
        # Validate machine type if specified
        if "machine_type" in config and not self._is_valid_machine_type(config["machine_type"]):
            return False
            
        # Validate Kubernetes version if specified
        if "kubernetes_version" in config and not self._is_valid_kubernetes_version(config["kubernetes_version"]):
            return False
            
        return True
        
    def _validate_node_pool_config(self, pool_config: Dict[str, Any]) -> bool:
        """Validate node pool configuration"""
        required_fields = ["name"]
        
        for field in required_fields:
            if field not in pool_config:
                return False
                
        # Validate machine type
        if "machine_type" in pool_config and not self._is_valid_machine_type(pool_config["machine_type"]):
            return False
            
        # Validate node count
        initial_node_count = pool_config.get("initial_node_count", 1)
        if not (0 <= initial_node_count <= 1000):
            return False
            
        # Validate auto-scaling if enabled
        if pool_config.get("autoscaling", {}).get("enabled", False):
            min_nodes = pool_config["autoscaling"].get("min_node_count", 0)
            max_nodes = pool_config["autoscaling"].get("max_node_count", 1)
            if not (0 <= min_nodes <= max_nodes <= 1000):
                return False
                
        return True
        
    def _get_common_machine_types(self) -> List[str]:
        """Get list of common GKE machine types"""
        return [
            # Cost-optimized
            "e2-micro",
            "e2-small",
            "e2-medium", 
            "e2-standard-2",
            "e2-standard-4",
            
            # Balanced
            "n1-standard-1",
            "n1-standard-2",
            "n1-standard-4",
            "n1-standard-8",
            
            # Latest generation
            "n2-standard-2",
            "n2-standard-4",
            "n2-standard-8",
            
            # High memory
            "n1-highmem-2",
            "n1-highmem-4",
            "n2-highmem-2",
            "n2-highmem-4",
            
            # High CPU
            "n1-highcpu-4",
            "n1-highcpu-8",
            "c2-standard-4",
            "c2-standard-8"
        ]
        
    def _get_machine_type_description(self, machine_type: str) -> str:
        """Get description for a machine type"""
        descriptions = {
            "e2-micro": "Micro instance (0.25-2 vCPUs, 1GB RAM) - Cost optimized",
            "e2-small": "Small instance (0.5-2 vCPUs, 2GB RAM) - Cost optimized", 
            "e2-medium": "Medium instance (1-2 vCPUs, 4GB RAM) - Cost optimized",
            "e2-standard-2": "Standard instance (2 vCPUs, 8GB RAM) - Cost optimized",
            "e2-standard-4": "Standard instance (4 vCPUs, 16GB RAM) - Cost optimized",
            "n1-standard-1": "Standard instance (1 vCPU, 3.75GB RAM) - Balanced",
            "n1-standard-2": "Standard instance (2 vCPUs, 7.5GB RAM) - Balanced",
            "n1-standard-4": "Standard instance (4 vCPUs, 15GB RAM) - Balanced",
            "n2-standard-2": "Standard instance (2 vCPUs, 8GB RAM) - Latest generation",
            "n2-standard-4": "Standard instance (4 vCPUs, 16GB RAM) - Latest generation",
            "c2-standard-4": "Compute-optimized instance (4 vCPUs, 16GB RAM) - High performance"
        }
        return descriptions.get(machine_type, machine_type)
        
    def _estimate_gke_cost(self) -> float:
        """Estimate monthly cost for GKE cluster"""
        # GKE pricing (simplified)
        
        # Cluster management fee
        cluster_management_fee = 0.10 * 24 * 30  # $0.10 per hour for standard clusters
        
        # Node costs (estimated per machine type per hour)
        node_cost_map = {
            'e2-micro': 0.008,
            'e2-small': 0.017,
            'e2-medium': 0.034,
            'e2-standard-2': 0.067,
            'e2-standard-4': 0.134,
            'n1-standard-1': 0.048,
            'n1-standard-2': 0.095,
            'n1-standard-4': 0.190,
            'n1-standard-8': 0.380,
            'n2-standard-2': 0.100,
            'n2-standard-4': 0.200,
            'n2-highmem-2': 0.118,
            'n2-highmem-4': 0.236,
            'c2-standard-4': 0.225,
            'c2-standard-8': 0.450
        }
        
        base_node_cost = node_cost_map.get(self.machine_type, 0.100)
        
        # Calculate node costs
        if self.auto_scaling_enabled:
            # Use average of min and max for estimation
            avg_nodes = (self.min_node_count + self.max_node_count) / 2
        else:
            avg_nodes = self.initial_node_count
            
        node_cost = base_node_cost * 24 * 30 * avg_nodes
        
        # Apply preemptible discount
        if self.preemptible_nodes or self.spot_instances:
            node_cost *= 0.2  # 80% discount
            
        # Disk costs (estimated)
        disk_cost_per_gb = 0.04 if self.disk_type == "pd-standard" else 0.17  # pd-ssd
        disk_cost = disk_cost_per_gb * self.disk_size_gb * avg_nodes
        
        # Load balancer costs (if used)
        load_balancer_cost = 18.25  # $18.25/month for Network Load Balancer
        
        total_cost = cluster_management_fee + node_cost + disk_cost
        
        return total_cost
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of GKE cluster from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get cluster information
            if self.gke_manager:
                cluster_info = self.gke_manager.get_cluster_info(
                    self.cluster_name, self.location
                )
                
                if cluster_info:
                    return {
                        "exists": True,
                        "cluster_name": self.cluster_name,
                        "location": self.location,
                        "status": cluster_info.get("status", "UNKNOWN"),
                        "current_master_version": cluster_info.get("currentMasterVersion"),
                        "current_node_version": cluster_info.get("currentNodeVersion"),
                        "current_node_count": cluster_info.get("currentNodeCount", 0),
                        "initial_node_count": cluster_info.get("initialNodeCount", 0),
                        "node_pools": cluster_info.get("nodePools", []),
                        "node_pools_count": len(cluster_info.get("nodePools", [])),
                        "endpoint": cluster_info.get("endpoint"),
                        "network": cluster_info.get("network"),
                        "subnetwork": cluster_info.get("subnetwork"),
                        "cluster_ipv4_cidr": cluster_info.get("clusterIpv4Cidr"),
                        "services_ipv4_cidr": cluster_info.get("servicesIpv4Cidr"),
                        "locations": cluster_info.get("locations", []),
                        "zone": cluster_info.get("zone"),
                        "logging_service": cluster_info.get("loggingService"),
                        "monitoring_service": cluster_info.get("monitoringService"),
                        "addons_config": cluster_info.get("addonsConfig", {}),
                        "master_auth": cluster_info.get("masterAuth", {}),
                        "labels": cluster_info.get("resourceLabels", {}),
                        "legacy_abac": cluster_info.get("legacyAbac", {}).get("enabled", False),
                        "network_policy": cluster_info.get("networkPolicy", {}).get("enabled", False),
                        "ip_allocation_policy": cluster_info.get("ipAllocationPolicy", {}),
                        "private_cluster_config": cluster_info.get("privateClusterConfig", {}),
                        "workload_identity_config": cluster_info.get("workloadIdentityConfig", {}),
                        "shielded_nodes": cluster_info.get("shieldedNodes", {}).get("enabled", False),
                        "release_channel": cluster_info.get("releaseChannel", {}).get("channel", "UNSPECIFIED"),
                        "create_time": cluster_info.get("createTime"),
                        "self_link": cluster_info.get("selfLink")
                    }
                else:
                    return {
                        "exists": False,
                        "cluster_name": self.cluster_name,
                        "location": self.location
                    }
            else:
                return {
                    "exists": False,
                    "cluster_name": self.cluster_name,
                    "location": self.location,
                    "error": "GKE manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch GKE state: {str(e)}")
            return {
                "exists": False,
                "cluster_name": self.cluster_name,
                "location": self.location,
                "error": str(e)
            }
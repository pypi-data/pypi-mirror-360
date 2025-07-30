"""
GCP GKE Configuration Mixin

Chainable configuration methods for Google Kubernetes Engine (GKE).
Provides Rails-like method chaining for fluent cluster configuration.
"""

from typing import Dict, Any, List, Optional


class GKEConfigurationMixin:
    """
    Mixin for GKE configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Cluster location and version configuration
    - Node pool and machine type settings
    - Network and security configuration
    - Auto-scaling and maintenance settings
    - Add-ons and monitoring configuration
    """
    
    def description(self, description: str):
        """Set description for the GKE cluster"""
        self.cluster_description = description
        return self
        
    def project(self, project_id: str):
        """Set project ID for GKE operations - Rails convenience"""
        self.project_id = project_id
        return self
        
    def location(self, location: str):
        """Set cluster location (zone or region)"""
        if not self._is_valid_location(location):
            print(f"⚠️  Warning: Invalid location '{location}'. Use us-central1-a, us-central1, etc.")
        self.location = location
        self.location_type = "regional" if "-" in location and len(location.split("-")) == 2 else "zonal"
        return self
        
    def region(self, region: str):
        """Set cluster to regional (multi-zone) configuration"""
        return self.location(region)
        
    def zone(self, zone: str):
        """Set cluster to zonal configuration"""
        return self.location(zone)
        
    def zones(self, zones: List[str]):
        """Set specific zones for regional clusters"""
        self.zones = zones
        return self
        
    # Kubernetes version configuration
    def kubernetes_version(self, version: str):
        """Set Kubernetes version"""
        if not self._is_valid_kubernetes_version(version):
            print(f"⚠️  Warning: Invalid Kubernetes version '{version}'. Use format like '1.24.8-gke.2000'")
        self.kubernetes_version = version
        self.master_version = version
        self.node_version = version
        return self
        
    def master_version(self, version: str):
        """Set master Kubernetes version separately"""
        self.master_version = version
        return self
        
    def node_version(self, version: str):
        """Set node Kubernetes version separately"""
        self.node_version = version
        return self
        
    def release_channel(self, channel: str):
        """Set release channel (RAPID, REGULAR, STABLE, UNSPECIFIED)"""
        if not self._is_valid_release_channel(channel):
            print(f"⚠️  Warning: Invalid release channel '{channel}'. Use RAPID, REGULAR, STABLE, or UNSPECIFIED")
        self.release_channel = channel
        return self
        
    # Node pool configuration
    def nodes(self, count: int):
        """Set initial node count"""
        if not (0 <= count <= 1000):
            print(f"⚠️  Warning: Invalid node count {count}. Must be between 0-1000")
        self.initial_node_count = count
        return self
        
    def machine_type(self, machine_type: str):
        """Set machine type for nodes"""
        if not self._is_valid_machine_type(machine_type):
            print(f"⚠️  Warning: Invalid machine type '{machine_type}'. Use e2-medium, n1-standard-2, etc.")
        self.machine_type = machine_type
        return self
        
    def disk_size(self, size_gb: int):
        """Set disk size for nodes in GB"""
        if not (10 <= size_gb <= 65536):
            print(f"⚠️  Warning: Invalid disk size {size_gb}GB. Must be between 10-65536 GB")
        self.disk_size_gb = size_gb
        return self
        
    def disk_type(self, disk_type: str):
        """Set disk type (pd-standard, pd-ssd)"""
        valid_types = ["pd-standard", "pd-ssd"]
        if disk_type not in valid_types:
            print(f"⚠️  Warning: Invalid disk type '{disk_type}'. Use pd-standard or pd-ssd")
        self.disk_type = disk_type
        return self
        
    def image_type(self, image_type: str):
        """Set node image type"""
        if not self._is_valid_image_type(image_type):
            print(f"⚠️  Warning: Invalid image type '{image_type}'. Use COS_CONTAINERD, UBUNTU_CONTAINERD, etc.")
        self.image_type = image_type
        return self
        
    # Auto-scaling configuration
    def auto_scaling(self, enabled: bool = True, min_nodes: int = 1, max_nodes: int = 10):
        """Configure cluster auto-scaling - Rails convenience"""
        self.auto_scaling_enabled = enabled
        self.enable_autoscaling = enabled
        self.min_node_count = min_nodes
        self.max_node_count = max_nodes
        return self
        
    def min_nodes(self, count: int):
        """Set minimum nodes for auto-scaling"""
        if not (0 <= count <= 1000):
            print(f"⚠️  Warning: Invalid min nodes {count}. Must be between 0-1000")
        self.min_node_count = count
        return self
        
    def max_nodes(self, count: int):
        """Set maximum nodes for auto-scaling"""
        if not (1 <= count <= 1000):
            print(f"⚠️  Warning: Invalid max nodes {count}. Must be between 1-1000")
        self.max_node_count = count
        return self
        
    def preemptible(self, enabled: bool = True):
        """Enable preemptible nodes for cost savings"""
        self.preemptible_nodes = enabled
        return self
        
    def spot_instances(self, enabled: bool = True):
        """Enable spot instances for cost savings"""
        self.spot_instances = enabled
        return self
        
    # Network configuration
    def network(self, network: str, subnetwork: str = None):
        """Set VPC network configuration"""
        self.network = network
        if subnetwork:
            self.subnetwork = subnetwork
        return self
        
    def subnetwork(self, subnetwork: str):
        """Set subnetwork for cluster"""
        self.subnetwork = subnetwork
        return self
        
    def enable_ip_alias(self, enabled: bool = True):
        """Enable VPC-native networking with IP aliasing"""
        self.enable_ip_alias = enabled
        return self
        
    def cluster_ipv4_cidr(self, cidr: str):
        """Set cluster IPv4 CIDR range"""
        self.cluster_ipv4_cidr = cidr
        return self
        
    def services_ipv4_cidr(self, cidr: str):
        """Set services IPv4 CIDR range"""
        self.services_ipv4_cidr = cidr
        return self
        
    def private_cluster(self, enabled: bool = True, master_cidr: str = "172.16.0.0/28"):
        """Configure private cluster with private endpoints"""
        self.enable_private_nodes = enabled
        self.enable_private_endpoint = enabled
        if enabled:
            self.master_ipv4_cidr_block = master_cidr
        return self
        
    def private_nodes(self, enabled: bool = True):
        """Enable private nodes only"""
        self.enable_private_nodes = enabled
        return self
        
    def private_endpoint(self, enabled: bool = True):
        """Enable private master endpoint"""
        self.enable_private_endpoint = enabled
        return self
        
    # Security configuration
    def enable_shielded_nodes(self, enabled: bool = True):
        """Enable shielded GKE nodes for enhanced security"""
        self.enable_shielded_nodes = enabled
        return self
        
    def enable_workload_identity(self, enabled: bool = True):
        """Enable Workload Identity for secure pod-to-GCP access"""
        self.enable_workload_identity = enabled
        if enabled and self.project_id:
            self.workload_pool = f"{self.project_id}.svc.id.goog"
        return self
        
    def enable_network_policy(self, enabled: bool = True):
        """Enable network policy for pod-to-pod security"""
        self.enable_network_policy = enabled
        return self
        
    def enable_pod_security_policy(self, enabled: bool = True):
        """Enable Pod Security Policy (deprecated)"""
        self.enable_pod_security_policy = enabled
        return self
        
    def master_authorized_networks(self, networks: List[Dict[str, str]]):
        """Set master authorized networks for API server access"""
        self.master_auth_networks = networks
        return self
        
    def authorized_network(self, cidr: str, display_name: str = ""):
        """Add single authorized network - Rails convenience"""
        self.master_auth_networks.append({
            "cidr_block": cidr,
            "display_name": display_name or f"Authorized network {cidr}"
        })
        return self
        
    # Monitoring and logging
    def enable_monitoring(self, enabled: bool = True):
        """Enable Cloud Monitoring"""
        self.enable_cloud_monitoring = enabled
        self.monitoring_service = "monitoring.googleapis.com/kubernetes" if enabled else None
        return self
        
    def enable_logging(self, enabled: bool = True):
        """Enable Cloud Logging"""
        self.enable_cloud_logging = enabled
        self.logging_service = "logging.googleapis.com/kubernetes" if enabled else None
        return self
        
    def monitoring_service(self, service: str):
        """Set monitoring service endpoint"""
        self.monitoring_service = service
        return self
        
    def logging_service(self, service: str):
        """Set logging service endpoint"""
        self.logging_service = service
        return self
        
    # Add-ons configuration
    def enable_http_load_balancing(self, enabled: bool = True):
        """Enable HTTP Load Balancing add-on"""
        self.http_load_balancing_disabled = not enabled
        return self
        
    def enable_horizontal_pod_autoscaling(self, enabled: bool = True):
        """Enable Horizontal Pod Autoscaling add-on"""
        self.horizontal_pod_autoscaling_disabled = not enabled
        return self
        
    def enable_kubernetes_dashboard(self, enabled: bool = False):
        """Enable Kubernetes Dashboard (not recommended for production)"""
        self.kubernetes_dashboard_disabled = not enabled
        return self
        
    def enable_dns_cache(self, enabled: bool = True):
        """Enable NodeLocal DNSCache add-on"""
        self.dns_cache_config_enabled = enabled
        return self
        
    def enable_config_connector(self, enabled: bool = True):
        """Enable Config Connector add-on"""
        self.config_connector_config_enabled = enabled
        return self
        
    # Maintenance configuration
    def maintenance_window(self, start_time: str, duration: str = "4h"):
        """Set maintenance window (HH:MM format, UTC)"""
        self.maintenance_window = {
            "start_time": start_time,
            "duration": duration
        }
        return self
        
    def maintenance_exclusion(self, name: str, start_time: str, end_time: str):
        """Add maintenance exclusion period"""
        self.maintenance_exclusions.append({
            "name": name,
            "start_time": start_time,
            "end_time": end_time
        })
        return self
        
    # Service account configuration
    def service_account(self, email: str):
        """Set service account for nodes"""
        self.service_account = email
        return self
        
    def oauth_scopes(self, scopes: List[str]):
        """Set OAuth scopes for nodes"""
        self.oauth_scopes = scopes
        return self
        
    def default_scopes(self):
        """Use default OAuth scopes for nodes"""
        self.oauth_scopes = [
            "https://www.googleapis.com/auth/devstorage.read_only",
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring",
            "https://www.googleapis.com/auth/servicecontrol",
            "https://www.googleapis.com/auth/service.management.readonly",
            "https://www.googleapis.com/auth/trace.append"
        ]
        return self
        
    def full_scopes(self):
        """Use full OAuth scopes for nodes (less secure)"""
        self.oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        return self
        
    # Labels and metadata
    def labels(self, labels: Dict[str, str]):
        """Add cluster labels"""
        self.cluster_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual cluster label - Rails convenience"""
        self.cluster_labels[key] = value
        return self
        
    def node_labels(self, labels: Dict[str, str]):
        """Add node labels"""
        self.node_labels.update(labels)
        return self
        
    def node_label(self, key: str, value: str):
        """Add individual node label - Rails convenience"""
        self.node_labels[key] = value
        return self
        
    def node_tags(self, tags: List[str]):
        """Set network tags for nodes"""
        self.node_tags = tags
        return self
        
    def node_tag(self, tag: str):
        """Add individual node tag - Rails convenience"""
        self.node_tags.append(tag)
        return self
        
    def node_taints(self, taints: List[Dict[str, str]]):
        """Set node taints"""
        self.node_taints = taints
        return self
        
    def node_taint(self, key: str, value: str, effect: str = "NoSchedule"):
        """Add individual node taint - Rails convenience"""
        self.node_taints.append({
            "key": key,
            "value": value,
            "effect": effect
        })
        return self
        
    # Environment and cluster type configurations
    def development(self):
        """Configure for development environment - Rails convention"""
        return (self.machine_type("e2-medium")
                .nodes(2)
                .auto_scaling(True, 1, 5)
                .disk_size(50)
                .disk_type("pd-standard")
                .preemptible(True)
                .label("environment", "development")
                .label("cost-optimization", "enabled"))
                
    def staging(self):
        """Configure for staging environment - Rails convention"""
        return (self.machine_type("n1-standard-2")
                .nodes(3)
                .auto_scaling(True, 2, 8)
                .disk_size(100)
                .disk_type("pd-ssd")
                .enable_monitoring(True)
                .enable_logging(True)
                .label("environment", "staging")
                .label("testing", "enabled"))
                
    def production(self):
        """Configure for production environment - Rails convention"""
        return (self.machine_type("n1-standard-4")
                .nodes(5)
                .auto_scaling(True, 3, 20)
                .disk_size(200)
                .disk_type("pd-ssd")
                .enable_monitoring(True)
                .enable_logging(True)
                .enable_shielded_nodes(True)
                .enable_workload_identity(True)
                .enable_network_policy(True)
                .private_nodes(True)
                .label("environment", "production")
                .label("security", "enhanced"))
                
    # Cluster type configurations
    def standard_cluster(self):
        """Configure as standard GKE cluster"""
        self.cluster_type = "standard"
        return self
        
    def autopilot_cluster(self):
        """Configure as GKE Autopilot cluster"""
        self.cluster_type = "autopilot"
        self.enable_autopilot = True
        return self
        
    # Common use case configurations
    def web_workloads(self):
        """Configure for web workloads - Rails convenience"""
        return (self.machine_type("n1-standard-2")
                .auto_scaling(True, 2, 10)
                .enable_http_load_balancing(True)
                .enable_horizontal_pod_autoscaling(True)
                .enable_monitoring(True)
                .label("workload-type", "web"))
                
    def batch_workloads(self):
        """Configure for batch workloads - Rails convenience"""
        return (self.machine_type("n1-standard-4")
                .auto_scaling(True, 0, 50)
                .preemptible(True)
                .label("workload-type", "batch"))
                
    def ml_workloads(self):
        """Configure for ML workloads - Rails convenience"""
        return (self.machine_type("n1-standard-8")
                .auto_scaling(True, 1, 20)
                .disk_size(500)
                .disk_type("pd-ssd")
                .label("workload-type", "ml"))
                
    def microservices(self):
        """Configure for microservices - Rails convenience"""
        return (self.machine_type("n1-standard-2")
                .auto_scaling(True, 3, 15)
                .enable_network_policy(True)
                .enable_workload_identity(True)
                .label("workload-type", "microservices"))
                
    # Cost optimization configurations
    def cost_optimized(self):
        """Configure for cost optimization"""
        return (self.machine_type("e2-medium")
                .preemptible(True)
                .disk_type("pd-standard")
                .auto_scaling(True, 1, 5)
                .label("optimization", "cost"))
                
    def performance_optimized(self):
        """Configure for performance optimization"""
        return (self.machine_type("n2-standard-4")
                .disk_type("pd-ssd")
                .auto_scaling(True, 5, 20)
                .enable_dns_cache(True)
                .label("optimization", "performance"))
                
    def security_optimized(self):
        """Configure for security optimization"""
        return (self.enable_shielded_nodes(True)
                .enable_workload_identity(True)
                .enable_network_policy(True)
                .private_cluster(True)
                .enable_pod_security_policy(True)
                .label("optimization", "security"))
                
    # Node pool management
    def add_node_pool(self, pool_config: Dict[str, Any]):
        """Add additional node pool"""
        if self._validate_node_pool_config(pool_config):
            self.node_pools.append(pool_config)
        return self
        
    def node_pool(self, name: str, machine_type: str = None, nodes: int = 3):
        """Add node pool with basic configuration - Rails convenience"""
        pool_config = {
            "name": name,
            "machine_type": machine_type or self.machine_type,
            "initial_node_count": nodes,
            "autoscaling": {
                "enabled": self.auto_scaling_enabled,
                "min_node_count": self.min_node_count,
                "max_node_count": self.max_node_count
            }
        }
        return self.add_node_pool(pool_config)
        
    # Utility methods for better UX
    def show_machine_types(self):
        """Display available machine types"""
        machine_types = self._get_common_machine_types()
        print("📋 Common GKE Machine Types:")
        for machine_type in machine_types:
            description = self._get_machine_type_description(machine_type)
            print(f"   • {machine_type}: {description}")
        return self
        
    def estimate_cost(self):
        """Display estimated monthly cost"""
        cost = self._estimate_gke_cost()
        print(f"💰 Estimated Monthly Cost: ${cost:.2f}")
        return self

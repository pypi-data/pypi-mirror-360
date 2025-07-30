"""
GCP GKE Complete Implementation (Modular Architecture)

Combines all GKE functionality through multiple inheritance:
- GKECore: Core attributes and authentication
- GKEConfigurationMixin: Chainable configuration methods  
- GKELifecycleMixin: Lifecycle operations (create/destroy/preview/scale/upgrade)
"""

from typing import Dict, Any, List, Optional
from .gke_core import GKECore
from .gke_configuration import GKEConfigurationMixin
from .gke_lifecycle import GKELifecycleMixin


class GKE(GKELifecycleMixin, GKEConfigurationMixin, GKECore):
    """
    Complete GCP GKE implementation for Kubernetes cluster management.
    
    This class combines:
    - Cluster configuration methods (nodes, networking, security)
    - Kubernetes lifecycle management (create, destroy, preview, scale, upgrade)
    - Advanced auto-scaling and node pool management
    - Security and compliance features
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize GKE instance for Kubernetes cluster management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$75.00/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._cluster_type = None
        self._auto_scaling_enabled = True
        self._high_availability_enabled = False
    
    def validate_configuration(self):
        """Validate the current GKE configuration"""
        errors = []
        warnings = []
        
        # Validate cluster name
        if not self.cluster_name:
            errors.append("Cluster name is required")
        
        # Validate location
        if not self.location:
            errors.append("Location is required")
        elif not self._is_valid_location(self.location):
            errors.append(f"Invalid location: {self.location}")
        
        # Validate machine type
        if not self._is_valid_machine_type(self.machine_type):
            errors.append(f"Invalid machine type: {self.machine_type}")
        
        # Validate node configuration
        if not (0 <= self.initial_node_count <= 1000):
            errors.append(f"Invalid initial node count: {self.initial_node_count}")
        
        if self.auto_scaling_enabled:
            if self.min_node_count > self.max_node_count:
                errors.append(f"Min nodes ({self.min_node_count}) cannot exceed max nodes ({self.max_node_count})")
        
        # Validate disk configuration
        if not (10 <= self.disk_size_gb <= 65536):
            errors.append(f"Invalid disk size: {self.disk_size_gb}GB")
        
        # Validate network configuration
        if self.enable_private_nodes and not self.master_ipv4_cidr_block:
            warnings.append("Private nodes enabled but no master CIDR specified")
        
        # Performance warnings
        if self.initial_node_count > 50:
            warnings.append(f"High initial node count ({self.initial_node_count}) will increase costs significantly")
        
        if self.machine_type.startswith("n2-") and self.disk_type == "pd-standard":
            warnings.append("N2 machine types perform better with SSD disks")
        
        # Security warnings
        if not self.enable_shielded_nodes:
            warnings.append("Shielded nodes disabled - consider enabling for enhanced security")
        
        if not self.enable_workload_identity:
            warnings.append("Workload Identity disabled - consider enabling for secure pod-to-GCP access")
        
        if not self.enable_network_policy:
            warnings.append("Network policy disabled - consider enabling for pod-to-pod security")
        
        # Node pool validation
        for pool in self.node_pools:
            if not self._validate_node_pool_config(pool):
                errors.append(f"Invalid node pool configuration: {pool.get('name', 'unknown')}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_cluster_info(self):
        """Get complete information about the GKE cluster"""
        return {
            'cluster_name': self.cluster_name,
            'description': self.cluster_description,
            'location': self.location,
            'location_type': self.location_type,
            'kubernetes_version': self.kubernetes_version,
            'release_channel': self.release_channel,
            'machine_type': self.machine_type,
            'initial_node_count': self.initial_node_count,
            'disk_size_gb': self.disk_size_gb,
            'disk_type': self.disk_type,
            'image_type': self.image_type,
            'auto_scaling_enabled': self.auto_scaling_enabled,
            'min_node_count': self.min_node_count,
            'max_node_count': self.max_node_count,
            'preemptible_nodes': self.preemptible_nodes,
            'spot_instances': self.spot_instances,
            'network': self.network,
            'subnetwork': self.subnetwork,
            'enable_ip_alias': self.enable_ip_alias,
            'enable_private_nodes': self.enable_private_nodes,
            'enable_private_endpoint': self.enable_private_endpoint,
            'enable_shielded_nodes': self.enable_shielded_nodes,
            'enable_workload_identity': self.enable_workload_identity,
            'enable_network_policy': self.enable_network_policy,
            'enable_cloud_monitoring': self.enable_cloud_monitoring,
            'enable_cloud_logging': self.enable_cloud_logging,
            'cluster_labels_count': len(self.cluster_labels),
            'cluster_labels': self.cluster_labels,
            'node_labels_count': len(self.node_labels),
            'node_pools_count': len(self.node_pools),
            'cluster_exists': self.cluster_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'cluster_type': self._cluster_type
        }
    
    def clone(self, new_name: str):
        """Create a copy of this GKE configuration with a new name"""
        cloned_cluster = GKE(new_name)
        cloned_cluster.cluster_name = new_name
        cloned_cluster.cluster_description = self.cluster_description
        cloned_cluster.location = self.location
        cloned_cluster.location_type = self.location_type
        cloned_cluster.kubernetes_version = self.kubernetes_version
        cloned_cluster.release_channel = self.release_channel
        cloned_cluster.machine_type = self.machine_type
        cloned_cluster.initial_node_count = self.initial_node_count
        cloned_cluster.disk_size_gb = self.disk_size_gb
        cloned_cluster.disk_type = self.disk_type
        cloned_cluster.image_type = self.image_type
        cloned_cluster.auto_scaling_enabled = self.auto_scaling_enabled
        cloned_cluster.min_node_count = self.min_node_count
        cloned_cluster.max_node_count = self.max_node_count
        cloned_cluster.preemptible_nodes = self.preemptible_nodes
        cloned_cluster.spot_instances = self.spot_instances
        cloned_cluster.network = self.network
        cloned_cluster.subnetwork = self.subnetwork
        cloned_cluster.enable_ip_alias = self.enable_ip_alias
        cloned_cluster.enable_private_nodes = self.enable_private_nodes
        cloned_cluster.enable_private_endpoint = self.enable_private_endpoint
        cloned_cluster.enable_shielded_nodes = self.enable_shielded_nodes
        cloned_cluster.enable_workload_identity = self.enable_workload_identity
        cloned_cluster.enable_network_policy = self.enable_network_policy
        cloned_cluster.enable_cloud_monitoring = self.enable_cloud_monitoring
        cloned_cluster.enable_cloud_logging = self.enable_cloud_logging
        cloned_cluster.cluster_labels = self.cluster_labels.copy()
        cloned_cluster.node_labels = self.node_labels.copy()
        cloned_cluster.node_pools = self.node_pools.copy()
        return cloned_cluster
    
    def export_configuration(self):
        """Export GKE configuration for backup or migration"""
        return {
            'metadata': {
                'cluster_name': self.cluster_name,
                'location': self.location,
                'kubernetes_version': self.kubernetes_version,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'cluster_name': self.cluster_name,
                'description': self.cluster_description,
                'location': self.location,
                'location_type': self.location_type,
                'kubernetes_version': self.kubernetes_version,
                'master_version': self.master_version,
                'node_version': self.node_version,
                'release_channel': self.release_channel,
                'machine_type': self.machine_type,
                'initial_node_count': self.initial_node_count,
                'disk_size_gb': self.disk_size_gb,
                'disk_type': self.disk_type,
                'image_type': self.image_type,
                'auto_scaling_enabled': self.auto_scaling_enabled,
                'min_node_count': self.min_node_count,
                'max_node_count': self.max_node_count,
                'auto_upgrade': self.auto_upgrade,
                'auto_repair': self.auto_repair,
                'preemptible_nodes': self.preemptible_nodes,
                'spot_instances': self.spot_instances,
                'network': self.network,
                'subnetwork': self.subnetwork,
                'enable_ip_alias': self.enable_ip_alias,
                'cluster_ipv4_cidr': self.cluster_ipv4_cidr,
                'services_ipv4_cidr': self.services_ipv4_cidr,
                'enable_private_nodes': self.enable_private_nodes,
                'enable_private_endpoint': self.enable_private_endpoint,
                'master_ipv4_cidr_block': self.master_ipv4_cidr_block,
                'enable_shielded_nodes': self.enable_shielded_nodes,
                'enable_workload_identity': self.enable_workload_identity,
                'workload_pool': self.workload_pool,
                'enable_network_policy': self.enable_network_policy,
                'enable_pod_security_policy': self.enable_pod_security_policy,
                'enable_cloud_monitoring': self.enable_cloud_monitoring,
                'enable_cloud_logging': self.enable_cloud_logging,
                'logging_service': self.logging_service,
                'monitoring_service': self.monitoring_service,
                'master_auth_networks': self.master_auth_networks,
                'service_account': self.service_account,
                'oauth_scopes': self.oauth_scopes,
                'cluster_labels': self.cluster_labels,
                'node_labels': self.node_labels,
                'node_tags': self.node_tags,
                'node_taints': self.node_taints,
                'maintenance_window': self.maintenance_window,
                'maintenance_exclusions': self.maintenance_exclusions,
                'node_pools': self.node_pools,
                'http_load_balancing_disabled': self.http_load_balancing_disabled,
                'horizontal_pod_autoscaling_disabled': self.horizontal_pod_autoscaling_disabled,
                'kubernetes_dashboard_disabled': self.kubernetes_dashboard_disabled,
                'network_policy_config_disabled': self.network_policy_config_disabled,
                'dns_cache_config_enabled': self.dns_cache_config_enabled,
                'config_connector_config_enabled': self.config_connector_config_enabled,
                'optimization_priority': self._optimization_priority,
                'cluster_type': self._cluster_type,
                'auto_scaling_enabled': self._auto_scaling_enabled,
                'high_availability_enabled': self._high_availability_enabled
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import GKE configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.cluster_name = config.get('cluster_name', self.cluster_name)
            self.cluster_description = config.get('description', f"GKE cluster for {self.cluster_name}")
            self.location = config.get('location', 'us-central1-a')
            self.location_type = config.get('location_type', 'zonal')
            self.kubernetes_version = config.get('kubernetes_version')
            self.master_version = config.get('master_version')
            self.node_version = config.get('node_version')
            self.release_channel = config.get('release_channel', 'REGULAR')
            self.machine_type = config.get('machine_type', 'e2-medium')
            self.initial_node_count = config.get('initial_node_count', 3)
            self.disk_size_gb = config.get('disk_size_gb', 100)
            self.disk_type = config.get('disk_type', 'pd-standard')
            self.image_type = config.get('image_type', 'COS_CONTAINERD')
            self.auto_scaling_enabled = config.get('auto_scaling_enabled', False)
            self.min_node_count = config.get('min_node_count', 1)
            self.max_node_count = config.get('max_node_count', 10)
            self.auto_upgrade = config.get('auto_upgrade', True)
            self.auto_repair = config.get('auto_repair', True)
            self.preemptible_nodes = config.get('preemptible_nodes', False)
            self.spot_instances = config.get('spot_instances', False)
            self.network = config.get('network', 'default')
            self.subnetwork = config.get('subnetwork', 'default')
            self.enable_ip_alias = config.get('enable_ip_alias', True)
            self.cluster_ipv4_cidr = config.get('cluster_ipv4_cidr')
            self.services_ipv4_cidr = config.get('services_ipv4_cidr')
            self.enable_private_nodes = config.get('enable_private_nodes', False)
            self.enable_private_endpoint = config.get('enable_private_endpoint', False)
            self.master_ipv4_cidr_block = config.get('master_ipv4_cidr_block')
            self.enable_shielded_nodes = config.get('enable_shielded_nodes', True)
            self.enable_workload_identity = config.get('enable_workload_identity', False)
            self.workload_pool = config.get('workload_pool')
            self.enable_network_policy = config.get('enable_network_policy', False)
            self.enable_pod_security_policy = config.get('enable_pod_security_policy', False)
            self.enable_cloud_monitoring = config.get('enable_cloud_monitoring', True)
            self.enable_cloud_logging = config.get('enable_cloud_logging', True)
            self.logging_service = config.get('logging_service', 'logging.googleapis.com/kubernetes')
            self.monitoring_service = config.get('monitoring_service', 'monitoring.googleapis.com/kubernetes')
            self.master_auth_networks = config.get('master_auth_networks', [])
            self.service_account = config.get('service_account')
            self.oauth_scopes = config.get('oauth_scopes', [])
            self.cluster_labels = config.get('cluster_labels', {})
            self.node_labels = config.get('node_labels', {})
            self.node_tags = config.get('node_tags', [])
            self.node_taints = config.get('node_taints', [])
            self.maintenance_window = config.get('maintenance_window')
            self.maintenance_exclusions = config.get('maintenance_exclusions', [])
            self.node_pools = config.get('node_pools', [])
            self._optimization_priority = config.get('optimization_priority')
            self._cluster_type = config.get('cluster_type')
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', True)
            self._high_availability_enabled = config.get('high_availability_enabled', False)
        
        return self
    
    def enable_auto_scaling(self, enabled: bool = True):
        """Enable automatic scaling optimizations"""
        self._auto_scaling_enabled = enabled
        if enabled:
            self.auto_scaling_enabled = True
            print("📈 Auto-scaling optimizations enabled")
            print("   💡 Dynamic node adjustment configured")
            print("   💡 Intelligent scaling policies applied")
        return self
    
    def enable_high_availability(self, enabled: bool = True):
        """Enable high availability for the cluster"""
        self._high_availability_enabled = enabled
        if enabled:
            self.location_type = "regional"  # Force regional for HA
            self.initial_node_count = max(self.initial_node_count, 3)  # Ensure multiple nodes
            self.min_node_count = max(self.min_node_count, 3)
            self.auto_repair = True
            self.auto_upgrade = True
            print("🛡️ High availability enabled")
            print("   💡 Regional deployment configured")
            print("   💡 Minimum 3 nodes across zones")
            print("   💡 Auto-repair and auto-upgrade enabled")
        return self
    
    def get_cluster_status(self):
        """Get current status of the GKE cluster"""
        status = {
            "overall_status": "healthy",
            "issues": [],
            "recommendations": []
        }
        
        # Check configuration issues
        if not self.cluster_name:
            status["issues"].append("No cluster name configured")
            status["overall_status"] = "error"
        
        if not self.location:
            status["issues"].append("No location configured")
            status["overall_status"] = "error"
        
        if self.initial_node_count == 0 and not self.auto_scaling_enabled:
            status["recommendations"].append("Consider enabling auto-scaling for zero-node clusters")
        
        if not self.enable_cloud_monitoring:
            status["recommendations"].append("Enable monitoring for better cluster observability")
        
        if not self.enable_cloud_logging:
            status["recommendations"].append("Enable logging for better debugging capabilities")
        
        if not self.enable_shielded_nodes:
            status["recommendations"].append("Enable shielded nodes for enhanced security")
        
        if not self.enable_workload_identity:
            status["recommendations"].append("Enable Workload Identity for secure pod-to-GCP access")
        
        if not self.enable_network_policy:
            status["recommendations"].append("Enable network policy for pod-to-pod security")
        
        # Check resource allocation
        if self.machine_type == "e2-micro" and self.initial_node_count > 5:
            status["recommendations"].append("Micro instances with many nodes may limit performance")
        
        # Check scaling configuration
        if self.auto_scaling_enabled and self.max_node_count == 1:
            status["recommendations"].append("Max nodes set to 1 - may limit scalability")
        
        return status
    
    def apply_best_practices(self):
        """Apply GKE best practices to the configuration"""
        print("🚀 Applying GKE best practices")
        
        # Ensure reasonable machine type
        if self.machine_type == "e2-micro":
            print("   💡 Upgrading from micro instance for better performance")
            self.machine_type = "e2-medium"
        
        # Enable essential security features
        if not self.enable_shielded_nodes:
            print("   💡 Enabling shielded nodes for security")
            self.enable_shielded_nodes = True
        
        # Enable monitoring and logging
        if not self.enable_cloud_monitoring:
            print("   💡 Enabling Cloud Monitoring")
            self.enable_cloud_monitoring = True
        
        if not self.enable_cloud_logging:
            print("   💡 Enabling Cloud Logging")
            self.enable_cloud_logging = True
        
        # Configure auto-scaling if not enabled
        if not self.auto_scaling_enabled and self.initial_node_count > 0:
            print("   💡 Enabling auto-scaling for better resource utilization")
            self.auto_scaling_enabled = True
            self.min_node_count = max(1, self.initial_node_count - 2)
            self.max_node_count = self.initial_node_count + 5
        
        # Add best practice labels
        self.cluster_labels.update({
            "managed-by": "infradsl",
            "best-practices": "applied",
            "container-platform": "gke"
        })
        print("   💡 Added best practice labels")
        
        # Enable auto-repair and auto-upgrade
        if not self.auto_repair:
            print("   💡 Enabling auto-repair for node reliability")
            self.auto_repair = True
        
        if not self.auto_upgrade:
            print("   💡 Enabling auto-upgrade for security patches")
            self.auto_upgrade = True
        
        return self
    
    def get_cost_breakdown(self):
        """Get detailed cost breakdown for GKE cluster"""
        # Estimate usage patterns
        cluster_management_fee = 0.10 * 24 * 30  # $0.10 per hour
        
        # Parse machine type for cost calculation
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
            'c2-standard-4': 0.225,
            'c2-standard-8': 0.450
        }
        
        base_node_cost = node_cost_map.get(self.machine_type, 0.100)
        
        # Calculate node costs
        if self.auto_scaling_enabled:
            avg_nodes = (self.min_node_count + self.max_node_count) / 2
        else:
            avg_nodes = self.initial_node_count
            
        node_cost = base_node_cost * 24 * 30 * avg_nodes
        
        # Apply preemptible/spot discount
        if self.preemptible_nodes or self.spot_instances:
            node_cost *= 0.2  # 80% discount
            
        # Disk costs
        disk_cost_per_gb = 0.04 if self.disk_type == "pd-standard" else 0.17  # pd-ssd
        disk_cost = disk_cost_per_gb * self.disk_size_gb * avg_nodes
        
        breakdown = {
            "cluster_management_fee": cluster_management_fee,
            "node_cost": node_cost,
            "disk_cost": disk_cost,
            "load_balancer_cost": 18.25,  # If load balancers are used
            "total_nodes": avg_nodes,
            "machine_type": self.machine_type,
            "disk_size_gb": self.disk_size_gb,
            "preemptible_discount": self.preemptible_nodes or self.spot_instances
        }
        
        breakdown["total_cost"] = (
            breakdown["cluster_management_fee"] + 
            breakdown["node_cost"] + 
            breakdown["disk_cost"]
        )
        
        return breakdown
    
    def get_security_analysis(self):
        """Analyze GKE security configuration"""
        analysis = {
            "security_score": 100,
            "issues": [],
            "recommendations": []
        }
        
        # Check shielded nodes
        if not self.enable_shielded_nodes:
            analysis["issues"].append("Shielded nodes disabled")
            analysis["security_score"] -= 20
        
        # Check workload identity
        if not self.enable_workload_identity:
            analysis["recommendations"].append("Enable Workload Identity for secure pod-to-GCP access")
            analysis["security_score"] -= 10
        
        # Check network policy
        if not self.enable_network_policy:
            analysis["recommendations"].append("Enable network policy for pod-to-pod security")
            analysis["security_score"] -= 10
        
        # Check private nodes
        if not self.enable_private_nodes:
            analysis["recommendations"].append("Use private nodes to isolate from public internet")
            analysis["security_score"] -= 15
        
        # Check pod security policy
        if not self.enable_pod_security_policy:
            analysis["recommendations"].append("Enable Pod Security Policy for pod security controls")
            analysis["security_score"] -= 5
        
        # Check authorized networks
        if not self.master_auth_networks:
            analysis["recommendations"].append("Configure master authorized networks to restrict API access")
            analysis["security_score"] -= 10
        
        # Check service account
        if not self.service_account:
            analysis["recommendations"].append("Use custom service account instead of default")
            analysis["security_score"] -= 5
        
        return analysis
    
    def get_performance_analysis(self):
        """Analyze GKE performance configuration"""
        analysis = {
            "performance_score": 100,
            "issues": [],
            "recommendations": []
        }
        
        # Check machine type
        if self.machine_type in ["e2-micro", "e2-small"]:
            analysis["issues"].append("Small machine types may limit performance")
            analysis["performance_score"] -= 20
        
        # Check disk type
        if self.disk_type == "pd-standard" and self.machine_type.startswith("n2-"):
            analysis["recommendations"].append("Use SSD disks with N2 machine types for better performance")
            analysis["performance_score"] -= 10
        
        # Check auto-scaling
        if not self.auto_scaling_enabled:
            analysis["recommendations"].append("Enable auto-scaling for dynamic resource allocation")
            analysis["performance_score"] -= 10
        
        # Check node count
        if self.initial_node_count == 1 and not self.auto_scaling_enabled:
            analysis["issues"].append("Single node without auto-scaling may cause availability issues")
            analysis["performance_score"] -= 15
        
        # Check regional vs zonal
        if self.location_type == "zonal":
            analysis["recommendations"].append("Consider regional clusters for better availability")
            analysis["performance_score"] -= 5
        
        # Check DNS cache
        if not self.dns_cache_config_enabled:
            analysis["recommendations"].append("Enable DNS cache for better DNS performance")
            analysis["performance_score"] -= 5
        
        return analysis


# Convenience functions for creating GKE instances
def create_development_cluster(project_id: str, cluster_name: str, location: str = "us-central1-a") -> GKE:
    """Create GKE cluster for development environment"""
    cluster = GKE(cluster_name)
    cluster.project(project_id).location(location).development()
    return cluster

def create_staging_cluster(project_id: str, cluster_name: str, location: str = "us-central1") -> GKE:
    """Create GKE cluster for staging environment"""
    cluster = GKE(cluster_name)
    cluster.project(project_id).location(location).staging()
    return cluster

def create_production_cluster(project_id: str, cluster_name: str, location: str = "us-central1") -> GKE:
    """Create GKE cluster for production environment"""
    cluster = GKE(cluster_name)
    cluster.project(project_id).location(location).production()
    return cluster

def create_cost_optimized_cluster(project_id: str, cluster_name: str, location: str = "us-central1-a") -> GKE:
    """Create cost-optimized GKE cluster"""
    cluster = GKE(cluster_name)
    cluster.project(project_id).location(location).cost_optimized()
    return cluster

def create_performance_cluster(project_id: str, cluster_name: str, location: str = "us-central1") -> GKE:
    """Create performance-optimized GKE cluster"""
    cluster = GKE(cluster_name)
    cluster.project(project_id).location(location).performance_optimized()
    return cluster

def create_secure_cluster(project_id: str, cluster_name: str, location: str = "us-central1") -> GKE:
    """Create security-optimized GKE cluster"""
    cluster = GKE(cluster_name)
    cluster.project(project_id).location(location).security_optimized()
    return cluster

# Aliases for backward compatibility
GCPKubernetesEngine = GKE
GCPGKE = GKE
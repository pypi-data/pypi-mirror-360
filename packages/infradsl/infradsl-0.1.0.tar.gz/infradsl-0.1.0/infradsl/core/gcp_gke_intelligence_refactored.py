"""
GCP GKE Intelligence - Refactored Modular Version

Enterprise GKE Intelligence Engine with modular architecture.

The world's first intelligent Kubernetes management system that provides:
- Smart cluster sizing and node pool optimization
- Predictive auto-scaling based on workload patterns
- Cost optimization for preemptible vs standard nodes
- Security and compliance recommendations
- Multi-zone cluster management
- Container resource optimization

This extends the Nexus Engine with enterprise-grade Kubernetes intelligence.
"""

# Import all GKE intelligence components
from .gke_types import (
    NodePoolType, ClusterType, SecurityLevel, NodeConfig, AutoscalingConfig,
    NodePoolRecommendation, GKESecurityFinding, GKECostAnalysis,
    GKEScalingPrediction, GKESecurityAssessment, GKEOptimizationAnalysis
)

from .gke_cost_analyzer import GKECostAnalyzer
from .gke_security_auditor import GKESecurityAuditor
from .gke_scaling_predictor import GKEScalingPredictor

# Import base classes
from .gcp_intelligence_base import GCPIntelligenceBase
from .stateless_intelligence import (
    ResourceType, ResourceFingerprint, ChangeImpactAnalysis, 
    ResourceHealth, HealthStatus
)

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json


class GCPGKEIntelligence(GCPIntelligenceBase):
    """
    GCP GKE Intelligence Engine - Refactored Modular Version
    
    Provides intelligent Kubernetes orchestration including:
    - Smart cluster sizing and node pool optimization
    - Predictive auto-scaling based on workload patterns
    - Cost optimization for preemptible vs standard nodes
    - Security and compliance recommendations
    - Multi-zone cluster management
    - Container resource optimization
    """
    
    def __init__(self):
        super().__init__(ResourceType.CONTAINER)
        self.optimization_rules = {
            "node_utilization_thresholds": {
                "scale_up": 0.75,      # Scale up at 75% utilization
                "scale_down": 0.30,    # Scale down at 30% utilization
                "optimal_range": (0.50, 0.70)
            },
            "cost_optimization": {
                "preemptible_savings": 0.80,     # 80% cost savings
                "preemptible_max_percentage": 0.70,  # Max 70% preemptible nodes
                "spot_instance_recommendation": True,
                "committed_use_threshold": 0.75   # 75% steady usage for CUD
            },
            "cluster_sizing": {
                "min_nodes_per_zone": 1,
                "max_nodes_per_zone": 10,
                "node_pool_max_size": 100,
                "recommended_zones": 3
            },
            "security_thresholds": {
                "workload_identity_required": True,
                "private_cluster_recommended": True,
                "binary_authorization_recommended": True,
                "pod_security_policy_required": True
            }
        }
        
        # Initialize specialized analyzers
        self.cost_analyzer = GKECostAnalyzer(self.optimization_rules)
        self.security_auditor = GKESecurityAuditor(self.optimization_rules["security_thresholds"])
        self.scaling_predictor = GKEScalingPredictor(self.optimization_rules["node_utilization_thresholds"])
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing GKE clusters and node pools"""
        
        # Mock implementation - in production would use Google Cloud Client Library
        return {
            "production-cluster": {
                "cluster_name": "production-cluster",
                "location": "us-central1",
                "location_type": "regional",
                "status": "RUNNING",
                "current_node_count": 12,
                "current_master_version": "1.27.3-gke.100",
                "node_version": "1.27.3-gke.100",
                "network": "default",
                "subnetwork": "default",
                "private_cluster_config": {
                    "enable_private_nodes": True,
                    "enable_private_endpoint": False,
                    "master_ipv4_cidr_block": "172.16.0.0/28"
                },
                "workload_identity_config": {
                    "workload_pool": "my-project.svc.id.goog"
                },
                "node_pools": [
                    {
                        "name": "default-pool",
                        "status": "RUNNING",
                        "initial_node_count": 3,
                        "current_node_count": 6,
                        "node_config": {
                            "machine_type": "e2-standard-4",
                            "disk_size_gb": 100,
                            "disk_type": "pd-standard",
                            "image_type": "COS_CONTAINERD",
                            "preemptible": False,
                            "spot": False
                        },
                        "autoscaling": {
                            "enabled": True,
                            "min_node_count": 2,
                            "max_node_count": 10
                        },
                        "management": {
                            "auto_upgrade": True,
                            "auto_repair": True
                        },
                        "locations": ["us-central1-a", "us-central1-b", "us-central1-c"]
                    },
                    {
                        "name": "spot-pool",
                        "status": "RUNNING",
                        "initial_node_count": 2,
                        "current_node_count": 4,
                        "node_config": {
                            "machine_type": "e2-standard-2",
                            "disk_size_gb": 50,
                            "disk_type": "pd-ssd",
                            "image_type": "COS_CONTAINERD",
                            "preemptible": False,
                            "spot": True
                        },
                        "autoscaling": {
                            "enabled": True,
                            "min_node_count": 0,
                            "max_node_count": 8
                        },
                        "management": {
                            "auto_upgrade": True,
                            "auto_repair": True
                        },
                        "locations": ["us-central1-a", "us-central1-b"]
                    }
                ],
                "addons_config": {
                    "network_policy_config": {"disabled": False},
                    "horizontal_pod_autoscaling": {"disabled": False},
                    "http_load_balancing": {"disabled": False},
                    "kubernetes_dashboard": {"disabled": True},
                    "istio_config": {"disabled": True}
                },
                "logging_service": "logging.googleapis.com/kubernetes",
                "monitoring_service": "monitoring.googleapis.com/kubernetes",
                "metrics": {
                    "cpu_utilization": 0.65,
                    "memory_utilization": 0.70,
                    "pod_count": 45,
                    "node_count": 10,
                    "running_pods": 42,
                    "pending_pods": 3,
                    "monthly_cost_estimate": 720.00
                },
                "security_config": {
                    "workload_identity_enabled": True,
                    "binary_authorization_enabled": False,
                    "pod_security_policy_enabled": False,
                    "network_policy_enabled": True
                }
            }
        }
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract GKE configuration from cloud state"""
        
        return {
            "cluster_name": cloud_state.get("cluster_name"),
            "location": cloud_state.get("location"),
            "location_type": cloud_state.get("location_type"),
            "current_master_version": cloud_state.get("current_master_version"),
            "node_pools": cloud_state.get("node_pools", []),
            "private_cluster_config": cloud_state.get("private_cluster_config", {}),
            "addons_config": cloud_state.get("addons_config", {}),
            "security_config": cloud_state.get("security_config", {}),
            "metrics": cloud_state.get("metrics", {})
        }
    
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """Generate hash for GKE configuration"""
        
        # Focus on key configuration elements
        key_config = {
            "cluster_name": config.get("cluster_name"),
            "location": config.get("location"),
            "location_type": config.get("location_type"),
            "master_version": config.get("current_master_version"),
            "node_pools": [
                {
                    "name": np.get("name"),
                    "machine_type": np.get("node_config", {}).get("machine_type"),
                    "node_count": np.get("current_node_count"),
                    "preemptible": np.get("node_config", {}).get("preemptible"),
                    "spot": np.get("node_config", {}).get("spot")
                }
                for np in config.get("node_pools", [])
            ],
            "private_cluster": config.get("private_cluster_config", {}).get("enable_private_nodes", False)
        }
        
        return str(hash(json.dumps(key_config, sort_keys=True)))
    
    # ==========================================
    # MAIN INTELLIGENCE METHODS
    # ==========================================
    
    def analyze_gke_optimization(self, cluster_data: Dict[str, Any]) -> GKEOptimizationAnalysis:
        """
        Analyze GKE cluster for optimization opportunities
        """
        
        # Cost analysis using specialized analyzer
        cost_analysis = self.cost_analyzer.analyze_cluster_costs(cluster_data)
        
        # Node pool analysis
        node_pool_recommendations = self._analyze_node_pools(cluster_data)
        
        # Security analysis using specialized auditor
        security_recommendations = self._analyze_gke_security(cluster_data)
        
        # Scaling analysis using specialized predictor
        scaling_recommendations = self.scaling_predictor.analyze_node_pool_scaling(cluster_data)
        
        # General cluster recommendations
        general_recommendations = self._generate_cluster_recommendations(cluster_data)
        
        return GKEOptimizationAnalysis(
            cluster_name=cluster_data.get("cluster_name"),
            current_cost_estimate=cost_analysis.current_monthly_cost,
            optimized_cost_estimate=cost_analysis.optimized_monthly_cost,
            potential_savings=cost_analysis.potential_savings,
            recommendations=general_recommendations,
            node_pool_recommendations=node_pool_recommendations,
            security_recommendations=security_recommendations,
            scaling_recommendations=scaling_recommendations,
            cost_breakdown=cost_analysis.cost_breakdown
        )
    
    def generate_gke_security_assessment(self, cluster_data: Dict[str, Any]) -> GKESecurityAssessment:
        """
        Generate comprehensive GKE security assessment
        """
        return self.security_auditor.generate_security_assessment(cluster_data)
    
    def predict_gke_scaling_needs(self, cluster_name: str, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict GKE scaling needs based on historical metrics
        """
        return self.scaling_predictor.predict_scaling_needs(cluster_name, metrics_history)
    
    # ==========================================
    # SPECIALIZED ANALYSIS METHODS
    # ==========================================
    
    def calculate_spot_savings_potential(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate potential savings from increased spot instance usage"""
        return self.cost_analyzer.calculate_spot_savings_potential(cluster_data)
    
    def generate_rightsizing_recommendations(self, cluster_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate machine type rightsizing recommendations"""
        return self.cost_analyzer.generate_rightsizing_recommendations(cluster_data)
    
    def check_compliance_frameworks(self, cluster_data: Dict[str, Any], 
                                  frameworks: List[str]) -> Dict[str, Any]:
        """Check compliance against security frameworks"""
        return self.security_auditor.check_compliance_frameworks(cluster_data, frameworks)
    
    def predict_peak_times(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict when peak usage typically occurs"""
        return self.scaling_predictor.predict_peak_times(metrics_history)
    
    def calculate_scaling_efficiency(self, cluster_data: Dict[str, Any], 
                                   metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate how efficiently the cluster is scaling"""
        return self.scaling_predictor.calculate_scaling_efficiency(cluster_data, metrics_history)
    
    # ==========================================
    # INTERNAL HELPER METHODS
    # ==========================================
    
    def _analyze_node_pools(self, cluster_data: Dict[str, Any]) -> List[NodePoolRecommendation]:
        """Analyze node pool configurations"""
        
        node_pools = cluster_data.get("node_pools", [])
        recommendations = []
        
        for pool in node_pools:
            pool_name = pool.get("name")
            node_config = pool.get("node_config", {})
            autoscaling = pool.get("autoscaling", {})
            management = pool.get("management", {})
            locations = pool.get("locations", [])
            
            pool_recommendations = []
            
            # Machine type recommendations
            machine_type = node_config.get("machine_type", "")
            if "micro" in machine_type or "small" in machine_type:
                pool_recommendations.append("Consider larger machine types for better resource efficiency")
            
            # Disk optimization
            disk_size = node_config.get("disk_size_gb", 100)
            disk_type = node_config.get("disk_type", "pd-standard")
            
            if disk_size > 100 and disk_type == "pd-standard":
                pool_recommendations.append("Consider pd-ssd for better performance with large disk sizes")
            
            # Autoscaling recommendations
            if not autoscaling.get("enabled", False):
                pool_recommendations.append("Enable autoscaling for better resource optimization")
            else:
                min_nodes = autoscaling.get("min_node_count", 0)
                max_nodes = autoscaling.get("max_node_count", 0)
                
                if min_nodes == max_nodes:
                    pool_recommendations.append("Configure proper min/max autoscaling range")
                
                if max_nodes > 20:
                    pool_recommendations.append("Consider splitting large node pools for better management")
            
            # Management recommendations
            if not management.get("auto_upgrade", False):
                pool_recommendations.append("Enable auto-upgrade for security and feature updates")
            
            if not management.get("auto_repair", False):
                pool_recommendations.append("Enable auto-repair for better reliability")
            
            # Zone distribution
            if len(locations) < 2:
                pool_recommendations.append("Deploy across multiple zones for high availability")
            
            if pool_recommendations:
                recommendations.append(NodePoolRecommendation(
                    pool_name=pool_name,
                    recommendations=pool_recommendations
                ))
        
        return recommendations
    
    def _analyze_gke_security(self, cluster_data: Dict[str, Any]) -> List[str]:
        """Analyze GKE security configuration"""
        
        recommendations = []
        security_config = cluster_data.get("security_config", {})
        private_cluster = cluster_data.get("private_cluster_config", {})
        addons = cluster_data.get("addons_config", {})
        
        # Private cluster recommendations
        if not private_cluster.get("enable_private_nodes", False):
            recommendations.append("Enable private nodes for better security isolation")
        
        # Workload Identity
        if not security_config.get("workload_identity_enabled", False):
            recommendations.append("Enable Workload Identity for secure pod authentication")
        
        # Binary Authorization
        if not security_config.get("binary_authorization_enabled", False):
            recommendations.append("Enable Binary Authorization for container image security")
        
        # Pod Security Policy/Pod Security Standards
        if not security_config.get("pod_security_policy_enabled", False):
            recommendations.append("Implement Pod Security Standards for runtime security")
        
        # Network Policy
        if not security_config.get("network_policy_enabled", False):
            recommendations.append("Enable Network Policy for micro-segmentation")
        
        # Kubernetes Dashboard (should be disabled)
        if not addons.get("kubernetes_dashboard", {}).get("disabled", True):
            recommendations.append("Disable Kubernetes Dashboard for security (use Cloud Console instead)")
        
        # General security recommendations
        recommendations.extend([
            "Implement least privilege RBAC policies",
            "Regular security scanning of container images",
            "Enable audit logging for compliance"
        ])
        
        return recommendations
    
    def _generate_cluster_recommendations(self, cluster_data: Dict[str, Any]) -> List[str]:
        """Generate general cluster recommendations"""
        
        recommendations = []
        location_type = cluster_data.get("location_type")
        addons = cluster_data.get("addons_config", {})
        
        # Regional vs Zonal
        if location_type == "zonal":
            recommendations.append("Consider regional cluster for high availability")
        
        # Monitoring and logging
        if not cluster_data.get("monitoring_service"):
            recommendations.append("Enable Google Cloud Monitoring for cluster observability")
        
        if not cluster_data.get("logging_service"):
            recommendations.append("Enable Google Cloud Logging for centralized log management")
        
        # Version management
        master_version = cluster_data.get("current_master_version", "")
        node_version = cluster_data.get("node_version", "")
        
        if master_version != node_version:
            recommendations.append("Sync master and node versions for compatibility")
        
        # Add-ons recommendations
        if addons.get("network_policy_config", {}).get("disabled", True):
            recommendations.append("Enable Network Policy for enhanced security")
        
        # Backup and GitOps recommendations
        recommendations.extend([
            "Implement regular backup strategy for cluster configuration",
            "Use GitOps for declarative cluster management"
        ])
        
        return recommendations


# Global GKE Intelligence instance for backward compatibility
gke_intelligence = GCPGKEIntelligence()

# Export all components for easy importing
__all__ = [
    # Types and Enums
    'NodePoolType',
    'ClusterType',
    'SecurityLevel',
    'NodeConfig',
    'AutoscalingConfig',
    'NodePoolRecommendation',
    'GKESecurityFinding',
    'GKECostAnalysis',
    'GKEScalingPrediction',
    'GKESecurityAssessment',
    'GKEOptimizationAnalysis',
    
    # Specialized Analyzers
    'GKECostAnalyzer',
    'GKESecurityAuditor',
    'GKEScalingPredictor',
    
    # Main Intelligence Class
    'GCPGKEIntelligence',
    
    # Global instance
    'gke_intelligence'
]
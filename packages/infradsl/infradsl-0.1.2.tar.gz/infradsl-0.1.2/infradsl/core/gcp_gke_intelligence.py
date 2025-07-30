"""
GCP GKE Intelligence

Advanced intelligence for Google Kubernetes Engine (GKE)
providing intelligent cluster management, auto-scaling, and cost optimization.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from .gcp_intelligence_base import GCPIntelligenceBase
from .stateless_intelligence import (
    ResourceType, ResourceFingerprint, ChangeImpactAnalysis, 
    ResourceHealth, HealthStatus
)


class GCPGKEIntelligence(GCPIntelligenceBase):
    """
    GCP GKE Intelligence Engine
    
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
            },
            "development-cluster": {
                "cluster_name": "development-cluster",
                "location": "us-west1-a",
                "location_type": "zonal",
                "status": "RUNNING",
                "current_node_count": 3,
                "current_master_version": "1.27.3-gke.100",
                "node_version": "1.27.3-gke.100",
                "network": "default",
                "subnetwork": "default",
                "private_cluster_config": {
                    "enable_private_nodes": False,
                    "enable_private_endpoint": False
                },
                "workload_identity_config": None,
                "node_pools": [
                    {
                        "name": "default-pool",
                        "status": "RUNNING",
                        "initial_node_count": 3,
                        "current_node_count": 3,
                        "node_config": {
                            "machine_type": "e2-medium",
                            "disk_size_gb": 20,
                            "disk_type": "pd-standard",
                            "image_type": "COS_CONTAINERD",
                            "preemptible": True,
                            "spot": False
                        },
                        "autoscaling": {
                            "enabled": False
                        },
                        "management": {
                            "auto_upgrade": False,
                            "auto_repair": True
                        },
                        "locations": ["us-west1-a"]
                    }
                ],
                "addons_config": {
                    "network_policy_config": {"disabled": True},
                    "horizontal_pod_autoscaling": {"disabled": True},
                    "http_load_balancing": {"disabled": False}
                },
                "metrics": {
                    "cpu_utilization": 0.25,
                    "memory_utilization": 0.30,
                    "pod_count": 8,
                    "node_count": 3,
                    "running_pods": 8,
                    "pending_pods": 0,
                    "monthly_cost_estimate": 85.00
                },
                "security_config": {
                    "workload_identity_enabled": False,
                    "binary_authorization_enabled": False,
                    "pod_security_policy_enabled": False,
                    "network_policy_enabled": False
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
    
    def analyze_gke_optimization(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze GKE cluster for optimization opportunities
        """
        
        optimization_analysis = {
            "cluster_name": cluster_data.get("cluster_name"),
            "current_cost_estimate": 0.0,
            "optimized_cost_estimate": 0.0,
            "potential_savings": 0.0,
            "recommendations": [],
            "node_pool_recommendations": [],
            "security_recommendations": [],
            "scaling_recommendations": [],
            "cost_breakdown": {}
        }
        
        # Cost analysis
        cost_analysis = self._analyze_gke_costs(cluster_data)
        optimization_analysis.update(cost_analysis)
        
        # Node pool optimization
        node_pool_analysis = self._analyze_node_pools(cluster_data)
        optimization_analysis["node_pool_recommendations"] = node_pool_analysis
        
        # Security analysis
        security_analysis = self._analyze_gke_security(cluster_data)
        optimization_analysis["security_recommendations"] = security_analysis
        
        # Scaling analysis
        scaling_analysis = self._analyze_gke_scaling(cluster_data)
        optimization_analysis["scaling_recommendations"] = scaling_analysis
        
        # General cluster recommendations
        cluster_recommendations = self._generate_cluster_recommendations(cluster_data)
        optimization_analysis["recommendations"].extend(cluster_recommendations)
        
        return optimization_analysis
    
    def _analyze_gke_costs(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze GKE cost optimization opportunities"""
        
        node_pools = cluster_data.get("node_pools", [])
        metrics = cluster_data.get("metrics", {})
        current_cost = metrics.get("monthly_cost_estimate", 0.0)
        
        optimized_cost = current_cost
        recommendations = []
        cost_breakdown = {
            "compute": 0.0,
            "storage": 0.0,
            "network": 0.0
        }
        
        total_standard_nodes = 0
        total_preemptible_nodes = 0
        total_spot_nodes = 0
        
        for pool in node_pools:
            node_config = pool.get("node_config", {})
            node_count = pool.get("current_node_count", 0)
            machine_type = node_config.get("machine_type", "")
            
            if node_config.get("spot", False):
                total_spot_nodes += node_count
            elif node_config.get("preemptible", False):
                total_preemptible_nodes += node_count
            else:
                total_standard_nodes += node_count
            
            # Machine type optimization
            if "standard-" in machine_type and node_count > 0:
                cpu_util = metrics.get("cpu_utilization", 0.5)
                memory_util = metrics.get("memory_utilization", 0.5)
                
                if cpu_util < 0.30 and memory_util < 0.30:
                    recommendations.append(f"Consider downsizing machine type for {pool.get('name')} - low utilization")
                    # Estimate 30% cost savings
                    potential_savings = current_cost * 0.30 * (node_count / sum(p.get("current_node_count", 0) for p in node_pools))
                    optimized_cost -= potential_savings
        
        # Preemptible/Spot recommendations
        total_nodes = total_standard_nodes + total_preemptible_nodes + total_spot_nodes
        if total_nodes > 0:
            preemptible_ratio = (total_preemptible_nodes + total_spot_nodes) / total_nodes
            
            if preemptible_ratio < 0.30 and total_standard_nodes > 2:
                recommendations.append("Increase preemptible/spot node usage for cost savings (up to 80% reduction)")
                # Estimate savings from converting some standard nodes
                convertible_nodes = min(total_standard_nodes - 2, int(total_standard_nodes * 0.5))
                estimated_savings = current_cost * 0.80 * (convertible_nodes / total_nodes)
                optimized_cost -= estimated_savings
        
        # Committed Use Discount recommendations
        cpu_util = metrics.get("cpu_utilization", 0.5)
        if cpu_util > self.optimization_rules["cost_optimization"]["committed_use_threshold"]:
            recommendations.append("Consider Committed Use Discounts for steady workloads (up to 57% savings)")
        
        # Autoscaling recommendations
        for pool in node_pools:
            if not pool.get("autoscaling", {}).get("enabled", False):
                recommendations.append(f"Enable autoscaling for {pool.get('name')} to optimize resource usage")
        
        return {
            "current_cost_estimate": current_cost,
            "optimized_cost_estimate": optimized_cost,
            "potential_savings": current_cost - optimized_cost,
            "cost_breakdown": cost_breakdown,
            "recommendations": recommendations
        }
    
    def _analyze_node_pools(self, cluster_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze node pool configurations"""
        
        node_pools = cluster_data.get("node_pools", [])
        recommendations = []
        
        for pool in node_pools:
            pool_name = pool.get("name")
            node_config = pool.get("node_config", {})
            autoscaling = pool.get("autoscaling", {})
            management = pool.get("management", {})
            current_nodes = pool.get("current_node_count", 0)
            
            pool_recommendations = {
                "pool_name": pool_name,
                "recommendations": []
            }
            
            # Machine type recommendations
            machine_type = node_config.get("machine_type", "")
            if "micro" in machine_type or "small" in machine_type:
                pool_recommendations["recommendations"].append(
                    "Consider larger machine types for better resource efficiency"
                )
            
            # Disk optimization
            disk_size = node_config.get("disk_size_gb", 100)
            disk_type = node_config.get("disk_type", "pd-standard")
            
            if disk_size > 100 and disk_type == "pd-standard":
                pool_recommendations["recommendations"].append(
                    "Consider pd-ssd for better performance with large disk sizes"
                )
            
            # Autoscaling recommendations
            if not autoscaling.get("enabled", False):
                pool_recommendations["recommendations"].append(
                    "Enable autoscaling for better resource optimization"
                )
            else:
                min_nodes = autoscaling.get("min_node_count", 0)
                max_nodes = autoscaling.get("max_node_count", 0)
                
                if min_nodes == max_nodes:
                    pool_recommendations["recommendations"].append(
                        "Configure proper min/max autoscaling range"
                    )
                
                if max_nodes > 20:
                    pool_recommendations["recommendations"].append(
                        "Consider splitting large node pools for better management"
                    )
            
            # Management recommendations
            if not management.get("auto_upgrade", False):
                pool_recommendations["recommendations"].append(
                    "Enable auto-upgrade for security and feature updates"
                )
            
            if not management.get("auto_repair", False):
                pool_recommendations["recommendations"].append(
                    "Enable auto-repair for better reliability"
                )
            
            # Zone distribution
            locations = pool.get("locations", [])
            if len(locations) < 2:
                pool_recommendations["recommendations"].append(
                    "Deploy across multiple zones for high availability"
                )
            
            if pool_recommendations["recommendations"]:
                recommendations.append(pool_recommendations)
        
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
        
        # RBAC recommendations
        recommendations.append("Implement least privilege RBAC policies")
        recommendations.append("Regular security scanning of container images")
        recommendations.append("Enable audit logging for compliance")
        
        return recommendations
    
    def _analyze_gke_scaling(self, cluster_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze GKE scaling configuration and patterns"""
        
        recommendations = []
        metrics = cluster_data.get("metrics", {})
        node_pools = cluster_data.get("node_pools", [])
        
        cpu_util = metrics.get("cpu_utilization", 0.5)
        memory_util = metrics.get("memory_utilization", 0.5)
        pod_count = metrics.get("pod_count", 0)
        running_pods = metrics.get("running_pods", 0)
        pending_pods = metrics.get("pending_pods", 0)
        
        # Cluster-level scaling analysis
        cluster_scaling = {
            "type": "cluster",
            "recommendations": []
        }
        
        # Resource utilization analysis
        if cpu_util > 0.80 or memory_util > 0.80:
            cluster_scaling["recommendations"].append(
                "High resource utilization detected - consider scaling up nodes"
            )
        elif cpu_util < 0.30 and memory_util < 0.30:
            cluster_scaling["recommendations"].append(
                "Low resource utilization - consider scaling down or using smaller instances"
            )
        
        # Pending pods analysis
        if pending_pods > 0:
            cluster_scaling["recommendations"].append(
                f"{pending_pods} pending pods detected - insufficient cluster capacity"
            )
        
        # HPA recommendations
        hpa_enabled = cluster_data.get("addons_config", {}).get("horizontal_pod_autoscaling", {}).get("disabled", True)
        if hpa_enabled:  # Actually means disabled=False
            cluster_scaling["recommendations"].append(
                "Horizontal Pod Autoscaler is enabled - ensure HPA configs are optimized"
            )
        else:
            cluster_scaling["recommendations"].append(
                "Enable Horizontal Pod Autoscaler for workload-based scaling"
            )
        
        recommendations.append(cluster_scaling)
        
        # Node pool-specific scaling
        for pool in node_pools:
            pool_name = pool.get("name")
            autoscaling = pool.get("autoscaling", {})
            current_nodes = pool.get("current_node_count", 0)
            
            pool_scaling = {
                "type": "node_pool",
                "pool_name": pool_name,
                "recommendations": []
            }
            
            if autoscaling.get("enabled", False):
                min_nodes = autoscaling.get("min_node_count", 0)
                max_nodes = autoscaling.get("max_node_count", 0)
                
                # Analyze scaling configuration
                if current_nodes == max_nodes:
                    pool_scaling["recommendations"].append(
                        "Node pool at maximum capacity - consider increasing max nodes"
                    )
                elif current_nodes == min_nodes and cpu_util < 0.40:
                    pool_scaling["recommendations"].append(
                        "Consider reducing minimum node count for cost optimization"
                    )
                
                # Scaling efficiency
                scaling_ratio = max_nodes / min_nodes if min_nodes > 0 else float('inf')
                if scaling_ratio > 10:
                    pool_scaling["recommendations"].append(
                        "Large scaling ratio may cause slow scale-up - consider multiple pools"
                    )
            
            if pool_scaling["recommendations"]:
                recommendations.append(pool_scaling)
        
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
        
        # Backup recommendations
        recommendations.append("Implement regular backup strategy for cluster configuration")
        recommendations.append("Use GitOps for declarative cluster management")
        
        return recommendations
    
    def predict_gke_scaling_needs(self, cluster_name: str, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict GKE scaling needs based on historical metrics
        """
        
        if not metrics_history:
            return {"prediction": "insufficient_data", "confidence": 0.0}
        
        # Analyze resource patterns
        cpu_values = [m.get("cpu_utilization", 0) for m in metrics_history]
        memory_values = [m.get("memory_utilization", 0) for m in metrics_history]
        pod_counts = [m.get("pod_count", 0) for m in metrics_history]
        node_counts = [m.get("node_count", 0) for m in metrics_history]
        
        avg_cpu = sum(cpu_values) / len(cpu_values)
        avg_memory = sum(memory_values) / len(memory_values)
        avg_pods = sum(pod_counts) / len(pod_counts)
        peak_cpu = max(cpu_values) if cpu_values else 0
        peak_memory = max(memory_values) if memory_values else 0
        
        # Trend analysis
        if len(cpu_values) >= 7:
            recent_cpu = sum(cpu_values[-7:]) / 7
            earlier_cpu = sum(cpu_values[:7]) / 7
            cpu_trend = "increasing" if recent_cpu > earlier_cpu * 1.1 else "stable"
        else:
            cpu_trend = "stable"
        
        # Pod count trend
        if len(pod_counts) >= 7:
            recent_pods = sum(pod_counts[-7:]) / 7
            earlier_pods = sum(pod_counts[:7]) / 7
            pod_trend = "increasing" if recent_pods > earlier_pods * 1.1 else "stable"
        else:
            pod_trend = "stable"
        
        prediction = {
            "cluster_name": cluster_name,
            "resource_analysis": {
                "average_cpu_utilization": avg_cpu,
                "average_memory_utilization": avg_memory,
                "peak_cpu_utilization": peak_cpu,
                "peak_memory_utilization": peak_memory,
                "average_pod_count": avg_pods,
                "cpu_trend": cpu_trend,
                "pod_trend": pod_trend
            },
            "scaling_prediction": self._generate_gke_scaling_prediction(avg_cpu, avg_memory, peak_cpu, cpu_trend, pod_trend),
            "capacity_recommendations": self._generate_gke_capacity_recommendations(avg_cpu, avg_memory, avg_pods),
            "confidence_score": min(len(metrics_history) / 168.0, 1.0)  # 1 week of hourly data = 100%
        }
        
        return prediction
    
    def _generate_gke_scaling_prediction(self, avg_cpu: float, avg_memory: float, peak_cpu: float, cpu_trend: str, pod_trend: str) -> Dict[str, Any]:
        """Generate GKE scaling predictions"""
        
        if cpu_trend == "increasing" and pod_trend == "increasing" and peak_cpu > 0.75:
            return {
                "action": "proactive_scale_up",
                "confidence": "high",
                "recommendation": "Workload trending upward - prepare for cluster expansion",
                "suggested_actions": [
                    "Increase node pool maximum size",
                    "Consider adding spot/preemptible nodes",
                    "Review HPA configurations"
                ]
            }
        elif peak_cpu > 0.85 or avg_memory > 0.80:
            return {
                "action": "immediate_scale_up",
                "confidence": "high",
                "recommendation": "High resource utilization - immediate scaling recommended",
                "suggested_actions": [
                    "Scale up node pools immediately",
                    "Check for resource constraints",
                    "Review pod resource requests"
                ]
            }
        elif avg_cpu < 0.25 and avg_memory < 0.30:
            return {
                "action": "scale_down",
                "confidence": "medium",
                "recommendation": "Low resource utilization - consider scaling down",
                "suggested_actions": [
                    "Reduce minimum node count",
                    "Consolidate workloads",
                    "Review node pool configurations"
                ]
            }
        else:
            return {
                "action": "maintain",
                "confidence": "medium",
                "recommendation": "Resource utilization appears optimal",
                "suggested_actions": [
                    "Continue monitoring",
                    "Optimize HPA settings",
                    "Review resource requests and limits"
                ]
            }
    
    def _generate_gke_capacity_recommendations(self, avg_cpu: float, avg_memory: float, avg_pods: float) -> List[str]:
        """Generate GKE capacity planning recommendations"""
        
        recommendations = []
        
        if avg_pods > 100:
            recommendations.append("High pod density - ensure adequate node resources and consider cluster autoscaling")
        
        if avg_cpu > 0.70:
            recommendations.append("High CPU utilization - consider vertical pod autoscaling for better resource allocation")
        
        if avg_memory > 0.75:
            recommendations.append("High memory utilization - review memory requests and limits")
        
        recommendations.append("Implement resource quotas to prevent resource exhaustion")
        recommendations.append("Use node affinity and pod disruption budgets for better workload distribution")
        recommendations.append("Monitor cluster autoscaler performance and tune accordingly")
        
        return recommendations
    
    def generate_gke_security_assessment(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive GKE security assessment
        """
        
        assessment = {
            "cluster_name": cluster_data.get("cluster_name"),
            "assessment_timestamp": datetime.now().isoformat(),
            "overall_security_score": 0.0,
            "security_findings": [],
            "compliance_status": {},
            "risk_level": "medium",
            "recommendations": []
        }
        
        # Security configuration audit
        security_findings = self._audit_gke_security_config(cluster_data)
        assessment["security_findings"].extend(security_findings)
        
        # Node security audit
        node_findings = self._audit_node_security(cluster_data.get("node_pools", []))
        assessment["security_findings"].extend(node_findings)
        
        # Network security audit
        network_findings = self._audit_network_security(cluster_data)
        assessment["security_findings"].extend(network_findings)
        
        # Calculate overall security score
        assessment["overall_security_score"] = self._calculate_gke_security_score(assessment["security_findings"])
        
        # Determine risk level
        if assessment["overall_security_score"] < 40:
            assessment["risk_level"] = "critical"
        elif assessment["overall_security_score"] < 70:
            assessment["risk_level"] = "high"
        elif assessment["overall_security_score"] < 85:
            assessment["risk_level"] = "medium"
        else:
            assessment["risk_level"] = "low"
        
        # Generate recommendations
        assessment["recommendations"] = self._generate_gke_security_recommendations(assessment["security_findings"])
        
        return assessment
    
    def _audit_gke_security_config(self, cluster_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Audit GKE security configuration"""
        
        findings = []
        security_config = cluster_data.get("security_config", {})
        private_cluster = cluster_data.get("private_cluster_config", {})
        
        # Workload Identity
        if not security_config.get("workload_identity_enabled", False):
            findings.append({
                "severity": "high",
                "category": "authentication",
                "finding": "Workload Identity is not enabled",
                "recommendation": "Enable Workload Identity for secure service account authentication"
            })
        
        # Binary Authorization
        if not security_config.get("binary_authorization_enabled", False):
            findings.append({
                "severity": "medium",
                "category": "container_security",
                "finding": "Binary Authorization is not enabled",
                "recommendation": "Enable Binary Authorization to ensure only trusted container images are deployed"
            })
        
        # Private nodes
        if not private_cluster.get("enable_private_nodes", False):
            findings.append({
                "severity": "high",
                "category": "network_security",
                "finding": "Private nodes are not enabled",
                "recommendation": "Enable private nodes to isolate worker nodes from public internet"
            })
        
        # Network Policy
        if not security_config.get("network_policy_enabled", False):
            findings.append({
                "severity": "medium",
                "category": "network_security", 
                "finding": "Network Policy is not enabled",
                "recommendation": "Enable Network Policy for pod-to-pod traffic control"
            })
        
        return findings
    
    def _audit_node_security(self, node_pools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Audit node pool security configurations"""
        
        findings = []
        
        for pool in node_pools:
            pool_name = pool.get("name")
            node_config = pool.get("node_config", {})
            
            # Image type check
            image_type = node_config.get("image_type", "")
            if "COS" not in image_type:
                findings.append({
                    "severity": "medium",
                    "category": "node_security",
                    "finding": f"Node pool {pool_name} not using Container-Optimized OS",
                    "recommendation": "Use Container-Optimized OS (COS) for better security"
                })
            
            # Automatic upgrades
            management = pool.get("management", {})
            if not management.get("auto_upgrade", False):
                findings.append({
                    "severity": "medium",
                    "category": "node_security",
                    "finding": f"Auto-upgrade disabled for node pool {pool_name}",
                    "recommendation": "Enable auto-upgrade for security patches"
                })
        
        return findings
    
    def _audit_network_security(self, cluster_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Audit network security configuration"""
        
        findings = []
        addons = cluster_data.get("addons_config", {})
        
        # Kubernetes Dashboard
        if not addons.get("kubernetes_dashboard", {}).get("disabled", True):
            findings.append({
                "severity": "critical",
                "category": "network_security",
                "finding": "Kubernetes Dashboard is enabled",
                "recommendation": "Disable Kubernetes Dashboard and use Cloud Console for cluster management"
            })
        
        return findings
    
    def _calculate_gke_security_score(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate overall GKE security score"""
        
        base_score = 100.0
        
        for finding in findings:
            severity = finding.get("severity", "low")
            
            if severity == "critical":
                base_score -= 30
            elif severity == "high":
                base_score -= 20
            elif severity == "medium":
                base_score -= 10
            elif severity == "low":
                base_score -= 5
        
        return max(0.0, base_score)
    
    def _generate_gke_security_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on findings"""
        
        recommendations = []
        
        # Group findings by category
        categories = {}
        for finding in findings:
            category = finding.get("category", "general")
            if category not in categories:
                categories[category] = []
            categories[category].append(finding)
        
        # Generate category-specific recommendations
        if "authentication" in categories:
            recommendations.append("Implement strong authentication mechanisms")
            recommendations.append("Use Workload Identity for service account management")
        
        if "network_security" in categories:
            recommendations.append("Implement network segmentation and policies")
            recommendations.append("Use private clusters for sensitive workloads")
        
        if "container_security" in categories:
            recommendations.append("Implement container image scanning and validation")
            recommendations.append("Use admission controllers for policy enforcement")
        
        # General recommendations
        recommendations.append("Regular security audits and compliance checks")
        recommendations.append("Implement least privilege access controls")
        recommendations.append("Monitor cluster activity with Cloud Audit Logs")
        
        return recommendations
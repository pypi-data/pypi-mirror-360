"""
GKE Scaling Predictor

Predictive scaling analysis and recommendations for GCP GKE clusters.
"""

from typing import Dict, Any, List
from .gke_types import GKEScalingPrediction


class GKEScalingPredictor:
    """
    GKE Scaling Prediction Engine
    
    Provides intelligent scaling predictions including:
    - Resource utilization trend analysis
    - Predictive auto-scaling recommendations
    - Capacity planning based on historical patterns
    - Node pool scaling optimization
    """
    
    def __init__(self, utilization_thresholds: Dict[str, Any]):
        self.utilization_thresholds = utilization_thresholds
    
    def predict_scaling_needs(self, cluster_name: str, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict GKE scaling needs based on historical metrics"""
        
        if not metrics_history:
            return {"prediction": "insufficient_data", "confidence": 0.0}
        
        # Analyze resource patterns
        resource_analysis = self._analyze_resource_patterns(metrics_history)
        
        # Generate scaling prediction
        scaling_prediction = self._generate_scaling_prediction(
            resource_analysis["avg_cpu"],
            resource_analysis["avg_memory"],
            resource_analysis["peak_cpu"],
            resource_analysis["cpu_trend"],
            resource_analysis["pod_trend"]
        )
        
        # Generate capacity recommendations
        capacity_recommendations = self._generate_capacity_recommendations(
            resource_analysis["avg_cpu"],
            resource_analysis["avg_memory"],
            resource_analysis["avg_pods"]
        )
        
        return {
            "cluster_name": cluster_name,
            "resource_analysis": resource_analysis,
            "scaling_prediction": scaling_prediction,
            "capacity_recommendations": capacity_recommendations,
            "confidence_score": min(len(metrics_history) / 168.0, 1.0)  # 1 week of hourly data = 100%
        }
    
    def _analyze_resource_patterns(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze resource utilization patterns"""
        
        cpu_values = [m.get("cpu_utilization", 0) for m in metrics_history]
        memory_values = [m.get("memory_utilization", 0) for m in metrics_history]
        pod_counts = [m.get("pod_count", 0) for m in metrics_history]
        node_counts = [m.get("node_count", 0) for m in metrics_history]
        
        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
        avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0
        avg_pods = sum(pod_counts) / len(pod_counts) if pod_counts else 0
        peak_cpu = max(cpu_values) if cpu_values else 0
        peak_memory = max(memory_values) if memory_values else 0
        
        # Trend analysis
        cpu_trend = self._calculate_trend(cpu_values)
        memory_trend = self._calculate_trend(memory_values)
        pod_trend = self._calculate_trend(pod_counts)
        
        return {
            "average_cpu_utilization": avg_cpu,
            "average_memory_utilization": avg_memory,
            "peak_cpu_utilization": peak_cpu,
            "peak_memory_utilization": peak_memory,
            "average_pod_count": avg_pods,
            "cpu_trend": cpu_trend,
            "memory_trend": memory_trend,
            "pod_trend": pod_trend,
            "avg_cpu": avg_cpu,
            "avg_memory": avg_memory,
            "avg_pods": avg_pods
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values"""
        
        if len(values) < 7:
            return "stable"
        
        recent_avg = sum(values[-7:]) / 7
        earlier_avg = sum(values[:7]) / 7
        
        if recent_avg > earlier_avg * 1.1:
            return "increasing"
        elif recent_avg < earlier_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_scaling_prediction(self, avg_cpu: float, avg_memory: float, 
                                   peak_cpu: float, cpu_trend: str, pod_trend: str) -> GKEScalingPrediction:
        """Generate GKE scaling predictions"""
        
        # Proactive scale up scenario
        if cpu_trend == "increasing" and pod_trend == "increasing" and peak_cpu > 0.75:
            return GKEScalingPrediction(
                action="proactive_scale_up",
                confidence="high",
                recommendation="Workload trending upward - prepare for cluster expansion",
                suggested_actions=[
                    "Increase node pool maximum size",
                    "Consider adding spot/preemptible nodes",
                    "Review HPA configurations"
                ]
            )
        
        # Immediate scale up scenario
        elif peak_cpu > 0.85 or avg_memory > 0.80:
            return GKEScalingPrediction(
                action="immediate_scale_up",
                confidence="high",
                recommendation="High resource utilization - immediate scaling recommended",
                suggested_actions=[
                    "Scale up node pools immediately",
                    "Check for resource constraints",
                    "Review pod resource requests"
                ]
            )
        
        # Scale down scenario
        elif avg_cpu < 0.25 and avg_memory < 0.30:
            return GKEScalingPrediction(
                action="scale_down",
                confidence="medium",
                recommendation="Low resource utilization - consider scaling down",
                suggested_actions=[
                    "Reduce minimum node count",
                    "Consolidate workloads",
                    "Review node pool configurations"
                ]
            )
        
        # Maintain current state
        else:
            return GKEScalingPrediction(
                action="maintain",
                confidence="medium",
                recommendation="Resource utilization appears optimal",
                suggested_actions=[
                    "Continue monitoring",
                    "Optimize HPA settings",
                    "Review resource requests and limits"
                ]
            )
    
    def _generate_capacity_recommendations(self, avg_cpu: float, avg_memory: float, avg_pods: float) -> List[str]:
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
    
    def analyze_node_pool_scaling(self, cluster_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze node pool-specific scaling configuration and patterns"""
        
        recommendations = []
        metrics = cluster_data.get("metrics", {})
        node_pools = cluster_data.get("node_pools", [])
        
        cpu_util = metrics.get("cpu_utilization", 0.5)
        memory_util = metrics.get("memory_utilization", 0.5)
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
        hpa_enabled = not cluster_data.get("addons_config", {}).get("horizontal_pod_autoscaling", {}).get("disabled", True)
        if hpa_enabled:
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
            else:
                pool_scaling["recommendations"].append(
                    "Enable autoscaling for better resource optimization"
                )
            
            if pool_scaling["recommendations"]:
                recommendations.append(pool_scaling)
        
        return recommendations
    
    def predict_peak_times(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict when peak usage typically occurs"""
        
        if len(metrics_history) < 24:
            return {"prediction": "insufficient_data"}
        
        # Group by hour of day and find peak patterns
        hourly_usage = {}
        for metric in metrics_history:
            timestamp = metric.get("timestamp")
            if timestamp:
                try:
                    from datetime import datetime
                    hour = datetime.fromisoformat(timestamp).hour
                    cpu = metric.get("cpu_utilization", 0)
                    memory = metric.get("memory_utilization", 0)
                    
                    if hour not in hourly_usage:
                        hourly_usage[hour] = {"cpu": [], "memory": []}
                    
                    hourly_usage[hour]["cpu"].append(cpu)
                    hourly_usage[hour]["memory"].append(memory)
                except:
                    continue
        
        if not hourly_usage:
            return {"prediction": "insufficient_data"}
        
        # Calculate average utilization by hour
        hourly_averages = {}
        for hour, metrics in hourly_usage.items():
            avg_cpu = sum(metrics["cpu"]) / len(metrics["cpu"])
            avg_memory = sum(metrics["memory"]) / len(metrics["memory"])
            hourly_averages[hour] = {
                "cpu": avg_cpu,
                "memory": avg_memory,
                "combined": (avg_cpu + avg_memory) / 2
            }
        
        # Find peak hours
        peak_hour = max(hourly_averages.keys(), 
                       key=lambda h: hourly_averages[h]["combined"])
        
        return {
            "peak_hour": f"{peak_hour:02d}:00",
            "peak_cpu_utilization": hourly_averages[peak_hour]["cpu"],
            "peak_memory_utilization": hourly_averages[peak_hour]["memory"],
            "hourly_pattern": hourly_averages,
            "recommendation": f"Consider proactive scaling before {peak_hour:02d}:00"
        }
    
    def calculate_scaling_efficiency(self, cluster_data: Dict[str, Any], 
                                   metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate how efficiently the cluster is scaling"""
        
        if len(metrics_history) < 10:
            return {"efficiency": "insufficient_data"}
        
        # Analyze scaling events (node count changes)
        node_counts = [m.get("node_count", 0) for m in metrics_history]
        cpu_values = [m.get("cpu_utilization", 0) for m in metrics_history]
        
        scaling_events = 0
        over_provisioning_events = 0
        under_provisioning_events = 0
        
        for i in range(1, len(node_counts)):
            if node_counts[i] != node_counts[i-1]:
                scaling_events += 1
                
                # Check if scaling was appropriate
                if node_counts[i] > node_counts[i-1] and cpu_values[i-1] < 0.50:
                    over_provisioning_events += 1
                elif node_counts[i] < node_counts[i-1] and cpu_values[i-1] > 0.80:
                    under_provisioning_events += 1
        
        efficiency_score = 100
        if scaling_events > 0:
            efficiency_score -= (over_provisioning_events / scaling_events) * 30
            efficiency_score -= (under_provisioning_events / scaling_events) * 40
        
        return {
            "efficiency_score": max(0, efficiency_score),
            "total_scaling_events": scaling_events,
            "over_provisioning_events": over_provisioning_events,
            "under_provisioning_events": under_provisioning_events,
            "recommendations": self._generate_efficiency_recommendations(
                over_provisioning_events, under_provisioning_events, scaling_events
            )
        }
    
    def _generate_efficiency_recommendations(self, over_prov: int, under_prov: int, total: int) -> List[str]:
        """Generate recommendations for scaling efficiency"""
        
        recommendations = []
        
        if total == 0:
            recommendations.append("No scaling events detected - consider enabling cluster autoscaler")
            return recommendations
        
        over_prov_ratio = over_prov / total if total > 0 else 0
        under_prov_ratio = under_prov / total if total > 0 else 0
        
        if over_prov_ratio > 0.3:
            recommendations.append("Frequent over-provisioning detected - adjust scale-up thresholds")
            recommendations.append("Consider longer stabilization periods before scaling up")
        
        if under_prov_ratio > 0.2:
            recommendations.append("Under-provisioning events detected - lower scale-up thresholds")
            recommendations.append("Consider more aggressive scaling policies for critical workloads")
        
        if over_prov_ratio < 0.1 and under_prov_ratio < 0.1:
            recommendations.append("Scaling efficiency is optimal - continue current configuration")
        
        return recommendations
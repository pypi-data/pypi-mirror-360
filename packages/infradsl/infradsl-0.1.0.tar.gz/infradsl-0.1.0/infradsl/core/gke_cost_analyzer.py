"""
GKE Cost Analyzer

Specialized cost analysis and optimization for GCP GKE clusters.
"""

from typing import Dict, Any, List
from .gke_types import GKECostAnalysis


class GKECostAnalyzer:
    """
    GKE Cost Analysis Engine
    
    Provides intelligent cost optimization including:
    - Preemptible/spot instance analysis
    - Machine type optimization
    - Committed Use Discount recommendations
    - Autoscaling cost impact analysis
    """
    
    def __init__(self, optimization_rules: Dict[str, Any]):
        self.optimization_rules = optimization_rules
    
    def analyze_cluster_costs(self, cluster_data: Dict[str, Any]) -> GKECostAnalysis:
        """Analyze cluster-wide cost optimization opportunities"""
        
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
        
        # Analyze node composition
        node_analysis = self._analyze_node_composition(node_pools, current_cost, metrics)
        optimized_cost -= node_analysis["savings"]
        recommendations.extend(node_analysis["recommendations"])
        
        # Committed Use Discount analysis
        cud_analysis = self._analyze_committed_use_discounts(metrics)
        recommendations.extend(cud_analysis)
        
        # Autoscaling cost impact
        autoscaling_analysis = self._analyze_autoscaling_costs(node_pools)
        recommendations.extend(autoscaling_analysis)
        
        return GKECostAnalysis(
            current_monthly_cost=current_cost,
            optimized_monthly_cost=optimized_cost,
            potential_savings=current_cost - optimized_cost,
            cost_breakdown=cost_breakdown,
            recommendations=recommendations
        )
    
    def _analyze_node_composition(self, node_pools: List[Dict[str, Any]], 
                                current_cost: float, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze node pool composition for cost optimization"""
        
        total_standard_nodes = 0
        total_preemptible_nodes = 0
        total_spot_nodes = 0
        savings = 0.0
        recommendations = []
        
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
                    pool_savings = current_cost * 0.30 * (node_count / sum(p.get("current_node_count", 0) for p in node_pools))
                    savings += pool_savings
        
        # Preemptible/Spot recommendations
        total_nodes = total_standard_nodes + total_preemptible_nodes + total_spot_nodes
        if total_nodes > 0:
            preemptible_ratio = (total_preemptible_nodes + total_spot_nodes) / total_nodes
            
            if preemptible_ratio < 0.30 and total_standard_nodes > 2:
                recommendations.append("Increase preemptible/spot node usage for cost savings (up to 80% reduction)")
                # Estimate savings from converting some standard nodes
                convertible_nodes = min(total_standard_nodes - 2, int(total_standard_nodes * 0.5))
                estimated_savings = current_cost * 0.80 * (convertible_nodes / total_nodes)
                savings += estimated_savings
        
        return {
            "savings": savings,
            "recommendations": recommendations,
            "node_composition": {
                "standard": total_standard_nodes,
                "preemptible": total_preemptible_nodes,
                "spot": total_spot_nodes
            }
        }
    
    def _analyze_committed_use_discounts(self, metrics: Dict[str, Any]) -> List[str]:
        """Analyze Committed Use Discount opportunities"""
        
        recommendations = []
        cpu_util = metrics.get("cpu_utilization", 0.5)
        
        if cpu_util > self.optimization_rules["cost_optimization"]["committed_use_threshold"]:
            recommendations.append("Consider Committed Use Discounts for steady workloads (up to 57% savings)")
        
        return recommendations
    
    def _analyze_autoscaling_costs(self, node_pools: List[Dict[str, Any]]) -> List[str]:
        """Analyze autoscaling configuration for cost optimization"""
        
        recommendations = []
        
        for pool in node_pools:
            pool_name = pool.get("name")
            if not pool.get("autoscaling", {}).get("enabled", False):
                recommendations.append(f"Enable autoscaling for {pool_name} to optimize resource usage")
        
        return recommendations
    
    def calculate_spot_savings_potential(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate potential savings from increased spot instance usage"""
        
        node_pools = cluster_data.get("node_pools", [])
        current_cost = cluster_data.get("metrics", {}).get("monthly_cost_estimate", 0.0)
        
        standard_nodes = 0
        total_nodes = 0
        
        for pool in node_pools:
            node_count = pool.get("current_node_count", 0)
            node_config = pool.get("node_config", {})
            
            total_nodes += node_count
            
            if not node_config.get("spot", False) and not node_config.get("preemptible", False):
                standard_nodes += node_count
        
        if total_nodes == 0:
            return {"potential_savings": 0.0, "recommendation": "No nodes to optimize"}
        
        # Assume we can convert 70% of standard nodes to spot (keeping some for stability)
        convertible_nodes = int(standard_nodes * 0.7)
        spot_savings_rate = self.optimization_rules["cost_optimization"]["preemptible_savings"]
        
        potential_savings = current_cost * (convertible_nodes / total_nodes) * spot_savings_rate
        
        return {
            "potential_monthly_savings": potential_savings,
            "potential_annual_savings": potential_savings * 12,
            "convertible_nodes": convertible_nodes,
            "recommendation": f"Convert {convertible_nodes} standard nodes to spot instances"
        }
    
    def generate_rightsizing_recommendations(self, cluster_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate machine type rightsizing recommendations"""
        
        recommendations = []
        node_pools = cluster_data.get("node_pools", [])
        metrics = cluster_data.get("metrics", {})
        
        cpu_util = metrics.get("cpu_utilization", 0.5)
        memory_util = metrics.get("memory_utilization", 0.5)
        
        for pool in node_pools:
            pool_name = pool.get("name")
            node_config = pool.get("node_config", {})
            machine_type = node_config.get("machine_type", "")
            node_count = pool.get("current_node_count", 0)
            
            recommendation = {
                "pool_name": pool_name,
                "current_machine_type": machine_type,
                "current_node_count": node_count,
                "recommendations": []
            }
            
            # Analyze machine type efficiency
            if "standard-" in machine_type:
                if cpu_util < 0.30 and memory_util < 0.30:
                    # Suggest smaller machine type
                    if "standard-4" in machine_type:
                        recommendation["recommended_machine_type"] = machine_type.replace("standard-4", "standard-2")
                        recommendation["estimated_savings"] = "~50%"
                    elif "standard-8" in machine_type:
                        recommendation["recommended_machine_type"] = machine_type.replace("standard-8", "standard-4")
                        recommendation["estimated_savings"] = "~50%"
                    
                    recommendation["recommendations"].append("Downsize machine type due to low utilization")
                
                elif cpu_util > 0.80 or memory_util > 0.80:
                    # Suggest larger machine type or more nodes
                    recommendation["recommendations"].append("Consider larger machine type or increase node count")
            
            if recommendation["recommendations"]:
                recommendations.append(recommendation)
        
        return recommendations
"""
AWS ECS/Fargate Intelligence

Advanced intelligence for AWS Elastic Container Service (ECS) and Fargate
providing intelligent container orchestration, auto-scaling, and optimization.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from .aws_intelligence_base import AWSIntelligenceBase
from .stateless_intelligence import (
    ResourceType, ResourceFingerprint, ChangeImpactAnalysis, 
    ResourceHealth
)


class AWSECSIntelligence(AWSIntelligenceBase):
    """
    AWS ECS/Fargate Intelligence Engine
    
    Provides intelligent container orchestration including:
    - Smart task definition optimization
    - Predictive auto-scaling based on patterns
    - Service mesh integration recommendations
    - Cost optimization for Fargate vs EC2
    - Container health monitoring and diagnostics
    """
    
    def __init__(self):
        super().__init__(ResourceType.CONTAINER)
        self.optimization_rules = {
            "cpu_utilization_thresholds": {
                "scale_up": 0.70,    # Scale up at 70% CPU
                "scale_down": 0.30,  # Scale down at 30% CPU
                "optimal_range": (0.50, 0.70)
            },
            "memory_utilization_thresholds": {
                "scale_up": 0.80,    # Scale up at 80% memory
                "scale_down": 0.40,  # Scale down at 40% memory
                "optimal_range": (0.60, 0.75)
            },
            "cost_optimization": {
                "fargate_breakeven_tasks": 5,  # Use Fargate for < 5 tasks
                "spot_instance_recommendation": True,
                "reserved_capacity_threshold": 0.80
            }
        }
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing ECS clusters, services, and tasks"""
        
        # Mock implementation - in production would use boto3
        return {
            "web-cluster": {
                "cluster_name": "web-cluster",
                "cluster_arn": "arn:aws:ecs:us-east-1:123456789012:cluster/web-cluster",
                "status": "ACTIVE",
                "capacity_providers": ["FARGATE", "EC2"],
                "services": {
                    "web-service": {
                        "service_name": "web-service",
                        "task_definition": "web-app:1",
                        "desired_count": 3,
                        "running_count": 3,
                        "launch_type": "FARGATE",
                        "platform_version": "1.4.0",
                        "cpu_utilization": 0.65,
                        "memory_utilization": 0.75,
                        "load_balancer": "web-alb"
                    }
                },
                "tasks": 3,
                "active_services": 1,
                "region": "us-east-1",
                "vpc_configuration": {
                    "subnets": ["subnet-12345", "subnet-67890"],
                    "security_groups": ["sg-web-ecs"]
                }
            },
            "api-cluster": {
                "cluster_name": "api-cluster",
                "cluster_arn": "arn:aws:ecs:us-east-1:123456789012:cluster/api-cluster",
                "status": "ACTIVE",
                "capacity_providers": ["EC2"],
                "services": {
                    "api-service": {
                        "service_name": "api-service",
                        "task_definition": "api-app:2",
                        "desired_count": 5,
                        "running_count": 4,
                        "launch_type": "EC2",
                        "cpu_utilization": 0.45,
                        "memory_utilization": 0.55,
                        "auto_scaling_enabled": True
                    }
                },
                "tasks": 4,
                "active_services": 1,
                "region": "us-east-1"
            }
        }
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ECS configuration from cloud state"""
        
        return {
            "cluster_name": cloud_state.get("cluster_name"),
            "capacity_providers": cloud_state.get("capacity_providers", []),
            "services": cloud_state.get("services", {}),
            "region": cloud_state.get("region"),
            "vpc_configuration": cloud_state.get("vpc_configuration", {}),
            "total_tasks": cloud_state.get("tasks", 0),
            "total_services": cloud_state.get("active_services", 0)
        }
    
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """Generate hash for ECS configuration"""
        
        # Focus on key configuration elements that affect functionality
        key_config = {
            "cluster_name": config.get("cluster_name"),
            "capacity_providers": sorted(config.get("capacity_providers", [])),
            "services": {
                name: {
                    "task_definition": svc.get("task_definition"),
                    "desired_count": svc.get("desired_count"),
                    "launch_type": svc.get("launch_type")
                }
                for name, svc in config.get("services", {}).items()
            },
            "vpc_configuration": config.get("vpc_configuration", {})
        }
        
        return str(hash(json.dumps(key_config, sort_keys=True)))
    
    def analyze_ecs_optimization(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze ECS cluster for optimization opportunities
        """
        
        optimization_analysis = {
            "cluster_name": cluster_data.get("cluster_name"),
            "current_cost_estimate": 0.0,
            "optimized_cost_estimate": 0.0,
            "potential_savings": 0.0,
            "recommendations": [],
            "scaling_recommendations": [],
            "launch_type_recommendations": {},
            "service_mesh_recommendations": []
        }
        
        # Analyze each service
        services = cluster_data.get("services", {})
        total_current_cost = 0.0
        total_optimized_cost = 0.0
        
        for service_name, service_data in services.items():
            service_analysis = self._analyze_service_optimization(service_name, service_data)
            
            total_current_cost += service_analysis["current_monthly_cost"]
            total_optimized_cost += service_analysis["optimized_monthly_cost"]
            
            if service_analysis["recommendations"]:
                optimization_analysis["recommendations"].extend(service_analysis["recommendations"])
            
            if service_analysis["scaling_recommendation"]:
                optimization_analysis["scaling_recommendations"].append(service_analysis["scaling_recommendation"])
            
            optimization_analysis["launch_type_recommendations"][service_name] = service_analysis["launch_type_recommendation"]
        
        optimization_analysis["current_cost_estimate"] = total_current_cost
        optimization_analysis["optimized_cost_estimate"] = total_optimized_cost
        optimization_analysis["potential_savings"] = total_current_cost - total_optimized_cost
        
        # Add cluster-level recommendations
        cluster_recommendations = self._generate_cluster_recommendations(cluster_data)
        optimization_analysis["recommendations"].extend(cluster_recommendations)
        
        # Service mesh recommendations
        if len(services) >= 3:
            optimization_analysis["service_mesh_recommendations"] = [
                "Consider implementing AWS App Mesh for service-to-service communication",
                "Enable service discovery with AWS Cloud Map",
                "Implement distributed tracing with AWS X-Ray"
            ]
        
        return optimization_analysis
    
    def _analyze_service_optimization(self, service_name: str, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual service for optimization"""
        
        current_count = service_data.get("desired_count", 1)
        launch_type = service_data.get("launch_type", "FARGATE")
        cpu_util = service_data.get("cpu_utilization", 0.5)
        memory_util = service_data.get("memory_utilization", 0.5)
        
        # Cost estimation (simplified)
        if launch_type == "FARGATE":
            cost_per_task_hour = 0.04048  # 0.25 vCPU, 0.5GB memory
            current_monthly_cost = current_count * cost_per_task_hour * 24 * 30
        else:  # EC2
            cost_per_task_hour = 0.025  # Estimated EC2 cost
            current_monthly_cost = current_count * cost_per_task_hour * 24 * 30
        
        analysis = {
            "service_name": service_name,
            "current_monthly_cost": current_monthly_cost,
            "optimized_monthly_cost": current_monthly_cost,
            "recommendations": [],
            "scaling_recommendation": None,
            "launch_type_recommendation": launch_type
        }
        
        # Scaling recommendations
        cpu_rules = self.optimization_rules["cpu_utilization_thresholds"]
        memory_rules = self.optimization_rules["memory_utilization_thresholds"]
        
        if cpu_util > cpu_rules["scale_up"] or memory_util > memory_rules["scale_up"]:
            recommended_count = min(current_count + 2, current_count * 2)
            analysis["scaling_recommendation"] = {
                "action": "scale_up",
                "current_count": current_count,
                "recommended_count": recommended_count,
                "reason": f"High resource utilization: CPU {cpu_util:.1%}, Memory {memory_util:.1%}"
            }
        elif cpu_util < cpu_rules["scale_down"] and memory_util < memory_rules["scale_down"]:
            recommended_count = max(1, current_count - 1)
            if recommended_count < current_count:
                analysis["scaling_recommendation"] = {
                    "action": "scale_down",
                    "current_count": current_count,
                    "recommended_count": recommended_count,
                    "reason": f"Low resource utilization: CPU {cpu_util:.1%}, Memory {memory_util:.1%}"
                }
                analysis["optimized_monthly_cost"] = recommended_count * cost_per_task_hour * 24 * 30
        
        # Launch type recommendations
        cost_rules = self.optimization_rules["cost_optimization"]
        
        if launch_type == "EC2" and current_count < cost_rules["fargate_breakeven_tasks"]:
            analysis["launch_type_recommendation"] = "FARGATE"
            analysis["recommendations"].append(
                f"Switch {service_name} to Fargate for better cost efficiency with {current_count} tasks"
            )
            # Recalculate cost for Fargate
            fargate_cost = current_count * 0.04048 * 24 * 30
            if fargate_cost < current_monthly_cost:
                analysis["optimized_monthly_cost"] = fargate_cost
        
        elif launch_type == "FARGATE" and current_count >= cost_rules["fargate_breakeven_tasks"]:
            analysis["launch_type_recommendation"] = "EC2"
            analysis["recommendations"].append(
                f"Consider EC2 launch type for {service_name} with {current_count} tasks for cost savings"
            )
            # Recalculate cost for EC2
            ec2_cost = current_count * 0.025 * 24 * 30
            if ec2_cost < current_monthly_cost:
                analysis["optimized_monthly_cost"] = ec2_cost
        
        # Resource optimization recommendations
        if cpu_util < 0.30 and memory_util < 0.30:
            analysis["recommendations"].append(
                f"Consider reducing task definition resources for {service_name} - utilization very low"
            )
        elif cpu_util > 0.80 or memory_util > 0.80:
            analysis["recommendations"].append(
                f"Consider increasing task definition resources for {service_name} - utilization high"
            )
        
        return analysis
    
    def _generate_cluster_recommendations(self, cluster_data: Dict[str, Any]) -> List[str]:
        """Generate cluster-level optimization recommendations"""
        
        recommendations = []
        
        capacity_providers = cluster_data.get("capacity_providers", [])
        services_count = cluster_data.get("active_services", 0)
        tasks_count = cluster_data.get("tasks", 0)
        
        # Capacity provider recommendations
        if "FARGATE_SPOT" not in capacity_providers and tasks_count > 10:
            recommendations.append(
                "Enable Fargate Spot capacity provider for non-critical workloads to save up to 70% on costs"
            )
        
        if "EC2" in capacity_providers and len(capacity_providers) == 1:
            recommendations.append(
                "Add Fargate capacity provider for better flexibility and reduced management overhead"
            )
        
        # Auto Scaling recommendations
        recommendations.append("Enable ECS Service Auto Scaling for dynamic workload management")
        
        # Monitoring recommendations
        recommendations.append("Implement CloudWatch Container Insights for detailed monitoring")
        recommendations.append("Set up CloudWatch alarms for service health monitoring")
        
        # Security recommendations
        if not cluster_data.get("vpc_configuration"):
            recommendations.append("Configure VPC networking for improved security")
        
        recommendations.append("Enable AWS Config rules for ECS compliance monitoring")
        
        return recommendations
    
    def predict_scaling_needs(self, service_name: str, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict future scaling needs based on historical metrics
        """
        
        if not metrics_history:
            return {"prediction": "insufficient_data", "confidence": 0.0}
        
        # Analyze patterns (simplified implementation)
        cpu_values = [m.get("cpu_utilization", 0) for m in metrics_history]
        memory_values = [m.get("memory_utilization", 0) for m in metrics_history]
        request_counts = [m.get("request_count", 0) for m in metrics_history]
        
        avg_cpu = sum(cpu_values) / len(cpu_values)
        avg_memory = sum(memory_values) / len(memory_values)
        avg_requests = sum(request_counts) / len(request_counts) if request_counts else 0
        
        # Trend analysis
        if len(cpu_values) >= 3:
            recent_cpu = sum(cpu_values[-3:]) / 3
            earlier_cpu = sum(cpu_values[:3]) / 3
            cpu_trend = "increasing" if recent_cpu > earlier_cpu * 1.1 else "stable"
        else:
            cpu_trend = "stable"
        
        prediction = {
            "service_name": service_name,
            "current_metrics": {
                "avg_cpu_utilization": avg_cpu,
                "avg_memory_utilization": avg_memory,
                "avg_request_count": avg_requests
            },
            "trend_analysis": {
                "cpu_trend": cpu_trend,
                "predicted_peak_time": self._predict_peak_time(metrics_history)
            },
            "scaling_prediction": self._generate_scaling_prediction(avg_cpu, avg_memory, cpu_trend),
            "confidence_score": min(len(metrics_history) / 24.0, 1.0)  # Higher confidence with more data
        }
        
        return prediction
    
    def _predict_peak_time(self, metrics_history: List[Dict[str, Any]]) -> Optional[str]:
        """Predict when peak usage typically occurs"""
        
        if len(metrics_history) < 24:
            return None
        
        # Group by hour of day and find peak
        hourly_usage = {}
        for metric in metrics_history:
            timestamp = metric.get("timestamp")
            if timestamp:
                try:
                    hour = datetime.fromisoformat(timestamp).hour
                    cpu = metric.get("cpu_utilization", 0)
                    if hour not in hourly_usage:
                        hourly_usage[hour] = []
                    hourly_usage[hour].append(cpu)
                except:
                    continue
        
        if not hourly_usage:
            return None
        
        # Find hour with highest average CPU
        peak_hour = max(hourly_usage.keys(), 
                       key=lambda h: sum(hourly_usage[h]) / len(hourly_usage[h]))
        
        return f"{peak_hour:02d}:00"
    
    def _generate_scaling_prediction(self, avg_cpu: float, avg_memory: float, trend: str) -> Dict[str, Any]:
        """Generate scaling prediction based on current metrics and trends"""
        
        if trend == "increasing" and (avg_cpu > 0.60 or avg_memory > 0.70):
            return {
                "action": "scale_up",
                "confidence": "high",
                "recommendation": "Proactive scaling recommended within next 2-4 hours",
                "suggested_increase": "25-50%"
            }
        elif avg_cpu < 0.25 and avg_memory < 0.30:
            return {
                "action": "scale_down",
                "confidence": "medium", 
                "recommendation": "Consider scaling down during low-usage periods",
                "suggested_decrease": "20-30%"
            }
        else:
            return {
                "action": "maintain",
                "confidence": "medium",
                "recommendation": "Current scaling appears optimal",
                "suggested_change": "none"
            }
    
    def generate_task_definition_optimization(self, task_def_arn: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate optimized task definition based on performance data
        """
        
        optimization = {
            "task_definition_arn": task_def_arn,
            "current_resources": performance_data.get("allocated_resources", {}),
            "actual_usage": performance_data.get("actual_usage", {}),
            "optimized_resources": {},
            "cost_impact": {},
            "recommendations": []
        }
        
        current_cpu = performance_data.get("allocated_resources", {}).get("cpu", 256)
        current_memory = performance_data.get("allocated_resources", {}).get("memory", 512)
        
        avg_cpu_usage = performance_data.get("actual_usage", {}).get("cpu_percent", 50)
        avg_memory_usage = performance_data.get("actual_usage", {}).get("memory_percent", 50)
        
        # CPU optimization
        if avg_cpu_usage < 30:
            optimized_cpu = max(256, int(current_cpu * 0.75))
            optimization["recommendations"].append("Reduce CPU allocation - current usage is low")
        elif avg_cpu_usage > 80:
            optimized_cpu = min(4096, int(current_cpu * 1.5))
            optimization["recommendations"].append("Increase CPU allocation - high utilization detected")
        else:
            optimized_cpu = current_cpu
        
        # Memory optimization
        if avg_memory_usage < 30:
            optimized_memory = max(512, int(current_memory * 0.75))
            optimization["recommendations"].append("Reduce memory allocation - current usage is low")
        elif avg_memory_usage > 80:
            optimized_memory = min(8192, int(current_memory * 1.5))
            optimization["recommendations"].append("Increase memory allocation - high utilization detected")
        else:
            optimized_memory = current_memory
        
        optimization["optimized_resources"] = {
            "cpu": optimized_cpu,
            "memory": optimized_memory
        }
        
        # Calculate cost impact
        current_cost = self._calculate_fargate_cost(current_cpu, current_memory)
        optimized_cost = self._calculate_fargate_cost(optimized_cpu, optimized_memory)
        
        optimization["cost_impact"] = {
            "current_hourly_cost": current_cost,
            "optimized_hourly_cost": optimized_cost,
            "hourly_savings": current_cost - optimized_cost,
            "monthly_savings": (current_cost - optimized_cost) * 24 * 30
        }
        
        return optimization
    
    def _calculate_fargate_cost(self, cpu: int, memory: int) -> float:
        """Calculate Fargate cost per hour"""
        
        # Fargate pricing (simplified)
        cpu_cost_per_vcpu_hour = 0.04048
        memory_cost_per_gb_hour = 0.004445
        
        vcpu = cpu / 1024.0  # Convert CPU units to vCPU
        gb_memory = memory / 1024.0  # Convert MB to GB
        
        return (vcpu * cpu_cost_per_vcpu_hour) + (gb_memory * memory_cost_per_gb_hour)
    
    def detect_service_mesh_opportunities(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect opportunities for service mesh implementation
        """
        
        services = cluster_data.get("services", {})
        service_count = len(services)
        
        mesh_analysis = {
            "cluster_name": cluster_data.get("cluster_name"),
            "service_count": service_count,
            "mesh_recommended": service_count >= 3,
            "complexity_score": self._calculate_complexity_score(services),
            "recommendations": [],
            "implementation_priority": "low"
        }
        
        if service_count >= 5:
            mesh_analysis["implementation_priority"] = "high"
            mesh_analysis["recommendations"].extend([
                "Implement AWS App Mesh for service-to-service communication",
                "Enable distributed tracing with AWS X-Ray",
                "Set up service discovery with AWS Cloud Map",
                "Implement circuit breaker patterns"
            ])
        elif service_count >= 3:
            mesh_analysis["implementation_priority"] = "medium"
            mesh_analysis["recommendations"].extend([
                "Consider AWS App Mesh for improved observability",
                "Implement service discovery with AWS Cloud Map"
            ])
        else:
            mesh_analysis["recommendations"].append(
                "Service mesh not recommended for current service count"
            )
        
        return mesh_analysis
    
    def _calculate_complexity_score(self, services: Dict[str, Any]) -> float:
        """Calculate service complexity score for mesh recommendation"""
        
        base_score = len(services) * 10
        
        # Add complexity for different launch types
        launch_types = set(s.get("launch_type", "FARGATE") for s in services.values())
        complexity_bonus = len(launch_types) * 5
        
        # Add complexity for load balancers
        lb_services = sum(1 for s in services.values() if s.get("load_balancer"))
        lb_bonus = lb_services * 3
        
        return min(100, base_score + complexity_bonus + lb_bonus)
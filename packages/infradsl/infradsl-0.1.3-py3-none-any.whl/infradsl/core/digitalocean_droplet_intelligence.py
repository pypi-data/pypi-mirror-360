"""
DigitalOcean Droplet Intelligence

Advanced intelligence for DigitalOcean Droplets
providing intelligent sizing, cost optimization, and scaling recommendations.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from .digitalocean_intelligence_base import DigitalOceanIntelligenceBase
from .stateless_intelligence import (
    ResourceType, ResourceFingerprint, ChangeImpactAnalysis, 
    ResourceHealth, HealthStatus
)


class DigitalOceanDropletIntelligence(DigitalOceanIntelligenceBase):
    """
    DigitalOcean Droplet Intelligence Engine
    
    Provides intelligent droplet management including:
    - Smart droplet sizing and optimization
    - Cost analysis and savings recommendations
    - Security configuration optimization
    - Performance monitoring and tuning
    - Auto-scaling recommendations
    - Backup and disaster recovery planning
    """
    
    def __init__(self):
        super().__init__(ResourceType.COMPUTE)
        
        # Droplet-specific optimization rules
        self.droplet_rules = {
            "sizing_thresholds": {
                "cpu_upgrade_threshold": 0.85,
                "memory_upgrade_threshold": 0.90,
                "cpu_downgrade_threshold": 0.15,
                "memory_downgrade_threshold": 0.20
            },
            "performance_metrics": {
                "response_time_warning": 2.0,
                "disk_io_warning": 0.80,
                "network_utilization_warning": 0.75
            },
            "droplet_types": {
                "basic": ["s-1vcpu-1gb", "s-1vcpu-2gb"],
                "general_purpose": ["s-2vcpu-2gb", "s-2vcpu-4gb", "s-4vcpu-8gb"],
                "cpu_optimized": ["c-2", "c-4", "c-8"],
                "memory_optimized": ["m-2vcpu-16gb", "m-4vcpu-32gb"],
                "storage_optimized": ["so1_5-2vcpu-16gb", "so1_5-4vcpu-32gb"]
            }
        }
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing DigitalOcean droplets"""
        
        # Mock implementation - in production would use DigitalOcean API
        return {
            "web-server-1": {
                "id": 123456,
                "name": "web-server-1",
                "status": "active",
                "size_slug": "s-2vcpu-4gb",
                "vcpus": 2,
                "memory": 4096,
                "disk": 80,
                "region": "nyc3",
                "image": "ubuntu-22-04-x64",
                "created_at": "2024-01-15T10:30:00Z",
                "features": ["private_networking", "monitoring"],
                "backup_enabled": True,
                "ipv6": False,
                "private_networking": True,
                "monitoring": True,
                "ssh_keys": [
                    {"id": 789, "name": "work-key", "fingerprint": "aa:bb:cc:dd:ee:ff"}
                ],
                "firewalls": [
                    {"id": 101, "name": "web-firewall"}
                ],
                "volumes": [
                    {
                        "id": "vol-001",
                        "name": "web-data",
                        "size_gigabytes": 100,
                        "type": "ext4",
                        "utilization_percentage": 0.65
                    }
                ],
                "load_balancer_id": "lb-001",
                "tags": ["production", "web"],
                "metrics": {
                    "cpu_utilization": 0.55,
                    "memory_utilization": 0.70,
                    "disk_utilization": 0.45,
                    "network_utilization": 0.30,
                    "response_time": 0.150,
                    "error_rate": 0.02,
                    "uptime": 0.999
                },
                "monthly_cost_estimate": 48.00
            },
            "api-server-1": {
                "id": 123457,
                "name": "api-server-1",
                "status": "active",
                "size_slug": "c-2",
                "vcpus": 2,
                "memory": 4096,
                "disk": 50,
                "region": "nyc3",
                "image": "ubuntu-22-04-x64",
                "created_at": "2024-02-01T10:30:00Z",
                "features": ["private_networking", "monitoring"],
                "backup_enabled": False,
                "ipv6": True,
                "private_networking": True,
                "monitoring": True,
                "ssh_keys": [
                    {"id": 789, "name": "work-key", "fingerprint": "aa:bb:cc:dd:ee:ff"}
                ],
                "firewalls": [
                    {"id": 102, "name": "api-firewall"}
                ],
                "volumes": [],
                "load_balancer_id": None,
                "tags": ["production", "api"],
                "metrics": {
                    "cpu_utilization": 0.85,
                    "memory_utilization": 0.60,
                    "disk_utilization": 0.80,
                    "network_utilization": 0.40,
                    "response_time": 0.080,
                    "error_rate": 0.01,
                    "uptime": 0.995
                },
                "monthly_cost_estimate": 60.00
            },
            "dev-server-1": {
                "id": 123458,
                "name": "dev-server-1",
                "status": "active",
                "size_slug": "s-1vcpu-1gb",
                "vcpus": 1,
                "memory": 1024,
                "disk": 25,
                "region": "sfo3",
                "image": "ubuntu-22-04-x64",
                "created_at": "2024-03-01T10:30:00Z",
                "features": [],
                "backup_enabled": False,
                "ipv6": False,
                "private_networking": False,
                "monitoring": False,
                "ssh_keys": [],
                "firewalls": [],
                "volumes": [],
                "load_balancer_id": None,
                "tags": ["development"],
                "metrics": {
                    "cpu_utilization": 0.15,
                    "memory_utilization": 0.25,
                    "disk_utilization": 0.30,
                    "network_utilization": 0.10,
                    "response_time": 0.300,
                    "error_rate": 0.05,
                    "uptime": 0.990
                },
                "monthly_cost_estimate": 6.00
            }
        }
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract droplet configuration from cloud state"""
        
        return {
            "name": cloud_state.get("name"),
            "size_slug": cloud_state.get("size_slug"),
            "vcpus": cloud_state.get("vcpus"),
            "memory": cloud_state.get("memory"),
            "disk": cloud_state.get("disk"),
            "region": cloud_state.get("region"),
            "image": cloud_state.get("image"),
            "features": cloud_state.get("features", []),
            "backup_enabled": cloud_state.get("backup_enabled", False),
            "private_networking": cloud_state.get("private_networking", False),
            "monitoring": cloud_state.get("monitoring", False),
            "ssh_keys": cloud_state.get("ssh_keys", []),
            "firewalls": cloud_state.get("firewalls", []),
            "volumes": cloud_state.get("volumes", []),
            "tags": cloud_state.get("tags", []),
            "metrics": cloud_state.get("metrics", {})
        }
    
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """Generate hash for droplet configuration"""
        
        # Focus on key configuration elements
        key_config = {
            "name": config.get("name"),
            "size_slug": config.get("size_slug"),
            "region": config.get("region"),
            "image": config.get("image"),
            "features": sorted(config.get("features", [])),
            "backup_enabled": config.get("backup_enabled"),
            "private_networking": config.get("private_networking"),
            "monitoring": config.get("monitoring"),
            "ssh_keys": len(config.get("ssh_keys", [])),
            "firewalls": len(config.get("firewalls", [])),
            "volumes": len(config.get("volumes", []))
        }
        
        return str(hash(json.dumps(key_config, sort_keys=True)))
    
    def analyze_droplet_optimization(self, droplet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze droplet for optimization opportunities
        """
        
        optimization_analysis = {
            "droplet_name": droplet_data.get("name"),
            "current_size": droplet_data.get("size_slug"),
            "current_cost_estimate": 0.0,
            "optimized_cost_estimate": 0.0,
            "potential_savings": 0.0,
            "recommendations": [],
            "sizing_recommendations": [],
            "security_recommendations": [],
            "performance_recommendations": []
        }
        
        # Cost and sizing analysis
        cost_analysis = self.analyze_do_cost_optimization(droplet_data)
        optimization_analysis.update(cost_analysis)
        
        # Sizing recommendations
        sizing_analysis = self._analyze_droplet_sizing(droplet_data)
        optimization_analysis["sizing_recommendations"] = sizing_analysis
        
        # Security analysis
        security_analysis = self.analyze_do_security_posture(droplet_data)
        optimization_analysis["security_recommendations"] = security_analysis["recommendations"]
        
        # Performance analysis
        performance_analysis = self.analyze_do_performance_optimization(droplet_data)
        optimization_analysis["performance_recommendations"] = performance_analysis["recommendations"]
        
        # General recommendations
        general_recommendations = self._generate_general_recommendations(droplet_data)
        optimization_analysis["recommendations"].extend(general_recommendations)
        
        return optimization_analysis
    
    def _analyze_droplet_sizing(self, droplet_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze droplet sizing and provide recommendations"""
        
        recommendations = []
        metrics = droplet_data.get("metrics", {})
        current_size = droplet_data.get("size_slug", "")
        
        cpu_utilization = metrics.get("cpu_utilization", 0.5)
        memory_utilization = metrics.get("memory_utilization", 0.5)
        
        # CPU sizing analysis
        if cpu_utilization > self.droplet_rules["sizing_thresholds"]["cpu_upgrade_threshold"]:
            recommendations.append({
                "type": "upgrade",
                "resource": "CPU",
                "reason": f"High CPU utilization ({cpu_utilization:.1%})",
                "suggested_action": "Upgrade to CPU-optimized droplet or larger size",
                "urgency": "high"
            })
        elif cpu_utilization < self.droplet_rules["sizing_thresholds"]["cpu_downgrade_threshold"]:
            recommendations.append({
                "type": "downgrade",
                "resource": "CPU",
                "reason": f"Low CPU utilization ({cpu_utilization:.1%})",
                "suggested_action": "Consider smaller droplet size",
                "urgency": "low"
            })
        
        # Memory sizing analysis
        if memory_utilization > self.droplet_rules["sizing_thresholds"]["memory_upgrade_threshold"]:
            recommendations.append({
                "type": "upgrade",
                "resource": "Memory",
                "reason": f"High memory utilization ({memory_utilization:.1%})",
                "suggested_action": "Upgrade to memory-optimized droplet or larger size",
                "urgency": "high"
            })
        elif memory_utilization < self.droplet_rules["sizing_thresholds"]["memory_downgrade_threshold"]:
            recommendations.append({
                "type": "downgrade",
                "resource": "Memory",
                "reason": f"Low memory utilization ({memory_utilization:.1%})",
                "suggested_action": "Consider smaller droplet size",
                "urgency": "low"
            })
        
        # Droplet type recommendations
        type_recommendation = self._recommend_droplet_type(droplet_data)
        if type_recommendation:
            recommendations.append(type_recommendation)
        
        return recommendations
    
    def _recommend_droplet_type(self, droplet_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recommend optimal droplet type based on usage patterns"""
        
        metrics = droplet_data.get("metrics", {})
        current_size = droplet_data.get("size_slug", "")
        
        cpu_utilization = metrics.get("cpu_utilization", 0.5)
        memory_utilization = metrics.get("memory_utilization", 0.5)
        disk_utilization = metrics.get("disk_utilization", 0.5)
        network_utilization = metrics.get("network_utilization", 0.3)
        
        # Determine workload characteristics
        if cpu_utilization > 0.70 and memory_utilization < 0.50:
            # CPU-intensive workload
            if current_size not in self.droplet_rules["droplet_types"]["cpu_optimized"]:
                return {
                    "type": "optimization",
                    "resource": "Droplet Type",
                    "reason": "CPU-intensive workload detected",
                    "suggested_action": "Consider CPU-optimized droplet",
                    "urgency": "medium"
                }
        
        elif memory_utilization > 0.80 and cpu_utilization < 0.50:
            # Memory-intensive workload
            if current_size not in self.droplet_rules["droplet_types"]["memory_optimized"]:
                return {
                    "type": "optimization",
                    "resource": "Droplet Type",
                    "reason": "Memory-intensive workload detected",
                    "suggested_action": "Consider memory-optimized droplet",
                    "urgency": "medium"
                }
        
        elif disk_utilization > 0.80:
            # Storage-intensive workload
            if current_size not in self.droplet_rules["droplet_types"]["storage_optimized"]:
                return {
                    "type": "optimization",
                    "resource": "Droplet Type",
                    "reason": "Storage-intensive workload detected",
                    "suggested_action": "Consider storage-optimized droplet",
                    "urgency": "medium"
                }
        
        return None
    
    def _generate_general_recommendations(self, droplet_data: Dict[str, Any]) -> List[str]:
        """Generate general droplet recommendations"""
        
        recommendations = []
        
        # Region optimization
        region = droplet_data.get("region", "")
        tags = droplet_data.get("tags", [])
        
        if "production" in tags and region in ["sfo3", "sgp1"]:
            recommendations.append("Consider deploying production workloads in multiple regions for better availability")
        
        # IPv6 recommendations
        if not droplet_data.get("ipv6", False):
            recommendations.append("Enable IPv6 for better connectivity and future-proofing")
        
        # Tag management
        if not tags:
            recommendations.append("Add tags for better resource organization and cost tracking")
        
        # Volume optimization
        volumes = droplet_data.get("volumes", [])
        if not volumes and droplet_data.get("disk", 0) > 50:
            recommendations.append("Consider using block storage volumes for better flexibility")
        
        return recommendations
    
    def predict_droplet_scaling_needs(self, droplet_name: str, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict droplet scaling needs based on historical metrics
        """
        
        scaling_prediction = self.generate_do_scaling_recommendations(
            {"name": droplet_name}, metrics_history
        )
        
        if scaling_prediction.get("recommendation") == "insufficient_data":
            return scaling_prediction
        
        # Enhanced prediction with droplet-specific insights
        recommendation = scaling_prediction["recommendation"]
        
        # Add droplet-specific scaling recommendations
        if recommendation["action"] == "scale_up":
            scaling_prediction["scaling_options"] = self._get_scaling_options(droplet_name, "up")
        elif recommendation["action"] == "scale_down":
            scaling_prediction["scaling_options"] = self._get_scaling_options(droplet_name, "down")
        
        return scaling_prediction
    
    def _get_scaling_options(self, droplet_name: str, direction: str) -> List[Dict[str, Any]]:
        """Get available scaling options for a droplet"""
        
        # In a real implementation, this would query the current droplet size
        # and provide next tier options
        if direction == "up":
            return [
                {
                    "size_slug": "s-4vcpu-8gb",
                    "vcpus": 4,
                    "memory": 8192,
                    "estimated_cost_increase": 24.00,
                    "performance_improvement": "2x CPU, 2x Memory"
                },
                {
                    "size_slug": "c-4",
                    "vcpus": 4,
                    "memory": 8192,
                    "estimated_cost_increase": 60.00,
                    "performance_improvement": "2x CPU (optimized), 2x Memory"
                }
            ]
        else:  # scale down
            return [
                {
                    "size_slug": "s-1vcpu-2gb",
                    "vcpus": 1,
                    "memory": 2048,
                    "estimated_cost_savings": 18.00,
                    "performance_impact": "50% CPU, 50% Memory"
                }
            ]
    
    def generate_disaster_recovery_plan(self, droplet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate disaster recovery recommendations for droplet
        """
        
        dr_plan = {
            "backup_strategy": {},
            "replication_recommendations": [],
            "recovery_time_estimate": "",
            "estimated_costs": {}
        }
        
        # Backup strategy analysis
        backup_enabled = droplet_data.get("backup_enabled", False)
        
        if backup_enabled:
            dr_plan["backup_strategy"] = {
                "current_strategy": "DigitalOcean Automated Backups",
                "frequency": "Weekly",
                "retention": "4 weeks",
                "estimated_rto": "1-2 hours",
                "estimated_rpo": "24 hours"
            }
        else:
            dr_plan["backup_strategy"] = {
                "recommendation": "Enable automated backups",
                "estimated_cost": f"{droplet_data.get('monthly_cost_estimate', 0) * 0.20:.2f} per month",
                "estimated_rto": "1-2 hours",
                "estimated_rpo": "24 hours"
            }
        
        # Replication recommendations
        region = droplet_data.get("region", "")
        tags = droplet_data.get("tags", [])
        
        if "production" in tags:
            dr_plan["replication_recommendations"] = [
                "Consider setting up a standby droplet in a different region",
                "Implement database replication if applicable",
                "Use load balancers for automatic failover",
                "Consider using floating IPs for quick DNS updates"
            ]
        
        # Recovery time estimates
        if backup_enabled:
            dr_plan["recovery_time_estimate"] = "1-2 hours (from backup)"
        else:
            dr_plan["recovery_time_estimate"] = "4-8 hours (manual reconstruction)"
        
        return dr_plan
    
    def analyze_droplet_network_performance(self, droplet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze network performance and optimization opportunities
        """
        
        network_analysis = {
            "performance_score": 0.0,
            "bottlenecks": [],
            "recommendations": []
        }
        
        metrics = droplet_data.get("metrics", {})
        network_utilization = metrics.get("network_utilization", 0.3)
        response_time = metrics.get("response_time", 0.1)
        
        # Network performance scoring
        performance_score = 100.0
        
        if network_utilization > 0.80:
            network_analysis["bottlenecks"].append("High network utilization")
            network_analysis["recommendations"].append("Consider upgrading to higher bandwidth droplet")
            performance_score -= 20
        
        if response_time > self.droplet_rules["performance_metrics"]["response_time_warning"]:
            network_analysis["bottlenecks"].append("High response time")
            network_analysis["recommendations"].append("Investigate network latency and optimize application")
            performance_score -= 15
        
        # Private networking analysis
        private_networking = droplet_data.get("private_networking", False)
        if not private_networking:
            network_analysis["recommendations"].append("Enable private networking for better performance and security")
            performance_score -= 10
        
        # Load balancer analysis
        load_balancer_id = droplet_data.get("load_balancer_id")
        if not load_balancer_id and "production" in droplet_data.get("tags", []):
            network_analysis["recommendations"].append("Consider using a load balancer for production workloads")
            performance_score -= 5
        
        network_analysis["performance_score"] = max(0.0, performance_score)
        
        return network_analysis
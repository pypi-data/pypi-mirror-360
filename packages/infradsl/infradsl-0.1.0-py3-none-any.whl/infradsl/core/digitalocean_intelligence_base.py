"""
DigitalOcean Intelligence Base

Base class for all DigitalOcean-specific intelligence implementations.
Provides foundational intelligence capabilities for DigitalOcean resources.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

from .stateless_intelligence import (
    StatelessIntelligence, ResourceType, ResourceFingerprint, 
    ChangeImpactAnalysis, ResourceHealth, HealthStatus
)


class DigitalOceanIntelligenceBase(StatelessIntelligence):
    """
    Base class for DigitalOcean Intelligence implementations
    
    Provides common functionality for DigitalOcean services including:
    - Resource discovery and fingerprinting
    - Cost optimization analysis
    - Security best practices
    - Performance optimization
    - Auto-scaling recommendations
    """
    
    def __init__(self, resource_type: ResourceType):
        super().__init__(resource_type)
        
        # DigitalOcean-specific optimization rules
        self.do_optimization_rules = {
            "cost_thresholds": {
                "underutilized_cpu": 0.20,     # 20% CPU utilization
                "underutilized_memory": 0.30,  # 30% memory utilization
                "high_utilization": 0.85,      # 85% utilization threshold
            },
            "security_requirements": {
                "firewall_required": True,
                "monitoring_required": True,
                "backup_required": True,
                "private_networking_recommended": True
            },
            "performance_thresholds": {
                "response_time_warning": 2.0,  # 2 seconds
                "error_rate_warning": 0.05,    # 5%
                "disk_usage_warning": 0.80     # 80% disk usage
            },
            "pricing": {
                "droplet_hourly_rates": {
                    "s-1vcpu-1gb": 0.007,     # Basic droplet
                    "s-1vcpu-2gb": 0.015,     # Standard droplet
                    "s-2vcpu-2gb": 0.022,     # CPU-optimized
                    "s-2vcpu-4gb": 0.030,     # General purpose
                    "s-4vcpu-8gb": 0.060,     # High memory
                    "c-2": 0.060,             # CPU-optimized
                    "g-2vcpu-8gb": 0.119      # General purpose
                },
                "storage_gb_monthly": 0.10,    # Block storage per GB
                "bandwidth_gb": 0.01,          # Bandwidth overage per GB
                "load_balancer_monthly": 12.00, # Load balancer
                "database_hourly_base": 0.060   # Managed database base
            }
        }
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover existing DigitalOcean resources
        Override in specific intelligence classes
        """
        raise NotImplementedError("Subclasses must implement _discover_existing_resources")
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract resource configuration from DigitalOcean API response
        Override in specific intelligence classes
        """
        raise NotImplementedError("Subclasses must implement _extract_resource_config")
    
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """
        Calculate configuration hash for drift detection
        Override in specific intelligence classes
        """
        raise NotImplementedError("Subclasses must implement _calculate_config_hash")
    
    # ==========================================
    # DIGITALOCEAN-SPECIFIC INTELLIGENCE
    # ==========================================
    
    def analyze_do_cost_optimization(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost optimization opportunities for DigitalOcean resources"""
        
        analysis = {
            "current_monthly_cost": 0.0,
            "optimized_monthly_cost": 0.0,
            "potential_savings": 0.0,
            "recommendations": [],
            "cost_breakdown": {}
        }
        
        # Analyze resource utilization
        utilization_analysis = self._analyze_resource_utilization(resource_data)
        analysis.update(utilization_analysis)
        
        # Storage optimization
        storage_analysis = self._analyze_storage_optimization(resource_data)
        analysis["recommendations"].extend(storage_analysis)
        
        # Network optimization
        network_analysis = self._analyze_network_optimization(resource_data)
        analysis["recommendations"].extend(network_analysis)
        
        return analysis
    
    def _analyze_resource_utilization(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resource utilization for cost optimization"""
        
        metrics = resource_data.get("metrics", {})
        size_slug = resource_data.get("size_slug", "")
        
        cpu_utilization = metrics.get("cpu_utilization", 0.5)
        memory_utilization = metrics.get("memory_utilization", 0.5)
        
        # Calculate current cost
        hourly_rate = self.do_optimization_rules["pricing"]["droplet_hourly_rates"].get(size_slug, 0.030)
        current_monthly_cost = hourly_rate * 24 * 30
        
        recommendations = []
        optimized_cost = current_monthly_cost
        
        # Underutilization analysis
        if (cpu_utilization < self.do_optimization_rules["cost_thresholds"]["underutilized_cpu"] and 
            memory_utilization < self.do_optimization_rules["cost_thresholds"]["underutilized_memory"]):
            
            recommendations.append("Resource is underutilized - consider downsizing")
            
            # Suggest smaller droplet size
            if "4vcpu" in size_slug:
                optimized_cost = current_monthly_cost * 0.5  # Estimate 50% savings
            elif "2vcpu" in size_slug:
                optimized_cost = current_monthly_cost * 0.7  # Estimate 30% savings
        
        # High utilization analysis
        elif (cpu_utilization > self.do_optimization_rules["cost_thresholds"]["high_utilization"] or 
              memory_utilization > self.do_optimization_rules["cost_thresholds"]["high_utilization"]):
            
            recommendations.append("High resource utilization detected - consider upgrading")
        
        return {
            "current_monthly_cost": current_monthly_cost,
            "optimized_monthly_cost": optimized_cost,
            "potential_savings": current_monthly_cost - optimized_cost,
            "utilization_analysis": {
                "cpu_utilization": cpu_utilization,
                "memory_utilization": memory_utilization
            },
            "recommendations": recommendations
        }
    
    def _analyze_storage_optimization(self, resource_data: Dict[str, Any]) -> List[str]:
        """Analyze storage optimization opportunities"""
        
        recommendations = []
        volumes = resource_data.get("volumes", [])
        
        for volume in volumes:
            size_gb = volume.get("size_gigabytes", 0)
            utilization = volume.get("utilization_percentage", 0.5)
            
            if utilization < 0.3:  # Less than 30% used
                recommendations.append(f"Volume {volume.get('name')} is underutilized - consider resizing")
            elif utilization > 0.9:  # More than 90% used
                recommendations.append(f"Volume {volume.get('name')} is near capacity - consider expanding")
        
        # Backup recommendations
        has_backups = resource_data.get("backup_enabled", False)
        if not has_backups:
            recommendations.append("Enable automated backups for data protection")
        
        return recommendations
    
    def _analyze_network_optimization(self, resource_data: Dict[str, Any]) -> List[str]:
        """Analyze network optimization opportunities"""
        
        recommendations = []
        
        # Private networking
        private_networking = resource_data.get("private_networking", False)
        if not private_networking:
            recommendations.append("Enable private networking for better security and performance")
        
        # Firewall configuration
        firewalls = resource_data.get("firewalls", [])
        if not firewalls:
            recommendations.append("Configure Cloud Firewall for enhanced security")
        
        # Load balancer usage
        has_load_balancer = resource_data.get("load_balancer_id") is not None
        instance_count = len(resource_data.get("related_droplets", []))
        
        if instance_count > 1 and not has_load_balancer:
            recommendations.append("Consider Load Balancer for distributing traffic across multiple droplets")
        
        return recommendations
    
    def analyze_do_security_posture(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security posture for DigitalOcean resources"""
        
        security_analysis = {
            "security_score": 0.0,
            "vulnerabilities": [],
            "recommendations": [],
            "compliance_status": {}
        }
        
        # Security configuration checks
        security_checks = self._perform_security_checks(resource_data)
        security_analysis.update(security_checks)
        
        # Compliance analysis
        compliance_analysis = self._analyze_compliance_requirements(resource_data)
        security_analysis["compliance_status"] = compliance_analysis
        
        return security_analysis
    
    def _perform_security_checks(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform security configuration checks"""
        
        vulnerabilities = []
        recommendations = []
        security_score = 100.0
        
        # Firewall check
        firewalls = resource_data.get("firewalls", [])
        if not firewalls:
            vulnerabilities.append("No firewall configured")
            recommendations.append("Configure Cloud Firewall with appropriate rules")
            security_score -= 20
        
        # SSH key authentication
        ssh_keys = resource_data.get("ssh_keys", [])
        if not ssh_keys:
            vulnerabilities.append("No SSH keys configured")
            recommendations.append("Use SSH key authentication instead of passwords")
            security_score -= 15
        
        # Monitoring
        monitoring_enabled = resource_data.get("monitoring", False)
        if not monitoring_enabled:
            vulnerabilities.append("Monitoring not enabled")
            recommendations.append("Enable monitoring for security visibility")
            security_score -= 10
        
        # Backup configuration
        backup_enabled = resource_data.get("backup_enabled", False)
        if not backup_enabled:
            vulnerabilities.append("Backups not enabled")
            recommendations.append("Enable automated backups for data protection")
            security_score -= 10
        
        # Private networking
        private_networking = resource_data.get("private_networking", False)
        if not private_networking:
            vulnerabilities.append("Private networking not enabled")
            recommendations.append("Enable private networking for internal communication")
            security_score -= 10
        
        return {
            "security_score": max(0.0, security_score),
            "vulnerabilities": vulnerabilities,
            "recommendations": recommendations
        }
    
    def _analyze_compliance_requirements(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze compliance with common frameworks"""
        
        compliance_status = {
            "SOC2": self._check_soc2_compliance(resource_data),
            "GDPR": self._check_gdpr_compliance(resource_data),
            "HIPAA": self._check_hipaa_compliance(resource_data)
        }
        
        return compliance_status
    
    def _check_soc2_compliance(self, resource_data: Dict[str, Any]) -> Dict[str, bool]:
        """Check SOC 2 compliance requirements"""
        
        return {
            "access_control": len(resource_data.get("ssh_keys", [])) > 0,
            "monitoring": resource_data.get("monitoring", False),
            "backup": resource_data.get("backup_enabled", False),
            "encryption": True,  # DigitalOcean encrypts data at rest by default
            "network_security": len(resource_data.get("firewalls", [])) > 0
        }
    
    def _check_gdpr_compliance(self, resource_data: Dict[str, Any]) -> Dict[str, bool]:
        """Check GDPR compliance requirements"""
        
        return {
            "data_encryption": True,  # Default encryption
            "access_controls": len(resource_data.get("ssh_keys", [])) > 0,
            "monitoring_logging": resource_data.get("monitoring", False),
            "backup_retention": resource_data.get("backup_enabled", False)
        }
    
    def _check_hipaa_compliance(self, resource_data: Dict[str, Any]) -> Dict[str, bool]:
        """Check HIPAA compliance requirements"""
        
        return {
            "encryption_at_rest": True,  # Default encryption
            "encryption_in_transit": resource_data.get("private_networking", False),
            "access_controls": len(resource_data.get("ssh_keys", [])) > 0,
            "audit_logging": resource_data.get("monitoring", False),
            "backup_procedures": resource_data.get("backup_enabled", False)
        }
    
    def generate_do_scaling_recommendations(self, resource_data: Dict[str, Any], 
                                          metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate scaling recommendations based on historical metrics"""
        
        if not metrics_history:
            return {"recommendation": "insufficient_data"}
        
        # Analyze utilization trends
        cpu_values = [m.get("cpu_utilization", 0) for m in metrics_history]
        memory_values = [m.get("memory_utilization", 0) for m in metrics_history]
        
        avg_cpu = sum(cpu_values) / len(cpu_values)
        avg_memory = sum(memory_values) / len(memory_values)
        peak_cpu = max(cpu_values) if cpu_values else 0
        peak_memory = max(memory_values) if memory_values else 0
        
        # Trend analysis
        if len(cpu_values) >= 7:
            recent_cpu = sum(cpu_values[-7:]) / 7
            earlier_cpu = sum(cpu_values[:7]) / 7
            cpu_trend = "increasing" if recent_cpu > earlier_cpu * 1.1 else "stable"
        else:
            cpu_trend = "stable"
        
        scaling_recommendation = {
            "current_metrics": {
                "avg_cpu": avg_cpu,
                "avg_memory": avg_memory,
                "peak_cpu": peak_cpu,
                "peak_memory": peak_memory
            },
            "trend": cpu_trend,
            "recommendation": self._generate_scaling_action(avg_cpu, avg_memory, peak_cpu, cpu_trend),
            "confidence": min(len(metrics_history) / 24.0, 1.0)  # 24 hours = 100% confidence
        }
        
        return scaling_recommendation
    
    def _generate_scaling_action(self, avg_cpu: float, avg_memory: float, 
                               peak_cpu: float, trend: str) -> Dict[str, Any]:
        """Generate specific scaling action recommendation"""
        
        if trend == "increasing" and peak_cpu > 0.80:
            return {
                "action": "scale_up",
                "reason": "Increasing utilization trend with high peaks",
                "urgency": "high",
                "suggested_size": "next_tier_up"
            }
        elif avg_cpu > 0.85 or avg_memory > 0.85:
            return {
                "action": "scale_up",
                "reason": "High average utilization",
                "urgency": "medium",
                "suggested_size": "next_tier_up"
            }
        elif avg_cpu < 0.20 and avg_memory < 0.30 and peak_cpu < 0.50:
            return {
                "action": "scale_down",
                "reason": "Consistently low utilization",
                "urgency": "low",
                "suggested_size": "next_tier_down"
            }
        else:
            return {
                "action": "maintain",
                "reason": "Utilization within optimal range",
                "urgency": "none",
                "suggested_size": "current"
            }
    
    def analyze_do_performance_optimization(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance optimization opportunities"""
        
        optimization_analysis = {
            "performance_score": 0.0,
            "bottlenecks": [],
            "recommendations": []
        }
        
        # Performance metrics analysis
        metrics = resource_data.get("metrics", {})
        
        # CPU performance
        cpu_utilization = metrics.get("cpu_utilization", 0.5)
        if cpu_utilization > 0.90:
            optimization_analysis["bottlenecks"].append("CPU bottleneck detected")
            optimization_analysis["recommendations"].append("Consider CPU-optimized droplet sizes")
        
        # Memory performance
        memory_utilization = metrics.get("memory_utilization", 0.5)
        if memory_utilization > 0.90:
            optimization_analysis["bottlenecks"].append("Memory bottleneck detected")
            optimization_analysis["recommendations"].append("Consider memory-optimized droplet sizes")
        
        # Disk performance
        disk_utilization = metrics.get("disk_utilization", 0.5)
        if disk_utilization > self.do_optimization_rules["performance_thresholds"]["disk_usage_warning"]:
            optimization_analysis["bottlenecks"].append("Disk space constraint")
            optimization_analysis["recommendations"].append("Expand disk storage or optimize usage")
        
        # Network performance
        network_utilization = metrics.get("network_utilization", 0.3)
        if network_utilization > 0.80:
            optimization_analysis["bottlenecks"].append("Network bandwidth constraint")
            optimization_analysis["recommendations"].append("Consider upgrading to higher bandwidth droplet")
        
        # Calculate performance score
        performance_score = 100.0
        performance_score -= len(optimization_analysis["bottlenecks"]) * 15
        optimization_analysis["performance_score"] = max(0.0, performance_score)
        
        # General performance recommendations
        optimization_analysis["recommendations"].extend([
            "Monitor resource utilization trends",
            "Implement caching where appropriate",
            "Optimize application code for efficiency",
            "Consider SSD storage for better I/O performance"
        ])
        
        return optimization_analysis
    
    def get_do_pricing_estimate(self, resource_config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate pricing estimate for DigitalOcean resources"""
        
        pricing_estimate = {
            "monthly_cost": 0.0,
            "cost_breakdown": {},
            "cost_factors": []
        }
        
        # Droplet cost
        size_slug = resource_config.get("size_slug", "s-1vcpu-1gb")
        hourly_rate = self.do_optimization_rules["pricing"]["droplet_hourly_rates"].get(size_slug, 0.030)
        monthly_droplet_cost = hourly_rate * 24 * 30
        
        pricing_estimate["cost_breakdown"]["droplet"] = monthly_droplet_cost
        pricing_estimate["monthly_cost"] += monthly_droplet_cost
        
        # Storage cost
        volumes = resource_config.get("volumes", [])
        storage_cost = 0.0
        for volume in volumes:
            size_gb = volume.get("size_gigabytes", 0)
            storage_cost += size_gb * self.do_optimization_rules["pricing"]["storage_gb_monthly"]
        
        pricing_estimate["cost_breakdown"]["storage"] = storage_cost
        pricing_estimate["monthly_cost"] += storage_cost
        
        # Load balancer cost
        if resource_config.get("load_balancer_enabled", False):
            lb_cost = self.do_optimization_rules["pricing"]["load_balancer_monthly"]
            pricing_estimate["cost_breakdown"]["load_balancer"] = lb_cost
            pricing_estimate["monthly_cost"] += lb_cost
        
        # Backup cost (20% of droplet cost)
        if resource_config.get("backup_enabled", False):
            backup_cost = monthly_droplet_cost * 0.20
            pricing_estimate["cost_breakdown"]["backups"] = backup_cost
            pricing_estimate["monthly_cost"] += backup_cost
        
        pricing_estimate["cost_factors"] = [
            f"Droplet size: {size_slug}",
            f"Storage volumes: {len(volumes)}",
            f"Backups enabled: {resource_config.get('backup_enabled', False)}",
            f"Load balancer: {resource_config.get('load_balancer_enabled', False)}"
        ]
        
        return pricing_estimate
"""
Unified Provider Intelligence Interface

Central orchestration layer that coordinates intelligence across all cloud providers.
Provides a unified interface for multi-cloud intelligence and optimization.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import json
from enum import Enum

# Import all provider intelligence classes
from .aws_intelligence_base import AWSIntelligenceBase
from .aws_ec2_intelligence import EC2Intelligence
from .aws_ecs_intelligence import AWSECSIntelligence
from .aws_load_balancer_intelligence import AWSLoadBalancerIntelligence
from .aws_vpc_intelligence import AWSVPCIntelligence

from .gcp_intelligence_base import GCPIntelligenceBase
from .gcp_gke_intelligence_refactored import GCPGKEIntelligence
from .gcp_load_balancer_intelligence import GCPLoadBalancerIntelligence

from .digitalocean_intelligence_base import DigitalOceanIntelligenceBase
from .digitalocean_droplet_intelligence import DigitalOceanDropletIntelligence

from .cloudflare_intelligence_base import CloudflareIntelligenceBase
from .cloudflare_dns_intelligence import CloudflareDNSIntelligence

from .stateless_intelligence import ResourceType


class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    GCP = "gcp"
    DIGITALOCEAN = "digitalocean"
    CLOUDFLARE = "cloudflare"


class ServiceType(Enum):
    """Supported service types"""
    COMPUTE = "compute"
    CONTAINER = "container"
    LOAD_BALANCER = "load_balancer"
    NETWORK = "network"
    DNS = "dns"
    DATABASE = "database"
    STORAGE = "storage"


class UnifiedProviderIntelligence:
    """
    Unified Provider Intelligence Engine
    
    Orchestrates intelligence across all cloud providers providing:
    - Cross-cloud resource optimization
    - Multi-provider cost analysis
    - Unified security posture assessment
    - Cross-cloud migration recommendations
    - Global infrastructure optimization
    - Provider-agnostic best practices
    """
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all provider intelligence engines"""
        
        # AWS Services
        self.providers[CloudProvider.AWS] = {
            ServiceType.COMPUTE: EC2Intelligence(),
            ServiceType.CONTAINER: AWSECSIntelligence(),
            ServiceType.LOAD_BALANCER: AWSLoadBalancerIntelligence(),
            ServiceType.NETWORK: AWSVPCIntelligence()
        }
        
        # GCP Services
        self.providers[CloudProvider.GCP] = {
            ServiceType.CONTAINER: GCPGKEIntelligence(),
            ServiceType.LOAD_BALANCER: GCPLoadBalancerIntelligence()
        }
        
        # DigitalOcean Services
        self.providers[CloudProvider.DIGITALOCEAN] = {
            ServiceType.COMPUTE: DigitalOceanDropletIntelligence()
        }
        
        # Cloudflare Services
        self.providers[CloudProvider.CLOUDFLARE] = {
            ServiceType.DNS: CloudflareDNSIntelligence()
        }
    
    # ==========================================
    # UNIFIED ANALYSIS METHODS
    # ==========================================
    
    def analyze_multi_cloud_optimization(self, infrastructure_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze optimization opportunities across all cloud providers
        """
        
        optimization_analysis = {
            "total_monthly_cost": 0.0,
            "optimized_monthly_cost": 0.0,
            "potential_savings": 0.0,
            "provider_analyses": {},
            "cross_cloud_recommendations": [],
            "migration_opportunities": [],
            "consolidation_opportunities": []
        }
        
        # Analyze each provider
        for provider_name, provider_data in infrastructure_data.items():
            try:
                provider_enum = CloudProvider(provider_name.lower())
                provider_analysis = self._analyze_provider_optimization(provider_enum, provider_data)
                optimization_analysis["provider_analyses"][provider_name] = provider_analysis
                
                # Aggregate costs
                optimization_analysis["total_monthly_cost"] += provider_analysis.get("total_cost", 0.0)
                optimization_analysis["optimized_monthly_cost"] += provider_analysis.get("optimized_cost", 0.0)
                
            except ValueError:
                # Unknown provider
                continue
        
        # Calculate total potential savings
        optimization_analysis["potential_savings"] = (
            optimization_analysis["total_monthly_cost"] - 
            optimization_analysis["optimized_monthly_cost"]
        )
        
        # Generate cross-cloud recommendations
        cross_cloud_recommendations = self._generate_cross_cloud_recommendations(infrastructure_data)
        optimization_analysis["cross_cloud_recommendations"] = cross_cloud_recommendations
        
        # Identify migration opportunities
        migration_opportunities = self._identify_migration_opportunities(infrastructure_data)
        optimization_analysis["migration_opportunities"] = migration_opportunities
        
        # Find consolidation opportunities
        consolidation_opportunities = self._find_consolidation_opportunities(infrastructure_data)
        optimization_analysis["consolidation_opportunities"] = consolidation_opportunities
        
        return optimization_analysis
    
    def _analyze_provider_optimization(self, provider: CloudProvider, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze optimization for a specific provider"""
        
        provider_analysis = {
            "total_cost": 0.0,
            "optimized_cost": 0.0,
            "service_analyses": {},
            "recommendations": []
        }
        
        provider_services = self.providers.get(provider, {})
        
        for service_name, service_data in provider_data.items():
            # Determine service type and get appropriate intelligence engine
            service_type = self._determine_service_type(service_name, service_data)
            intelligence_engine = provider_services.get(service_type)
            
            if intelligence_engine:
                try:
                    # Perform service-specific analysis
                    if hasattr(intelligence_engine, 'analyze_optimization'):
                        analysis = intelligence_engine.analyze_optimization(service_data)
                    elif hasattr(intelligence_engine, 'analyze_cost_optimization'):
                        analysis = intelligence_engine.analyze_cost_optimization(service_data)
                    else:
                        # Generic analysis
                        analysis = self._generic_service_analysis(service_data)
                    
                    provider_analysis["service_analyses"][service_name] = analysis
                    
                    # Aggregate costs
                    provider_analysis["total_cost"] += analysis.get("current_cost_estimate", 0.0)
                    provider_analysis["optimized_cost"] += analysis.get("optimized_cost_estimate", 0.0)
                    
                    # Collect recommendations
                    if "recommendations" in analysis:
                        provider_analysis["recommendations"].extend(analysis["recommendations"])
                
                except Exception as e:
                    # Handle analysis errors gracefully
                    provider_analysis["service_analyses"][service_name] = {
                        "error": f"Analysis failed: {str(e)}"
                    }
        
        return provider_analysis
    
    def _determine_service_type(self, service_name: str, service_data: Dict[str, Any]) -> ServiceType:
        """Determine the service type from service name and data"""
        
        # Service name patterns
        if any(keyword in service_name.lower() for keyword in ["droplet", "instance", "vm", "compute"]):
            return ServiceType.COMPUTE
        elif any(keyword in service_name.lower() for keyword in ["container", "ecs", "gke", "kubernetes"]):
            return ServiceType.CONTAINER
        elif any(keyword in service_name.lower() for keyword in ["load", "balancer", "lb", "alb", "nlb"]):
            return ServiceType.LOAD_BALANCER
        elif any(keyword in service_name.lower() for keyword in ["vpc", "network", "subnet"]):
            return ServiceType.NETWORK
        elif any(keyword in service_name.lower() for keyword in ["dns", "domain", "zone"]):
            return ServiceType.DNS
        elif any(keyword in service_name.lower() for keyword in ["database", "rds", "sql"]):
            return ServiceType.DATABASE
        elif any(keyword in service_name.lower() for keyword in ["storage", "s3", "bucket"]):
            return ServiceType.STORAGE
        
        # Service data patterns
        if "instance_type" in service_data or "machine_type" in service_data:
            return ServiceType.COMPUTE
        elif "cluster_name" in service_data or "node_pools" in service_data:
            return ServiceType.CONTAINER
        elif "load_balancer_type" in service_data or "backend_services" in service_data:
            return ServiceType.LOAD_BALANCER
        elif "vpc_id" in service_data or "subnets" in service_data:
            return ServiceType.NETWORK
        elif "dns_records" in service_data or "zone_id" in service_data:
            return ServiceType.DNS
        
        # Default to compute
        return ServiceType.COMPUTE
    
    def _generic_service_analysis(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic analysis for services without specific intelligence"""
        
        return {
            "current_cost_estimate": 0.0,
            "optimized_cost_estimate": 0.0,
            "recommendations": ["Service analysis not available - consider manual review"]
        }
    
    # ==========================================
    # CROSS-CLOUD INTELLIGENCE
    # ==========================================
    
    def _generate_cross_cloud_recommendations(self, infrastructure_data: Dict[str, Any]) -> List[str]:
        """Generate cross-cloud optimization recommendations"""
        
        recommendations = []
        
        # Analyze provider distribution
        providers_used = list(infrastructure_data.keys())
        
        if len(providers_used) == 1:
            recommendations.append("Single provider detected - consider multi-cloud strategy for resilience")
        elif len(providers_used) > 3:
            recommendations.append("Many providers in use - consider consolidation for easier management")
        
        # DNS and CDN optimization
        if "cloudflare" in providers_used:
            recommendations.append("Cloudflare detected - leverage for global CDN and DDoS protection")
        
        # Container orchestration optimization
        has_ecs = any("ecs" in str(data).lower() for data in infrastructure_data.values())
        has_gke = any("gke" in str(data).lower() for data in infrastructure_data.values())
        
        if has_ecs and has_gke:
            recommendations.append("Multiple container platforms detected - consider standardizing on one platform")
        
        # Load balancer optimization
        lb_count = 0
        for provider_data in infrastructure_data.values():
            if isinstance(provider_data, dict):
                lb_count += len([s for s in provider_data.keys() if "load" in s.lower() or "lb" in s.lower()])
        
        if lb_count > 5:
            recommendations.append("Many load balancers detected - consider consolidation and global load balancing")
        
        # Data locality recommendations
        recommendations.append("Review data locality and compliance requirements across regions")
        recommendations.append("Implement cross-cloud backup and disaster recovery strategies")
        
        return recommendations
    
    def _identify_migration_opportunities(self, infrastructure_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify opportunities to migrate services between providers"""
        
        opportunities = []
        
        # Cost-based migration opportunities
        for provider_name, provider_data in infrastructure_data.items():
            if isinstance(provider_data, dict):
                for service_name, service_data in provider_data.items():
                    if isinstance(service_data, dict):
                        # Example: High-cost compute workloads could be migrated to cheaper providers
                        estimated_cost = service_data.get("monthly_cost_estimate", 0)
                        if estimated_cost > 500:  # High-cost service
                            opportunities.append({
                                "source_provider": provider_name,
                                "service": service_name,
                                "opportunity": "Consider migrating high-cost workload to more cost-effective provider",
                                "potential_savings": estimated_cost * 0.2,  # Estimate 20% savings
                                "migration_complexity": "medium"
                            })
        
        # Geographic optimization opportunities
        opportunities.append({
            "opportunity": "Migrate workloads closer to users for better performance",
            "recommendation": "Analyze user geography and optimize provider/region selection",
            "migration_complexity": "high"
        })
        
        return opportunities
    
    def _find_consolidation_opportunities(self, infrastructure_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find opportunities to consolidate services"""
        
        opportunities = []
        
        # Compute consolidation
        compute_services = []
        for provider_name, provider_data in infrastructure_data.items():
            if isinstance(provider_data, dict):
                for service_name, service_data in provider_data.items():
                    if isinstance(service_data, dict):
                        service_type = self._determine_service_type(service_name, service_data)
                        if service_type == ServiceType.COMPUTE:
                            compute_services.append({
                                "provider": provider_name,
                                "service": service_name,
                                "utilization": service_data.get("metrics", {}).get("cpu_utilization", 0.5)
                            })
        
        # Find underutilized compute services
        underutilized = [s for s in compute_services if s["utilization"] < 0.3]
        if len(underutilized) > 1:
            opportunities.append({
                "type": "compute_consolidation",
                "services": underutilized,
                "opportunity": f"Consolidate {len(underutilized)} underutilized compute services",
                "potential_savings": len(underutilized) * 50,  # Estimate $50 savings per service
                "complexity": "medium"
            })
        
        return opportunities
    
    # ==========================================
    # UNIFIED SECURITY ANALYSIS
    # ==========================================
    
    def analyze_cross_cloud_security(self, infrastructure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security posture across all cloud providers"""
        
        security_analysis = {
            "overall_security_score": 0.0,
            "provider_security_scores": {},
            "critical_vulnerabilities": [],
            "recommendations": [],
            "compliance_summary": {}
        }
        
        total_score = 0.0
        provider_count = 0
        
        # Analyze each provider's security
        for provider_name, provider_data in infrastructure_data.items():
            try:
                provider_enum = CloudProvider(provider_name.lower())
                provider_security = self._analyze_provider_security(provider_enum, provider_data)
                
                security_analysis["provider_security_scores"][provider_name] = provider_security
                total_score += provider_security.get("security_score", 0.0)
                provider_count += 1
                
                # Collect critical vulnerabilities
                critical_vulns = provider_security.get("critical_vulnerabilities", [])
                security_analysis["critical_vulnerabilities"].extend(critical_vulns)
                
                # Collect recommendations
                recommendations = provider_security.get("recommendations", [])
                security_analysis["recommendations"].extend(recommendations)
                
            except ValueError:
                continue
        
        # Calculate overall security score
        if provider_count > 0:
            security_analysis["overall_security_score"] = total_score / provider_count
        
        # Generate cross-cloud security recommendations
        cross_cloud_security_recs = self._generate_cross_cloud_security_recommendations(infrastructure_data)
        security_analysis["recommendations"].extend(cross_cloud_security_recs)
        
        return security_analysis
    
    def _analyze_provider_security(self, provider: CloudProvider, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security for a specific provider"""
        
        provider_security = {
            "security_score": 0.0,
            "critical_vulnerabilities": [],
            "recommendations": []
        }
        
        provider_services = self.providers.get(provider, {})
        service_scores = []
        
        for service_name, service_data in provider_data.items():
            service_type = self._determine_service_type(service_name, service_data)
            intelligence_engine = provider_services.get(service_type)
            
            if intelligence_engine and hasattr(intelligence_engine, 'analyze_security_posture'):
                try:
                    security_analysis = intelligence_engine.analyze_security_posture(service_data)
                    service_scores.append(security_analysis.get("security_score", 0.0))
                    
                    # Collect vulnerabilities and recommendations
                    provider_security["critical_vulnerabilities"].extend(
                        security_analysis.get("vulnerabilities", [])
                    )
                    provider_security["recommendations"].extend(
                        security_analysis.get("recommendations", [])
                    )
                    
                except Exception:
                    # Handle analysis errors gracefully
                    service_scores.append(50.0)  # Default moderate score
        
        # Calculate average security score
        if service_scores:
            provider_security["security_score"] = sum(service_scores) / len(service_scores)
        
        return provider_security
    
    def _generate_cross_cloud_security_recommendations(self, infrastructure_data: Dict[str, Any]) -> List[str]:
        """Generate cross-cloud security recommendations"""
        
        recommendations = [
            "Implement centralized security monitoring across all cloud providers",
            "Ensure consistent security policies across all environments",
            "Regular security audits and penetration testing for multi-cloud setup",
            "Implement zero-trust architecture for cross-cloud communications"
        ]
        
        # Provider-specific recommendations
        providers_used = list(infrastructure_data.keys())
        
        if "aws" in providers_used and "gcp" in providers_used:
            recommendations.append("Implement cross-cloud IAM federation between AWS and GCP")
        
        if "cloudflare" in providers_used:
            recommendations.append("Leverage Cloudflare WAF for unified web application protection")
        
        return recommendations
    
    # ==========================================
    # PERFORMANCE OPTIMIZATION
    # ==========================================
    
    def analyze_cross_cloud_performance(self, infrastructure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance optimization across all providers"""
        
        performance_analysis = {
            "overall_performance_score": 0.0,
            "provider_performance": {},
            "bottlenecks": [],
            "optimization_opportunities": []
        }
        
        # Analyze each provider
        for provider_name, provider_data in infrastructure_data.items():
            provider_performance = self._analyze_provider_performance(provider_name, provider_data)
            performance_analysis["provider_performance"][provider_name] = provider_performance
        
        # Identify global bottlenecks and optimization opportunities
        global_optimizations = self._identify_global_performance_optimizations(infrastructure_data)
        performance_analysis["optimization_opportunities"] = global_optimizations
        
        return performance_analysis
    
    def _analyze_provider_performance(self, provider_name: str, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance for a specific provider"""
        
        # Generic performance analysis
        return {
            "response_time_avg": 0.2,
            "availability": 0.999,
            "recommendations": [
                f"Monitor {provider_name} service performance regularly",
                f"Optimize {provider_name} resource allocation based on usage patterns"
            ]
        }
    
    def _identify_global_performance_optimizations(self, infrastructure_data: Dict[str, Any]) -> List[str]:
        """Identify global performance optimization opportunities"""
        
        return [
            "Implement global load balancing for better geographic distribution",
            "Use CDN services to improve content delivery performance",
            "Optimize database placement for data locality",
            "Implement caching strategies across all services"
        ]
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def get_supported_providers(self) -> List[str]:
        """Get list of supported cloud providers"""
        return [provider.value for provider in CloudProvider]
    
    def get_supported_services(self, provider: str) -> List[str]:
        """Get list of supported services for a provider"""
        try:
            provider_enum = CloudProvider(provider.lower())
            provider_services = self.providers.get(provider_enum, {})
            return [service.value for service in provider_services.keys()]
        except ValueError:
            return []
    
    def generate_unified_recommendations(self, infrastructure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate unified recommendations across all areas"""
        
        unified_recommendations = {
            "cost_optimization": [],
            "security_hardening": [],
            "performance_tuning": [],
            "architecture_improvements": [],
            "migration_opportunities": []
        }
        
        # Cost optimization recommendations
        cost_analysis = self.analyze_multi_cloud_optimization(infrastructure_data)
        unified_recommendations["cost_optimization"] = cost_analysis.get("cross_cloud_recommendations", [])
        unified_recommendations["migration_opportunities"] = cost_analysis.get("migration_opportunities", [])
        
        # Security recommendations
        security_analysis = self.analyze_cross_cloud_security(infrastructure_data)
        unified_recommendations["security_hardening"] = security_analysis.get("recommendations", [])
        
        # Performance recommendations
        performance_analysis = self.analyze_cross_cloud_performance(infrastructure_data)
        unified_recommendations["performance_tuning"] = performance_analysis.get("optimization_opportunities", [])
        
        # Architecture improvements
        unified_recommendations["architecture_improvements"] = [
            "Implement Infrastructure as Code across all providers",
            "Standardize monitoring and alerting across all environments",
            "Implement automated backup and disaster recovery",
            "Create consistent deployment pipelines for all environments"
        ]
        
        return unified_recommendations


# Global instance for easy access
unified_intelligence = UnifiedProviderIntelligence()

# Export for external use
__all__ = [
    'UnifiedProviderIntelligence',
    'CloudProvider', 
    'ServiceType',
    'unified_intelligence'
]
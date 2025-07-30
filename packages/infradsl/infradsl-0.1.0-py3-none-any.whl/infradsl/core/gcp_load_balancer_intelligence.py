"""
GCP Load Balancer Intelligence

Advanced intelligence for Google Cloud Load Balancing services
providing intelligent traffic distribution, SSL management, and cost optimization.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from .gcp_intelligence_base import GCPIntelligenceBase
from .stateless_intelligence import (
    ResourceType, ResourceFingerprint, ChangeImpactAnalysis, 
    ResourceHealth, HealthStatus
)


class GCPLoadBalancerIntelligence(GCPIntelligenceBase):
    """
    GCP Load Balancer Intelligence Engine
    
    Provides intelligent load balancing including:
    - Smart traffic routing optimization for Global/Regional LBs
    - SSL certificate management and automation
    - Cost optimization for different load balancer types
    - Health check intelligence and optimization
    - CDN integration recommendations
    - Auto-scaling integration with managed instance groups
    """
    
    def __init__(self):
        super().__init__(ResourceType.LOAD_BALANCER)
        self.optimization_rules = {
            "utilization_thresholds": {
                "consolidation_threshold": 0.25,  # Consolidate LBs under 25% utilization
                "optimal_range": (0.40, 0.75),
                "scale_threshold": 0.80
            },
            "cost_optimization": {
                "global_lb_monthly_cost": 18.00,     # Global Load Balancer
                "regional_lb_monthly_cost": 18.00,   # Regional Load Balancer
                "classic_lb_monthly_cost": 18.00,    # Classic Load Balancer
                "data_processing_cost_per_gb": 0.008, # Data processing
                "forwarding_rule_cost": 0.025,       # Per forwarding rule per hour
                "cloud_cdn_cost_per_gb": 0.08        # Cloud CDN cost
            },
            "ssl_management": {
                "certificate_expiry_warning_days": 30,
                "recommend_google_managed": True,
                "cipher_suite_recommendations": ["TLS_1_2", "TLS_1_3"]
            },
            "performance_thresholds": {
                "response_time_warning": 1.0,      # 1 second
                "error_rate_warning": 0.05,        # 5%
                "backend_utilization_warning": 0.85 # 85%
            }
        }
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing GCP load balancers"""
        
        # Mock implementation - in production would use Google Cloud Client Library
        return {
            "global-web-lb": {
                "name": "global-web-lb",
                "load_balancer_type": "EXTERNAL_HTTP_HTTPS",
                "ip_version": "IPV4",
                "load_balancing_scheme": "EXTERNAL",
                "protocol": "HTTP",
                "port_range": "80",
                "ip_address": "203.0.113.1",
                "creation_timestamp": "2024-01-15T10:30:00Z",
                "region": "global",
                "forwarding_rules": [
                    {
                        "name": "global-web-lb-forwarding-rule",
                        "ip_address": "203.0.113.1",
                        "ip_protocol": "TCP",
                        "port_range": "80",
                        "target": "global-web-lb-target-proxy"
                    },
                    {
                        "name": "global-web-lb-https-forwarding-rule",
                        "ip_address": "203.0.113.1",
                        "ip_protocol": "TCP",
                        "port_range": "443",
                        "target": "global-web-lb-https-target-proxy"
                    }
                ],
                "url_map": {
                    "name": "global-web-lb-url-map",
                    "default_service": "web-backend-service",
                    "path_matchers": [
                        {
                            "name": "api-matcher",
                            "default_service": "api-backend-service",
                            "path_rules": [
                                {"paths": ["/api/*"], "service": "api-backend-service"}
                            ]
                        }
                    ]
                },
                "backend_services": [
                    {
                        "name": "web-backend-service",
                        "protocol": "HTTP",
                        "port": 80,
                        "timeout_sec": 30,
                        "load_balancing_scheme": "EXTERNAL",
                        "backends": [
                            {
                                "group": "web-instance-group-us-central1",
                                "balancing_mode": "UTILIZATION",
                                "max_utilization": 0.8,
                                "capacity_scaler": 1.0
                            },
                            {
                                "group": "web-instance-group-us-east1",
                                "balancing_mode": "UTILIZATION",
                                "max_utilization": 0.8,
                                "capacity_scaler": 1.0
                            }
                        ],
                        "health_checks": ["web-health-check"],
                        "cdn_policy": {
                            "cache_key_policy": {
                                "include_host": True,
                                "include_protocol": True,
                                "include_query_string": False
                            },
                            "default_ttl": 3600
                        }
                    },
                    {
                        "name": "api-backend-service",
                        "protocol": "HTTP",
                        "port": 8080,
                        "timeout_sec": 10,
                        "load_balancing_scheme": "EXTERNAL",
                        "backends": [
                            {
                                "group": "api-instance-group-us-central1",
                                "balancing_mode": "RATE",
                                "max_rate_per_instance": 100,
                                "capacity_scaler": 1.0
                            }
                        ],
                        "health_checks": ["api-health-check"]
                    }
                ],
                "health_checks": [
                    {
                        "name": "web-health-check",
                        "type": "HTTP",
                        "request_path": "/health",
                        "port": 80,
                        "check_interval_sec": 10,
                        "timeout_sec": 5,
                        "healthy_threshold": 2,
                        "unhealthy_threshold": 3
                    },
                    {
                        "name": "api-health-check",
                        "type": "HTTP",
                        "request_path": "/api/health",
                        "port": 8080,
                        "check_interval_sec": 10,
                        "timeout_sec": 5,
                        "healthy_threshold": 2,
                        "unhealthy_threshold": 3
                    }
                ],
                "ssl_certificates": [
                    {
                        "name": "web-ssl-cert",
                        "type": "MANAGED",
                        "domains": ["example.com", "www.example.com"],
                        "status": "ACTIVE",
                        "creation_timestamp": "2024-01-01T00:00:00Z"
                    }
                ],
                "metrics": {
                    "request_count": 25000,
                    "request_bytes": 125000000,
                    "response_bytes": 500000000,
                    "backend_latency": 0.150,
                    "total_latency": 0.200,
                    "error_rate": 0.02,
                    "cache_hit_ratio": 0.75,
                    "data_processed_gb": 625.0
                },
                "cloud_cdn_enabled": True
            },
            "regional-internal-lb": {
                "name": "regional-internal-lb",
                "load_balancer_type": "INTERNAL_TCP_UDP",
                "ip_version": "IPV4",
                "load_balancing_scheme": "INTERNAL",
                "protocol": "TCP",
                "port_range": "80",
                "ip_address": "10.1.0.100",
                "creation_timestamp": "2024-02-01T10:30:00Z",
                "region": "us-central1",
                "forwarding_rules": [
                    {
                        "name": "internal-lb-forwarding-rule",
                        "ip_address": "10.1.0.100",
                        "ip_protocol": "TCP",
                        "port_range": "80",
                        "target": "internal-backend-service",
                        "subnetwork": "internal-subnet"
                    }
                ],
                "backend_services": [
                    {
                        "name": "internal-backend-service",
                        "protocol": "TCP",
                        "port": 80,
                        "timeout_sec": 30,
                        "load_balancing_scheme": "INTERNAL",
                        "backends": [
                            {
                                "group": "internal-instance-group",
                                "balancing_mode": "CONNECTION",
                                "max_connections": 100,
                                "capacity_scaler": 1.0
                            }
                        ],
                        "health_checks": ["internal-health-check"]
                    }
                ],
                "health_checks": [
                    {
                        "name": "internal-health-check",
                        "type": "TCP",
                        "port": 80,
                        "check_interval_sec": 10,
                        "timeout_sec": 5,
                        "healthy_threshold": 2,
                        "unhealthy_threshold": 3
                    }
                ],
                "metrics": {
                    "request_count": 5000,
                    "backend_latency": 0.080,
                    "total_latency": 0.090,
                    "error_rate": 0.01,
                    "data_processed_gb": 25.0
                },
                "cloud_cdn_enabled": False
            },
            "legacy-network-lb": {
                "name": "legacy-network-lb",
                "load_balancer_type": "EXTERNAL_TCP_UDP",
                "ip_version": "IPV4",
                "load_balancing_scheme": "EXTERNAL",
                "protocol": "TCP",
                "port_range": "80",
                "ip_address": "203.0.113.2",
                "creation_timestamp": "2023-06-01T10:30:00Z",
                "region": "us-west1",
                "forwarding_rules": [
                    {
                        "name": "legacy-lb-forwarding-rule",
                        "ip_address": "203.0.113.2",
                        "ip_protocol": "TCP",
                        "port_range": "80",
                        "target": "legacy-target-pool"
                    }
                ],
                "target_pools": [
                    {
                        "name": "legacy-target-pool",
                        "instances": [
                            "legacy-instance-1",
                            "legacy-instance-2"
                        ],
                        "health_checks": ["legacy-health-check"],
                        "session_affinity": "CLIENT_IP"
                    }
                ],
                "health_checks": [
                    {
                        "name": "legacy-health-check",
                        "type": "TCP",
                        "port": 80,
                        "check_interval_sec": 10,
                        "timeout_sec": 5,
                        "healthy_threshold": 2,
                        "unhealthy_threshold": 3
                    }
                ],
                "metrics": {
                    "request_count": 1500,
                    "backend_latency": 0.200,
                    "total_latency": 0.250,
                    "error_rate": 0.05,
                    "data_processed_gb": 7.5
                },
                "cloud_cdn_enabled": False
            }
        }
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract load balancer configuration from cloud state"""
        
        return {
            "name": cloud_state.get("name"),
            "load_balancer_type": cloud_state.get("load_balancer_type"),
            "load_balancing_scheme": cloud_state.get("load_balancing_scheme"),
            "protocol": cloud_state.get("protocol"),
            "region": cloud_state.get("region"),
            "forwarding_rules": cloud_state.get("forwarding_rules", []),
            "backend_services": cloud_state.get("backend_services", []),
            "health_checks": cloud_state.get("health_checks", []),
            "ssl_certificates": cloud_state.get("ssl_certificates", []),
            "metrics": cloud_state.get("metrics", {}),
            "cloud_cdn_enabled": cloud_state.get("cloud_cdn_enabled", False)
        }
    
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """Generate hash for load balancer configuration"""
        
        # Focus on key configuration elements
        key_config = {
            "name": config.get("name"),
            "load_balancer_type": config.get("load_balancer_type"),
            "load_balancing_scheme": config.get("load_balancing_scheme"),
            "forwarding_rules": [
                {
                    "port_range": fr.get("port_range"),
                    "ip_protocol": fr.get("ip_protocol")
                }
                for fr in config.get("forwarding_rules", [])
            ],
            "backend_services": [
                {
                    "name": bs.get("name"),
                    "protocol": bs.get("protocol"),
                    "port": bs.get("port")
                }
                for bs in config.get("backend_services", [])
            ],
            "ssl_certificates": len(config.get("ssl_certificates", []))
        }
        
        return str(hash(json.dumps(key_config, sort_keys=True)))
    
    def analyze_load_balancer_optimization(self, lb_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze load balancer for optimization opportunities
        """
        
        optimization_analysis = {
            "load_balancer_name": lb_data.get("name"),
            "type": lb_data.get("load_balancer_type"),
            "current_cost_estimate": 0.0,
            "optimized_cost_estimate": 0.0,
            "potential_savings": 0.0,
            "recommendations": [],
            "ssl_recommendations": [],
            "health_check_recommendations": [],
            "cdn_recommendations": [],
            "modernization_recommendations": []
        }
        
        # Cost analysis
        cost_analysis = self._analyze_cost_optimization(lb_data)
        optimization_analysis.update(cost_analysis)
        
        # SSL/TLS analysis
        ssl_analysis = self._analyze_ssl_configuration(lb_data)
        optimization_analysis["ssl_recommendations"] = ssl_analysis
        
        # Health check optimization
        health_analysis = self._analyze_health_checks(lb_data)
        optimization_analysis["health_check_recommendations"] = health_analysis
        
        # CDN optimization
        cdn_analysis = self._analyze_cdn_optimization(lb_data)
        optimization_analysis["cdn_recommendations"] = cdn_analysis
        
        # Modernization recommendations
        if lb_data.get("load_balancer_type") == "EXTERNAL_TCP_UDP":
            modernization = self._analyze_modernization_opportunities(lb_data)
            optimization_analysis["modernization_recommendations"] = modernization
        
        # Performance recommendations
        performance_analysis = self._analyze_performance_optimization(lb_data)
        optimization_analysis["recommendations"].extend(performance_analysis)
        
        return optimization_analysis
    
    def _analyze_cost_optimization(self, lb_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost optimization opportunities"""
        
        lb_type = lb_data.get("load_balancer_type")
        metrics = lb_data.get("metrics", {})
        region = lb_data.get("region", "global")
        
        # Calculate current costs
        if region == "global":
            base_cost = self.optimization_rules["cost_optimization"]["global_lb_monthly_cost"]
        else:
            base_cost = self.optimization_rules["cost_optimization"]["regional_lb_monthly_cost"]
        
        data_processed = metrics.get("data_processed_gb", 0)
        data_cost = data_processed * self.optimization_rules["cost_optimization"]["data_processing_cost_per_gb"]
        
        forwarding_rules = lb_data.get("forwarding_rules", [])
        forwarding_rule_cost = len(forwarding_rules) * self.optimization_rules["cost_optimization"]["forwarding_rule_cost"] * 24 * 30
        
        current_monthly_cost = base_cost + data_cost + forwarding_rule_cost
        
        # CDN cost analysis
        cdn_cost = 0.0
        if lb_data.get("cloud_cdn_enabled", False):
            # Estimate CDN cost based on cache hit ratio
            cache_hit_ratio = metrics.get("cache_hit_ratio", 0.0)
            cdn_eligible_traffic = data_processed * cache_hit_ratio
            cdn_cost = cdn_eligible_traffic * self.optimization_rules["cost_optimization"]["cloud_cdn_cost_per_gb"]
            current_monthly_cost += cdn_cost
        
        # Analyze utilization
        request_count = metrics.get("request_count", 0)
        utilization_score = min(request_count / 50000, 1.0)  # Normalize to 50k requests as 100%
        
        optimized_cost = current_monthly_cost
        recommendations = []
        
        if utilization_score < self.optimization_rules["utilization_thresholds"]["consolidation_threshold"]:
            recommendations.append(f"Low utilization detected ({utilization_score:.1%}) - consider consolidation")
            # Potential savings through consolidation
            optimized_cost = current_monthly_cost * 0.6
        
        # CDN optimization
        if not lb_data.get("cloud_cdn_enabled", False) and data_processed > 100:
            recommendations.append("Enable Cloud CDN to reduce origin traffic and costs")
            # Estimate CDN savings
            estimated_cdn_savings = data_processed * 0.3 * self.optimization_rules["cost_optimization"]["data_processing_cost_per_gb"]
            optimized_cost -= estimated_cdn_savings
        
        # Forwarding rule optimization
        if len(forwarding_rules) > 2:
            recommendations.append("Review forwarding rules for potential consolidation")
        
        return {
            "current_cost_estimate": current_monthly_cost,
            "optimized_cost_estimate": optimized_cost,
            "potential_savings": current_monthly_cost - optimized_cost,
            "utilization_score": utilization_score,
            "cost_breakdown": {
                "base_cost": base_cost,
                "data_processing": data_cost,
                "forwarding_rules": forwarding_rule_cost,
                "cdn_cost": cdn_cost
            },
            "recommendations": recommendations
        }
    
    def _analyze_ssl_configuration(self, lb_data: Dict[str, Any]) -> List[str]:
        """Analyze SSL/TLS configuration and provide recommendations"""
        
        recommendations = []
        ssl_certificates = lb_data.get("ssl_certificates", [])
        forwarding_rules = lb_data.get("forwarding_rules", [])
        
        # Check for HTTPS support
        has_https = any(fr.get("port_range") == "443" for fr in forwarding_rules)
        has_http = any(fr.get("port_range") == "80" for fr in forwarding_rules)
        
        if has_http and not has_https:
            recommendations.append("Add HTTPS support for improved security")
        
        # SSL certificate analysis
        for cert in ssl_certificates:
            cert_type = cert.get("type", "SELF_MANAGED")
            
            if cert_type == "SELF_MANAGED":
                recommendations.append("Consider Google-managed SSL certificates for easier management")
            
            # Check certificate status
            status = cert.get("status", "")
            if status != "ACTIVE":
                recommendations.append(f"SSL certificate {cert.get('name')} is not active")
            
            # Check domain coverage
            domains = cert.get("domains", [])
            if len(domains) > 100:
                recommendations.append("Consider splitting certificates for better management")
        
        # General SSL recommendations
        if ssl_certificates:
            recommendations.append("Enable HTTP Strict Transport Security (HSTS)")
            recommendations.append("Configure security headers for enhanced protection")
        
        if not ssl_certificates and has_https:
            recommendations.append("HTTPS forwarding rule without SSL certificate detected")
        
        return recommendations
    
    def _analyze_health_checks(self, lb_data: Dict[str, Any]) -> List[str]:
        """Analyze health check configuration"""
        
        recommendations = []
        health_checks = lb_data.get("health_checks", [])
        backend_services = lb_data.get("backend_services", [])
        
        for hc in health_checks:
            check_interval = hc.get("check_interval_sec", 10)
            timeout = hc.get("timeout_sec", 5)
            healthy_threshold = hc.get("healthy_threshold", 2)
            unhealthy_threshold = hc.get("unhealthy_threshold", 3)
            check_type = hc.get("type", "HTTP")
            
            # Check interval optimization
            if check_interval > 30:
                recommendations.append(f"Consider reducing health check interval for {hc.get('name')} for faster failure detection")
            elif check_interval < 5:
                recommendations.append(f"Health check interval for {hc.get('name')} may be too aggressive")
            
            # Timeout optimization
            if timeout > check_interval * 0.8:
                recommendations.append(f"Health check timeout for {hc.get('name')} is close to interval")
            
            # Threshold optimization
            if healthy_threshold > 5:
                recommendations.append(f"Reduce healthy threshold for {hc.get('name')} for faster recovery")
            
            if unhealthy_threshold < 2:
                recommendations.append(f"Increase unhealthy threshold for {hc.get('name')} to avoid false positives")
            
            # Health check path optimization
            if check_type == "HTTP":
                request_path = hc.get("request_path", "/")
                if request_path == "/":
                    recommendations.append(f"Use dedicated health check endpoint for {hc.get('name')}")
        
        # Backend service health check coverage
        for bs in backend_services:
            bs_health_checks = bs.get("health_checks", [])
            if not bs_health_checks:
                recommendations.append(f"Backend service {bs.get('name')} has no health checks")
        
        return recommendations
    
    def _analyze_cdn_optimization(self, lb_data: Dict[str, Any]) -> List[str]:
        """Analyze CDN configuration and optimization"""
        
        recommendations = []
        cdn_enabled = lb_data.get("cloud_cdn_enabled", False)
        metrics = lb_data.get("metrics", {})
        backend_services = lb_data.get("backend_services", [])
        
        data_processed = metrics.get("data_processed_gb", 0)
        cache_hit_ratio = metrics.get("cache_hit_ratio", 0.0)
        
        if not cdn_enabled and data_processed > 50:
            recommendations.append("Enable Cloud CDN to improve performance and reduce costs")
            recommendations.append("Cloud CDN can significantly reduce origin server load")
        
        if cdn_enabled:
            # Cache hit ratio optimization
            if cache_hit_ratio < 0.5:
                recommendations.append("Low cache hit ratio - review cache policies and TTL settings")
                recommendations.append("Consider optimizing cacheable content and headers")
            elif cache_hit_ratio > 0.9:
                recommendations.append("Excellent cache hit ratio - consider expanding CDN usage")
            
            # CDN policy optimization
            for bs in backend_services:
                cdn_policy = bs.get("cdn_policy", {})
                if cdn_policy:
                    default_ttl = cdn_policy.get("default_ttl", 3600)
                    if default_ttl < 300:  # 5 minutes
                        recommendations.append(f"Consider increasing default TTL for {bs.get('name')}")
                    
                    cache_key_policy = cdn_policy.get("cache_key_policy", {})
                    if cache_key_policy.get("include_query_string", False):
                        recommendations.append("Review query string inclusion in cache key for better hit rates")
        
        # Regional CDN recommendations
        region = lb_data.get("region", "global")
        if region != "global" and cdn_enabled:
            recommendations.append("Consider global load balancer for better CDN performance")
        
        return recommendations
    
    def _analyze_modernization_opportunities(self, lb_data: Dict[str, Any]) -> List[str]:
        """Analyze modernization opportunities for legacy load balancers"""
        
        recommendations = [
            "Migrate from Network Load Balancer to Application Load Balancer for better features",
            "Application Load Balancer provides URL-based routing and SSL termination",
            "Enhanced monitoring and logging capabilities with modern load balancers",
            "Better integration with Google Cloud services like Cloud Armor"
        ]
        
        # Analyze current configuration for migration complexity
        target_pools = lb_data.get("target_pools", [])
        forwarding_rules = lb_data.get("forwarding_rules", [])
        
        if len(target_pools) == 1 and len(forwarding_rules) == 1:
            recommendations.append("Simple migration path available - single target pool and forwarding rule")
        else:
            recommendations.append("Complex migration - plan carefully for multiple target pools")
        
        # Protocol analysis
        protocol = lb_data.get("protocol", "TCP")
        if protocol == "TCP":
            recommendations.append("Consider Application Load Balancer for HTTP/HTTPS traffic")
        
        return recommendations
    
    def _analyze_performance_optimization(self, lb_data: Dict[str, Any]) -> List[str]:
        """Analyze performance optimization opportunities"""
        
        recommendations = []
        metrics = lb_data.get("metrics", {})
        backend_services = lb_data.get("backend_services", [])
        
        # Latency analysis
        backend_latency = metrics.get("backend_latency", 0)
        total_latency = metrics.get("total_latency", 0)
        
        if backend_latency > self.optimization_rules["performance_thresholds"]["response_time_warning"]:
            recommendations.append("High backend latency detected - investigate backend performance")
        
        if total_latency > backend_latency * 1.5:
            recommendations.append("High load balancer overhead - review configuration")
        
        # Error rate analysis
        error_rate = metrics.get("error_rate", 0)
        if error_rate > self.optimization_rules["performance_thresholds"]["error_rate_warning"]:
            recommendations.append("High error rate detected - investigate backend health and capacity")
        
        # Backend service optimization
        for bs in backend_services:
            balancing_mode = None
            max_utilization = 0
            
            for backend in bs.get("backends", []):
                if backend.get("balancing_mode") == "UTILIZATION":
                    balancing_mode = "UTILIZATION"
                    max_utilization = max(max_utilization, backend.get("max_utilization", 0))
            
            if balancing_mode == "UTILIZATION" and max_utilization > 0.85:
                recommendations.append(f"High utilization threshold for {bs.get('name')} - consider reducing")
            
            # Timeout analysis
            timeout_sec = bs.get("timeout_sec", 30)
            if timeout_sec > 60:
                recommendations.append(f"Long timeout configured for {bs.get('name')} - review necessity")
        
        # Regional distribution
        region = lb_data.get("region", "global")
        if region != "global":
            recommendations.append("Consider global load balancer for better geographic distribution")
        
        return recommendations
    
    def predict_traffic_patterns(self, lb_name: str, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict traffic patterns and scaling needs
        """
        
        if not metrics_history or len(metrics_history) < 24:
            return {"prediction": "insufficient_data", "confidence": 0.0}
        
        # Analyze traffic patterns
        request_counts = [m.get("request_count", 0) for m in metrics_history]
        response_times = [m.get("backend_latency", 0) for m in metrics_history]
        error_rates = [m.get("error_rate", 0) for m in metrics_history]
        
        # Calculate basic statistics
        avg_requests = sum(request_counts) / len(request_counts)
        peak_requests = max(request_counts)
        avg_response_time = sum(response_times) / len(response_times)
        avg_error_rate = sum(error_rates) / len(error_rates)
        
        # Identify peak hours
        peak_hours = self._identify_peak_hours(metrics_history)
        
        # Trend analysis
        if len(request_counts) >= 7:
            recent_avg = sum(request_counts[-7:]) / 7
            earlier_avg = sum(request_counts[:7]) / 7
            trend = "increasing" if recent_avg > earlier_avg * 1.1 else "stable"
        else:
            trend = "stable"
        
        prediction = {
            "load_balancer_name": lb_name,
            "traffic_analysis": {
                "average_requests": avg_requests,
                "peak_requests": peak_requests,
                "average_response_time": avg_response_time,
                "average_error_rate": avg_error_rate,
                "peak_hours": peak_hours,
                "trend": trend
            },
            "scaling_prediction": self._generate_traffic_scaling_prediction(avg_requests, peak_requests, trend),
            "capacity_recommendations": self._generate_capacity_recommendations(avg_requests, avg_response_time, avg_error_rate),
            "confidence_score": min(len(metrics_history) / 168.0, 1.0)  # 1 week of hourly data = 100%
        }
        
        return prediction
    
    def _identify_peak_hours(self, metrics_history: List[Dict[str, Any]]) -> List[int]:
        """Identify hours with consistently high traffic"""
        
        hourly_traffic = {}
        
        for metric in metrics_history:
            timestamp = metric.get("timestamp")
            if timestamp:
                try:
                    hour = datetime.fromisoformat(timestamp).hour
                    requests = metric.get("request_count", 0)
                    if hour not in hourly_traffic:
                        hourly_traffic[hour] = []
                    hourly_traffic[hour].append(requests)
                except:
                    continue
        
        if not hourly_traffic:
            return []
        
        # Calculate average for each hour
        hourly_averages = {
            hour: sum(requests) / len(requests)
            for hour, requests in hourly_traffic.items()
        }
        
        # Find hours above 80th percentile
        sorted_hours = sorted(hourly_averages.values())
        if len(sorted_hours) >= 5:
            threshold = sorted_hours[int(len(sorted_hours) * 0.8)]
            peak_hours = [hour for hour, avg in hourly_averages.items() if avg >= threshold]
            return sorted(peak_hours)
        
        return []
    
    def _generate_traffic_scaling_prediction(self, avg_requests: float, peak_requests: float, trend: str) -> Dict[str, Any]:
        """Generate traffic scaling predictions"""
        
        if trend == "increasing" and peak_requests > avg_requests * 1.5:
            return {
                "action": "scale_up_backends",
                "confidence": "high",
                "recommendation": "Traffic trending upward - prepare backend capacity",
                "suggested_increase": "30-50%"
            }
        elif peak_requests > avg_requests * 3.0:
            return {
                "action": "optimize_for_spikes",
                "confidence": "medium",
                "recommendation": "High traffic spikes detected - implement auto-scaling",
                "suggested_approach": "managed_instance_groups"
            }
        elif avg_requests < peak_requests * 0.2:
            return {
                "action": "optimize_for_efficiency",
                "confidence": "medium",
                "recommendation": "Consistent low traffic - consider cost optimization",
                "suggested_approach": "reduce_backend_capacity"
            }
        else:
            return {
                "action": "maintain",
                "confidence": "medium",
                "recommendation": "Traffic patterns appear stable",
                "suggested_approach": "monitor_and_maintain"
            }
    
    def _generate_capacity_recommendations(self, avg_requests: float, avg_response_time: float, avg_error_rate: float) -> List[str]:
        """Generate capacity planning recommendations"""
        
        recommendations = []
        
        if avg_response_time > 1.0:
            recommendations.append("High response times - consider scaling backend capacity")
            recommendations.append("Review backend instance performance and sizing")
        
        if avg_error_rate > 0.05:
            recommendations.append("High error rate - investigate backend health and capacity")
            recommendations.append("Consider implementing circuit breaker patterns")
        
        if avg_requests > 100000:  # 100k requests
            recommendations.append("High traffic volume - ensure adequate backend scaling")
            recommendations.append("Consider implementing request rate limiting")
        
        recommendations.append("Monitor backend service metrics for scaling decisions")
        recommendations.append("Set up Cloud Monitoring alerts for performance thresholds")
        recommendations.append("Implement graceful degradation for high load scenarios")
        
        return recommendations
    
    def generate_security_recommendations(self, lb_data: Dict[str, Any]) -> List[str]:
        """
        Generate security recommendations for load balancer
        """
        
        recommendations = []
        ssl_certificates = lb_data.get("ssl_certificates", [])
        forwarding_rules = lb_data.get("forwarding_rules", [])
        backend_services = lb_data.get("backend_services", [])
        
        # SSL/TLS security
        has_https = any(fr.get("port_range") == "443" for fr in forwarding_rules)
        
        if not has_https:
            recommendations.append("Enable HTTPS for encrypted communication")
            recommendations.append("Implement SSL/TLS termination at the load balancer")
        
        # Certificate management
        for cert in ssl_certificates:
            if cert.get("type") == "SELF_MANAGED":
                recommendations.append("Consider Google-managed certificates for better security")
        
        # Backend security
        for bs in backend_services:
            protocol = bs.get("protocol", "HTTP")
            if protocol == "HTTP" and has_https:
                recommendations.append(f"Backend service {bs.get('name')} using HTTP - consider HTTPS")
        
        # General security recommendations
        recommendations.extend([
            "Implement Cloud Armor for DDoS protection and WAF",
            "Configure security headers (HSTS, CSP, etc.)",
            "Regular security audits and penetration testing",
            "Monitor access logs for suspicious patterns",
            "Implement rate limiting and IP allowlisting where appropriate"
        ])
        
        return recommendations
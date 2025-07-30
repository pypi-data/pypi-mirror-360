"""
AWS Load Balancer Intelligence

Advanced intelligence for AWS Elastic Load Balancing (ALB, NLB, CLB)
providing intelligent traffic distribution, SSL management, and cost optimization.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from .aws_intelligence_base import AWSIntelligenceBase
from .stateless_intelligence import (
    ResourceType, ResourceFingerprint, ChangeImpactAnalysis, 
    ResourceHealth, HealthStatus
)


class AWSLoadBalancerIntelligence(AWSIntelligenceBase):
    """
    AWS Load Balancer Intelligence Engine
    
    Provides intelligent load balancing including:
    - Smart traffic routing optimization
    - SSL certificate management and automation
    - Cost optimization recommendations
    - Health check intelligence
    - Auto-scaling integration
    - Security best practices enforcement
    """
    
    def __init__(self):
        super().__init__(ResourceType.LOAD_BALANCER)
        self.optimization_rules = {
            "utilization_thresholds": {
                "consolidation_threshold": 0.30,  # Consolidate LBs under 30% utilization
                "optimal_range": (0.40, 0.80),
                "scale_threshold": 0.85
            },
            "cost_optimization": {
                "alb_monthly_cost": 22.50,  # Base ALB cost
                "nlb_monthly_cost": 22.50,  # Base NLB cost
                "clb_monthly_cost": 18.00,  # Base CLB cost
                "data_processing_cost_per_gb": 0.008,
                "target_group_cost": 0.50  # Per target group per month
            },
            "ssl_management": {
                "certificate_expiry_warning_days": 30,
                "recommend_acm": True,
                "cipher_suite_recommendations": ["TLSv1.2", "TLSv1.3"]
            }
        }
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing load balancers across ALB, NLB, and CLB"""
        
        # Mock implementation - in production would use boto3
        return {
            "web-alb": {
                "name": "web-alb",
                "arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/web-alb/50dc6c495c0c9188",
                "type": "application",
                "scheme": "internet-facing",
                "state": "active",
                "vpc_id": "vpc-12345678",
                "availability_zones": ["us-east-1a", "us-east-1b"],
                "listeners": [
                    {
                        "port": 80,
                        "protocol": "HTTP",
                        "ssl_policy": None,
                        "certificates": [],
                        "default_actions": [{"type": "redirect", "redirect_config": {"protocol": "HTTPS", "port": "443"}}]
                    },
                    {
                        "port": 443,
                        "protocol": "HTTPS",
                        "ssl_policy": "ELBSecurityPolicy-TLS-1-2-2017-01",
                        "certificates": [{"certificate_arn": "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012"}],
                        "default_actions": [{"type": "forward", "target_group_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/web-tg/50dc6c495c0c9188"}]
                    }
                ],
                "target_groups": [
                    {
                        "name": "web-tg",
                        "arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/web-tg/50dc6c495c0c9188",
                        "protocol": "HTTP",
                        "port": 80,
                        "health_check": {
                            "protocol": "HTTP",
                            "path": "/health",
                            "healthy_threshold": 2,
                            "unhealthy_threshold": 5,
                            "timeout": 5,
                            "interval": 30
                        },
                        "targets": [
                            {"id": "i-1234567890abcdef0", "port": 80, "health": "healthy"},
                            {"id": "i-0987654321fedcba0", "port": 80, "health": "healthy"},
                            {"id": "i-1111222233334444", "port": 80, "health": "unhealthy"}
                        ]
                    }
                ],
                "metrics": {
                    "request_count": 15000,
                    "active_connection_count": 250,
                    "new_connection_count": 500,
                    "target_response_time": 0.150,
                    "http_4xx_count": 45,
                    "http_5xx_count": 12,
                    "data_processed_gb": 125.5
                },
                "security_groups": ["sg-web-alb"],
                "created_time": "2024-01-15T10:30:00Z"
            },
            "api-nlb": {
                "name": "api-nlb",
                "arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/api-nlb/50dc6c495c0c9188",
                "type": "network",
                "scheme": "internal",
                "state": "active",
                "vpc_id": "vpc-12345678",
                "availability_zones": ["us-east-1a", "us-east-1b"],
                "listeners": [
                    {
                        "port": 8080,
                        "protocol": "TCP",
                        "ssl_policy": None,
                        "certificates": [],
                        "default_actions": [{"type": "forward", "target_group_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/api-tg/50dc6c495c0c9188"}]
                    }
                ],
                "target_groups": [
                    {
                        "name": "api-tg",
                        "arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/api-tg/50dc6c495c0c9188",
                        "protocol": "TCP",
                        "port": 8080,
                        "health_check": {
                            "protocol": "TCP",
                            "healthy_threshold": 3,
                            "unhealthy_threshold": 3,
                            "timeout": 10,
                            "interval": 30
                        },
                        "targets": [
                            {"id": "i-5555666677778888", "port": 8080, "health": "healthy"},
                            {"id": "i-9999aaaabbbbcccc", "port": 8080, "health": "healthy"}
                        ]
                    }
                ],
                "metrics": {
                    "active_flow_count": 1500,
                    "new_flow_count": 300,
                    "target_response_time": 0.080,
                    "unhealthy_target_count": 0,
                    "data_processed_gb": 89.2
                }
            },
            "legacy-clb": {
                "name": "legacy-clb",
                "arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/legacy-clb",
                "type": "classic",
                "scheme": "internet-facing",
                "state": "active",
                "vpc_id": "vpc-12345678",
                "availability_zones": ["us-east-1a"],
                "listeners": [
                    {
                        "port": 80,
                        "protocol": "HTTP",
                        "instance_port": 80,
                        "instance_protocol": "HTTP"
                    }
                ],
                "instances": [
                    {"instance_id": "i-oldinstance1234567", "state": "InService"},
                    {"instance_id": "i-oldinstance7654321", "state": "OutOfService"}
                ],
                "health_check": {
                    "target": "HTTP:80/health",
                    "interval": 30,
                    "timeout": 5,
                    "healthy_threshold": 10,
                    "unhealthy_threshold": 2
                },
                "metrics": {
                    "request_count": 2500,
                    "latency": 0.250,
                    "http_4xx_count": 15,
                    "http_5xx_count": 8,
                    "backend_connection_errors": 3
                }
            }
        }
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract load balancer configuration from cloud state"""
        
        return {
            "name": cloud_state.get("name"),
            "type": cloud_state.get("type"),
            "scheme": cloud_state.get("scheme"),
            "vpc_id": cloud_state.get("vpc_id"),
            "availability_zones": cloud_state.get("availability_zones", []),
            "listeners": cloud_state.get("listeners", []),
            "target_groups": cloud_state.get("target_groups", []),
            "security_groups": cloud_state.get("security_groups", []),
            "metrics": cloud_state.get("metrics", {})
        }
    
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """Generate hash for load balancer configuration"""
        
        # Focus on key configuration elements
        key_config = {
            "name": config.get("name"),
            "type": config.get("type"),
            "scheme": config.get("scheme"),
            "listeners": [
                {
                    "port": l.get("port"),
                    "protocol": l.get("protocol"),
                    "ssl_policy": l.get("ssl_policy")
                }
                for l in config.get("listeners", [])
            ],
            "target_groups": [
                {
                    "name": tg.get("name"),
                    "protocol": tg.get("protocol"),
                    "port": tg.get("port")
                }
                for tg in config.get("target_groups", [])
            ]
        }
        
        return str(hash(json.dumps(key_config, sort_keys=True)))
    
    def analyze_load_balancer_optimization(self, lb_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze load balancer for optimization opportunities
        """
        
        optimization_analysis = {
            "load_balancer_name": lb_data.get("name"),
            "type": lb_data.get("type"),
            "current_cost_estimate": 0.0,
            "optimized_cost_estimate": 0.0,
            "potential_savings": 0.0,
            "recommendations": [],
            "ssl_recommendations": [],
            "health_check_recommendations": [],
            "consolidation_opportunities": [],
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
        
        # Modernization recommendations
        if lb_data.get("type") == "classic":
            modernization = self._analyze_clb_modernization(lb_data)
            optimization_analysis["modernization_recommendations"] = modernization
        
        # Performance recommendations
        performance_analysis = self._analyze_performance_optimization(lb_data)
        optimization_analysis["recommendations"].extend(performance_analysis)
        
        return optimization_analysis
    
    def _analyze_cost_optimization(self, lb_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost optimization opportunities"""
        
        lb_type = lb_data.get("type")
        metrics = lb_data.get("metrics", {})
        
        # Calculate current costs
        if lb_type == "application":
            base_cost = self.optimization_rules["cost_optimization"]["alb_monthly_cost"]
        elif lb_type == "network":
            base_cost = self.optimization_rules["cost_optimization"]["nlb_monthly_cost"]
        else:  # classic
            base_cost = self.optimization_rules["cost_optimization"]["clb_monthly_cost"]
        
        data_processed = metrics.get("data_processed_gb", 0)
        data_cost = data_processed * self.optimization_rules["cost_optimization"]["data_processing_cost_per_gb"]
        
        target_groups = lb_data.get("target_groups", [])
        target_group_cost = len(target_groups) * self.optimization_rules["cost_optimization"]["target_group_cost"]
        
        current_monthly_cost = base_cost + data_cost + target_group_cost
        
        # Analyze utilization
        request_count = metrics.get("request_count", 0)
        utilization_score = min(request_count / 10000, 1.0)  # Normalize to 10k requests as 100%
        
        optimized_cost = current_monthly_cost
        recommendations = []
        
        if utilization_score < self.optimization_rules["utilization_thresholds"]["consolidation_threshold"]:
            recommendations.append(f"Low utilization detected ({utilization_score:.1%}) - consider consolidation")
            # Potential savings through consolidation
            optimized_cost = current_monthly_cost * 0.7
        
        # Target group optimization
        if len(target_groups) > 3:
            recommendations.append("Consider consolidating target groups where possible")
            potential_tg_savings = min(2, len(target_groups) - 3) * self.optimization_rules["cost_optimization"]["target_group_cost"]
            optimized_cost -= potential_tg_savings
        
        return {
            "current_cost_estimate": current_monthly_cost,
            "optimized_cost_estimate": optimized_cost,
            "potential_savings": current_monthly_cost - optimized_cost,
            "utilization_score": utilization_score,
            "cost_breakdown": {
                "base_cost": base_cost,
                "data_processing": data_cost,
                "target_groups": target_group_cost
            },
            "recommendations": recommendations
        }
    
    def _analyze_ssl_configuration(self, lb_data: Dict[str, Any]) -> List[str]:
        """Analyze SSL/TLS configuration and provide recommendations"""
        
        recommendations = []
        listeners = lb_data.get("listeners", [])
        
        https_listeners = [l for l in listeners if l.get("protocol") == "HTTPS"]
        http_listeners = [l for l in listeners if l.get("protocol") == "HTTP"]
        
        # Check for HTTP listeners without HTTPS redirect
        for http_listener in http_listeners:
            default_actions = http_listener.get("default_actions", [])
            has_redirect = any(action.get("type") == "redirect" for action in default_actions)
            
            if not has_redirect:
                recommendations.append("Add HTTPS redirect for HTTP listeners to improve security")
        
        # Analyze HTTPS listeners
        for https_listener in https_listeners:
            ssl_policy = https_listener.get("ssl_policy")
            certificates = https_listener.get("certificates", [])
            
            # SSL policy recommendations
            if ssl_policy and "TLS-1-0" in ssl_policy:
                recommendations.append("Upgrade SSL policy to support TLS 1.2+ only for better security")
            elif not ssl_policy or "2017" in ssl_policy:
                recommendations.append("Consider updating to latest SSL security policy")
            
            # Certificate recommendations
            if not certificates:
                recommendations.append("HTTPS listener missing SSL certificate")
            else:
                recommendations.append("Ensure SSL certificates are managed through AWS Certificate Manager (ACM)")
        
        # General SSL recommendations
        if https_listeners:
            recommendations.append("Enable HTTP Strict Transport Security (HSTS) headers")
            recommendations.append("Consider implementing certificate transparency monitoring")
        
        if not https_listeners and http_listeners:
            recommendations.append("Add HTTPS listener for improved security")
        
        return recommendations
    
    def _analyze_health_checks(self, lb_data: Dict[str, Any]) -> List[str]:
        """Analyze health check configuration"""
        
        recommendations = []
        lb_type = lb_data.get("type")
        
        if lb_type == "classic":
            health_check = lb_data.get("health_check", {})
            if health_check:
                interval = health_check.get("interval", 30)
                timeout = health_check.get("timeout", 5)
                healthy_threshold = health_check.get("healthy_threshold", 10)
                unhealthy_threshold = health_check.get("unhealthy_threshold", 2)
                
                if interval > 30:
                    recommendations.append("Consider reducing health check interval for faster failure detection")
                
                if healthy_threshold > 5:
                    recommendations.append("Reduce healthy threshold for faster target recovery")
                
                if timeout > 10:
                    recommendations.append("Reduce health check timeout for better responsiveness")
        else:
            # ALB/NLB target groups
            target_groups = lb_data.get("target_groups", [])
            for tg in target_groups:
                health_check = tg.get("health_check", {})
                if health_check:
                    protocol = health_check.get("protocol")
                    path = health_check.get("path")
                    interval = health_check.get("interval", 30)
                    timeout = health_check.get("timeout", 5)
                    
                    if protocol == "HTTP" and not path:
                        recommendations.append(f"Add specific health check path for target group {tg.get('name')}")
                    
                    if protocol == "HTTP" and path == "/":
                        recommendations.append(f"Use dedicated health check endpoint instead of root path for {tg.get('name')}")
                    
                    if interval > 30:
                        recommendations.append(f"Consider reducing health check interval for {tg.get('name')}")
                    
                    # Check target health
                    targets = tg.get("targets", [])
                    unhealthy_targets = [t for t in targets if t.get("health") != "healthy"]
                    if unhealthy_targets:
                        recommendations.append(f"Address {len(unhealthy_targets)} unhealthy targets in {tg.get('name')}")
        
        return recommendations
    
    def _analyze_clb_modernization(self, clb_data: Dict[str, Any]) -> List[str]:
        """Analyze Classic Load Balancer for modernization opportunities"""
        
        recommendations = [
            "Migrate from Classic Load Balancer to Application Load Balancer for better features",
            "ALB provides path-based routing, host-based routing, and WebSocket support",
            "ALB offers better integration with AWS services like WAF and Lambda",
            "Consider Network Load Balancer if you need ultra-high performance and static IP addresses"
        ]
        
        # Analyze current configuration for migration complexity
        listeners = clb_data.get("listeners", [])
        instances = clb_data.get("instances", [])
        
        if len(listeners) == 1 and len(instances) <= 5:
            recommendations.append("Simple migration path available - single listener and few instances")
        else:
            recommendations.append("Complex migration - plan carefully for multiple listeners or many instances")
        
        # Check for SSL
        has_ssl = any(l.get("protocol") in ["HTTPS", "SSL"] for l in listeners)
        if has_ssl:
            recommendations.append("SSL migration: Update certificate configuration for ALB/NLB")
        
        return recommendations
    
    def _analyze_performance_optimization(self, lb_data: Dict[str, Any]) -> List[str]:
        """Analyze performance optimization opportunities"""
        
        recommendations = []
        metrics = lb_data.get("metrics", {})
        lb_type = lb_data.get("type")
        
        # Response time analysis
        response_time = metrics.get("target_response_time", 0)
        if response_time > 1.0:
            recommendations.append("High response time detected - investigate target performance")
        elif response_time > 0.5:
            recommendations.append("Consider optimizing target response time")
        
        # Error rate analysis
        request_count = metrics.get("request_count", 0)
        http_4xx = metrics.get("http_4xx_count", 0)
        http_5xx = metrics.get("http_5xx_count", 0)
        
        if request_count > 0:
            error_rate_4xx = http_4xx / request_count
            error_rate_5xx = http_5xx / request_count
            
            if error_rate_4xx > 0.05:  # 5% 4xx error rate
                recommendations.append("High 4xx error rate - review client requests and routing rules")
            
            if error_rate_5xx > 0.01:  # 1% 5xx error rate
                recommendations.append("High 5xx error rate - investigate target health and capacity")
        
        # Connection analysis for ALB
        if lb_type == "application":
            active_connections = metrics.get("active_connection_count", 0)
            new_connections = metrics.get("new_connection_count", 0)
            
            if active_connections > 10000:
                recommendations.append("High connection count - consider scaling targets or implementing connection pooling")
            
            if new_connections > 1000:
                recommendations.append("High new connection rate - consider keep-alive optimization")
        
        # Flow analysis for NLB
        elif lb_type == "network":
            active_flows = metrics.get("active_flow_count", 0)
            new_flows = metrics.get("new_flow_count", 0)
            
            if active_flows > 50000:
                recommendations.append("High flow count - consider scaling targets")
        
        # Availability zone recommendations
        availability_zones = lb_data.get("availability_zones", [])
        if len(availability_zones) < 2:
            recommendations.append("Enable multiple availability zones for high availability")
        
        return recommendations
    
    def predict_traffic_patterns(self, lb_name: str, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict traffic patterns and scaling needs
        """
        
        if not metrics_history or len(metrics_history) < 24:
            return {"prediction": "insufficient_data", "confidence": 0.0}
        
        # Analyze traffic patterns
        request_counts = [m.get("request_count", 0) for m in metrics_history]
        response_times = [m.get("target_response_time", 0) for m in metrics_history]
        timestamps = [m.get("timestamp") for m in metrics_history if m.get("timestamp")]
        
        # Calculate basic statistics
        avg_requests = sum(request_counts) / len(request_counts)
        peak_requests = max(request_counts)
        avg_response_time = sum(response_times) / len(response_times)
        
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
                "peak_hours": peak_hours,
                "trend": trend
            },
            "scaling_prediction": self._generate_traffic_scaling_prediction(avg_requests, peak_requests, trend),
            "capacity_recommendations": self._generate_capacity_recommendations(avg_requests, peak_requests),
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
                "action": "scale_up_targets",
                "confidence": "high",
                "recommendation": "Traffic trending upward - prepare for increased load",
                "suggested_increase": "30-50%"
            }
        elif peak_requests > avg_requests * 2.0:
            return {
                "action": "optimize_for_spikes",
                "confidence": "medium",
                "recommendation": "High traffic spikes detected - implement auto-scaling",
                "suggested_approach": "predictive_scaling"
            }
        elif avg_requests < peak_requests * 0.3:
            return {
                "action": "optimize_for_efficiency",
                "confidence": "medium",
                "recommendation": "Consistent low traffic - consider cost optimization",
                "suggested_approach": "schedule_based_scaling"
            }
        else:
            return {
                "action": "maintain",
                "confidence": "medium",
                "recommendation": "Traffic patterns appear stable",
                "suggested_approach": "monitor_and_maintain"
            }
    
    def _generate_capacity_recommendations(self, avg_requests: float, peak_requests: float) -> List[str]:
        """Generate capacity planning recommendations"""
        
        recommendations = []
        
        if peak_requests > avg_requests * 3:
            recommendations.append("High traffic variance - implement predictive auto-scaling")
            recommendations.append("Consider using Spot instances for handling traffic spikes")
        
        if avg_requests > 1000:
            recommendations.append("High traffic volume - ensure targets have adequate capacity")
            recommendations.append("Consider implementing connection draining for deployments")
        
        if peak_requests > 10000:
            recommendations.append("Very high peak traffic - consider multiple load balancers")
            recommendations.append("Implement CDN for static content to reduce load balancer traffic")
        
        recommendations.append("Monitor target group metrics for scaling decisions")
        recommendations.append("Set up CloudWatch alarms for traffic threshold monitoring")
        
        return recommendations
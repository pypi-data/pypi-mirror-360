"""
Cloudflare Intelligence Base

Base class for all Cloudflare-specific intelligence implementations.
Provides foundational intelligence capabilities for Cloudflare services.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

from .stateless_intelligence import (
    StatelessIntelligence, ResourceType, ResourceFingerprint, 
    ChangeImpactAnalysis, ResourceHealth, HealthStatus
)


class CloudflareIntelligenceBase(StatelessIntelligence):
    """
    Base class for Cloudflare Intelligence implementations
    
    Provides common functionality for Cloudflare services including:
    - DNS and domain management optimization
    - CDN and caching optimization
    - Security and DDoS protection analysis
    - Performance optimization
    - WAF rule optimization
    - Edge computing recommendations
    """
    
    def __init__(self, resource_type: ResourceType):
        super().__init__(resource_type)
        
        # Cloudflare-specific optimization rules
        self.cf_optimization_rules = {
            "performance_thresholds": {
                "cache_hit_ratio_warning": 0.80,    # 80% cache hit ratio minimum
                "response_time_warning": 0.200,     # 200ms response time
                "bandwidth_utilization": 0.75,      # 75% bandwidth utilization
                "ssl_handshake_time": 0.100         # 100ms SSL handshake time
            },
            "security_requirements": {
                "ssl_required": True,
                "hsts_required": True,
                "waf_recommended": True,
                "ddos_protection_required": True,
                "bot_management_recommended": True
            },
            "caching_optimization": {
                "static_content_ttl": 86400,        # 24 hours for static content
                "dynamic_content_ttl": 300,         # 5 minutes for dynamic content
                "edge_cache_ttl": 7200,             # 2 hours for edge cache
                "browser_cache_ttl": 14400          # 4 hours for browser cache
            },
            "pricing": {
                "free_plan_limits": {
                    "requests_per_month": 10000000,  # 10M requests
                    "bandwidth_gb": 100,              # 100GB bandwidth
                    "page_rules": 3,                  # 3 page rules
                    "dns_queries": 1000000           # 1M DNS queries
                },
                "pro_plan_monthly": 20.00,
                "business_plan_monthly": 200.00,
                "enterprise_plan_monthly": 5000.00,
                "additional_page_rule": 5.00,
                "load_balancer_monthly": 5.00,
                "rate_limiting_monthly": 5.00
            }
        }
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover existing Cloudflare resources
        Override in specific intelligence classes
        """
        raise NotImplementedError("Subclasses must implement _discover_existing_resources")
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract resource configuration from Cloudflare API response
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
    # CLOUDFLARE-SPECIFIC INTELLIGENCE
    # ==========================================
    
    def analyze_cf_performance_optimization(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance optimization opportunities for Cloudflare resources"""
        
        analysis = {
            "performance_score": 0.0,
            "cache_efficiency": {},
            "recommendations": [],
            "optimization_opportunities": []
        }
        
        # Cache performance analysis
        cache_analysis = self._analyze_cache_performance(resource_data)
        analysis.update(cache_analysis)
        
        # CDN optimization
        cdn_analysis = self._analyze_cdn_optimization(resource_data)
        analysis["recommendations"].extend(cdn_analysis)
        
        # Edge optimization
        edge_analysis = self._analyze_edge_optimization(resource_data)
        analysis["recommendations"].extend(edge_analysis)
        
        return analysis
    
    def _analyze_cache_performance(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cache performance and efficiency"""
        
        analytics = resource_data.get("analytics", {})
        cache_hit_ratio = analytics.get("cache_hit_ratio", 0.0)
        bandwidth_saved = analytics.get("bandwidth_saved_gb", 0.0)
        response_time = analytics.get("response_time_avg", 0.0)
        
        performance_score = 100.0
        recommendations = []
        
        # Cache hit ratio analysis
        if cache_hit_ratio < self.cf_optimization_rules["performance_thresholds"]["cache_hit_ratio_warning"]:
            recommendations.append(f"Low cache hit ratio ({cache_hit_ratio:.1%}) - optimize caching rules")
            performance_score -= 20
        
        # Response time analysis
        if response_time > self.cf_optimization_rules["performance_thresholds"]["response_time_warning"]:
            recommendations.append(f"High response time ({response_time:.3f}s) - investigate origin performance")
            performance_score -= 15
        
        # Bandwidth efficiency
        requests_total = analytics.get("requests_total", 0)
        if requests_total > 0:
            bandwidth_efficiency = bandwidth_saved / (requests_total / 1000000)  # GB per million requests
            if bandwidth_efficiency < 10:  # Less than 10GB saved per million requests
                recommendations.append("Low bandwidth efficiency - review caching strategy")
                performance_score -= 10
        
        return {
            "performance_score": max(0.0, performance_score),
            "cache_efficiency": {
                "hit_ratio": cache_hit_ratio,
                "bandwidth_saved_gb": bandwidth_saved,
                "response_time_avg": response_time
            },
            "recommendations": recommendations
        }
    
    def _analyze_cdn_optimization(self, resource_data: Dict[str, Any]) -> List[str]:
        """Analyze CDN configuration for optimization opportunities"""
        
        recommendations = []
        settings = resource_data.get("settings", {})
        
        # Caching level optimization
        caching_level = settings.get("caching_level", "standard")
        if caching_level == "basic":
            recommendations.append("Upgrade caching level from basic to standard or aggressive")
        
        # Browser cache TTL
        browser_cache_ttl = settings.get("browser_cache_ttl", 14400)
        if browser_cache_ttl < self.cf_optimization_rules["caching_optimization"]["browser_cache_ttl"]:
            recommendations.append("Increase browser cache TTL for better performance")
        
        # Always Online
        always_online = settings.get("always_online", False)
        if not always_online:
            recommendations.append("Enable Always Online for better availability during origin downtime")
        
        # Minification
        minification = settings.get("minification", {})
        if not minification.get("html", False):
            recommendations.append("Enable HTML minification for reduced bandwidth")
        if not minification.get("css", False):
            recommendations.append("Enable CSS minification for faster loading")
        if not minification.get("js", False):
            recommendations.append("Enable JavaScript minification for improved performance")
        
        # Image optimization
        polish = settings.get("polish", "off")
        if polish == "off":
            recommendations.append("Enable Polish for automatic image optimization")
        
        return recommendations
    
    def _analyze_edge_optimization(self, resource_data: Dict[str, Any]) -> List[str]:
        """Analyze edge computing optimization opportunities"""
        
        recommendations = []
        
        # Workers analysis
        workers = resource_data.get("workers", [])
        page_rules = resource_data.get("page_rules", [])
        
        if not workers and len(page_rules) > 5:
            recommendations.append("Consider using Cloudflare Workers to replace complex page rules")
        
        # Edge locations
        analytics = resource_data.get("analytics", {})
        top_countries = analytics.get("top_countries", [])
        
        if len(top_countries) > 3:
            recommendations.append("Consider Workers deployment for better geographic performance")
        
        return recommendations
    
    def analyze_cf_security_posture(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security posture for Cloudflare resources"""
        
        security_analysis = {
            "security_score": 0.0,
            "vulnerabilities": [],
            "recommendations": [],
            "threat_intelligence": {}
        }
        
        # Security configuration checks
        security_checks = self._perform_cf_security_checks(resource_data)
        security_analysis.update(security_checks)
        
        # Threat analysis
        threat_analysis = self._analyze_threat_landscape(resource_data)
        security_analysis["threat_intelligence"] = threat_analysis
        
        return security_analysis
    
    def _perform_cf_security_checks(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Cloudflare security configuration checks"""
        
        vulnerabilities = []
        recommendations = []
        security_score = 100.0
        
        settings = resource_data.get("settings", {})
        
        # SSL/TLS configuration
        ssl_mode = settings.get("ssl", "off")
        if ssl_mode == "off":
            vulnerabilities.append("SSL not enabled")
            recommendations.append("Enable SSL encryption (at minimum Flexible SSL)")
            security_score -= 30
        elif ssl_mode == "flexible":
            recommendations.append("Upgrade from Flexible to Full or Full (Strict) SSL")
            security_score -= 10
        
        # HSTS configuration
        hsts = settings.get("security_header", {}).get("strict_transport_security", {})
        if not hsts.get("enabled", False):
            vulnerabilities.append("HSTS not enabled")
            recommendations.append("Enable HTTP Strict Transport Security (HSTS)")
            security_score -= 15
        
        # WAF configuration
        waf = settings.get("waf", {})
        if not waf.get("enabled", False):
            vulnerabilities.append("Web Application Firewall not enabled")
            recommendations.append("Enable Cloudflare WAF for application protection")
            security_score -= 20
        
        # DDoS protection
        ddos_protection = settings.get("ddos_protection", {})
        if not ddos_protection.get("enabled", True):  # Usually enabled by default
            vulnerabilities.append("DDoS protection not optimally configured")
            recommendations.append("Review and optimize DDoS protection settings")
            security_score -= 15
        
        # Bot management
        bot_management = settings.get("bot_management", {})
        if not bot_management.get("enabled", False):
            recommendations.append("Consider enabling Bot Management for advanced protection")
            security_score -= 5
        
        # Rate limiting
        rate_limiting = resource_data.get("rate_limiting_rules", [])
        if not rate_limiting:
            recommendations.append("Implement rate limiting rules for API endpoints")
            security_score -= 10
        
        return {
            "security_score": max(0.0, security_score),
            "vulnerabilities": vulnerabilities,
            "recommendations": recommendations
        }
    
    def _analyze_threat_landscape(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze threat landscape and attack patterns"""
        
        analytics = resource_data.get("analytics", {})
        security_events = analytics.get("security_events", {})
        
        threat_analysis = {
            "total_threats_blocked": security_events.get("threats_blocked", 0),
            "attack_types": security_events.get("attack_types", {}),
            "threat_countries": security_events.get("threat_countries", []),
            "risk_level": "low"
        }
        
        threats_blocked = threat_analysis["total_threats_blocked"]
        
        # Determine risk level based on threat volume
        if threats_blocked > 10000:
            threat_analysis["risk_level"] = "critical"
        elif threats_blocked > 1000:
            threat_analysis["risk_level"] = "high"
        elif threats_blocked > 100:
            threat_analysis["risk_level"] = "medium"
        
        return threat_analysis
    
    def analyze_cf_cost_optimization(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost optimization opportunities for Cloudflare services"""
        
        analysis = {
            "current_plan": "",
            "current_monthly_cost": 0.0,
            "optimized_monthly_cost": 0.0,
            "potential_savings": 0.0,
            "recommendations": [],
            "usage_analysis": {}
        }
        
        # Plan analysis
        plan_analysis = self._analyze_plan_optimization(resource_data)
        analysis.update(plan_analysis)
        
        # Usage efficiency
        usage_analysis = self._analyze_usage_efficiency(resource_data)
        analysis["usage_analysis"] = usage_analysis
        analysis["recommendations"].extend(usage_analysis.get("recommendations", []))
        
        # Add-on optimization
        addon_analysis = self._analyze_addon_optimization(resource_data)
        analysis["recommendations"].extend(addon_analysis)
        
        return analysis
    
    def _analyze_plan_optimization(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Cloudflare plan optimization"""
        
        current_plan = resource_data.get("plan", "free")
        analytics = resource_data.get("analytics", {})
        
        monthly_requests = analytics.get("requests_total", 0)
        monthly_bandwidth_gb = analytics.get("bandwidth_gb", 0)
        
        recommendations = []
        
        # Free plan analysis
        if current_plan == "free":
            free_limits = self.cf_optimization_rules["pricing"]["free_plan_limits"]
            
            if monthly_requests > free_limits["requests_per_month"]:
                recommendations.append("Exceeding free plan request limits - consider Pro plan")
            
            if monthly_bandwidth_gb > free_limits["bandwidth_gb"]:
                recommendations.append("Approaching free plan bandwidth limits - consider Pro plan")
            
            current_cost = 0.0
            optimized_cost = 0.0
            
            # Recommend upgrade if approaching limits
            if (monthly_requests > free_limits["requests_per_month"] * 0.8 or 
                monthly_bandwidth_gb > free_limits["bandwidth_gb"] * 0.8):
                optimized_cost = self.cf_optimization_rules["pricing"]["pro_plan_monthly"]
                recommendations.append("Consider upgrading to Pro plan for better performance and reliability")
        
        elif current_plan == "pro":
            current_cost = self.cf_optimization_rules["pricing"]["pro_plan_monthly"]
            optimized_cost = current_cost
            
            # Check if Business plan features would be beneficial
            security_events = analytics.get("security_events", {}).get("threats_blocked", 0)
            if security_events > 10000:
                recommendations.append("High security threats - consider Business plan for advanced WAF")
        
        elif current_plan == "business":
            current_cost = self.cf_optimization_rules["pricing"]["business_plan_monthly"]
            optimized_cost = current_cost
            
            # Check if Enterprise features are needed
            if monthly_requests > 100000000:  # 100M requests
                recommendations.append("High traffic volume - consider Enterprise plan for dedicated support")
        
        else:  # enterprise
            current_cost = self.cf_optimization_rules["pricing"]["enterprise_plan_monthly"]
            optimized_cost = current_cost
        
        return {
            "current_plan": current_plan,
            "current_monthly_cost": current_cost,
            "optimized_monthly_cost": optimized_cost,
            "potential_savings": current_cost - optimized_cost,
            "recommendations": recommendations
        }
    
    def _analyze_usage_efficiency(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze usage efficiency and optimization opportunities"""
        
        analytics = resource_data.get("analytics", {})
        cache_hit_ratio = analytics.get("cache_hit_ratio", 0.0)
        bandwidth_saved_gb = analytics.get("bandwidth_saved_gb", 0.0)
        
        usage_efficiency = {
            "cache_efficiency": cache_hit_ratio,
            "bandwidth_efficiency": bandwidth_saved_gb,
            "recommendations": []
        }
        
        # Cache efficiency recommendations
        if cache_hit_ratio < 0.80:
            usage_efficiency["recommendations"].append("Improve cache hit ratio to reduce origin server load")
        
        # Bandwidth optimization
        if bandwidth_saved_gb < 10:  # Less than 10GB saved per month
            usage_efficiency["recommendations"].append("Optimize caching to save more bandwidth and reduce costs")
        
        return usage_efficiency
    
    def _analyze_addon_optimization(self, resource_data: Dict[str, Any]) -> List[str]:
        """Analyze add-on service optimization"""
        
        recommendations = []
        
        # Load balancer analysis
        load_balancers = resource_data.get("load_balancers", [])
        if not load_balancers:
            origins = resource_data.get("origins", [])
            if len(origins) > 1:
                recommendations.append("Multiple origins detected - consider Cloudflare Load Balancer")
        
        # Rate limiting analysis
        rate_limiting_rules = resource_data.get("rate_limiting_rules", [])
        analytics = resource_data.get("analytics", {})
        api_requests = analytics.get("api_requests", 0)
        
        if api_requests > 100000 and not rate_limiting_rules:  # 100k API requests
            recommendations.append("High API traffic - consider Rate Limiting add-on")
        
        return recommendations
    
    def generate_cf_performance_recommendations(self, resource_data: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        # Page Rules optimization
        page_rules = resource_data.get("page_rules", [])
        if len(page_rules) > 10:
            recommendations.append("Many Page Rules detected - consider consolidating or using Workers")
        
        # Caching recommendations
        settings = resource_data.get("settings", {})
        caching_level = settings.get("caching_level", "standard")
        
        if caching_level != "aggressive":
            recommendations.append("Consider aggressive caching level for better performance")
        
        # Compression recommendations
        if not settings.get("brotli", False):
            recommendations.append("Enable Brotli compression for better performance")
        
        # HTTP/3 recommendations
        if not settings.get("http3", False):
            recommendations.append("Enable HTTP/3 for improved performance")
        
        # Early Hints
        if not settings.get("early_hints", False):
            recommendations.append("Enable Early Hints for faster page loading")
        
        return recommendations
    
    def get_cf_pricing_estimate(self, resource_config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate pricing estimate for Cloudflare services"""
        
        pricing_estimate = {
            "monthly_cost": 0.0,
            "cost_breakdown": {},
            "cost_factors": []
        }
        
        # Base plan cost
        plan = resource_config.get("plan", "free")
        if plan == "pro":
            base_cost = self.cf_optimization_rules["pricing"]["pro_plan_monthly"]
        elif plan == "business":
            base_cost = self.cf_optimization_rules["pricing"]["business_plan_monthly"]
        elif plan == "enterprise":
            base_cost = self.cf_optimization_rules["pricing"]["enterprise_plan_monthly"]
        else:
            base_cost = 0.0
        
        pricing_estimate["cost_breakdown"]["base_plan"] = base_cost
        pricing_estimate["monthly_cost"] += base_cost
        
        # Add-on costs
        addons = resource_config.get("addons", {})
        
        # Load Balancer
        if addons.get("load_balancer", False):
            lb_cost = self.cf_optimization_rules["pricing"]["load_balancer_monthly"]
            pricing_estimate["cost_breakdown"]["load_balancer"] = lb_cost
            pricing_estimate["monthly_cost"] += lb_cost
        
        # Rate Limiting
        if addons.get("rate_limiting", False):
            rl_cost = self.cf_optimization_rules["pricing"]["rate_limiting_monthly"]
            pricing_estimate["cost_breakdown"]["rate_limiting"] = rl_cost
            pricing_estimate["monthly_cost"] += rl_cost
        
        # Additional Page Rules
        page_rules = resource_config.get("page_rules_count", 0)
        free_page_rules = 3 if plan == "free" else 20  # Pro+ plans get more
        
        if page_rules > free_page_rules:
            additional_rules = page_rules - free_page_rules
            rules_cost = additional_rules * self.cf_optimization_rules["pricing"]["additional_page_rule"]
            pricing_estimate["cost_breakdown"]["additional_page_rules"] = rules_cost
            pricing_estimate["monthly_cost"] += rules_cost
        
        pricing_estimate["cost_factors"] = [
            f"Plan: {plan}",
            f"Page Rules: {page_rules}",
            f"Load Balancer: {addons.get('load_balancer', False)}",
            f"Rate Limiting: {addons.get('rate_limiting', False)}"
        ]
        
        return pricing_estimate
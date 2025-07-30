"""
GCP Load Balancer Complete Implementation

Combines all Load Balancer functionality through multiple inheritance:
- LoadBalancerCore: Core attributes and authentication
- LoadBalancerConfigurationMixin: Chainable configuration methods  
- LoadBalancerLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from typing import Dict, Any, List, Optional
from .load_balancer_core import LoadBalancerCore
from .load_balancer_configuration import LoadBalancerConfigurationMixin
from .load_balancer_lifecycle import LoadBalancerLifecycleMixin


class LoadBalancer(LoadBalancerLifecycleMixin, LoadBalancerConfigurationMixin, LoadBalancerCore):
    """
    Complete GCP Load Balancer implementation for traffic distribution.
    
    This class combines:
    - Load balancer configuration methods (type, scheme, protocol, backends)
    - Load balancer lifecycle management (create, destroy, preview)
    - SSL/TLS and security configuration
    - Health check and traffic distribution settings
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize LoadBalancer instance for traffic distribution"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$40.87/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._load_balancer_type = None
        self._monitoring_enabled = True
        self._auto_scaling_enabled = False
    
    def validate_configuration(self):
        """Validate the current Load Balancer configuration"""
        errors = []
        warnings = []
        
        # Validate load balancer name
        if not self.lb_name:
            errors.append("Load balancer name is required")
        
        # Validate load balancer type
        if not self._is_valid_lb_type(self.lb_type):
            errors.append(f"Invalid load balancer type: {self.lb_type}")
        
        # Validate scheme
        if not self._is_valid_scheme(self.lb_scheme):
            errors.append(f"Invalid load balancer scheme: {self.lb_scheme}")
        
        # Validate protocol
        if not self._is_valid_protocol(self.lb_protocol):
            errors.append(f"Invalid protocol: {self.lb_protocol}")
        
        # Validate region
        if not self._is_valid_region(self.lb_region):
            warnings.append(f"Unusual region: {self.lb_region}")
        
        # Validate backends
        if not self.backends:
            errors.append("At least one backend is required")
        else:
            for i, backend in enumerate(self.backends):
                if not self._validate_backend(backend):
                    errors.append(f"Invalid backend configuration at index {i}")
        
        # Validate session affinity
        if not self._is_valid_session_affinity(self.session_affinity):
            errors.append(f"Invalid session affinity: {self.session_affinity}")
        
        # Validate ports
        if self.http_port < 1 or self.http_port > 65535:
            errors.append("HTTP port must be between 1 and 65535")
        
        if self.https_port < 1 or self.https_port > 65535:
            errors.append("HTTPS port must be between 1 and 65535")
        
        if self.backend_port < 1 or self.backend_port > 65535:
            errors.append("Backend port must be between 1 and 65535")
        
        # Validate timeouts
        if self.timeout_seconds < 1 or self.timeout_seconds > 3600:
            errors.append("Timeout must be between 1 and 3600 seconds")
        
        if self.connection_draining_timeout < 0 or self.connection_draining_timeout > 3600:
            errors.append("Connection draining timeout must be between 0 and 3600 seconds")
        
        # Security warnings
        if self.lb_scheme == "EXTERNAL" and not self.ssl_certificate:
            warnings.append("External load balancer without SSL certificate - consider adding HTTPS")
        
        if self.enable_cdn and not self.ssl_certificate:
            warnings.append("CDN enabled without SSL certificate - HTTPS recommended for CDN")
        
        if not self.health_check_enabled:
            warnings.append("Health checks disabled - consider enabling for better reliability")
        
        # Configuration compatibility warnings
        if self.lb_type == "NETWORK" and self.lb_protocol in ["HTTP", "HTTPS"]:
            warnings.append("Network Load Balancer with HTTP/HTTPS protocol - consider Application Load Balancer")
        
        if self.lb_type == "APPLICATION" and self.lb_protocol in ["TCP", "UDP"]:
            warnings.append("Application Load Balancer with TCP/UDP protocol - consider Network Load Balancer")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_load_balancer_info(self):
        """Get complete information about the Load Balancer"""
        return {
            'lb_name': self.lb_name,
            'lb_type': self.lb_type,
            'lb_type_display': self._get_load_balancer_type_display(),
            'lb_scheme': self.lb_scheme,
            'lb_protocol': self.lb_protocol,
            'lb_region': self.lb_region,
            'http_port': self.http_port,
            'https_port': self.https_port,
            'backend_port': self.backend_port,
            'backend_count': len(self.backends),
            'backends': self.backends,
            'ssl_certificate': self.ssl_certificate,
            'ssl_policy': self.ssl_policy,
            'redirect_http_to_https': self.redirect_http_to_https,
            'health_check_enabled': self.health_check_enabled,
            'health_check_path': self.health_check_path,
            'health_check_protocol': self.health_check_protocol,
            'health_check_port': self.health_check_port,
            'session_affinity': self.session_affinity,
            'connection_draining_timeout': self.connection_draining_timeout,
            'timeout_seconds': self.timeout_seconds,
            'enable_cdn': self.enable_cdn,
            'security_policy': self.security_policy,
            'allowed_regions': self.allowed_regions,
            'labels_count': len(self.lb_labels),
            'custom_headers_count': len(self.custom_headers),
            'url_map': self.url_map,
            'frontend_ip': self.frontend_ip,
            'lb_exists': self.lb_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'load_balancer_type': self._load_balancer_type
        }
    
    def clone(self, new_name: str):
        """Create a copy of this load balancer with a new name"""
        cloned_lb = LoadBalancer(new_name)
        cloned_lb.lb_name = new_name
        cloned_lb.lb_type = self.lb_type
        cloned_lb.lb_scheme = self.lb_scheme
        cloned_lb.lb_protocol = self.lb_protocol
        cloned_lb.lb_region = self.lb_region
        cloned_lb.http_port = self.http_port
        cloned_lb.https_port = self.https_port
        cloned_lb.backend_port = self.backend_port
        cloned_lb.backends = self.backends.copy()
        cloned_lb.ssl_certificate = self.ssl_certificate
        cloned_lb.ssl_policy = self.ssl_policy
        cloned_lb.redirect_http_to_https = self.redirect_http_to_https
        cloned_lb.health_check_enabled = self.health_check_enabled
        cloned_lb.health_check_path = self.health_check_path
        cloned_lb.health_check_protocol = self.health_check_protocol
        cloned_lb.health_check_port = self.health_check_port
        cloned_lb.session_affinity = self.session_affinity
        cloned_lb.connection_draining_timeout = self.connection_draining_timeout
        cloned_lb.timeout_seconds = self.timeout_seconds
        cloned_lb.enable_cdn = self.enable_cdn
        cloned_lb.security_policy = self.security_policy
        cloned_lb.allowed_regions = self.allowed_regions.copy()
        cloned_lb.lb_labels = self.lb_labels.copy()
        cloned_lb.custom_headers = self.custom_headers.copy()
        cloned_lb.url_map = self.url_map
        return cloned_lb
    
    def export_configuration(self):
        """Export load balancer configuration for backup or migration"""
        return {
            'metadata': {
                'lb_name': self.lb_name,
                'lb_type': self.lb_type,
                'lb_scheme': self.lb_scheme,
                'region': self.lb_region,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'lb_type': self.lb_type,
                'lb_scheme': self.lb_scheme,
                'lb_protocol': self.lb_protocol,
                'lb_region': self.lb_region,
                'http_port': self.http_port,
                'https_port': self.https_port,
                'backend_port': self.backend_port,
                'backends': self.backends,
                'ssl_certificate': self.ssl_certificate,
                'ssl_policy': self.ssl_policy,
                'redirect_http_to_https': self.redirect_http_to_https,
                'health_check_enabled': self.health_check_enabled,
                'health_check_path': self.health_check_path,
                'health_check_protocol': self.health_check_protocol,
                'health_check_port': self.health_check_port,
                'session_affinity': self.session_affinity,
                'connection_draining_timeout': self.connection_draining_timeout,
                'timeout_seconds': self.timeout_seconds,
                'enable_cdn': self.enable_cdn,
                'security_policy': self.security_policy,
                'allowed_regions': self.allowed_regions,
                'labels': self.lb_labels,
                'custom_headers': self.custom_headers,
                'url_map': self.url_map,
                'optimization_priority': self._optimization_priority,
                'load_balancer_type': self._load_balancer_type,
                'monitoring_enabled': self._monitoring_enabled,
                'auto_scaling_enabled': self._auto_scaling_enabled
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import load balancer configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.lb_type = config.get('lb_type', 'APPLICATION')
            self.lb_scheme = config.get('lb_scheme', 'EXTERNAL')
            self.lb_protocol = config.get('lb_protocol', 'HTTP')
            self.lb_region = config.get('lb_region', 'us-central1')
            self.http_port = config.get('http_port', 80)
            self.https_port = config.get('https_port', 443)
            self.backend_port = config.get('backend_port', 80)
            self.backends = config.get('backends', [])
            self.ssl_certificate = config.get('ssl_certificate')
            self.ssl_policy = config.get('ssl_policy')
            self.redirect_http_to_https = config.get('redirect_http_to_https', False)
            self.health_check_enabled = config.get('health_check_enabled', True)
            self.health_check_path = config.get('health_check_path', '/')
            self.health_check_protocol = config.get('health_check_protocol', 'HTTP')
            self.health_check_port = config.get('health_check_port')
            self.session_affinity = config.get('session_affinity', 'NONE')
            self.connection_draining_timeout = config.get('connection_draining_timeout', 300)
            self.timeout_seconds = config.get('timeout_seconds', 30)
            self.enable_cdn = config.get('enable_cdn', False)
            self.security_policy = config.get('security_policy')
            self.allowed_regions = config.get('allowed_regions', [])
            self.lb_labels = config.get('labels', {})
            self.custom_headers = config.get('custom_headers', {})
            self.url_map = config.get('url_map')
            self._optimization_priority = config.get('optimization_priority')
            self._load_balancer_type = config.get('load_balancer_type')
            self._monitoring_enabled = config.get('monitoring_enabled', True)
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', False)
        
        return self
    
    def enable_monitoring(self, enabled: bool = True):
        """Enable comprehensive monitoring and alerting"""
        self._monitoring_enabled = enabled
        if enabled:
            print("📊 Comprehensive monitoring enabled")
            print("   💡 Load balancer metrics activated")
            print("   💡 Health check monitoring configured")
            print("   💡 Traffic analytics enabled")
        return self
    
    def enable_auto_scaling(self, enabled: bool = True):
        """Enable automatic backend scaling"""
        self._auto_scaling_enabled = enabled
        if enabled:
            print("📈 Auto-scaling enabled for backends")
            print("   💡 Backend capacity will adjust based on load")
        return self
    
    def add_backend_group(self, group_name: str, instances: List[str], zone: str = None):
        """Add multiple instances as a backend group"""
        zone = zone or f"{self.lb_region}-a"
        
        for instance in instances:
            self.instance_backend(instance, zone)
        
        print(f"🖥️  Added {len(instances)} instances from group '{group_name}' to load balancer")
        return self
    
    def remove_backend(self, backend_name: str):
        """Remove a backend from the load balancer"""
        self.backends = [b for b in self.backends if b.get('name') != backend_name]
        print(f"🗑️  Removed backend '{backend_name}' from load balancer")
        return self
    
    def get_backend_health(self):
        """Get health status of all backends"""
        if not self.load_balancer_manager:
            return {"error": "Load balancer manager not available"}
        
        try:
            health_status = self.load_balancer_manager.get_backend_health(self.lb_name)
            return {
                "lb_name": self.lb_name,
                "backend_count": len(self.backends),
                "health_status": health_status,
                "healthy_backends": len([b for b in health_status if b.get('status') == 'HEALTHY']),
                "unhealthy_backends": len([b for b in health_status if b.get('status') == 'UNHEALTHY'])
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_traffic_stats(self):
        """Get traffic statistics for the load balancer"""
        if not self.load_balancer_manager:
            return {"error": "Load balancer manager not available"}
        
        try:
            stats = self.load_balancer_manager.get_traffic_stats(self.lb_name)
            return {
                "lb_name": self.lb_name,
                "requests_per_second": stats.get("rps", 0),
                "total_requests": stats.get("total_requests", 0),
                "error_rate": stats.get("error_rate", 0),
                "avg_response_time": stats.get("avg_response_time", 0),
                "data_transferred": stats.get("data_transferred", 0),
                "period": stats.get("period", "24h")
            }
        except Exception as e:
            return {"error": str(e)}


# Convenience functions for creating LoadBalancer instances
def create_load_balancer(name: str) -> LoadBalancer:
    """
    Create a new LoadBalancer instance.
    
    Args:
        name: Load balancer name
        
    Returns:
        LoadBalancer instance
    """
    return LoadBalancer(name)

def create_web_load_balancer(name: str) -> LoadBalancer:
    """Create a load balancer optimized for web applications"""
    lb = LoadBalancer(name)
    lb.web_lb().optimize_for("performance")
    return lb

def create_api_load_balancer(name: str) -> LoadBalancer:
    """Create a load balancer optimized for API services"""
    lb = LoadBalancer(name)
    lb.api_lb().optimize_for("performance")
    return lb

def create_internal_load_balancer(name: str) -> LoadBalancer:
    """Create a load balancer for internal services"""
    lb = LoadBalancer(name)
    lb.internal_lb().optimize_for("cost")
    return lb

def create_production_load_balancer(name: str) -> LoadBalancer:
    """Create a load balancer for production workloads"""
    lb = LoadBalancer(name)
    lb.production_lb().optimize_for("reliability")
    return lb

def create_development_load_balancer(name: str) -> LoadBalancer:
    """Create a load balancer for development environments"""
    lb = LoadBalancer(name)
    lb.development_lb().optimize_for("cost")
    return lb
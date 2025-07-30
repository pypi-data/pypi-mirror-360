"""
GCP Load Balancer Configuration Mixin

Chainable configuration methods for Google Cloud Load Balancers.
Provides Rails-like method chaining for fluent load balancer configuration.
"""

from typing import Dict, Any, List, Optional


class LoadBalancerConfigurationMixin:
    """
    Mixin for Load Balancer configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Load balancer type and scheme selection
    - Frontend and backend configuration
    - SSL/TLS and security settings
    - Health check configuration
    - Traffic distribution settings
    """
    
    def lb_type(self, load_balancer_type: str):
        """Set load balancer type (APPLICATION, NETWORK, INTERNAL, INTERNAL_MANAGED)"""
        if not self._is_valid_lb_type(load_balancer_type):
            print(f"⚠️  Warning: Invalid load balancer type '{load_balancer_type}'")
        self.lb_type = load_balancer_type
        return self
        
    def scheme(self, scheme_type: str):
        """Set load balancer scheme (EXTERNAL, INTERNAL, INTERNAL_MANAGED)"""
        if not self._is_valid_scheme(scheme_type):
            print(f"⚠️  Warning: Invalid scheme '{scheme_type}'")
        self.lb_scheme = scheme_type
        return self
        
    def protocol(self, protocol_type: str):
        """Set load balancer protocol (HTTP, HTTPS, TCP, UDP, SSL)"""
        if not self._is_valid_protocol(protocol_type):
            print(f"⚠️  Warning: Invalid protocol '{protocol_type}'")
        self.lb_protocol = protocol_type
        return self
        
    def region(self, region_name: str):
        """Set load balancer region"""
        if not self._is_valid_region(region_name):
            print(f"⚠️  Warning: Unusual region '{region_name}' - verify this is correct")
        self.lb_region = region_name
        return self
        
    # Load balancer type convenience methods
    def application(self):
        """Configure as Application Load Balancer (HTTP/HTTPS) - Rails convention"""
        self.lb_type = "APPLICATION"
        self.lb_protocol = "HTTP"
        return self
        
    def network(self):
        """Configure as Network Load Balancer (TCP/UDP) - Rails convention"""
        self.lb_type = "NETWORK"
        self.lb_protocol = "TCP"
        return self
        
    def internal(self):
        """Configure as Internal Load Balancer - Rails convention"""
        self.lb_type = "INTERNAL"
        self.lb_scheme = "INTERNAL"
        return self
        
    def internal_managed(self):
        """Configure as Internal Managed Load Balancer - Rails convention"""
        self.lb_type = "INTERNAL_MANAGED"
        self.lb_scheme = "INTERNAL_MANAGED"
        return self
        
    # Scheme convenience methods
    def external(self):
        """Configure as external-facing load balancer - Rails convention"""
        self.lb_scheme = "EXTERNAL"
        return self
        
    def private(self):
        """Configure as internal/private load balancer - Rails convention"""
        self.lb_scheme = "INTERNAL"
        return self
        
    # Protocol convenience methods
    def http(self, port: int = 80):
        """Configure HTTP protocol - Rails convention"""
        self.lb_protocol = "HTTP"
        self.http_port = port
        return self
        
    def https(self, port: int = 443):
        """Configure HTTPS protocol - Rails convention"""
        self.lb_protocol = "HTTPS"
        self.https_port = port
        return self
        
    def tcp(self, port: int = 80):
        """Configure TCP protocol - Rails convention"""
        self.lb_protocol = "TCP"
        self.backend_port = port
        return self
        
    def udp(self, port: int = 80):
        """Configure UDP protocol - Rails convention"""
        self.lb_protocol = "UDP"
        self.backend_port = port
        return self
        
    # Frontend configuration
    def frontend_ip(self, ip_address: str):
        """Set static frontend IP address"""
        self.frontend_ip = ip_address
        return self
        
    def ephemeral_ip(self):
        """Use ephemeral (dynamic) IP address - Rails convention"""
        self.frontend_ip = None
        return self
        
    def ports(self, http_port: int = 80, https_port: int = 443):
        """Configure frontend ports"""
        self.http_port = http_port
        self.https_port = https_port
        return self
        
    def backend_port(self, port: int):
        """Set backend port for instances"""
        self.backend_port = port
        return self
        
    # Backend configuration
    def backend(self, backend_config: Dict[str, Any]):
        """Add backend configuration"""
        if self._validate_backend(backend_config):
            self.backends.append(backend_config)
        else:
            print(f"⚠️  Warning: Invalid backend configuration: {backend_config}")
        return self
        
    def instance_backend(self, instance_name: str, zone: str, port: int = None):
        """Add instance as backend - Rails convention"""
        backend = {
            "name": instance_name,
            "type": "instance",
            "zone": zone,
            "port": port or self.backend_port
        }
        return self.backend(backend)
        
    def instance_group_backend(self, group_name: str, zone: str, port: int = None):
        """Add instance group as backend - Rails convention"""
        backend = {
            "name": group_name,
            "type": "instance_group",
            "zone": zone,
            "port": port or self.backend_port
        }
        return self.backend(backend)
        
    def function_backend(self, function_name: str, region: str = None):
        """Add Cloud Function as backend - Rails convention"""
        backend = {
            "name": function_name,
            "type": "function",
            "region": region or self.lb_region
        }
        return self.backend(backend)
        
    # SSL/TLS configuration
    def ssl_certificate(self, cert_name: str):
        """Set SSL certificate for HTTPS"""
        self.ssl_certificate = cert_name
        return self
        
    def ssl_policy(self, policy_name: str):
        """Set SSL policy for security configuration"""
        self.ssl_policy = policy_name
        return self
        
    def redirect_http_to_https(self, enabled: bool = True):
        """Enable HTTP to HTTPS redirect"""
        self.redirect_http_to_https = enabled
        return self
        
    def no_ssl_redirect(self):
        """Disable HTTP to HTTPS redirect - Rails convenience"""
        return self.redirect_http_to_https(False)
        
    # Health check configuration
    def health_check(self, path: str = "/", protocol: str = "HTTP", port: int = None):
        """Configure health check settings"""
        self.health_check_enabled = True
        self.health_check_path = path
        self.health_check_protocol = protocol
        self.health_check_port = port
        return self
        
    def health_check_port(self, port: int):
        """Set health check port"""
        self.health_check_port = port
        return self
        
    def no_health_check(self):
        """Disable health checks - Rails convenience"""
        self.health_check_enabled = False
        return self
        
    # Traffic distribution and session affinity
    def session_affinity(self, affinity_type: str):
        """Set session affinity type"""
        if not self._is_valid_session_affinity(affinity_type):
            print(f"⚠️  Warning: Invalid session affinity type '{affinity_type}'")
        self.session_affinity = affinity_type
        return self
        
    def client_ip_affinity(self):
        """Use client IP-based session affinity - Rails convention"""
        return self.session_affinity("CLIENT_IP")
        
    def cookie_affinity(self):
        """Use cookie-based session affinity - Rails convention"""
        return self.session_affinity("GENERATED_COOKIE")
        
    def no_affinity(self):
        """Disable session affinity - Rails convention"""
        return self.session_affinity("NONE")
        
    def connection_draining(self, timeout_seconds: int = 300):
        """Set connection draining timeout"""
        self.connection_draining_timeout = timeout_seconds
        return self
        
    def timeout(self, seconds: int):
        """Set request timeout"""
        self.timeout_seconds = seconds
        return self
        
    # Security and access control
    def enable_cdn(self, enabled: bool = True):
        """Enable Cloud CDN for caching"""
        self.enable_cdn = enabled
        return self
        
    def cdn(self):
        """Enable Cloud CDN - Rails convenience"""
        return self.enable_cdn(True)
        
    def no_cdn(self):
        """Disable Cloud CDN - Rails convenience"""
        return self.enable_cdn(False)
        
    def security_policy(self, policy_name: str):
        """Set Cloud Armor security policy"""
        self.security_policy = policy_name
        return self
        
    def allowed_regions(self, regions: List[str]):
        """Set allowed regions for geo-restriction"""
        self.allowed_regions = regions
        return self
        
    def allow_region(self, region: str):
        """Add single allowed region - Rails convenience"""
        if region not in self.allowed_regions:
            self.allowed_regions.append(region)
        return self
        
    # Advanced configuration
    def labels(self, labels: Dict[str, str]):
        """Add labels for organization and billing"""
        self.lb_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.lb_labels[key] = value
        return self
        
    def custom_header(self, name: str, value: str):
        """Add custom header to backend requests"""
        self.custom_headers[name] = value
        return self
        
    def custom_headers(self, headers: Dict[str, str]):
        """Add multiple custom headers"""
        self.custom_headers.update(headers)
        return self
        
    def url_map(self, map_name: str):
        """Set URL map for path-based routing"""
        self.url_map = map_name
        return self
        
    # Rails-like environment configurations
    def development_lb(self):
        """Configure for development environment - Rails convention"""
        return (self.application()
                .external()
                .http(8080)
                .health_check("/health")
                .no_ssl_redirect()
                .no_cdn()
                .label("environment", "development"))
                
    def staging_lb(self):
        """Configure for staging environment - Rails convention"""
        return (self.application()
                .external()
                .http(80)
                .https(443)
                .health_check("/health")
                .redirect_http_to_https()
                .no_cdn()
                .label("environment", "staging"))
                
    def production_lb(self):
        """Configure for production environment - Rails convention"""
        return (self.application()
                .external()
                .http(80)
                .https(443)
                .health_check("/health")
                .redirect_http_to_https()
                .cdn()
                .connection_draining(300)
                .timeout(30)
                .label("environment", "production"))
                
    def internal_lb(self):
        """Configure for internal services - Rails convention"""
        return (self.application()
                .internal()
                .http(80)
                .health_check("/health")
                .no_ssl_redirect()
                .no_cdn()
                .label("type", "internal"))
                
    def api_lb(self):
        """Configure for API services - Rails convention"""
        return (self.application()
                .external()
                .https(443)
                .health_check("/api/health")
                .timeout(60)
                .no_affinity()
                .label("service", "api"))
                
    def web_lb(self):
        """Configure for web applications - Rails convention"""
        return (self.application()
                .external()
                .http(80)
                .https(443)
                .health_check("/")
                .redirect_http_to_https()
                .cdn()
                .cookie_affinity()
                .label("service", "web"))
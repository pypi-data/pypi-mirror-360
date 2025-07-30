"""
DigitalOcean Load Balancer Complete Implementation

Complete DigitalOcean Load Balancer implementation with modular architecture.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .base_resource import BaseDigitalOceanResource


class LoadBalancer(BaseDigitalOceanResource):
    """
    Complete DigitalOcean Load Balancer implementation.
    
    Features:
    - Rails-like method chaining for fluent load balancer configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Complete load balancing solution (HTTP/HTTPS/TCP)
    - SSL termination and certificate management
    - Health checks and backend management
    - Sticky sessions and load balancing algorithms
    - Common load balancer patterns (web app, API, microservices)
    - Environment-specific configurations (development, staging, production)
    
    Example:
        # Simple web application load balancer
        lb = LoadBalancer("web-lb")
        lb.http().sticky_sessions().region("nyc3")
        lb.add_droplet_tag("web-server")
        lb.create()
        
        # HTTPS load balancer with SSL termination
        lb = LoadBalancer("api-lb")
        lb.https().ssl_certificate("cert-id")
        lb.health_check("/health").sticky_sessions()
        lb.add_droplet_tag("api-server")
        lb.create()
        
        # TCP load balancer for database connections
        lb = LoadBalancer("db-lb")
        lb.tcp(5432).algorithm("least_connections")
        lb.add_droplet_ids([123456, 789012])
        lb.create()
        
        # Production load balancer with advanced features
        lb = LoadBalancer("prod-lb")
        lb.https().redirect_http_to_https()
        lb.ssl_certificate("cert-id").sticky_sessions()
        lb.health_check("/health", interval=30, timeout=10)
        lb.algorithm("round_robin").region("nyc3")
        lb.vpc("vpc-uuid").firewall_rules(["web-traffic"])
        lb.monitoring().tags(["production", "web"])
        lb.create()
        
        # Microservices load balancer
        lb = LoadBalancer("microservices-lb")
        lb.http().algorithm("least_connections")
        lb.forwarding_rule(80, 8080, "http")
        lb.forwarding_rule(443, 8443, "https")
        lb.health_check("/actuator/health")
        lb.add_droplet_tag("microservice")
        lb.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize DigitalOcean Load Balancer with load balancer name.
        
        Args:
            name: Load balancer name
        """
        super().__init__(name)
        
        # Core load balancer attributes
        self.lb_name = name
        self.lb_description = f"DigitalOcean Load Balancer: {name}"
        
        # Load balancer configuration
        self.algorithm = "round_robin"  # round_robin, least_connections, ip_hash
        self.region = "nyc3"
        self.vpc_uuid = None
        self.size = "lb-small"  # lb-small, lb-medium, lb-large
        
        # Forwarding rules
        self.forwarding_rules = []
        self.default_forwarding_rule = None
        
        # Health checks
        self.health_check_enabled = True
        self.health_check_config = {
            "protocol": "http",
            "port": 80,
            "path": "/",
            "check_interval_seconds": 10,
            "response_timeout_seconds": 5,
            "unhealthy_threshold": 3,
            "healthy_threshold": 2
        }
        
        # Sticky sessions
        self.sticky_sessions_enabled = False
        self.sticky_sessions_config = {
            "type": "cookies",
            "cookie_name": "lb",
            "cookie_ttl_seconds": 3600
        }
        
        # SSL/TLS configuration
        self.ssl_termination = False
        self.certificate_id = None
        self.redirect_http_to_https = False
        self.ssl_protocols = ["TLSv1.2", "TLSv1.3"]
        
        # Backend configuration
        self.droplet_ids = []
        self.droplet_tags = []
        
        # Firewall and security
        self.firewall_rules = []
        self.enable_proxy_protocol = False
        self.enable_backend_keepalive = True
        
        # Monitoring and logging
        self.monitoring_enabled = True
        self.access_logs_enabled = False
        self.enable_http2 = True
        
        # Labels and metadata
        self.lb_tags = []
        self.lb_labels = {}
        self.lb_annotations = {}
        
        # State tracking
        self.lb_exists = False
        self.lb_created = False
        self.lb_status = None
        self.lb_ip = None
        
        # Cost tracking
        self.estimated_monthly_cost = "$12.00/month"
        
        # Client references
        self.lb_manager = None
        
    def _initialize_managers(self):
        """Initialize Load Balancer-specific managers"""
        self.lb_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            from ..digitalocean_managers.load_balancer_manager import LoadBalancerManager
            self.lb_manager = LoadBalancerManager(self.do_client)
                
        except Exception as e:
            print(f"⚠️  Load Balancer manager setup note: {str(e)}")
    
    # Protocol configuration methods
    def http(self, port: int = 80):
        """Configure HTTP load balancing"""
        self.default_forwarding_rule = {
            "entry_protocol": "http",
            "entry_port": port,
            "target_protocol": "http",
            "target_port": port
        }
        self.health_check_config["protocol"] = "http"
        self.health_check_config["port"] = port
        return self
    
    def https(self, port: int = 443):
        """Configure HTTPS load balancing"""
        self.default_forwarding_rule = {
            "entry_protocol": "https",
            "entry_port": port,
            "target_protocol": "http",
            "target_port": 80
        }
        self.ssl_termination = True
        self.health_check_config["protocol"] = "http"
        self.health_check_config["port"] = 80
        return self
    
    def tcp(self, port: int):
        """Configure TCP load balancing"""
        self.default_forwarding_rule = {
            "entry_protocol": "tcp",
            "entry_port": port,
            "target_protocol": "tcp",
            "target_port": port
        }
        self.health_check_config["protocol"] = "tcp"
        self.health_check_config["port"] = port
        return self
    
    def udp(self, port: int):
        """Configure UDP load balancing"""
        self.default_forwarding_rule = {
            "entry_protocol": "udp",
            "entry_port": port,
            "target_protocol": "udp",
            "target_port": port
        }
        # UDP doesn't support health checks
        self.health_check_enabled = False
        return self
    
    # Forwarding rules configuration
    def forwarding_rule(self, entry_port: int, target_port: int, protocol: str = "http"):
        """Add custom forwarding rule"""
        rule = {
            "entry_protocol": protocol,
            "entry_port": entry_port,
            "target_protocol": protocol,
            "target_port": target_port
        }
        self.forwarding_rules.append(rule)
        return self
    
    def forwarding_rule_advanced(self, entry_protocol: str, entry_port: int, 
                                target_protocol: str, target_port: int):
        """Add advanced forwarding rule with different protocols"""
        rule = {
            "entry_protocol": entry_protocol,
            "entry_port": entry_port,
            "target_protocol": target_protocol,
            "target_port": target_port
        }
        self.forwarding_rules.append(rule)
        return self
    
    # Load balancing algorithm
    def algorithm(self, algo: str):
        """Set load balancing algorithm"""
        valid_algorithms = ["round_robin", "least_connections", "ip_hash"]
        if algo not in valid_algorithms:
            raise ValueError(f"Invalid algorithm. Must be one of: {valid_algorithms}")
        self.algorithm = algo
        return self
    
    def round_robin(self):
        """Use round robin algorithm"""
        return self.algorithm("round_robin")
    
    def least_connections(self):
        """Use least connections algorithm"""
        return self.algorithm("least_connections")
    
    def ip_hash(self):
        """Use IP hash algorithm"""
        return self.algorithm("ip_hash")
    
    # Health check configuration
    def health_check(self, path: str = "/", protocol: str = "http", port: int = 80,
                    interval: int = 10, timeout: int = 5, 
                    unhealthy_threshold: int = 3, healthy_threshold: int = 2):
        """Configure health check"""
        self.health_check_enabled = True
        self.health_check_config = {
            "protocol": protocol,
            "port": port,
            "path": path,
            "check_interval_seconds": interval,
            "response_timeout_seconds": timeout,
            "unhealthy_threshold": unhealthy_threshold,
            "healthy_threshold": healthy_threshold
        }
        return self
    
    def disable_health_check(self):
        """Disable health checks"""
        self.health_check_enabled = False
        return self
    
    # Sticky sessions configuration
    def sticky_sessions(self, cookie_name: str = "lb", ttl: int = 3600):
        """Enable sticky sessions"""
        self.sticky_sessions_enabled = True
        self.sticky_sessions_config = {
            "type": "cookies",
            "cookie_name": cookie_name,
            "cookie_ttl_seconds": ttl
        }
        return self
    
    def disable_sticky_sessions(self):
        """Disable sticky sessions"""
        self.sticky_sessions_enabled = False
        return self
    
    # SSL/TLS configuration
    def ssl_certificate(self, cert_id: str):
        """Configure SSL certificate"""
        self.certificate_id = cert_id
        self.ssl_termination = True
        return self
    
    def redirect_http_to_https(self, enabled: bool = True):
        """Enable HTTP to HTTPS redirect"""
        self.redirect_http_to_https = enabled
        return self
    
    def ssl_protocols(self, protocols: List[str]):
        """Set SSL/TLS protocols"""
        valid_protocols = ["TLSv1.0", "TLSv1.1", "TLSv1.2", "TLSv1.3"]
        for protocol in protocols:
            if protocol not in valid_protocols:
                raise ValueError(f"Invalid SSL protocol: {protocol}")
        self.ssl_protocols = protocols
        return self
    
    # Backend configuration
    def add_droplet_ids(self, droplet_ids: List[int]):
        """Add backend droplet IDs"""
        self.droplet_ids.extend(droplet_ids)
        return self
    
    def add_droplet_id(self, droplet_id: int):
        """Add single backend droplet ID"""
        if droplet_id not in self.droplet_ids:
            self.droplet_ids.append(droplet_id)
        return self
    
    def add_droplet_tag(self, tag: str):
        """Add backend droplets by tag"""
        if tag not in self.droplet_tags:
            self.droplet_tags.append(tag)
        return self
    
    def add_droplet_tags(self, tags: List[str]):
        """Add backend droplets by multiple tags"""
        for tag in tags:
            if tag not in self.droplet_tags:
                self.droplet_tags.append(tag)
        return self
    
    # Network and security configuration
    def region(self, region: str):
        """Set load balancer region"""
        self.region = region
        return self
    
    def vpc(self, vpc_uuid: str):
        """Place load balancer in VPC"""
        self.vpc_uuid = vpc_uuid
        return self
    
    def size(self, size: str):
        """Set load balancer size"""
        valid_sizes = ["lb-small", "lb-medium", "lb-large"]
        if size not in valid_sizes:
            raise ValueError(f"Invalid size. Must be one of: {valid_sizes}")
        self.size = size
        return self
    
    def firewall_rules(self, rules: List[str]):
        """Add firewall rules"""
        self.firewall_rules = rules
        return self
    
    def proxy_protocol(self, enabled: bool = True):
        """Enable proxy protocol"""
        self.enable_proxy_protocol = enabled
        return self
    
    def backend_keepalive(self, enabled: bool = True):
        """Enable backend keepalive"""
        self.enable_backend_keepalive = enabled
        return self
    
    # Monitoring and features
    def monitoring(self, enabled: bool = True):
        """Enable monitoring"""
        self.monitoring_enabled = enabled
        return self
    
    def access_logs(self, enabled: bool = True):
        """Enable access logs"""
        self.access_logs_enabled = enabled
        return self
    
    def http2(self, enabled: bool = True):
        """Enable HTTP/2"""
        self.enable_http2 = enabled
        return self
    
    # Labels and metadata
    def tags(self, tags: List[str]):
        """Add tags to the load balancer"""
        self.lb_tags = tags
        return self
    
    def tag(self, tag: str):
        """Add a single tag"""
        if tag not in self.lb_tags:
            self.lb_tags.append(tag)
        return self
    
    def label(self, key: str, value: str):
        """Add a label"""
        self.lb_labels[key] = value
        return self
    
    # Rails-like convenience methods
    def development(self):
        """Configure for development environment"""
        return (self.size("lb-small")
                .health_check("/", interval=30)
                .label("environment", "development")
                .tag("development"))
    
    def staging(self):
        """Configure for staging environment"""
        return (self.size("lb-medium")
                .health_check("/health", interval=20)
                .monitoring(True)
                .label("environment", "staging")
                .tag("staging"))
    
    def production(self):
        """Configure for production environment"""
        return (self.size("lb-large")
                .health_check("/health", interval=10, timeout=5)
                .monitoring(True)
                .access_logs(True)
                .backend_keepalive(True)
                .label("environment", "production")
                .tag("production"))
    
    # Application-specific patterns
    def web_app_lb(self):
        """Configure for web application"""
        return (self.http()
                .sticky_sessions()
                .health_check("/")
                .label("purpose", "web-app")
                .tag("web-application"))
    
    def api_lb(self):
        """Configure for API load balancing"""
        return (self.http()
                .health_check("/health")
                .algorithm("least_connections")
                .label("purpose", "api")
                .tag("api"))
    
    def microservices_lb(self):
        """Configure for microservices"""
        return (self.http()
                .health_check("/actuator/health")
                .algorithm("least_connections")
                .monitoring(True)
                .label("purpose", "microservices")
                .tag("microservices"))
    
    def database_lb(self):
        """Configure for database load balancing"""
        return (self.tcp(5432)
                .algorithm("least_connections")
                .disable_health_check()
                .label("purpose", "database")
                .tag("database"))
    
    def websocket_lb(self):
        """Configure for WebSocket applications"""
        return (self.http()
                .sticky_sessions()
                .health_check("/health")
                .backend_keepalive(True)
                .label("purpose", "websocket")
                .tag("websocket"))
    
    # Lifecycle operations
    def preview(self) -> Dict[str, Any]:
        """Preview the load balancer configuration"""
        config = self._get_lb_config()
        cost = self._estimate_lb_cost()
        
        # Get all forwarding rules
        all_rules = []
        if self.default_forwarding_rule:
            all_rules.append(self.default_forwarding_rule)
        all_rules.extend(self.forwarding_rules)
        
        preview = {
            "resource_type": "DigitalOcean Load Balancer",
            "lb_name": self.lb_name,
            "description": self.lb_description,
            
            # Configuration
            "algorithm": self.algorithm,
            "region": self.region,
            "size": self.size,
            "vpc_uuid": self.vpc_uuid,
            
            # Forwarding rules
            "forwarding_rules": all_rules,
            "forwarding_rule_count": len(all_rules),
            
            # Health checks
            "health_check": {
                "enabled": self.health_check_enabled,
                "config": self.health_check_config if self.health_check_enabled else None
            },
            
            # Sticky sessions
            "sticky_sessions": {
                "enabled": self.sticky_sessions_enabled,
                "config": self.sticky_sessions_config if self.sticky_sessions_enabled else None
            },
            
            # SSL/TLS
            "ssl": {
                "termination": self.ssl_termination,
                "certificate_id": self.certificate_id,
                "redirect_http_to_https": self.redirect_http_to_https,
                "protocols": self.ssl_protocols if self.ssl_termination else None
            },
            
            # Backends
            "backends": {
                "droplet_ids": self.droplet_ids,
                "droplet_tags": self.droplet_tags,
                "total_backends": len(self.droplet_ids) + len(self.droplet_tags)
            },
            
            # Security
            "security": {
                "firewall_rules": self.firewall_rules,
                "proxy_protocol": self.enable_proxy_protocol,
                "backend_keepalive": self.enable_backend_keepalive
            },
            
            # Features
            "features": {
                "monitoring": self.monitoring_enabled,
                "access_logs": self.access_logs_enabled,
                "http2": self.enable_http2
            },
            
            # Metadata
            "metadata": {
                "tags": self.lb_tags,
                "labels": self.lb_labels,
                "annotations": self.lb_annotations
            },
            
            # Cost
            "cost": {
                "estimated_monthly": f"${cost:.2f}",
                "size_cost": self._get_size_cost()
            },
            
            # Generated configuration
            "config": config
        }
        
        return preview
    
    def create(self) -> Dict[str, Any]:
        """Create the load balancer"""
        self._ensure_authenticated()
        
        print(f"\\n⚖️  Creating DigitalOcean Load Balancer: {self.lb_name}")
        
        # Validate configuration
        config = self._get_lb_config()
        self._validate_lb_config(config)
        
        # Display configuration summary
        self._display_creation_summary()
        
        try:
            # Check if load balancer already exists
            current_state = self._fetch_current_lb_state()
            if current_state.get("exists"):
                print(f"⚠️  Load balancer '{self.lb_name}' already exists")
                return {
                    "status": "exists",
                    "lb_info": current_state,
                    "message": "Load balancer already exists"
                }
            
            # Create the load balancer
            print(f"🚀 Creating load balancer...")
            
            if self.lb_manager:
                result = self.lb_manager.create_load_balancer(config)
                
                if result.get("success"):
                    self.lb_exists = True
                    self.lb_created = True
                    self.lb_status = "new"
                    
                    lb_info = result.get("load_balancer", {})
                    lb_id = lb_info.get("id")
                    self.lb_ip = lb_info.get("ip")
                    
                    print(f"✅ Load balancer created successfully")
                    print(f"📊 Load Balancer ID: {lb_id}")
                    print(f"🌐 IP Address: {self.lb_ip}")
                    
                    # Display connection information
                    self._display_lb_info(lb_info)
                    
                    return {
                        "status": "created",
                        "lb_info": lb_info,
                        "ip_address": self.lb_ip,
                        "console_url": f"https://cloud.digitalocean.com/networking/load_balancers/{lb_id}"
                    }
                else:
                    error_msg = result.get("error", "Unknown error")
                    print(f"❌ Load balancer creation failed: {error_msg}")
                    return {
                        "status": "failed",
                        "error": error_msg
                    }
            else:
                raise Exception("Load balancer manager not available")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Load balancer creation failed: {error_msg}")
            return {
                "status": "failed",
                "error": error_msg
            }
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy the load balancer"""
        self._ensure_authenticated()
        
        print(f"\\n🗑️  Destroying load balancer: {self.lb_name}")
        
        try:
            if self.lb_manager:
                result = self.lb_manager.destroy_load_balancer(self.lb_name)
                
                if result.get("success"):
                    self.lb_exists = False
                    self.lb_status = "deleted"
                    
                    print(f"✅ Load balancer '{self.lb_name}' destroyed successfully")
                    return {
                        "status": "destroyed",
                        "lb_name": self.lb_name
                    }
                else:
                    error_msg = result.get("error", "Unknown error")
                    print(f"❌ Failed to destroy load balancer: {error_msg}")
                    return {
                        "status": "failed",
                        "error": error_msg
                    }
            else:
                raise Exception("Load balancer manager not available")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Load balancer destruction failed: {error_msg}")
            return {
                "status": "failed",
                "error": error_msg
            }
    
    # Helper methods
    def _get_lb_config(self) -> Dict[str, Any]:
        """Get complete load balancer configuration"""
        # Get all forwarding rules
        forwarding_rules = []
        if self.default_forwarding_rule:
            forwarding_rules.append(self.default_forwarding_rule)
        forwarding_rules.extend(self.forwarding_rules)
        
        config = {
            "name": self.lb_name,
            "algorithm": self.algorithm,
            "region": self.region,
            "size": self.size,
            "forwarding_rules": forwarding_rules,
            "health_check": self.health_check_config if self.health_check_enabled else None,
            "sticky_sessions": self.sticky_sessions_config if self.sticky_sessions_enabled else None,
            "droplet_ids": self.droplet_ids,
            "tag": self.droplet_tags[0] if self.droplet_tags else None,  # DigitalOcean supports one tag
            "tags": self.lb_tags,
            "redirect_http_to_https": self.redirect_http_to_https,
            "enable_proxy_protocol": self.enable_proxy_protocol,
            "enable_backend_keepalive": self.enable_backend_keepalive
        }
        
        # Optional configurations
        if self.vpc_uuid:
            config["vpc_uuid"] = self.vpc_uuid
        
        if self.certificate_id:
            config["certificate_id"] = self.certificate_id
        
        return config
    
    def _validate_lb_config(self, config: Dict[str, Any]):
        """Validate load balancer configuration"""
        if not config.get("forwarding_rules"):
            raise ValueError("At least one forwarding rule is required")
        
        if not config.get("droplet_ids") and not config.get("tag"):
            raise ValueError("At least one backend (droplet ID or tag) is required")
        
        # Validate SSL configuration
        if self.ssl_termination and not self.certificate_id:
            raise ValueError("SSL certificate ID is required for HTTPS load balancing")
    
    def _display_creation_summary(self):
        """Display creation summary"""
        print(f"📊 Algorithm: {self.algorithm}")
        print(f"💾 Size: {self.size}")
        print(f"📍 Region: {self.region}")
        
        # Show forwarding rules
        all_rules = []
        if self.default_forwarding_rule:
            all_rules.append(self.default_forwarding_rule)
        all_rules.extend(self.forwarding_rules)
        
        print(f"🔀 Forwarding Rules:")
        for rule in all_rules:
            print(f"   {rule['entry_protocol'].upper()}:{rule['entry_port']} → {rule['target_protocol'].upper()}:{rule['target_port']}")
        
        # Show backends
        backend_count = len(self.droplet_ids) + len(self.droplet_tags)
        print(f"🖥️  Backends: {backend_count}")
        
        if self.droplet_ids:
            print(f"   Droplet IDs: {', '.join(map(str, self.droplet_ids))}")
        
        if self.droplet_tags:
            print(f"   Droplet Tags: {', '.join(self.droplet_tags)}")
        
        if self.health_check_enabled:
            hc = self.health_check_config
            print(f"❤️  Health Check: {hc['protocol'].upper()}:{hc['port']}{hc.get('path', '')}")
        
        cost = self._estimate_lb_cost()
        print(f"💰 Estimated Cost: ${cost:.2f}/month")
    
    def _display_lb_info(self, lb_info: Dict[str, Any]):
        """Display load balancer information"""
        print(f"\\n📡 Load Balancer Information:")
        print(f"   🌐 IP Address: {lb_info.get('ip')}")
        print(f"   📊 Status: {lb_info.get('status')}")
        print(f"   📍 Region: {lb_info.get('region', {}).get('name')}")
        
        print(f"\\n🌐 Console: https://cloud.digitalocean.com/networking/load_balancers/{lb_info.get('id')}")
    
    def _estimate_lb_cost(self) -> float:
        """Estimate monthly cost for load balancer"""
        # DigitalOcean Load Balancer pricing
        size_costs = {
            "lb-small": 12.00,   # $12/month
            "lb-medium": 30.00,  # $30/month  
            "lb-large": 60.00    # $60/month
        }
        
        return size_costs.get(self.size, 12.00)
    
    def _get_size_cost(self) -> str:
        """Get size-specific cost information"""
        size_costs = {
            "lb-small": "$12/month",
            "lb-medium": "$30/month", 
            "lb-large": "$60/month"
        }
        
        return size_costs.get(self.size, "$12/month")
    
    def _fetch_current_lb_state(self) -> Dict[str, Any]:
        """Fetch current state of load balancer"""
        try:
            if self.lb_manager:
                lb_info = self.lb_manager.get_load_balancer_info(self.lb_name)
                
                if lb_info:
                    return {
                        "exists": True,
                        "lb_name": self.lb_name,
                        "id": lb_info.get("id"),
                        "ip": lb_info.get("ip"),
                        "status": lb_info.get("status"),
                        "algorithm": lb_info.get("algorithm"),
                        "region": lb_info.get("region", {}).get("slug"),
                        "size": lb_info.get("size_unit"),
                        "created_at": lb_info.get("created_at")
                    }
            
            return {
                "exists": False,
                "lb_name": self.lb_name
            }
            
        except Exception as e:
            return {
                "exists": False,
                "lb_name": self.lb_name,
                "error": str(e)
            }


# Convenience function for creating Load Balancer instances
def create_load_balancer(name: str) -> LoadBalancer:
    """
    Create a new Load Balancer instance.
    
    Args:
        name: Load balancer name
        
    Returns:
        LoadBalancer instance
    """
    return LoadBalancer(name)


# Export the class for easy importing
__all__ = ['LoadBalancer', 'create_load_balancer']
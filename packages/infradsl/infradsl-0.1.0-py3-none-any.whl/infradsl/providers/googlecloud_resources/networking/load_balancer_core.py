"""
GCP Load Balancer Core Implementation

Core attributes and authentication for Google Cloud Load Balancers.
Provides the foundation for the modular load balancing system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class LoadBalancerCore(BaseGcpResource):
    """
    Core class for Google Cloud Load Balancer functionality.
    
    This class provides:
    - Basic load balancer attributes and configuration
    - Authentication setup
    - Common utilities for load balancing operations
    """
    
    def __init__(self, name: str):
        """Initialize load balancer core with load balancer name"""
        super().__init__(name)
        
        # Core load balancer attributes
        self.lb_name = name
        self.lb_type = "APPLICATION"  # Default to Application Load Balancer
        self.lb_scheme = "EXTERNAL"  # External load balancer by default
        self.lb_protocol = "HTTP"  # Default protocol
        self.lb_region = "us-central1"  # Default region
        
        # Ports and listeners
        self.http_port = 80
        self.https_port = 443
        self.backend_port = 80
        
        # SSL/TLS configuration
        self.ssl_certificate = None
        self.ssl_policy = None
        self.redirect_http_to_https = False
        
        # Backend configuration
        self.backends = []
        self.health_check_enabled = True
        self.health_check_path = "/"
        self.health_check_protocol = "HTTP"
        self.health_check_port = None  # Use backend port if None
        
        # Traffic distribution
        self.session_affinity = "NONE"
        self.connection_draining_timeout = 300
        self.timeout_seconds = 30
        
        # Security and access
        self.enable_cdn = False
        self.security_policy = None
        self.allowed_regions = []
        
        # Advanced configuration
        self.lb_labels = {}
        self.custom_headers = {}
        self.url_map = None
        
        # Load balancer URLs and networking
        self.frontend_ip = None
        self.backend_service_url = None
        self.url_map_url = None
        self.target_proxy_url = None
        
        # State tracking
        self.lb_exists = False
        self.lb_created = False
        
    def _initialize_managers(self):
        """Initialize load balancer-specific managers"""
        # Will be set up after authentication
        self.load_balancer_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Import here to avoid circular imports
        from ...googlecloud_managers.load_balancer_manager import GcpLoadBalancerManager
        self.load_balancer_manager = GcpLoadBalancerManager(self.gcp_client)
        
        # Set up load balancer URLs (will be populated after creation)
        self.project_id = self.gcp_client.project_id
        
    def _is_valid_lb_type(self, lb_type: str) -> bool:
        """Check if load balancer type is valid"""
        valid_types = ["APPLICATION", "NETWORK", "INTERNAL", "INTERNAL_MANAGED"]
        return lb_type in valid_types
        
    def _is_valid_scheme(self, scheme: str) -> bool:
        """Check if load balancer scheme is valid"""
        valid_schemes = ["EXTERNAL", "INTERNAL", "INTERNAL_MANAGED"]
        return scheme in valid_schemes
        
    def _is_valid_protocol(self, protocol: str) -> bool:
        """Check if protocol is valid"""
        valid_protocols = ["HTTP", "HTTPS", "TCP", "UDP", "SSL"]
        return protocol in valid_protocols
        
    def _is_valid_region(self, region: str) -> bool:
        """Check if region is valid for GCP Load Balancers"""
        gcp_regions = [
            'us-central1', 'us-east1', 'us-east4', 'us-west1', 'us-west2', 'us-west3', 'us-west4',
            'europe-north1', 'europe-west1', 'europe-west2', 'europe-west3', 'europe-west4', 'europe-west6',
            'asia-east1', 'asia-east2', 'asia-northeast1', 'asia-northeast2', 'asia-south1', 'asia-southeast1',
            'australia-southeast1', 'northamerica-northeast1', 'southamerica-east1'
        ]
        return region in gcp_regions
        
    def _is_valid_session_affinity(self, affinity: str) -> bool:
        """Check if session affinity type is valid"""
        valid_types = ["NONE", "CLIENT_IP", "CLIENT_IP_PROTO", "CLIENT_IP_PORT_PROTO", "GENERATED_COOKIE", "HTTP_COOKIE"]
        return affinity in valid_types
        
    def _validate_backend(self, backend: Dict[str, Any]) -> bool:
        """Validate backend configuration"""
        required_fields = ["name", "type"]
        for field in required_fields:
            if field not in backend:
                return False
        
        # Validate backend type
        valid_types = ["instance", "instance_group", "network_endpoint_group", "function"]
        if backend["type"] not in valid_types:
            return False
            
        return True
        
    def _get_load_balancer_type_display(self) -> str:
        """Get display name for load balancer type"""
        type_mapping = {
            "APPLICATION": "Application Load Balancer (HTTP/HTTPS)",
            "NETWORK": "Network Load Balancer (TCP/UDP)",
            "INTERNAL": "Internal Load Balancer",
            "INTERNAL_MANAGED": "Internal Application Load Balancer"
        }
        return type_mapping.get(self.lb_type, self.lb_type)
        
    def _estimate_base_cost(self) -> float:
        """Estimate base monthly cost for the load balancer"""
        # GCP Load Balancer pricing (simplified)
        if self.lb_type == "APPLICATION":
            # Application Load Balancer: $22.27/month + $0.025/hour per rule
            base_cost = 22.27
            forwarding_rules_cost = 0.025 * 24 * 30  # $18.60/month per rule
            return base_cost + forwarding_rules_cost
        elif self.lb_type == "NETWORK":
            # Network Load Balancer: $18.60/month per forwarding rule
            return 0.025 * 24 * 30
        elif self.lb_type in ["INTERNAL", "INTERNAL_MANAGED"]:
            # Internal Load Balancer: $18.60/month per forwarding rule
            return 0.025 * 24 * 30
        else:
            return 25.0  # Default estimate
            
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the load balancer from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get load balancer info if it exists
            if self.load_balancer_manager:
                lb_info = self.load_balancer_manager.get_load_balancer_info(self.lb_name)
                
                if lb_info.get("exists", False):
                    return {
                        "exists": True,
                        "lb_name": self.lb_name,
                        "lb_type": lb_info.get("lb_type"),
                        "scheme": lb_info.get("scheme"),
                        "protocol": lb_info.get("protocol"),
                        "region": lb_info.get("region"),
                        "frontend_ip": lb_info.get("frontend_ip"),
                        "backend_count": lb_info.get("backend_count", 0),
                        "backends": lb_info.get("backends", []),
                        "health_checks": lb_info.get("health_checks", []),
                        "ssl_certificates": lb_info.get("ssl_certificates", []),
                        "security_policy": lb_info.get("security_policy"),
                        "session_affinity": lb_info.get("session_affinity"),
                        "timeout_seconds": lb_info.get("timeout_seconds"),
                        "creation_time": lb_info.get("creation_time"),
                        "status": lb_info.get("status", "UNKNOWN")
                    }
                else:
                    return {
                        "exists": False,
                        "lb_name": self.lb_name
                    }
            else:
                return {
                    "exists": False,
                    "lb_name": self.lb_name,
                    "error": "Load balancer manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch load balancer state: {str(e)}")
            return {
                "exists": False,
                "lb_name": self.lb_name,
                "error": str(e)
            }
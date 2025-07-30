from typing import Optional, List

class BackendConfig:
    """Configuration for a backend in a load balancer"""
    def __init__(self, vm_name: str, zone: str, port: int = 80, health_check_name: Optional[str] = None):
        self.vm_name = vm_name
        self.zone = zone
        self.port = port
        self.health_check_name = health_check_name or f"{vm_name}-health-check"

class LoadBalancerConfig:
    """Configuration for a load balancer"""
    def __init__(self, name: str):
        self.name = name
        self.backends: List[BackendConfig] = []
        self.ssl_certificate: Optional[str] = None
        self.domain: Optional[str] = None
        self.port = 80
        self.ssl_port = 443 
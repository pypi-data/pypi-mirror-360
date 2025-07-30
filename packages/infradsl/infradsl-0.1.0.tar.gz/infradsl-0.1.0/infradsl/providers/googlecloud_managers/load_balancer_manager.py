import time
from typing import Dict, Any, Optional, List
from google.cloud import compute_v1
from .gcp_client import GcpClient
from .load_balancer import LoadBalancerManager, LoadBalancerConfig, BackendConfig

class GcpLoadBalancerManager:
    """Manages Google Cloud load balancer operations (Legacy wrapper for backward compatibility)"""
    
    def __init__(self, gcp_client: GcpClient):
        self.gcp_client = gcp_client
        # Initialize the new modular load balancer manager
        self._load_balancer_manager = None
    
    @property
    def load_balancer_manager(self):
        """Get the load balancer manager (lazy loading after authentication)"""
        if not self._load_balancer_manager:
            print(f"🔐 Initializing load balancer manager...")
            print(f"   - Project ID: {self.gcp_client.project}")
            print(f"   - Credentials type: {type(self.gcp_client.credentials)}")
            print(f"   - Is authenticated: {self.gcp_client.is_authenticated}")
            
            self._load_balancer_manager = LoadBalancerManager(
                project_id=self.gcp_client.project,
                credentials=self.gcp_client.credentials
            )
            print(f"✅ Load balancer manager initialized")
        return self._load_balancer_manager
    
    def create_load_balancer(self, config: LoadBalancerConfig) -> Dict[str, Any]:
        """Create a complete load balancer setup"""
        return self.load_balancer_manager.create_load_balancer(config)
    
    def delete_load_balancer(self, name: str) -> bool:
        """Delete a complete load balancer setup"""
        return self.load_balancer_manager.delete_load_balancer(name)
    
    def update_backend_service_with_vms(self, backend_service_name: str, backends: List[BackendConfig]):
        """Update a backend service to include VMs once they're available"""
        return self.load_balancer_manager.backend_service_manager.update_backend_service_with_vms(
            backend_service_name, backends, self.load_balancer_manager.instance_group_manager
        )

# Legacy class aliases for backward compatibility
BackendConfig = BackendConfig
LoadBalancerConfig = LoadBalancerConfig

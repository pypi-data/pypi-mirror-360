import time
from typing import Dict, Any, Optional
from google.cloud import compute_v1
from .gcp_client import GcpClient

class GcpHealthCheckManager:
    """Manages Google Cloud health check operations"""
    
    def __init__(self, gcp_client: GcpClient):
        self.gcp_client = gcp_client
        # Don't access client properties immediately - they require authentication
        self._project_id = None
        self._health_check_client = None
    
    @property
    def project_id(self):
        """Get the project ID (lazy loading after authentication)"""
        if not self._project_id:
            self._project_id = self.gcp_client.project
        return self._project_id
    
    @property
    def health_check_client(self):
        """Get the health check client (lazy loading after authentication)"""
        if not self._health_check_client:
            self._health_check_client = compute_v1.HealthChecksClient(credentials=self.gcp_client.credentials)
        return self._health_check_client
    
    def create_health_check(self, vm_name: str, health_check_config: Dict[str, Any]) -> str:
        """Create a health check for a VM"""
        health_check_name = f"{vm_name}-health-check"
        
        # Check if health check already exists
        existing_health_check = self._get_health_check(health_check_name)
        if existing_health_check:
            print(f"🔄 Using existing health check: {health_check_name}")
            return existing_health_check.name
        
        print(f"🏥 Creating health check: {health_check_name}")
        
        # Create health check based on protocol
        if health_check_config["protocol"].lower() == "http":
            health_check = compute_v1.HealthCheck()
            health_check.name = health_check_name
            health_check.type_ = "HTTP"
            health_check.http_health_check = compute_v1.HTTPHealthCheck()
            health_check.http_health_check.port = health_check_config["port"]
            health_check.http_health_check.request_path = health_check_config["path"]
            health_check.http_health_check.host = None  # Use default host
            health_check.http_health_check.response = "200"  # Expect 200 OK
        elif health_check_config["protocol"].lower() == "https":
            health_check = compute_v1.HealthCheck()
            health_check.name = health_check_name
            health_check.type_ = "HTTPS"
            health_check.https_health_check = compute_v1.HTTPSHealthCheck()
            health_check.https_health_check.port = health_check_config["port"]
            health_check.https_health_check.request_path = health_check_config["path"]
            health_check.https_health_check.host = None  # Use default host
            health_check.https_health_check.response = "200"  # Expect 200 OK
        elif health_check_config["protocol"].lower() == "tcp":
            health_check = compute_v1.HealthCheck()
            health_check.name = health_check_name
            health_check.type_ = "TCP"
            health_check.tcp_health_check = compute_v1.TCPHealthCheck()
            health_check.tcp_health_check.port = health_check_config["port"]
        else:
            raise ValueError(f"Unsupported health check protocol: {health_check_config['protocol']}")
        
        # Set common health check parameters
        health_check.check_interval_sec = 5  # Check every 5 seconds
        health_check.timeout_sec = 5  # 5 second timeout
        health_check.unhealthy_threshold = 2  # Mark unhealthy after 2 failures
        health_check.healthy_threshold = 2  # Mark healthy after 2 successes
        
        # Create the health check
        request = compute_v1.InsertHealthCheckRequest(
            project=self.project_id,
            health_check_resource=health_check
        )
        
        try:
            operation = self.health_check_client.insert(request=request)
            print(f"   ⏳ Creating health check...")
            
            # Small delay to allow operation to start
            time.sleep(1)
            
            # Wait for operation to complete (brief wait)
            self._wait_for_health_check_operation(operation)
            
            print(f"   ✅ Health check created: {health_check_name}")
            return health_check_name
            
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to create health check {health_check_name}: {e}")
            return None
    
    def delete_health_check(self, vm_name: str) -> bool:
        """Delete health check associated with a VM"""
        try:
            health_check_name = f"{vm_name}-health-check"
            
            # Check if health check exists
            existing_health_check = self._get_health_check(health_check_name)
            if not existing_health_check:
                print(f"✅ No health check found for VM: {vm_name}")
                return True
            
            print(f"🗑️  Deleting health check: {health_check_name}")
            
            delete_request = compute_v1.DeleteHealthCheckRequest(
                project=self.project_id,
                health_check=health_check_name
            )
            
            try:
                operation = self.health_check_client.delete(request=delete_request)
                self._wait_for_health_check_operation(operation)
                print(f"   ✅ Health check deleted: {health_check_name}")
                return True
            except Exception as e:
                print(f"   ⚠️  Warning: Failed to delete health check {health_check_name}: {e}")
                return False
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to delete health check: {e}")
            return False
    
    def _get_health_check(self, health_check_name: str) -> Optional[compute_v1.HealthCheck]:
        """Get health check by name"""
        try:
            request = compute_v1.GetHealthCheckRequest(
                project=self.project_id,
                health_check=health_check_name
            )
            return self.health_check_client.get(request=request)
        except Exception:
            return None
    
    def _wait_for_health_check_operation(self, operation, timeout: int = 180):
        """Wait for health check operation to complete"""
        try:
            result = operation.result(timeout=timeout)
            if operation.error_code:
                print(f"   ❌ Health check operation failed: [Code: {operation.error_code}] {operation.error_message}")
                raise operation.exception() or RuntimeError(operation.error_message)
            
            if operation.warnings:
                print(f"   ⚠️  Warnings during health check operation:")
                for warning in operation.warnings:
                    print(f"      - {warning.code}: {warning.message}")
            
            print(f"   ✅ Health check operation completed successfully")
            return result

        except Exception as e:
            print(f"   ⏰ Timeout waiting for health check operation (after {timeout}s)")
            raise e 
import time
from typing import List, Optional
from google.cloud import compute_v1
from .operations import OperationManager
from .config import BackendConfig

class BackendServiceManager:
    """Manages backend services for load balancers"""
    
    def __init__(self, project_id: str, credentials, operation_manager: OperationManager = None):
        self.project_id = project_id
        self.credentials = credentials
        self.operation_manager = operation_manager or OperationManager(project_id, credentials)
        self._backend_services_client = None
    
    @property
    def backend_services_client(self):
        """Get the backend services client (lazy loading)"""
        if not self._backend_services_client:
            self._backend_services_client = compute_v1.BackendServicesClient(credentials=self.credentials)
        return self._backend_services_client
    
    def create_backend_service(self, name: str, health_check_name: Optional[str] = None) -> Optional[str]:
        """Create a backend service without any backends initially"""
        print(f"   🔧 Creating backend service: {name}")

        existing_service = self._get_backend_service(name)
        if existing_service:
            print(f"   🔄 Using existing backend service: {name}")
            return name

        backend_service = compute_v1.BackendService(
            name=name,
            protocol="HTTP",
            port_name="http",
            timeout_sec=30,
            load_balancing_scheme="EXTERNAL_MANAGED",
            port=80,
            backends=[],  # Start with no backends
        )

        if health_check_name:
            health_check = f"projects/{self.project_id}/global/healthChecks/{health_check_name}"
            backend_service.health_checks = [health_check]
            print(f"      - Health Check: {health_check_name}")

        request = compute_v1.InsertBackendServiceRequest(
            project=self.project_id,
            backend_service_resource=backend_service,
        )

        try:
            print(f"   🔍 Backend service configuration:")
            print(f"      - Name: {name}")
            print(f"      - Protocol: {backend_service.protocol}")
            print(f"      - Port: {backend_service.port}")
            
            operation = self.backend_services_client.insert(request=request)
            print(f"   ⏳ Creating backend service...")
            
            self.operation_manager.wait_for_global_operation(operation)
            
            print(f"   ✅ Backend service '{name}' created successfully")
            
            return name
        except Exception as e:
            print(f"   ❌ Failed to create backend service {name}: {e}")
            return None
    
    def update_backend_service_with_vms(self, backend_service_name: str, backends: List[BackendConfig], instance_group_manager):
        """Update a backend service to include VMs once they're available"""
        print(f"   🔄 Updating backend service with VMs...")
        
        try:
            # Get the current backend service
            backend_service = self._get_backend_service(backend_service_name)
            if not backend_service:
                print(f"   ⚠️  Backend service {backend_service_name} not found")
                return
            
            # Create or get instance groups for each backend
            backend_list = []
            for backend_config in backends:
                instance_group_name = f"{backend_config.vm_name}-group"
                instance_group = instance_group_manager.create_instance_group(
                    instance_group_name, backend_config.zone, [backend_config.vm_name], port=backend_config.port
                )
                
                if instance_group:
                    backend = compute_v1.Backend()
                    backend.group = f"projects/{self.project_id}/zones/{backend_config.zone}/instanceGroups/{instance_group_name}"
                    backend_list.append(backend)
            
            if backend_list:
                # Update the backend service
                backend_service.backends = backend_list
                
                request = compute_v1.UpdateBackendServiceRequest(
                    project=self.project_id,
                    backend_service=backend_service_name,
                    backend_service_resource=backend_service
                )
                
                operation = self.backend_services_client.update(request=request)
                print(f"   ⏳ Updating backend service...")
                
                # Small delay to allow operation to start
                time.sleep(1)
                
                self.operation_manager.wait_for_global_operation(operation)
                print(f"   ✅ Backend service updated with {len(backend_list)} backends")
            else:
                print(f"   ⚠️  No valid backends could be added to the service")
                
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to update backend service: {e}")
    
    def update_backend_service_backends(self, backend_service_name: str, backends: List[BackendConfig], instance_group_manager) -> bool:
        """Update a backend service to add backends, ensuring no duplicates."""
        try:
            request = compute_v1.GetBackendServiceRequest(
                project=self.project_id,
                backend_service=backend_service_name
            )
            backend_service = self.backend_services_client.get(request=request)
            
            initial_backend_urls = {b.group for b in backend_service.backends}
            final_backend_urls = {b.group for b in backend_service.backends}
            
            for backend_config in backends:
                instance_group_name = f"{backend_config.vm_name}-group"
                instance_group = instance_group_manager.create_instance_group(
                    instance_group_name, backend_config.zone, [backend_config.vm_name], port=backend_config.port
                )
                
                if not instance_group:
                    print(f"      ⚠️  Warning: Could not create instance group for {backend_config.vm_name}. It will not be added to the load balancer.")
                    continue

                backend_group_url = f"projects/{self.project_id}/zones/{backend_config.zone}/instanceGroups/{instance_group_name}"
                final_backend_urls.add(backend_group_url)
            
            # If the backends haven't changed, do nothing
            if final_backend_urls == initial_backend_urls:
                print(f"   ✅ All backends are already in the service")
                return True

            # Rebuild the list of backends from the unique set of URLs
            new_backend_list = []
            for url in final_backend_urls:
                backend = compute_v1.Backend()
                backend.group = url
                backend.balancing_mode = "UTILIZATION"
                backend.max_utilization = 0.8
                backend.capacity_scaler = 1.0
                new_backend_list.append(backend)
            
            backend_service.backends = new_backend_list
            
            request = compute_v1.UpdateBackendServiceRequest(
                project=self.project_id,
                backend_service=backend_service_name,
                backend_service_resource=backend_service
            )
            
            operation = self.backend_services_client.update(request=request)
            print(f"   ⏳ Updating backend service with {len(new_backend_list)} total backends...")
            
            self.operation_manager.wait_for_global_operation(operation)
            print(f"   ✅ Successfully updated backends for {backend_service_name}")
            return True
                
        except Exception as e:
            print(f"   ❌ Failed to update backend service {backend_service_name}: {e}")
            return False
    
    def get_backend_service(self, name: str):
        """Get a backend service by name"""
        return self._get_backend_service(name)
    
    def _get_backend_service(self, name: str):
        """Get a backend service by name"""
        try:
            request = compute_v1.GetBackendServiceRequest(project=self.project_id, backend_service=name)
            return self.backend_services_client.get(request=request)
        except Exception:
            return None
    
    def delete_backend_service(self, name: str):
        """Delete a backend service"""
        try:
            request = compute_v1.DeleteBackendServiceRequest(project=self.project_id, backend_service=name)
            operation = self.backend_services_client.delete(request=request)
            self.operation_manager.wait_for_global_operation(operation)
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to delete backend service {name}: {e}")
    
    def _create_default_health_check(self, name: str):
        """Create a default HTTP health check"""
        try:
            # Check if health check already exists
            health_check_client = compute_v1.HealthChecksClient(credentials=self.credentials)
            try:
                request = compute_v1.GetHealthCheckRequest(project=self.project_id, health_check=name)
                health_check_client.get(request=request)
                print(f"      ✅ Using existing health check: {name}")
                return
            except Exception:
                # Health check doesn't exist, create it
                pass
            
            # Create HTTP health check
            health_check = compute_v1.HealthCheck()
            health_check.name = name
            health_check.type_ = "HTTP"
            health_check.http_health_check = compute_v1.HTTPHealthCheck()
            health_check.http_health_check.port = 80
            health_check.http_health_check.request_path = "/"
            health_check.check_interval_sec = 5
            health_check.timeout_sec = 5
            health_check.unhealthy_threshold = 2
            health_check.healthy_threshold = 2
            
            request = compute_v1.InsertHealthCheckRequest(
                project=self.project_id,
                health_check_resource=health_check
            )
            
            operation = health_check_client.insert(request=request)
            print(f"   ⏳ Creating health check...")
            self.operation_manager.wait_for_global_operation(operation)
            print(f"   ✅ Health check created: {name}")
            
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"      ✅ Health check already exists: {name}")
                return
            print(f"      ⚠️  Warning: Failed to create default health check {name}: {e}")
            raise 
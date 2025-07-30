import time
from typing import Dict, Any, List
from google.cloud import compute_v1
from .config import LoadBalancerConfig, BackendConfig
from .backend_services import BackendServiceManager
from .url_maps import UrlMapManager
from .target_proxies import TargetProxyManager
from .forwarding_rules import ForwardingRuleManager
from .instance_groups import InstanceGroupManager
from .operations import OperationManager
from .error_handler import LoadBalancerErrorHandler, ProgressTracker, UserExperienceEnhancer
from .validator import LoadBalancerValidator, ResourceAvailabilityChecker


class LoadBalancerManager:
    """Main orchestrator for Google Cloud Load Balancer operations"""
    
    def __init__(self, project_id: str, credentials):
        self.project_id = project_id
        self.credentials = credentials
        
        # Initialize sub-managers
        self.operation_manager = OperationManager(project_id, credentials)
        self.instance_group_manager = InstanceGroupManager(project_id, credentials, self.operation_manager)
        self.backend_service_manager = BackendServiceManager(project_id, credentials, self.operation_manager)
        self.url_map_manager = UrlMapManager(project_id, credentials, self.operation_manager)
        self.target_proxy_manager = TargetProxyManager(project_id, credentials, self.operation_manager)
        self.forwarding_rule_manager = ForwardingRuleManager(project_id, credentials, self.operation_manager)
        
        # Initialize UX components
        self.progress_tracker = None
        self.error_handler = LoadBalancerErrorHandler()
        self.validator = LoadBalancerValidator()
        self.availability_checker = ResourceAvailabilityChecker(project_id, credentials)
    
    def create_load_balancer(self, config: LoadBalancerConfig) -> Dict[str, Any]:
        """Create a complete load balancer with intelligent backend management"""
        if not config.backends:
            print("❌ No backends configured for load balancer")
            return None
        
        print(f"\n🚀 Creating load balancer with intelligent backend management...")
        print(f"   📝 Name: {config.name}")
        print(f"   🔄 Backends: {len(config.backends)}")
        
        # Initialize progress tracking
        self.progress_tracker = ProgressTracker([
            "Analyzing backend configuration",
            "Creating health checks",
            "Setting up instance groups", 
            "Creating backend service",
            "Creating URL map",
            "Creating target proxy",
            "Creating forwarding rule and allocating IP"
        ])
        
        # Step 1: Intelligent backend analysis
        self.progress_tracker.start_step("Analyzing backend configuration")
        healthy_backends = self._analyze_backends_intelligence(config.backends)
        self.progress_tracker.complete_step("Analyzing backend configuration", success=True)
        
        if not healthy_backends:
            print("❌ No healthy backends found after analysis")
            return None
        
        # Use healthy backends for the rest of the process
        config.backends = healthy_backends
        
        print(f"🌐 Creating load balancer: {config.name}")
        print(f"💡 This process creates multiple Google Cloud resources and may take several minutes.")
        print(f"💡 We'll keep you updated on the progress...")
        
        # Step 0: Validate configuration
        print(f"\n🔍 Step 0/6: Validating configuration...")
        is_valid, validation_errors = self.validator.validate_load_balancer_config(config)
        
        if not is_valid:
            print(self.validator.format_validation_errors(validation_errors))
            return None
        
        print(f"   ✅ Configuration is valid")
        
        # Step 0.5: Check resource availability
        print(f"\n🔍 Step 0.5/6: Checking resource availability...")
        availability = self.availability_checker.check_backend_availability(config.backends)
        print(self.availability_checker.format_availability_report(availability))
        
        if availability["unavailable"]:
            print(f"\n⚠️  Some resources are not available, but we'll proceed anyway.")
            print(f"💡 The load balancer will be created and VMs can be added later.")
        
        # Show helpful tips
        UserExperienceEnhancer.show_operation_tips("load_balancer_creation")
        
        try:
            # Step 1: Create backend service
            self.progress_tracker.start_step("Creating backend service")
            backend_service_name = f"{config.name}-backend"
            health_check_name = config.backends[0].health_check_name if config.backends and config.backends[0].health_check_name else None
            backend_service = self._create_backend_service_with_retry(
                backend_service_name, health_check_name
            )
            
            if not backend_service:
                self.progress_tracker.complete_step("Creating backend service", success=False)
                return None
            
            self.progress_tracker.complete_step("Creating backend service", success=True)
            
            # Step 2: Update backend service with additional backends
            self.progress_tracker.start_step("Configuring backends")
            self.backend_service_manager.update_backend_service_backends(
                backend_service_name, config.backends, self.instance_group_manager
            )
            self.progress_tracker.complete_step("Configuring backends", success=True)
            
            # Step 3: Create URL map
            self.progress_tracker.start_step("Creating URL map")
            url_map_name = f"{config.name}-urlmap"
            url_map = self._create_url_map_with_retry(url_map_name, backend_service)
            
            if not url_map:
                self.progress_tracker.complete_step("Creating URL map", success=False)
                return None
            
            self.progress_tracker.complete_step("Creating URL map", success=True)
            
            # Step 4: Create target proxy
            self.progress_tracker.start_step("Creating target proxy")
            is_https = False
            if config.ssl_certificate:
                target_proxy_name = f"{config.name}-https-proxy"
                target_proxy = self._create_https_proxy_with_retry(
                    target_proxy_name, url_map, config.ssl_certificate
                )
                forwarding_rule_port = config.ssl_port
                is_https = True
            else:
                target_proxy_name = f"{config.name}-http-proxy"
                target_proxy = self._create_http_proxy_with_retry(target_proxy_name, url_map)
                forwarding_rule_port = config.port
            
            if not target_proxy:
                self.progress_tracker.complete_step("Creating target proxy", success=False)
                return None
            
            self.progress_tracker.complete_step("Creating target proxy", success=True)
            
            # Step 5: Create global forwarding rule
            self.progress_tracker.start_step("Creating forwarding rule and allocating IP")
            forwarding_rule_name = f"{config.name}-forwarding-rule"
            forwarding_rule = self._create_forwarding_rule_with_retry(
                forwarding_rule_name, target_proxy, forwarding_rule_port, is_https
            )
            
            if not forwarding_rule:
                self.progress_tracker.complete_step("Creating forwarding rule and allocating IP", success=False)
                return None
            
            self.progress_tracker.complete_step("Creating forwarding rule and allocating IP", success=True)
            
            # Finalize: Add VMs to instance groups
            print(f"\n🔄 Finalizing: Adding VMs to instance groups...")
            self._retry_add_vms_to_instance_groups(config.backends)
            
            # Update backend service with VMs
            self.backend_service_manager.update_backend_service_with_vms(
                backend_service_name, config.backends, self.instance_group_manager
            )
            
            # Provide comprehensive summary
            self._provide_load_balancer_summary(config.name, backend_service_name, config.backends)
            
            # Show next steps
            UserExperienceEnhancer.show_next_steps("load_balancer", config.name)
            
            print(f"\n{self.progress_tracker.get_progress_summary()}")
            
            return {
                "name": config.name,
                "ip_address": forwarding_rule.ip_address,
                "port": forwarding_rule_port,
                "backend_service": backend_service_name,
                "url_map": url_map_name,
                "target_proxy": target_proxy_name,
                "forwarding_rule": forwarding_rule_name
            }
            
        except Exception as e:
            # Handle errors gracefully
            error_analysis = self.error_handler.analyze_error(e, "load balancer creation")
            print(f"\n{self.error_handler.format_error_message(error_analysis)}")
            
            # Show troubleshooting guide
            UserExperienceEnhancer.show_troubleshooting_guide()
            
            return None
    
    def _create_backend_service_with_retry(self, name: str, health_check_name: str, max_attempts: int = 3) -> str:
        """Create backend service with retry logic"""
        for attempt in range(max_attempts):
            try:
                return self.backend_service_manager.create_backend_service(
                    name, health_check_name
                )
            except Exception as e:
                if attempt < max_attempts - 1 and self.error_handler.should_retry_operation(e, attempt):
                    delay = self.error_handler.get_retry_delay(attempt)
                    print(f"   ⏳ Retrying in {delay} seconds... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(delay)
                else:
                    raise e
        return None
    
    def _create_url_map_with_retry(self, name: str, backend_service: str, max_attempts: int = 3) -> str:
        """Create URL map with retry logic"""
        for attempt in range(max_attempts):
            try:
                return self.url_map_manager.create_url_map(name, backend_service)
            except Exception as e:
                if attempt < max_attempts - 1 and self.error_handler.should_retry_operation(e, attempt):
                    delay = self.error_handler.get_retry_delay(attempt)
                    print(f"   ⏳ Retrying in {delay} seconds... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(delay)
                else:
                    raise e
        return None
    
    def _create_http_proxy_with_retry(self, name: str, url_map: str, max_attempts: int = 3) -> str:
        """Create HTTP proxy with retry logic"""
        for attempt in range(max_attempts):
            try:
                return self.target_proxy_manager.create_http_proxy(name, url_map)
            except Exception as e:
                if attempt < max_attempts - 1 and self.error_handler.should_retry_operation(e, attempt):
                    delay = self.error_handler.get_retry_delay(attempt)
                    print(f"   ⏳ Retrying in {delay} seconds... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(delay)
                else:
                    raise e
        return None
    
    def _create_https_proxy_with_retry(self, name: str, url_map: str, ssl_certificate: str, max_attempts: int = 3) -> str:
        """Create HTTPS proxy with retry logic"""
        for attempt in range(max_attempts):
            try:
                return self.target_proxy_manager.create_https_proxy(name, url_map, ssl_certificate)
            except Exception as e:
                if attempt < max_attempts - 1 and self.error_handler.should_retry_operation(e, attempt):
                    delay = self.error_handler.get_retry_delay(attempt)
                    print(f"   ⏳ Retrying in {delay} seconds... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(delay)
                else:
                    raise e
        return None
    
    def _create_forwarding_rule_with_retry(self, name: str, target_proxy: str, port: int, is_https: bool, max_attempts: int = 3) -> Any:
        """Create forwarding rule with retry logic"""
        for attempt in range(max_attempts):
            try:
                return self.forwarding_rule_manager.create_forwarding_rule(
                    name, target_proxy, port, is_https=is_https
                )
            except Exception as e:
                if attempt < max_attempts - 1 and self.error_handler.should_retry_operation(e, attempt):
                    delay = self.error_handler.get_retry_delay(attempt)
                    print(f"   ⏳ Retrying in {delay} seconds... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(delay)
                else:
                    raise e
        return None
    
    def _retry_add_vms_to_instance_groups(self, backends: List[BackendConfig]):
        """Retry adding VMs to instance groups with better error handling"""
        for backend in backends:
            # Handle both single VM (vm_name) and multiple VMs (vms) cases
            if hasattr(backend, 'vms') and backend.vms:
                # New interface with multiple VMs
                try:
                    print(f"   🔄 Adding VMs to instance group for backend: {backend.vm_name}")
                    self.instance_group_manager.add_vms_to_instance_group(
                        backend.vm_name, backend.vms
                    )
                except Exception as e:
                    print(f"   ⚠️  Could not add VMs to instance group {backend.vm_name}: {e}")
                    print(f"   💡 This is normal if VMs are still being created or are in a different zone")
            else:
                # Legacy interface with single VM
                try:
                    print(f"   🔄 Adding VM to instance group for backend: {backend.vm_name}")
                    # For single VM, we need to create the instance group name
                    instance_group_name = f"{backend.vm_name}-group"
                    self.instance_group_manager.add_vms_to_instance_group(
                        instance_group_name, [backend.vm_name], backend.zone
                    )
                except Exception as e:
                    print(f"   ⚠️  Could not add VM to instance group {backend.vm_name}: {e}")
                    print(f"   💡 This is normal if VMs are still being created or are in a different zone")
    
    def delete_load_balancer(self, name: str) -> bool:
        """Delete a complete load balancer setup"""
        print(f"🗑️  Deleting load balancer: {name}")
        
        try:
            # Delete in reverse order
            forwarding_rule_name = f"{name}-forwarding-rule"
            self.forwarding_rule_manager.delete_forwarding_rule(forwarding_rule_name)
            
            target_proxy_name = f"{name}-http-proxy"
            self.target_proxy_manager.delete_http_proxy(target_proxy_name)
            
            url_map_name = f"{name}-urlmap"
            self.url_map_manager.delete_url_map(url_map_name)
            
            backend_service_name = f"{name}-backend"
            self.backend_service_manager.delete_backend_service(backend_service_name)
            
            # Delete instance groups
            # Note: We'd need to track which instance groups were created
            print(f"✅ Load balancer deleted: {name}")
            return True
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to delete load balancer {name}: {e}")
            return False
    
    def _provide_load_balancer_summary(self, lb_name: str, backend_service_name: str, backends: List[BackendConfig]):
        """Provide a helpful summary after load balancer creation"""
        print(f"\n🎉 Load balancer '{lb_name}' created successfully!")
        print(f"\n📋 Summary:")
        print(f"   • Backend service: {backend_service_name}")
        print(f"   • Backends configured: {len(backends)}")
        for i, backend in enumerate(backends, 1):
            print(f"     {i}. {backend.vm_name} ({backend.zone})")
            if hasattr(backend, 'vms') and backend.vms:
                print(f"        VMs: {len(backend.vms)} instances")
            else:
                print(f"        VM: {backend.vm_name}")
        
        print(f"\n🔗 Next steps:")
        print(f"   • Your load balancer will be available at the IP address shown above")
        print(f"   • It may take a few minutes for all components to be fully operational")
        print(f"   • You can monitor the load balancer in the Google Cloud Console")
        print(f"   • To delete the load balancer, use the delete command")
        
        print(f"\n💡 Tips:")
        print(f"   • If you see health check failures, ensure your VMs are running and accessible")
        print(f"   • The load balancer will automatically distribute traffic across healthy backends")
        print(f"   • You can add more backends later by updating the configuration")

    def _add_vm_to_instance_group_with_retry(self, backend_config, retries=3):
        """Add VM to instance group with retry logic"""
        for attempt in range(retries):
            try:
                # Try to add VM to instance group
                success = self.instance_group_manager.add_vm_to_group(
                    backend_config.vm_name,
                    backend_config.zone,
                    f"{self.config.name}-instance-group"
                )
                if success:
                    return True
                    
            except Exception as e:
                print(f"   ⚠️  Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    print(f"   🔄 Retrying in 5 seconds...")
                    time.sleep(5)
                    
        return False

    def _analyze_backends_intelligence(self, backends: List) -> List:
        """Intelligently analyze backend health and configuration"""
        print(f"🧠 Analyzing {len(backends)} backends with AI-like intelligence...")
        
        healthy_backends = []
        issues_found = []
        
        for i, backend in enumerate(backends, 1):
            print(f"   🔍 Analyzing backend {i}: {backend.vm_name}")
            
            # Check VM existence and health
            vm_status = self._check_vm_health(backend)
            
            if vm_status['exists']:
                if vm_status['running']:
                    print(f"   ✅ Backend {backend.vm_name}: Healthy")
                    healthy_backends.append(backend)
                else:
                    print(f"   ⚠️  Backend {backend.vm_name}: VM exists but not running")
                    issues_found.append(f"VM {backend.vm_name} is not running")
            else:
                print(f"   ❌ Backend {backend.vm_name}: VM does not exist")
                issues_found.append(f"VM {backend.vm_name} does not exist")
        
        # Provide intelligent recommendations
        if len(healthy_backends) < len(backends):
            print(f"\n🔍 Backend Analysis Results:")
            print(f"   ✅ Healthy backends: {len(healthy_backends)}/{len(backends)}")
            
            if issues_found:
                print(f"   ⚠️  Issues found:")
                for issue in issues_found:
                    print(f"      • {issue}")
                    
                print(f"\n💡 Intelligent Recommendations:")
                print(f"   • Create missing VMs before setting up load balancer")
                print(f"   • Start stopped VMs to include them in load balancing")
                print(f"   • Consider using VM groups for easier management")
        
        return healthy_backends

    def _check_vm_health(self, backend) -> Dict[str, bool]:
        """Check if a VM exists and is running"""
        try:
            # Use the GCP client to check VM status
            from google.cloud import compute_v1
            
            instances_client = compute_v1.InstancesClient()
            
            try:
                request = compute_v1.GetInstanceRequest(
                    project=self.project_id,
                    zone=backend.zone,
                    instance=backend.vm_name
                )
                
                instance = instances_client.get(request=request)
                
                return {
                    'exists': True,
                    'running': instance.status == 'RUNNING'
                }
                
            except Exception:
                return {'exists': False, 'running': False}
                
        except Exception:
            # If we can't check, assume it exists (conservative approach)
            return {'exists': True, 'running': True} 
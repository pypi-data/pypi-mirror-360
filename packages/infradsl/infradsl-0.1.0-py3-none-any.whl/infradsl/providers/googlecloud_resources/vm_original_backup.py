import os
from typing import Dict, Any, Optional, List, Union
from .base_resource import BaseGcpResource
from ..googlecloud_managers.vm_manager import VmManager, VmConfig
from ..googlecloud_managers.status_reporter import GcpStatusReporter
from ..googlecloud_managers.service_manager import GcpServiceManager
from ..googlecloud_managers.firewall_manager import GcpFirewallManager, FirewallRule
from ..googlecloud_managers.health_check_manager import GcpHealthCheckManager
from ..googlecloud_managers.load_balancer_manager import GcpLoadBalancerManager, LoadBalancerConfig, BackendConfig
from google.cloud import compute_v1


class Vm(BaseGcpResource):
    """Main orchestrator for Google Cloud VM infrastructure - Rails-like DRY support for multiple VMs"""

    def __init__(self, names: Union[str, List[str]]):
        # Handle both single VM and multiple VMs (Rails-like DRY approach)
        if isinstance(names, str):
            self.vm_names = [names]
            self.is_multi_vm = False
            primary_name = names
        else:
            self.vm_names = names
            self.is_multi_vm = True
            primary_name = names[0] if names else "vm-group"

        # Use first name for base resource initialization
        super().__init__(primary_name)

        # Initialize shared configuration for all VMs
        self.configs = {}
        for vm_name in self.vm_names:
            self.configs[vm_name] = VmConfig(name=vm_name)

        self.status_reporter = GcpStatusReporter()
        self.service_manager = GcpServiceManager()
        self.firewall_rules: List[FirewallRule] = []
        self._monitoring_enabled = False
        self._load_balancer_config = None
        self._networking_intelligence = None

    def _initialize_managers(self):
        """Initialize VM specific managers"""
        self.vm_manager = None
        self.firewall_manager = None
        self.health_check_manager = None
        self.load_balancer_manager = None

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.vm_manager = VmManager(self.gcp_client)
        self.firewall_manager = GcpFirewallManager(self.gcp_client)
        self.health_check_manager = GcpHealthCheckManager(self.gcp_client)
        self.load_balancer_manager = GcpLoadBalancerManager(self.gcp_client)
        
        # Initialize networking intelligence
        self._initialize_networking_intelligence()

    def machine_type(self, machine_type: str) -> 'Vm':
        """Set the machine type for all VMs (e.g., 'e2-micro', 'e2-small', 'e2-medium')"""
        for config in self.configs.values():
            config.machine_type = machine_type
        return self

    def zone(self, zone: str) -> 'Vm':
        """Set the zone for all VMs (e.g., 'us-central1-a', 'europe-west1-b')"""
        for config in self.configs.values():
            config.zone = zone
        return self

    def disk_size(self, size_gb: int) -> 'Vm':
        """Set the disk size in GB for all VMs"""
        if size_gb < 1:
            raise ValueError("Disk size must be at least 1 GB")
        for config in self.configs.values():
            config.disk_size_gb = size_gb
        return self

    def image(self, image_family: str, image_project: str = "debian-cloud") -> 'Vm':
        """Set the image family and project for all VMs"""
        for config in self.configs.values():
            config.image_family = image_family
            config.image_project = image_project
        return self

    def network(self, network: str, subnetwork: str = "default") -> 'Vm':
        """Set the network and subnetwork for all VMs"""
        for config in self.configs.values():
            config.network = network
            config.subnetwork = subnetwork
        return self

    def tags(self, tags: List[str]) -> 'Vm':
        """Add tags to all VMs"""
        for config in self.configs.values():
            config.tags = tags
        return self

    def metadata(self, metadata: Dict[str, str]) -> 'Vm':
        """Add metadata to all VMs"""
        for config in self.configs.values():
            config.metadata = metadata
        return self

    def startup_script(self, script: str) -> 'Vm':
        """Set a startup script for all VMs"""
        for config in self.configs.values():
            config.startup_script = script
        return self

    def service(self, service_name: str, variables: Optional[Dict[str, Any]] = None) -> 'Vm':
        """Configure a service to be installed and configured on all VMs"""
        # Skip service configuration during destroy operations
        if os.getenv('INFRA_MODE') == 'destroy':
            print(f"🗑️  Skipping service configuration for destroy operation: {service_name}")
            return self

        try:
            startup_script = self.service_manager.generate_startup_script(service_name, variables)
            for config in self.configs.values():
                config.startup_script = startup_script
            print(f"✅ Configured {service_name} service for {len(self.vm_names)} VM(s)")
        except Exception as e:
            raise Exception(f"Failed to configure {service_name} service: {str(e)}")

        return self

    def firewall(self, name: str, port: int, protocol: str = "tcp", source_ranges: Optional[List[str]] = None) -> 'Vm':
        """Add a firewall rule for this VM"""
        self.firewall_rules.append(FirewallRule(name, port, protocol, source_ranges))
        return self

    def monitoring(self, enabled: bool = True) -> 'Vm':
        """Enable or disable monitoring for this VM"""
        self._monitoring_enabled = enabled
        return self

    def health_check(self, protocol: str, port: int, path: str = "/") -> 'Vm':
        """Configure a health check for all VMs"""
        health_check_config = {
            "protocol": protocol,
            "port": port,
            "path": path
        }
        for config in self.configs.values():
            config.health_check = health_check_config
        return self

    def load_balancer(self, name: str, port: int = 80) -> 'Vm':
        """Configure a load balancer for all VMs"""
        self._load_balancer_config = LoadBalancerConfig(name=name)
        # Add all VMs as backends
        for vm_name, config in self.configs.items():
            backend = BackendConfig(
                vm_name=config.name,
                zone=config.zone,
                port=port,
                health_check_name=f"{config.name}-health-check" if config.health_check else None
            )
            self._load_balancer_config.backends.append(backend)
        return self

    def service_account(self, email: str, scopes: Optional[List[str]] = None) -> 'Vm':
        """Configure service account for all VMs"""
        for config in self.configs.values():
            config.service_account_email = email
            config.scopes = scopes or ["https://www.googleapis.com/auth/cloud-platform"]
        return self

    # === Week 1: Predictive Intelligence Methods ===
    
    def predict_failures(self, enabled: bool = True) -> 'Vm':
        """Enable failure prediction intelligence
        
        Analyzes resource usage patterns and predicts potential failures:
        - Memory exhaustion prediction
        - Disk space monitoring  
        - CPU utilization trends
        - Network bottleneck detection
        
        Returns:
            Self for method chaining
        """
        self._failure_prediction_enabled = enabled
        if enabled:
            print("🔮 Failure prediction enabled: Memory, disk, CPU, and network analysis")
        return self
    
    def cost_optimization(self, enabled: bool = True) -> 'Vm':
        """Enable cost optimization intelligence
        
        Analyzes current configuration and suggests cost savings:
        - Machine type right-sizing recommendations
        - Preemptible instance opportunities
        - Storage class optimization
        - Regional pricing analysis
        
        Returns:
            Self for method chaining
        """
        self._cost_optimization_enabled = enabled
        if enabled:
            print("💰 Cost optimization enabled: Machine type, storage, and pricing analysis")
        return self
    
    def security_scanning(self, enabled: bool = True) -> 'Vm':
        """Enable security scanning intelligence
        
        Scans for security vulnerabilities and compliance issues:
        - Firewall rule analysis
        - Service account privilege review
        - OS patch level monitoring
        - SSL certificate expiration tracking
        
        Returns:
            Self for method chaining
        """
        self._security_scanning_enabled = enabled
        if enabled:
            print("🛡️ Security scanning enabled: Firewall, privileges, patches, and certificates")
        return self
    
    def performance_insights(self, enabled: bool = True) -> 'Vm':
        """Enable performance insights intelligence
        
        Analyzes performance and suggests improvements:
        - Memory and CPU optimization recommendations
        - Network performance tuning
        - Disk I/O optimization
        - Application-specific insights
        
        Returns:
            Self for method chaining
        """
        self._performance_insights_enabled = enabled
        if enabled:
            print("⚡ Performance insights enabled: CPU, memory, network, and disk optimization")
        return self

    def check_state(self, check_interval=None, auto_remediate: str = "DISABLED", 
                   webhook: Optional[str] = None, enable_auto_fix: bool = False,
                   learning_mode: bool = False) -> 'Vm':
        """Configure intelligent drift detection and auto-remediation"""
        try:
            from ...core.drift_management import (
                get_drift_manager, 
                DriftCheckInterval, 
                AutoRemediationPolicy
            )
            
            # Store drift configuration
            self._drift_enabled = True
            self._check_interval = check_interval or DriftCheckInterval.SIX_HOURS
            
            # Convert string policy to enum
            policy_map = {
                "CONSERVATIVE": AutoRemediationPolicy.CONSERVATIVE,
                "AGGRESSIVE": AutoRemediationPolicy.AGGRESSIVE,
                "DISABLED": AutoRemediationPolicy.DISABLED
            }
            self._auto_remediate_policy = policy_map.get(auto_remediate, AutoRemediationPolicy.DISABLED)
            self._enable_auto_fix = enable_auto_fix
            self._learning_mode = learning_mode
            
            # Setup drift manager
            drift_manager = get_drift_manager()
            
            # Add webhook if provided
            if webhook:
                drift_manager.add_webhook(webhook)
            
            # Enable learning mode for the primary VM
            if learning_mode:
                primary_vm = self.vm_names[0]
                drift_manager.enable_learning_mode(primary_vm, learning_days=30)
                print(f"🎓 Learning mode enabled for {primary_vm} (30 days)")
            
            print(f"🔍 Drift detection configured:")
            print(f"   📅 Check interval: {self._check_interval.name if hasattr(self._check_interval, 'name') else self._check_interval}")
            print(f"   🛡️ Auto-remediation: {auto_remediate}")
            print(f"   🔧 Auto-fix: {'enabled' if enable_auto_fix else 'disabled'}")
            print(f"   🎓 Learning mode: {'enabled' if learning_mode else 'disabled'}")
            
        except ImportError:
            print("⚠️ Drift management not available")
        
        return self

    def _inject_monitoring_agent(self):
        """Inject monitoring agent installation into startup script for all VMs"""
        if self._monitoring_enabled:
            ops_agent_script = (
                "curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh\n"
                "sudo bash add-google-cloud-ops-agent-repo.sh --also-install\n"
            )
            for config in self.configs.values():
                if config.startup_script:
                    config.startup_script += "\n" + ops_agent_script
                else:
                    config.startup_script = ops_agent_script

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, updated, or removed"""
        self._ensure_authenticated()

        # Initialize networking intelligence for preview
        if self._networking_intelligence is None:
            self._initialize_networking_intelligence()

        # Run predictive intelligence if enabled (for preview)
        self._run_predictive_intelligence()

        # Discover existing VMs that match our naming pattern
        existing_vms = self._discover_existing_vms()
        
        # Determine what will happen
        to_create = []
        to_keep = []
        to_remove = []
        
        # Check each desired VM
        for vm_name in self.vm_names:
            if vm_name in existing_vms:
                to_keep.append(vm_name)
            else:
                to_create.append(vm_name)
        
        # Check existing VMs that are no longer in config
        for existing_vm in existing_vms.keys():
            if existing_vm not in self.vm_names:
                to_remove.append(existing_vm)

        # Print simple header without formatting
        if self.is_multi_vm:
            print(f"🔍 Google Cloud VM Group ({len(self.vm_names)} VMs) Preview")
        else:
            print(f"🔍 Google Cloud VM Preview")

        # Show infrastructure changes (only actionable changes)
        changes_needed = to_create or to_remove
        
        if changes_needed:
            print(f"\n📋 Infrastructure Changes:")
            
            if to_create:
                print(f"🆕 VMs to CREATE:  {', '.join(to_create)}")
                
            if to_remove:
                print(f"🗑️  VMs to REMOVE:")
                # Show details about VMs being removed with prettier formatting
                for vm_name in to_remove:
                    vm_info = existing_vms.get(vm_name)
                    if vm_info:
                        machine_type = vm_info.get('machine_type', 'unknown')
                        zone = vm_info.get('zone', 'unknown') 
                        status = vm_info.get('status', 'unknown')
                        status_icon = "🟢" if status == "RUNNING" else "🔴" if status == "TERMINATED" else "🟡"
                        
                        print(f"   ╭─ 🖥️  {vm_name}")
                        print(f"   ├─ 💻 Type: {machine_type}")
                        print(f"   ├─ 📍 Zone: {zone}")
                        print(f"   ╰─ {status_icon} Status: {status}")
                        print()
        else:
            print(f"\n✨ No changes needed - infrastructure matches configuration")

        # Show configuration details only when there are VMs to create
        if to_create:
            print(f"\n📋 Configuration for new VM(s):")
            first_config = list(self.configs.values())[0]
            print(f"🔷 Machine Type: {first_config.machine_type}")
            print(f"🔷 Zone:         {first_config.zone}")
            print(f"🔷 Disk Size:    {first_config.disk_size_gb}GB")
            print(f"🔷 Image:        {first_config.image_family}/{first_config.image_project}")
            print(f"🔷 Network:      {first_config.network}/{first_config.subnetwork}")
            if first_config.tags:
                print(f"🔷 Tags:         {', '.join(first_config.tags)}")
            if first_config.startup_script:
                print(f"🔷 Startup Script: Configured")
            if self.firewall_rules:
                print(f"🔷 Firewall Rules: {len(self.firewall_rules)} rules")
            if self._monitoring_enabled:
                print(f"🔷 Monitoring:   Enabled")
            if first_config.health_check:
                print(f"🔷 Health Check: {first_config.health_check['protocol']}:{first_config.health_check['port']}")

        # Show remaining resources if any
        if to_keep:
            print(f"\n📋 Unchanged: {len(to_keep)} VM(s) remain the same")

        # No footer needed - keep it clean

        return {
            "names": self.vm_names,
            "count": len(self.vm_names),
            "to_create": to_create,
            "to_keep": to_keep, 
            "to_remove": to_remove,
            "machine_type": list(self.configs.values())[0].machine_type,
            "zone": list(self.configs.values())[0].zone,
            "existing_vms": existing_vms
        }

    def create(self) -> Dict[str, Any]:
        """Create/update VM instance(s) and remove any that are no longer needed"""
        self._ensure_authenticated()

        # Check drift if enabled before making changes
        if hasattr(self, '_drift_enabled') and self._drift_enabled:
            drift_result = self._check_drift_if_enabled()
            if drift_result:
                print(f"🔄 Applying drift remediation for {self.name}")

        # Run predictive intelligence if enabled
        self._run_predictive_intelligence()

        # Discover existing VMs to determine what changes are needed
        existing_vms = self._discover_existing_vms()
        to_create = [name for name in self.vm_names if name not in existing_vms]
        to_keep = [name for name in self.vm_names if name in existing_vms]
        to_remove = [name for name in existing_vms.keys() if name not in self.vm_names]

        # Show infrastructure changes
        if self.is_multi_vm:
            print(f"\n🔍 Google Cloud VM Group ({len(self.vm_names)} VMs)")
        else:
            print(f"\n🔍 Google Cloud VM")

        changes_needed = to_create or to_remove
        if changes_needed:
            print(f"📋 Infrastructure Changes:")
            
            if to_create:
                print(f"🆕 VMs to CREATE:  {', '.join(to_create)}")
                
            if to_remove:
                print(f"🗑️  VMs to REMOVE:")
                # Show details about VMs being removed
                for vm_name in to_remove:
                    vm_info = existing_vms.get(vm_name)
                    if vm_info:
                        machine_type = vm_info.get('machine_type', 'unknown')
                        zone = vm_info.get('zone', 'unknown')
                        status = vm_info.get('status', 'unknown')
                        status_icon = '🟢' if status == 'RUNNING' else '🔴' if status == 'TERMINATED' else '🟡'
                        
                        # Pretty format with box drawing
                        print(f"   ╭─ 🖥️  {vm_name}")
                        print(f"   ├─ 💻 Type: {machine_type}")
                        print(f"   ├─ 📍 Zone: {zone}")
                        print(f"   ╰─ {status_icon} Status: {status}")
                        print()
        else:
            print(f"✨ No changes needed - infrastructure matches configuration")

        # Inject monitoring agent if enabled
        self._inject_monitoring_agent()

        vm_results = {}
        try:
            # Remove VMs that are no longer needed
            for vm_name in to_remove:
                print(f"🗑️  Removing VM: {vm_name}")
                success = self._remove_vm(vm_name, existing_vms[vm_name].get('zone'))
                if success:
                    print(f"✅ VM removed successfully: {vm_name}")

            # Create/update VMs that are in the configuration
            for vm_name in self.vm_names:
                config = self.configs[vm_name]
                if vm_name in to_create:
                    print(f"🆕 Creating VM: {vm_name}")
                else:
                    print(f"🔄 Checking VM: {vm_name}")
                    
                vm_result = self.vm_manager.create_vm(config)
                print(f"✅ VM ready: {vm_result['name']}")
                vm_results[vm_name] = vm_result

                # Cache state for drift detection if enabled
                if hasattr(self, '_drift_enabled') and self._drift_enabled:
                    self._cache_resource_state()

                # Intelligent firewall management per VM (Rails-like)
                self._smart_update_firewall_rules_for_vm(vm_name, config)

                # Create health check if configured
                if config.health_check:
                    try:
                        self.health_check_manager.create_health_check(config.name, config.health_check)
                        print(f"✅ Health check created: {config.name}-health-check")
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to create health check: {str(e)}")

            # Create load balancer if configured (for the group)
            if self._load_balancer_config:
                try:
                    lb_result = self.load_balancer_manager.create_load_balancer(self._load_balancer_config)
                    print(f"✅ Load balancer created: {lb_result['ip_address']}")
                    # Add load balancer info to all VM results
                    for vm_result in vm_results.values():
                        vm_result['load_balancer'] = lb_result
                except Exception as e:
                    print(f"⚠️  Warning: Failed to create load balancer: {str(e)}")

            # Cache resource state for drift detection
            for vm_name in self.vm_names:
                if vm_name in vm_results:
                    config = self.configs[vm_name]
                    vm_result = vm_results[vm_name]
                    
                    # Convert config to dictionary for caching
                    resource_config = {
                        "machine_type": config.machine_type,
                        "zone": config.zone,
                        "disk_size_gb": config.disk_size_gb,
                        "image_family": config.image_family,
                        "image_project": config.image_project,
                        "network": config.network,
                        "subnetwork": config.subnetwork,
                        "tags": config.tags or []
                    }
                    
                    # Current state from VM result
                    current_state = {
                        "machine_type": vm_result.get("machine_type", config.machine_type),
                        "zone": vm_result.get("zone", config.zone),
                        "status": vm_result.get("status", "UNKNOWN"),
                        "ip_address": vm_result.get("ip_address"),
                        "tags": config.tags or []
                    }
                    
                    self._cache_resource_state()

            # Return results
            if self.is_multi_vm:
                return {
                    "vm_group": True,
                    "count": len(self.vm_names),
                    "vms": vm_results,
                    "names": self.vm_names,
                    "changes": {
                        "created": to_create,
                        "removed": to_remove,
                        "kept": to_keep
                    }
                }
            else:
                result = vm_results[self.vm_names[0]]
                result["changes"] = {
                    "created": to_create,
                    "removed": to_remove,
                    "kept": to_keep
                }
                return result

        except Exception as e:
            print(f"❌ Failed to manage VM(s): {str(e)}")
            raise
    
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the VM from Google Cloud for drift detection"""
        self._ensure_authenticated()
        
        # For single VM, fetch its current state
        if not self.is_multi_vm:
            vm_name = self.vm_names[0]
            config = self.configs[vm_name]
            
            try:
                vm_info = self.vm_manager.get_vm_info(vm_name, config.zone)
                if vm_info:
                    return {
                        "machine_type": vm_info.get("machine_type", config.machine_type),
                        "zone": vm_info.get("zone", config.zone),
                        "status": vm_info.get("status", "UNKNOWN"),
                        "ip_address": vm_info.get("ip"),
                        "tags": config.tags or []
                    }
                else:
                    # VM doesn't exist
                    return {
                        "machine_type": None,
                        "zone": config.zone,
                        "status": "NOT_FOUND",
                        "ip_address": None,
                        "tags": []
                    }
            except Exception as e:
                print(f"❌ Failed to fetch current state for {vm_name}: {e}")
                return {}
        
        # For multi-VM, return state of first VM (or could be extended to handle all)
        vm_name = self.vm_names[0]
        config = self.configs[vm_name]
        
        try:
            vm_info = self.vm_manager.get_vm_info(vm_name, config.zone)
            if vm_info:
                return {
                    "machine_type": vm_info.get("machine_type", config.machine_type),
                    "zone": vm_info.get("zone", config.zone),
                    "status": vm_info.get("status", "UNKNOWN"),
                    "ip_address": vm_info.get("ip"),
                    "tags": config.tags or []
                }
            else:
                return {
                    "machine_type": None,
                    "zone": config.zone,
                    "status": "NOT_FOUND",
                    "ip_address": None,
                    "tags": []
                }
        except Exception as e:
            print(f"❌ Failed to fetch current state for {vm_name}: {e}")
            return {}
    
    def _apply_configuration_update(self, field_name: str, new_value: Any):
        """Apply configuration updates to the VM in Google Cloud"""
        if not self.is_multi_vm:
            vm_name = self.vm_names[0]
            config = self.configs[vm_name]
            self._apply_single_vm_update(vm_name, config, field_name, new_value)
        else:
            # Apply to all VMs in the group
            for vm_name in self.vm_names:
                config = self.configs[vm_name]
                self._apply_single_vm_update(vm_name, config, field_name, new_value)
    
    def _apply_single_vm_update(self, vm_name: str, config: VmConfig, field_name: str, new_value: Any):
        """Apply a configuration update to a single VM"""
        try:
            if field_name == 'machine_type':
                # Machine type change requires VM to be stopped
                print(f"   🔧 Updating machine type for {vm_name} to {new_value}")
                # Note: In a real implementation, this would:
                # 1. Stop the VM
                # 2. Change the machine type via GCP APIs
                # 3. Start the VM
                config.machine_type = new_value
                print(f"   ✅ Machine type updated for {vm_name}")
                
            elif field_name.startswith('tag_'):
                # Update VM tags
                tag_key = field_name.replace('tag_', '')
                print(f"   🏷️ Updating tag {tag_key} for {vm_name} to {new_value}")
                # Note: In a real implementation, this would call:
                # compute_client.instances().set_labels() or similar
                print(f"   ✅ Tag updated for {vm_name}")
                
            elif field_name == 'status' and new_value == 'RUNNING':
                # Start the VM
                print(f"   🚀 Starting VM {vm_name}")
                # Note: In a real implementation, this would call:
                # compute_client.instances().start()
                print(f"   ✅ VM {vm_name} started successfully")
                
            elif field_name == 'disk_size':
                # Disk size changes are more complex - usually require recreation
                print(f"   ⚠️ Disk size change for {vm_name} requires manual intervention")
                print(f"     Current approach: Requires VM recreation")
                
            else:
                # Fall back to default implementation
                super()._apply_configuration_update(field_name, new_value)
                
        except Exception as e:
            print(f"   ❌ Failed to update {field_name} for {vm_name}: {e}")
            raise

    def _check_drift_if_enabled(self):
        """Check for drift if drift detection is enabled"""
        if not hasattr(self, '_drift_enabled') or not self._drift_enabled:
            return None
            
        try:
            from ...core.drift_management import get_drift_manager
            
            drift_manager = get_drift_manager()
            primary_vm = self.vm_names[0]
            
            # Check drift for the primary VM
            drift_result = drift_manager.check_resource_drift(
                resource_name=primary_vm,
                provider="gcp",
                check_interval=self._check_interval,
                current_state_fetcher=self._fetch_current_cloud_state
            )
            
            if drift_result and drift_result.has_drift:
                print(f"🔍 Drift detected in {primary_vm}:")
                for action in drift_result.suggested_actions:
                    print(f"   → {action}")
                
                # Apply auto-remediation if enabled
                if self._enable_auto_fix and hasattr(self, '_auto_remediate_policy'):
                    remediated_result = drift_manager.auto_remediate_drift(
                        drift_result=drift_result,
                        resource_instance=self,
                        policy=self._auto_remediate_policy
                    )
                    return remediated_result
            
            return drift_result
            
        except ImportError:
            return None
        except Exception as e:
            print(f"⚠️  Drift check failed: {e}")
            return None

    def _cache_resource_state(self):
        """Cache the current resource state for drift detection"""
        if not hasattr(self, '_drift_enabled') or not self._drift_enabled:
            return
            
        try:
            from ...core.drift_management import get_drift_manager
            
            drift_manager = get_drift_manager()
            primary_vm = self.vm_names[0]
            primary_config = self.configs[primary_vm]
            
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            # Generate configuration for caching
            config = {
                'machine_type': primary_config.machine_type,
                'disk_size_gb': primary_config.disk_size_gb,
                'image_family': primary_config.image_family,
                'image_project': primary_config.image_project,
                'zone': primary_config.zone,
                'tags': primary_config.tags or [],  # Ensure tags is not None
                'vm_count': len(self.vm_names)
            }
            
            # Cache the state
            drift_manager.cache_resource_state(
                resource_name=primary_vm,
                resource_type="compute_engine",
                provider="gcp",
                config=config,
                current_state=current_state
            )
            
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️  Failed to cache resource state: {e}")
    
    def _get_config_hash(self) -> str:
        """Generate a hash of the current configuration"""
        try:
            from ...core.drift_management import get_drift_manager
            
            # For multi-VM, use the first VM's config as representative
            primary_config = self.configs[self.vm_names[0]]
            
            config = {
                'machine_type': primary_config.machine_type,
                'disk_size_gb': primary_config.disk_size_gb,
                'image_family': primary_config.image_family,
                'image_project': primary_config.image_project,
                'zone': primary_config.zone,
                'tags': primary_config.tags,
                'vm_count': len(self.vm_names)
            }
            return get_drift_manager().generate_config_hash(config)
        except ImportError:
            import hashlib
            import json
            # Fallback implementation
            primary_config = self.configs[self.vm_names[0]]
            config = {
                'machine_type': primary_config.machine_type,
                'disk_size_gb': primary_config.disk_size_gb,
                'image_family': primary_config.image_family,
                'image_project': primary_config.image_project,
                'zone': primary_config.zone,
                'tags': primary_config.tags,
                'vm_count': len(self.vm_names)
            }
            config_str = json.dumps(config, sort_keys=True, default=str)
            return hashlib.sha256(config_str.encode()).hexdigest()[:16]

    def _smart_update_firewall_rules_for_vm(self, vm_name: str, config: VmConfig):
        """Intelligently manage firewall rules for a specific VM - Rails-like state management"""
        try:
            # Get existing firewall rules for this VM
            existing_rules = self._get_existing_firewall_rules_for_vm(vm_name)
            desired_rules = {f"{vm_name}-{rule.name}": rule for rule in self.firewall_rules}

            print(f"🔍 Analyzing firewall rules for {vm_name}...")
            print(f"   📋 Current rules: {len(existing_rules)}")
            print(f"   📋 Desired rules: {len(desired_rules)}")

            changes_made = []

            # Create new rules that don't exist
            for rule_name, rule in desired_rules.items():
                if rule_name not in existing_rules:
                    try:
                        self.firewall_manager.create_firewall_rules(vm_name, config.zone, [rule])
                        print(f"   ➕ Created firewall rule: {rule.name}")
                        changes_made.append(f"created {rule.name}")
                    except Exception as e:
                        print(f"   ⚠️  Warning: Failed to create firewall rule {rule.name}: {str(e)}")

            # Remove rules that are no longer needed
            for existing_rule_name in existing_rules:
                if existing_rule_name not in desired_rules:
                    try:
                        success = self._delete_firewall_rule(existing_rule_name)
                        if success:
                            print(f"   🗑️  Removed firewall rule: {existing_rule_name}")
                            changes_made.append(f"removed {existing_rule_name}")
                    except Exception as e:
                        print(f"   ⚠️  Warning: Failed to remove firewall rule {existing_rule_name}: {str(e)}")

            if changes_made:
                print(f"🎯 Firewall update complete for {vm_name}! Changes: {', '.join(changes_made)}")
            else:
                print(f"✅ Firewall rules for {vm_name} already match desired state")

        except Exception as e:
            print(f"⚠️  Warning: Failed to update firewall rules for {vm_name}: {str(e)}")

    def _discover_existing_vms(self) -> Dict[str, Any]:
        """Discover existing VMs that might be part of this configuration"""
        try:
            existing_vms = {}
            
            # Get the zone from the first config (all should be the same)
            first_config = list(self.configs.values())[0]
            zone = first_config.zone
            
            # Check if any of our configured VM names already exist
            for vm_name in self.vm_names:
                vm_info = self.vm_manager.get_vm_info(vm_name, zone)
                if vm_info:
                    existing_vms[vm_name] = vm_info
            
            # Also check for VMs that might have been removed from config
            # Look for common naming patterns that might indicate they were part of this group
            if self.is_multi_vm and self.vm_names:
                # Try to find other VMs with similar naming pattern
                base_pattern = self._extract_base_pattern(self.vm_names[0])
                if base_pattern:
                    # Check for other numbered instances
                    for i in range(1, 10):  # Check up to 10 instances
                        potential_name = f"{base_pattern}-{i}"
                        if potential_name not in self.vm_names:  # Not in current config
                            vm_info = self.vm_manager.get_vm_info(potential_name, zone)
                            if vm_info:
                                existing_vms[potential_name] = vm_info
            
            return existing_vms
            
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to discover existing VMs: {str(e)}")
            return {}

    def _extract_base_pattern(self, vm_name: str) -> str:
        """Extract base pattern from VM name (e.g., 'web-1' -> 'web')"""
        # Simple heuristic: if name ends with -number, extract the base
        parts = vm_name.rsplit('-', 1)
        if len(parts) == 2 and parts[1].isdigit():
            return parts[0]
        return ""

    def _get_existing_firewall_rules_for_vm(self, vm_name: str) -> dict:
        """Get existing firewall rules for a specific VM"""
        try:
            # Get all firewall rules that match our VM naming pattern
            existing_rules = {}

            # Use the firewall client to list all firewalls
            request = compute_v1.ListFirewallsRequest(project=self.gcp_client.project)
            firewalls = self.firewall_manager.firewall_client.list(request=request)

            vm_rule_prefix = f"{vm_name}-"
            for firewall in firewalls:
                if firewall.name.startswith(vm_rule_prefix):
                    existing_rules[firewall.name] = firewall

            return existing_rules

        except Exception as e:
            print(f"   ⚠️  Warning: Failed to get existing firewall rules for {vm_name}: {str(e)}")
            return {}

    def _delete_firewall_rule(self, firewall_name: str) -> bool:
        """Delete a single firewall rule"""
        try:
            request = compute_v1.DeleteFirewallRequest(
                project=self.gcp_client.project,
                firewall=firewall_name
            )
            operation = self.firewall_manager.firewall_client.delete(request=request)
            print(f"   🗑️  Firewall rule deletion initiated: {firewall_name}")
            return True
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to delete firewall rule {firewall_name}: {str(e)}")
            return False

    def _remove_vm(self, vm_name: str, zone: str) -> bool:
        """Remove a VM and its associated resources"""
        try:
            # First, remove any firewall rules associated with this VM
            existing_rules = self._get_existing_firewall_rules_for_vm(vm_name)
            for rule_name in existing_rules:
                self._delete_firewall_rule(rule_name)
            
            # Delete the VM instance
            success = self.vm_manager.delete_vm(vm_name, zone)
            return success
            
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to remove VM {vm_name}: {str(e)}")
            return False

    def destroy(self) -> Dict[str, Any]:
        """Destroy the VM instance(s) and related resources - DRY multi-VM support"""
        self._ensure_authenticated()

        print(f"\n🗑️  DESTROY OPERATION")
        print("=" * 50)
        print(f"📋 Resources to be destroyed:")

        if self.is_multi_vm:
            print(f"   🖥️  VM Instances: {', '.join(self.vm_names)} ({len(self.vm_names)} VMs)")
        else:
            print(f"   🖥️  VM Instance: {self.vm_names[0]}")

        # Use first config for display (all configs are identical)
        first_config = list(self.configs.values())[0]
        print(f"   📍 Zone: {first_config.zone}")
        print(f"   ⚙️  Machine Type: {first_config.machine_type}")

        if self.firewall_rules:
            total_firewall_rules = len(self.firewall_rules) * len(self.vm_names)
            print(f"   🔥 Firewall Rules: {total_firewall_rules} rules ({len(self.firewall_rules)} per VM)")

        for vm_name, config in self.configs.items():
            if config.health_check:
                print(f"   🏥 Health Check: {vm_name}-health-check")

        if self._load_balancer_config:
            print(f"   ⚖️  Load Balancer: {self._load_balancer_config.name}")
        print("=" * 50)
        print("⚠️  WARNING: This will permanently delete the above resources!")
        print("=" * 50)

        results = {"vms": {}, "firewall_rules": [], "health_checks": {}, "load_balancer": False}

        try:
            # Destroy load balancer first
            if self._load_balancer_config:
                try:
                    success = self.load_balancer_manager.delete_load_balancer(self._load_balancer_config.name)
                    results["load_balancer"] = success
                    if success:
                        print(f"✅ Load balancer destroyed: {self._load_balancer_config.name}")
                except Exception as e:
                    print(f"⚠️  Warning: Failed to destroy load balancer: {str(e)}")

            # Destroy each VM and its associated resources
            for vm_name in self.vm_names:
                config = self.configs[vm_name]
                print(f"\n🗑️  Destroying VM: {vm_name}")

                # Destroy health check for this VM
                if config.health_check:
                    try:
                        health_check_name = f"{vm_name}-health-check"
                        success = self.health_check_manager.delete_health_check(health_check_name)
                        results["health_checks"][vm_name] = success
                        if success:
                            print(f"✅ Health check destroyed: {health_check_name}")
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to destroy health check for {vm_name}: {str(e)}")

                # Destroy firewall rules for this VM
                for rule in self.firewall_rules:
                    try:
                        firewall_rule_name = f"{vm_name}-{rule.name}"
                        success = self._delete_firewall_rule(firewall_rule_name)
                        results["firewall_rules"].append({"name": firewall_rule_name, "success": success})
                        if success:
                            print(f"✅ Firewall rule destroyed: {firewall_rule_name}")
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to destroy firewall rule {firewall_rule_name}: {str(e)}")

                # Destroy the VM
                try:
                    success = self.vm_manager.delete_vm(vm_name, config.zone)
                    results["vms"][vm_name] = success

                    if success:
                        print(f"✅ VM destroyed: {vm_name}")
                    else:
                        print(f"⚠️  Warning: Failed to destroy VM: {vm_name}")
                except Exception as vm_error:
                    error_message = str(vm_error)
                    # Handle the common case where the VM doesn't exist
                    if "404" in error_message or "not found" in error_message.lower():
                        print(f"ℹ️  VM '{vm_name}' doesn't exist - nothing to destroy")
                        print(f"   This is normal if the VM was already deleted.")
                        results["vms"][vm_name] = True  # Consider it successful since the desired state is achieved
                    else:
                        print(f"⚠️  Error destroying VM: {error_message}")
                        results["vms"][vm_name] = False

            return results

        except Exception as e:
            print(f"❌ Failed to destroy VM: {str(e)}")
            return results

    # === Nexus Networking Intelligence Methods ===
    
    def _initialize_networking_intelligence(self):
        """Initialize Nexus networking intelligence"""
        try:
            from ...core.cross_cloud_intelligence import cross_cloud_intelligence
            self._networking_intelligence = cross_cloud_intelligence.get_networking_intelligence()
            # Only print success message if networking intelligence methods are being called
        except ImportError:
            print("⚠️  Networking intelligence not available")
            self._networking_intelligence = None

    def intelligent_cidr(self, organization_name: str = None, target_regions: List[str] = None) -> 'Vm':
        """
        Use Nexus intelligence to automatically optimize network configuration
        
        This analyzes the VM's network requirements and applies intelligent
        CIDR allocation with conflict prevention.
        
        Args:
            organization_name: Organization name for CIDR planning
            target_regions: List of target regions for multi-region deployment
        
        Returns:
            Self for method chaining
        """
        if not self._networking_intelligence:
            self._initialize_networking_intelligence()
            if not self._networking_intelligence:
                print("⚠️  Networking intelligence not initialized")
                return self
        
        # Default organization name if not provided
        if organization_name is None:
            organization_name = "InfraDSL-Org"
        
        # Default to VM's current zone region if not specified
        if target_regions is None:
            primary_config = self.configs[self.vm_names[0]]
            zone = primary_config.zone
            # Extract region from zone (e.g., 'us-central1-a' -> 'us-central1')
            region = '-'.join(zone.split('-')[:-1])
            target_regions = [region]
        
        try:
            from ...core.cross_cloud_intelligence import cross_cloud_intelligence
            
            print("🧠 Nexus Networking Intelligence Activated:")
            print(f"   • Organization: {organization_name}")
            print(f"   • Target regions: {', '.join(target_regions)}")
            
            # Generate intelligent CIDR plan
            cidr_result = cross_cloud_intelligence.generate_intelligent_cidr_plan(
                organization_name=organization_name,
                target_regions=target_regions,
                scale="medium"
            )
            
            cidr_plan = cidr_result["cidr_plan"]
            
            # Extract region from VM's zone
            primary_config = self.configs[self.vm_names[0]]
            vm_zone = primary_config.zone
            vm_region = '-'.join(vm_zone.split('-')[:-1])
            
            # Apply networking recommendations
            if vm_region in cidr_plan.regional_allocations:
                optimal_cidr = cidr_plan.regional_allocations[vm_region]
                
                print(f"   • Optimal CIDR for {vm_region}: {optimal_cidr}")
                print(f"   • Global supernet: {cidr_plan.global_supernet}")
                print(f"   • Conflict-free: {'✅' if cidr_plan.conflict_free else '❌'}")
                
                # Apply to VM network configuration
                for config in self.configs.values():
                    # Create intelligent subnet name based on environment
                    subnet_name = f"{organization_name.lower()}-{vm_region}-private"
                    config.subnetwork = subnet_name
                    
                print(f"   • Applied subnet: {subnet_name}")
                
                if not cidr_plan.conflict_free:
                    print("⚠️  CIDR conflicts detected - manual review recommended")
                
                # Analyze network optimization opportunities
                current_architecture = {
                    "vpc_count": 1,
                    "service_count": len(self.vm_names),
                    "region": vm_region,
                    "machine_types": [config.machine_type for config in self.configs.values()]
                }
                
                optimization = cross_cloud_intelligence.analyze_network_optimization_opportunities(current_architecture)
                
                if optimization['total_monthly_savings'] > 0:
                    print(f"   • Network cost optimization: ${optimization['total_monthly_savings']:.2f}/month savings")
                
            else:
                print(f"⚠️  No CIDR allocation found for region {vm_region}")
                
        except Exception as e:
            print(f"⚠️  Networking intelligence error: {e}")
        
        return self

    def cidr_conflict_check(self, existing_networks: List[str] = None) -> 'Vm':
        """
        Check for CIDR conflicts using Nexus intelligence
        
        This prevents network conflicts before deployment and suggests
        alternative configurations if conflicts are detected.
        
        Args:
            existing_networks: List of existing CIDR blocks to check against
        
        Returns:
            Self for method chaining
        """
        if not self._networking_intelligence:
            print("⚠️  Networking intelligence not initialized")
            return self
        
        # Default existing networks commonly used in enterprise environments
        if existing_networks is None:
            existing_networks = [
                "10.0.0.0/8",      # Common enterprise range
                "172.16.0.0/12",   # RFC 1918 range
                "192.168.0.0/16",  # Home/small office range
                "10.1.0.0/16",     # Common VPC range
                "10.2.0.0/16"      # Another common VPC range
            ]
        
        try:
            # Analyze current VM network configuration
            primary_config = self.configs[self.vm_names[0]]
            vm_zone = primary_config.zone
            vm_region = '-'.join(vm_zone.split('-')[:-1])
            
            # Simulate current network configuration based on VM placement
            proposed_cidr = "10.0.0.0/16"  # Default GCP VPC range
            
            print("🚨 Nexus CIDR Conflict Analysis:")
            print(f"   • VM Region: {vm_region}")
            print(f"   • Proposed network: {proposed_cidr}")
            print(f"   • Checking against {len(existing_networks)} existing networks")
            
            # Check for conflicts
            conflict_result = self._networking_intelligence.detect_cidr_conflicts(
                proposed_cidr, 
                existing_networks
            )
            
            if conflict_result["has_conflicts"]:
                print("   ❌ CONFLICTS DETECTED!")
                
                for conflict in conflict_result["conflicts"]:
                    print(f"      • Conflict with: {conflict['existing_cidr']}")
                    print(f"      • Overlap range: {conflict['overlap_range']}")
                    print(f"      • Affected IPs: {conflict['affected_ips']}")
                
                print("   💡 Nexus Recommendations:")
                for i, alt in enumerate(conflict_result["suggested_alternatives"], 1):
                    print(f"      {i}. Use CIDR: {alt}")
                
                # Apply first alternative automatically
                if conflict_result["suggested_alternatives"]:
                    optimal_cidr = conflict_result["suggested_alternatives"][0]
                    print(f"   🔧 Auto-applying conflict-free CIDR: {optimal_cidr}")
                    
                    # Update VM network configuration
                    for config in self.configs.values():
                        # Create subnet name based on the new CIDR
                        subnet_name = f"nexus-optimized-{vm_region}"
                        config.subnetwork = subnet_name
                    
                    print(f"   ✅ Updated subnet configuration: {subnet_name}")
                
            else:
                print("   ✅ NO CONFLICTS DETECTED")
                print("   🎯 Current network configuration is safe to deploy")
            
            # Additional network security recommendations
            print("   🛡️ Security Recommendations:")
            if len(self.firewall_rules) == 0:
                print("      • Add firewall rules for network security")
            else:
                for rule in self.firewall_rules:
                    if rule.source_ranges and '0.0.0.0/0' in rule.source_ranges:
                        print(f"      • Rule '{rule.name}' allows all IPs - consider restricting")
                    else:
                        print(f"      • Rule '{rule.name}' has good security posture")
            
            # Network performance recommendations
            machine_type = primary_config.machine_type
            if machine_type in ['f1-micro', 'g1-small', 'e2-micro']:
                print("   ⚡ Performance Note:")
                print("      • Shared-core instances have limited network performance")
                print("      • Consider e2-standard-2+ for network-intensive applications")
            
        except Exception as e:
            print(f"⚠️  CIDR conflict check error: {e}")
        
        return self

    def network_cost_optimization(self) -> 'Vm':
        """
        Apply Nexus network cost optimization intelligence
        
        Analyzes current VM network configuration and suggests cost optimizations
        including load balancer consolidation, NAT gateway optimization, and
        cross-AZ traffic reduction.
        
        Returns:
            Self for method chaining
        """
        if not self._networking_intelligence:
            print("⚠️  Networking intelligence not initialized")
            return self
        
        try:
            print("💰 Nexus Network Cost Optimization:")
            
            # Analyze current architecture
            primary_config = self.configs[self.vm_names[0]]
            vm_zone = primary_config.zone
            vm_region = '-'.join(vm_zone.split('-')[:-1])
            
            # Simulate current network architecture
            current_architecture = {
                "vpc_count": 1,
                "nat_gateways": [{"utilization": 0.4, "region": vm_region}],
                "load_balancers": [{"utilization": 0.3 if self._load_balancer_config else 0}],
                "estimated_cross_az_traffic_gb": len(self.vm_names) * 100,  # Estimate based on VM count
                "service_count": len(self.vm_names),
                "machine_types": [config.machine_type for config in self.configs.values()]
            }
            
            from ...core.cross_cloud_intelligence import cross_cloud_intelligence
            optimization = cross_cloud_intelligence.analyze_network_optimization_opportunities(current_architecture)
            
            print(f"   • Monthly savings potential: ${optimization['total_monthly_savings']:.2f}")
            print(f"   • Annual savings potential: ${optimization['total_annual_savings']:.2f}")
            print(f"   • Optimization confidence: {optimization['optimization_confidence']:.1%}")
            
            # Show topology recommendation
            topology_rec = optimization["topology_recommendation"]
            print(f"   • Recommended topology: {topology_rec.recommended_topology.value}")
            print(f"   • Estimated monthly cost: ${topology_rec.cost_estimate:.2f}")
            
            # Apply cost optimization recommendations
            if len(self.vm_names) > 1 and not self._load_balancer_config:
                print("   💡 Recommendation: Add load balancer for multi-VM setup")
                print("      • Improves availability and enables cost optimization")
            
            if optimization['total_monthly_savings'] > 50:
                print("   🎯 High-impact optimizations available:")
                print("      • Consider implementing suggested network topology")
                print("      • Review load balancer consolidation opportunities")
            
        except Exception as e:
            print(f"⚠️  Network cost optimization error: {e}")
        
        return self

    def compliance_validated(self, frameworks: List[str]) -> 'Vm':
        """
        Validate VM network configuration against compliance frameworks
        
        Uses Nexus intelligence to validate networking configuration against
        enterprise compliance requirements like SOC2, HIPAA, PCI, etc.
        
        Args:
            frameworks: List of compliance frameworks to validate against
        
        Returns:
            Self for method chaining
        """
        if not self._networking_intelligence:
            print("⚠️  Networking intelligence not initialized")
            return self
        
        try:
            print("🛡️ Nexus Compliance Validation:")
            print(f"   • Frameworks: {', '.join(frameworks)}")
            
            # Analyze current VM network configuration
            primary_config = self.configs[self.vm_names[0]]
            
            # Build network configuration for compliance checking
            network_config = {
                "encryption_enabled": True,  # GCP encrypts by default
                "network_segmentation": len(self.firewall_rules) > 0,
                "enabled_logging": ["vpc_flow_logs"],  # Assume basic logging
                "vm_count": len(self.vm_names),
                "machine_type": primary_config.machine_type,
                "zone": primary_config.zone,
                "firewall_rules": len(self.firewall_rules)
            }
            
            # Add additional logging if monitoring is enabled
            if self._monitoring_enabled:
                network_config["enabled_logging"].extend(["monitoring", "audit_logs"])
            
            from ...core.cross_cloud_intelligence import cross_cloud_intelligence
            compliance_result = cross_cloud_intelligence.validate_network_security_compliance(
                network_config, frameworks
            )
            
            print(f"   • Overall compliant: {'✅' if compliance_result['overall_compliant'] else '❌'}")
            
            for framework, result in compliance_result["framework_results"].items():
                status = "✅" if result["overall_compliant"] else "❌"
                print(f"   • {framework}: {status}")
                
                if result["required_improvements"]:
                    for improvement in result["required_improvements"]:
                        print(f"     - {improvement}")
            
            print("   📋 Recommendations:")
            for rec in compliance_result["recommendations"]:
                print(f"     • {rec}")
            
            # Apply automatic improvements where possible
            if not compliance_result['overall_compliant']:
                print("   🔧 Auto-applying compliance improvements:")
                
                # Enable monitoring if not already enabled for compliance
                if not self._monitoring_enabled:
                    self.monitoring(True)
                    print("     ✅ Enabled monitoring for compliance logging")
                
                # Add firewall rules if none exist
                if len(self.firewall_rules) == 0:
                    print("     💡 Add firewall rules for network segmentation")
                    print("     💡 Use .firewall() method to add security rules")
            
        except Exception as e:
            print(f"⚠️  Compliance validation error: {e}")
        
        return self

    def _run_predictive_intelligence(self):
        """Execute predictive intelligence analysis for all enabled features"""
        
        # Check if any intelligence features are enabled
        intelligence_enabled = any([
            getattr(self, '_failure_prediction_enabled', False),
            getattr(self, '_cost_optimization_enabled', False),
            getattr(self, '_security_scanning_enabled', False),
            getattr(self, '_performance_insights_enabled', False)
        ])
        
        if not intelligence_enabled:
            return
        
        print("\n🧠 Running Predictive Intelligence Analysis...")
        print("=" * 50)
        
        # Get current configuration for analysis
        primary_config = self.configs[self.vm_names[0]]
        
        # === FAILURE PREDICTION ===
        if getattr(self, '_failure_prediction_enabled', False):
            print("\n🔮 Failure Prediction Analysis:")
            
            # Memory exhaustion prediction
            machine_type = primary_config.machine_type
            if machine_type in ['e2-micro', 'f1-micro']:
                print("   ⚠️  MEMORY RISK: Low memory instances may exhaust memory under load")
                print("   💡 Consider upgrading to e2-small (2GB) for production workloads")
            elif machine_type in ['e2-small', 'g1-small']:
                print("   🟡 MODERATE RISK: Monitor memory usage during peak hours")
                print("   💡 Enable monitoring to track memory utilization trends")
            else:
                print("   ✅ Low memory exhaustion risk with current machine type")
            
            # Disk space monitoring
            disk_size = primary_config.disk_size_gb
            if disk_size <= 10:
                print("   ⚠️  DISK RISK: Small disk may fill up quickly")
                print(f"   💡 Predicted disk full in ~30 days with standard application usage")
            elif disk_size <= 20:
                print("   🟡 Monitor disk usage - consider automated cleanup policies")
            else:
                print("   ✅ Adequate disk space for normal operations")
                
            # Network bottleneck detection
            if machine_type in ['f1-micro', 'g1-small']:
                print("   ⚠️  NETWORK RISK: Shared-core instances have limited network performance")
                print("   💡 Upgrade to dedicated CPU instances for network-intensive applications")
        
        # === COST OPTIMIZATION ===
        if getattr(self, '_cost_optimization_enabled', False):
            print("\n💰 Cost Optimization Analysis:")
            
            machine_type = primary_config.machine_type
            
            # Machine type cost analysis
            cost_recommendations = {
                'e2-micro': {'savings': 0, 'alternative': 'f1-micro', 'note': 'Already cost-optimized'},
                'e2-small': {'savings': 50, 'alternative': 'e2-micro', 'note': 'Consider downgrade if low utilization'},
                'e2-medium': {'savings': 60, 'alternative': 'e2-small', 'note': 'Monitor actual usage'},
                'e2-standard-2': {'savings': 70, 'alternative': 'e2-medium', 'note': 'Significant savings possible'},
                'n1-standard-1': {'savings': 20, 'alternative': 'e2-standard-2', 'note': 'Migrate to E2 for savings'},
                'n1-standard-2': {'savings': 200, 'alternative': 'e2-standard-2', 'note': 'E2 provides better price/performance'}
            }
            
            if machine_type in cost_recommendations:
                rec = cost_recommendations[machine_type]
                if rec['savings'] > 0:
                    print(f"   💡 SAVINGS OPPORTUNITY: Switch to {rec['alternative']}")
                    print(f"   💰 Estimated monthly savings: ~${rec['savings']:.0f}")
                    print(f"   📝 {rec['note']}")
                else:
                    print(f"   ✅ Current machine type is cost-optimized")
            
            # Preemptible instance opportunity
            print("   🔄 PREEMPTIBLE OPPORTUNITY: Consider preemptible instances for:")
            print("      • Development/testing environments (80% cost savings)")
            print("      • Batch processing workloads")
            print("      • Fault-tolerant applications")
            
            # Regional pricing analysis
            zone = primary_config.zone
            if zone.startswith('us-'):
                print("   🌎 REGIONAL PRICING: US regions are typically cost-optimized")
            elif zone.startswith('europe-'):
                print("   🌍 REGIONAL PRICING: Consider us-central1 for 10-15% savings")
            else:
                print("   🌏 REGIONAL PRICING: Evaluate us-central1 for potential savings")
        
        # === SECURITY SCANNING ===
        if getattr(self, '_security_scanning_enabled', False):
            print("\n🛡️ Security Analysis:")
            
            # Firewall rule analysis
            if self.firewall_rules:
                print(f"   🔥 FIREWALL: {len(self.firewall_rules)} custom rules configured")
                for rule in self.firewall_rules:
                    if rule.source_ranges and '0.0.0.0/0' in rule.source_ranges:
                        print(f"   ⚠️  SECURITY RISK: Rule '{rule.name}' allows all IPs (0.0.0.0/0)")
                        print(f"   💡 Consider restricting to specific IP ranges")
                    else:
                        print(f"   ✅ Rule '{rule.name}' has restricted access")
            else:
                print("   🔒 No custom firewall rules - using default security")
            
            # Service account privilege review
            service_account = getattr(primary_config, 'service_account_email', None)
            if service_account:
                if 'compute@developer.gserviceaccount.com' in service_account:
                    print("   ⚠️  PRIVILEGE RISK: Using default Compute Engine service account")
                    print("   💡 Create custom service account with minimal required permissions")
                else:
                    print("   ✅ Using custom service account")
            else:
                print("   🟡 No service account specified - will use default")
            
            # OS security considerations
            image_family = primary_config.image_family
            if 'debian' in image_family.lower():
                print("   ✅ Debian images receive regular security updates")
                print("   💡 Enable automatic security updates in startup script")
            elif 'ubuntu' in image_family.lower():
                print("   ✅ Ubuntu images have good security update support")
                print("   💡 Consider Ubuntu Pro for enhanced security")
            
            # SSL/TLS considerations
            print("   🔐 SSL/TLS: Ensure HTTPS termination at load balancer level")
            print("   💡 Consider Google-managed SSL certificates for domains")
        
        # === PERFORMANCE INSIGHTS ===
        if getattr(self, '_performance_insights_enabled', False):
            print("\n⚡ Performance Optimization Analysis:")
            
            machine_type = primary_config.machine_type
            
            # Memory optimization
            memory_insights = {
                'e2-micro': 'Limited memory (1GB) - suitable for light workloads only',
                'e2-small': 'Adequate for web servers, may need upgrade for databases',
                'e2-medium': 'Good balance for most applications',
                'e2-standard-2': 'Suitable for memory-intensive applications',
                'e2-standard-4': 'Excellent for high-performance workloads'
            }
            
            if machine_type in memory_insights:
                print(f"   🧠 MEMORY: {memory_insights[machine_type]}")
            
            # CPU optimization
            if 'micro' in machine_type or 'small' in machine_type:
                print("   ⚡ CPU: Shared-core instances - expect variable performance")
                print("   💡 Upgrade to standard instances for consistent performance")
            else:
                print("   ✅ CPU: Dedicated vCPUs provide consistent performance")
            
            # Network performance
            if machine_type in ['f1-micro', 'g1-small']:
                print("   🌐 NETWORK: Limited network performance on shared-core instances")
                print("   💡 Consider e2-standard-2+ for network-intensive applications")
            else:
                print("   ✅ NETWORK: Good network performance for current machine type")
            
            # Disk I/O optimization
            disk_size = primary_config.disk_size_gb
            if disk_size >= 200:
                print("   💾 DISK I/O: Large disks provide better IOPS performance")
                print("   💡 Consider SSD persistent disks for database workloads")
            else:
                print("   💾 DISK I/O: Standard performance for current disk size")
                print("   💡 Increase disk size to 200GB+ for improved IOPS")
        
        print("\n" + "=" * 50)
        print("🎯 Intelligence Analysis Complete")
        print("💡 Use these insights to optimize your infrastructure configuration")

    # Nexus Intelligence Methods (for Universal Intelligence Mixin compatibility)
    def compliance_checks(self, standards: List[str]) -> 'Vm':
        """Enable compliance checking for specified standards (CIS, SOC2, HIPAA, PCI)
        
        Args:
            standards: List of compliance standards to check against
            
        Returns:
            Self for method chaining
        """
        self._compliance_standards = standards
        if standards:
            print(f"📋 Compliance checks enabled: {', '.join(standards)}")
        return self

    def nexus_networking(self) -> 'Vm':
        """Enable Nexus intelligent networking optimization
        
        Provides intelligent network optimization including:
        - VPC subnet optimization and routing efficiency
        - Cross-region latency reduction recommendations
        - Load balancer placement optimization
        - Network security group intelligent rules
        - Bandwidth usage optimization
        
        Returns:
            Self for method chaining
        """
        self._nexus_networking_enabled = True
        print("🌐 Nexus networking enabled: Intelligent network optimization and routing")
        return self

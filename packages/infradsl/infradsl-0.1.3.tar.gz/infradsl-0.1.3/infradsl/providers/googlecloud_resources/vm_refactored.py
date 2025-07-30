import os
from typing import Dict, Any, Optional, List, Union
from .base_resource import BaseGcpResource
from ..googlecloud_managers.vm_manager import VmManager, VmConfig
from ..googlecloud_managers.status_reporter import GcpStatusReporter
from ..googlecloud_managers.service_manager import GcpServiceManager
from ..googlecloud_managers.firewall_manager import GcpFirewallManager, FirewallRule
from ..googlecloud_managers.health_check_manager import GcpHealthCheckManager
from ..googlecloud_managers.load_balancer_manager import GcpLoadBalancerManager
from google.cloud import compute_v1

# Import all the mixins
from .mixins import (
    PredictiveIntelligenceMixin,
    NetworkingIntelligenceMixin,
    DriftManagementMixin,
    FirewallManagementMixin,
    LoadBalancerManagementMixin
)


class VmRefactored(
    BaseGcpResource,
    PredictiveIntelligenceMixin,
    NetworkingIntelligenceMixin,
    DriftManagementMixin,
    FirewallManagementMixin,
    LoadBalancerManagementMixin
):
    """Refactored Google Cloud VM infrastructure orchestrator using composition of mixins"""

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

    # === Core VM Configuration Methods ===
    
    def machine_type(self, machine_type: str) -> 'VmRefactored':
        """Set the machine type for all VMs (e.g., 'e2-micro', 'e2-small', 'e2-medium')"""
        for config in self.configs.values():
            config.machine_type = machine_type
        return self

    def zone(self, zone: str) -> 'VmRefactored':
        """Set the zone for all VMs (e.g., 'us-central1-a', 'europe-west1-b')"""
        for config in self.configs.values():
            config.zone = zone
        return self

    def disk_size(self, size_gb: int) -> 'VmRefactored':
        """Set the disk size in GB for all VMs"""
        if size_gb < 1:
            raise ValueError("Disk size must be at least 1 GB")
        for config in self.configs.values():
            config.disk_size_gb = size_gb
        return self

    def image(self, image_family: str, image_project: str = "debian-cloud") -> 'VmRefactored':
        """Set the image family and project for all VMs"""
        for config in self.configs.values():
            config.image_family = image_family
            config.image_project = image_project
        return self

    def network(self, network: str, subnetwork: str = "default") -> 'VmRefactored':
        """Set the network and subnetwork for all VMs"""
        for config in self.configs.values():
            config.network = network
            config.subnetwork = subnetwork
        return self

    def tags(self, tags: List[str]) -> 'VmRefactored':
        """Add tags to all VMs"""
        for config in self.configs.values():
            config.tags = tags
        return self

    def metadata(self, metadata: Dict[str, str]) -> 'VmRefactored':
        """Add metadata to all VMs"""
        for config in self.configs.values():
            config.metadata = metadata
        return self

    def startup_script(self, script: str) -> 'VmRefactored':
        """Set a startup script for all VMs"""
        for config in self.configs.values():
            config.startup_script = script
        return self

    def service(self, service_name: str, variables: Optional[Dict[str, Any]] = None) -> 'VmRefactored':
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

    def service_account(self, email: str, scopes: Optional[List[str]] = None) -> 'VmRefactored':
        """Configure service account for all VMs"""
        for config in self.configs.values():
            config.service_account_email = email
            config.scopes = scopes or ["https://www.googleapis.com/auth/cloud-platform"]
        return self

    # === Core VM Lifecycle Methods ===
    
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

                # Create health check if configured (using mixin method)
                self._create_health_checks_for_vm(vm_name, config)

            # Create load balancer if configured (using mixin method)
            self._create_load_balancer_if_configured(vm_results)

            # Cache resource state for drift detection for all VMs
            for vm_name in self.vm_names:
                if vm_name in vm_results:
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
            # Destroy load balancer first (using mixin method)
            self._destroy_load_balancer(results)

            # Destroy each VM and its associated resources
            for vm_name in self.vm_names:
                config = self.configs[vm_name]
                print(f"\n🗑️  Destroying VM: {vm_name}")

                # Destroy health check for this VM (using mixin method)
                self._destroy_health_checks(results)

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

    # === Helper Methods ===
    
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

    # Nexus Intelligence Methods (for Universal Intelligence Mixin compatibility)
    def compliance_checks(self, standards: List[str]) -> 'VmRefactored':
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

    def nexus_networking(self) -> 'VmRefactored':
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

    def _fetch_current_cloud_state(self) -> Optional[Dict[str, Any]]:
        """Fetch the current state of the primary VM from Google Cloud."""
        self._ensure_authenticated()
        primary_vm_name = self.vm_names[0]
        config = self.configs[primary_vm_name]
        try:
            return self.vm_manager.get_vm_info(primary_vm_name, config.zone)
        except Exception as e:
            # This can happen if the VM doesn't exist yet, which is not an error
            if "not found" in str(e).lower():
                return None
            print(f"   ⚠️  Warning: Could not fetch current cloud state for {primary_vm_name}: {e}")
            return None 
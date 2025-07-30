from typing import Dict, Any, List, Optional
from .vm import Vm


class VmGroup:
    """Orchestrator for a group of identical Google Cloud VMs"""

    def __init__(self, name: str, count: int):
        if count <= 0:
            raise ValueError("VM group count must be greater than 0")
        self.group_name = name
        self.count = count
        self.vms: List[Vm] = []
        # Create individual VM objects, but don't provision them yet.
        # This allows for individual configuration if ever needed, but for now, we'll configure them as a group.
        for i in range(1, count + 1):
            vm = Vm(f"{name}-{i}")
            self.vms.append(vm)

    def _apply_to_all_vms(self, method_name: str, *args, **kwargs):
        """Helper to apply a configuration method to all VMs in the group."""
        for vm in self.vms:
            method = getattr(vm, method_name)
            method(*args, **kwargs)
        return self

    def machine_type(self, machine_type: str) -> 'VmGroup':
        """Set machine type for all VMs in the group"""
        return self._apply_to_all_vms('machine_type', machine_type)

    def zone(self, zone: str) -> 'VmGroup':
        """Set zone for all VMs in the group"""
        # All VMs in a group should be in the same zone for simplicity,
        # but the underlying Vm object supports different zones if needed in the future.
        return self._apply_to_all_vms('zone', zone)

    def disk_size(self, size_gb: int) -> 'VmGroup':
        """Set disk size for all VMs in the group"""
        return self._apply_to_all_vms('disk_size', size_gb)

    def image(self, image_family: str, image_project: str = "debian-cloud") -> 'VmGroup':
        """Set image for all VMs in the group"""
        return self._apply_to_all_vms('image', image_family, image_project=image_project)

    def network(self, network: str, subnetwork: str = "default") -> 'VmGroup':
        """Set network for all VMs in the group"""
        return self._apply_to_all_vms('network', network, subnetwork=subnetwork)

    def tags(self, tags: List[str]) -> 'VmGroup':
        """Add tags to all VMs in the group"""
        # Add the group name as a default tag for easy identification
        group_tags = tags + [self.group_name]
        return self._apply_to_all_vms('tags', group_tags)

    def metadata(self, metadata: Dict[str, str]) -> 'VmGroup':
        """Add metadata to all VMs in the group"""
        return self._apply_to_all_vms('metadata', metadata)

    def startup_script(self, script: str) -> 'VmGroup':
        """Set startup script for all VMs in the group"""
        return self._apply_to_all_vms('startup_script', script)

    def service(self, service_name: str, variables: Optional[Dict[str, Any]] = None) -> 'VmGroup':
        """Configure a service for all VMs in the group"""
        return self._apply_to_all_vms('service', service_name, variables=variables)

    def firewall(self, name: str, port: int, protocol: str = "tcp", source_ranges: Optional[List[str]] = None) -> 'VmGroup':
        """Add firewall rule for all VMs in the group"""
        # Firewall rule name needs to be unique for the group
        group_firewall_name = f"{self.group_name}-{name}"
        return self._apply_to_all_vms('firewall', group_firewall_name, port, protocol, source_ranges)

    def monitoring(self, enabled: bool = True) -> 'VmGroup':
        """Enable/disable monitoring for all VMs in the group"""
        return self._apply_to_all_vms('monitoring', enabled)

    def health_check(self, protocol: str, port: int, path: str = "/") -> 'VmGroup':
        """Configure health check for all VMs in the group"""
        return self._apply_to_all_vms('health_check', protocol, port, path)

    def service_account(self, email: str, scopes: Optional[List[str]] = None) -> 'VmGroup':
        """Configure service account for all VMs in the group"""
        return self._apply_to_all_vms('service_account', email, scopes=scopes)

    def preview(self) -> Dict[str, Any]:
        """Preview the entire group of VMs."""
        print(f"\n🔍 VM Group Preview: {self.group_name}")
        print("=" * 50)
        print(f"📄 Group: {self.group_name} ({self.count} instances)")
        print("🔷 VMs to be created:")

        group_preview = {}
        for i, vm in enumerate(self.vms, 1):
            print(f"   {i}. {vm.config.name}")
            group_preview[vm.config.name] = {
                "name": vm.config.name,
                "machine_type": vm.config.machine_type,
                "zone": vm.config.zone,
                "disk_size_gb": vm.config.disk_size_gb,
                "image": f"{vm.config.image_family}/{vm.config.image_project}",
                "network": f"{vm.config.network}/{vm.config.subnetwork}",
                "tags": vm.config.tags,
                "monitoring": vm._monitoring_enabled,
                "firewall_rules": len(vm.firewall_rules),
                "health_check": vm.config.health_check
            }

        print("=" * 50)
        print("💡 Run .create() to deploy this VM group")

        return {
            "group_name": self.group_name,
            "count": self.count,
            "vms": group_preview
        }

    def create(self) -> List[Dict[str, Any]]:
        """Create all VM instances in the group."""
        print(f"\n🚀 Creating VM Group: {self.group_name} with {self.count} instances...")
        print("=" * 60)

        created_vms = []
        for i, vm in enumerate(self.vms, 1):
            print(f"\n--- Creating instance {i}/{self.count}: {vm.config.name} ---")
            try:
                result = vm.create()
                created_vms.append(result)
                print(f"✅ Instance {i}/{self.count} created successfully")
            except Exception as e:
                print(f"❌ Failed to create instance {i}/{self.count}: {str(e)}")
                # Continue with other VMs even if one fails
                created_vms.append({"error": str(e), "vm_name": vm.config.name})

        successful_creates = len([vm for vm in created_vms if "error" not in vm])
        print(f"\n🎉 VM Group Creation Complete!")
        print(f"   ✅ Successfully created: {successful_creates}/{self.count} instances")
        if successful_creates < self.count:
            failed_creates = self.count - successful_creates
            print(f"   ❌ Failed to create: {failed_creates}/{self.count} instances")

        return created_vms

    def destroy(self) -> List[Dict[str, Any]]:
        """Destroy all VM instances in the group."""
        print(f"\n🗑️  Destroying VM Group: {self.group_name}")
        print("=" * 50)

        destroyed_vms = []
        for i, vm in enumerate(self.vms, 1):
            print(f"\n--- Destroying instance {i}/{self.count}: {vm.config.name} ---")
            try:
                result = vm.destroy()
                destroyed_vms.append(result)
                print(f"✅ Instance {i}/{self.count} destroyed successfully")
            except Exception as e:
                print(f"❌ Failed to destroy instance {i}/{self.count}: {str(e)}")
                destroyed_vms.append({"error": str(e), "vm_name": vm.config.name})

        successful_destroys = len([vm for vm in destroyed_vms if "error" not in vm])
        print(f"\n🎉 VM Group Destruction Complete!")
        print(f"   ✅ Successfully destroyed: {successful_destroys}/{self.count} instances")
        if successful_destroys < self.count:
            failed_destroys = self.count - successful_destroys
            print(f"   ❌ Failed to destroy: {failed_destroys}/{self.count} instances")

        return destroyed_vms

    def get_vm(self, index: int) -> Vm:
        """Get a specific VM from the group by index (0-based)"""
        if index < 0 or index >= len(self.vms):
            raise IndexError(f"VM index {index} out of range. Group has {len(self.vms)} VMs.")
        return self.vms[index]

    def get_vm_by_name(self, name: str) -> Optional[Vm]:
        """Get a specific VM from the group by name"""
        for vm in self.vms:
            if vm.config.name == name:
                return vm
        return None

    def list_vms(self) -> List[str]:
        """List all VM names in the group"""
        return [vm.config.name for vm in self.vms]

    # Nexus Intelligence Methods (for Universal Intelligence Mixin compatibility)
    def compliance_checks(self, standards: List[str]) -> 'VmGroup':
        """Enable compliance checking for specified standards on all VMs in the group"""
        return self._apply_to_all_vms('compliance_checks', standards)

    def nexus_networking(self) -> 'VmGroup':
        """Enable Nexus intelligent networking optimization on all VMs in the group"""
        return self._apply_to_all_vms('nexus_networking')

    def cost_optimization(self, enabled: bool = True) -> 'VmGroup':
        """Enable cost optimization intelligence on all VMs in the group"""
        return self._apply_to_all_vms('cost_optimization', enabled)

    def security_scanning(self, enabled: bool = True) -> 'VmGroup':
        """Enable security scanning intelligence on all VMs in the group"""
        return self._apply_to_all_vms('security_scanning', enabled)

    def predict_failures(self, enabled: bool = True) -> 'VmGroup':
        """Enable failure prediction intelligence on all VMs in the group"""
        return self._apply_to_all_vms('predict_failures', enabled)

    def performance_insights(self, enabled: bool = True) -> 'VmGroup':
        """Enable performance insights intelligence on all VMs in the group"""
        return self._apply_to_all_vms('performance_insights', enabled)

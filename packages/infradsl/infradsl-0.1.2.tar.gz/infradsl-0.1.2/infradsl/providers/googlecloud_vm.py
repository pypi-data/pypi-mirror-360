from typing import Optional, List, Dict, Any
from .googlecloud_managers.gcp_client import GcpClient
from .googlecloud_managers.vm_manager import VmManager, VmConfig
from .googlecloud_managers.status_reporter import GcpStatusReporter
from .googlecloud_managers.service_manager import GcpServiceManager
from .googlecloud_managers.firewall_manager import GcpFirewallManager, FirewallRule
from .googlecloud_managers.health_check_manager import GcpHealthCheckManager
from .googlecloud_managers.load_balancer_manager import GcpLoadBalancerManager, LoadBalancerConfig, BackendConfig
import os

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
        return self._apply_to_all_vms('machine_type', machine_type)

    def zone(self, zone: str) -> 'VmGroup':
        # All VMs in a group should be in the same zone for simplicity,
        # but the underlying Vm object supports different zones if needed in the future.
        return self._apply_to_all_vms('zone', zone)

    def disk_size(self, size_gb: int) -> 'VmGroup':
        return self._apply_to_all_vms('disk_size', size_gb)

    def image(self, image_family: str, image_project: str = "debian-cloud") -> 'VmGroup':
        return self._apply_to_all_vms('image', image_family, image_project=image_project)

    def network(self, network: str, subnetwork: str = "default") -> 'VmGroup':
        return self._apply_to_all_vms('network', network, subnetwork=subnetwork)

    def tags(self, tags: List[str]) -> 'VmGroup':
        for vm in self.vms:
            vm.tags(tags + [vm.config.name])  # Add VM-specific name tag
        return self

    def metadata(self, metadata: Dict[str, str]) -> 'VmGroup':
        return self._apply_to_all_vms('metadata', metadata)

    def startup_script(self, script: str) -> 'VmGroup':
        return self._apply_to_all_vms('startup_script', script)

    def service(self, service_name: str) -> 'VmGroup':
        return self._apply_to_all_vms('service', service_name)

    def firewall(self, name: str, port: int, protocol: str = "tcp", source_ranges: Optional[List[str]] = None) -> 'VmGroup':
        for vm in self.vms:
            vm.firewall(f"{name}-{vm.config.name}", port, protocol, source_ranges)
        return self

    def monitoring(self, enabled: bool = True) -> 'VmGroup':
        return self._apply_to_all_vms('monitoring', enabled)

    def health_check(self, protocol: str, port: int, path: str = "/") -> 'VmGroup':
        return self._apply_to_all_vms('health_check', protocol, port, path)

    def service_account(self, email: str, scopes: Optional[List[str]] = None) -> 'VmGroup':
        return self._apply_to_all_vms('service_account', email, scopes=scopes)

    def preview(self) -> Dict[str, Any]:
        """Preview what VMs will be created without actually creating them"""
        print(f"\n🔍 VM Group Preview: {self.group_name}")
        print("=" * 40)
        print(f"📋 What will be created:")
        print(f"🔷 VM Count: {self.count}")
        for vm in self.vms:
            vm.preview()
        return {"group_name": self.group_name, "count": self.count, "vms": [vm.config.name for vm in self.vms]}

    def create(self) -> List[Dict[str, Any]]:
        """Create all VMs in the group"""
        print(f"\n🚀 Creating VM Group: {self.group_name} ({self.count} VMs)")
        results = []
        for vm in self.vms:
            result = vm.create()
            results.append(result)
        print(f"✅ VM Group '{self.group_name}' created successfully!")
        return results

    def destroy(self) -> List[Dict[str, Any]]:
        """Destroy all VMs in the group"""
        print(f"\n🗑️  Destroying VM Group: {self.group_name}")
        results = []
        for vm in self.vms:
            result = vm.destroy()
            results.append(result)
        return results


class Vm:
    """Main orchestrator for Google Cloud VM infrastructure"""

    def __init__(self, name: str):
        self.config = VmConfig(name=name)
        self.gcp_client = GcpClient()
        self.vm_manager = None
        self.status_reporter = None
        self.service_manager = None
        self.firewall_manager = None
        self.health_check_manager = None
        self.load_balancer_manager = None
        self._auto_authenticated = False
        self.firewall_rules = []
        self._load_balancer_config = None

    def _ensure_authenticated(self):
        if not self._auto_authenticated:
            # Try multiple locations for oopscli.json
            possible_paths = [
                "oopscli.json",  # Project root
                os.path.join(os.getcwd(), "oopscli.json"),  # Current working directory
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "oopscli.json"),  # Project root
            ]

            credentials_found = False
            for path in possible_paths:
                if os.path.exists(path):
                    try:
                        self.gcp_client.authenticate(credentials_path=path)
                        self.vm_manager = VmManager(self.gcp_client)
                        self.status_reporter = GcpStatusReporter()
                        self.service_manager = GcpServiceManager()
                        self.firewall_manager = GcpFirewallManager(self.gcp_client)
                        self.health_check_manager = GcpHealthCheckManager(self.gcp_client)
                        self.load_balancer_manager = GcpLoadBalancerManager(self.gcp_client)
                        self._auto_authenticated = True
                        credentials_found = True
                        break
                    except Exception as e:
                        print(f"⚠️  Failed to authenticate with {path}: {str(e)}")
                        continue

            if not credentials_found:
                raise Exception("Could not find or authenticate with oopscli.json. Please ensure the file exists and contains valid Google Cloud service account credentials.")

    def machine_type(self, machine_type: str) -> 'Vm':
        """Set the machine type (e.g., 'e2-micro')"""
        self.config.machine_type = machine_type
        return self

    def zone(self, zone: str) -> 'Vm':
        """Set the zone (e.g., 'us-central1-a')"""
        self.config.zone = zone
        return self

    def disk_size(self, size_gb: int) -> 'Vm':
        """Set the boot disk size in GB"""
        if size_gb < 10:
            raise ValueError("Disk size must be at least 10 GB")
        self.config.disk_size_gb = size_gb
        return self

    def image(self, image_family: str, image_project: str = "debian-cloud") -> 'Vm':
        """Set the image family and project"""
        self.config.image_family = image_family
        self.config.image_project = image_project
        return self

    def network(self, network: str, subnetwork: str = "default") -> 'Vm':
        """Set the network and subnetwork"""
        self.config.network = network
        self.config.subnetwork = subnetwork
        return self

    def tags(self, tags: List[str]) -> 'Vm':
        """Add network tags"""
        self.config.tags = tags
        return self

    def metadata(self, metadata: Dict[str, str]) -> 'Vm':
        """Add metadata key-value pairs"""
        self.config.metadata = metadata
        return self

    def startup_script(self, script: str) -> 'Vm':
        """Set a startup script"""
        self.config.startup_script = script
        return self

    def service(self, service_name: str) -> 'Vm':
        """Configure a service (e.g., 'nginx', 'postgres') using templates"""
        self._ensure_authenticated()
        try:
            startup_script = self.service_manager.generate_startup_script(service_name)
            self.config.startup_script = startup_script
            print(f"✅ Configured {service_name} service")
        except Exception as e:
            raise Exception(f"Failed to configure {service_name} service: {str(e)}")

        return self

    def firewall(self, name: str, port: int, protocol: str = "tcp", source_ranges: Optional[List[str]] = None) -> 'Vm':
        if source_ranges is None:
            source_ranges = ["0.0.0.0/0"]
        self.firewall_rules.append(FirewallRule(name=name, port=port, protocol=protocol, source_ranges=source_ranges))
        return self

    def monitoring(self, enabled: bool = True) -> 'Vm':
        """Enable or disable monitoring"""
        self.config.monitoring_enabled = enabled
        return self

    def health_check(self, protocol: str, port: int, path: str = "/") -> 'Vm':
        """Configure health check"""
        self.config.health_check = {
            "protocol": protocol,
            "port": port,
            "path": path
        }
        return self

    def load_balancer(self, name: str, port: int = 80) -> 'Vm':
        """Configure a load balancer for this VM"""
        backend = BackendConfig(
            vm_name=self.config.name,
            zone=self.config.zone,
            port=port,
            health_check_name=f"{self.config.name}-health-check" if self.config.health_check else None
        )
        self._load_balancer_config = LoadBalancerConfig(
            name=name,
            backends=[backend]
        )
        return self

    def service_account(self, email: str, scopes: Optional[List[str]] = None) -> 'Vm':
        """Configure a service account"""
        self.config.service_account_email = email
        self.config.scopes = scopes or ["https://www.googleapis.com/auth/cloud-platform"]
        return self

    def _inject_monitoring_agent(self):
        """Inject monitoring agent installation into startup script if monitoring is enabled"""
        if hasattr(self.config, 'monitoring_enabled') and self.config.monitoring_enabled:
            monitoring_script = """
# Install Google Cloud Monitoring Agent
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install
"""
            if self.config.startup_script:
                self.config.startup_script += monitoring_script
            else:
                self.config.startup_script = monitoring_script

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created without actually creating it"""
        print(f"\n🔍 VM Preview: {self.config.name}")
        return {"name": self.config.name, "machine_type": self.config.machine_type, "zone": self.config.zone}

    def create(self) -> Dict[str, Any]:
        """Create the VM instance with all configured options"""
        self._ensure_authenticated()

        # Inject monitoring agent if needed
        self._inject_monitoring_agent()

        # Create firewall rules first
        if self.firewall_rules:
            print(f"\n🔥 Creating firewall rules for VM: {self.config.name}")
            self.firewall_manager.create_firewall_rules(self.config.name, self.config.zone, self.firewall_rules)

        # Create health check if configured
        health_check_name = None
        if self.config.health_check:
            print(f"\n🏥 Creating health check for VM: {self.config.name}")
            health_check_name = self.health_check_manager.create_health_check(self.config.name, self.config.health_check)

        existing_vm = self.vm_manager.get_vm_info(self.config.name, self.config.zone)
        was_existing = existing_vm is not None
        if was_existing:
            print(f"\n🔄 VM '{self.config.name}' already exists. Checking status...")
            vm_result = existing_vm
            if vm_result["status"] != "RUNNING":
                print(f"   VM status: {vm_result['status']}. Starting VM...")
                self.vm_manager.start_vm(self.config.name, self.config.zone)
        else:
            print(f"🚀 Creating new VM instance...")
            vm_result = self.vm_manager.create_vm(self.config)

        # Create load balancer if configured
        load_balancer_info = None
        if self._load_balancer_config:
            print(f"\n🌐 Creating load balancer for VM: {self.config.name}")
            try:
                load_balancer_info = self.load_balancer_manager.create_load_balancer(self._load_balancer_config)
            except Exception as e:
                print(f"⚠️  Warning: Failed to create load balancer: {e}")
                load_balancer_info = None

        # Determine if a service is configured
        service_name = None
        if self.config.startup_script:
            # Simple heuristic to detect if a service was configured
            if "Service deployment completed successfully" in self.config.startup_script:
                # This indicates a service was configured via .service()
                service_name = "configured-service"

        result = {
            "id": vm_result["id"],
            "name": self.config.name,
            "ip": vm_result["ip_address"],
            "status": vm_result["status"],
            "machine_type": self.config.machine_type,
            "zone": self.config.zone,
            "was_existing": was_existing,
            "service": service_name,
            "firewall_rules": len(self.firewall_rules),
            "health_check": health_check_name,
            "load_balancer": load_balancer_info,
            "monitoring": getattr(self.config, 'monitoring_enabled', False)
        }

        self.status_reporter.print_vm_summary(result)
        return result

    def destroy(self) -> Dict[str, Any]:
        """Destroy the VM instance"""
        self._ensure_authenticated()
        print(f"\n🗑️  Destroying VM instance: {self.config.name}")

        # Delete load balancer first (if it exists)
        load_balancer_deleted = False
        if self._load_balancer_config:
            try:
                print(f"\n🗑️  Deleting load balancer: {self._load_balancer_config.name}")
                if self.load_balancer_manager.delete_load_balancer(self._load_balancer_config.name):
                    load_balancer_deleted = True
                    print(f"✅ Load balancer deleted successfully")
                else:
                    print(f"⚠️  Warning: Failed to delete load balancer: {self._load_balancer_config.name}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to delete load balancer: {e}")

        success = self.vm_manager.delete_vm(self.config.name, self.config.zone)

        # Delete firewall rules after VM deletion
        if self.firewall_rules:
            print(f"\n🗑️  Deleting firewall rules for VM: {self.config.name}")
            self.firewall_manager.delete_firewall_rules(self.config.name)

        # Delete health check after VM deletion
        if self.config.health_check:
            print(f"\n🗑️  Deleting health check for VM: {self.config.name}")
            self.health_check_manager.delete_health_check(self.config.name)

        return {
            "vm": success,
            "load_balancer": load_balancer_deleted,
            "firewall_rules": True,
            "health_check": True if self.config.health_check else False,
            "name": self.config.name,
            "zone": self.config.zone
        }

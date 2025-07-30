"""
Google Compute Engine VM Core Implementation

Core attributes and authentication for Google Compute Engine Virtual Machines.
Provides the foundation for the modular VM infrastructure.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource
from ...googlecloud_managers.vm_manager import VmManager, VmConfig
from ...googlecloud_managers.status_reporter import GcpStatusReporter
from ...googlecloud_managers.service_manager import GcpServiceManager
from ...googlecloud_managers.firewall_manager import GcpFirewallManager, FirewallRule
from ...googlecloud_managers.health_check_manager import GcpHealthCheckManager
from ...googlecloud_managers.load_balancer_manager import GcpLoadBalancerManager


class VmCore(BaseGcpResource):
    """
    Core class for Google Compute Engine VM functionality.
    
    This class provides:
    - Basic VM attributes and configuration
    - Authentication setup
    - Common utilities for VM operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, names: Union[str, List[str]]):
        """
        Initialize VM core with single or multiple VM names.
        
        Args:
            names: Single VM name or list of VM names for multi-VM operations
        """
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
        
        # Core VM attributes
        self.vm_type = "compute_instance"
        self.vm_description = f"Google Compute Engine VM: {', '.join(self.vm_names)}"
        
        # Initialize shared configuration for all VMs
        self.configs = {}
        for vm_name in self.vm_names:
            self.configs[vm_name] = VmConfig(name=vm_name)
            
        # Manager references
        self.status_reporter = GcpStatusReporter()
        self.service_manager = GcpServiceManager()
        self.vm_manager = None
        self.firewall_manager = None
        self.health_check_manager = None
        self.load_balancer_manager = None
        
        # Configuration tracking
        self.firewall_rules: List[FirewallRule] = []
        self._monitoring_enabled = False
        self._load_balancer_config = None
        self._optimization_priority = None
        self._networking_intelligence = None
        
        # State tracking
        self.vm_exists = {}
        self.vm_created = {}
        self.vm_state = {}
        self.deployment_status = None
        
        # Labels and metadata
        self.vm_labels = {}
        self.vm_annotations = {}
        
        # Cost tracking
        self.estimated_monthly_cost = "$0.00/month"
        
    def _initialize_managers(self):
        """Initialize VM specific managers"""
        self.vm_manager = None
        self.firewall_manager = None
        self.health_check_manager = None
        self.load_balancer_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            self.vm_manager = VmManager(self.gcp_client)
            self.firewall_manager = GcpFirewallManager(self.gcp_client)
            self.health_check_manager = GcpHealthCheckManager(self.gcp_client)
            self.load_balancer_manager = GcpLoadBalancerManager(self.gcp_client)
            
            # Set project ID from GCP client if available
            if hasattr(self.gcp_client, 'project'):
                for config in self.configs.values():
                    if not config.project_id:
                        config.project_id = self.gcp_client.project
                        
        except Exception as e:
            print(f"⚠️  VM setup note: {str(e)}")
            
    def _fetch_current_cloud_state(self) -> Optional[Dict[str, Any]]:
        """Fetch the current state of the primary VM from Google Cloud"""
        self._ensure_authenticated()
        primary_vm_name = self.vm_names[0]
        config = self.configs[primary_vm_name]
        
        try:
            return self.vm_manager.get_vm_info(primary_vm_name, config.zone)
        except Exception as e:
            # This can happen if the VM doesn't exist yet, which is not an error
            if "not found" in str(e).lower():
                return None
            print(f"⚠️  Warning: Could not fetch current cloud state for {primary_vm_name}: {e}")
            return None
            
    def _validate_machine_type(self, machine_type: str) -> bool:
        """Validate if machine type is valid for GCP"""
        # Standard machine types
        valid_prefixes = ["e2", "n1", "n2", "n2d", "t2d", "c2", "c2d", "m1", "m2", "a2"]
        
        # Check for custom machine types
        if machine_type.startswith("custom-"):
            parts = machine_type.split("-")
            if len(parts) == 3:
                try:
                    cpus = int(parts[1])
                    memory = int(parts[2])
                    return 1 <= cpus <= 96 and memory >= 256
                except ValueError:
                    return False
                    
        # Check for standard machine types
        for prefix in valid_prefixes:
            if machine_type.startswith(prefix + "-"):
                return True
                
        return False
        
    def _validate_zone(self, zone: str) -> bool:
        """Validate if zone is valid for GCP"""
        # Basic validation - should match pattern like 'us-central1-a'
        parts = zone.split("-")
        return len(parts) >= 3 and parts[-1].isalpha()
        
    def _validate_image(self, image_family: str, image_project: str) -> bool:
        """Validate image configuration"""
        # Basic validation
        valid_projects = [
            "debian-cloud", "ubuntu-os-cloud", "centos-cloud", 
            "rhel-cloud", "windows-cloud", "cos-cloud"
        ]
        return bool(image_family) and (image_project in valid_projects or image_project)
        
    def _extract_cpu_from_machine_type(self, machine_type: str) -> int:
        """Extract CPU count from machine type"""
        if machine_type.startswith("custom-"):
            parts = machine_type.split("-")
            if len(parts) >= 2:
                try:
                    return int(parts[1])
                except ValueError:
                    pass
                    
        # Standard machine type mappings
        machine_cpus = {
            "e2-micro": 2, "e2-small": 2, "e2-medium": 2,
            "e2-standard-2": 2, "e2-standard-4": 4, "e2-standard-8": 8,
            "e2-standard-16": 16, "e2-standard-32": 32,
            "n1-standard-1": 1, "n1-standard-2": 2, "n1-standard-4": 4,
            "n1-standard-8": 8, "n1-standard-16": 16, "n1-standard-32": 32,
            "n2-standard-2": 2, "n2-standard-4": 4, "n2-standard-8": 8,
            "n2-standard-16": 16, "n2-standard-32": 32,
        }
        
        return machine_cpus.get(machine_type, 2)
        
    def _extract_ram_from_machine_type(self, machine_type: str) -> int:
        """Extract RAM in GB from machine type"""
        if machine_type.startswith("custom-"):
            parts = machine_type.split("-")
            if len(parts) >= 3:
                try:
                    memory_mb = int(parts[2])
                    return memory_mb // 1024
                except ValueError:
                    pass
                    
        # Standard machine type mappings
        machine_ram = {
            "e2-micro": 1, "e2-small": 2, "e2-medium": 4,
            "e2-standard-2": 8, "e2-standard-4": 16, "e2-standard-8": 32,
            "e2-standard-16": 64, "e2-standard-32": 128,
            "n1-standard-1": 3.75, "n1-standard-2": 7.5, "n1-standard-4": 15,
            "n1-standard-8": 30, "n1-standard-16": 60, "n1-standard-32": 120,
            "n2-standard-2": 8, "n2-standard-4": 16, "n2-standard-8": 32,
            "n2-standard-16": 64, "n2-standard-32": 128,
        }
        
        return int(machine_ram.get(machine_type, 4))
        
    def _get_vm_type_from_config(self) -> str:
        """Determine VM type from configuration"""
        primary_config = list(self.configs.values())[0]
        
        # Check for specific service types
        if hasattr(primary_config, 'services') and primary_config.services:
            service_types = [s.name for s in primary_config.services]
            if "apache" in service_types or "nginx" in service_types:
                return "web_server"
            elif "postgres" in service_types or "mysql" in service_types:
                return "database_server"
            elif "jenkins" in service_types:
                return "ci_cd_server"
                
        # Check by machine type
        machine_type = primary_config.machine_type
        if machine_type.startswith("e2-micro") or machine_type.startswith("e2-small"):
            return "development"
        elif machine_type.startswith("n2") or machine_type.startswith("c2"):
            return "compute_optimized"
        elif machine_type.startswith("m1") or machine_type.startswith("m2"):
            return "memory_optimized"
        elif self.is_multi_vm:
            return "vm_cluster"
        else:
            return "general_purpose"
            
    def _estimate_vm_cost(self) -> float:
        """Estimate monthly cost for VMs"""
        total_cost = 0.0
        
        for vm_name, config in self.configs.items():
            # Base costs per hour (simplified)
            machine_costs = {
                "e2-micro": 0.0084,
                "e2-small": 0.0168,
                "e2-medium": 0.0336,
                "e2-standard-2": 0.067,
                "e2-standard-4": 0.134,
                "e2-standard-8": 0.268,
                "n1-standard-1": 0.0475,
                "n1-standard-2": 0.095,
                "n1-standard-4": 0.19,
                "n2-standard-2": 0.0971,
                "n2-standard-4": 0.1942,
            }
            
            # Get base hourly cost
            hourly_cost = machine_costs.get(config.machine_type, 0.05)
            
            # Add disk cost (standard persistent disk: $0.04/GB/month)
            disk_cost_monthly = config.disk_size_gb * 0.04
            
            # Calculate monthly cost (730 hours)
            vm_monthly_cost = (hourly_cost * 730) + disk_cost_monthly
            
            # Add premium for additional features
            if config.external_ip:
                vm_monthly_cost += 7.20  # Static IP cost
                
            if self._monitoring_enabled:
                vm_monthly_cost *= 1.1  # 10% overhead for monitoring
                
            total_cost += vm_monthly_cost
            
        return total_cost
        
    def _fetch_current_vm_state(self, vm_name: str) -> Dict[str, Any]:
        """Fetch current state of a specific VM from Google Cloud"""
        try:
            if not self.vm_manager:
                return {
                    "exists": False,
                    "vm_name": vm_name,
                    "error": "VM manager not initialized"
                }
                
            config = self.configs.get(vm_name)
            if not config:
                return {
                    "exists": False,
                    "vm_name": vm_name,
                    "error": "No configuration found"
                }
                
            # Try to get VM info
            vm_info = self.vm_manager.get_vm_info(vm_name, config.zone)
            
            if vm_info:
                return {
                    "exists": True,
                    "vm_name": vm_name,
                    "zone": config.zone,
                    "machine_type": vm_info.get("machineType", "").split("/")[-1],
                    "status": vm_info.get("status", "UNKNOWN"),
                    "creation_timestamp": vm_info.get("creationTimestamp", ""),
                    "self_link": vm_info.get("selfLink", ""),
                    "network_interfaces": vm_info.get("networkInterfaces", []),
                    "disks": vm_info.get("disks", []),
                    "labels": vm_info.get("labels", {}),
                    "metadata": vm_info.get("metadata", {}),
                }
            else:
                return {
                    "exists": False,
                    "vm_name": vm_name,
                    "zone": config.zone
                }
                
        except Exception as e:
            if "not found" in str(e).lower():
                return {
                    "exists": False,
                    "vm_name": vm_name,
                    "zone": config.zone if config else "unknown"
                }
            else:
                return {
                    "exists": False,
                    "vm_name": vm_name,
                    "error": str(e)
                }
                
    def _discover_existing_vms(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing VMs in the project"""
        existing_vms = {}
        
        try:
            if not self.vm_manager:
                return existing_vms
                
            # For each VM in our configuration, check if it exists
            for vm_name in self.vm_names:
                vm_state = self._fetch_current_vm_state(vm_name)
                if vm_state.get("exists"):
                    existing_vms[vm_name] = vm_state
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing VMs: {str(e)}")
            
        return existing_vms
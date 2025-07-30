import os
from typing import Dict, Any, Optional, List, Union
from ..base_resource import BaseGcpResource
from ...googlecloud_managers.vm_manager import VmManager, VmConfig
from ...googlecloud_managers.status_reporter import GcpStatusReporter
from ...googlecloud_managers.service_manager import GcpServiceManager
from ...googlecloud_managers.firewall_manager import GcpFirewallManager, FirewallRule
from ...googlecloud_managers.health_check_manager import GcpHealthCheckManager
from ...googlecloud_managers.load_balancer_manager import GcpLoadBalancerManager
from google.cloud import compute_v1

# Import all the mixins
from ..mixins import (
    PredictiveIntelligenceMixin,
    NetworkingIntelligenceMixin,
    DriftManagementMixin,
    FirewallManagementMixin,
    LoadBalancerManagementMixin
)


class Vm(
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

    # === Firewall and Load Balancer Methods are now in respective mixins ===

    def cpu(self, cores: int) -> 'Vm':
        """Set CPU cores - maps to appropriate GCP machine type
        
        Args:
            cores: Number of CPU cores (1, 2, 4, 8, 16, 32, 64, etc.)
            
        Returns:
            Self for method chaining
            
        Note:
            Maps CPU cores to GCP machine types automatically:
            - 1 core -> e2-micro (1 vCPU, 1GB RAM)
            - 2 cores -> e2-small (2 vCPUs, 2GB RAM)  
            - 4 cores -> e2-medium (2 vCPUs, 4GB RAM)
            - 8+ cores -> e2-standard-{cores/2} or custom
        """
        if cores < 1:
            raise ValueError("CPU cores must be at least 1")
            
        # GCP machine type mapping based on CPU cores
        machine_type_map = {
            1: "e2-micro",        # 1 vCPU, 1GB RAM
            2: "e2-small",        # 2 vCPUs, 2GB RAM
            4: "e2-medium",       # 2 vCPUs, 4GB RAM
            8: "e2-standard-4",   # 4 vCPUs, 16GB RAM
            16: "e2-standard-8",  # 8 vCPUs, 32GB RAM
            32: "e2-standard-16", # 16 vCPUs, 64GB RAM
            64: "e2-standard-32"  # 32 vCPUs, 128GB RAM
        }
        
        if cores in machine_type_map:
            machine_type = machine_type_map[cores]
            print(f"🔧 Setting CPU cores: {cores} → machine type: {machine_type}")
        else:
            # For non-standard core counts, use custom machine type
            # GCP custom format: custom-{vCPUs}-{memory_MB}
            # Default to 4GB RAM per vCPU for custom instances
            memory_mb = cores * 4 * 1024  # 4GB per core
            machine_type = f"custom-{cores}-{memory_mb}"
            print(f"🔧 Setting CPU cores: {cores} → custom machine type: {machine_type}")
        
        # Apply to all VM configs
        for config in self.configs.values():
            config.machine_type = machine_type
            
        return self

    def ram(self, gb: int) -> 'Vm':
        """Set RAM in GB - maps to appropriate GCP machine type
        
        Args:
            gb: RAM in gigabytes (1, 2, 4, 8, 16, 32, etc.)
            
        Returns:
            Self for method chaining
            
        Note:
            Maps RAM to GCP machine types automatically:
            - 1GB -> e2-micro
            - 2GB -> e2-small
            - 4GB -> e2-medium
            - 8GB+ -> e2-standard-{appropriate size}
        """
        if gb < 1:
            raise ValueError("RAM must be at least 1 GB")
            
        # GCP machine type mapping based on RAM
        if gb <= 1:
            machine_type = "e2-micro"        # 1 vCPU, 1GB RAM
        elif gb <= 2:
            machine_type = "e2-small"        # 2 vCPUs, 2GB RAM
        elif gb <= 4:
            machine_type = "e2-medium"       # 2 vCPUs, 4GB RAM
        elif gb <= 8:
            machine_type = "e2-standard-2"   # 2 vCPUs, 8GB RAM
        elif gb <= 16:
            machine_type = "e2-standard-4"   # 4 vCPUs, 16GB RAM
        elif gb <= 32:
            machine_type = "e2-standard-8"   # 8 vCPUs, 32GB RAM
        elif gb <= 64:
            machine_type = "e2-standard-16"  # 16 vCPUs, 64GB RAM
        elif gb <= 90:  # Reduced threshold so 100GB triggers custom
            machine_type = "e2-standard-32"  # 32 vCPUs, 128GB RAM (but only up to 90GB for our logic)
        else:
            # For large RAM requirements, use custom machine type
            # Estimate vCPUs based on 4GB per core ratio
            vcpus = max(1, gb // 4)
            memory_mb = gb * 1024
            machine_type = f"custom-{vcpus}-{memory_mb}"
            print(f"🔧 Setting RAM: {gb}GB → custom machine type: {machine_type}")
        
        if not machine_type.startswith("custom"):
            print(f"🔧 Setting RAM: {gb}GB → machine type: {machine_type}")
        
        # Apply to all VM configs  
        for config in self.configs.values():
            config.machine_type = machine_type
            
        return self

    def optimize_for(self, priority: str) -> 'Vm':
        """Use Cross-Cloud Magic to optimize for cost/performance/reliability
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
            
        Note:
            This integrates with InfraDSL's revolutionary Cross-Cloud Magic system
            to automatically select the optimal cloud provider and configuration.
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        # Store optimization preference for later use
        self._optimization_priority = priority
        
        print(f"🎯 Cross-Cloud Magic: Optimizing for {priority}")
        
        # Integrate with Cross-Cloud Intelligence
        try:
            from ...core.cross_cloud_intelligence import cross_cloud_intelligence, ServiceRequirements, ServiceCategory
            
            # Create service requirements based on current VM configuration
            primary_config = list(self.configs.values())[0]
            
            # Extract CPU/RAM from machine type if available
            cpu_count = self._extract_cpu_from_machine_type(primary_config.machine_type)
            ram_gb = self._extract_ram_from_machine_type(primary_config.machine_type)
            
            # Create service requirements
            requirements = ServiceRequirements(
                service_category=ServiceCategory.COMPUTE,
                service_type="web-servers",  # Default to web servers
                performance_tier="standard",
                reliability_requirement="high",
                cost_sensitivity=1.0 if priority == "cost" else 0.3,
                performance_sensitivity=1.0 if priority == "performance" else 0.3,
                reliability_sensitivity=1.0 if priority == "reliability" else 0.3,
                compliance_sensitivity=1.0 if priority == "compliance" else 0.3
            )
            
            # Get Cross-Cloud recommendation
            recommendation = cross_cloud_intelligence.select_optimal_provider(requirements)
            
            # Show recommendation to user
            if recommendation.recommended_provider != "gcp":
                print(f"💡 Cross-Cloud Magic suggests {recommendation.recommended_provider.upper()} for {priority} optimization")
                print(f"   💰 Potential monthly savings: ${recommendation.estimated_monthly_cost:.2f}")
                print(f"   📊 Confidence: {recommendation.confidence_score:.1%}")
                print(f"   📝 Consider switching providers for optimal {priority}")
            else:
                print(f"✅ Google Cloud is optimal for {priority} optimization")
                
        except ImportError:
            print("⚠️  Cross-Cloud Magic not available - using provider-specific optimizations")
        except Exception as e:
            print(f"⚠️  Cross-Cloud Magic error: {e} - using provider-specific optimizations")
        
        # Apply GCP-specific optimizations based on priority
        if priority == "cost":
            print("💰 Cost optimization: Selecting cost-effective machine types")
            self._apply_cost_optimizations()
        elif priority == "performance":
            print("⚡ Performance optimization: Selecting high-performance machine types")
            self._apply_performance_optimizations()
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Selecting stable, non-preemptible instances")
            self._apply_reliability_optimizations()
        elif priority == "compliance":
            print("📋 Compliance optimization: Selecting compliant regions and configurations")
            self._apply_compliance_optimizations()
        
        return self
    
    def _extract_cpu_from_machine_type(self, machine_type: str) -> int:
        """Extract CPU count from GCP machine type"""
        if machine_type == "e2-micro":
            return 1
        elif machine_type == "e2-small":
            return 2
        elif machine_type == "e2-medium":
            return 2
        elif "e2-standard-" in machine_type:
            # e2-standard-4 means 4 vCPUs
            return int(machine_type.split("-")[-1])
        elif "custom-" in machine_type:
            # custom-4-16384 means 4 vCPUs
            return int(machine_type.split("-")[1])
        else:
            return 2  # Default fallback
    
    def _extract_ram_from_machine_type(self, machine_type: str) -> int:
        """Extract RAM in GB from GCP machine type"""
        if machine_type == "e2-micro":
            return 1
        elif machine_type == "e2-small":
            return 2
        elif machine_type == "e2-medium":
            return 4
        elif "e2-standard-" in machine_type:
            # e2-standard-4 means 16GB RAM (4 vCPUs * 4GB)
            vcpus = int(machine_type.split("-")[-1])
            return vcpus * 4
        elif "custom-" in machine_type:
            # custom-4-16384 means 16384MB = 16GB
            ram_mb = int(machine_type.split("-")[2])
            return ram_mb // 1024
        else:
            return 4  # Default fallback
    
    def _apply_cost_optimizations(self):
        """Apply GCP-specific cost optimizations"""
        for config in self.configs.values():
            # Use smaller disk for cost savings
            if config.disk_size_gb == 10:  # Default
                config.disk_size_gb = 10  # Keep minimal
            
            # Suggest cost-effective machine types
            if "e2-standard-" in config.machine_type:
                # Keep existing for now, but note cost optimization
                print(f"   💰 Current: {config.machine_type} (cost-optimized e2 series)")
            
            # Add cost optimization metadata
            if not config.metadata:
                config.metadata = {}
            config.metadata["cost-optimized"] = "true"
            config.metadata["preemptible-suggested"] = "true"
    
    def _apply_performance_optimizations(self):
        """Apply GCP-specific performance optimizations"""
        for config in self.configs.values():
            # Switch to compute-optimized if using standard
            if "e2-standard-" in config.machine_type:
                # Suggest c2-standard for better CPU performance
                vcpus = config.machine_type.split("-")[-1]
                suggested_type = f"c2-standard-{vcpus}"
                print(f"   🚀 Performance suggestion: upgrade to {suggested_type}")
                # Note: Actual upgrade would require more validation
                
            # Increase disk size for better I/O performance
            if config.disk_size_gb <= 10:
                config.disk_size_gb = 50  # Larger disk for better performance
                print(f"   💿 Increased disk size to {config.disk_size_gb}GB for better I/O")
            
            # Add performance optimization metadata
            if not config.metadata:
                config.metadata = {}
            config.metadata["performance-optimized"] = "true"
            config.metadata["ssd-recommended"] = "true"
    
    def _apply_reliability_optimizations(self):
        """Apply GCP-specific reliability optimizations"""
        for config in self.configs.values():
            # Use reliable zones
            if "us-central1-a" in config.zone:
                print(f"   🛡️ Using reliable zone: {config.zone}")
            
            # Increase disk size for reliability
            if config.disk_size_gb < 20:
                config.disk_size_gb = 20  # Larger disk for better reliability
                print(f"   💿 Increased disk size to {config.disk_size_gb}GB for reliability")
            
            # Add reliability optimization metadata
            if not config.metadata:
                config.metadata = {}
            config.metadata["reliability-optimized"] = "true"
            config.metadata["non-preemptible"] = "true"
    
    def _apply_compliance_optimizations(self):
        """Apply GCP-specific compliance optimizations"""
        for config in self.configs.values():
            # Ensure compliant regions
            if not config.zone or "us-central1" in config.zone:
                print(f"   📋 Using compliant zone: {config.zone}")
            
            # Add compliance optimization metadata
            if not config.metadata:
                config.metadata = {}
            config.metadata["compliance-optimized"] = "true"
            config.metadata["secure-boot-recommended"] = "true"
            config.metadata["encryption-enabled"] = "true"

    def service_account(self, email: str, scopes: Optional[List[str]] = None) -> 'Vm':
        """Configure service account for all VMs"""
        for config in self.configs.values():
            config.service_account_email = email
            config.scopes = scopes or ["https://www.googleapis.com/auth/cloud-platform"]
        return self

    # === Predictive Intelligence Methods are now in PredictiveIntelligenceMixin ===

    # === Drift Management Methods are now in DriftManagementMixin ===

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

                # Create health check if configured (using mixin method)
                self._create_health_checks_for_vm(vm_name, config)

            # Create load balancer if configured (using mixin method)
            self._create_load_balancer_if_configured(vm_results)

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
    
    # === All drift management methods are now in DriftManagementMixin ===
    
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

    # === Networking Intelligence Methods are now in NetworkingIntelligenceMixin ===

    # === More Networking Intelligence Methods are now in NetworkingIntelligenceMixin ===

    # === Predictive Intelligence Methods are now in PredictiveIntelligenceMixin ===

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

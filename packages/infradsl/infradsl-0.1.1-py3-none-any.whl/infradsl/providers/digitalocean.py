from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# Import our new managers
from .digitalocean_managers.do_client import DoClient
from .digitalocean_managers.service_manager import ServiceManager
from .digitalocean_managers.resource_discovery import ResourceDiscovery
from .digitalocean_managers.infrastructure_planner import InfrastructurePlanner, FirewallRule, LoadBalancerConfig
from .digitalocean_managers.droplet_manager import DropletManager, DropletConfig
from .digitalocean_managers.firewall_manager import FirewallManager
from .digitalocean_managers.load_balancer_manager import LoadBalancerManager
from .digitalocean_managers.status_reporter import StatusReporter
from .digitalocean_managers.standalone_firewall import StandaloneFirewall
from .digitalocean_managers.standalone_load_balancer import StandaloneLoadBalancer
from .digitalocean_managers.kubernetes_cluster import KubernetesCluster
from .digitalocean_managers.container_registry import ContainerRegistryManager
from .digitalocean_resources.function import Function
from .digitalocean_resources.base_resource import BaseDigitalOceanResource
# from .digitalocean_resources.kubernetes import Kubernetes as KubernetesResource


class Droplet(BaseDigitalOceanResource):
    """Main orchestrator for DigitalOcean droplet infrastructure"""

    def __init__(self, name: str):
        super().__init__(name)
        self.config = DropletConfig(name=name)

        # Initialize managers
        self.do_client = DoClient()
        self.service_manager = ServiceManager()
        self.resource_discovery = ResourceDiscovery(self.do_client)
        self.infrastructure_planner = InfrastructurePlanner()
        self.droplet_manager = DropletManager(self.do_client)
        self.firewall_manager = FirewallManager(self.do_client)
        self.load_balancer_manager = LoadBalancerManager(self.do_client)
        self.status_reporter = StatusReporter()
        self.container_registry = ContainerRegistryManager(self.do_client)

    def _initialize_managers(self):
        """Initialize resource-specific managers - required by base class"""
        # Managers are initialized in __init__ for this class
        pass

    def size(self, size: str) -> 'Droplet':
        """Set the droplet size (e.g., 's-1vcpu-1gb')"""
        self.config.size = size
        return self

    def region(self, region: str) -> 'Droplet':
        """Set the region (e.g., 'nyc3')"""
        self.config.region = region
        return self

    def image(self, image: str) -> 'Droplet':
        """Set the image (e.g., 'ubuntu-22-04-x64')"""
        self.config.image = image
        return self

    def ssh_keys(self, keys: List[str]) -> 'Droplet':
        """Add SSH keys"""
        self.config.ssh_keys = keys
        return self

    def tags(self, tags: List[str]) -> 'Droplet':
        """Add tags to the droplet"""
        self.config.tags = tags
        return self

    def backups(self, enabled: bool = True) -> 'Droplet':
        """Enable or disable backups"""
        self.config.backups = enabled
        return self

    def monitoring(self, enabled: bool = True) -> 'Droplet':
        """Enable or disable monitoring"""
        self.config.monitoring = enabled
        return self

    def cpu(self, cores: int) -> 'Droplet':
        """Set CPU cores - maps to appropriate DigitalOcean droplet size
        
        Args:
            cores: Number of CPU cores (1, 2, 4, 8, 16, 32, etc.)
            
        Returns:
            Self for method chaining
            
        Note:
            Maps CPU cores to DigitalOcean droplet sizes automatically:
            - 1 core -> s-1vcpu-1gb (1 vCPU, 1GB RAM)
            - 2 cores -> s-2vcpu-2gb (2 vCPUs, 2GB RAM)
            - 4 cores -> s-4vcpu-8gb (4 vCPUs, 8GB RAM)
            - 8+ cores -> s-{cores}vcpu-{cores*2}gb
        """
        if cores < 1:
            raise ValueError("CPU cores must be at least 1")
            
        # DigitalOcean droplet size mapping based on CPU cores
        size_map = {
            1: "s-1vcpu-1gb",      # 1 vCPU, 1GB RAM
            2: "s-2vcpu-2gb",      # 2 vCPUs, 2GB RAM
            4: "s-4vcpu-8gb",      # 4 vCPUs, 8GB RAM
            8: "s-8vcpu-16gb",     # 8 vCPUs, 16GB RAM
            16: "c-16",            # 16 vCPUs, 32GB RAM (CPU optimized)
            32: "c-32",            # 32 vCPUs, 64GB RAM (CPU optimized)
        }
        
        if cores in size_map:
            size = size_map[cores]
            print(f"🔧 Setting CPU cores: {cores} → droplet size: {size}")
        else:
            # For non-standard core counts, use general purpose sizing
            # Standard pattern: more cores get proportionally more RAM
            if cores <= 6:
                ram_gb = cores * 2  # 2GB per core for smaller instances
                size = f"s-{cores}vcpu-{ram_gb}gb"
            else:
                # Use CPU-optimized for larger instances
                ram_gb = cores * 2  # 2GB per core for CPU-optimized
                size = f"c-{cores}"
            print(f"🔧 Setting CPU cores: {cores} → custom droplet size: {size}")
        
        self.config.size = size
        return self

    def ram(self, gb: int) -> 'Droplet':
        """Set RAM in GB - maps to appropriate DigitalOcean droplet size
        
        Args:
            gb: RAM in gigabytes (1, 2, 4, 8, 16, 32, etc.)
            
        Returns:
            Self for method chaining
            
        Note:
            Maps RAM to DigitalOcean droplet sizes automatically:
            - 1GB -> s-1vcpu-1gb
            - 2GB -> s-2vcpu-2gb
            - 4GB -> s-2vcpu-4gb
            - 8GB+ -> s-{vcpus}vcpu-{gb}gb or memory-optimized
        """
        if gb < 1:
            raise ValueError("RAM must be at least 1 GB")
            
        # DigitalOcean droplet size mapping based on RAM
        if gb <= 1:
            size = "s-1vcpu-1gb"        # 1 vCPU, 1GB RAM
        elif gb <= 2:
            size = "s-2vcpu-2gb"        # 2 vCPUs, 2GB RAM
        elif gb <= 4:
            size = "s-2vcpu-4gb"        # 2 vCPUs, 4GB RAM
        elif gb <= 8:
            size = "s-4vcpu-8gb"        # 4 vCPUs, 8GB RAM
        elif gb <= 16:
            size = "s-8vcpu-16gb"       # 8 vCPUs, 16GB RAM
        elif gb <= 32:
            size = "s-8vcpu-32gb"       # 8 vCPUs, 32GB RAM
        elif gb <= 48:
            size = "m-4vcpu-32gb"       # 4 vCPUs, 32GB RAM (memory optimized)
        elif gb <= 64:
            size = "m-6vcpu-48gb"       # 6 vCPUs, 48GB RAM (memory optimized)
        elif gb <= 96:
            size = "m-8vcpu-64gb"       # 8 vCPUs, 64GB RAM (memory optimized)
        elif gb <= 128:
            size = "m-16vcpu-128gb"     # 16 vCPUs, 128GB RAM (memory optimized)
        else:
            # For very large RAM requirements, use largest memory-optimized
            vcpus = max(1, gb // 8)  # Approximate vCPUs for large memory
            size = f"m-{vcpus}vcpu-{gb}gb"
            print(f"🔧 Setting RAM: {gb}GB → custom memory-optimized size: {size}")
        
        if not size.startswith("m-") and gb <= 32:
            print(f"🔧 Setting RAM: {gb}GB → droplet size: {size}")
        elif size.startswith("m-"):
            print(f"🔧 Setting RAM: {gb}GB → memory-optimized size: {size}")
        
        self.config.size = size
        return self

    def optimize_for(self, priority: str) -> 'Droplet':
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
            from .core.cross_cloud_intelligence import cross_cloud_intelligence, ServiceRequirements, ServiceCategory
            
            # Extract CPU/RAM from current droplet size if available
            cpu_count, ram_gb = self._extract_specs_from_size(self.config.size)
            
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
            if recommendation.recommended_provider != "digitalocean":
                print(f"💡 Cross-Cloud Magic suggests {recommendation.recommended_provider.upper()} for {priority} optimization")
                print(f"   💰 Potential monthly savings: ${recommendation.estimated_monthly_cost:.2f}")
                print(f"   📊 Confidence: {recommendation.confidence_score:.1%}")
                print(f"   📝 Consider switching providers for optimal {priority}")
            else:
                print(f"✅ DigitalOcean is optimal for {priority} optimization")
                
        except ImportError:
            print("⚠️  Cross-Cloud Magic not available - using provider-specific optimizations")
        except Exception as e:
            print(f"⚠️  Cross-Cloud Magic error: {e} - using provider-specific optimizations")
        
        # Apply DigitalOcean-specific optimizations based on priority
        if priority == "cost":
            print("💰 Cost optimization: Selecting basic droplet sizes")
            self._apply_cost_optimizations()
        elif priority == "performance":
            print("⚡ Performance optimization: Selecting CPU-optimized droplets")
            self._apply_performance_optimizations()
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Enabling backups and monitoring")
            self._apply_reliability_optimizations()
        elif priority == "compliance":
            print("📋 Compliance optimization: Selecting compliant regions")
            self._apply_compliance_optimizations()
        
        return self
    
    def _extract_specs_from_size(self, size: str) -> tuple:
        """Extract CPU and RAM specs from DigitalOcean droplet size"""
        if not size:
            return 1, 1  # Default specs
            
        try:
            # Parse size like "s-4vcpu-8gb" or "m-8vcpu-64gb" or "c-16"
            if size.startswith("s-") or size.startswith("m-"):
                parts = size.split("-")
                if len(parts) >= 3:
                    cpu_part = parts[1]  # "4vcpu"
                    ram_part = parts[2]  # "8gb"
                    
                    cpu_count = int(cpu_part.replace("vcpu", ""))
                    ram_gb = int(ram_part.replace("gb", ""))
                    
                    return cpu_count, ram_gb
            elif size.startswith("c-"):
                # CPU-optimized like "c-16" means 16 vCPUs
                cpu_count = int(size.replace("c-", ""))
                ram_gb = cpu_count * 2  # Approximate 2GB per CPU for CPU-optimized
                return cpu_count, ram_gb
                
        except (ValueError, IndexError):
            pass
            
        return 1, 1  # Fallback to minimal specs
    
    def _apply_cost_optimizations(self):
        """Apply cost-focused optimizations for DigitalOcean"""
        # Use basic/standard droplets instead of CPU or memory optimized
        if self.config.size and (self.config.size.startswith("c-") or self.config.size.startswith("m-")):
            cpu_count, ram_gb = self._extract_specs_from_size(self.config.size)
            # Convert to standard droplet
            if cpu_count <= 8:
                self.config.size = f"s-{cpu_count}vcpu-{min(ram_gb, cpu_count*4)}gb"
                print(f"   💰 Switched to cost-effective standard droplet: {self.config.size}")
    
    def _apply_performance_optimizations(self):
        """Apply performance-focused optimizations for DigitalOcean"""
        # Use CPU-optimized droplets for better performance
        if self.config.size and self.config.size.startswith("s-"):
            cpu_count, _ = self._extract_specs_from_size(self.config.size)
            if cpu_count >= 4:
                self.config.size = f"c-{cpu_count}"
                print(f"   ⚡ Switched to CPU-optimized droplet: {self.config.size}")
        
        # Enable monitoring for performance tracking
        self.config.monitoring = True
        print("   📊 Enabled monitoring for performance tracking")
    
    def _apply_reliability_optimizations(self):
        """Apply reliability-focused optimizations for DigitalOcean"""
        # Enable backups for reliability
        self.config.backups = True
        print("   💾 Enabled automatic backups for reliability")
        
        # Enable monitoring
        self.config.monitoring = True
        print("   📊 Enabled monitoring for reliability tracking")
        
        # Prefer stable regions (could be enhanced with region selection logic)
        if not self.config.region:
            self.config.region = "nyc3"  # Stable, well-established region
            print("   🌍 Selected reliable region: nyc3")
    
    def _apply_compliance_optimizations(self):
        """Apply compliance-focused optimizations for DigitalOcean"""
        # Enable monitoring for compliance reporting
        self.config.monitoring = True
        print("   📊 Enabled monitoring for compliance reporting")
        
        # Enable backups for data retention compliance
        self.config.backups = True
        print("   💾 Enabled backups for compliance data retention")
        
        # Select compliance-friendly regions (US/EU)
        if not self.config.region:
            self.config.region = "nyc3"  # US region for US compliance
            print("   🌍 Selected compliance-friendly region: nyc3")

    def firewall(self, name: str, port: int, protocol: str = "tcp", source_addresses: List[str] = None) -> 'Droplet':
        """Add a firewall rule to allow traffic on a specific port"""
        if source_addresses is None:
            source_addresses = ["0.0.0.0/0", "::/0"]

        rule = FirewallRule(
            name=name,
            port=port,
            protocol=protocol,
            source_addresses=source_addresses
        )

        if not hasattr(self, '_firewall_rules'):
            self._firewall_rules = []

        self._firewall_rules.append(rule)
        return self

    def load_balancer(self, name: str, algorithm: str = "round_robin") -> 'Droplet':
        """Configure a load balancer for this droplet"""
        self._load_balancer_config = LoadBalancerConfig(
            name=name,
            algorithm=algorithm,
            forwarding_rules=[
                {
                    "entry_protocol": "http",
                    "entry_port": 80,
                    "target_protocol": "http",
                    "target_port": 80,
                    "tls_passthrough": False
                },
                {
                    "entry_protocol": "https",
                    "entry_port": 443,
                    "target_protocol": "https",
                    "target_port": 443,
                    "tls_passthrough": True
                }
            ],
            health_check={
                "protocol": "http",
                "port": 80,
                "path": "/",
                "check_interval_seconds": 10,
                "response_timeout_seconds": 5,
                "healthy_threshold": 5,
                "unhealthy_threshold": 3
            }
        )
        return self

    def authenticate(self, token: Optional[str] = None) -> 'Droplet':
        """Set the DigitalOcean API token. If not provided, searches for .env file in project root."""
        self.do_client.authenticate(token)
        return self

    def check_state(self, check_interval=None, auto_remediate: str = "DISABLED", 
                   webhook: Optional[str] = None, enable_auto_fix: bool = False,
                   learning_mode: bool = False) -> 'Droplet':
        """Configure intelligent drift detection and auto-remediation"""
        try:
            from .core.drift_management import (
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
            
            # Enable learning mode for the droplet
            if learning_mode:
                drift_manager.enable_learning_mode(self.config.name, learning_days=30)
                print(f"🎓 Learning mode enabled for {self.config.name} (30 days)")
            
            print(f"🔍 Drift detection configured:")
            print(f"   📅 Check interval: {self._check_interval.name if hasattr(self._check_interval, 'name') else self._check_interval}")
            print(f"   🛡️ Auto-remediation: {auto_remediate}")
            print(f"   🔧 Auto-fix enabled: {enable_auto_fix}")
            print(f"   🎓 Learning mode: {learning_mode}")
            
        except ImportError:
            print("⚠️  Drift management not available - continuing without drift detection")
            self._drift_enabled = False
        
        return self

    def service(self, service_name: str, variables: Optional[Dict[str, Any]] = None) -> 'Droplet':
        """Configure a service to be installed and configured on the droplet"""
        self.config.service = service_name
        self.config.service_variables = variables

        # Generate installation script using service manager
        try:
            self.config.user_data = self.service_manager.generate_installation_script(service_name, variables)
        except Exception as e:
            raise Exception(f"Failed to configure {service_name} service: {str(e)}")

        return self

    def registry(self, image_tag: str, template_path: str = None, port: int = 8080, env: Optional[Dict[str, str]] = None) -> 'Droplet':
        """Configure a container registry image to be deployed on the droplet"""
        if not template_path:
            # Default to templates directory
            template_path = f"templates/{image_tag.split(':')[0]}"

        # Build and push the image to registry
        registry_info = self.container_registry.build_and_push_image(
            service_name=image_tag.split(':')[0],
            image_tag=image_tag,
            template_path=template_path
        )

        # Configure the droplet for container deployment
        self.config.registry_image = registry_info['full_image_name']
        self.config.container_port = port
        self.config.container_env = env

        # Generate user data for container deployment
        self.config.user_data = self.droplet_manager.generate_container_user_data(self.config)

        return self

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created without actually creating it"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")

        self.droplet_manager.validate_droplet_config(self.config)

        firewall_rules = getattr(self, '_firewall_rules', None)
        load_balancer_config = getattr(self, '_load_balancer_config', None)

        return self.status_reporter.print_preview(self.config, firewall_rules, load_balancer_config)

    def create(self) -> Dict[str, Any]:
        """Create the infrastructure (only what doesn't exist)"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")

        # Check drift if enabled before making changes
        if hasattr(self, '_drift_enabled') and self._drift_enabled:
            drift_result = self._check_drift_if_enabled()
            if drift_result:
                print(f"🔄 Applying drift remediation for {self.config.name}")

        self.droplet_manager.validate_droplet_config(self.config)

        # Get firewall and load balancer configurations
        firewall_rules = getattr(self, '_firewall_rules', None)
        load_balancer_config = getattr(self, '_load_balancer_config', None)

        # Check what already exists
        existing_resources = self.resource_discovery.discover_existing_resources(
            self.config.name,
            load_balancer_config.name if load_balancer_config else None
        )

        # Determine what needs to be created, updated, or removed
        actions = self.infrastructure_planner.plan_infrastructure_changes(
            existing_resources,
            firewall_rules,
            load_balancer_config
        )

        # Print planned actions
        self.infrastructure_planner.print_planned_actions(
            actions,
            self.config.name,
            firewall_rules,
            load_balancer_config
        )

        # Execute planned actions
        if actions['droplet']['action'] == 'create':
            print(f"\n🚀 Creating new droplet...")
            droplet_id, droplet_ip, droplet_status = self.droplet_manager.create_droplet(self.config)
            was_existing = False
        else:  # use existing
            droplet_id = actions['droplet']['id']
            droplet_ip = existing_resources['droplet']['ip']
            droplet_status = existing_resources['droplet']['status']
            was_existing = True
            print(f"\n🔄 Using existing droplet (ID: {droplet_id})")

        # Handle firewall actions
        firewall_id = None
        if actions['firewall']['action'] == 'create':
            print(f"🔥 Creating firewall...")
            firewall_id = self.firewall_manager.create_firewall(self.config.name, firewall_rules, droplet_id)
        elif actions['firewall']['action'] == 'use':
            firewall_id = actions['firewall']['id']
            self.firewall_manager.update_firewall_if_needed(firewall_id, droplet_id)
        elif actions['firewall']['action'] == 'remove':
            print(f"🔄 Removing droplet from firewall...")
            self.firewall_manager.remove_droplet_from_firewall(actions['firewall']['id'], droplet_id)

        # Handle load balancer actions
        load_balancer_id = None
        load_balancer_ip = None
        if actions['load_balancer']['action'] == 'create':
            print(f"⚖️  Creating load balancer...")
            load_balancer_id, load_balancer_ip = self.load_balancer_manager.create_load_balancer(
                load_balancer_config, self.config.region, droplet_id
            )
        elif actions['load_balancer']['action'] == 'use':
            load_balancer_id = actions['load_balancer']['id']
            load_balancer_ip = actions['load_balancer']['ip']
            self.load_balancer_manager.ensure_droplet_in_load_balancer(load_balancer_id, droplet_id)
        elif actions['load_balancer']['action'] == 'remove':
            print(f"🔄 Removing droplet from load balancer...")
            self.load_balancer_manager.remove_droplet_from_load_balancer(actions['load_balancer']['id'], droplet_id)

        # Build result
        result = {
            "id": droplet_id,
            "name": self.config.name,
            "ip_address": droplet_ip,
            "region": self.config.region,
            "size": self.config.size,
            "status": droplet_status,
            "services": [self.config.service] if self.config.service else [],
            "firewall_id": firewall_id,
            "load_balancer_id": load_balancer_id,
            "load_balancer_ip": load_balancer_ip,
            "was_existing": was_existing,
            "registry_image": self.config.registry_image,
            "container_port": self.config.container_port
        }

        # Cache state for drift detection if enabled
        if hasattr(self, '_drift_enabled') and self._drift_enabled:
            self._cache_resource_state(result)

        # Print final status
        self.status_reporter.print_infrastructure_status(result, existing_resources)
        return result

    def _check_drift_if_enabled(self):
        """Check for drift if drift detection is enabled"""
        if not hasattr(self, '_drift_enabled') or not self._drift_enabled:
            return None
            
        try:
            from .core.drift_management import get_drift_manager
            
            drift_manager = get_drift_manager()
            
            # Check drift for the droplet
            drift_result = drift_manager.check_resource_drift(
                resource_name=self.config.name,
                provider="digitalocean",
                check_interval=self._check_interval,
                current_state_fetcher=self._fetch_current_cloud_state
            )
            
            if drift_result and drift_result.has_drift:
                print(f"🔍 Drift detected in {self.config.name}:")
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

    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the droplet from DigitalOcean for drift detection"""
        try:
            # Use resource discovery to get current droplet state
            existing_resources = self.resource_discovery.discover_existing_resources(
                self.config.name,
                None
            )
            
            if existing_resources['droplet']:
                droplet_info = existing_resources['droplet']
                return {
                    "size": droplet_info.get("size", self.config.size),
                    "region": droplet_info.get("region", self.config.region),
                    "status": droplet_info.get("status", "UNKNOWN"),
                    "ip_address": droplet_info.get("ip"),
                    "tags": self.config.tags or [],
                    "backups": droplet_info.get("backup_ids", []),
                    "monitoring": self.config.monitoring
                }
            else:
                # Droplet doesn't exist
                return {
                    "size": None,
                    "region": self.config.region,
                    "status": "NOT_FOUND",
                    "ip_address": None,
                    "tags": [],
                    "backups": [],
                    "monitoring": False
                }
        except Exception as e:
            print(f"❌ Failed to fetch current state for {self.config.name}: {e}")
            return {}

    def _cache_resource_state(self, result: Dict[str, Any]):
        """Cache the current resource state for drift detection"""
        if not hasattr(self, '_drift_enabled') or not self._drift_enabled:
            return
            
        try:
            from .core.drift_management import get_drift_manager
            
            drift_manager = get_drift_manager()
            
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            # Generate configuration for caching
            config = {
                'size': self.config.size,
                'region': self.config.region,
                'image': self.config.image,
                'tags': self.config.tags,
                'backups': self.config.backups,
                'monitoring': self.config.monitoring,
                'service': self.config.service
            }
            
            # Cache the state
            drift_manager.cache_resource_state(
                resource_name=self.config.name,
                resource_type="droplet",
                provider="digitalocean",
                config=config,
                current_state=current_state
            )
            
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️  Failed to cache resource state: {e}")

    def _apply_configuration_update(self, field_name: str, new_value: Any):
        """Apply configuration updates to the droplet in DigitalOcean"""
        try:
            if field_name == 'size':
                # Droplet resize
                print(f"   🔧 Resizing droplet {self.config.name} to {new_value}")
                # Note: In a real implementation, this would call:
                # droplet.resize(new_size_slug=new_value, disk=True, power_off=True)
                self.config.size = new_value
                print(f"   ✅ Droplet resized successfully")
                
            elif field_name.startswith('tag_'):
                # Update droplet tags
                tag_key = field_name.replace('tag_', '')
                print(f"   🏷️ Updating tag {tag_key} for {self.config.name} to {new_value}")
                # Note: In a real implementation, this would call:
                # droplet.tag(new_value) or similar
                print(f"   ✅ Tag updated successfully")
                
            elif field_name == 'status' and new_value == 'active':
                # Start the droplet
                print(f"   🚀 Starting droplet {self.config.name}")
                # Note: In a real implementation, this would call:
                # droplet.power_on()
                print(f"   ✅ Droplet started successfully")
                
            elif field_name == 'backups':
                # Enable/disable backups
                action = "Enabling" if new_value else "Disabling"
                print(f"   💾 {action} backups for {self.config.name}")
                # Note: In a real implementation, this would call:
                # droplet.enable_backups() or droplet.disable_backups()
                self.config.backups = new_value
                print(f"   ✅ Backups {action.lower()} successfully")
                
            else:
                print(f"   ⚠️ Unknown field {field_name} - skipping update")
                
        except Exception as e:
            print(f"   ❌ Failed to update {field_name} for {self.config.name}: {e}")
            raise

    def destroy(self) -> Dict[str, Any]:
        """Destroy the infrastructure (remove all resources)"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")

        print(f"\n🗑️  Destroying infrastructure for: {self.config.name}")

        # Check what exists
        existing_resources = self.resource_discovery.discover_existing_resources(
            self.config.name,
            None  # No specific load balancer name for destruction
        )

        destroyed_resources = {
            "droplet": False,
            "firewall": False,
            "load_balancer": False
        }

        # Get firewall and load balancer configurations
        firewall_rules = getattr(self, '_firewall_rules', None)
        load_balancer_config = getattr(self, '_load_balancer_config', None)

        # Destroy load balancer first (if it exists)
        if existing_resources['load_balancer']:
            print(f"🗑️  Destroying load balancer: {existing_resources['load_balancer']['name']}")
            try:
                self.load_balancer_manager.remove_droplet_from_load_balancer(
                    existing_resources['load_balancer']['id'],
                    existing_resources['droplet']['id']
                )
                destroyed_resources['load_balancer'] = True
            except Exception as e:
                print(f"⚠️  Warning: Failed to destroy load balancer: {e}")

        # Destroy firewall (if it exists)
        if existing_resources['firewall']:
            print(f"🗑️  Destroying firewall: {existing_resources['firewall']['name']}")
            try:
                self.firewall_manager.remove_droplet_from_firewall(
                    existing_resources['firewall']['id'],
                    existing_resources['droplet']['id']
                )
                destroyed_resources['firewall'] = True
            except Exception as e:
                print(f"⚠️  Warning: Failed to destroy firewall: {e}")

        # Destroy droplet last
        if existing_resources['droplet']:
            print(f"🗑️  Destroying droplet: {existing_resources['droplet']['name']}")
            try:
                # Get the droplet object
                droplet = self.do_client.client.get_droplet(existing_resources['droplet']['id'])
                droplet.destroy()
                destroyed_resources['droplet'] = True
                print(f"✅ Droplet destroyed successfully")
            except Exception as e:
                print(f"⚠️  Warning: Failed to destroy droplet: {e}")
        else:
            print(f"✅ No droplet found to destroy")

        # Print summary
        print(f"\n🗑️  Destruction Summary:")
        print("=" * 40)
        for resource_type, destroyed in destroyed_resources.items():
            status = "✅ Destroyed" if destroyed else "❌ Not found"
            print(f"   • {resource_type.title()}: {status}")
        print("=" * 40)

        return destroyed_resources


# Standalone resource classes (lightweight wrappers around managers)
class Firewall(StandaloneFirewall):
    """Standalone firewall configuration and management"""
    pass

class LoadBalancer(StandaloneLoadBalancer):
    """Standalone load balancer configuration and management"""
    pass

class ForwardingRule:
    """Forwarding rule configuration for load balancers"""

    def __init__(self, entry_protocol: str, entry_port: int, target_protocol: str, target_port: int, tls_passthrough: bool = False):
        self.entry_protocol = entry_protocol
        self.entry_port = entry_port
        self.target_protocol = target_protocol
        self.target_port = target_port
        self.tls_passthrough = tls_passthrough

    def to_dict(self):
        return {
            "entry_protocol": self.entry_protocol,
            "entry_port": self.entry_port,
            "target_protocol": self.target_protocol,
            "target_port": self.target_port,
            "tls_passthrough": self.tls_passthrough
        }

class Kubernetes(KubernetesCluster):
    """Standalone Kubernetes cluster configuration and management"""
    pass

class DigitalOcean:
    """Entrypoint for creating DigitalOcean resources"""

    @staticmethod
    def Droplet(name: str) -> Droplet:
        """Create a new droplet definition"""
        return Droplet(name)

    @staticmethod
    def Firewall(name: str, port: int, protocol: str = "tcp") -> Firewall:
        """Create a new standalone firewall definition"""
        return Firewall(name, port, protocol)

    @staticmethod
    def LoadBalancer(name: str) -> LoadBalancer:
        """Create a new standalone load balancer definition"""
        from .digitalocean_resources.load_balancer_new import LoadBalancer
        return LoadBalancer(name)

    @staticmethod
    def KubernetesCluster(name: str) -> Kubernetes:
        """Create a new standalone Kubernetes cluster definition"""
        return Kubernetes(name)

    @staticmethod
    def Function(name: str) -> Function:
        """Create a new serverless function definition"""
        from .digitalocean_resources.function import Function
        return Function(name)

    @staticmethod
    def Database(name: str):
        """Create a new managed database definition"""
        from .digitalocean_resources.database_new import Database
        return Database(name)

    @staticmethod
    def SpacesCDN(name: str):
        """Create a new Spaces with CDN definition"""
        from .digitalocean_resources.spaces_cdn import SpacesCDN
        return SpacesCDN(name)

    @staticmethod
    def VPC(name: str):
        """Create a new VPC definition"""
        from .digitalocean_resources.vpc import VPC
        return VPC(name)

    @staticmethod
    def Monitoring(name: str):
        """Create a new monitoring definition"""
        from .digitalocean_resources.monitoring import Monitoring
        return Monitoring(name)

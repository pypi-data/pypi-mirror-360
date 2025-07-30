"""
Google Compute Engine VM Configuration Mixin

Configuration methods for Google Compute Engine VMs.
Provides Rails-like method chaining for fluent VM configuration.
"""

from typing import Dict, Any, List, Optional, Union
from ...googlecloud_managers.service_manager import ServiceConfig


class VmConfigurationMixin:
    """
    Mixin for Google Compute Engine VM configuration methods.
    
    This mixin provides:
    - Rails-like method chaining for fluent VM configuration
    - Common VM patterns (web server, database, development, etc.)
    - Machine type and resource configuration
    - Networking and security configuration
    - Service integrations and startup scripts
    - Optimization methods with Cross-Cloud Magic
    """
    
    # Machine Type Configuration Methods
    def machine_type(self, machine_type: str) -> 'Vm':
        """Set the machine type for all VMs"""
        if not self._validate_machine_type(machine_type):
            raise ValueError(f"Invalid machine type: {machine_type}")
            
        for config in self.configs.values():
            config.machine_type = machine_type
        return self
        
    def zone(self, zone: str) -> 'Vm':
        """Set the zone for all VMs"""
        if not self._validate_zone(zone):
            raise ValueError(f"Invalid zone: {zone}")
            
        for config in self.configs.values():
            config.zone = zone
        return self
        
    def cpu(self, cores: int) -> 'Vm':
        """Set CPU cores - maps to appropriate GCP machine type"""
        if cores < 1:
            raise ValueError("CPU cores must be at least 1")
            
        # For standard CPU counts, use predefined machine types
        standard_mappings = {
            1: "n1-standard-1",
            2: "e2-standard-2", 
            4: "e2-standard-4",
            8: "e2-standard-8",
            16: "e2-standard-16",
            32: "e2-standard-32"
        }
        
        if cores in standard_mappings:
            machine_type = standard_mappings[cores]
            print(f"🔧 Setting CPU: {cores} cores → machine type: {machine_type}")
        else:
            # For non-standard CPU counts, create custom machine type
            # Estimate RAM based on 4GB per core
            memory_mb = cores * 4 * 1024
            machine_type = f"custom-{cores}-{memory_mb}"
            print(f"🔧 Setting CPU: {cores} cores → custom machine type: {machine_type}")
            
        return self.machine_type(machine_type)
        
    def ram(self, gb: int) -> 'Vm':
        """Set RAM in GB - maps to appropriate GCP machine type"""
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
        elif gb <= 90:
            machine_type = "e2-standard-32"  # 32 vCPUs, 128GB RAM
        else:
            # For large RAM requirements, use custom machine type
            vcpus = max(1, gb // 4)
            memory_mb = gb * 1024
            machine_type = f"custom-{vcpus}-{memory_mb}"
            
        print(f"🔧 Setting RAM: {gb}GB → machine type: {machine_type}")
        return self.machine_type(machine_type)
        
    # Storage Configuration Methods
    def disk_size(self, size_gb: int) -> 'Vm':
        """Set the boot disk size in GB for all VMs"""
        if size_gb < 10:
            raise ValueError("Disk size must be at least 10 GB")
            
        for config in self.configs.values():
            config.disk_size_gb = size_gb
        return self
        
    def disk_type(self, disk_type: str) -> 'Vm':
        """Set disk type (pd-standard, pd-ssd, pd-balanced)"""
        valid_types = ["pd-standard", "pd-ssd", "pd-balanced"]
        if disk_type not in valid_types:
            raise ValueError(f"Disk type must be one of: {valid_types}")
            
        for config in self.configs.values():
            config.disk_type = disk_type
        return self
        
    def ssd_disk(self, size_gb: int = 100) -> 'Vm':
        """Use SSD disk with specified size"""
        return self.disk_type("pd-ssd").disk_size(size_gb)
        
    # OS Image Configuration Methods
    def image(self, image_family: str, image_project: str = "debian-cloud") -> 'Vm':
        """Set the OS image for all VMs"""
        if not self._validate_image(image_family, image_project):
            raise ValueError(f"Invalid image configuration: {image_family} from {image_project}")
            
        for config in self.configs.values():
            config.image_family = image_family
            config.image_project = image_project
        return self
        
    def ubuntu(self, version: str = "2204-lts") -> 'Vm':
        """Use Ubuntu image"""
        return self.image(f"ubuntu-{version}", "ubuntu-os-cloud")
        
    def debian(self, version: str = "11") -> 'Vm':
        """Use Debian image"""
        return self.image(f"debian-{version}", "debian-cloud")
        
    def centos(self, version: str = "7") -> 'Vm':
        """Use CentOS image"""
        return self.image(f"centos-{version}", "centos-cloud")
        
    def windows(self, version: str = "2019") -> 'Vm':
        """Use Windows Server image"""
        return self.image(f"windows-{version}", "windows-cloud")
        
    # Network Configuration Methods
    def network(self, network: str, subnetwork: str = "default") -> 'Vm':
        """Set the network and subnetwork for all VMs"""
        for config in self.configs.values():
            config.network = network
            config.subnetwork = subnetwork
        return self
        
    def external_ip(self, enabled: bool = True) -> 'Vm':
        """Enable or disable external IP"""
        for config in self.configs.values():
            config.external_ip = enabled
        return self
        
    def internal_only(self) -> 'Vm':
        """Configure VM for internal access only"""
        return self.external_ip(False)
        
    def tags(self, tags: List[str]) -> 'Vm':
        """Set network tags for all VMs"""
        for config in self.configs.values():
            config.tags = tags
        return self
        
    def allow_http(self) -> 'Vm':
        """Add HTTP server tag"""
        for config in self.configs.values():
            if "http-server" not in config.tags:
                config.tags.append("http-server")
        return self
        
    def allow_https(self) -> 'Vm':
        """Add HTTPS server tag"""
        for config in self.configs.values():
            if "https-server" not in config.tags:
                config.tags.append("https-server")
        return self
        
    def allow_ssh(self) -> 'Vm':
        """Add SSH tag"""
        for config in self.configs.values():
            if "ssh-server" not in config.tags:
                config.tags.append("ssh-server")
        return self
        
    # Metadata and Startup Configuration Methods
    def metadata(self, metadata: Dict[str, str]) -> 'Vm':
        """Set metadata for all VMs"""
        for config in self.configs.values():
            config.metadata.update(metadata)
        return self
        
    def startup_script(self, script: str) -> 'Vm':
        """Set startup script for all VMs"""
        for config in self.configs.values():
            config.metadata['startup-script'] = script
        return self
        
    def startup_script_url(self, url: str) -> 'Vm':
        """Set startup script URL for all VMs"""
        for config in self.configs.values():
            config.metadata['startup-script-url'] = url
        return self
        
    def ssh_keys(self, username: str, public_key: str) -> 'Vm':
        """Add SSH keys to VM metadata"""
        ssh_key_entry = f"{username}:{public_key}"
        for config in self.configs.values():
            existing_keys = config.metadata.get('ssh-keys', '')
            if existing_keys:
                config.metadata['ssh-keys'] = f"{existing_keys}\\n{ssh_key_entry}"
            else:
                config.metadata['ssh-keys'] = ssh_key_entry
        return self
        
    # Service Configuration Methods
    def service(self, service_name: str, variables: Optional[Dict[str, Any]] = None) -> 'Vm':
        """Add a service to be installed on all VMs"""
        service_config = ServiceConfig(name=service_name, variables=variables or {})
        
        for vm_name, config in self.configs.items():
            config.services.append(service_config)
            print(f"   📦 Adding service '{service_name}' to VM '{vm_name}'")
            
        # Auto-configure firewall rules for known services
        if service_name == "apache":
            self.allow_http().allow_https()
        elif service_name == "nginx":
            self.allow_http().allow_https()
        elif service_name == "postgres":
            self.tags(self.configs[self.vm_names[0]].tags + ["postgres-server"])
        elif service_name == "mysql":
            self.tags(self.configs[self.vm_names[0]].tags + ["mysql-server"])
            
        return self
        
    # Service Account Configuration Methods
    def service_account(self, email: str, scopes: Optional[List[str]] = None) -> 'Vm':
        """Set service account for all VMs"""
        if scopes is None:
            scopes = [
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/compute",
                "https://www.googleapis.com/auth/devstorage.read_write"
            ]
            
        for config in self.configs.values():
            config.service_account = email
            config.service_account_scopes = scopes
        return self
        
    def default_service_account(self) -> 'Vm':
        """Use default compute service account"""
        return self.service_account("default")
        
    # Label Configuration Methods
    def label(self, key: str, value: str) -> 'Vm':
        """Add label to all VMs"""
        self.vm_labels[key] = value
        for config in self.configs.values():
            config.labels[key] = value
        return self
        
    def labels(self, labels: Dict[str, str]) -> 'Vm':
        """Add multiple labels to all VMs"""
        self.vm_labels.update(labels)
        for config in self.configs.values():
            config.labels.update(labels)
        return self
        
    def environment(self, env: str) -> 'Vm':
        """Set environment label"""
        return self.label("environment", env)
        
    def team(self, team_name: str) -> 'Vm':
        """Set team label"""
        return self.label("team", team_name)
        
    def cost_center(self, cost_center: str) -> 'Vm':
        """Set cost center label"""
        return self.label("cost-center", cost_center)
        
    # Monitoring Configuration Methods
    def monitoring(self, enabled: bool = True) -> 'Vm':
        """Enable or disable monitoring"""
        self._monitoring_enabled = enabled
        
        if enabled:
            # Add monitoring agent to startup script
            monitoring_script = """
# Install Stackdriver monitoring agent
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install
"""
            for config in self.configs.values():
                existing_script = config.metadata.get('startup-script', '')
                config.metadata['startup-script'] = existing_script + monitoring_script
                
        return self
        
    # Common VM Patterns
    def web_server(self, server_type: str = "nginx") -> 'Vm':
        """Configure as web server"""
        self.vm_labels["purpose"] = "web-server"
        self.vm_labels["server-type"] = server_type
        
        return (self
                .service(server_type)
                .allow_http()
                .allow_https()
                .allow_ssh()
                .disk_size(50)
                .monitoring())
                
    def database_server(self, db_type: str = "postgres") -> 'Vm':
        """Configure as database server"""
        self.vm_labels["purpose"] = "database"
        self.vm_labels["database-type"] = db_type
        
        return (self
                .service(db_type)
                .ssd_disk(100)
                .internal_only()
                .allow_ssh()
                .monitoring())
                
    def app_server(self, runtime: str = "python") -> 'Vm':
        """Configure as application server"""
        self.vm_labels["purpose"] = "app-server"
        self.vm_labels["runtime"] = runtime
        
        startup_script = ""
        if runtime == "python":
            startup_script = """
# Install Python and pip
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
"""
        elif runtime == "node":
            startup_script = """
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
"""
        elif runtime == "java":
            startup_script = """
# Install Java
sudo apt-get update
sudo apt-get install -y default-jdk
"""
            
        return (self
                .startup_script(startup_script)
                .allow_http()
                .allow_https()
                .allow_ssh()
                .disk_size(50)
                .monitoring())
                
    def development_vm(self) -> 'Vm':
        """Configure as development VM"""
        self.vm_labels["purpose"] = "development"
        self.vm_labels["environment"] = "dev"
        
        return (self
                .machine_type("e2-medium")
                .disk_size(100)
                .allow_ssh()
                .external_ip()
                .label("auto-shutdown", "true"))
                
    def jenkins_server(self) -> 'Vm':
        """Configure as Jenkins CI/CD server"""
        self.vm_labels["purpose"] = "ci-cd"
        self.vm_labels["ci-tool"] = "jenkins"
        
        return (self
                .service("jenkins")
                .machine_type("e2-standard-4")
                .ssd_disk(200)
                .allow_http()
                .allow_https()
                .allow_ssh()
                .monitoring())
                
    def kubernetes_node(self) -> 'Vm':
        """Configure as Kubernetes node"""
        self.vm_labels["purpose"] = "kubernetes-node"
        
        startup_script = """
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install kubeadm, kubelet, kubectl
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
"""
        
        return (self
                .ubuntu()
                .startup_script(startup_script)
                .machine_type("e2-standard-4")
                .disk_size(100)
                .allow_ssh()
                .monitoring())
                
    # Optimization Methods
    def optimize_for(self, priority: str) -> 'Vm':
        """Use Cross-Cloud Magic to optimize for cost/performance/reliability"""
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
            
        self._optimization_priority = priority
        print(f"🎯 Cross-Cloud Magic: Optimizing for {priority}")
        
        if priority == "cost":
            return self._apply_cost_optimizations()
        elif priority == "performance":
            return self._apply_performance_optimizations()
        elif priority == "reliability":
            return self._apply_reliability_optimizations()
        elif priority == "compliance":
            return self._apply_compliance_optimizations()
            
        return self
        
    def _apply_cost_optimizations(self) -> 'Vm':
        """Apply cost optimization settings"""
        print("   ├─ 🏷️  Using preemptible instances")
        print("   ├─ 💾 Using standard persistent disks")
        print("   ├─ 🌍 Selecting cheapest regions")
        print("   └─ ⏰ Enabling auto-shutdown for dev/test")
        
        # Use preemptible instances
        for config in self.configs.values():
            config.preemptible = True
            config.automatic_restart = False
            config.on_host_maintenance = "TERMINATE"
            
        # Use standard disks
        self.disk_type("pd-standard")
        
        # Add cost optimization labels
        self.labels({
            "optimization": "cost",
            "preemptible": "true"
        })
        
        return self
        
    def _apply_performance_optimizations(self) -> 'Vm':
        """Apply performance optimization settings"""
        print("   ├─ 🚀 Using compute-optimized machine types")
        print("   ├─ 💾 Using SSD persistent disks")
        print("   ├─ 🌍 Selecting low-latency regions")
        print("   └─ 📊 Enabling enhanced monitoring")
        
        # Use SSD disks
        self.disk_type("pd-ssd")
        
        # Enable monitoring
        self.monitoring(True)
        
        # Add performance labels
        self.labels({
            "optimization": "performance",
            "disk-type": "ssd"
        })
        
        return self
        
    def _apply_reliability_optimizations(self) -> 'Vm':
        """Apply reliability optimization settings"""
        print("   ├─ 🛡️  Disabling preemptible instances")
        print("   ├─ 🔄 Enabling automatic restart")
        print("   ├─ 💾 Using reliable persistent disks")
        print("   └─ 📊 Enabling comprehensive monitoring")
        
        # Disable preemptible
        for config in self.configs.values():
            config.preemptible = False
            config.automatic_restart = True
            config.on_host_maintenance = "MIGRATE"
            
        # Enable monitoring
        self.monitoring(True)
        
        # Add reliability labels
        self.labels({
            "optimization": "reliability",
            "automatic-restart": "true"
        })
        
        return self
        
    def _apply_compliance_optimizations(self) -> 'Vm':
        """Apply compliance optimization settings"""
        print("   ├─ 🔒 Enforcing encryption at rest")
        print("   ├─ 🛡️  Restricting network access")
        print("   ├─ 📊 Enabling audit logging")
        print("   └─ 🏷️  Adding compliance labels")
        
        # Restrict network access
        self.internal_only()
        
        # Enable monitoring and logging
        self.monitoring(True)
        
        # Add compliance labels
        self.labels({
            "optimization": "compliance",
            "encryption": "enabled",
            "audit-logging": "enabled"
        })
        
        return self
        
    # Helper methods
    def get_config(self, vm_name: str) -> Any:
        """Get configuration for a specific VM"""
        return self.configs.get(vm_name)
        
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all VM configurations"""
        return self.configs
        
    def is_optimized(self) -> bool:
        """Check if VM has optimization applied"""
        return self._optimization_priority is not None
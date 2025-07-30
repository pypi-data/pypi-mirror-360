"""
Google Compute Engine VM Complete Implementation

Complete Google Compute Engine VM implementation combining core functionality,
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .vm_core import VmCore
from .vm_configuration import VmConfigurationMixin
from .vm_lifecycle import VmLifecycleMixin


class Vm(VmCore, VmConfigurationMixin, VmLifecycleMixin):
    """
    Complete Google Compute Engine VM implementation.
    
    This class combines:
    - VmCore: Basic VM attributes and authentication
    - VmConfigurationMixin: Chainable configuration methods
    - VmLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent VM configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Single and multi-VM support
    - Common VM patterns (web server, database, development, etc.)
    - Machine type and resource configuration (CPU, RAM, disk)
    - Networking and security configuration
    - Service integrations and startup scripts
    - Firewall rule management
    - Monitoring and labeling
    
    Example:
        # Single web server
        web = Vm("web-server")
        web.zone("us-central1-a").web_server("nginx")
        web.create()
        
        # Database server
        db = Vm("database")
        db.zone("us-central1-a").database_server("postgres")
        db.ssd_disk(200).internal_only()
        db.create()
        
        # Development VM
        dev = Vm("dev-machine")
        dev.zone("us-west1-a").development_vm()
        dev.ubuntu().allow_ssh()
        dev.create()
        
        # Multiple app servers
        apps = Vm(["app-1", "app-2", "app-3"])
        apps.zone("us-central1-a").app_server("python")
        apps.machine_type("e2-standard-4").monitoring()
        apps.create()
        
        # Custom configuration
        custom = Vm("custom-vm")
        custom.zone("europe-west1-b").cpu(8).ram(32)
        custom.debian().ssd_disk(500)
        custom.service("docker").service("kubernetes")
        custom.allow_ssh().allow_https()
        custom.label("project", "ml-training")
        custom.startup_script("#!/bin/bash\\napt-get update")
        custom.create()
        
        # Jenkins CI/CD server
        jenkins = Vm("jenkins-master")
        jenkins.zone("us-central1-a").jenkins_server()
        jenkins.external_ip().monitoring()
        jenkins.create()
        
        # Kubernetes nodes
        k8s_nodes = Vm(["k8s-node-1", "k8s-node-2", "k8s-node-3"])
        k8s_nodes.zone("us-central1-a").kubernetes_node()
        k8s_nodes.label("cluster", "production")
        k8s_nodes.create()
        
        # Cross-Cloud Magic optimization
        optimized = Vm("optimized-vm")
        optimized.zone("us-central1-a").web_server()
        optimized.optimize_for("cost")
        optimized.create()
    """
    
    def __init__(self, names: Union[str, List[str]]):
        """
        Initialize Google Compute Engine VM with single or multiple names.
        
        Args:
            names: Single VM name or list of VM names for multi-VM operations
        """
        # Initialize all parent classes
        VmCore.__init__(self, names)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of VM instance"""
        vm_type = self._get_vm_type_from_config()
        vm_count = len(self.vm_names)
        primary_config = list(self.configs.values())[0]
        status = "configured" if primary_config.zone else "unconfigured"
        
        if self.is_multi_vm:
            return (f"Vm(names={self.vm_names}, "
                    f"count={vm_count}, "
                    f"type='{vm_type}', "
                    f"zone='{primary_config.zone}', "
                    f"machine_type='{primary_config.machine_type}', "
                    f"status='{status}')")
        else:
            return (f"Vm(name='{self.vm_names[0]}', "
                    f"type='{vm_type}', "
                    f"zone='{primary_config.zone}', "
                    f"machine_type='{primary_config.machine_type}', "
                    f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of VM configuration.
        
        Returns:
            Dict containing all configuration details
        """
        primary_config = list(self.configs.values())[0]
        
        # Analyze VM configuration
        vm_features = []
        if primary_config.external_ip:
            vm_features.append("external_ip")
        if primary_config.services:
            vm_features.append("services")
        if primary_config.metadata.get('startup-script'):
            vm_features.append("startup_script")
        if self._monitoring_enabled:
            vm_features.append("monitoring")
        if primary_config.preemptible:
            vm_features.append("preemptible")
            
        # Analyze services
        services = []
        for config in self.configs.values():
            services.extend([s.name for s in config.services])
        unique_services = list(set(services))
        
        # Analyze networking
        network_features = []
        if "http-server" in primary_config.tags:
            network_features.append("http")
        if "https-server" in primary_config.tags:
            network_features.append("https")
        if "ssh-server" in primary_config.tags:
            network_features.append("ssh")
            
        summary = {
            "vm_names": self.vm_names,
            "vm_count": len(self.vm_names),
            "is_multi_vm": self.is_multi_vm,
            "vm_type": self._get_vm_type_from_config(),
            "vm_description": self.vm_description,
            
            # Primary configuration
            "zone": primary_config.zone,
            "machine_type": primary_config.machine_type,
            "cpu_count": self._extract_cpu_from_machine_type(primary_config.machine_type),
            "ram_gb": self._extract_ram_from_machine_type(primary_config.machine_type),
            "disk_size_gb": primary_config.disk_size_gb,
            "disk_type": primary_config.disk_type,
            
            # OS and image
            "image_family": primary_config.image_family,
            "image_project": primary_config.image_project,
            
            # Network configuration
            "network": primary_config.network,
            "subnetwork": primary_config.subnetwork,
            "external_ip": primary_config.external_ip,
            "tags": primary_config.tags,
            "network_features": network_features,
            
            # Services and startup
            "services": unique_services,
            "service_count": len(unique_services),
            "has_startup_script": bool(primary_config.metadata.get('startup-script')),
            
            # Security
            "service_account": primary_config.service_account,
            "firewall_rule_count": len(self.firewall_rules),
            
            # Features analysis
            "vm_features": vm_features,
            "monitoring_enabled": self._monitoring_enabled,
            "optimization_priority": self._optimization_priority,
            
            # Labels and metadata
            "labels": {**primary_config.labels, **self.vm_labels},
            "label_count": len(primary_config.labels) + len(self.vm_labels),
            "metadata_count": len(primary_config.metadata),
            
            # State
            "state": {
                "exists": self.vm_exists,
                "created": self.vm_created,
                "deployment_status": self.deployment_status
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_vm_cost():.2f}",
            "total_disk_gb": sum(c.disk_size_gb for c in self.configs.values()),
            "total_cpu_cores": sum(self._extract_cpu_from_machine_type(c.machine_type) for c in self.configs.values()),
            "total_ram_gb": sum(self._extract_ram_from_machine_type(c.machine_type) for c in self.configs.values())
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\\n🖥️  Google Compute Engine VM Configuration")
        
        if self.is_multi_vm:
            print(f"   📦 VM Group: {len(self.vm_names)} instances")
            print(f"   🏷️  Names: {', '.join(self.vm_names[:3])}" + 
                  (f" (+{len(self.vm_names)-3} more)" if len(self.vm_names) > 3 else ""))
        else:
            print(f"   🏷️  Name: {self.vm_names[0]}")
            
        print(f"   📝 Description: {self.vm_description}")
        print(f"   🎯 VM Type: {self._get_vm_type_from_config().replace('_', ' ').title()}")
        
        # Show primary configuration
        primary_config = list(self.configs.values())[0]
        
        print(f"\\n🖥️  Machine Configuration:")
        print(f"   📍 Zone: {primary_config.zone}")
        print(f"   🖥️  Machine Type: {primary_config.machine_type}")
        print(f"   🧮 CPU Cores: {self._extract_cpu_from_machine_type(primary_config.machine_type)}")
        print(f"   💾 RAM: {self._extract_ram_from_machine_type(primary_config.machine_type)}GB")
        
        print(f"\\n💾 Storage Configuration:")
        print(f"   📦 Boot Disk: {primary_config.disk_size_gb}GB")
        print(f"   💿 Disk Type: {primary_config.disk_type}")
        
        print(f"\\n🖼️  Operating System:")
        print(f"   🖼️  Image: {primary_config.image_family}")
        print(f"   📁 Project: {primary_config.image_project}")
        
        print(f"\\n🌐 Network Configuration:")
        print(f"   🌐 Network: {primary_config.network}")
        print(f"   🔗 Subnetwork: {primary_config.subnetwork}")
        print(f"   🌍 External IP: {'✅ Enabled' if primary_config.external_ip else '❌ Disabled'}")
        
        if primary_config.tags:
            print(f"   🏷️  Tags: {', '.join(primary_config.tags)}")
            
        if self.firewall_rules:
            print(f"   🔥 Firewall Rules: {len(self.firewall_rules)}")
            
        # Show services
        all_services = []
        for config in self.configs.values():
            all_services.extend([s.name for s in config.services])
        unique_services = list(set(all_services))
        
        if unique_services:
            print(f"\\n📦 Services ({len(unique_services)}):")
            for service in unique_services[:5]:
                print(f"   • {service}")
            if len(unique_services) > 5:
                print(f"   • ... and {len(unique_services) - 5} more")
                
        # Show startup script preview
        if primary_config.metadata.get('startup-script'):
            script = primary_config.metadata['startup-script']
            print(f"\\n📜 Startup Script:")
            lines = script.strip().split('\\n')[:3]
            for line in lines:
                print(f"   {line[:60]}{'...' if len(line) > 60 else ''}")
            if len(script.split('\\n')) > 3:
                print(f"   ... and {len(script.split('\\n')) - 3} more lines")
                
        # Show labels
        all_labels = {**primary_config.labels, **self.vm_labels}
        if all_labels:
            print(f"\\n🏷️  Labels ({len(all_labels)}):")
            for key, value in list(all_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(all_labels) > 5:
                print(f"   • ... and {len(all_labels) - 5} more")
                
        # Show optimization
        if self._optimization_priority:
            print(f"\\n🎯 Optimization: {self._optimization_priority}")
            if primary_config.preemptible:
                print(f"   • Preemptible: ✅ Enabled")
                
        # Show monitoring
        if self._monitoring_enabled:
            print(f"\\n📊 Monitoring: ✅ Enabled")
            
        # Show totals for multi-VM
        if self.is_multi_vm:
            print(f"\\n📊 Totals:")
            print(f"   🖥️  VMs: {len(self.vm_names)}")
            print(f"   🧮 Total vCPUs: {sum(self._extract_cpu_from_machine_type(c.machine_type) for c in self.configs.values())}")
            print(f"   💾 Total RAM: {sum(self._extract_ram_from_machine_type(c.machine_type) for c in self.configs.values())}GB")
            print(f"   💿 Total Disk: {sum(c.disk_size_gb for c in self.configs.values())}GB")
            
        # Cost estimate
        cost = self._estimate_vm_cost()
        print(f"\\n💰 Estimated Cost: ${cost:.2f}/month")
        
        # Console link
        if primary_config.zone:
            project_id = getattr(self.gcp_client, 'project', 'your-project') if hasattr(self, 'gcp_client') else 'your-project'
            print(f"\\n🌐 Console:")
            print(f"   🔗 https://console.cloud.google.com/compute/instances?project={project_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get VM status for backwards compatibility"""
        primary_config = list(self.configs.values())[0]
        
        return {
            "vm_names": self.vm_names,
            "vm_count": len(self.vm_names),
            "zone": primary_config.zone,
            "machine_type": primary_config.machine_type,
            "cpu_count": self._extract_cpu_from_machine_type(primary_config.machine_type),
            "ram_gb": self._extract_ram_from_machine_type(primary_config.machine_type),
            "disk_size_gb": primary_config.disk_size_gb,
            "external_ip": primary_config.external_ip,
            "services": [s.name for s in primary_config.services],
            "monitoring_enabled": self._monitoring_enabled,
            "optimization": self._optimization_priority,
            "deployment_status": self.deployment_status,
            "estimated_cost": f"${self._estimate_vm_cost():.2f}/month"
        }
    
    # Backwards compatibility methods
    def enable_monitoring(self) -> 'Vm':
        """Enable monitoring (backwards compatibility)"""
        return self.monitoring(True)
        
    def add_firewall_rule(self, rule) -> 'Vm':
        """Add firewall rule (backwards compatibility)"""
        if rule not in self.firewall_rules:
            self.firewall_rules.append(rule)
        return self


# Convenience function for creating VM instances
def create_vm(names: Union[str, List[str]]) -> Vm:
    """
    Create a new Google Compute Engine VM instance.
    
    Args:
        names: Single VM name or list of VM names
        
    Returns:
        Vm instance
    """
    return Vm(names)


# Export the class for easy importing
__all__ = ['Vm', 'create_vm']
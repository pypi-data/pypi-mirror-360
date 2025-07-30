from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..vm import Vm

class LoadBalancerManagementMixin:
    """Mixin for load balancer and health check management"""
    
    def health_check(self: 'Vm', protocol: str, port: int, path: str = "/") -> 'Vm':
        """Configure a health check for all VMs"""
        health_check_config = {
            "protocol": protocol,
            "port": port,
            "path": path
        }
        for config in self.configs.values():
            config.health_check = health_check_config
        return self

    def load_balancer(self: 'Vm', name: str, port: int = 80) -> 'Vm':
        """Configure a load balancer for all VMs"""
        from ...googlecloud_managers.load_balancer_manager import LoadBalancerConfig, BackendConfig
        
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

    def _inject_monitoring_agent(self: 'Vm'):
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

    def monitoring(self: 'Vm', enabled: bool = True) -> 'Vm':
        """Enable or disable monitoring for this VM"""
        self._monitoring_enabled = enabled
        return self

    def _create_health_checks_for_vm(self: 'Vm', vm_name: str, config):
        """Create health check if configured for a VM"""
        if config.health_check:
            try:
                self.health_check_manager.create_health_check(config.name, config.health_check)
                print(f"✅ Health check created: {config.name}-health-check")
            except Exception as e:
                print(f"⚠️  Warning: Failed to create health check: {str(e)}")

    def _create_load_balancer_if_configured(self: 'Vm', vm_results: dict):
        """Create load balancer if configured for the VM group"""
        if self._load_balancer_config:
            try:
                lb_result = self.load_balancer_manager.create_load_balancer(self._load_balancer_config)
                print(f"✅ Load balancer created: {lb_result['ip_address']}")
                # Add load balancer info to all VM results
                for vm_result in vm_results.values():
                    vm_result['load_balancer'] = lb_result
                return lb_result
            except Exception as e:
                print(f"⚠️  Warning: Failed to create load balancer: {str(e)}")
                return None

    def _destroy_health_checks(self: 'Vm', results: dict):
        """Destroy health checks for all VMs"""
        for vm_name in self.vm_names:
            config = self.configs[vm_name]
            if config.health_check:
                try:
                    health_check_name = f"{vm_name}-health-check"
                    success = self.health_check_manager.delete_health_check(health_check_name)
                    results["health_checks"][vm_name] = success
                    if success:
                        print(f"✅ Health check destroyed: {health_check_name}")
                except Exception as e:
                    print(f"⚠️  Warning: Failed to destroy health check for {vm_name}: {str(e)}")

    def _destroy_load_balancer(self: 'Vm', results: dict):
        """Destroy load balancer if configured"""
        if self._load_balancer_config:
            try:
                success = self.load_balancer_manager.delete_load_balancer(self._load_balancer_config.name)
                results["load_balancer"] = success
                if success:
                    print(f"✅ Load balancer destroyed: {self._load_balancer_config.name}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to destroy load balancer: {str(e)}") 
import os
import yaml
from typing import Dict, Any, Optional, List
from jinja2 import Template


class ServiceConfig:
    """Configuration class for services"""
    
    def __init__(self, service_name: str, config: Dict[str, Any] = None):
        self.service_name = service_name
        self.config = config or {}
        
    def get_packages(self) -> List[str]:
        """Get required packages"""
        return self.config.get("packages", [])
        
    def get_services(self) -> List[str]:
        """Get services to manage"""
        return self.config.get("services", [])
        
    def get_commands(self) -> List[str]:
        """Get custom commands"""
        return self.config.get("commands", [])


class GcpServiceManager:
    """Manages service installation and configuration for Google Cloud VMs"""
    
    def __init__(self):
        self.templates_dir = "templates"
    
    def generate_startup_script(self, service_name: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """Generate a startup script for a service from template"""
        if variables is None:
            variables = {}
        
        # Check if service template exists
        service_dir = os.path.join(self.templates_dir, service_name)
        if not os.path.exists(service_dir):
            raise Exception(f"Service template not found: {service_name}")
        
        # Look for service.yaml configuration
        service_config_path = os.path.join(service_dir, "service.yaml")
        if os.path.exists(service_config_path):
            with open(service_config_path, 'r') as f:
                service_config = yaml.safe_load(f)
        else:
            # Default configuration
            service_config = {
                "packages": [],
                "services": [],
                "files": [],
                "commands": []
            }
        
        # Generate the startup script
        script_lines = [
            "#!/bin/bash",
            "set -e",
            "",
            "# Update system",
            "apt-get update",
            ""
        ]
        
        # Handle different service.yaml formats
        if "pre_install" in service_config:
            # New format (like nginx template)
            script_lines.append("# Pre-installation steps")
            for step in service_config.get("pre_install", []):
                script_lines.append(step)
            
            # Handle file deployments
            if "files" in service_config:
                script_lines.append("")
                script_lines.append("# Deploy service files")
                
                # Handle directories
                if "directories" in service_config["files"]:
                    for dir_config in service_config["files"]["directories"]:
                        source = dir_config.get("source")
                        target = dir_config.get("target")
                        if source and target:
                            source_path = os.path.join(service_dir, source)
                            if os.path.exists(source_path):
                                script_lines.append(f"mkdir -p {target}")
                                script_lines.append(f"cp -r {source_path}/* {target}/")
                
                # Handle individual files
                if "files" in service_config["files"]:
                    for file_config in service_config["files"]["files"]:
                        source = file_config.get("source")
                        target = file_config.get("target")
                        if source and target:
                            source_path = os.path.join(service_dir, source)
                            if os.path.exists(source_path):
                                dest_dir = os.path.dirname(target)
                                script_lines.append(f"mkdir -p {dest_dir}")
                                script_lines.append(f"cp {source_path} {target}")
            
            # Handle post-installation steps
            if "post_install" in service_config:
                script_lines.append("")
                script_lines.append("# Post-installation steps")
                for step in service_config["post_install"]:
                    script_lines.append(step)
        
        else:
            # Old format (simple packages/services/commands)
            # Add package installation
            if service_config.get("packages"):
                script_lines.append("# Install required packages")
                script_lines.append(f"apt-get install -y {' '.join(service_config['packages'])}")
            
            # Add custom commands
            if service_config.get("commands"):
                script_lines.append("")
                script_lines.append("# Run custom commands")
                for command in service_config["commands"]:
                    script_lines.append(command)
            
            # Add file deployment
            if service_config.get("files"):
                script_lines.append("")
                script_lines.append("# Deploy service files")
                for file_config in service_config["files"]:
                    source = file_config.get("source")
                    destination = file_config.get("destination")
                    if source and destination:
                        # Create destination directory if needed
                        dest_dir = os.path.dirname(destination)
                        script_lines.append(f"mkdir -p {dest_dir}")
                        script_lines.append(f"cp {source} {destination}")
            
            # Add service management
            if service_config.get("services"):
                script_lines.append("")
                script_lines.append("# Start and enable services")
                for service in service_config["services"]:
                    script_lines.append(f"systemctl start {service}")
                    script_lines.append(f"systemctl enable {service}")
        
        # Add template-specific startup script if it exists
        startup_script_path = os.path.join(service_dir, "startup.sh")
        if os.path.exists(startup_script_path):
            script_lines.append("")
            script_lines.append("# Service-specific startup script")
            with open(startup_script_path, 'r') as f:
                startup_content = f.read()
                # Replace variables in the startup script
                template = Template(startup_content)
                startup_content = template.render(**variables)
                script_lines.append(startup_content)
        
        # Add health check
        script_lines.append("")
        script_lines.append("# Wait for services to be ready")
        script_lines.append("sleep 10")
        script_lines.append("")
        script_lines.append("# Check if services are running")
        
        # Determine which services to check
        services_to_check = []
        if "post_install" in service_config:
            # Look for systemctl commands in post_install
            for step in service_config.get("post_install", []):
                if "systemctl enable" in step:
                    service_name = step.split()[-1]
                    services_to_check.append(service_name)
        elif service_config.get("services"):
            services_to_check = service_config["services"]
        
        if services_to_check:
            for service in services_to_check:
                script_lines.append(f"if systemctl is-active --quiet {service}; then")
                script_lines.append(f"    echo '✅ {service} is running'")
                script_lines.append("else")
                script_lines.append(f"    echo '❌ {service} failed to start'")
                script_lines.append(f"    systemctl status {service}")
                script_lines.append("    exit 1")
                script_lines.append("fi")
        
        script_lines.append("")
        script_lines.append("echo '🎉 Service deployment completed successfully!'")
        
        return "\n".join(script_lines)
    
    def get_available_services(self) -> list:
        """Get list of available service templates"""
        if not os.path.exists(self.templates_dir):
            return []
        
        services = []
        for item in os.listdir(self.templates_dir):
            item_path = os.path.join(self.templates_dir, item)
            if os.path.isdir(item_path):
                services.append(item)
        
        return services 
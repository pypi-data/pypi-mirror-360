import os
import yaml
from typing import Optional, List, Dict, Any
from jinja2 import Template
from pydantic import BaseModel


class ServiceConfig(BaseModel):
    name: str
    description: str
    pre_install: List[str]
    files: Dict[str, Any]
    post_install: List[str]
    health_check: Dict[str, Any]
    variables: Dict[str, Any]


class ServiceManager:
    """Manages service templates, configuration loading, and file processing"""
    
    def __init__(self):
        # Look for templates in the current directory first, then in package templates
        self._template_paths = [
            os.path.join(os.getcwd(), "templates"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "templates")
        ]
    
    def find_service_template(self, service: str) -> Optional[str]:
        """Find the service template directory"""
        for base_path in self._template_paths:
            service_path = os.path.join(base_path, service)
            if os.path.exists(service_path):
                return service_path
        return None
    
    def load_service_config(self, service_path: str) -> ServiceConfig:
        """Load and validate the service configuration"""
        config_path = os.path.join(service_path, "service.yaml")
        if not os.path.exists(config_path):
            raise ValueError(f"Service configuration not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return ServiceConfig(**config)
    
    def process_template(self, template_path: str, variables: Dict[str, Any]) -> str:
        """Process a template file with variables"""
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        template = Template(template_content)
        return template.render(**variables)
    
    def generate_file_copy_commands(self, service_path: str, service_config: ServiceConfig, variables: Dict[str, Any]) -> List[str]:
        """Generate commands to copy and configure files"""
        commands = []
        
        # Create temporary directory
        commands.append("mkdir -p /tmp/service_setup")
        
        # Process directories
        for dir_config in service_config.files.get('directories', []):
            source_dir = os.path.join(service_path, dir_config['source'])
            if os.path.exists(source_dir):
                target_dir = dir_config['target']
                commands.extend([
                    f"mkdir -p {target_dir}",
                    f"cp -r {source_dir}/* {target_dir}/",
                    f"chown -R {dir_config['owner']}:{dir_config['group']} {target_dir}",
                    f"chmod -R {dir_config['mode']} {target_dir}"
                ])
        
        # Process individual files
        for file_config in service_config.files.get('files', []):
            source_file = os.path.join(service_path, file_config['source'])
            if os.path.exists(source_file):
                target_file = file_config['target']
                target_dir = os.path.dirname(target_file)
                
                # If it's a template file, process it
                if source_file.endswith(('.conf', '.template', '.html')):
                    processed_content = self.process_template(source_file, variables)
                    temp_file = f"/tmp/service_setup/{os.path.basename(source_file)}"
                    commands.extend([
                        f"cat > {temp_file} << 'EOL'\n{processed_content}\nEOL",
                        f"mkdir -p {target_dir}",
                        f"mv {temp_file} {target_file}",
                    ])
                else:
                    commands.extend([
                        f"mkdir -p {target_dir}",
                        f"cp {source_file} {target_file}",
                    ])
                
                commands.extend([
                    f"chown {file_config['owner']}:{file_config['group']} {target_file}",
                    f"chmod {file_config['mode']} {target_file}"
                ])
        
        return commands
    
    def generate_installation_script(self, service_name: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """Generate the complete installation script for a service"""
        # Find service template
        service_path = self.find_service_template(service_name)
        if not service_path:
            raise ValueError(f"Service template not found: {service_name}")
        
        try:
            # Load service configuration
            service_config = self.load_service_config(service_path)
            
            # Merge variables
            final_variables = {**service_config.variables, **(variables or {})}
            
            # Generate installation script
            script_parts = [
                "#!/bin/bash",
                "set -e",  # Exit on any error
                "",
                "# Pre-installation steps",
                *service_config.pre_install,
                "",
                "# File setup",
                *self.generate_file_copy_commands(service_path, service_config, final_variables),
                "",
                "# Post-installation steps",
                *service_config.post_install,
                "",
                "# Cleanup",
                "rm -rf /tmp/service_setup",
                "",
                "# Health check",
                f"echo 'Waiting for service to be ready (timeout: {service_config.health_check['timeout']}s)...'",
                "for i in $(seq 1 30); do",
                f"    if curl -sf http://localhost:{service_config.health_check['port']}{service_config.health_check['path']} >/dev/null 2>&1; then",
                "        echo 'Service is ready!'",
                "        exit 0",
                "    fi",
                "    sleep 1",
                "done",
                "echo 'Service failed to start properly'",
                "exit 1"
            ]
            
            return "\n".join(script_parts)
            
        except Exception as e:
            raise Exception(f"Failed to configure {service_name} service: {str(e)}") 
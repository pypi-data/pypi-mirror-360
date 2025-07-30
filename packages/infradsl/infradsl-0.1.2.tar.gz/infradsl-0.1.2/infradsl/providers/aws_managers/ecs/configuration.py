"""
ECS Configuration and DSL Methods

This module provides Rails-like chainable methods and configuration builders for ECS services.
"""

from typing import Dict, Any, List, Optional


class EcsConfigurationManager:
    """
    ECS Configuration and DSL Methods
    
    Handles:
    - Rails-like chainable methods
    - Workload-specific configurations (web, api, microservice, background)
    - Size configurations and resource sizing
    - Configuration validation and defaults
    """
    
    def __init__(self, ecs_service):
        """Initialize with reference to the ECS service instance."""
        self.service = ecs_service
    
    # Rails-like chainable methods
    def fargate(self):
        """Configure for AWS Fargate (serverless containers) - chainable"""
        self.service.launch_type = 'FARGATE'
        self.service.network_mode = 'awsvpc'
        return self.service
    
    def ec2(self):
        """Configure for EC2 launch type - chainable"""
        self.service.launch_type = 'EC2'
        return self.service
    
    def container(self, image: str, port: int = 80):
        """Set container image and port - chainable"""
        self.service.image = image
        self.service.port = port
        return self.service
    
    # Workload-specific configurations
    def web(self):
        """Configure for web application workload - chainable"""
        self.service.cpu = '512'
        self.service.memory = '1024'
        self.service.port = 80
        self.service.public_ip = True
        self.service.health_check = {
            'command': ['CMD-SHELL', 'curl -f http://localhost/ || exit 1'],
            'interval': 30,
            'timeout': 5,
            'retries': 3,
            'start_period': 60
        }
        return self.service
    
    def api(self):
        """Configure for API service workload - chainable"""
        self.service.cpu = '256'
        self.service.memory = '512'
        self.service.port = 8080
        self.service.public_ip = True
        self.service.health_check = {
            'command': ['CMD-SHELL', 'curl -f http://localhost:8080/health || exit 1'],
            'interval': 30,
            'timeout': 5,
            'retries': 3,
            'start_period': 30
        }
        return self.service
    
    def microservice(self):
        """Configure for microservice workload - chainable"""
        self.service.cpu = '256'
        self.service.memory = '512'
        self.service.port = 3000
        self.service.public_ip = False  # Private by default
        self.service.desired_count = 2  # Multiple instances for resilience
        self.service.health_check = {
            'command': ['CMD-SHELL', 'curl -f http://localhost:3000/health || exit 1'],
            'interval': 30,
            'timeout': 5,
            'retries': 3,
            'start_period': 45
        }
        return self.service
    
    def background(self):
        """Configure for background/worker service - chainable"""
        self.service.cpu = '512'
        self.service.memory = '1024'
        self.service.port = None  # No port for background services
        self.service.public_ip = False
        self.service.desired_count = 1
        self.service.health_check = None  # Background services often don't need health checks
        return self.service
    
    # Size configurations
    def small(self):
        """Use small instance size (256 CPU, 512 MB) - chainable"""
        self.service.cpu = '256'
        self.service.memory = '512'
        return self.service
    
    def medium(self):
        """Use medium instance size (512 CPU, 1024 MB) - chainable"""
        self.service.cpu = '512'
        self.service.memory = '1024'
        return self.service
    
    def large(self):
        """Use large instance size (1024 CPU, 2048 MB) - chainable"""
        self.service.cpu = '1024'
        self.service.memory = '2048'
        return self.service
    
    def xlarge(self):
        """Use extra large instance size (2048 CPU, 4096 MB) - chainable"""
        self.service.cpu = '2048'
        self.service.memory = '4096'
        return self.service
    
    def instances(self, count: int):
        """Set desired number of running instances - chainable"""
        self.service.desired_count = count
        return self.service
    
    # Network configuration
    def public(self):
        """Make service publicly accessible - chainable"""
        self.service.public_ip = True
        return self.service
    
    def private(self):
        """Make service private (internal only) - chainable"""
        self.service.public_ip = False
        return self.service
    
    # Environment configuration
    def env(self, key: str, value: str):
        """Add environment variable - chainable"""
        self.service.environment_variables[key] = value
        return self.service
    
    def envs(self, env_dict: Dict[str, str]):
        """Add multiple environment variables - chainable"""
        self.service.environment_variables.update(env_dict)
        return self.service
    
    def secret(self, key: str, secret_arn: str):
        """Add a secret from Systems Manager or Secrets Manager - chainable"""
        self.service.secrets[key] = secret_arn
        return self.service
    
    def secrets(self, secrets_dict: Dict[str, str]):
        """Add multiple secrets - chainable"""
        self.service.secrets.update(secrets_dict)
        return self.service
    
    # Auto-scaling configuration
    def auto_scale(self, min_capacity: int = 1, max_capacity: int = 10, target_cpu: int = 70):
        """Enable auto scaling with configuration - chainable"""
        self.service.auto_scaling = {
            'min_capacity': min_capacity,
            'max_capacity': max_capacity,
            'target_cpu_utilization': target_cpu,
            'target_memory_utilization': None,
            'scale_out_cooldown': 300,
            'scale_in_cooldown': 300
        }
        return self.service
    
    def auto_scale_memory(self, target_memory: int = 80):
        """Add memory-based auto scaling - chainable"""
        if not self.service.auto_scaling:
            self.auto_scale()  # Initialize with defaults
        self.service.auto_scaling['target_memory_utilization'] = target_memory
        return self.service
    
    # Health check configuration
    def health_check(self, command: List[str], interval: int = 30, timeout: int = 5, retries: int = 3, start_period: int = 60):
        """Configure container health check - chainable"""
        self.service.health_check = {
            'command': command,
            'interval': interval,
            'timeout': timeout,
            'retries': retries,
            'start_period': start_period
        }
        return self.service
    
    def no_health_check(self):
        """Disable health checks - chainable"""
        self.service.health_check = None
        return self.service
    
    # Load balancer configuration
    def with_load_balancer(self, target_group_arn: str, container_port: Optional[int] = None):
        """Configure load balancer integration - chainable"""
        port = container_port or self.service.port
        self.service.load_balancer = {
            'target_group_arn': target_group_arn,
            'container_name': self.service.name,
            'container_port': port
        }
        return self.service
    
    # Service discovery configuration
    def with_service_discovery(self, namespace: str, service_name: Optional[str] = None):
        """Configure service discovery - chainable"""
        self.service.service_discovery = {
            'namespace': namespace,
            'service_name': service_name or self.service.name,
            'dns_type': 'A',
            'dns_ttl': 60
        }
        return self.service
    
    # Container Magic integration
    def container_magic(self, auto_build: bool = True, auto_push: bool = True, auto_deploy: bool = False):
        """Enable Container Magic with Universal Container Engine - chainable"""
        self.service.container_magic_enabled = True
        self.service.auto_build_enabled = auto_build
        self.service.auto_push_enabled = auto_push
        self.service.auto_deploy_enabled = auto_deploy
        return self.service
    
    def dockerfile_template(self, template_name: str):
        """Set Dockerfile template for Container Magic - chainable"""
        self.service.dockerfile_template = template_name
        return self.service
    
    # Logging configuration
    def with_logging(self, log_group: Optional[str] = None):
        """Enable CloudWatch logging - chainable"""
        self.service.enable_logging = True
        if log_group:
            self.service.log_group = log_group
        return self.service
    
    def no_logging(self):
        """Disable CloudWatch logging - chainable"""
        self.service.enable_logging = False
        self.service.log_group = None
        return self.service
    
    # Tag configuration
    def tag(self, key: str, value: str):
        """Add a tag - chainable"""
        self.service.service_tags[key] = value
        return self.service
    
    def tags(self, tags_dict: Dict[str, str]):
        """Add multiple tags - chainable"""
        self.service.service_tags.update(tags_dict)
        return self.service
    
    # Quick deployment methods
    def quick_deploy(self, image: str, port: int = 80) -> Dict[str, Any]:
        """Quick deployment with minimal configuration"""
        self.service.image = image
        self.service.port = port
        
        print(f"🚀 Quick deploying {image} on port {port}")
        return self.service.create()
    
    def deploy_from_github(self, repo_url: str, dockerfile_path: str = "Dockerfile") -> Dict[str, Any]:
        """Deploy directly from GitHub repository with Container Magic"""
        if not self.service.container_magic_enabled:
            self.container_magic()
        
        self.service.dockerfile_path = dockerfile_path
        # In a real implementation, this would clone the repo and build
        print(f"🔗 Deploying from GitHub: {repo_url}")
        print(f"📝 Using Dockerfile: {dockerfile_path}")
        
        # Enable auto-build since we're building from source
        self.service.auto_build_enabled = True
        return self.service.create()
    
    # Convenience methods
    def set_image(self, image: str):
        """Update container image"""
        self.service.image = image
        print(f"✅ Container image updated to: {image}")
        return self.service
    
    def add_environment_variable(self, key: str, value: str):
        """Add an environment variable"""
        self.service.environment_variables[key] = value
        return self.service
    
    def add_secret(self, key: str, secret_arn: str):
        """Add a secret from Systems Manager or Secrets Manager"""
        self.service.secrets[key] = secret_arn
        return self.service
    
    def enable_auto_scaling(self, min_capacity: int = 1, max_capacity: int = 10, target_cpu: int = 70):
        """Enable auto scaling with default settings"""
        return self.auto_scale(min_capacity, max_capacity, target_cpu)
    
    def set_health_check(self, command: List[str], interval: int = 30, timeout: int = 5, retries: int = 3):
        """Configure container health check"""
        return self.health_check(command, interval, timeout, retries)
    
    # Validation methods
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current ECS configuration."""
        errors = []
        warnings = []
        
        # Required fields
        if not self.service.image and not self.service.container_magic_enabled:
            errors.append("Container image is required unless Container Magic is enabled")
        
        if not self.service.name:
            errors.append("Service name is required")
        
        # CPU/Memory validation for Fargate
        if self.service.launch_type == 'FARGATE':
            valid_cpu_memory = {
                '256': ['512', '1024', '2048'],
                '512': ['1024', '2048', '3072', '4096'],
                '1024': ['2048', '3072', '4096', '5120', '6144', '7168', '8192'],
                '2048': ['4096', '5120', '6144', '7168', '8192', '9216', '10240', '11264', '12288', '13312', '14336', '15360', '16384'],
                '4096': ['8192', '9216', '10240', '11264', '12288', '13312', '14336', '15360', '16384']
            }
            
            if self.service.cpu not in valid_cpu_memory:
                errors.append(f"Invalid CPU value '{self.service.cpu}' for Fargate")
            elif self.service.memory not in valid_cpu_memory.get(self.service.cpu, []):
                errors.append(f"Invalid memory '{self.service.memory}' for CPU '{self.service.cpu}' in Fargate")
        
        # Port validation
        if self.service.port and not isinstance(self.service.port, int):
            errors.append("Port must be an integer")
        
        if self.service.port and (self.service.port < 1 or self.service.port > 65535):
            errors.append("Port must be between 1 and 65535")
        
        # Auto-scaling validation
        if self.service.auto_scaling:
            min_cap = self.service.auto_scaling.get('min_capacity', 1)
            max_cap = self.service.auto_scaling.get('max_capacity', 10)
            
            if min_cap >= max_cap:
                errors.append("Auto-scaling min_capacity must be less than max_capacity")
            
            if min_cap < 1:
                errors.append("Auto-scaling min_capacity must be at least 1")
        
        # Health check validation
        if self.service.health_check and self.service.port is None:
            warnings.append("Health check configured but no port specified")
        
        # Public IP validation
        if self.service.launch_type == 'EC2' and self.service.public_ip:
            warnings.append("public_ip setting only applies to Fargate launch type")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            'service_name': self.service.name,
            'cluster_name': self.service.cluster_name,
            'image': self.service.image or 'Container Magic (auto-build)',
            'launch_type': self.service.launch_type,
            'cpu': f"{self.service.cpu} units",
            'memory': f"{self.service.memory} MB",
            'port': self.service.port,
            'desired_count': self.service.desired_count,
            'public_ip': self.service.public_ip if self.service.launch_type == 'FARGATE' else 'N/A',
            'environment_variables': len(self.service.environment_variables),
            'secrets': len(self.service.secrets),
            'health_check': bool(self.service.health_check),
            'auto_scaling': bool(self.service.auto_scaling),
            'load_balancer': bool(self.service.load_balancer),
            'service_discovery': bool(self.service.service_discovery),
            'container_magic': self.service.container_magic_enabled,
            'logging': self.service.enable_logging,
            'tags': len(self.service.service_tags)
        }
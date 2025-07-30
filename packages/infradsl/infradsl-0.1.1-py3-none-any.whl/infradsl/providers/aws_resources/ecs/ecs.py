"""
AWS ECS Complete Implementation

Combines all ECS functionality through multiple inheritance:
- ECSCore: Core attributes and authentication
- ECSConfigurationMixin: Chainable configuration methods  
- ECSLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from .ecs_core import ECSCore
from .ecs_configuration import ECSConfigurationMixin
from .ecs_lifecycle import ECSLifecycleMixin


class ECS(ECSLifecycleMixin, ECSConfigurationMixin, ECSCore):
    """
    Complete AWS ECS implementation for containerized applications.
    
    This class combines:
    - Container service configuration (image, CPU, memory, networking)
    - Service lifecycle management (create, destroy, preview)
    - Auto-scaling and load balancer integration
    - Health checks and service discovery
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str, **kwargs):
        """Initialize ECS instance for container service management"""
        super().__init__(name, **kwargs)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$15.50/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._auto_scaling_configured = False
        self._load_balancer_configured = False
        
    def validate_configuration(self):
        """Validate the current ECS configuration"""
        errors = []
        warnings = []
        
        # Validate service name
        if not self.name:
            errors.append("Service name is required")
        elif not self._is_valid_service_name(self.name):
            errors.append("Invalid service name format")
        
        # Validate container image
        if not self.image:
            errors.append("Container image is required")
        
        # Validate CPU and memory for Fargate
        if self.launch_type == 'FARGATE':
            valid_cpu_memory_combos = {
                '256': ['512', '1024', '2048'],
                '512': ['1024', '2048', '3072', '4096'],
                '1024': ['2048', '3072', '4096', '5120', '6144', '7168', '8192'],
                '2048': ['4096', '5120', '6144', '7168', '8192', '9216', '10240', '11264', '12288', '13312', '14336', '15360', '16384'],
                '4096': ['8192', '9216', '10240', '11264', '12288', '13312', '14336', '15360', '16384']
            }
            
            if self.cpu not in valid_cpu_memory_combos:
                errors.append(f"Invalid CPU value for Fargate: {self.cpu}")
            elif self.memory not in valid_cpu_memory_combos.get(self.cpu, []):
                errors.append(f"Invalid memory value {self.memory} for CPU {self.cpu}")
        
        # Validate network configuration
        if self.launch_type == 'FARGATE' and self.network_mode != 'awsvpc':
            errors.append("Fargate requires awsvpc network mode")
        
        # Validate desired count
        if not isinstance(self.desired_count, int) or self.desired_count < 0:
            errors.append("Desired count must be a non-negative integer")
        
        # Validate port
        if not (1 <= self.port <= 65535):
            errors.append("Port must be between 1 and 65535")
        
        # Validate environment variables
        for key, value in self.environment_variables.items():
            if not isinstance(key, str) or not isinstance(value, str):
                errors.append(f"Environment variable {key} must be a string")
        
        # Validate auto-scaling configuration
        if self.auto_scaling:
            min_cap = self.auto_scaling.get('min_capacity', 1)
            max_cap = self.auto_scaling.get('max_capacity', 10)
            if min_cap > max_cap:
                errors.append("Auto-scaling min_capacity cannot be greater than max_capacity")
            if min_cap > self.desired_count or self.desired_count > max_cap:
                warnings.append("Desired count should be between auto-scaling min and max capacity")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_service_info(self):
        """Get complete information about the ECS service"""
        return {
            'service_name': self.name,
            'cluster_name': self.cluster_name,
            'image': self.image,
            'task_definition_family': self.task_definition_family,
            'cpu': self.cpu,
            'memory': self.memory,
            'port': self.port,
            'desired_count': self.desired_count,
            'launch_type': self.launch_type,
            'network_mode': self.network_mode,
            'public_ip': self.public_ip,
            'cluster_arn': self.cluster_arn,
            'service_arn': self.service_arn,
            'task_definition_arn': self.task_definition_arn,
            'service_status': self.service_status,
            'running_count': self.running_count,
            'pending_count': self.pending_count,
            'service_url': self.service_url,
            'environment_variables_count': len(self.environment_variables),
            'secrets_count': len(self.secrets),
            'health_check_enabled': bool(self.health_check),
            'auto_scaling_enabled': bool(self.auto_scaling),
            'load_balancer_enabled': bool(self.load_balancer),
            'service_discovery_enabled': bool(self.service_discovery),
            'logging_enabled': self.enable_logging,
            'log_group': self.log_group,
            'security_groups_count': len(self.security_groups),
            'subnets_count': len(self.subnets),
            'tags_count': len(self.service_tags),
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'container_magic_enabled': self.container_magic_enabled
        }
    
    def clone(self, new_name: str):
        """Create a copy of this service with a new name"""
        cloned_service = ECS(new_name)
        cloned_service.cluster_name = f"{new_name}-cluster"
        cloned_service.task_definition_family = f"{new_name}-task"
        cloned_service.image = self.image
        cloned_service.cpu = self.cpu
        cloned_service.memory = self.memory
        cloned_service.port = self.port
        cloned_service.desired_count = self.desired_count
        cloned_service.launch_type = self.launch_type
        cloned_service.network_mode = self.network_mode
        cloned_service.public_ip = self.public_ip
        cloned_service.environment_variables = self.environment_variables.copy()
        cloned_service.secrets = self.secrets.copy()
        cloned_service.health_check = self.health_check.copy() if self.health_check else None
        cloned_service.auto_scaling = self.auto_scaling.copy() if self.auto_scaling else None
        cloned_service.load_balancer = self.load_balancer.copy() if self.load_balancer else None
        cloned_service.service_discovery = self.service_discovery.copy() if self.service_discovery else None
        cloned_service.service_tags = self.service_tags.copy()
        cloned_service.execution_role_arn = self.execution_role_arn
        cloned_service.task_role_arn = self.task_role_arn
        cloned_service.security_groups = self.security_groups.copy()
        cloned_service.subnets = self.subnets.copy()
        cloned_service.enable_logging = self.enable_logging
        cloned_service.log_group = self.log_group
        return cloned_service
    
    def export_configuration(self):
        """Export service configuration for backup or migration"""
        return {
            'metadata': {
                'service_name': self.name,
                'cluster_name': self.cluster_name,
                'task_definition_family': self.task_definition_family,
                'launch_type': self.launch_type,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'image': self.image,
                'cpu': self.cpu,
                'memory': self.memory,
                'port': self.port,
                'desired_count': self.desired_count,
                'network_mode': self.network_mode,
                'public_ip': self.public_ip,
                'environment_variables': self.environment_variables,
                'secrets': self.secrets,
                'health_check': self.health_check,
                'auto_scaling': self.auto_scaling,
                'load_balancer': self.load_balancer,
                'service_discovery': self.service_discovery,
                'execution_role_arn': self.execution_role_arn,
                'task_role_arn': self.task_role_arn,
                'security_groups': self.security_groups,
                'subnets': self.subnets,
                'enable_logging': self.enable_logging,
                'log_group': self.log_group,
                'platform_version': self.platform_version,
                'placement_constraints': self.placement_constraints,
                'service_registries': self.service_registries,
                'optimization_priority': self._optimization_priority,
                'container_magic_enabled': self.container_magic_enabled
            },
            'tags': self.service_tags
        }
    
    def import_configuration(self, config_data: dict):
        """Import service configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.image = config.get('image')
            self.cpu = config.get('cpu', '256')
            self.memory = config.get('memory', '512')
            self.port = config.get('port', 80)
            self.desired_count = config.get('desired_count', 1)
            self.network_mode = config.get('network_mode', 'awsvpc')
            self.public_ip = config.get('public_ip', True)
            self.environment_variables = config.get('environment_variables', {})
            self.secrets = config.get('secrets', {})
            self.health_check = config.get('health_check')
            self.auto_scaling = config.get('auto_scaling')
            self.load_balancer = config.get('load_balancer')
            self.service_discovery = config.get('service_discovery')
            self.execution_role_arn = config.get('execution_role_arn')
            self.task_role_arn = config.get('task_role_arn')
            self.security_groups = config.get('security_groups', [])
            self.subnets = config.get('subnets', [])
            self.enable_logging = config.get('enable_logging', True)
            self.log_group = config.get('log_group')
            self.platform_version = config.get('platform_version', 'LATEST')
            self.placement_constraints = config.get('placement_constraints', [])
            self.service_registries = config.get('service_registries', [])
            self._optimization_priority = config.get('optimization_priority')
            self.container_magic_enabled = config.get('container_magic_enabled', False)
        
        if 'tags' in config_data:
            self.service_tags = config_data['tags']
        
        return self
    
    def _is_valid_service_name(self, service_name: str) -> bool:
        """Validate ECS service name according to AWS rules"""
        import re
        
        # Service name can be 1-255 characters
        if len(service_name) < 1 or len(service_name) > 255:
            return False
        
        # Must contain only letters, numbers, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9-_]+$', service_name):
            return False
        
        return True
    
    def optimize_for(self, priority: str):
        """Use Cross-Cloud Magic to optimize for cost/performance/reliability
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        self._optimization_priority = priority
        print(f"🎯 Cross-Cloud Magic: Optimizing ECS for {priority}")
        
        # Apply AWS ECS-specific optimizations
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective container service")
            self._apply_cost_optimizations()
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance container service")
            self._apply_performance_optimizations()
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable container service")
            self._apply_reliability_optimizations()
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant container service")
            self._apply_compliance_optimizations()
        
        return self
    
    def _apply_cost_optimizations(self):
        """Apply AWS ECS-specific cost optimizations"""
        # Use Spot instances for EC2 launch type
        if self.launch_type == 'EC2':
            print("   💰 Consider using Spot instances for EC2 launch type")
        
        # Optimize CPU and memory allocation
        if int(self.cpu) > 512:
            print(f"   💰 Consider reducing CPU from {self.cpu} to 512 for cost savings")
        
        if int(self.memory) > 1024:
            print(f"   💰 Consider reducing memory from {self.memory} to 1024 for cost savings")
        
        # Configure auto-scaling for cost optimization
        if not self.auto_scaling:
            print("   💰 Enabling auto-scaling for cost optimization")
            self.enable_auto_scaling(min_capacity=1, max_capacity=3, target_cpu=80)
            self._auto_scaling_configured = True
        
        # Add cost optimization tags
        self.service_tags.update({
            "cost-optimized": "true",
            "auto-scaling": "enabled"
        })
    
    def _apply_performance_optimizations(self):
        """Apply AWS ECS-specific performance optimizations"""
        # Increase CPU and memory for better performance
        if int(self.cpu) < 1024:
            print(f"   ⚡ Increasing CPU from {self.cpu} to 1024 for performance")
            self.cpu = '1024'
        
        if int(self.memory) < 2048:
            print(f"   ⚡ Increasing memory from {self.memory} to 2048 for performance")
            self.memory = '2048'
        
        # Configure auto-scaling for performance
        if not self.auto_scaling:
            print("   ⚡ Enabling auto-scaling for performance optimization")
            self.enable_auto_scaling(min_capacity=2, max_capacity=10, target_cpu=60)
            self._auto_scaling_configured = True
        
        # Enable Application Load Balancer
        if not self.load_balancer:
            print("   ⚡ Performance: Consider enabling Application Load Balancer")
        
        # Add performance tags
        self.service_tags.update({
            "performance-optimized": "true",
            "high-availability": "enabled"
        })
    
    def _apply_reliability_optimizations(self):
        """Apply AWS ECS-specific reliability optimizations"""
        # Ensure minimum task count for high availability
        if self.desired_count < 2:
            print(f"   🛡️ Increasing desired count from {self.desired_count} to 2 for reliability")
            self.desired_count = 2
        
        # Configure health checks
        if not self.health_check:
            print("   🛡️ Enabling health checks for reliability")
            self.set_health_check(
                command=["CMD-SHELL", f"curl -f http://localhost:{self.port}/health || exit 1"],
                interval=30,
                timeout=5,
                retries=3
            )
        
        # Configure auto-scaling for reliability
        if not self.auto_scaling:
            print("   🛡️ Enabling auto-scaling for reliability")
            self.enable_auto_scaling(min_capacity=2, max_capacity=6, target_cpu=70)
            self._auto_scaling_configured = True
        
        # Enable logging
        if not self.enable_logging:
            print("   🛡️ Enabling CloudWatch logging for monitoring")
            self.enable_logging = True
        
        # Add reliability tags
        self.service_tags.update({
            "reliability-optimized": "true",
            "health-checks": "enabled",
            "monitoring": "enabled"
        })
    
    def _apply_compliance_optimizations(self):
        """Apply AWS ECS-specific compliance optimizations"""
        # Disable public IP for compliance
        if self.public_ip:
            print("   📋 Disabling public IP for compliance and security")
            self.public_ip = False
        
        # Ensure task role is configured
        if not self.task_role_arn:
            print("   📋 Consider configuring task role for fine-grained permissions")
        
        # Enable logging for audit trail
        if not self.enable_logging:
            print("   📋 Enabling CloudWatch logging for audit compliance")
            self.enable_logging = True
        
        # Add compliance tags
        self.service_tags.update({
            "compliance-optimized": "true",
            "audit-enabled": "true",
            "security-hardened": "true"
        })


# Convenience functions for creating ECS instances
def create_service(name: str, image: str, port: int = 80, cpu: str = '256', memory: str = '512') -> ECS:
    """Create a new ECS service with basic configuration"""
    service = ECS(name)
    service.set_image(image)
    service.port = port
    service.cpu = cpu
    service.memory = memory
    return service

def create_web_service(name: str, image: str, port: int = 80) -> ECS:
    """Create an ECS service configured for web applications"""
    service = ECS(name)
    service.set_image(image).fargate()
    service.port = port
    service.cpu = '512'
    service.memory = '1024'
    service.enable_auto_scaling(min_capacity=2, max_capacity=10, target_cpu=70)
    return service

def create_api_service(name: str, image: str, port: int = 8080) -> ECS:
    """Create an ECS service configured for API applications"""
    service = ECS(name)
    service.set_image(image).fargate()
    service.port = port
    service.cpu = '512'
    service.memory = '1024'
    service.set_health_check(
        command=["CMD-SHELL", f"curl -f http://localhost:{port}/health || exit 1"],
        interval=30,
        timeout=5,
        retries=3
    )
    return service

def create_background_service(name: str, image: str) -> ECS:
    """Create an ECS service for background/worker processes"""
    service = ECS(name)
    service.set_image(image).fargate()
    service.cpu = '256'
    service.memory = '512'
    service.desired_count = 1
    # No port mapping for background services
    service.port = None
    return service
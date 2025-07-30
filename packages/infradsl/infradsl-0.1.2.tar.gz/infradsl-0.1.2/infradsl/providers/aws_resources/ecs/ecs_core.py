from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseAwsResource
from infradsl.container_engine import UniversalContainerEngine


class ECSCore(BaseAwsResource):
    def __init__(
        self,
        name: str,
        cluster_name: Optional[str] = None,
        image: Optional[str] = None,
        task_definition_family: Optional[str] = None,
        cpu: str = '256',
        memory: str = '512',
        port: int = 80,
        desired_count: int = 1,
        launch_type: str = 'FARGATE',
        network_mode: str = 'awsvpc',
        public_ip: bool = True,
        environment_variables: Optional[Dict[str, str]] = None,
        secrets: Optional[Dict[str, str]] = None,
        health_check: Optional[Dict[str, Any]] = None,
        auto_scaling: Optional[Dict[str, Any]] = None,
        load_balancer: Optional[Dict[str, Any]] = None,
        service_discovery: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        super().__init__(name)

        # Core service configuration
        self.cluster_name = cluster_name or f"{name}-cluster"
        self.image = image
        self.task_definition_family = task_definition_family or f"{name}-task"
        self.cpu = cpu
        self.memory = memory
        self.port = port
        self.desired_count = desired_count
        self.launch_type = launch_type
        self.network_mode = network_mode
        self.public_ip = public_ip
        self.environment_variables = environment_variables or {}
        self.secrets = secrets or {}
        self.health_check = health_check
        self.auto_scaling = auto_scaling
        self.load_balancer = load_balancer
        self.service_discovery = service_discovery
        self.service_tags = tags or {}

        # Extended configuration from kwargs
        self.execution_role_arn = kwargs.get('execution_role_arn')
        self.task_role_arn = kwargs.get('task_role_arn')
        self.security_groups = kwargs.get('security_groups', [])
        self.subnets = kwargs.get('subnets', [])
        self.platform_version = kwargs.get('platform_version', 'LATEST')
        self.enable_logging = kwargs.get('enable_logging', True)
        self.log_group = kwargs.get('log_group')
        self.placement_constraints = kwargs.get('placement_constraints', [])
        self.service_registries = kwargs.get('service_registries', [])

        # Service state
        self.cluster_arn = None
        self.service_arn = None
        self.task_definition_arn = None
        self.service_status = None
        self.running_count = 0
        self.pending_count = 0
        self.service_url = None

        # Managers
        self.ecs_manager = None

        # Universal Container Engine
        self.container_engine = None
        self.container_magic_enabled = False
        self.auto_build_enabled = False
        self.auto_push_enabled = False
        self.auto_deploy_enabled = False
        self.dockerfile_template = None

    def _initialize_managers(self):
        self.ecs_manager = None

    def _post_authentication_setup(self):
        from ..aws_managers.aws_client import AwsClient
        self.aws_client = AwsClient()
        self.aws_client.authenticate(silent=True)

        if not self.execution_role_arn:
            self._setup_execution_role()

        if not self.security_groups:
            self._setup_default_security_group()

        if not self.subnets:
            self._setup_default_subnets()

        if not self.log_group and self.enable_logging:
            self.log_group = f"/ecs/{self.name}"

    def create(self):
        """Create/update ECS service - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .ecs_lifecycle import ECSLifecycleMixin
        # Call the lifecycle mixin's create method
        return ECSLifecycleMixin.create(self)

    def destroy(self):
        """Destroy ECS service - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .ecs_lifecycle import ECSLifecycleMixin
        # Call the lifecycle mixin's destroy method
        return ECSLifecycleMixin.destroy(self)

    def preview(self):
        """Preview ECS service configuration"""
        return {
            "resource_type": "AWS ECS Service",
            "service_name": self.name,
            "cluster_name": self.cluster_name,
            "image": self.image,
            "task_definition_family": self.task_definition_family,
            "cpu": self.cpu,
            "memory": self.memory,
            "port": self.port,
            "desired_count": self.desired_count,
            "launch_type": self.launch_type,
            "network_mode": self.network_mode,
            "public_ip": self.public_ip,
            "environment_variables": self.environment_variables,
            "health_check_enabled": bool(self.health_check),
            "auto_scaling_enabled": bool(self.auto_scaling),
            "load_balancer_enabled": bool(self.load_balancer),
            "service_discovery_enabled": bool(self.service_discovery),
            "logging_enabled": self.enable_logging,
            "log_group": self.log_group,
            "estimated_monthly_cost": self._estimate_monthly_cost(),
            "container_magic_enabled": self.container_magic_enabled
        }

    def _estimate_monthly_cost(self) -> str:
        """Estimate monthly cost for ECS service"""
        # Basic Fargate pricing calculation
        vcpu_hours_per_month = float(self.cpu) / 1024 * 24 * 30 * self.desired_count
        memory_gb_hours_per_month = float(self.memory) / 1024 * 24 * 30 * self.desired_count
        
        # Fargate pricing (US East)
        vcpu_cost = vcpu_hours_per_month * 0.04048  # $0.04048 per vCPU per hour
        memory_cost = memory_gb_hours_per_month * 0.004445  # $0.004445 per GB per hour
        
        total_cost = vcpu_cost + memory_cost
        return f"${total_cost:.2f}"

        if self.container_magic_enabled:
            self.container_engine = UniversalContainerEngine()
            self.container_engine.auto_deploy(self.auto_deploy_enabled)

    def _setup_execution_role(self):
        account_id = self.aws_client.get_account_id()
        self.execution_role_arn = f"arn:aws:iam::{account_id}:role/ecsTaskExecutionRole"

    def _setup_default_security_group(self):
        pass

    def _setup_default_subnets(self):
        pass

    def _get_all_tags(self) -> Dict[str, str]:
        default_tags = {
            'Name': self.name,
            'ManagedBy': 'InfraDSL',
            'Environment': 'development',
            'Resource': 'ECSService'
        }
        default_tags.update(self.service_tags)
        return default_tags

    def _estimate_monthly_cost(self) -> str:
        if self.launch_type == 'FARGATE':
            cpu_cost = int(self.cpu) * 0.00001251 * 24 * 30
            memory_cost = int(self.memory) * 0.00000137 * 24 * 30
            total_per_task = (cpu_cost + memory_cost) * self.desired_count
            return f"~${total_per_task:.2f} (Fargate: {self.desired_count} tasks)"
        else:
            return f"EC2 launch type - depends on underlying EC2 instances"
    
    def get_ecs_client(self, region: str = None):
        """Get ECS client for this resource"""
        return self.get_client('ecs', region)
    
    def get_client(self, service_name: str, region: str = None):
        """Get AWS client for specified service"""
        from ..auth_service import AwsAuthenticationService
        return AwsAuthenticationService.get_client(service_name, region)
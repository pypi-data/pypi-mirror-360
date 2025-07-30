from typing import Dict, Any, List, Optional


class ECSConfigurationMixin:
    def set_image(self, image: str):
        self.image = image
        print(f"✅ Container image updated to: {image}")
        return self

    def add_environment_variable(self, key: str, value: str):
        self.environment_variables[key] = value
        return self

    def add_secret(self, key: str, secret_arn: str):
        self.secrets[key] = secret_arn
        return self

    def enable_auto_scaling(self, min_capacity: int = 1, max_capacity: int = 10, target_cpu: int = 70):
        self.auto_scaling = {
            'min_capacity': min_capacity,
            'max_capacity': max_capacity,
            'target_cpu_utilization': target_cpu
        }
        return self

    def set_health_check(self, command: List[str], interval: int = 30, timeout: int = 5, retries: int = 3):
        self.health_check = {
            'command': command,
            'interval': interval,
            'timeout': timeout,
            'retries': retries,
            'startPeriod': 60
        }
        return self

    def quick_deploy(self, image: str, port: int = 80) -> Dict[str, Any]:
        self.image = image
        self.port = port

        print(f"🚀 Quick deploying {image} on port {port}")
        return self.create()

    def fargate(self):
        self.launch_type = 'FARGATE'
        self.network_mode = 'awsvpc'
        return self

    def ec2(self):
        self.launch_type = 'EC2'
        return self

    def container_image(self, image: str):
        """Set container image"""
        self.image = image
        return self

    def cpu_units(self, cpu_units: int):
        """Set CPU units (256, 512, 1024, etc.)"""
        self.cpu = str(cpu_units)
        return self

    def memory_mb(self, memory_mb: int):
        """Set memory in MB"""
        self.memory = str(memory_mb)
        return self

    def instances(self, count: int):
        """Set desired number of running tasks"""
        self.desired_count = count
        return self

    def port(self, port: int):
        """Set container port"""
        self.port = port
        return self

    def cluster(self, cluster_name: str):
        """Set ECS cluster name"""
        self.cluster_name = cluster_name
        return self

    def container(self, image: str, port: int = 80):
        """Set container image and port"""
        self.image = image
        self.port = port
        return self

    def web(self):
        self.cpu = '512'
        self.memory = '1024'
        self.port = 80
        self.public_ip = True
        self.health_check = {
            'path': '/',
            'interval': 30,
            'timeout': 5,
            'healthy_threshold': 2,
            'unhealthy_threshold': 5
        }
        return self

    def api(self):
        self.cpu = '256'
        self.memory = '512'
        self.port = 8080
        self.public_ip = True
        self.health_check = {
            'path': '/health',
            'interval': 30,
            'timeout': 5,
            'healthy_threshold': 2,
            'unhealthy_threshold': 3
        }
        return self

    def microservice(self):
        self.cpu = '256'
        self.memory = '512'
        self.port = 3000
        self.public_ip = False
        self.desired_count = 2
        return self

    def background(self):
        self.cpu = '512'
        self.memory = '1024'
        self.port = None
        self.public_ip = False
        self.desired_count = 1
        return self

    def small(self):
        self.cpu = '256'
        self.memory = '512'
        return self

    def medium(self):
        self.cpu = '512'
        self.memory = '1024'
        return self

    def large(self):
        self.cpu = '1024'
        self.memory = '2048'
        return self

    def xlarge(self):
        self.cpu = '2048'
        self.memory = '4096'
        return self

    def instances(self, count: int):
        self.desired_count = count
        return self

    def public(self):
        self.public_ip = True
        return self

    def private(self):
        self.public_ip = False
        return self

    def env(self, key: str, value: str):
        self.environment_variables[key] = value
        return self

    def envs(self, env_dict: Dict[str, str]):
        self.environment_variables.update(env_dict)
        return self

    def listen_port(self, port_number: int):
        self.port = port_number
        return self

    def cluster(self, cluster_name: str):
        self.cluster_name = cluster_name
        return self

    def region(self, region_name: str):
        return self

    def tags(self, tag_dict: Dict[str, str]):
        self.service_tags.update(tag_dict)
        return self

    def tag(self, key: str, value: str):
        self.service_tags[key] = value
        return self

    def autoscale(self, min_capacity: int = 1, max_capacity: int = 10, target_cpu: int = 70):
        self.auto_scaling = {
            'min_capacity': min_capacity,
            'max_capacity': max_capacity,
            'target_cpu_utilization': target_cpu,
            'scale_out_cooldown': 300,
            'scale_in_cooldown': 300
        }
        return self

    def health_check_path(self, path: str):
        if not self.health_check:
            self.health_check = {}
        self.health_check['path'] = path
        return self

    def logs(self, group_name: str):
        self.log_group = group_name
        self.enable_logging = True
        return self

    def container_magic(self, enabled: bool = True):
        self.container_magic_enabled = enabled
        return self

    def container_engine(self, engine_name: str):
        if not self.container_engine:
            self.container_engine = UniversalContainerEngine(preferred_engine=engine_name)
        else:
            self.container_engine.engine(engine_name)
        return self

    def dockerfile_template(self, template_path: str = None):
        self.dockerfile_template = template_path
        return self

    def auto_build(self, enabled: bool = True):
        self.auto_build_enabled = enabled
        return self

    def auto_push(self, enabled: bool = True, registry: str = None):
        self.auto_push_enabled = enabled
        if registry and self.container_engine:
            self.container_engine.registry(registry)
        return self

    def auto_deploy(self, enabled: bool = True):
        self.auto_deploy_enabled = enabled
        return self

    def universal_deploy(self, project_path: str = "."):
        if not self.container_engine:
            self.container_engine = UniversalContainerEngine()

        print(f"✨ Starting Universal Container Magic for ECS...")

        self.container_engine.auto_deploy(True)

        result = self.container_engine.magic(project_path)

        if result["success"]:
            print(f"🚀 Container magic completed! Ready for ECS deployment.")
            return self.create()
        else:
            print(f"❌ Container magic failed: {result.get('error', 'Unknown error')}")
            return result

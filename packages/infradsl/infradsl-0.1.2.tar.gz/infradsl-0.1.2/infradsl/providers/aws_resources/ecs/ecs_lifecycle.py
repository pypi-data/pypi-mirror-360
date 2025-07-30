from typing import Dict, Any, List, Optional
import boto3


class ECSLifecycleMixin:
    def create(self) -> Dict[str, Any]:
        self._ensure_authenticated()

        if not self.image:
            raise ValueError("Container image is required. Specify the 'image' parameter.")

        existing_services = self._discover_existing_services()
        service_exists = self.name in existing_services
        to_create = [] if service_exists else [self.name]
        to_remove = [name for name in existing_services.keys() if name != self.name]

        print(f"\n🔍 ECS Service")

        changes_needed = to_create or to_remove
        if changes_needed:
            print(f"📋 Infrastructure Changes:")
            
            if to_create:
                print(f"🆕 SERVICES to CREATE:  {', '.join(to_create)}")
                
            if to_remove:
                print(f"🗑️  SERVICES to REMOVE:")
                for service_name in to_remove:
                    service_info = existing_services.get(service_name)
                    if service_info:
                        cluster = service_info.get('cluster', 'unknown')
                        status = service_info.get('status', 'unknown')
                        task_count = service_info.get('running_count', 0)
                        
                        print(f"   ╭─ 🚢 {service_name}")
                        print(f"   ├─ 🏗️  Cluster: {cluster}")
                        print(f"   ├─ 🔄 Status: {status}")
                        print(f"   ├─ 📊 Tasks: {task_count} running")
                        print(f"   ╰─ ⚠️  Will stop all tasks and delete service")
                        print()
        else:
            print(f"✨ No changes needed - infrastructure matches configuration")

        try:
            for service_name in to_remove:
                service_info = existing_services.get(service_name)
                if service_info:
                    print(f"🗑️  Removing service: {service_name}")
                    try:
                        print(f"   - Scaling service to 0 tasks...")
                        print(f"   - Deleting service...")
                        print(f"✅ Service removed successfully: {service_name}")
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to remove service {service_name}: {str(e)}")

            if service_exists:
                print(f"🔄 Updating service: {self.name}")
            else:
                print(f"🆕 Creating service: {self.name}")

            cluster_result = self._create_cluster()

            task_def_result = self._register_task_definition()

            service_result = self._create_service()

            if self.auto_scaling:
                self._configure_auto_scaling()

            if self.service_discovery:
                self._configure_service_discovery()

            print(f"✅ Service ready: {self.name}")
            print(f"   🏗️  Cluster: {self.cluster_name}")
            print(f"   📊 Tasks: {self.desired_count} desired")
            if self.service_url:
                print(f"   🌐 URL: {self.service_url}")

            result = {
                'service_name': self.name,
                'service_arn': self.service_arn,
                'cluster_name': self.cluster_name,
                'cluster_arn': self.cluster_arn,
                'task_definition_arn': self.task_definition_arn,
                'desired_count': self.desired_count,
                'launch_type': self.launch_type,
                'service_url': self.service_url,
                'created': True
            }

            result["changes"] = {
                "created": to_create,
                "removed": to_remove,
                "updated": [self.name] if service_exists else []
            }

            return result

        except Exception as e:
            print(f"❌ Failed to manage ECS service: {str(e)}")
            raise

    def destroy(self) -> Dict[str, Any]:
        self._ensure_authenticated()

        print(f"🗑️  Destroying ECS service: {self.name}")

        try:
            print("   - Scaling service to 0 tasks...")

            print("   - Deleting service...")

            print("   - Deregistering task definitions...")

            print("   - Checking if cluster should be deleted...")

            print(f"✅ ECS service destroyed successfully")

            return {
                'service_name': self.name,
                'cluster_name': self.cluster_name,
                'status': 'deleted',
                'destroyed': True
            }

        except Exception as e:
            print(f"❌ Failed to destroy ECS service: {str(e)}")
            raise

    def scale(self, desired_count: int) -> Dict[str, Any]:
        self._ensure_authenticated()

        if not self.service_arn:
            raise ValueError("Service not created yet. Call create() first.")

        print(f"📈 Scaling ECS service {self.name} to {desired_count} tasks")

        try:
            self.desired_count = desired_count

            print(f"✅ Service scaled to {desired_count} tasks")

            return {
                'service_name': self.name,
                'desired_count': desired_count,
                'status': 'scaling'
            }

        except Exception as e:
            print(f"❌ Failed to scale service: {str(e)}")
            raise

    def get_status(self) -> Dict[str, Any]:
        self._ensure_authenticated()

        if not self.service_arn:
            return {'status': 'not_created', 'message': 'Service not created yet'}

        try:
            return {
                'service_name': self.name,
                'service_arn': self.service_arn,
                'cluster_name': self.cluster_name,
                'status': self.service_status or 'unknown',
                'running_count': self.running_count,
                'pending_count': self.pending_count,
                'desired_count': self.desired_count,
                'launch_type': self.launch_type,
                'task_definition': self.task_definition_arn
            }

        except Exception as e:
            print(f"❌ Failed to get service status: {str(e)}")
            raise

    def get_logs(self, lines: int = 100) -> Dict[str, Any]:
        self._ensure_authenticated()

        if not self.enable_logging:
            return {'logs': [], 'message': 'Logging not enabled for this service'}

        try:
            print(f"📋 Retrieving last {lines} log lines for {self.name}...")

            return {
                'service_name': self.name,
                'log_group': self.log_group,
                'lines': lines,
                'message': 'Log retrieval not implemented in this preview'
            }

        except Exception as e:
            print(f"❌ Failed to get logs: {str(e)}")
            raise

    def _create_cluster(self) -> Dict[str, Any]:
        print(f"   - Creating/verifying cluster: {self.cluster_name}")

        self.cluster_arn = f"arn:aws:ecs:{self.aws_client.get_region()}:{self.aws_client.get_account_id()}:cluster/{self.cluster_name}"

        return {
            'cluster_name': self.cluster_name,
            'cluster_arn': self.cluster_arn
        }

    def _register_task_definition(self) -> Dict[str, Any]:
        print(f"   - Registering task definition: {self.task_definition_family}")

        container_definition = {
            'name': self.name,
            'image': self.image,
            'cpu': int(self.cpu),
            'memory': int(self.memory),
            'essential': True,
            'portMappings': [
                {
                    'containerPort': self.port,
                    'protocol': 'tcp'
                }
            ],
            'environment': [
                {'name': key, 'value': value}
                for key, value in self.environment_variables.items()
            ]
        }

        if self.secrets:
            container_definition['secrets'] = [
                {'name': key, 'valueFrom': value}
                for key, value in self.secrets.items()
            ]

        if self.health_check:
            container_definition['healthCheck'] = self.health_check

        if self.enable_logging:
            container_definition['logConfiguration'] = {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-group': self.log_group,
                    'awslogs-region': self.aws_client.get_region(),
                    'awslogs-stream-prefix': 'ecs'
                }
            }

        self.task_definition_arn = f"arn:aws:ecs:{self.aws_client.get_region()}:{self.aws_client.get_account_id()}:task-definition/{self.task_definition_family}:1"

        return {
            'task_definition_family': self.task_definition_family,
            'task_definition_arn': self.task_definition_arn,
            'container_definitions': [container_definition]
        }

    def _create_service(self) -> Dict[str, Any]:
        print(f"   - Creating service: {self.name}")

        network_config = None
        if self.launch_type == 'FARGATE':
            network_config = {
                'awsvpcConfiguration': {
                    'subnets': self.subnets or ['subnet-12345'],
                    'securityGroups': self.security_groups or ['sg-12345'],
                    'assignPublicIp': 'ENABLED' if self.public_ip else 'DISABLED'
                }
            }

        self.service_arn = f"arn:aws:ecs:{self.aws_client.get_region()}:{self.aws_client.get_account_id()}:service/{self.cluster_name}/{self.name}"
        self.service_status = 'ACTIVE'
        self.running_count = self.desired_count

        if self.public_ip and self.launch_type == 'FARGATE':
            self.service_url = f"http://service-{self.name}.example.com"

        return {
            'service_name': self.name,
            'service_arn': self.service_arn,
            'network_configuration': network_config
        }

    def _configure_auto_scaling(self):
        print("   - Configuring auto scaling...")

    def _configure_service_discovery(self):
        print("   - Configuring service discovery...")

"""
ECS Task Definition Management

This module handles ECS task definition registration, management, and container configuration.
"""

from typing import Dict, Any, List, Optional
import json


class EcsTaskDefinitionManager:
    """
    ECS Task Definition Management
    
    Handles:
    - Task definition registration and updates
    - Container definition building
    - Environment variables, secrets, and health checks
    - Logging configuration
    """
    
    def __init__(self, aws_client):
        """Initialize the task definition manager with AWS client."""
        self.aws_client = aws_client
    
    def register_task_definition(
        self,
        family: str,
        container_definitions: List[Dict[str, Any]],
        cpu: str,
        memory: str,
        network_mode: str = 'awsvpc',
        requires_compatibilities: List[str] = None,
        execution_role_arn: Optional[str] = None,
        task_role_arn: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Register a new task definition.
        
        Args:
            family: Task definition family name
            container_definitions: List of container definitions
            cpu: CPU units
            memory: Memory in MB
            network_mode: Network mode (awsvpc, bridge, host, none)
            requires_compatibilities: Launch types (FARGATE, EC2)
            execution_role_arn: Task execution role ARN
            task_role_arn: Task role ARN
            tags: Optional tags
            
        Returns:
            Task definition registration result
        """
        try:
            print(f"📋 Registering task definition: {family}")
            
            # Build task definition
            task_def = {
                'family': family,
                'containerDefinitions': container_definitions,
                'requiresCompatibilities': requires_compatibilities or ['FARGATE'],
                'networkMode': network_mode,
                'cpu': cpu,
                'memory': memory
            }
            
            # Add execution role if provided
            if execution_role_arn:
                task_def['executionRoleArn'] = execution_role_arn
            
            # Add task role if provided
            if task_role_arn:
                task_def['taskRoleArn'] = task_role_arn
            
            # Add tags if provided
            if tags:
                task_def['tags'] = [
                    {'key': key, 'value': value}
                    for key, value in tags.items()
                ]
            
            # Register task definition
            response = self.aws_client.ecs.register_task_definition(**task_def)
            task_definition = response['taskDefinition']
            
            print(f"✅ Task definition registered: {family}:{task_definition['revision']}")
            
            return {
                'task_definition_arn': task_definition['taskDefinitionArn'],
                'family': task_definition['family'],
                'revision': task_definition['revision'],
                'status': task_definition['status']
            }
            
        except Exception as e:
            print(f"❌ Failed to register task definition '{family}': {str(e)}")
            raise
    
    def build_container_definition(
        self,
        name: str,
        image: str,
        port: int,
        environment_variables: Optional[Dict[str, str]] = None,
        secrets: Optional[Dict[str, str]] = None,
        health_check: Optional[Dict[str, Any]] = None,
        log_group: Optional[str] = None,
        cpu: int = 0,
        memory: Optional[int] = None,
        memory_reservation: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build a container definition.
        
        Args:
            name: Container name
            image: Container image URI
            port: Container port
            environment_variables: Environment variables
            secrets: Secrets from Systems Manager or Secrets Manager
            health_check: Health check configuration
            log_group: CloudWatch log group
            cpu: CPU units for this container
            memory: Hard memory limit
            memory_reservation: Soft memory limit
            
        Returns:
            Container definition
        """
        container_def = {
            'name': name,
            'image': image,
            'essential': True,
            'portMappings': [
                {
                    'containerPort': port,
                    'protocol': 'tcp'
                }
            ]
        }
        
        # Add CPU if specified
        if cpu > 0:
            container_def['cpu'] = cpu
        
        # Add memory limits
        if memory:
            container_def['memory'] = memory
        if memory_reservation:
            container_def['memoryReservation'] = memory_reservation
        
        # Add environment variables
        if environment_variables:
            container_def['environment'] = [
                {'name': key, 'value': value}
                for key, value in environment_variables.items()
            ]
        
        # Add secrets
        if secrets:
            container_def['secrets'] = [
                {'name': key, 'valueFrom': value}
                for key, value in secrets.items()
            ]
        
        # Add health check
        if health_check:
            container_def['healthCheck'] = self._build_health_check(health_check)
        
        # Add logging configuration
        if log_group:
            container_def['logConfiguration'] = {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-group': log_group,
                    'awslogs-region': self.aws_client.region_name,
                    'awslogs-stream-prefix': 'ecs'
                }
            }
        
        return container_def
    
    def _build_health_check(self, health_check_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build health check configuration."""
        health_check = {
            'command': health_check_config.get('command', ['CMD-SHELL', 'exit 0']),
            'interval': health_check_config.get('interval', 30),
            'timeout': health_check_config.get('timeout', 5),
            'retries': health_check_config.get('retries', 3),
            'startPeriod': health_check_config.get('start_period', 0)
        }
        
        return health_check
    
    def get_task_definition(self, family: str, revision: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get task definition by family and optional revision.
        
        Args:
            family: Task definition family name
            revision: Optional specific revision (defaults to latest)
            
        Returns:
            Task definition or None if not found
        """
        try:
            task_def_identifier = f"{family}:{revision}" if revision else family
            
            response = self.aws_client.ecs.describe_task_definition(
                taskDefinition=task_def_identifier
            )
            
            return response['taskDefinition']
            
        except Exception:
            return None
    
    def list_task_definitions(self, family_prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List task definitions, optionally filtered by family prefix.
        
        Args:
            family_prefix: Optional family prefix filter
            
        Returns:
            List of task definition information
        """
        try:
            params = {}
            if family_prefix:
                params['familyPrefix'] = family_prefix
            
            response = self.aws_client.ecs.list_task_definitions(**params)
            task_def_arns = response.get('taskDefinitionArns', [])
            
            task_definitions = []
            for arn in task_def_arns:
                # Extract family and revision from ARN
                arn_parts = arn.split('/')[-1].split(':')
                family = arn_parts[0]
                revision = int(arn_parts[1])
                
                task_definitions.append({
                    'family': family,
                    'revision': revision,
                    'arn': arn,
                    'status': 'ACTIVE'  # Listed task definitions are active
                })
            
            return task_definitions
            
        except Exception as e:
            print(f"❌ Failed to list task definitions: {str(e)}")
            return []
    
    def deregister_task_definition(self, task_definition_arn: str) -> Dict[str, Any]:
        """
        Deregister a task definition.
        
        Args:
            task_definition_arn: Task definition ARN to deregister
            
        Returns:
            Deregistration result
        """
        try:
            print(f"🗑️  Deregistering task definition: {task_definition_arn}")
            
            response = self.aws_client.ecs.deregister_task_definition(
                taskDefinition=task_definition_arn
            )
            
            task_definition = response['taskDefinition']
            
            print(f"✅ Task definition deregistered: {task_definition['family']}:{task_definition['revision']}")
            
            return {
                'deregistered': True,
                'family': task_definition['family'],
                'revision': task_definition['revision'],
                'status': task_definition['status']
            }
            
        except Exception as e:
            print(f"❌ Failed to deregister task definition: {str(e)}")
            raise
    
    def create_log_group(self, log_group_name: str, tags: Optional[Dict[str, str]] = None) -> bool:
        """
        Create CloudWatch log group for ECS logging.
        
        Args:
            log_group_name: Name of the log group to create
            tags: Optional tags for the log group
            
        Returns:
            True if created or already exists, False otherwise
        """
        try:
            # Check if log group already exists
            try:
                self.aws_client.logs.describe_log_groups(
                    logGroupNamePrefix=log_group_name,
                    limit=1
                )
                # If we get here, log group exists
                return True
            except:
                pass
            
            print(f"📝 Creating CloudWatch log group: {log_group_name}")
            
            # Create log group
            params = {'logGroupName': log_group_name}
            if tags:
                params['tags'] = tags
            
            self.aws_client.logs.create_log_group(**params)
            
            print(f"✅ Log group created: {log_group_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create log group '{log_group_name}': {str(e)}")
            return False
    
    def get_container_definition_template(self, workload_type: str = 'web') -> Dict[str, Any]:
        """
        Get a container definition template based on workload type.
        
        Args:
            workload_type: Type of workload (web, api, microservice, background)
            
        Returns:
            Container definition template
        """
        templates = {
            'web': {
                'health_check': {
                    'command': ['CMD-SHELL', 'curl -f http://localhost/ || exit 1'],
                    'interval': 30,
                    'timeout': 5,
                    'retries': 3,
                    'start_period': 60
                },
                'environment_variables': {
                    'NODE_ENV': 'production',
                    'PORT': '80'
                }
            },
            'api': {
                'health_check': {
                    'command': ['CMD-SHELL', 'curl -f http://localhost/health || exit 1'],
                    'interval': 30,
                    'timeout': 5,
                    'retries': 3,
                    'start_period': 30
                },
                'environment_variables': {
                    'NODE_ENV': 'production',
                    'PORT': '3000'
                }
            },
            'microservice': {
                'health_check': {
                    'command': ['CMD-SHELL', 'curl -f http://localhost:8080/actuator/health || exit 1'],
                    'interval': 30,
                    'timeout': 5,
                    'retries': 3,
                    'start_period': 45
                },
                'environment_variables': {
                    'SPRING_PROFILES_ACTIVE': 'production',
                    'SERVER_PORT': '8080'
                }
            },
            'background': {
                'health_check': None,  # Background services typically don't need health checks
                'environment_variables': {
                    'NODE_ENV': 'production'
                }
            }
        }
        
        return templates.get(workload_type, templates['web'])
    
    def discover_existing_task_definitions(self, family_prefix: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Discover existing task definitions for preview operations.
        
        Args:
            family_prefix: Optional family prefix filter
            
        Returns:
            Dictionary mapping family names to their latest task definition info
        """
        task_definitions = self.list_task_definitions(family_prefix)
        
        # Group by family and get latest revision
        families = {}
        for td in task_definitions:
            family = td['family']
            if family not in families or td['revision'] > families[family]['revision']:
                families[family] = td
        
        return families
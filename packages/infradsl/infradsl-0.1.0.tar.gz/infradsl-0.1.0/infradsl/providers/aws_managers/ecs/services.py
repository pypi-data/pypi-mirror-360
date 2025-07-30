"""
ECS Service Lifecycle Management

This module handles ECS service creation, updates, deletion, and network configuration.
"""

from typing import Dict, Any, List, Optional
import time


class EcsServiceManager:
    """
    ECS Service Lifecycle Management
    
    Handles:
    - Service creation, update, and deletion
    - Network configuration (Fargate/EC2)
    - Load balancer integration
    - Service discovery configuration
    """
    
    def __init__(self, aws_client):
        """Initialize the service manager with AWS client."""
        self.aws_client = aws_client
    
    def create_service(
        self,
        service_name: str,
        cluster_name: str,
        task_definition_arn: str,
        desired_count: int = 1,
        launch_type: str = 'FARGATE',
        network_configuration: Optional[Dict[str, Any]] = None,
        load_balancers: Optional[List[Dict[str, Any]]] = None,
        service_registries: Optional[List[Dict[str, Any]]] = None,
        platform_version: str = 'LATEST',
        placement_constraints: Optional[List[Dict[str, Any]]] = None,
        placement_strategy: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create ECS service.
        
        Args:
            service_name: Name of the service
            cluster_name: Name of the ECS cluster
            task_definition_arn: Task definition ARN
            desired_count: Number of tasks to run
            launch_type: FARGATE or EC2
            network_configuration: Network configuration for Fargate
            load_balancers: Load balancer configurations
            service_registries: Service discovery registries
            platform_version: Fargate platform version
            placement_constraints: Task placement constraints
            placement_strategy: Task placement strategy
            tags: Service tags
            
        Returns:
            Service creation result
        """
        try:
            print(f"🚢 Creating ECS service: {service_name}")
            
            # Build service configuration
            service_config = {
                'serviceName': service_name,
                'cluster': cluster_name,
                'taskDefinition': task_definition_arn,
                'desiredCount': desired_count,
                'launchType': launch_type,
                'enableExecuteCommand': True  # Enable ECS Exec for debugging
            }
            
            # Add Fargate-specific configuration
            if launch_type == 'FARGATE':
                service_config['platformVersion'] = platform_version
                
                # Network configuration is required for Fargate
                if network_configuration:
                    service_config['networkConfiguration'] = {
                        'awsvpcConfiguration': network_configuration
                    }
            
            # Add load balancers if provided
            if load_balancers:
                service_config['loadBalancers'] = load_balancers
            
            # Add service registries if provided
            if service_registries:
                service_config['serviceRegistries'] = service_registries
            
            # Add placement constraints for EC2
            if placement_constraints:
                service_config['placementConstraints'] = placement_constraints
            
            # Add placement strategy for EC2
            if placement_strategy:
                service_config['placementStrategy'] = placement_strategy
            
            # Add tags if provided
            if tags:
                service_config['tags'] = [
                    {'key': key, 'value': value}
                    for key, value in tags.items()
                ]
            
            # Create service
            response = self.aws_client.ecs.create_service(**service_config)
            service = response['service']
            
            print(f"✅ ECS service created: {service_name}")
            
            # Wait for service to stabilize
            self._wait_for_service_stable(cluster_name, service_name)
            
            return {
                'service_arn': service['serviceArn'],
                'service_name': service['serviceName'],
                'cluster_arn': service['clusterArn'],
                'status': service['status'],
                'running_count': service['runningCount'],
                'pending_count': service['pendingCount'],
                'desired_count': service['desiredCount']
            }
            
        except Exception as e:
            print(f"❌ Failed to create service '{service_name}': {str(e)}")
            raise
    
    def update_service(
        self,
        service_name: str,
        cluster_name: str,
        task_definition_arn: Optional[str] = None,
        desired_count: Optional[int] = None,
        network_configuration: Optional[Dict[str, Any]] = None,
        platform_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update ECS service.
        
        Args:
            service_name: Name of the service
            cluster_name: Name of the ECS cluster
            task_definition_arn: New task definition ARN
            desired_count: New desired count
            network_configuration: Updated network configuration
            platform_version: Updated platform version
            
        Returns:
            Service update result
        """
        try:
            print(f"🔄 Updating ECS service: {service_name}")
            
            # Build update configuration
            update_config = {
                'cluster': cluster_name,
                'service': service_name
            }
            
            # Add task definition if provided
            if task_definition_arn:
                update_config['taskDefinition'] = task_definition_arn
            
            # Add desired count if provided
            if desired_count is not None:
                update_config['desiredCount'] = desired_count
            
            # Add network configuration if provided
            if network_configuration:
                update_config['networkConfiguration'] = {
                    'awsvpcConfiguration': network_configuration
                }
            
            # Add platform version if provided
            if platform_version:
                update_config['platformVersion'] = platform_version
            
            # Update service
            response = self.aws_client.ecs.update_service(**update_config)
            service = response['service']
            
            print(f"✅ ECS service updated: {service_name}")
            
            # Wait for service to stabilize
            self._wait_for_service_stable(cluster_name, service_name)
            
            return {
                'service_arn': service['serviceArn'],
                'service_name': service['serviceName'],
                'status': service['status'],
                'running_count': service['runningCount'],
                'pending_count': service['pendingCount'],
                'desired_count': service['desiredCount']
            }
            
        except Exception as e:
            print(f"❌ Failed to update service '{service_name}': {str(e)}")
            raise
    
    def delete_service(self, service_name: str, cluster_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Delete ECS service.
        
        Args:
            service_name: Name of the service to delete
            cluster_name: Name of the ECS cluster
            force: Whether to force deletion
            
        Returns:
            Service deletion result
        """
        try:
            print(f"🗑️  Deleting ECS service: {service_name}")
            
            # First, scale down the service to 0
            if not force:
                print(f"📉 Scaling down service to 0 tasks...")
                self.update_service(service_name, cluster_name, desired_count=0)
            
            # Delete service
            response = self.aws_client.ecs.delete_service(
                cluster=cluster_name,
                service=service_name,
                force=force
            )
            
            service = response['service']
            
            print(f"✅ ECS service deleted: {service_name}")
            
            return {
                'deleted': True,
                'service_arn': service['serviceArn'],
                'service_name': service['serviceName'],
                'status': service['status']
            }
            
        except Exception as e:
            print(f"❌ Failed to delete service '{service_name}': {str(e)}")
            raise
    
    def get_service(self, service_name: str, cluster_name: str) -> Optional[Dict[str, Any]]:
        """
        Get service information.
        
        Args:
            service_name: Name of the service
            cluster_name: Name of the ECS cluster
            
        Returns:
            Service information or None if not found
        """
        try:
            response = self.aws_client.ecs.describe_services(
                cluster=cluster_name,
                services=[service_name]
            )
            
            services = response.get('services', [])
            if services and services[0]['status'] != 'INACTIVE':
                return services[0]
            
            return None
            
        except Exception:
            return None
    
    def list_services(self, cluster_name: str) -> List[Dict[str, Any]]:
        """
        List services in a cluster.
        
        Args:
            cluster_name: Name of the ECS cluster
            
        Returns:
            List of service information
        """
        try:
            # Get service ARNs
            response = self.aws_client.ecs.list_services(cluster=cluster_name)
            service_arns = response.get('serviceArns', [])
            
            if not service_arns:
                return []
            
            # Get detailed service information
            response = self.aws_client.ecs.describe_services(
                cluster=cluster_name,
                services=service_arns
            )
            
            services = []
            for service in response.get('services', []):
                if service['status'] != 'INACTIVE':
                    services.append({
                        'name': service['serviceName'],
                        'arn': service['serviceArn'],
                        'cluster': service['clusterArn'],
                        'status': service['status'],
                        'task_definition': service['taskDefinition'],
                        'desired_count': service['desiredCount'],
                        'running_count': service['runningCount'],
                        'pending_count': service['pendingCount'],
                        'launch_type': service.get('launchType'),
                        'platform_version': service.get('platformVersion'),
                        'created_at': service.get('createdAt'),
                        'load_balancers': service.get('loadBalancers', []),
                        'service_registries': service.get('serviceRegistries', [])
                    })
            
            return services
            
        except Exception as e:
            print(f"❌ Failed to list services: {str(e)}")
            return []
    
    def get_service_status(self, service_name: str, cluster_name: str) -> Dict[str, Any]:
        """
        Get detailed service status.
        
        Args:
            service_name: Name of the service
            cluster_name: Name of the ECS cluster
            
        Returns:
            Service status information
        """
        service = self.get_service(service_name, cluster_name)
        if not service:
            return {'exists': False}
        
        return {
            'exists': True,
            'name': service['serviceName'],
            'arn': service['serviceArn'],
            'status': service['status'],
            'task_definition': service['taskDefinition'],
            'desired_count': service['desiredCount'],
            'running_count': service['runningCount'],
            'pending_count': service['pendingCount'],
            'launch_type': service.get('launchType'),
            'platform_version': service.get('platformVersion'),
            'created_at': service.get('createdAt'),
            'deployments': service.get('deployments', []),
            'events': service.get('events', [])[-5:],  # Last 5 events
            'load_balancers': len(service.get('loadBalancers', [])),
            'service_registries': len(service.get('serviceRegistries', []))
        }
    
    def build_network_configuration(
        self,
        subnets: List[str],
        security_groups: List[str],
        assign_public_ip: bool = True
    ) -> Dict[str, Any]:
        """
        Build network configuration for Fargate services.
        
        Args:
            subnets: List of subnet IDs
            security_groups: List of security group IDs
            assign_public_ip: Whether to assign public IP
            
        Returns:
            Network configuration
        """
        return {
            'subnets': subnets,
            'securityGroups': security_groups,
            'assignPublicIp': 'ENABLED' if assign_public_ip else 'DISABLED'
        }
    
    def build_load_balancer_configuration(
        self,
        target_group_arn: str,
        container_name: str,
        container_port: int
    ) -> Dict[str, Any]:
        """
        Build load balancer configuration.
        
        Args:
            target_group_arn: Target group ARN
            container_name: Container name
            container_port: Container port
            
        Returns:
            Load balancer configuration
        """
        return {
            'targetGroupArn': target_group_arn,
            'containerName': container_name,
            'containerPort': container_port
        }
    
    def _wait_for_service_stable(self, cluster_name: str, service_name: str, timeout: int = 600):
        """Wait for service to become stable."""
        print(f"⏳ Waiting for service to become stable...")
        
        try:
            waiter = self.aws_client.ecs.get_waiter('services_stable')
            waiter.wait(
                cluster=cluster_name,
                services=[service_name],
                WaiterConfig={'delay': 15, 'maxAttempts': timeout // 15}
            )
            print(f"✅ Service is stable")
        except Exception as e:
            print(f"⚠️  Service may not be fully stable: {str(e)}")
    
    def discover_existing_services(self, cluster_name: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Discover existing services for preview operations.
        
        Args:
            cluster_name: Optional cluster name filter
            
        Returns:
            Dictionary mapping service names to their information
        """
        services = {}
        
        if cluster_name:
            # Get services from specific cluster
            cluster_services = self.list_services(cluster_name)
            for service in cluster_services:
                services[service['name']] = service
        else:
            # Get services from all clusters (would need cluster discovery)
            # For now, just return empty dict if no cluster specified
            pass
        
        return services
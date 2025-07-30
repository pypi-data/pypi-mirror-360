"""
ECS Manager - Main Orchestrator

This module coordinates all ECS operations by delegating to specialized managers.
"""

from typing import Dict, Any, List, Optional
from .clusters import EcsClusterManager
from .task_definitions import EcsTaskDefinitionManager
from .services import EcsServiceManager
from .monitoring import EcsMonitoringManager
from .configuration import EcsConfigurationManager


class EcsManager:
    """
    ECS Manager - Main Orchestrator
    
    Coordinates all ECS operations by delegating to specialized managers:
    - ClusterManager: Cluster operations
    - TaskDefinitionManager: Task definition operations
    - ServiceManager: Service lifecycle management
    - MonitoringManager: Monitoring, scaling, and logging
    - ConfigurationManager: DSL methods and configuration
    """
    
    def __init__(self, aws_client, ecs_service):
        """
        Initialize ECS manager with AWS client and service instance.
        
        Args:
            aws_client: Authenticated AWS client
            ecs_service: Reference to the ECS service instance
        """
        self.aws_client = aws_client
        self.service = ecs_service
        
        # Initialize specialized managers
        self.cluster_manager = EcsClusterManager(aws_client)
        self.task_definition_manager = EcsTaskDefinitionManager(aws_client)
        self.service_manager = EcsServiceManager(aws_client)
        self.monitoring_manager = EcsMonitoringManager(aws_client)
        self.configuration_manager = EcsConfigurationManager(ecs_service)
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, updated, or removed."""
        print(f"\n🚢 AWS ECS Service Configuration Preview")
        
        # Discover existing resources
        existing_clusters = self.cluster_manager.discover_existing_clusters()
        existing_services = self.service_manager.discover_existing_services(self.service.cluster_name)
        existing_task_defs = self.task_definition_manager.discover_existing_task_definitions(
            self.service.task_definition_family
        )
        
        # Determine what will happen
        cluster_exists = self.service.cluster_name in existing_clusters
        service_exists = self.service.name in existing_services
        task_def_exists = self.service.task_definition_family in existing_task_defs
        
        to_create = []
        to_keep = []
        to_remove = []
        
        if not cluster_exists:
            to_create.append(f"Cluster: {self.service.cluster_name}")
        else:
            to_keep.append(f"Cluster: {self.service.cluster_name}")
        
        if not task_def_exists:
            to_create.append(f"Task Definition: {self.service.task_definition_family}")
        else:
            to_create.append(f"Task Definition: {self.service.task_definition_family} (new revision)")
        
        if not service_exists:
            to_create.append(f"Service: {self.service.name}")
        else:
            to_create.append(f"Service: {self.service.name} (update)")
        
        # Show what will be created/updated
        if to_create:
            print(f"╭─ 🚢 ECS Resources to CREATE/UPDATE: {len(to_create)}")
            for item in to_create:
                print(f"│  ├─ 🆕 {item}")
            
            print(f"│  ├─ 🐳 Image: {self.service.image or 'Container Magic (auto-build)'}")
            print(f"│  ├─ 💻 CPU: {self.service.cpu} units")
            print(f"│  ├─ 💾 Memory: {self.service.memory} MB")
            print(f"│  ├─ 🌐 Port: {self.service.port}")
            print(f"│  ├─ 📊 Desired Tasks: {self.service.desired_count}")
            print(f"│  ├─ 🚀 Launch Type: {self.service.launch_type}")
            
            if self.service.launch_type == 'FARGATE':
                public_status = "Enabled" if self.service.public_ip else "Disabled"
                print(f"│  ├─ 🌍 Public Access: {public_status}")
            
            if self.service.environment_variables:
                print(f"│  ├─ 🔧 Environment Variables: {len(self.service.environment_variables)}")
            
            if self.service.health_check:
                print(f"│  ├─ ❤️  Health Checks: Enabled")
            
            if self.service.auto_scaling:
                min_cap = self.service.auto_scaling.get('min_capacity', 1)
                max_cap = self.service.auto_scaling.get('max_capacity', 10)
                target_cpu = self.service.auto_scaling.get('target_cpu_utilization', 70)
                print(f"│  ├─ 📈 Auto Scaling: {min_cap}-{max_cap} tasks ({target_cpu}% CPU)")
            
            if self.service.container_magic_enabled:
                print(f"│  ├─ ✨ Container Magic: Enabled")
                if self.service.auto_build_enabled:
                    print(f"│  ├─ 🔨 Auto Build: Enabled")
            
            print(f"│  ├─ 🏷️  Tags: {len(self._get_all_tags())}")
            print(f"│  └─ 🐳 Container Orchestration: Full ECS API")
        
        if not to_create and not to_remove:
            print(f"├─ ✨ No changes needed - infrastructure matches configuration")
        
        print(f"╰─")
        
        # Cost estimation
        if to_create:
            print(f"\n💰 Estimated Monthly Costs:")
            cost_estimate = self.monitoring_manager.estimate_monthly_cost(
                cpu=self.service.cpu,
                memory=self.service.memory,
                desired_count=self.service.desired_count,
                launch_type=self.service.launch_type,
                auto_scaling=self.service.auto_scaling
            )
            
            if cost_estimate['launch_type'] == 'FARGATE':
                estimated_cost = cost_estimate.get('estimated_monthly_cost', 0)
                print(f"   ├─ 🚀 Fargate Compute: ${estimated_cost:.2f}")
                print(f"   ├─ 💰 No EC2 Management: Serverless pricing")
                
                if self.service.auto_scaling:
                    min_cost = cost_estimate.get('min_monthly_cost', 0)
                    max_cost = cost_estimate.get('max_monthly_cost', 0)
                    print(f"   ├─ 📈 Auto Scaling Range: ${min_cost:.2f} - ${max_cost:.2f}")
                
                if self.service.public_ip:
                    print(f"   ├─ 🌍 NAT Gateway: ~$32.40/month (if using private subnets)")
                
                print(f"   ├─ 📊 CloudWatch Logs: ~$0.50/GB (first 5GB free)")
                print(f"   └─ 🎯 AWS Free Tier: Some services included")
            else:
                print(f"   ├─ 💻 EC2 Launch Type: Depends on underlying EC2 instances")
                print(f"   ├─ 🏗️  ECS Service: No additional charge")
                print(f"   └─ 💰 Cost: Based on your EC2 instance pricing")
        
        print(f"\n✅ Preview completed - no resources were created.")
        
        return {
            'resource_type': 'aws_ecs_service',
            'name': self.service.name,
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'existing_clusters': existing_clusters,
            'existing_services': existing_services,
            'existing_task_definitions': existing_task_defs,
            'estimated_cost': cost_estimate,
            'configuration': self.configuration_manager.get_configuration_summary()
        }
    
    def create(self) -> Dict[str, Any]:
        """Create/update ECS service and all required resources."""
        if not self.service.image and not self.service.container_magic_enabled:
            raise ValueError("Container image is required unless Container Magic is enabled")
        
        print(f"\n🚢 Creating/updating ECS service: {self.service.name}")
        
        try:
            # Step 1: Ensure cluster exists
            cluster_result = self.cluster_manager.create_cluster(
                cluster_name=self.service.cluster_name,
                tags=self._get_all_tags()
            )
            self.service.cluster_arn = cluster_result['cluster_arn']
            
            # Step 2: Create log group if logging is enabled
            if self.service.enable_logging and self.service.log_group:
                self.task_definition_manager.create_log_group(
                    self.service.log_group,
                    tags=self._get_all_tags()
                )
            
            # Step 3: Build container definition
            container_def = self.task_definition_manager.build_container_definition(
                name=self.service.name,
                image=self.service.image,
                port=self.service.port,
                environment_variables=self.service.environment_variables,
                secrets=self.service.secrets,
                health_check=self.service.health_check,
                log_group=self.service.log_group if self.service.enable_logging else None
            )
            
            # Step 4: Register task definition
            task_def_result = self.task_definition_manager.register_task_definition(
                family=self.service.task_definition_family,
                container_definitions=[container_def],
                cpu=self.service.cpu,
                memory=self.service.memory,
                network_mode=self.service.network_mode,
                requires_compatibilities=[self.service.launch_type],
                execution_role_arn=self.service.execution_role_arn,
                task_role_arn=self.service.task_role_arn,
                tags=self._get_all_tags()
            )
            self.service.task_definition_arn = task_def_result['task_definition_arn']
            
            # Step 5: Prepare service configuration
            service_config = {
                'service_name': self.service.name,
                'cluster_name': self.service.cluster_name,
                'task_definition_arn': self.service.task_definition_arn,
                'desired_count': self.service.desired_count,
                'launch_type': self.service.launch_type,
                'platform_version': self.service.platform_version,
                'tags': self._get_all_tags()
            }
            
            # Add network configuration for Fargate
            if self.service.launch_type == 'FARGATE':
                service_config['network_configuration'] = self.service_manager.build_network_configuration(
                    subnets=self.service.subnets,
                    security_groups=self.service.security_groups,
                    assign_public_ip=self.service.public_ip
                )
            
            # Add load balancer configuration if specified
            if self.service.load_balancer:
                service_config['load_balancers'] = [
                    self.service_manager.build_load_balancer_configuration(
                        target_group_arn=self.service.load_balancer['target_group_arn'],
                        container_name=self.service.name,
                        container_port=self.service.port
                    )
                ]
            
            # Step 6: Create or update service
            existing_service = self.service_manager.get_service(self.service.name, self.service.cluster_name)
            
            if existing_service:
                print(f"🔄 Updating existing service...")
                service_result = self.service_manager.update_service(
                    service_name=self.service.name,
                    cluster_name=self.service.cluster_name,
                    task_definition_arn=self.service.task_definition_arn,
                    desired_count=self.service.desired_count,
                    network_configuration=service_config.get('network_configuration')
                )
            else:
                print(f"🆕 Creating new service...")
                service_result = self.service_manager.create_service(**service_config)
            
            self.service.service_arn = service_result['service_arn']
            self.service.service_status = service_result['status']
            self.service.running_count = service_result['running_count']
            self.service.pending_count = service_result['pending_count']
            
            # Step 7: Configure auto-scaling if specified
            if self.service.auto_scaling:
                self.monitoring_manager.configure_auto_scaling(
                    service_name=self.service.name,
                    cluster_name=self.service.cluster_name,
                    min_capacity=self.service.auto_scaling['min_capacity'],
                    max_capacity=self.service.auto_scaling['max_capacity'],
                    target_cpu_utilization=self.service.auto_scaling['target_cpu_utilization'],
                    target_memory_utilization=self.service.auto_scaling.get('target_memory_utilization'),
                    scale_out_cooldown=self.service.auto_scaling.get('scale_out_cooldown', 300),
                    scale_in_cooldown=self.service.auto_scaling.get('scale_in_cooldown', 300)
                )
            
            print(f"\n✅ ECS service deployment completed successfully!")
            print(f"   ├─ Service ARN: {self.service.service_arn}")
            print(f"   ├─ Cluster: {self.service.cluster_name}")
            print(f"   ├─ Status: {self.service.service_status}")
            print(f"   └─ Running Tasks: {self.service.running_count}/{self.service.desired_count}")
            
            return {
                'success': True,
                'service_arn': self.service.service_arn,
                'cluster_arn': self.service.cluster_arn,
                'task_definition_arn': self.service.task_definition_arn,
                'status': self.service.service_status,
                'running_count': self.service.running_count,
                'pending_count': self.service.pending_count,
                'desired_count': self.service.desired_count
            }
            
        except Exception as e:
            print(f"❌ Failed to create ECS service: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy ECS service and optionally clean up related resources."""
        print(f"\n🗑️  Destroying ECS service: {self.service.name}")
        
        try:
            results = {'deleted_resources': []}
            
            # Step 1: Delete the service
            try:
                service_result = self.service_manager.delete_service(
                    service_name=self.service.name,
                    cluster_name=self.service.cluster_name
                )
                if service_result['deleted']:
                    results['deleted_resources'].append(f"Service: {self.service.name}")
            except Exception as e:
                print(f"⚠️  Service deletion failed or service not found: {str(e)}")
            
            # Step 2: Deregister task definitions (optional - keep for rollback)
            # In production, you might want to keep task definitions for rollback
            
            # Step 3: Check if cluster should be deleted (if empty)
            cluster_services = self.service_manager.list_services(self.service.cluster_name)
            active_services = [s for s in cluster_services if s['status'] == 'ACTIVE']
            
            if not active_services:
                try:
                    cluster_result = self.cluster_manager.delete_cluster(self.service.cluster_name)
                    if cluster_result['deleted']:
                        results['deleted_resources'].append(f"Cluster: {self.service.cluster_name}")
                except Exception as e:
                    print(f"⚠️  Cluster deletion failed: {str(e)}")
            else:
                print(f"🔒 Cluster retained: {len(active_services)} other active services")
            
            print(f"\n✅ ECS service destruction completed!")
            if results['deleted_resources']:
                print(f"   └─ Deleted: {', '.join(results['deleted_resources'])}")
            
            return {'success': True, **results}
            
        except Exception as e:
            print(f"❌ Failed to destroy ECS service: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def status(self) -> Dict[str, Any]:
        """Get comprehensive status of the ECS service."""
        return {
            'cluster_status': self.cluster_manager.get_cluster_status(self.service.cluster_name),
            'service_status': self.service_manager.get_service_status(self.service.name, self.service.cluster_name),
            'service_health': self.monitoring_manager.get_service_health(self.service.name, self.service.cluster_name),
            'auto_scaling_status': self.monitoring_manager.get_auto_scaling_status(self.service.name, self.service.cluster_name)
        }
    
    def logs(self, start_time: Optional[str] = None, end_time: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs from the service."""
        if not self.service.log_group:
            return []
        
        return self.monitoring_manager.get_service_logs(
            log_group=self.service.log_group,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
    
    def scale(self, desired_count: int) -> Dict[str, Any]:
        """Scale the service to a specific number of tasks."""
        return self.monitoring_manager.scale_service(
            service_name=self.service.name,
            cluster_name=self.service.cluster_name,
            desired_count=desired_count
        )
    
    def _get_all_tags(self) -> Dict[str, str]:
        """Get all tags including service tags and defaults."""
        tags = {
            'ManagedBy': 'InfraDSL',
            'Service': self.service.name,
            'Cluster': self.service.cluster_name
        }
        tags.update(self.service.service_tags)
        return tags
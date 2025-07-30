"""
ECS Monitoring and Operations

This module handles ECS service monitoring, auto-scaling, logging, and operational tasks.
"""

from typing import Dict, Any, List, Optional
import time
import json


class EcsMonitoringManager:
    """
    ECS Monitoring and Operations
    
    Handles:
    - Service status and health monitoring
    - Auto-scaling configuration and management
    - Log retrieval and monitoring
    - Cost estimation and resource tracking
    """
    
    def __init__(self, aws_client):
        """Initialize the monitoring manager with AWS client."""
        self.aws_client = aws_client
    
    def configure_auto_scaling(
        self,
        service_name: str,
        cluster_name: str,
        min_capacity: int = 1,
        max_capacity: int = 10,
        target_cpu_utilization: int = 70,
        target_memory_utilization: Optional[int] = None,
        scale_out_cooldown: int = 300,
        scale_in_cooldown: int = 300
    ) -> Dict[str, Any]:
        """
        Configure auto-scaling for ECS service.
        
        Args:
            service_name: Name of the ECS service
            cluster_name: Name of the ECS cluster
            min_capacity: Minimum number of tasks
            max_capacity: Maximum number of tasks
            target_cpu_utilization: Target CPU utilization percentage
            target_memory_utilization: Target memory utilization percentage
            scale_out_cooldown: Scale out cooldown in seconds
            scale_in_cooldown: Scale in cooldown in seconds
            
        Returns:
            Auto-scaling configuration result
        """
        try:
            print(f"📈 Configuring auto-scaling for service: {service_name}")
            
            # Resource ID for ECS service
            resource_id = f"service/{cluster_name}/{service_name}"
            
            # Register scalable target
            self.aws_client.application_autoscaling.register_scalable_target(
                ServiceNamespace='ecs',
                ResourceId=resource_id,
                ScalableDimension='ecs:service:DesiredCount',
                MinCapacity=min_capacity,
                MaxCapacity=max_capacity
            )
            
            policies_created = []
            
            # Create CPU-based scaling policy
            if target_cpu_utilization:
                cpu_policy_name = f"{service_name}-cpu-scaling"
                
                self.aws_client.application_autoscaling.put_scaling_policy(
                    PolicyName=cpu_policy_name,
                    ServiceNamespace='ecs',
                    ResourceId=resource_id,
                    ScalableDimension='ecs:service:DesiredCount',
                    PolicyType='TargetTrackingScaling',
                    TargetTrackingScalingPolicyConfiguration={
                        'TargetValue': target_cpu_utilization,
                        'PredefinedMetricSpecification': {
                            'PredefinedMetricType': 'ECSServiceAverageCPUUtilization'
                        },
                        'ScaleOutCooldown': scale_out_cooldown,
                        'ScaleInCooldown': scale_in_cooldown
                    }
                )
                policies_created.append(f"CPU scaling (target: {target_cpu_utilization}%)")
            
            # Create memory-based scaling policy
            if target_memory_utilization:
                memory_policy_name = f"{service_name}-memory-scaling"
                
                self.aws_client.application_autoscaling.put_scaling_policy(
                    PolicyName=memory_policy_name,
                    ServiceNamespace='ecs',
                    ResourceId=resource_id,
                    ScalableDimension='ecs:service:DesiredCount',
                    PolicyType='TargetTrackingScaling',
                    TargetTrackingScalingPolicyConfiguration={
                        'TargetValue': target_memory_utilization,
                        'PredefinedMetricSpecification': {
                            'PredefinedMetricType': 'ECSServiceAverageMemoryUtilization'
                        },
                        'ScaleOutCooldown': scale_out_cooldown,
                        'ScaleInCooldown': scale_in_cooldown
                    }
                )
                policies_created.append(f"Memory scaling (target: {target_memory_utilization}%)")
            
            print(f"✅ Auto-scaling configured: {', '.join(policies_created)}")
            
            return {
                'configured': True,
                'resource_id': resource_id,
                'min_capacity': min_capacity,
                'max_capacity': max_capacity,
                'policies': policies_created
            }
            
        except Exception as e:
            print(f"❌ Failed to configure auto-scaling: {str(e)}")
            raise
    
    def get_service_metrics(
        self,
        service_name: str,
        cluster_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get CloudWatch metrics for ECS service.
        
        Args:
            service_name: Name of the ECS service
            cluster_name: Name of the ECS cluster
            start_time: Start time for metrics (defaults to last hour)
            end_time: End time for metrics (defaults to now)
            
        Returns:
            Service metrics data
        """
        try:
            from datetime import datetime, timedelta
            
            # Default time range: last hour
            if not end_time:
                end_time = datetime.utcnow()
            else:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            if not start_time:
                start_time = end_time - timedelta(hours=1)
            else:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
            # Get CPU utilization
            cpu_response = self.aws_client.cloudwatch.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='CPUUtilization',
                Dimensions=[
                    {'Name': 'ServiceName', 'Value': service_name},
                    {'Name': 'ClusterName', 'Value': cluster_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5-minute intervals
                Statistics=['Average', 'Maximum']
            )
            
            # Get memory utilization
            memory_response = self.aws_client.cloudwatch.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='MemoryUtilization',
                Dimensions=[
                    {'Name': 'ServiceName', 'Value': service_name},
                    {'Name': 'ClusterName', 'Value': cluster_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5-minute intervals
                Statistics=['Average', 'Maximum']
            )
            
            # Get task count
            task_count_response = self.aws_client.cloudwatch.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='RunningTaskCount',
                Dimensions=[
                    {'Name': 'ServiceName', 'Value': service_name},
                    {'Name': 'ClusterName', 'Value': cluster_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5-minute intervals
                Statistics=['Average']
            )
            
            return {
                'service_name': service_name,
                'cluster_name': cluster_name,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'cpu_utilization': cpu_response.get('Datapoints', []),
                'memory_utilization': memory_response.get('Datapoints', []),
                'task_count': task_count_response.get('Datapoints', [])
            }
            
        except Exception as e:
            print(f"❌ Failed to get service metrics: {str(e)}")
            return {}
    
    def get_service_logs(
        self,
        log_group: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent logs from CloudWatch for the service.
        
        Args:
            log_group: CloudWatch log group name
            start_time: Start time for logs
            end_time: End time for logs
            limit: Maximum number of log events to return
            
        Returns:
            List of log events
        """
        try:
            from datetime import datetime, timedelta
            
            # Default time range: last hour
            kwargs = {
                'logGroupName': log_group,
                'limit': limit,
                'startFromHead': False  # Get most recent logs first
            }
            
            if start_time:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                kwargs['startTime'] = int(start_dt.timestamp() * 1000)
            else:
                # Default to last hour
                start_dt = datetime.utcnow() - timedelta(hours=1)
                kwargs['startTime'] = int(start_dt.timestamp() * 1000)
            
            if end_time:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                kwargs['endTime'] = int(end_dt.timestamp() * 1000)
            
            response = self.aws_client.logs.filter_log_events(**kwargs)
            
            logs = []
            for event in response.get('events', []):
                logs.append({
                    'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000).isoformat(),
                    'message': event['message'].strip(),
                    'log_stream': event['logStreamName']
                })
            
            return logs
            
        except Exception as e:
            print(f"❌ Failed to get service logs: {str(e)}")
            return []
    
    def scale_service(
        self,
        service_name: str,
        cluster_name: str,
        desired_count: int
    ) -> Dict[str, Any]:
        """
        Manually scale ECS service.
        
        Args:
            service_name: Name of the ECS service
            cluster_name: Name of the ECS cluster
            desired_count: New desired task count
            
        Returns:
            Scaling result
        """
        try:
            print(f"📊 Scaling service '{service_name}' to {desired_count} tasks")
            
            response = self.aws_client.ecs.update_service(
                cluster=cluster_name,
                service=service_name,
                desiredCount=desired_count
            )
            
            service = response['service']
            
            print(f"✅ Service scaled to {desired_count} tasks")
            
            return {
                'scaled': True,
                'service_name': service['serviceName'],
                'previous_count': service.get('previousDesiredCount', 'unknown'),
                'new_count': service['desiredCount'],
                'running_count': service['runningCount'],
                'pending_count': service['pendingCount']
            }
            
        except Exception as e:
            print(f"❌ Failed to scale service: {str(e)}")
            raise
    
    def get_service_health(self, service_name: str, cluster_name: str) -> Dict[str, Any]:
        """
        Get comprehensive service health information.
        
        Args:
            service_name: Name of the ECS service
            cluster_name: Name of the ECS cluster
            
        Returns:
            Service health status
        """
        try:
            # Get service details
            response = self.aws_client.ecs.describe_services(
                cluster=cluster_name,
                services=[service_name]
            )
            
            services = response.get('services', [])
            if not services:
                return {'healthy': False, 'reason': 'Service not found'}
            
            service = services[0]
            
            # Check service status
            if service['status'] != 'ACTIVE':
                return {
                    'healthy': False,
                    'reason': f"Service status is {service['status']}"
                }
            
            # Check task counts
            desired = service['desiredCount']
            running = service['runningCount']
            pending = service['pendingCount']
            
            # Service is healthy if running count matches desired count
            healthy = (running == desired and pending == 0)
            
            # Get recent events for additional context
            events = service.get('events', [])[:3]  # Last 3 events
            
            # Check deployment status
            deployments = service.get('deployments', [])
            primary_deployment = next((d for d in deployments if d['status'] == 'PRIMARY'), None)
            
            deployment_healthy = True
            if primary_deployment:
                deployment_healthy = (
                    primary_deployment['runningCount'] == primary_deployment['desiredCount']
                )
            
            return {
                'healthy': healthy and deployment_healthy,
                'service_status': service['status'],
                'desired_count': desired,
                'running_count': running,
                'pending_count': pending,
                'deployment_status': primary_deployment['status'] if primary_deployment else 'UNKNOWN',
                'recent_events': [
                    {
                        'message': event['message'],
                        'created_at': event['createdAt'].isoformat() if 'createdAt' in event else None
                    }
                    for event in events
                ],
                'last_updated': service.get('updatedAt', '').isoformat() if service.get('updatedAt') else None
            }
            
        except Exception as e:
            print(f"❌ Failed to get service health: {str(e)}")
            return {'healthy': False, 'reason': f'Error: {str(e)}'}
    
    def estimate_monthly_cost(
        self,
        cpu: str,
        memory: str,
        desired_count: int = 1,
        launch_type: str = 'FARGATE',
        auto_scaling: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate monthly cost for ECS service.
        
        Args:
            cpu: CPU units
            memory: Memory in MB
            desired_count: Number of tasks
            launch_type: FARGATE or EC2
            auto_scaling: Auto-scaling configuration
            
        Returns:
            Cost estimation breakdown
        """
        if launch_type == 'FARGATE':
            # Fargate pricing (approximate, varies by region)
            cpu_cost_per_hour = int(cpu) * 0.00001251  # Per vCPU per hour
            memory_cost_per_hour = int(memory) * 0.00000137  # Per GB per hour
            
            hours_per_month = 24 * 30
            
            base_cost = (cpu_cost_per_hour + memory_cost_per_hour) * hours_per_month * desired_count
            
            cost_breakdown = {
                'launch_type': 'FARGATE',
                'cpu_cost': cpu_cost_per_hour * hours_per_month * desired_count,
                'memory_cost': memory_cost_per_hour * hours_per_month * desired_count,
                'base_monthly_cost': base_cost
            }
            
            if auto_scaling:
                min_cap = auto_scaling.get('min_capacity', desired_count)
                max_cap = auto_scaling.get('max_capacity', desired_count * 2)
                
                min_cost = (cpu_cost_per_hour + memory_cost_per_hour) * hours_per_month * min_cap
                max_cost = (cpu_cost_per_hour + memory_cost_per_hour) * hours_per_month * max_cap
                
                cost_breakdown.update({
                    'auto_scaling': True,
                    'min_monthly_cost': min_cost,
                    'max_monthly_cost': max_cost,
                    'estimated_monthly_cost': (min_cost + base_cost) / 2  # Average estimate
                })
            else:
                cost_breakdown['estimated_monthly_cost'] = base_cost
            
            return cost_breakdown
        
        else:  # EC2
            return {
                'launch_type': 'EC2',
                'note': 'Cost depends on underlying EC2 instances',
                'ecs_service_cost': 0,  # No additional charge for ECS service
                'estimated_monthly_cost': 'Variable based on EC2 pricing'
            }
    
    def get_auto_scaling_status(self, service_name: str, cluster_name: str) -> Dict[str, Any]:
        """
        Get auto-scaling status for a service.
        
        Args:
            service_name: Name of the ECS service
            cluster_name: Name of the ECS cluster
            
        Returns:
            Auto-scaling status information
        """
        try:
            resource_id = f"service/{cluster_name}/{service_name}"
            
            # Get scalable targets
            response = self.aws_client.application_autoscaling.describe_scalable_targets(
                ServiceNamespace='ecs',
                ResourceIds=[resource_id]
            )
            
            targets = response.get('ScalableTargets', [])
            if not targets:
                return {'configured': False}
            
            target = targets[0]
            
            # Get scaling policies
            policies_response = self.aws_client.application_autoscaling.describe_scaling_policies(
                ServiceNamespace='ecs',
                ResourceId=resource_id
            )
            
            policies = policies_response.get('ScalingPolicies', [])
            
            return {
                'configured': True,
                'min_capacity': target['MinCapacity'],
                'max_capacity': target['MaxCapacity'],
                'current_capacity': target.get('CurrentCapacity', 'unknown'),
                'policies': [
                    {
                        'name': policy['PolicyName'],
                        'type': policy['PolicyType'],
                        'target_value': policy.get('TargetTrackingScalingPolicyConfiguration', {}).get('TargetValue'),
                        'metric_type': policy.get('TargetTrackingScalingPolicyConfiguration', {}).get('PredefinedMetricSpecification', {}).get('PredefinedMetricType')
                    }
                    for policy in policies
                ]
            }
            
        except Exception as e:
            print(f"❌ Failed to get auto-scaling status: {str(e)}")
            return {'configured': False, 'error': str(e)}
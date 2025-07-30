"""
EC2 Stateless Intelligence Implementation

Smart resource fingerprinting and predictive change impact analysis for EC2 instances.
Extends the AWS intelligence base with EC2-specific capabilities.
"""

import boto3
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

from .aws_intelligence_base import AWSIntelligenceBase
from .stateless_intelligence import (
    ResourceType,
    ChangeImpact,
    ChangeImpactAnalysis,
    ResourceHealth
)


class EC2Intelligence(AWSIntelligenceBase):
    """EC2-specific stateless intelligence implementation"""
    
    def __init__(self):
        super().__init__(ResourceType.EC2_INSTANCE)
        self.ec2_client = None
        self.ec2_resource = None
    
    def _get_ec2_client(self):
        """Get EC2 client with error handling"""
        if not self.ec2_client:
            try:
                self.ec2_client = boto3.client('ec2')
                self.ec2_resource = boto3.resource('ec2')
            except (NoCredentialsError, Exception) as e:
                print(f"⚠️  Failed to create EC2 client: {e}")
                return None
        return self.ec2_client
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing EC2 instances"""
        existing_instances = {}
        
        client = self._get_ec2_client()
        if not client:
            return existing_instances
        
        try:
            # Get all instances (including terminated ones for completeness)
            paginator = client.get_paginator('describe_instances')
            
            for page in paginator.paginate():
                for reservation in page.get('Reservations', []):
                    for instance in reservation.get('Instances', []):
                        instance_id = instance['InstanceId']
                        
                        try:
                            instance_data = self._extract_instance_data(instance)
                            existing_instances[instance_id] = instance_data
                            
                        except Exception as e:
                            print(f"⚠️  Failed to extract data for instance {instance_id}: {str(e)}")
                            existing_instances[instance_id] = {
                                'instance_id': instance_id,
                                'state': instance.get('State', {}).get('Name', 'unknown'),
                                'error': str(e)
                            }
        
        except Exception as e:
            print(f"⚠️  Failed to discover EC2 instances: {str(e)}")
        
        return existing_instances
    
    def _extract_instance_data(self, instance: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive instance data"""
        
        # Extract tags
        tags = {}
        for tag in instance.get('Tags', []):
            tags[tag['Key']] = tag['Value']
        
        instance_data = {
            'instance_id': instance['InstanceId'],
            'instance_type': instance.get('InstanceType'),
            'state': instance.get('State', {}).get('Name'),
            'availability_zone': instance.get('Placement', {}).get('AvailabilityZone'),
            'subnet_id': instance.get('SubnetId'),
            'vpc_id': instance.get('VpcId'),
            'private_ip': instance.get('PrivateIpAddress'),
            'public_ip': instance.get('PublicIpAddress'),
            'image_id': instance.get('ImageId'),
            'key_name': instance.get('KeyName'),
            'launch_time': instance.get('LaunchTime'),
            'platform': instance.get('Platform', 'linux'),
            'architecture': instance.get('Architecture'),
            'root_device_type': instance.get('RootDeviceType'),
            'hypervisor': instance.get('Hypervisor'),
            'tags': tags,
            'name': tags.get('Name', ''),
            'security_groups': [sg['GroupId'] for sg in instance.get('SecurityGroups', [])],
            'network_interfaces': instance.get('NetworkInterfaces', []),
            'block_device_mappings': instance.get('BlockDeviceMappings', []),
            'iam_instance_profile': instance.get('IamInstanceProfile', {}),
            'monitoring': instance.get('Monitoring', {}).get('State'),
            'termination_protection': False  # Would need separate API call
        }
        
        return instance_data
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from EC2 instance state"""
        return {
            'instance_id': cloud_state.get('instance_id'),
            'instance_type': cloud_state.get('instance_type'),
            'image_id': cloud_state.get('image_id'),
            'key_name': cloud_state.get('key_name'),
            'availability_zone': cloud_state.get('availability_zone'),
            'subnet_id': cloud_state.get('subnet_id'),
            'vpc_id': cloud_state.get('vpc_id'),
            'security_groups': cloud_state.get('security_groups', []),
            'monitoring_enabled': cloud_state.get('monitoring') == 'enabled',
            'root_device_type': cloud_state.get('root_device_type'),
            'platform': cloud_state.get('platform'),
            'tags': cloud_state.get('tags', {})
        }
    
    def _generate_service_specific_fingerprint_data(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate EC2-specific fingerprint data"""
        fingerprint_data = {}
        
        # Instance sizing pattern
        instance_type = cloud_state.get('instance_type', '')
        if instance_type:
            fingerprint_data['sizing_pattern'] = {
                'family': instance_type.split('.')[0] if '.' in instance_type else '',
                'size': instance_type.split('.')[1] if '.' in instance_type else '',
                'is_burstable': instance_type.startswith(('t2', 't3', 't4g')),
                'is_compute_optimized': instance_type.startswith(('c4', 'c5', 'c6')),
                'is_memory_optimized': instance_type.startswith(('r4', 'r5', 'r6', 'x1')),
                'is_storage_optimized': instance_type.startswith(('i3', 'd2', 'h1'))
            }
        
        # Network configuration fingerprint
        fingerprint_data['network_pattern'] = {
            'has_public_ip': bool(cloud_state.get('public_ip')),
            'security_group_count': len(cloud_state.get('security_groups', [])),
            'in_default_vpc': cloud_state.get('subnet_id', '').startswith('subnet-') if cloud_state.get('subnet_id') else False,
            'availability_zone': cloud_state.get('availability_zone', '')
        }
        
        # Security and management fingerprint
        fingerprint_data['management_pattern'] = {
            'has_key_pair': bool(cloud_state.get('key_name')),
            'has_iam_role': bool(cloud_state.get('iam_instance_profile')),
            'monitoring_enabled': cloud_state.get('monitoring') == 'enabled',
            'platform': cloud_state.get('platform', 'linux'),
            'root_device_type': cloud_state.get('root_device_type', 'ebs')
        }
        
        # Storage fingerprint
        block_devices = cloud_state.get('block_device_mappings', [])
        fingerprint_data['storage_pattern'] = {
            'volume_count': len(block_devices),
            'has_additional_storage': len(block_devices) > 1,
            'storage_types': list(set(bd.get('Ebs', {}).get('VolumeType', 'standard') 
                                    for bd in block_devices if 'Ebs' in bd))
        }
        
        return fingerprint_data
    
    def _predict_service_specific_impact(self, current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict EC2-specific change impacts"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0
        propagation_time = 60  # 1 minute for most EC2 operations
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # Analyze specific EC2 changes
        
        # 1. Instance type changes
        current_type = current.get('instance_type')
        desired_type = desired.get('instance_type')
        
        if current_type != desired_type:
            changes.append("instance_type_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            downtime = 300  # 5 minutes typical stop/start time
            propagation_time = max(propagation_time, 600)  # 10 minutes total
            rollback_complexity = "medium"
            
            # Calculate cost impact
            cost_impact = self._estimate_instance_type_cost_impact(current_type, desired_type)
            
            recommendations.append("Instance type change requires stop/start (5+ minutes downtime)")
            recommendations.append("Backup critical data before instance type change")
            
            if cost_impact > 50:
                recommendations.append(f"WARNING: Cost increase of ~{cost_impact:.0f}%")
            elif cost_impact < -20:
                recommendations.append(f"Cost savings of ~{abs(cost_impact):.0f}% detected")
        
        # 2. Security group changes
        current_sgs = set(current.get('security_groups', []))
        desired_sgs = set(desired.get('security_groups', []))
        
        if current_sgs != desired_sgs:
            changes.append("security_group_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            propagation_time = max(propagation_time, 120)  # 2 minutes
            
            added_sgs = desired_sgs - current_sgs
            removed_sgs = current_sgs - desired_sgs
            
            if removed_sgs:
                recommendations.append("WARNING: Removing security groups may break connectivity")
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            
            if added_sgs:
                recommendations.append("Test connectivity after adding new security groups")
            
            affected_resources.extend([f"security_group:{sg}" for sg in added_sgs.union(removed_sgs)])
        
        # 3. Key pair changes
        if current.get('key_name') != desired.get('key_name'):
            changes.append("key_pair_modification")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            recommendations.append("CRITICAL: Key pair cannot be changed on running instance")
            recommendations.append("This change requires instance recreation")
            rollback_complexity = "high"
            downtime = 600  # 10 minutes for recreation
        
        # 4. Subnet/VPC changes
        if (current.get('subnet_id') != desired.get('subnet_id') or 
            current.get('vpc_id') != desired.get('vpc_id')):
            changes.append("network_modification")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            recommendations.append("CRITICAL: Network changes require instance recreation")
            recommendations.append("IP addresses will change")
            rollback_complexity = "high"
            downtime = 600  # 10 minutes for recreation
            
            affected_resources.append("route53_records")
            affected_resources.append("load_balancer_targets")
        
        # 5. Image ID changes
        if current.get('image_id') != desired.get('image_id'):
            changes.append("ami_modification")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            recommendations.append("CRITICAL: AMI change requires instance recreation")
            recommendations.append("All instance data will be lost unless stored on EBS")
            rollback_complexity = "high"
            downtime = 600  # 10 minutes for recreation
        
        # 6. Monitoring changes
        current_monitoring = current.get('monitoring') == 'enabled'
        desired_monitoring = desired.get('monitoring_enabled', False)
        
        if current_monitoring != desired_monitoring:
            changes.append("monitoring_modification")
            impact_level = ChangeImpact.LOW if impact_level.value < ChangeImpact.LOW.value else impact_level
            recommendations.append("Monitoring changes take effect immediately")
            
            if desired_monitoring:
                cost_impact += 2  # CloudWatch costs
                recommendations.append("Detailed monitoring will incur additional costs")
        
        # 7. State changes
        current_state = current.get('state', 'running')
        desired_state = desired.get('state', 'running')
        
        if current_state != desired_state:
            changes.append("state_modification")
            
            if desired_state == 'stopped' and current_state == 'running':
                impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
                downtime = 120  # 2 minutes to stop
                recommendations.append("Stopping instance will cause service interruption")
            elif desired_state == 'running' and current_state == 'stopped':
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
                propagation_time = max(propagation_time, 180)  # 3 minutes to start
                recommendations.append("Starting instance may change public IP if not using Elastic IP")
        
        # Find affected resources
        instance_id = current.get('instance_id') or 'new-instance'
        affected_resources.extend([
            f"cloudwatch_alarms:{instance_id}",
            f"backup_policies:{instance_id}"
        ])
        
        change_type = ", ".join(changes) if changes else "configuration_update"
        
        return ChangeImpactAnalysis(
            change_type=change_type,
            impact_level=impact_level,
            estimated_downtime=downtime,
            propagation_time=propagation_time,
            cost_impact=cost_impact,
            affected_resources=affected_resources,
            recommendations=recommendations,
            rollback_complexity=rollback_complexity
        )
    
    def _estimate_instance_type_cost_impact(self, current_type: str, desired_type: str) -> float:
        """Estimate cost impact of instance type changes"""
        
        # Simplified cost estimation based on instance families
        cost_multipliers = {
            't2.nano': 1, 't2.micro': 2, 't2.small': 4, 't2.medium': 8, 't2.large': 16,
            't3.nano': 1.2, 't3.micro': 2.4, 't3.small': 4.8, 't3.medium': 9.6, 't3.large': 19.2,
            'm5.large': 20, 'm5.xlarge': 40, 'm5.2xlarge': 80, 'm5.4xlarge': 160,
            'c5.large': 18, 'c5.xlarge': 36, 'c5.2xlarge': 72, 'c5.4xlarge': 144,
            'r5.large': 25, 'r5.xlarge': 50, 'r5.2xlarge': 100, 'r5.4xlarge': 200
        }
        
        current_cost = cost_multipliers.get(current_type, 10)
        desired_cost = cost_multipliers.get(desired_type, 10)
        
        if current_cost == 0:
            return 0
        
        return ((desired_cost - current_cost) / current_cost) * 100
    
    def _check_service_specific_health(self, resource_id: str, 
                                     cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check EC2 instance health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # State check
        state = cloud_state.get('state', 'unknown')
        if state != 'running':
            health_score -= 0.4
            issues.append(f"Instance state: {state}")
        
        # Security checks
        security_groups = cloud_state.get('security_groups', [])
        if not security_groups:
            health_score -= 0.2
            issues.append("No security groups attached")
        
        # Key pair check
        if not cloud_state.get('key_name'):
            health_score -= 0.1
            issues.append("No key pair configured (SSH access may be limited)")
        
        # IAM role check
        if not cloud_state.get('iam_instance_profile'):
            health_score -= 0.1
            issues.append("No IAM instance profile (limited AWS service access)")
        
        # Monitoring check
        if cloud_state.get('monitoring') != 'enabled':
            issues.append("Detailed monitoring not enabled")
        
        # Network check
        if not cloud_state.get('vpc_id'):
            health_score -= 0.2
            issues.append("Instance not in VPC (using EC2-Classic)")
        
        # Storage check
        block_devices = cloud_state.get('block_device_mappings', [])
        if not block_devices:
            health_score -= 0.1
            issues.append("No block devices found")
        
        # Instance type appropriateness
        instance_type = cloud_state.get('instance_type', '')
        if instance_type.startswith('t2.nano'):
            issues.append("Very small instance type (t2.nano) - consider upgrading for production")
        
        # Calculate metrics
        metrics['security_features'] = sum([
            bool(security_groups),
            bool(cloud_state.get('key_name')),
            bool(cloud_state.get('iam_instance_profile')),
            cloud_state.get('state') == 'running'
        ])
        
        metrics['network_features'] = sum([
            bool(cloud_state.get('vpc_id')),
            bool(cloud_state.get('subnet_id')),
            bool(cloud_state.get('private_ip'))
        ])
        
        metrics['management_features'] = sum([
            cloud_state.get('monitoring') == 'enabled',
            len(cloud_state.get('tags', {})) > 0,
            len(block_devices) > 0
        ])
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate EC2-specific changes"""
        changes = {}
        
        # Check instance type
        if current.get('instance_type') != desired.get('instance_type'):
            changes['instance_type'] = {
                'from': current.get('instance_type'),
                'to': desired.get('instance_type'),
                'requires': 'restart'
            }
        
        # Check security groups
        current_sgs = set(current.get('security_groups', []))
        desired_sgs = set(desired.get('security_groups', []))
        
        if current_sgs != desired_sgs:
            changes['security_groups'] = {
                'from': list(current_sgs),
                'to': list(desired_sgs),
                'requires': 'update'
            }
        
        # Check key name
        if current.get('key_name') != desired.get('key_name'):
            changes['key_name'] = {
                'from': current.get('key_name'),
                'to': desired.get('key_name'),
                'requires': 'recreation'
            }
        
        # Check subnet
        if current.get('subnet_id') != desired.get('subnet_id'):
            changes['subnet_id'] = {
                'from': current.get('subnet_id'),
                'to': desired.get('subnet_id'),
                'requires': 'recreation'
            }
        
        # Check monitoring
        current_monitoring = current.get('monitoring') == 'enabled'
        desired_monitoring = desired.get('monitoring_enabled', False)
        
        if current_monitoring != desired_monitoring:
            changes['monitoring'] = {
                'from': current_monitoring,
                'to': desired_monitoring,
                'requires': 'update'
            }
        
        return changes
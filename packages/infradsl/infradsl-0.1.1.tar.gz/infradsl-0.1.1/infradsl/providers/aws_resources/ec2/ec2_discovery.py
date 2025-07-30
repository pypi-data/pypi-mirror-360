"""
EC2 Discovery Module

This module contains methods for discovering and managing existing EC2 instances.
It handles instance lookup, filtering, and provides utilities for finding
instances that might be related to the current configuration.
"""

from typing import Dict, Any, Optional, List


class EC2DiscoveryMixin:
    """
    Mixin class providing EC2 instance discovery capabilities.
    
    This class contains methods for:
    - Discovering existing instances in the account
    - Finding instances by name or tag
    - Filtering instances based on configuration
    """

    def _discover_existing_instances(self) -> Dict[str, Any]:
        """Discover existing EC2 instances that might be related to this configuration"""
        try:
            existing_instances = {}
            
            # List all EC2 instances in the current region
            response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopping', 'stopped']}
                ]
            )
            
            # Filter instances that might be related to this configuration
            # We look for instances that either:
            # 1. Have the exact same name as our instance
            # 2. Match our naming pattern (same base name with different suffixes)
            # 3. Have InfraDSL-related tags
            
            base_name = self.name.lower().replace('_', '-')
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    # Get instance name from tags
                    instance_name = None
                    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    instance_name = tags.get('Name', instance['InstanceId'])
                    
                    # Check if this instance might be related
                    is_related = False
                    
                    # 1. Exact match
                    if instance_name == self.name:
                        is_related = True
                    
                    # 2. Naming pattern match (same base name)
                    elif base_name in instance_name.lower():
                        is_related = True
                    
                    # 3. Check tags for InfraDSL managed instances
                    if any(tag_key.lower() in ['infradsl', 'managedby'] for tag_key in tags.keys()):
                        is_related = True
                    
                    if is_related:
                        # Parse launch time
                        launch_time = 'unknown'
                        if instance.get('LaunchTime'):
                            try:
                                launch_time = instance['LaunchTime'].strftime('%Y-%m-%d %H:%M')
                            except Exception:
                                pass
                        
                        existing_instances[instance_name] = {
                            'instance_id': instance['InstanceId'],
                            'instance_name': instance_name,
                            'instance_type': instance['InstanceType'],
                            'state': instance['State']['Name'],
                            'public_ip': instance.get('PublicIpAddress', 'none'),
                            'private_ip': instance.get('PrivateIpAddress', 'unknown'),
                            'availability_zone': instance['Placement']['AvailabilityZone'],
                            'ami_id': instance['ImageId'],
                            'launch_time': launch_time,
                            'tags': tags
                        }
            
            return existing_instances
            
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to discover existing EC2 instances: {str(e)}")
            return {}

    def _find_existing_instance(self) -> Optional[Dict[str, Any]]:
        """Find existing instance by name"""
        try:
            response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'tag:Name', 'Values': [self.name]},
                    {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopping', 'stopped']}
                ]
            )

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    return {
                        'instance_id': instance['InstanceId'],
                        'state': instance['State']['Name'],
                        'public_ip': instance.get('PublicIpAddress'),
                        'private_ip': instance.get('PrivateIpAddress'),
                        'availability_zone': instance['Placement']['AvailabilityZone'],
                        'instance_type': instance['InstanceType'],
                        'ami_id': instance['ImageId']
                    }
            return None
        except Exception as e:
            print(f"⚠️  Failed to check for existing instances: {str(e)}")
            return None

    def cleanup_duplicates(self) -> Dict[str, Any]:
        """Clean up duplicate instances with similar names"""
        existing_instances = self._discover_existing_instances()
        
        # Find potential duplicates (instances with similar names)
        duplicates = []
        base_name = self.name.lower().replace('_', '-')
        
        for instance_name, instance_info in existing_instances.items():
            if instance_name != self.name and base_name in instance_name.lower():
                duplicates.append(instance_info)
        
        if not duplicates:
            print(f"✅ No duplicate instances found")
            return {'duplicates_removed': 0, 'instances_kept': len(existing_instances)}
        
        print(f"🔍 Found {len(duplicates)} potential duplicate instances:")
        
        removed_count = 0
        for duplicate in duplicates:
            instance_name = duplicate['instance_name']
            instance_id = duplicate['instance_id']
            state = duplicate['state']
            
            print(f"   🗑️  Terminating duplicate: {instance_name} ({instance_id}) - {state}")
            
            try:
                if state not in ['terminated', 'terminating']:
                    self.ec2_client.terminate_instances(InstanceIds=[instance_id])
                    removed_count += 1
                    print(f"   ✅ Successfully terminated: {instance_name}")
                else:
                    print(f"   ⏭️  Already terminated: {instance_name}")
            except Exception as e:
                print(f"   ❌ Failed to terminate {instance_name}: {str(e)}")
        
        return {
            'duplicates_removed': removed_count,
            'instances_kept': len(existing_instances) - len(duplicates),
            'total_duplicates_found': len(duplicates)
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the instance"""
        if not self.instance_id:
            # Try to find the instance by name
            existing_instance = self._find_existing_instance()
            if existing_instance:
                self.instance_id = existing_instance['instance_id']
            else:
                return {
                    'status': 'not_found',
                    'message': f"No instance found with name '{self.name}'"
                }

        try:
            response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
            
            if response['Reservations']:
                instance = response['Reservations'][0]['Instances'][0]
                
                # Update instance state
                self.instance_state = instance['State']['Name']
                self.public_ip = instance.get('PublicIpAddress')
                self.private_ip = instance.get('PrivateIpAddress')
                self.availability_zone = instance['Placement']['AvailabilityZone']

                print(f"📊 Instance Status: {self.name}")
                print(f"   Instance ID: {self.instance_id}")
                print(f"   State: {self.instance_state}")
                print(f"   Instance Type: {instance['InstanceType']}")
                if self.public_ip:
                    print(f"   Public IP: {self.public_ip}")
                print(f"   Private IP: {self.private_ip}")
                print(f"   Availability Zone: {self.availability_zone}")
                print(f"   Launch Time: {instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')}")

                return {
                    'status': self.instance_state,
                    'instance_id': self.instance_id,
                    'instance_type': instance['InstanceType'],
                    'public_ip': self.public_ip,
                    'private_ip': self.private_ip,
                    'availability_zone': self.availability_zone,
                    'launch_time': instance['LaunchTime'].isoformat(),
                    'ami_id': instance['ImageId']
                }
            else:
                return {
                    'status': 'not_found',
                    'message': f"Instance {self.instance_id} not found"
                }

        except Exception as e:
            print(f"❌ Failed to get instance status: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _list_instances_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """List instances matching a naming pattern"""
        try:
            response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopping', 'stopped']}
                ]
            )
            
            matching_instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    instance_name = tags.get('Name', instance['InstanceId'])
                    
                    if pattern.lower() in instance_name.lower():
                        matching_instances.append({
                            'instance_id': instance['InstanceId'],
                            'name': instance_name,
                            'state': instance['State']['Name'],
                            'instance_type': instance['InstanceType'],
                            'public_ip': instance.get('PublicIpAddress'),
                            'private_ip': instance.get('PrivateIpAddress'),
                            'launch_time': instance.get('LaunchTime')
                        })
            
            return matching_instances
            
        except Exception as e:
            print(f"❌ Failed to list instances: {str(e)}")
            return []

    def _get_instance_details(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific instance"""
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            
            if response['Reservations']:
                instance = response['Reservations'][0]['Instances'][0]
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                
                return {
                    'instance_id': instance['InstanceId'],
                    'name': tags.get('Name', 'N/A'),
                    'state': instance['State']['Name'],
                    'instance_type': instance['InstanceType'],
                    'ami_id': instance['ImageId'],
                    'public_ip': instance.get('PublicIpAddress'),
                    'private_ip': instance.get('PrivateIpAddress'),
                    'availability_zone': instance['Placement']['AvailabilityZone'],
                    'launch_time': instance.get('LaunchTime'),
                    'security_groups': [sg['GroupId'] for sg in instance.get('SecurityGroups', [])],
                    'subnet_id': instance.get('SubnetId'),
                    'vpc_id': instance.get('VpcId'),
                    'tags': tags
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to get instance details: {str(e)}")
            return None
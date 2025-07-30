"""
EC2 Lifecycle Module

This module handles EC2 instance lifecycle operations including:
- Creating new instances
- Updating existing instances  
- Starting and stopping instances
- Destroying/terminating instances
- Volume management operations
"""

from typing import Dict, Any, Optional


class EC2LifecycleMixin:
    """
    Mixin class providing EC2 instance lifecycle management capabilities.
    
    This class contains methods for:
    - Creating new EC2 instances
    - Updating existing instances
    - Managing instance state (start/stop/destroy)
    - Volume resize operations
    """

    def _create_new_instance(self) -> Dict[str, Any]:
        """Create a new EC2 instance"""
        if not self.ami_id:
            raise ValueError("AMI ID is required. Either specify ami_id or ensure auto-detection works.")

        try:
            # Apply any pending security rules first
            self._apply_security_rules()

            # Prepare instance parameters
            run_params = {
                'ImageId': self.ami_id,
                'InstanceType': self.instance_type,
                'MinCount': 1,
                'MaxCount': 1,
                'TagSpecifications': [
                    {
                        'ResourceType': 'instance',
                        'Tags': [{'Key': k, 'Value': v} for k, v in self._get_all_tags().items()]
                    }
                ]
            }

            # Configure root volume size and type
            run_params['BlockDeviceMappings'] = [{
                'DeviceName': '/dev/sda1',  # Root device for Ubuntu
                'Ebs': {
                    'VolumeSize': self.root_volume_size,
                    'VolumeType': self.root_volume_type,
                    'DeleteOnTermination': True
                }
            }]

            # Add optional parameters
            if self.key_name:
                run_params['KeyName'] = self.key_name
            if self.security_groups:
                run_params['SecurityGroupIds'] = self.security_groups
            if self.subnet_id:
                run_params['SubnetId'] = self.subnet_id
            if self.user_data:
                run_params['UserData'] = self.user_data

            if self.associate_public_ip:
                run_params['NetworkInterfaces'] = [{
                    'DeviceIndex': 0,
                    'AssociatePublicIpAddress': True,
                    'Groups': self.security_groups or []
                }]
                # Remove SecurityGroupIds if using NetworkInterfaces
                run_params.pop('SecurityGroupIds', None)

            # Create instance using EC2 client
            response = self.ec2_client.run_instances(**run_params)
            instance = response['Instances'][0]

            result = {
                'instance_id': instance['InstanceId'],
                'state': instance['State']['Name'],
                'private_ip': instance.get('PrivateIpAddress'),
                'availability_zone': instance['Placement']['AvailabilityZone']
            }

            # Get public IP if assigned
            if 'PublicIpAddress' in instance:
                result['public_ip'] = instance['PublicIpAddress']

            # Store instance information
            self.instance_id = result['instance_id']
            self.instance_state = result['state']
            self.public_ip = result.get('public_ip')
            self.private_ip = result.get('private_ip')
            self.availability_zone = result.get('availability_zone')

            print(f"✅ EC2 instance created successfully")
            print(f"   Instance ID: {self.instance_id}")
            if self.public_ip:
                print(f"   Public IP: {self.public_ip}")
            print(f"   Private IP: {self.private_ip}")
            print(f"   Availability Zone: {self.availability_zone}")

            if self.key_name:
                print(f"💡 SSH access: ssh -i {self.key_name}.pem ubuntu@{self.public_ip or self.private_ip}")

            return {
                'instance_id': self.instance_id,
                'name': self.name,
                'state': self.instance_state,
                'public_ip': self.public_ip,
                'private_ip': self.private_ip,
                'availability_zone': self.availability_zone,
                'instance_type': self.instance_type,
                'ami_id': self.ami_id,
                'created': True
            }

        except Exception as e:
            print(f"❌ Failed to create EC2 instance: {str(e)}")
            raise

    def _update_existing_instance(self, existing_instance: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing instance (security rules only)"""
        # Store existing instance information
        self.instance_id = existing_instance['instance_id']
        self.instance_state = existing_instance['state']
        self.public_ip = existing_instance.get('public_ip')
        self.private_ip = existing_instance.get('private_ip')
        self.availability_zone = existing_instance.get('availability_zone')

        # Apply security rules to existing instance
        self._apply_security_rules()

        print(f"✅ EC2 instance updated successfully")
        print(f"   Instance ID: {self.instance_id}")
        print(f"   State: {self.instance_state}")
        if self.public_ip:
            print(f"   Public IP: {self.public_ip}")
        print(f"   Private IP: {self.private_ip}")

        if self.key_name and self.public_ip:
            print(f"💡 SSH access: ssh -i {self.key_name}.pem ubuntu@{self.public_ip}")

        return {
            'instance_id': self.instance_id,
            'name': self.name,
            'state': self.instance_state,
            'public_ip': self.public_ip,
            'private_ip': self.private_ip,
            'availability_zone': self.availability_zone,
            'instance_type': existing_instance['instance_type'],
            'ami_id': existing_instance['ami_id'],
            'updated': True
        }

    def destroy(self) -> Dict[str, Any]:
        """Destroy the EC2 instance(s) - handles duplicates"""
        if not self.instance_id:
            print("⚠️  No instance ID found. Attempting to find instances by name...")
            response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'tag:Name', 'Values': [self.name]},
                    {'Name': 'instance-state-name', 'Values': ['running', 'stopped', 'pending']}
                ]
            )

            matching_instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    matching_instances.append({
                        'instance_id': instance['InstanceId'],
                        'state': instance['State']['Name']
                    })

            if not matching_instances:
                print(f"❌ No instances found with name: {self.name}")
                return {'destroyed': False, 'reason': 'Instance not found'}

            if len(matching_instances) > 1:
                print(f"🚨 Found {len(matching_instances)} duplicate instances with name: {self.name}")
                for inst in matching_instances:
                    print(f"   - {inst['instance_id']} ({inst['state']})")

                print("🗑️  Destroying ALL duplicate instances...")
                destroyed_count = 0
                destroyed_instances = []

                for instance in matching_instances:
                    try:
                        self.ec2_client.terminate_instances(InstanceIds=[instance['instance_id']])
                        destroyed_instances.append(instance['instance_id'])
                        destroyed_count += 1
                        print(f"✅ Terminated: {instance['instance_id']}")
                    except Exception as e:
                        print(f"❌ Failed to terminate {instance['instance_id']}: {str(e)}")

                return {
                    'name': self.name,
                    'destroyed_count': destroyed_count,
                    'destroyed_instances': destroyed_instances,
                    'destroyed': True
                }
            else:
                self.instance_id = matching_instances[0]['instance_id']

        print(f"🗑️  Destroying EC2 instance: {self.name} ({self.instance_id})")

        try:
            response = self.ec2_client.terminate_instances(InstanceIds=[self.instance_id])
            result = {
                'instance_id': self.instance_id,
                'status': 'terminating'
            }

            # Reset instance state
            self.instance_state = 'terminated'

            print(f"✅ EC2 instance destroyed successfully")

            return {
                'instance_id': self.instance_id,
                'name': self.name,
                'status': 'terminated',
                'destroyed': True
            }

        except Exception as e:
            print(f"❌ Failed to destroy EC2 instance: {str(e)}")
            raise

    def start(self) -> Dict[str, Any]:
        """Start a stopped EC2 instance"""
        if not self.instance_id:
            raise ValueError("Instance ID not set. Create instance first or set instance_id manually.")

        try:
            response = self.ec2_client.start_instances(InstanceIds=[self.instance_id])
            self.instance_state = 'running'

            # Get updated instance info
            instances_response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
            instance = instances_response['Reservations'][0]['Instances'][0]
            self.public_ip = instance.get('PublicIpAddress')
            self.private_ip = instance.get('PrivateIpAddress')

            print(f"✅ EC2 instance started successfully")
            print(f"   Instance ID: {self.instance_id}")
            print(f"   State: {instance['State']['Name']}")
            if self.public_ip:
                print(f"   Public IP: {self.public_ip}")

            return {
                'instance_id': self.instance_id,
                'name': self.name,
                'state': instance['State']['Name'],
                'public_ip': self.public_ip,
                'private_ip': self.private_ip
            }
        except Exception as e:
            print(f"❌ Failed to start instance: {str(e)}")
            raise

    def stop(self) -> Dict[str, Any]:
        """Stop a running EC2 instance"""
        if not self.instance_id:
            raise ValueError("Instance ID not set. Create instance first or set instance_id manually.")

        try:
            response = self.ec2_client.stop_instances(InstanceIds=[self.instance_id])
            self.instance_state = 'stopping'

            print(f"✅ EC2 instance stopped successfully")
            print(f"   Instance ID: {self.instance_id}")
            print(f"   State: stopping")

            return {
                'instance_id': self.instance_id,
                'name': self.name,
                'state': 'stopping'
            }
        except Exception as e:
            print(f"❌ Failed to stop instance: {str(e)}")
            raise

    def resize_volume(self, new_size_gb: int) -> Dict[str, Any]:
        """Resize the root volume of the instance"""
        if not self.instance_id:
            raise ValueError("Instance ID not set. Create instance first or set instance_id manually.")

        try:
            # Get the instance details to find the root volume
            response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
            instance = response['Reservations'][0]['Instances'][0]
            
            # Find root volume
            root_volume_id = None
            for bdm in instance['BlockDeviceMappings']:
                if bdm['DeviceName'] == '/dev/sda1':  # Root device for Ubuntu
                    root_volume_id = bdm['Ebs']['VolumeId']
                    break
            
            if not root_volume_id:
                raise ValueError("Could not find root volume for instance")

            # Get current volume info
            volumes_response = self.ec2_client.describe_volumes(VolumeIds=[root_volume_id])
            current_volume = volumes_response['Volumes'][0]
            current_size = current_volume['Size']

            if new_size_gb <= current_size:
                print(f"⚠️  New size ({new_size_gb} GB) must be larger than current size ({current_size} GB)")
                return {
                    'resized': False,
                    'reason': f'New size must be larger than current size ({current_size} GB)'
                }

            print(f"📏 Resizing volume from {current_size} GB to {new_size_gb} GB...")

            # Resize the volume
            self.ec2_client.modify_volume(
                VolumeId=root_volume_id,
                Size=new_size_gb
            )

            # Update our configuration
            self.root_volume_size = new_size_gb

            print(f"✅ Volume resize initiated successfully")
            print(f"   Volume ID: {root_volume_id}")
            print(f"   New Size: {new_size_gb} GB")
            print(f"💡 You may need to extend the filesystem inside the instance:")
            print(f"   sudo resize2fs /dev/xvda1")

            return {
                'volume_id': root_volume_id,
                'old_size_gb': current_size,
                'new_size_gb': new_size_gb,
                'resized': True,
                'instance_id': self.instance_id
            }

        except Exception as e:
            print(f"❌ Failed to resize volume: {str(e)}")
            raise

    def _apply_security_rules(self):
        """Apply security rules (placeholder - implement in configuration module)"""
        # This method will be implemented in the configuration module
        # For now, we'll just pass
        pass

    def _get_all_tags(self) -> Dict[str, str]:
        """Get all tags for the instance (placeholder)"""
        # This method should be implemented in the main EC2 class
        return self.instance_tags or {}

    def set_instance_id(self, instance_id: str):
        """Set the instance ID manually"""
        self.instance_id = instance_id
        return self

    def generate_ssh_command(self) -> str:
        """Generate SSH command for connecting to the instance"""
        if not self.public_ip and not self.private_ip:
            return "Instance has no IP address assigned"
        
        if not self.key_name:
            return "No key pair configured for SSH access"
        
        ip_address = self.public_ip or self.private_ip
        return f"ssh -i {self.key_name}.pem ubuntu@{ip_address}"
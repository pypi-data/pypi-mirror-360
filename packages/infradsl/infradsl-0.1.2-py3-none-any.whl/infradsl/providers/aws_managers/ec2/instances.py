"""
AWS EC2 Instances Operations

Focused module for EC2 instance lifecycle management.
Handles creation, deletion, start, stop, and listing of EC2 instances.
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from ..aws_client import AwsClient

if TYPE_CHECKING:
    try:
        from botocore.client import BaseClient
        from boto3.resources.base import ServiceResource
    except ImportError:
        BaseClient = Any
        ServiceResource = Any


class EC2Instances:
    """Handles EC2 instance operations"""

    def __init__(self, aws_client: AwsClient):
        self.aws_client = aws_client
        self.ec2_client: Optional['BaseClient'] = None
        self.ec2_resource: Optional['ServiceResource'] = None

    def _ensure_clients(self):
        """Ensure EC2 clients are initialized"""
        if not self.ec2_client:
            self.ec2_client = self.aws_client.get_client('ec2')
            self.ec2_resource = self.aws_client.get_resource('ec2')

        if not self.ec2_client:
            raise RuntimeError("Failed to initialize EC2 client")

    def create(
        self,
        instance_name: str,
        image_id: str,
        instance_type: str = 't3.micro',
        key_name: Optional[str] = None,
        security_groups: Optional[List[str]] = None,
        subnet_id: Optional[str] = None,
        user_data: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        min_count: int = 1,
        max_count: int = 1
    ) -> Dict[str, Any]:
        """
        Create EC2 instance(s).

        Args:
            instance_name: Name for the instance
            image_id: AMI ID to use
            instance_type: Instance type (default: t3.micro)
            key_name: Key pair name for SSH access
            security_groups: List of security group IDs
            subnet_id: Subnet ID for VPC
            user_data: User data script
            tags: Additional tags for the instance
            min_count: Minimum number of instances
            max_count: Maximum number of instances

        Returns:
            Dict containing instance information
        """
        self._ensure_clients()

        print(f"🚀 Creating EC2 instance: {instance_name}")
        print(f"   - Image ID: {image_id}")
        print(f"   - Instance Type: {instance_type}")
        print(f"   - Region: {self.aws_client.get_region()}")

        # Build launch parameters
        launch_params = {
            'ImageId': image_id,
            'InstanceType': instance_type,
            'MinCount': min_count,
            'MaxCount': max_count,
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': instance_name}
                    ]
                }
            ]
        }

        # Add optional parameters
        if key_name:
            launch_params['KeyName'] = key_name
            print(f"   - Key Pair: {key_name}")

        if security_groups:
            launch_params['SecurityGroupIds'] = security_groups
            print(f"   - Security Groups: {', '.join(security_groups)}")

        if subnet_id:
            launch_params['SubnetId'] = subnet_id
            print(f"   - Subnet: {subnet_id}")

        if user_data:
            launch_params['UserData'] = user_data
            print("   - User Data: Provided")

        # Add custom tags
        if tags:
            for key, value in tags.items():
                launch_params['TagSpecifications'][0]['Tags'].append({
                    'Key': key,
                    'Value': value
                })

        try:
            # Launch instance
            response = self.ec2_client.run_instances(**launch_params)
            instances = response['Instances']

            print("✅ Instance launch initiated")
            for instance in instances:
                instance_id = instance['InstanceId']
                print(f"   - Instance ID: {instance_id}")

            # Wait for instances to be in running state
            if len(instances) == 1:
                instance_id = instances[0]['InstanceId']
                print(f"⏳ Waiting for instance {instance_id} to be running...")

                waiter = self.ec2_client.get_waiter('instance_running')
                waiter.wait(InstanceIds=[instance_id])

                # Get updated instance info
                updated_response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
                instance_info = updated_response['Reservations'][0]['Instances'][0]

                print(f"✅ Instance {instance_id} is now running")
                if instance_info.get('PublicIpAddress'):
                    print(f"   - Public IP: {instance_info['PublicIpAddress']}")
                if instance_info.get('PrivateIpAddress'):
                    print(f"   - Private IP: {instance_info['PrivateIpAddress']}")

                return {
                    'instance_id': instance_id,
                    'name': instance_name,
                    'state': instance_info['State']['Name'],
                    'public_ip': instance_info.get('PublicIpAddress'),
                    'private_ip': instance_info.get('PrivateIpAddress'),
                    'instance_type': instance_info['InstanceType'],
                    'availability_zone': instance_info['Placement']['AvailabilityZone']
                }

            return {
                'instances': [
                    {
                        'instance_id': inst['InstanceId'],
                        'name': instance_name,
                        'state': inst['State']['Name']
                    }
                    for inst in instances
                ]
            }

        except Exception as e:
            print(f"❌ Failed to create instance: {str(e)}")
            raise

    def terminate(self, instance_id: str) -> Dict[str, Any]:
        """
        Terminate an EC2 instance.

        Args:
            instance_id: Instance ID to terminate

        Returns:
            Dict containing termination information
        """
        self._ensure_clients()

        print(f"🗑️  Terminating EC2 instance: {instance_id}")

        try:
            # Get instance info before termination
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            instance = response['Reservations'][0]['Instances'][0]
            instance_name = next(
                (tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'),
                'Unknown'
            )

            # Terminate instance
            self.ec2_client.terminate_instances(InstanceIds=[instance_id])

            print(f"✅ Termination initiated for {instance_name} ({instance_id})")
            print("⏳ Waiting for instance to terminate...")

            # Wait for termination
            waiter = self.ec2_client.get_waiter('instance_terminated')
            waiter.wait(InstanceIds=[instance_id])

            print(f"✅ Instance {instance_id} has been terminated")

            return {
                'instance_id': instance_id,
                'name': instance_name,
                'status': 'terminated'
            }

        except Exception as e:
            print(f"❌ Failed to terminate instance: {str(e)}")
            raise

    def start(self, instance_id: str) -> Dict[str, Any]:
        """
        Start a stopped EC2 instance.

        Args:
            instance_id: Instance ID to start

        Returns:
            Dict containing start operation information
        """
        self._ensure_clients()

        print(f"▶️  Starting EC2 instance: {instance_id}")

        try:
            self.ec2_client.start_instances(InstanceIds=[instance_id])

            print(f"⏳ Waiting for instance {instance_id} to be running...")
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id])

            print(f"✅ Instance {instance_id} is now running")

            return {
                'instance_id': instance_id,
                'status': 'running'
            }

        except Exception as e:
            print(f"❌ Failed to start instance: {str(e)}")
            raise

    def stop(self, instance_id: str) -> Dict[str, Any]:
        """
        Stop a running EC2 instance.

        Args:
            instance_id: Instance ID to stop

        Returns:
            Dict containing stop operation information
        """
        self._ensure_clients()

        print(f"⏸️  Stopping EC2 instance: {instance_id}")

        try:
            self.ec2_client.stop_instances(InstanceIds=[instance_id])

            print(f"⏳ Waiting for instance {instance_id} to stop...")
            waiter = self.ec2_client.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=[instance_id])

            print(f"✅ Instance {instance_id} has been stopped")

            return {
                'instance_id': instance_id,
                'status': 'stopped'
            }

        except Exception as e:
            print(f"❌ Failed to stop instance: {str(e)}")
            raise

    def list(self, filters: Optional[Dict[str, List[str]]] = None) -> List[Dict[str, Any]]:
        """
        List EC2 instances.

        Args:
            filters: Optional filters for instances

        Returns:
            List of instance information
        """
        self._ensure_clients()

        try:
            params = {}
            if filters:
                params['Filters'] = [
                    {'Name': key, 'Values': values}
                    for key, values in filters.items()
                ]

            response = self.ec2_client.describe_instances(**params)
            instances = []

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_name = next(
                        (tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'),
                        'Unknown'
                    )

                    instances.append({
                        'instance_id': instance['InstanceId'],
                        'name': instance_name,
                        'state': instance['State']['Name'],
                        'instance_type': instance['InstanceType'],
                        'public_ip': instance.get('PublicIpAddress'),
                        'private_ip': instance.get('PrivateIpAddress'),
                        'availability_zone': instance['Placement']['AvailabilityZone'],
                        'launch_time': instance['LaunchTime'].isoformat() if instance.get('LaunchTime') else None
                    })

            return instances

        except Exception as e:
            print(f"❌ Failed to list instances: {str(e)}")
            raise

    def get(self, instance_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific instance.

        Args:
            instance_id: Instance ID to get information for

        Returns:
            Dict containing detailed instance information
        """
        self._ensure_clients()

        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            instance = response['Reservations'][0]['Instances'][0]

            instance_name = next(
                (tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'),
                'Unknown'
            )

            return {
                'instance_id': instance['InstanceId'],
                'name': instance_name,
                'state': instance['State']['Name'],
                'instance_type': instance['InstanceType'],
                'image_id': instance['ImageId'],
                'public_ip': instance.get('PublicIpAddress'),
                'private_ip': instance.get('PrivateIpAddress'),
                'availability_zone': instance['Placement']['AvailabilityZone'],
                'subnet_id': instance.get('SubnetId'),
                'vpc_id': instance.get('VpcId'),
                'security_groups': [sg['GroupId'] for sg in instance.get('SecurityGroups', [])],
                'key_name': instance.get('KeyName'),
                'launch_time': instance['LaunchTime'].isoformat() if instance.get('LaunchTime') else None,
                'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            }

        except Exception as e:
            print(f"❌ Failed to get instance info: {str(e)}")
            raise

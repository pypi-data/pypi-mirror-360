"""
AWS EC2 Manager

Main coordinator for EC2 operations. This manager orchestrates
different EC2 components like instances and images.
"""

from typing import Dict, Any, List, Optional
from ..aws_client import AwsClient
from .instances import EC2Instances
from .images import EC2Images


class EC2Manager:
    """Main EC2 manager that coordinates instance and image operations"""

    def __init__(self, aws_client: Optional[AwsClient] = None):
        self.aws_client = aws_client or AwsClient()

        # Initialize component managers
        self.instances = EC2Instances(self.aws_client)
        self.images = EC2Images(self.aws_client)

    def _ensure_authenticated(self):
        """Ensure AWS authentication"""
        if not self.aws_client.is_authenticated:
            self.aws_client.authenticate(silent=True)

    # Instance operations - delegate to instances component
    def create_instance(
        self,
        instance_name: str,
        image_id: str,
        instance_type: str = 't3.micro',
        **kwargs
    ) -> Dict[str, Any]:
        """Create an EC2 instance"""
        self._ensure_authenticated()
        return self.instances.create(instance_name, image_id, instance_type, **kwargs)

    def terminate_instance(self, instance_id: str) -> Dict[str, Any]:
        """Terminate an EC2 instance"""
        self._ensure_authenticated()
        return self.instances.terminate(instance_id)

    def start_instance(self, instance_id: str) -> Dict[str, Any]:
        """Start a stopped EC2 instance"""
        self._ensure_authenticated()
        return self.instances.start(instance_id)

    def stop_instance(self, instance_id: str) -> Dict[str, Any]:
        """Stop a running EC2 instance"""
        self._ensure_authenticated()
        return self.instances.stop(instance_id)

    def list_instances(self, filters: Optional[Dict[str, List[str]]] = None) -> List[Dict[str, Any]]:
        """List EC2 instances"""
        self._ensure_authenticated()
        return self.instances.list(filters)

    def get_instance(self, instance_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific instance"""
        self._ensure_authenticated()
        return self.instances.get(instance_id)

    # Image operations - delegate to images component
    def get_available_amis(
        self,
        owners: Optional[List[str]] = None,
        filters: Optional[Dict[str, List[str]]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Get available AMIs"""
        self._ensure_authenticated()
        return self.images.list_available(owners, filters, **kwargs)

    def find_ubuntu_ami(self, version: str = '22.04') -> Optional[Dict[str, Any]]:
        """Find the latest Ubuntu AMI"""
        self._ensure_authenticated()
        return self.images.find_ubuntu_latest(version)

    def find_amazon_linux_ami(self, version: str = '2') -> Optional[Dict[str, Any]]:
        """Find the latest Amazon Linux AMI"""
        self._ensure_authenticated()
        return self.images.find_amazon_linux_latest(version)

    def find_windows_ami(self, version: str = '2022') -> Optional[Dict[str, Any]]:
        """Find the latest Windows Server AMI"""
        self._ensure_authenticated()
        return self.images.find_windows_latest(version)

    def get_popular_amis(self) -> Dict[str, Dict[str, Any]]:
        """Get a curated list of popular AMIs"""
        self._ensure_authenticated()
        return self.images.get_popular_amis()

    def validate_ami(self, image_id: str) -> bool:
        """Validate that an AMI exists and is available"""
        self._ensure_authenticated()
        return self.images.validate_image_exists(image_id)

    # Convenience methods for common workflows
    def quick_launch(
        self,
        instance_name: str,
        os_type: str = 'ubuntu',
        instance_type: str = 't3.micro',
        key_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Quick launch an instance with sensible defaults.

        Args:
            instance_name: Name for the instance
            os_type: OS type ('ubuntu', 'amazon-linux', 'windows')
            instance_type: Instance type
            key_name: SSH key pair name

        Returns:
            Instance information
        """
        self._ensure_authenticated()

        print(f"🚀 Quick launching {os_type} instance: {instance_name}")

        # Find appropriate AMI
        if os_type.lower() == 'ubuntu':
            ami = self.find_ubuntu_ami()
        elif os_type.lower() in ['amazon-linux', 'amazonlinux']:
            ami = self.find_amazon_linux_ami()
        elif os_type.lower() == 'windows':
            ami = self.find_windows_ami()
        else:
            raise ValueError(f"Unsupported OS type: {os_type}")

        if not ami:
            raise ValueError(f"Could not find suitable AMI for {os_type}")

        print(f"   - Using AMI: {ami['name']} ({ami['image_id']})")

        return self.create_instance(
            instance_name=instance_name,
            image_id=ami['image_id'],
            instance_type=instance_type,
            key_name=key_name
        )

    def get_region(self) -> str:
        """Get current AWS region"""
        return self.aws_client.get_region()

    def get_account_id(self) -> str:
        """Get current AWS account ID"""
        return self.aws_client.get_account_id()

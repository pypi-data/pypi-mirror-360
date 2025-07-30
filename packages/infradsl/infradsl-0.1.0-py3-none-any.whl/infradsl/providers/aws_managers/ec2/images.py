"""
AWS EC2 AMI Operations

Focused module for EC2 AMI (Amazon Machine Image) management.
Handles listing, filtering, and working with AMIs.
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from ..aws_client import AwsClient

if TYPE_CHECKING:
    try:
        from botocore.client import BaseClient
    except ImportError:
        BaseClient = Any


class EC2Images:
    """Handles EC2 AMI operations"""

    def __init__(self, aws_client: AwsClient):
        self.aws_client = aws_client
        self.ec2_client: Optional['BaseClient'] = None

    def _ensure_clients(self):
        """Ensure EC2 clients are initialized"""
        if not self.ec2_client:
            self.ec2_client = self.aws_client.get_client('ec2')

        if not self.ec2_client:
            raise RuntimeError("Failed to initialize EC2 client")

    def list_available(
        self,
        owners: Optional[List[str]] = None,
        filters: Optional[Dict[str, List[str]]] = None,
        architecture: str = 'x86_64',
        virtualization_type: str = 'hvm',
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get available AMIs.

        Args:
            owners: List of owner IDs (default: ['amazon'])
            filters: Additional filters for AMIs
            architecture: Architecture filter (x86_64, arm64)
            virtualization_type: Virtualization type (hvm, paravirtual)
            limit: Maximum number of AMIs to return

        Returns:
            List of available AMIs
        """
        self._ensure_clients()

        if owners is None:
            owners = ['amazon']

        params = {
            'Owners': owners,
            'Filters': [
                {'Name': 'architecture', 'Values': [architecture]},
                {'Name': 'virtualization-type', 'Values': [virtualization_type]},
                {'Name': 'state', 'Values': ['available']}
            ]
        }

        # Add custom filters
        if filters:
            for key, values in filters.items():
                params['Filters'].append({'Name': key, 'Values': values})

        try:
            response = self.ec2_client.describe_images(**params)
            amis = []

            for image in response['Images']:
                amis.append({
                    'image_id': image['ImageId'],
                    'name': image.get('Name', 'Unknown'),
                    'description': image.get('Description', ''),
                    'architecture': image.get('Architecture'),
                    'platform': image.get('Platform', 'linux'),
                    'virtualization_type': image.get('VirtualizationType'),
                    'creation_date': image.get('CreationDate'),
                    'owner_id': image.get('OwnerId'),
                    'public': image.get('Public', False),
                    'root_device_type': image.get('RootDeviceType'),
                    'root_device_name': image.get('RootDeviceName')
                })

            # Sort by creation date (newest first) and limit results
            sorted_amis = sorted(amis, key=lambda x: x['creation_date'] or '', reverse=True)
            return sorted_amis[:limit]

        except Exception as e:
            print(f"❌ Failed to list AMIs: {str(e)}")
            raise

    def find_ubuntu_latest(self, version: str = '22.04') -> Optional[Dict[str, Any]]:
        """
        Find the latest Ubuntu AMI for a specific version.

        Args:
            version: Ubuntu version (e.g., '22.04', '20.04')

        Returns:
            Latest Ubuntu AMI information or None if not found
        """
        filters = {
            'name': [f'ubuntu/images/hvm-ssd/ubuntu-*-{version}-amd64-server-*'],
            'owner-id': ['099720109477']  # Canonical
        }

        amis = self.list_available(owners=['099720109477'], filters=filters, limit=1)
        return amis[0] if amis else None

    def find_amazon_linux_latest(self, version: str = '2') -> Optional[Dict[str, Any]]:
        """
        Find the latest Amazon Linux AMI.

        Args:
            version: Amazon Linux version ('1', '2', '2023')

        Returns:
            Latest Amazon Linux AMI information or None if not found
        """
        if version == '2023':
            name_pattern = 'al2023-ami-*-x86_64'
        elif version == '2':
            name_pattern = 'amzn2-ami-hvm-*-x86_64-gp2'
        else:
            name_pattern = 'amzn-ami-hvm-*-x86_64-gp2'

        filters = {
            'name': [name_pattern],
            'owner-id': ['137112412989']  # Amazon
        }

        amis = self.list_available(owners=['137112412989'], filters=filters, limit=1)
        return amis[0] if amis else None

    def find_windows_latest(self, version: str = '2022') -> Optional[Dict[str, Any]]:
        """
        Find the latest Windows Server AMI.

        Args:
            version: Windows Server version ('2019', '2022')

        Returns:
            Latest Windows Server AMI information or None if not found
        """
        filters = {
            'name': [f'Windows_Server-{version}-English-Full-Base-*'],
            'owner-id': ['801119661308']  # Amazon
        }

        amis = self.list_available(owners=['801119661308'], filters=filters, limit=1)
        return amis[0] if amis else None

    def search_by_name(self, name_pattern: str, owner_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search AMIs by name pattern.

        Args:
            name_pattern: Name pattern to search for (supports wildcards)
            owner_id: Optional owner ID to filter by

        Returns:
            List of matching AMIs
        """
        filters = {
            'name': [name_pattern]
        }

        owners = [owner_id] if owner_id else ['self', 'amazon']
        return self.list_available(owners=owners, filters=filters)

    def get_image_details(self, image_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific AMI.

        Args:
            image_id: AMI ID to get details for

        Returns:
            Detailed AMI information
        """
        self._ensure_clients()

        try:
            response = self.ec2_client.describe_images(ImageIds=[image_id])

            if not response['Images']:
                raise ValueError(f"AMI {image_id} not found")

            image = response['Images'][0]

            return {
                'image_id': image['ImageId'],
                'name': image.get('Name', 'Unknown'),
                'description': image.get('Description', ''),
                'architecture': image.get('Architecture'),
                'platform': image.get('Platform', 'linux'),
                'virtualization_type': image.get('VirtualizationType'),
                'creation_date': image.get('CreationDate'),
                'owner_id': image.get('OwnerId'),
                'public': image.get('Public', False),
                'root_device_type': image.get('RootDeviceType'),
                'root_device_name': image.get('RootDeviceName'),
                'block_device_mappings': image.get('BlockDeviceMappings', []),
                'tags': {tag['Key']: tag['Value'] for tag in image.get('Tags', [])},
                'state': image.get('State'),
                'hypervisor': image.get('Hypervisor'),
                'image_type': image.get('ImageType'),
                'kernel_id': image.get('KernelId'),
                'ramdisk_id': image.get('RamdiskId'),
                'sriov_net_support': image.get('SriovNetSupport'),
                'ena_support': image.get('EnaSupport')
            }

        except Exception as e:
            print(f"❌ Failed to get image details: {str(e)}")
            raise

    def get_popular_amis(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a curated list of popular AMIs for quick reference.

        Returns:
            Dictionary of popular AMIs by category
        """
        popular_amis = {}

        # Ubuntu 22.04 LTS
        ubuntu_ami = self.find_ubuntu_latest('22.04')
        if ubuntu_ami:
            popular_amis['ubuntu_22_04_lts'] = ubuntu_ami

        # Ubuntu 20.04 LTS
        ubuntu_20_ami = self.find_ubuntu_latest('20.04')
        if ubuntu_20_ami:
            popular_amis['ubuntu_20_04_lts'] = ubuntu_20_ami

        # Amazon Linux 2
        al2_ami = self.find_amazon_linux_latest('2')
        if al2_ami:
            popular_amis['amazon_linux_2'] = al2_ami

        # Amazon Linux 2023
        al2023_ami = self.find_amazon_linux_latest('2023')
        if al2023_ami:
            popular_amis['amazon_linux_2023'] = al2023_ami

        # Windows Server 2022
        windows_ami = self.find_windows_latest('2022')
        if windows_ami:
            popular_amis['windows_server_2022'] = windows_ami

        return popular_amis

    def validate_image_exists(self, image_id: str) -> bool:
        """
        Validate that an AMI exists and is available.

        Args:
            image_id: AMI ID to validate

        Returns:
            True if AMI exists and is available, False otherwise
        """
        try:
            image_details = self.get_image_details(image_id)
            return image_details.get('state') == 'available'
        except (ValueError, Exception):
            return False

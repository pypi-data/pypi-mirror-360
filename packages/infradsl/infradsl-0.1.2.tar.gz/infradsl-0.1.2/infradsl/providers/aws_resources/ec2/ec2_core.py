"""
EC2 Core Module

This module contains the main EC2 class with core functionality including
initialization, authentication setup, AMI detection, and the main preview/create methods.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseAwsResource
import os


class EC2Core(BaseAwsResource):
    """
    Core EC2 Instance Resource
    
    This is the main EC2 class containing core functionality for instance management.
    Additional capabilities are provided by mixins for discovery, lifecycle, and configuration.
    """

    def __init__(self, name: str):
        """
        Initialize EC2 instance resource.

        Args:
            name: Instance name (used for tagging)
        """
        super().__init__(name)

        # Core instance configuration (defaults)
        self.instance_type = 't3.micro'
        self.ami_id = None
        self.key_name = None
        self.security_groups = []
        self.subnet_id = None
        self.user_data = None
        self.instance_tags = {}

        # Extended configuration
        self.monitoring_enabled = True
        self.ebs_optimized = False
        self.associate_public_ip = True
        self.root_volume_size = 8
        self.root_volume_type = 'gp3'
        self.termination_protection = False

        # Instance state
        self.instance_id = None
        self.instance_state = None
        self.public_ip = None
        self.private_ip = None
        self.availability_zone = None

    def _initialize_managers(self):
        """Initialize EC2 managers"""
        self.ec2_client = None
        self.ec2_resource = None
        self.service_manager = None

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize EC2 clients directly using authentication service
        self.ec2_client = self.get_ec2_client()
        self.ec2_resource = self.get_ec2_resource()

        # Initialize service manager
        from ...aws_managers.service_manager import AwsServiceManager
        self.service_manager = AwsServiceManager()

        if not self.ami_id:
            # Auto-detect latest Ubuntu 22.04 LTS AMI
            self._auto_detect_ami()

    def _auto_detect_ami(self):
        """Auto-detect appropriate AMI based on region and preferences"""
        if self.ec2_client:
            try:
                # Find Ubuntu 22.04 LTS AMI
                response = self.ec2_client.describe_images(
                    Filters=[
                        {'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*']},
                        {'Name': 'owner-id', 'Values': ['099720109477']},  # Canonical
                        {'Name': 'state', 'Values': ['available']},
                    ],
                    Owners=['099720109477']
                )

                if response['Images']:
                    # Sort by creation date and get the latest
                    latest_image = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)[0]
                    self.ami_id = latest_image['ImageId']
                    print(f"🔍 Auto-detected Ubuntu 22.04 LTS AMI: {self.ami_id}")
                else:
                    # Fallback to Amazon Linux 2
                    response = self.ec2_client.describe_images(
                        Filters=[
                            {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                            {'Name': 'owner-id', 'Values': ['137112412989']},  # Amazon
                            {'Name': 'state', 'Values': ['available']},
                        ],
                        Owners=['137112412989']
                    )

                    if response['Images']:
                        latest_image = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)[0]
                        self.ami_id = latest_image['ImageId']
                        print(f"🔍 Auto-detected Amazon Linux 2 AMI: {self.ami_id}")
            except Exception as e:
                print(f"⚠️  Could not auto-detect AMI: {str(e)}")
                print("💡 Please specify ami_id manually")

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, updated, or removed"""
        self._ensure_authenticated()

        # Import discovery methods
        from .ec2_discovery import EC2DiscoveryMixin
        discovery = EC2DiscoveryMixin()
        discovery.ec2_client = self.ec2_client
        discovery.name = self.name

        # Discover existing instances to determine what will happen
        existing_instances = discovery._discover_existing_instances()
        
        # Determine what will happen
        instance_exists = self.name in existing_instances
        to_create = [] if instance_exists else [self.name]
        to_keep = [self.name] if instance_exists else []
        to_remove = [name for name in existing_instances.keys() if name != self.name]

        # Print simple header without formatting
        print(f"🔍 EC2 Instance Preview")

        # Show infrastructure changes (only actionable changes)
        changes_needed = to_create or to_remove
        
        if changes_needed:
            print(f"📋 Infrastructure Changes:")
            
            if to_create:
                print(f"🆕 INSTANCES to CREATE:  {', '.join(to_create)}")
                # Show details about instance being created
                print(f"   ╭─ 💻 {self.name}")
                print(f"   ├─ 🏗️  Type: {self.instance_type}")
                print(f"   ├─ 💿 AMI: {self.ami_id or 'Auto-detect Ubuntu 22.04 LTS'}")
                print(f"   ├─ 🔑 Key: {self.key_name or 'None (SSH disabled)'}")
                print(f"   ├─ 🌐 Public IP: {self.associate_public_ip}")
                print(f"   ├─ 💾 Volume: {self.root_volume_size} GB ({self.root_volume_type})")
                print(f"   ├─ 🔒 Security: {len(self.security_groups or [])} group(s)")
                print(f"   ├─ 📊 Monitoring: {self.monitoring_enabled}")
                if self.user_data:
                    print(f"   ├─ 📜 User Data: Configured")
                print(f"   ╰─ 💰 Est. Cost: {self._estimate_monthly_cost()}")
                print()
                
            if to_remove:
                print(f"🗑️  INSTANCES to REMOVE:")
                # Show details about instances being removed
                for instance_name in to_remove:
                    instance_info = existing_instances.get(instance_name)
                    if instance_info:
                        instance_type = instance_info.get('instance_type', 'unknown')
                        state = instance_info.get('state', 'unknown')
                        public_ip = instance_info.get('public_ip', 'none')
                        
                        # Pretty format with box drawing
                        print(f"   ╭─ 💻 {instance_name}")
                        print(f"   ├─ 🏗️  Type: {instance_type}")
                        print(f"   ├─ 🔄 State: {state}")
                        print(f"   ├─ 🌐 Public IP: {public_ip}")
                        print(f"   ╰─ ⚠️  Will terminate instance")
                        print()
        else:
            print(f"✨ No changes needed - infrastructure matches configuration")

        # Show unchanged instances summary
        if to_keep:
            print(f"📋 Unchanged: {len(to_keep)} instance(s) remain the same")

        # Register for preview summary
        try:
            from ....cli.commands import register_preview_resource
            if to_create:
                for instance_name in to_create:
                    register_preview_resource(
                        provider='aws',
                        resource_type='ec2',
                        name=instance_name,
                        details=[
                            f"Type: {self.instance_type}",
                            f"AMI: {self.ami_id or 'Auto-detect Ubuntu 22.04 LTS'}",
                            f"Cost: {self._estimate_monthly_cost()}"
                        ]
                    )
        except ImportError:
            pass  # CLI module not available

        return {
            'resource_type': 'aws_ec2_instance',
            'name': self.name,
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'existing_instances': existing_instances,
            'instance_type': self.instance_type,
            'ami_id': self.ami_id or 'Will auto-detect Ubuntu 22.04 LTS',
            'key_name': self.key_name or 'None (SSH access disabled)',
            'security_groups': self.security_groups or ['Default VPC security group'],
            'subnet_id': self.subnet_id or 'Default VPC subnet',
            'monitoring_enabled': self.monitoring_enabled,
            'associate_public_ip': self.associate_public_ip,
            'root_volume': {
                'size': f"{self.root_volume_size} GB",
                'type': self.root_volume_type
            },
            'termination_protection': self.termination_protection,
            'estimated_cost': self._estimate_monthly_cost(),
            'tags': self._get_all_tags()
        }

    def create(self) -> Dict[str, Any]:
        """Create/update EC2 instance and remove any that are no longer needed"""
        self._ensure_authenticated()

        # Import discovery methods
        from .ec2_discovery import EC2DiscoveryMixin
        discovery = EC2DiscoveryMixin()
        discovery.ec2_client = self.ec2_client
        discovery.name = self.name

        # Discover existing instances to determine what changes are needed
        existing_instances = discovery._discover_existing_instances()
        instance_exists = self.name in existing_instances
        to_create = [] if instance_exists else [self.name]
        to_remove = [name for name in existing_instances.keys() if name != self.name]

        # Show infrastructure changes
        print(f"\n🔍 EC2 Instance")

        changes_needed = to_create or to_remove
        if changes_needed:
            print(f"📋 Infrastructure Changes:")
            
            if to_create:
                print(f"🆕 INSTANCES to CREATE:  {', '.join(to_create)}")
                
            if to_remove:
                print(f"🗑️  INSTANCES to REMOVE:")
                # Show details about instances being removed
                for instance_name in to_remove:
                    instance_info = existing_instances.get(instance_name)
                    if instance_info:
                        instance_type = instance_info.get('instance_type', 'unknown')
                        state = instance_info.get('state', 'unknown')
                        public_ip = instance_info.get('public_ip', 'none')
                        
                        # Pretty format with box drawing
                        print(f"   ╭─ 💻 {instance_name}")
                        print(f"   ├─ 🏗️  Type: {instance_type}")
                        print(f"   ├─ 🔄 State: {state}")
                        print(f"   ├─ 🌐 Public IP: {public_ip}")
                        print(f"   ╰─ ⚠️  Will terminate instance")
                        print()
        else:
            print(f"✨ No changes needed - infrastructure matches configuration")

        try:
            # Remove instances that are no longer needed
            for instance_name in to_remove:
                instance_info = existing_instances.get(instance_name)
                if instance_info and instance_info.get('instance_id'):
                    print(f"🗑️  Removing instance: {instance_name}")
                    try:
                        # Terminate the instance
                        self.ec2_client.terminate_instances(InstanceIds=[instance_info['instance_id']])
                        print(f"✅ Instance terminated successfully: {instance_name}")
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to terminate instance {instance_name}: {str(e)}")

            # Create/update the instance that is in the configuration
            if instance_exists:
                # Instance exists, update it
                existing_instance = existing_instances[self.name]
                result = self._update_existing_instance(existing_instance)
            else:
                # Instance doesn't exist, create it
                result = self._create_new_instance()

            return result

        except Exception as e:
            print(f"❌ Error managing EC2 instance: {str(e)}")
            raise

    def _update_existing_instance(self, existing_instance: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing instance (placeholder - implement in lifecycle module)"""
        from .ec2_lifecycle import EC2LifecycleMixin
        lifecycle = EC2LifecycleMixin()
        lifecycle.ec2_client = self.ec2_client
        lifecycle.instance_tags = self.instance_tags
        lifecycle.name = self.name
        return lifecycle._update_existing_instance(existing_instance)

    def _create_new_instance(self) -> Dict[str, Any]:
        """Create a new instance (placeholder - implement in lifecycle module)"""
        from .ec2_lifecycle import EC2LifecycleMixin
        lifecycle = EC2LifecycleMixin()
        lifecycle.ec2_client = self.ec2_client
        lifecycle.ami_id = self.ami_id
        lifecycle.instance_type = self.instance_type
        lifecycle.key_name = self.key_name
        lifecycle.security_groups = self.security_groups
        lifecycle.subnet_id = self.subnet_id
        lifecycle.user_data = self.user_data
        lifecycle.associate_public_ip = self.associate_public_ip
        lifecycle.monitoring_enabled = self.monitoring_enabled
        lifecycle.ebs_optimized = self.ebs_optimized
        lifecycle.root_volume_size = self.root_volume_size
        lifecycle.root_volume_type = self.root_volume_type
        lifecycle.termination_protection = self.termination_protection
        lifecycle.instance_tags = self.instance_tags
        lifecycle.name = self.name
        return lifecycle._create_new_instance()

    def _get_all_tags(self) -> Dict[str, str]:
        """Get all tags for the instance"""
        all_tags = {
            'Name': self.name,
            'ManagedBy': 'InfraDSL',
            'Environment': os.getenv('ENVIRONMENT', 'development')
        }
        all_tags.update(self.instance_tags)
        return all_tags

    def _estimate_monthly_cost(self) -> str:
        """Estimate monthly cost for the instance"""
        # Simplified cost estimation based on instance type
        cost_mapping = {
            't3.micro': 8.47,
            't3.small': 16.94,
            't3.medium': 33.89,
            't3.large': 67.78,
            'c5.large': 78.84,
            'r5.large': 109.50
        }
        
        base_cost = cost_mapping.get(self.instance_type, 50.0)
        
        # Add storage cost (roughly $0.10 per GB per month for gp3)
        storage_cost = self.root_volume_size * 0.08
        
        total_cost = base_cost + storage_cost
        return f"${total_cost:.2f}/month"
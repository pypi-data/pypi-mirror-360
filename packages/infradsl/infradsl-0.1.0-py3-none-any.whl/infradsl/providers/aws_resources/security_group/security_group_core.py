from typing import Dict, Any
from ..base_resource import BaseAwsResource

class SecurityGroupCore(BaseAwsResource):
    """
    Core SecurityGroup class with main attributes and authentication logic.
    """
    def __init__(self, name: str):
        super().__init__(name)
        # Core attributes (to be filled in)
        self.group_id = None
        self.group_name = name
        self.group_description = f"Security group managed by InfraDSL for {name}"
        self.vpc_id = None
        self.ingress_rules = []
        self.egress_rules = []
        self.tags = {}
        self.security_group_exists = False
        self.security_group_manager = None

    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        # Security group manager will be initialized after authentication
        self.security_group_manager = None

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize the EC2 client for security group management
        self.ec2_client = self.get_ec2_client()
        self.ec2_resource = self.get_ec2_resource()
    
    def create(self):
        """Create/update security group - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .security_group_lifecycle import SecurityGroupLifecycleMixin
        # Call the lifecycle mixin's create method
        return SecurityGroupLifecycleMixin.create(self)

    def destroy(self):
        """Destroy security group - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .security_group_lifecycle import SecurityGroupLifecycleMixin
        # Call the lifecycle mixin's destroy method
        return SecurityGroupLifecycleMixin.destroy(self)

    def preview(self):
        """Preview security group configuration - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .security_group_lifecycle import SecurityGroupLifecycleMixin
        # Call the lifecycle mixin's preview method
        return SecurityGroupLifecycleMixin.preview(self)

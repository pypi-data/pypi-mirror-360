"""
EC2 Module

This module contains the refactored EC2 components that were previously
in a single large ec2.py file. The components are now organized as:

- ec2_core.py: Core EC2 class with main functionality (~350 lines)
- ec2_discovery.py: Instance discovery and management (~200 lines)
- ec2_lifecycle.py: Lifecycle operations (start/stop/destroy) (~250 lines) 
- ec2_configuration.py: Chainable configuration methods (~400 lines)

This modular structure makes the EC2 resource more maintainable and testable.
The main EC2 class combines all functionality through multiple inheritance.
"""

from .ec2_core import EC2Core
from .ec2_discovery import EC2DiscoveryMixin
from .ec2_lifecycle import EC2LifecycleMixin
from .ec2_configuration import EC2ConfigurationMixin


from typing import Dict, Any

class EC2(EC2Core, EC2DiscoveryMixin, EC2LifecycleMixin, EC2ConfigurationMixin):
    """
    Complete EC2 Instance Resource
    
    This class combines all EC2 functionality through multiple inheritance:
    - EC2Core: Main class with authentication and core methods
    - EC2DiscoveryMixin: Instance discovery and management
    - EC2LifecycleMixin: Start, stop, create, destroy operations
    - EC2ConfigurationMixin: Chainable configuration methods
    
    Usage:
        instance = (AWS.EC2("web-server")
                   .t3_micro()
                   .ubuntu()
                   .key_pair("my-key")
                   .allow_ssh()
                   .allow_http()
                   .create())
    """
    
    def __init__(self, name: str):
        """Initialize EC2 instance with all capabilities"""
        # Initialize the core class, which will call all parent __init__ methods
        super().__init__(name)

    def create(self) -> Dict[str, Any]:
        return super().create()

    def destroy(self) -> Dict[str, Any]:
        return super().destroy()

    def preview(self) -> Dict[str, Any]:
        return super().preview()


# Export the main EC2 class
__all__ = ['EC2']
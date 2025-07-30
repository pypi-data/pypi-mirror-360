from typing import Dict, Any

from .security_group_core import SecurityGroupCore
from .security_group_discovery import SecurityGroupDiscoveryMixin
from .security_group_lifecycle import SecurityGroupLifecycleMixin
from .security_group_configuration import SecurityGroupConfigurationMixin


class SecurityGroup(SecurityGroupCore, SecurityGroupDiscoveryMixin, SecurityGroupLifecycleMixin, SecurityGroupConfigurationMixin):
    """
    Complete AWS SecurityGroup Resource
    
    This class combines all SecurityGroup functionality through multiple inheritance.
    """
    def __init__(self, name: str):
        """Initialize SecurityGroup with all capabilities"""
        super().__init__(name)


__all__ = ['SecurityGroup']
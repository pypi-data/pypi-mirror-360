"""
API Gateway Module

This module contains the refactored API Gateway components that were previously
in a single large api_gateway.py file. The components are now organized as:

- api_gateway_core.py: Core API Gateway class with main functionality
- api_gateway_discovery.py: API Gateway discovery and management
- api_gateway_lifecycle.py: Lifecycle operations (create/update/destroy)
- api_gateway_configuration.py: Chainable configuration methods

This modular structure makes the API Gateway resource more maintainable and testable.
The main APIGateway class combines all functionality through multiple inheritance.
"""

from .api_gateway_core import APIGatewayCore
from .api_gateway_discovery import APIGatewayDiscoveryMixin
from .api_gateway_lifecycle import APIGatewayLifecycleMixin
from .api_gateway_configuration import APIGatewayConfigurationMixin


class APIGateway(APIGatewayCore, APIGatewayDiscoveryMixin, APIGatewayLifecycleMixin, APIGatewayConfigurationMixin):
    """
    Complete AWS API Gateway Resource
    
    This class combines all API Gateway functionality through multiple inheritance.
    """
    
    def __init__(self, name: str):
        """Initialize API Gateway with all capabilities"""
        super().__init__(name)


# Export the main APIGateway class
__all__ = ['APIGateway']

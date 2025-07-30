# Import the comprehensive ECS class that includes all features
from .ecs import ECS

# Also export the individual components for advanced usage
from .ecs_core import ECSCore
from .ecs_discovery import ECSDiscoveryMixin
from .ecs_lifecycle import ECSLifecycleMixin
from .ecs_configuration import ECSConfigurationMixin

__all__ = ['ECS', 'ECSCore', 'ECSDiscoveryMixin', 'ECSLifecycleMixin', 'ECSConfigurationMixin']

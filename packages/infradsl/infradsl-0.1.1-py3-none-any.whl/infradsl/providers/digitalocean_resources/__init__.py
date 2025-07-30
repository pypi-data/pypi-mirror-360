# DigitalOcean Resources Package

from .base_resource import BaseDigitalOceanResource
from .function import Function
from .database import Database
from .spaces_cdn import SpacesCDN
from .vpc import VPC
from .monitoring import Monitoring

# New modular architecture implementations
from .database_new import Database as DatabaseNew
from .load_balancer_new import LoadBalancer

__all__ = [
    'BaseDigitalOceanResource',
    'Function',
    'Database',
    'DatabaseNew',
    'LoadBalancer', 
    'SpacesCDN',
    'VPC',
    'Monitoring'
] 
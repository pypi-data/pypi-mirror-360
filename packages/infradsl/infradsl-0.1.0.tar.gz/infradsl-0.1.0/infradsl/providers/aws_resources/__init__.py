"""
AWS Resources

This module contains AWS resource classes that provide a Rails-like DSL for managing
AWS cloud infrastructure. Each resource class offers intuitive methods for creating,
managing, and destroying AWS resources with intelligent defaults and convention over
configuration principles.
"""

from .base_resource import BaseAwsResource
from .ec2 import EC2
from .lambda_function import Lambda
from .s3 import S3
from .rds import RDS
from .ecs import ECS
from .route53 import Route53
from .cloudfront import CloudFront
from .load_balancer import LoadBalancer
from .api_gateway import APIGateway
from .sqs import SQS
from .sns import SNS
from .certificate_manager import CertificateManager
from .secrets_manager import SecretsManager
from .elasticache import ElastiCache
from .domain_registration import DomainRegistration

__all__ = [
    'BaseAwsResource',
    'EC2',
    'Lambda', 
    'S3',
    'RDS',
    'ECS',
    'Route53',
    'CloudFront',
    'LoadBalancer',
    'APIGateway',
    'SQS',
    'SNS',
    'CertificateManager',
    'SecretsManager',
    'ElastiCache',
    'DomainRegistration'
]

"""
AWS Managers

Collection of AWS service managers providing Rails-like interfaces
for AWS resource management. Now with modular structure for better
maintainability and extensibility.
"""

from .aws_client import AwsClient
from .ec2 import EC2Manager
from .s3 import S3Manager
from .cloudfront import CloudFrontManager

__all__ = [
    'AwsClient',
    'EC2Manager',
    'S3Manager',
    'CloudFrontManager'
]

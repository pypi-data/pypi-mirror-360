"""
AWS RDS Module

Modular RDS management components for AWS infrastructure.
Provides a clean separation of concerns for database instance management.
"""

from .manager import RDSManager

__all__ = [
    'RDSManager'
]

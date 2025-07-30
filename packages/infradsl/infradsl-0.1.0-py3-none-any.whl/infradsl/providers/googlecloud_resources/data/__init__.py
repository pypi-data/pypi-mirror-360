"""
Data Resources Package
"""

# Use the new modular implementation
from .bigquery_new import BigQuery

__all__ = [
    'BigQuery',
]
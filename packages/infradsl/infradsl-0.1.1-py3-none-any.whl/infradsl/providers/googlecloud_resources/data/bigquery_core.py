"""
GCP BigQuery Core Implementation

Core attributes and authentication for Google Cloud BigQuery.
Provides the foundation for the modular analytics system.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class BigQueryCore(BaseGcpResource):
    """
    Core class for Google Cloud BigQuery functionality.
    
    This class provides:
    - Basic dataset and table attributes and configuration
    - Authentication setup
    - Common utilities for BigQuery operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, dataset_name: str):
        """Initialize BigQuery core with dataset name"""
        super().__init__(dataset_name)
        
        # Core dataset attributes
        self.dataset_name = dataset_name
        self.dataset_id = dataset_name
        self.dataset_description = f"BigQuery dataset for {dataset_name}"
        self.dataset_location = "US"  # Default to multi-region US
        self.dataset_friendly_name = None
        self.dataset_resource_name = None
        
        # Dataset configuration
        self.dataset_schema_type = None  # analytics, streaming, reporting, logs
        self.dataset_labels = {}
        self.dataset_access_policies = []
        self.default_table_expiration_ms = None
        self.default_partition_expiration_ms = None
        
        # Table configurations
        self.table_configs = []
        self.current_table_config = None
        
        # State tracking
        self.dataset_exists = False
        self.dataset_created = False
        self.tables_created = []
        
        # Client references
        self.bigquery_client = None
        self.bigquery_manager = None
        
        # Cost estimation
        self.estimated_monthly_cost = "$10.00/month"
        
    def _initialize_managers(self):
        """Initialize BigQuery-specific managers"""
        self.bigquery_client = None
        self.bigquery_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            from google.cloud import bigquery
            from ...googlecloud_managers.analytics.bigquery_manager import BigQueryManager
            
            # Initialize client
            self.bigquery_client = bigquery.Client(
                project=self.project_id,
                credentials=self.gcp_client.credentials
            )
            
            # Initialize manager
            self.bigquery_manager = BigQueryManager(self.gcp_client)
            
            # Set project context
            self.project_id = self.project_id or self.gcp_client.project_id
            
            # Generate resource names
            if self.project_id:
                self.dataset_resource_name = f"projects/{self.project_id}/datasets/{self.dataset_id}"
                
        except Exception as e:
            print(f"⚠️  Failed to initialize BigQuery client: {str(e)}")
            
    def _is_valid_dataset_name(self, name: str) -> bool:
        """Check if dataset name is valid"""
        import re
        # Dataset names must contain only letters, numbers, underscores
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, name)) and 1 <= len(name) <= 1024
        
    def _is_valid_table_name(self, name: str) -> bool:
        """Check if table name is valid"""
        import re
        # Table names must contain only letters, numbers, underscores
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, name)) and 1 <= len(name) <= 1024
        
    def _is_valid_location(self, location: str) -> bool:
        """Check if BigQuery location is valid"""
        valid_locations = [
            "US", "EU",  # Multi-regions
            "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west3", "us-west4",
            "europe-north1", "europe-west1", "europe-west2", "europe-west3", "europe-west4", "europe-west6",
            "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2", "asia-northeast3",
            "asia-south1", "asia-southeast1", "asia-southeast2", "australia-southeast1"
        ]
        return location in valid_locations
        
    def _validate_dataset_config(self, config: Dict[str, Any]) -> bool:
        """Validate dataset configuration"""
        required_fields = ["dataset_id"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate dataset name format
        if not self._is_valid_dataset_name(config["dataset_id"]):
            return False
            
        # Validate location if specified
        if config.get("location") and not self._is_valid_location(config["location"]):
            return False
            
        return True
        
    def _get_dataset_type_from_config(self) -> str:
        """Determine dataset type from configuration"""
        if self.dataset_schema_type:
            return self.dataset_schema_type
        elif any(keyword in self.dataset_name.lower() for keyword in ['analytics', 'dwh', 'warehouse']):
            return "analytics"
        elif any(keyword in self.dataset_name.lower() for keyword in ['stream', 'realtime', 'events']):
            return "streaming"
        elif any(keyword in self.dataset_name.lower() for keyword in ['report', 'bi', 'dashboard']):
            return "reporting"
        elif any(keyword in self.dataset_name.lower() for keyword in ['log', 'audit', 'monitor']):
            return "logs"
        else:
            return "general"
            
    def _estimate_bigquery_cost(self) -> float:
        """Estimate monthly cost for BigQuery usage"""
        # BigQuery pricing (simplified)
        
        # Storage cost: $0.02 per GB per month (active), $0.01 per GB per month (long-term)
        estimated_storage_gb = 100  # Default estimate
        storage_cost = estimated_storage_gb * 0.02
        
        # Query cost: $5 per TB processed
        estimated_query_tb = 1  # Default estimate
        query_cost = estimated_query_tb * 5
        
        # Streaming cost: $0.01 per 200MB
        streaming_cost = 0  # No streaming by default
        
        # Table count multiplier
        table_count = len(self.table_configs) if self.table_configs else 1
        if table_count > 10:
            storage_cost *= 1.2  # Slight increase for many tables
            
        # Schema type optimization
        if self.dataset_schema_type == "analytics":
            query_cost *= 2  # Analytics tends to process more data
        elif self.dataset_schema_type == "streaming":
            streaming_cost = 10  # Estimate streaming costs
        elif self.dataset_schema_type == "logs":
            storage_cost *= 1.5  # Logs tend to use more storage
            
        total_cost = storage_cost + query_cost + streaming_cost
        
        # Minimum charge
        if total_cost < 1.0:
            total_cost = 1.0
            
        return total_cost
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of BigQuery dataset from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Check if dataset exists
            try:
                dataset = self.bigquery_client.get_dataset(self.dataset_id)
                dataset_exists = True
            except Exception:
                dataset_exists = False
                
            if not dataset_exists:
                return {
                    "exists": False,
                    "dataset_id": self.dataset_id,
                    "dataset_resource_name": self.dataset_resource_name
                }
                
            # Get dataset details
            current_state = {
                "exists": True,
                "dataset_id": self.dataset_id,
                "dataset_resource_name": dataset.self_link if hasattr(dataset, 'self_link') else None,
                "location": dataset.location,
                "description": dataset.description or "",
                "friendly_name": dataset.friendly_name or "",
                "labels": dict(dataset.labels) if dataset.labels else {},
                "created": dataset.created.isoformat() if hasattr(dataset, 'created') else None,
                "modified": dataset.modified.isoformat() if hasattr(dataset, 'modified') else None,
                "default_table_expiration_ms": dataset.default_table_expiration_ms,
                "default_partition_expiration_ms": dataset.default_partition_expiration_ms,
                "tables": [],
                "table_count": 0
            }
            
            # Get table information
            try:
                tables = []
                for table in self.bigquery_client.list_tables(dataset):
                    table_info = {
                        "table_id": table.table_id,
                        "table_type": table.table_type,
                        "created": table.created.isoformat() if hasattr(table, 'created') else None,
                        "modified": table.modified.isoformat() if hasattr(table, 'modified') else None,
                        "num_rows": table.num_rows or 0,
                        "num_bytes": table.num_bytes or 0,
                        "labels": dict(table.labels) if table.labels else {}
                    }
                    tables.append(table_info)
                    
                current_state["tables"] = tables
                current_state["table_count"] = len(tables)
                
            except Exception as e:
                print(f"⚠️  Warning: Failed to get table information: {str(e)}")
                
            return current_state
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch BigQuery state: {str(e)}")
            return {
                "exists": False,
                "dataset_id": self.dataset_id,
                "dataset_resource_name": self.dataset_resource_name,
                "error": str(e)
            }
            
    def _discover_existing_datasets(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing datasets in the project"""
        existing_datasets = {}
        
        try:
            for dataset in self.bigquery_client.list_datasets():
                dataset_id = dataset.dataset_id
                
                try:
                    # Get basic dataset information
                    dataset_info = {
                        "dataset_id": dataset_id,
                        "location": dataset.location,
                        "description": dataset.description or "",
                        "friendly_name": dataset.friendly_name or "",
                        "labels": dict(dataset.labels) if dataset.labels else {},
                        "created": dataset.created.isoformat() if hasattr(dataset, 'created') else None,
                        "default_table_expiration_ms": dataset.default_table_expiration_ms,
                        "table_count": 0,
                        "tables": []
                    }
                    
                    # Get table count
                    try:
                        tables = list(self.bigquery_client.list_tables(dataset))
                        dataset_info["table_count"] = len(tables)
                        dataset_info["tables"] = [
                            {
                                "table_id": table.table_id,
                                "table_type": table.table_type,
                                "num_rows": table.num_rows or 0,
                                "num_bytes": table.num_bytes or 0
                            }
                            for table in tables[:10]  # Limit to first 10 tables
                        ]
                    except Exception:
                        dataset_info["table_count"] = 0
                        
                    existing_datasets[dataset_id] = dataset_info
                    
                except Exception as e:
                    print(f"⚠️  Failed to get details for dataset {dataset_id}: {str(e)}")
                    existing_datasets[dataset_id] = {
                        "dataset_id": dataset_id,
                        "error": str(e)
                    }
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing datasets: {str(e)}")
            
        return existing_datasets


class TableConfig:
    """Configuration class for BigQuery tables"""
    
    def __init__(self, table_id: str, dataset_id: str):
        self.table_id = table_id
        self.dataset_id = dataset_id
        
        # Schema configuration
        self.table_schema = None
        self.schema_type = None  # predefined schema type
        self.table_type = "table"  # table, view, external
        
        # Performance optimization
        self.partition_field = None
        self.partition_type = "DAY"  # DAY, HOUR, MONTH, YEAR
        self.clustering_fields = []
        self.require_partition_filter = False
        
        # Metadata
        self.description = None
        self.friendly_name = None
        self.labels = {}
        
        # Expiration settings
        self.expiration_ms = None
        self.partition_expiration_days = None
        
        # External table settings
        self.source_uris = []
        self.source_format = None
        self.compression = None
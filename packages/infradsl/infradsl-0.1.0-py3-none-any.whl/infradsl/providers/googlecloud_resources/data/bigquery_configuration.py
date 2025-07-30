"""
GCP BigQuery Configuration Mixin

Chainable configuration methods for Google Cloud BigQuery.
Provides Rails-like method chaining for fluent analytics configuration.
"""

from typing import Dict, Any, List, Optional, Union
from .bigquery_core import TableConfig


class BigQueryConfigurationMixin:
    """
    Mixin for BigQuery configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Dataset configuration (location, description, labels)
    - Table creation and schema configuration
    - Performance optimization (partitioning, clustering)
    - Common analytics patterns and schemas
    """
    
    # Dataset configuration methods
    def location(self, location: str):
        """Set dataset location (e.g., 'US', 'EU', 'us-central1')"""
        if not self._is_valid_location(location):
            print(f"⚠️  Warning: Invalid location '{location}'. Use valid BigQuery regions.")
        self.dataset_location = location
        return self
        
    def description(self, description: str):
        """Set dataset description"""
        self.dataset_description = description
        return self
        
    def friendly_name(self, name: str):
        """Set user-friendly dataset name"""
        self.dataset_friendly_name = name
        return self
        
    def project(self, project_id: str):
        """Set project ID for BigQuery operations - Rails convenience"""
        self.project_id = project_id
        if self.project_id:
            self.dataset_resource_name = f"projects/{self.project_id}/datasets/{self.dataset_id}"
        return self
        
    # Dataset labels and metadata
    def labels(self, labels: Dict[str, str]):
        """Add labels to the dataset"""
        self.dataset_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.dataset_labels[key] = value
        return self
        
    # Dataset expiration settings
    def default_table_expiration(self, days: int):
        """Set default table expiration in days"""
        self.default_table_expiration_ms = days * 24 * 60 * 60 * 1000
        return self
        
    def default_partition_expiration(self, days: int):
        """Set default partition expiration in days"""
        self.default_partition_expiration_ms = days * 24 * 60 * 60 * 1000
        return self
        
    # Rails-like dataset conventions
    def analytics_dataset(self):
        """Configure for analytics workloads (Rails convention)"""
        self.dataset_schema_type = "analytics"
        self.dataset_description = "Analytics data warehouse with optimized partitioning"
        self.dataset_location = "US"  # Multi-region for analytics
        self.dataset_labels.update({
            "purpose": "analytics",
            "workload": "batch",
            "optimization": "query-performance"
        })
        return self
        
    def streaming_dataset(self):
        """Configure for streaming data (Rails convention)"""
        self.dataset_schema_type = "streaming"
        self.dataset_description = "Real-time streaming data with hourly partitioning"
        self.dataset_labels.update({
            "purpose": "streaming",
            "workload": "realtime",
            "optimization": "ingestion-speed"
        })
        return self
        
    def reporting_dataset(self):
        """Configure for reporting workloads (Rails convention)"""
        self.dataset_schema_type = "reporting"
        self.dataset_description = "Business reporting dataset with monthly partitions"
        self.dataset_labels.update({
            "purpose": "reporting",
            "workload": "batch",
            "optimization": "cost-efficient"
        })
        return self
        
    def logs_dataset(self):
        """Configure for log storage (Rails convention)"""
        self.dataset_schema_type = "logs"
        self.dataset_description = "Application and system logs with automatic expiration"
        self.default_table_expiration_ms = 90 * 24 * 60 * 60 * 1000  # 90 days
        self.dataset_labels.update({
            "purpose": "logs",
            "workload": "ingestion",
            "retention": "90-days"
        })
        return self
        
    def data_lake_dataset(self):
        """Configure for data lake storage (Rails convention)"""
        self.dataset_schema_type = "data_lake"
        self.dataset_description = "Data lake with external tables and federated queries"
        self.dataset_labels.update({
            "purpose": "data_lake",
            "workload": "exploration",
            "optimization": "storage-cost"
        })
        return self
        
    def machine_learning_dataset(self):
        """Configure for ML workloads (Rails convention)"""
        self.dataset_schema_type = "ml"
        self.dataset_description = "Machine learning feature store and training data"
        self.dataset_labels.update({
            "purpose": "machine_learning",
            "workload": "training",
            "optimization": "feature-engineering"
        })
        return self
        
    # Table creation methods
    def table(self, table_name: str, schema: Optional[Union[str, List[Dict[str, Any]]]] = None):
        """
        Add a table to the dataset.
        
        Args:
            table_name: Name of the table
            schema: Either a predefined schema type ('web_analytics', 'user_events', etc.)
                   or a custom schema definition
        """
        if not self._is_valid_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")
            
        table_config = TableConfig(
            table_id=table_name,
            dataset_id=self.dataset_id
        )
        
        if isinstance(schema, str):
            # Predefined schema type
            table_config.schema_type = schema
            table_config.table_schema = self._get_predefined_schema(schema)
        elif isinstance(schema, list):
            # Custom schema
            table_config.table_schema = schema
            
        self.table_configs.append(table_config)
        self.current_table_config = table_config
        return self
        
    # Predefined table types with schemas
    def web_analytics_table(self, table_name: str = "page_views"):
        """Create web analytics table with predefined schema (Rails convention)"""
        schema = [
            {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "Event timestamp"},
            {"name": "date", "type": "DATE", "mode": "REQUIRED", "description": "Event date for partitioning"},
            {"name": "user_id", "type": "STRING", "mode": "NULLABLE", "description": "User identifier"},
            {"name": "session_id", "type": "STRING", "mode": "NULLABLE", "description": "Session identifier"},
            {"name": "page_url", "type": "STRING", "mode": "REQUIRED", "description": "Page URL"},
            {"name": "page_title", "type": "STRING", "mode": "NULLABLE", "description": "Page title"},
            {"name": "referrer", "type": "STRING", "mode": "NULLABLE", "description": "Referrer URL"},
            {"name": "user_agent", "type": "STRING", "mode": "NULLABLE", "description": "User agent string"},
            {"name": "ip_address", "type": "STRING", "mode": "NULLABLE", "description": "IP address"},
            {"name": "country", "type": "STRING", "mode": "NULLABLE", "description": "Country"},
            {"name": "device_type", "type": "STRING", "mode": "NULLABLE", "description": "Device type"},
            {"name": "browser", "type": "STRING", "mode": "NULLABLE", "description": "Browser"},
            {"name": "utm_source", "type": "STRING", "mode": "NULLABLE", "description": "UTM source"},
            {"name": "utm_medium", "type": "STRING", "mode": "NULLABLE", "description": "UTM medium"},
            {"name": "utm_campaign", "type": "STRING", "mode": "NULLABLE", "description": "UTM campaign"}
        ]
        
        return (self.table(table_name, schema)
                .partition_by("date")
                .cluster_by(["user_id", "page_url"])
                .table_labels({"table_type": "web_analytics"}))
        
    def user_events_table(self, table_name: str = "events"):
        """Create user events table with predefined schema (Rails convention)"""
        schema = [
            {"name": "event_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "Event timestamp"},
            {"name": "date", "type": "DATE", "mode": "REQUIRED", "description": "Event date for partitioning"},
            {"name": "user_id", "type": "STRING", "mode": "NULLABLE", "description": "User identifier"},
            {"name": "session_id", "type": "STRING", "mode": "NULLABLE", "description": "Session identifier"},
            {"name": "event_name", "type": "STRING", "mode": "REQUIRED", "description": "Event name"},
            {"name": "event_category", "type": "STRING", "mode": "NULLABLE", "description": "Event category"},
            {"name": "event_action", "type": "STRING", "mode": "NULLABLE", "description": "Event action"},
            {"name": "event_label", "type": "STRING", "mode": "NULLABLE", "description": "Event label"},
            {"name": "event_value", "type": "NUMERIC", "mode": "NULLABLE", "description": "Event value"},
            {"name": "properties", "type": "JSON", "mode": "NULLABLE", "description": "Event properties"},
            {"name": "platform", "type": "STRING", "mode": "NULLABLE", "description": "Platform"},
            {"name": "app_version", "type": "STRING", "mode": "NULLABLE", "description": "App version"},
            {"name": "device_type", "type": "STRING", "mode": "NULLABLE", "description": "Device type"},
            {"name": "country", "type": "STRING", "mode": "NULLABLE", "description": "Country"}
        ]
        
        return (self.table(table_name, schema)
                .partition_by("date")
                .cluster_by(["user_id", "event_name"])
                .table_labels({"table_type": "user_events"}))
        
    def ecommerce_table(self, table_name: str = "transactions"):
        """Create ecommerce table with predefined schema (Rails convention)"""
        schema = [
            {"name": "transaction_id", "type": "STRING", "mode": "REQUIRED", "description": "Transaction ID"},
            {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "Transaction timestamp"},
            {"name": "date", "type": "DATE", "mode": "REQUIRED", "description": "Transaction date for partitioning"},
            {"name": "user_id", "type": "STRING", "mode": "NULLABLE", "description": "User identifier"},
            {"name": "customer_id", "type": "STRING", "mode": "NULLABLE", "description": "Customer identifier"},
            {"name": "product_id", "type": "STRING", "mode": "REQUIRED", "description": "Product identifier"},
            {"name": "product_name", "type": "STRING", "mode": "NULLABLE", "description": "Product name"},
            {"name": "product_category", "type": "STRING", "mode": "NULLABLE", "description": "Product category"},
            {"name": "product_brand", "type": "STRING", "mode": "NULLABLE", "description": "Product brand"},
            {"name": "quantity", "type": "INTEGER", "mode": "REQUIRED", "description": "Quantity purchased"},
            {"name": "unit_price", "type": "NUMERIC", "mode": "REQUIRED", "description": "Unit price"},
            {"name": "total_amount", "type": "NUMERIC", "mode": "REQUIRED", "description": "Total amount"},
            {"name": "currency", "type": "STRING", "mode": "REQUIRED", "description": "Currency code"},
            {"name": "payment_method", "type": "STRING", "mode": "NULLABLE", "description": "Payment method"},
            {"name": "country", "type": "STRING", "mode": "NULLABLE", "description": "Country"}
        ]
        
        return (self.table(table_name, schema)
                .partition_by("date")
                .cluster_by(["user_id", "product_id"])
                .table_labels({"table_type": "ecommerce"}))
        
    def logs_table(self, table_name: str = "application_logs"):
        """Create logs table with predefined schema (Rails convention)"""
        schema = [
            {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "Log timestamp"},
            {"name": "date", "type": "DATE", "mode": "REQUIRED", "description": "Log date for partitioning"},
            {"name": "severity", "type": "STRING", "mode": "REQUIRED", "description": "Log severity"},
            {"name": "source", "type": "STRING", "mode": "REQUIRED", "description": "Log source"},
            {"name": "service", "type": "STRING", "mode": "NULLABLE", "description": "Service name"},
            {"name": "version", "type": "STRING", "mode": "NULLABLE", "description": "Service version"},
            {"name": "environment", "type": "STRING", "mode": "NULLABLE", "description": "Environment"},
            {"name": "message", "type": "STRING", "mode": "REQUIRED", "description": "Log message"},
            {"name": "logger", "type": "STRING", "mode": "NULLABLE", "description": "Logger name"},
            {"name": "thread", "type": "STRING", "mode": "NULLABLE", "description": "Thread ID"},
            {"name": "trace_id", "type": "STRING", "mode": "NULLABLE", "description": "Trace ID"},
            {"name": "span_id", "type": "STRING", "mode": "NULLABLE", "description": "Span ID"},
            {"name": "user_id", "type": "STRING", "mode": "NULLABLE", "description": "User ID"},
            {"name": "request_id", "type": "STRING", "mode": "NULLABLE", "description": "Request ID"},
            {"name": "metadata", "type": "JSON", "mode": "NULLABLE", "description": "Additional metadata"}
        ]
        
        return (self.table(table_name, schema)
                .partition_by("date")
                .cluster_by(["severity", "source"])
                .table_labels({"table_type": "logs"}))
        
    def fact_table(self, table_name: str):
        """Configure table as a fact table in star schema"""
        schema = [
            {"name": "fact_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique fact identifier"},
            {"name": "date", "type": "DATE", "mode": "REQUIRED", "description": "Fact date for partitioning"},
            {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "Fact timestamp"},
            {"name": "user_key", "type": "STRING", "mode": "NULLABLE", "description": "User dimension key"},
            {"name": "product_key", "type": "STRING", "mode": "NULLABLE", "description": "Product dimension key"},
            {"name": "time_key", "type": "STRING", "mode": "NULLABLE", "description": "Time dimension key"},
            {"name": "geography_key", "type": "STRING", "mode": "NULLABLE", "description": "Geography dimension key"},
            {"name": "measure_1", "type": "NUMERIC", "mode": "NULLABLE", "description": "Primary measure"},
            {"name": "measure_2", "type": "NUMERIC", "mode": "NULLABLE", "description": "Secondary measure"},
            {"name": "measure_3", "type": "NUMERIC", "mode": "NULLABLE", "description": "Tertiary measure"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "Record creation timestamp"}
        ]
        
        return (self.table(table_name, schema)
                .partition_by("date")
                .cluster_by(["user_key", "product_key"])
                .table_labels({"table_type": "fact", "schema_type": "star"}))
        
    def dimension_table(self, table_name: str):
        """Configure table as a dimension table in star schema"""
        schema = [
            {"name": "dimension_key", "type": "STRING", "mode": "REQUIRED", "description": "Primary dimension key"},
            {"name": "date", "type": "DATE", "mode": "REQUIRED", "description": "Date for partitioning"},
            {"name": "name", "type": "STRING", "mode": "REQUIRED", "description": "Dimension name"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE", "description": "Dimension description"},
            {"name": "category", "type": "STRING", "mode": "NULLABLE", "description": "Dimension category"},
            {"name": "attributes", "type": "JSON", "mode": "NULLABLE", "description": "Additional attributes"},
            {"name": "is_active", "type": "BOOLEAN", "mode": "REQUIRED", "description": "Whether dimension is active"},
            {"name": "effective_from", "type": "DATE", "mode": "REQUIRED", "description": "Effective from date"},
            {"name": "effective_to", "type": "DATE", "mode": "NULLABLE", "description": "Effective to date"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "Record creation timestamp"},
            {"name": "updated_at", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "Record update timestamp"}
        ]
        
        return (self.table(table_name, schema)
                .table_labels({"table_type": "dimension", "schema_type": "star"}))
        
    # Table configuration methods (work on the current table)
    def partition_by(self, field: str, partition_type: str = "DAY"):
        """Configure table partitioning"""
        if self.current_table_config:
            self.current_table_config.partition_field = field
            self.current_table_config.partition_type = partition_type
        return self
        
    def cluster_by(self, fields: List[str]):
        """Configure table clustering"""
        if self.current_table_config:
            self.current_table_config.clustering_fields = fields
        return self
        
    def require_partition_filter(self, required: bool = True):
        """Require partition filter for queries (cost optimization)"""
        if self.current_table_config:
            self.current_table_config.require_partition_filter = required
        return self
        
    def table_description(self, description: str):
        """Set description for current table"""
        if self.current_table_config:
            self.current_table_config.description = description
        return self
        
    def table_labels(self, labels: Dict[str, str]):
        """Add labels to current table"""
        if self.current_table_config:
            if not self.current_table_config.labels:
                self.current_table_config.labels = {}
            self.current_table_config.labels.update(labels)
        return self
        
    def table_expiration(self, days: int):
        """Set expiration for current table"""
        if self.current_table_config:
            self.current_table_config.expiration_ms = days * 24 * 60 * 60 * 1000
        return self
        
    def partition_expiration(self, days: int):
        """Set partition expiration for current table"""
        if self.current_table_config:
            self.current_table_config.partition_expiration_days = days
        return self
        
    # Environment configurations
    def development(self):
        """Configure for development environment - Rails convention"""
        return (self.location("US")
                .default_table_expiration(30)  # 30 days
                .label("environment", "development")
                .label("cost-optimization", "enabled"))
                
    def staging(self):
        """Configure for staging environment - Rails convention"""
        return (self.location("US")
                .default_table_expiration(90)  # 90 days
                .label("environment", "staging")
                .label("testing", "enabled"))
                
    def production(self):
        """Configure for production environment - Rails convention"""
        return (self.location("US")
                .label("environment", "production")
                .label("backup", "enabled"))
                
    # Cost optimization patterns
    def cost_optimized(self):
        """Configure for cost optimization"""
        return (self.location("US")  # Multi-region is cost-effective for most workloads
                .default_table_expiration(365)  # 1 year retention
                .default_partition_expiration(90)  # 90 day partitions
                .label("optimization", "cost"))
                
    def performance_optimized(self):
        """Configure for performance optimization"""
        return (self.location("us-central1")  # Single region for performance
                .label("optimization", "performance"))
                
    def compliance_ready(self):
        """Configure for compliance requirements"""
        return (self.location("us-central1")  # Data residency
                .label("compliance", "required")
                .label("audit", "enabled")
                .label("retention", "7years"))
                
    # Utility methods
    def _get_predefined_schema(self, schema_type: str) -> List[Dict[str, Any]]:
        """Get predefined schema by type"""
        schemas = {
            "web_analytics": [
                {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
                {"name": "date", "type": "DATE", "mode": "REQUIRED"},
                {"name": "user_id", "type": "STRING", "mode": "NULLABLE"},
                {"name": "page_url", "type": "STRING", "mode": "REQUIRED"},
                {"name": "properties", "type": "JSON", "mode": "NULLABLE"}
            ],
            "user_events": [
                {"name": "event_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
                {"name": "date", "type": "DATE", "mode": "REQUIRED"},
                {"name": "user_id", "type": "STRING", "mode": "NULLABLE"},
                {"name": "event_name", "type": "STRING", "mode": "REQUIRED"},
                {"name": "properties", "type": "JSON", "mode": "NULLABLE"}
            ],
            "logs": [
                {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
                {"name": "date", "type": "DATE", "mode": "REQUIRED"},
                {"name": "severity", "type": "STRING", "mode": "REQUIRED"},
                {"name": "message", "type": "STRING", "mode": "REQUIRED"},
                {"name": "metadata", "type": "JSON", "mode": "NULLABLE"}
            ]
        }
        return schemas.get(schema_type, [])
"""
BigQuery Manager - Rails-like data warehouse operations

This module provides Rails-like conventions for Google BigQuery operations,
including dataset management, table creation, schema automation, and query optimization.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from ..status_reporter import GcpStatusReporter


class DatasetConfig(BaseModel):
    """Configuration for BigQuery dataset"""
    dataset_id: str
    project_id: Optional[str] = None
    location: str = "US"  # Rails-like default: US multi-region
    description: Optional[str] = None
    default_table_expiration_ms: Optional[int] = None  # No expiration by default
    default_partition_expiration_ms: Optional[int] = None
    labels: Optional[Dict[str, str]] = None

    # Rails conventions
    friendly_name: Optional[str] = None
    access_controls: List[Dict[str, str]] = []

    # Schema conventions
    schema_type: str = "custom"  # custom, web_analytics, user_events, etc.


class TableConfig(BaseModel):
    """Configuration for BigQuery table"""
    table_id: str
    dataset_id: str
    table_schema: Optional[List[Dict[str, Any]]] = None
    schema_type: str = "custom"  # Rails convention: predefined schemas
    partition_field: Optional[str] = None
    partition_type: str = "DAY"  # DAY, HOUR, MONTH, YEAR
    clustering_fields: List[str] = []
    time_partitioning: Optional[Dict[str, Any]] = None
    require_partition_filter: bool = False
    description: Optional[str] = None
    labels: Optional[Dict[str, str]] = None

    # Rails-like table types
    table_type: str = "standard"  # standard, events, logs, analytics, staging


class BigQueryManager:
    """
    Manages Google BigQuery operations with Rails-like conventions.

    Provides intelligent defaults, convention-based schemas, and
    developer-friendly abstractions for data warehouse operations.
    """

    def __init__(self, gcp_client):
        self.gcp_client = gcp_client
        self.status_reporter = GcpStatusReporter()
        self._client = None

    @property
    def bigquery_client(self) -> bigquery.Client:
        """Get authenticated BigQuery client"""
        if self._client is None:
            self._client = bigquery.Client(
                project=self.gcp_client.project,
                credentials=self.gcp_client.credentials
            )
        return self._client

    @property
    def project_id(self) -> str:
        """Get the current project ID"""
        return self.gcp_client.project

    def create_dataset(self, config: DatasetConfig) -> Dict[str, Any]:
        """
        Create a BigQuery dataset with Rails-like conventions.

        Args:
            config: Dataset configuration

        Returns:
            Dict containing dataset information
        """
        try:
            # Set project if not specified
            if not config.project_id:
                config.project_id = self.project_id

            dataset_ref = f"{config.project_id}.{config.dataset_id}"

            # Check if dataset exists
            try:
                existing_dataset = self.bigquery_client.get_dataset(dataset_ref)
                self.status_reporter.info(f"📊 Dataset '{config.dataset_id}' already exists")
                return self._dataset_to_dict(existing_dataset)
            except NotFound:
                pass  # Dataset doesn't exist, create it

            # Create dataset
            self.status_reporter.info(f"📊 Creating BigQuery dataset '{config.dataset_id}'...")

            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = config.location

            if config.description:
                dataset.description = config.description
            elif config.schema_type != "custom":
                dataset.description = f"Rails-generated {config.schema_type} dataset"

            if config.friendly_name:
                dataset.friendly_name = config.friendly_name

            if config.default_table_expiration_ms:
                dataset.default_table_expiration_ms = config.default_table_expiration_ms

            if config.default_partition_expiration_ms:
                dataset.default_partition_expiration_ms = config.default_partition_expiration_ms

            if config.labels:
                dataset.labels = config.labels

            # Apply access controls
            if config.access_controls:
                access_entries = []
                for access in config.access_controls:
                    entry = bigquery.AccessEntry(
                        role=access.get("role", "READER"),
                        entity_type=access.get("entity_type", "userByEmail"),
                        entity_id=access["entity_id"]
                    )
                    access_entries.append(entry)
                dataset.access_entries = access_entries

            created_dataset = self.bigquery_client.create_dataset(dataset)

            self.status_reporter.success(f"✅ Dataset '{config.dataset_id}' created successfully")
            return self._dataset_to_dict(created_dataset)

        except Exception as e:
            self.status_reporter.error(f"❌ Failed to create dataset '{config.dataset_id}': {str(e)}")
            raise

    def create_table(self, config: TableConfig) -> Dict[str, Any]:
        """
        Create a BigQuery table with Rails-like conventions.

        Args:
            config: Table configuration

        Returns:
            Dict containing table information
        """
        try:
            table_ref = f"{self.project_id}.{config.dataset_id}.{config.table_id}"

            # Check if table exists
            try:
                existing_table = self.bigquery_client.get_table(table_ref)
                self.status_reporter.info(f"📋 Table '{config.table_id}' already exists")
                return self._table_to_dict(existing_table)
            except NotFound:
                pass  # Table doesn't exist, create it

            self.status_reporter.info(f"📋 Creating BigQuery table '{config.table_id}'...")

            # Create table
            table = bigquery.Table(table_ref)

            # Set schema
            if config.table_schema:
                table.schema = self._build_schema_from_config(config.table_schema)
            elif config.schema_type != "custom":
                table.schema = self._get_rails_schema(config.schema_type)

            if config.description:
                table.description = config.description
            elif config.table_type != "standard":
                table.description = f"Rails-generated {config.table_type} table"

            # Configure partitioning
            if config.partition_field:
                # Check if this is a time-based field for time partitioning
                time_fields = ["date", "timestamp", "created_at", "updated_at", "event_timestamp",
                              "order_date", "signup_date", "transaction_date", "event_date",
                              "session_date", "interaction_date", "report_date", "campaign_date",
                              "conversion_date", "cohort_month", "_PARTITIONTIME"]

                if config.partition_field.lower() in [f.lower() for f in time_fields] or config.partition_field == "_PARTITIONTIME":
                    # Time-unit column partitioning
                    table.time_partitioning = bigquery.TimePartitioning(
                        type_=getattr(bigquery.TimePartitioningType, config.partition_type),
                        field=config.partition_field if config.partition_field != "_PARTITIONTIME" else None
                    )
                else:
                    # For non-time fields, skip range partitioning for now to avoid complexity
                    # Range partitioning requires specific range configuration which is advanced
                    self.status_reporter.warning(f"⚠️ Skipping range partitioning for field '{config.partition_field}' - using time partitioning instead")
                    # Default to ingestion time partitioning
                    table.time_partitioning = bigquery.TimePartitioning(
                        type_=getattr(bigquery.TimePartitioningType, config.partition_type)
                    )

                table.require_partition_filter = config.require_partition_filter

            # Configure clustering
            if config.clustering_fields:
                table.clustering_fields = config.clustering_fields

            if config.labels:
                table.labels = config.labels

            created_table = self.bigquery_client.create_table(table)

            self.status_reporter.success(f"✅ Table '{config.table_id}' created successfully")
            return self._table_to_dict(created_table)

        except Exception as e:
            self.status_reporter.error(f"❌ Failed to create table '{config.table_id}': {str(e)}")
            raise

    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """Get information about a dataset"""
        try:
            dataset_ref = f"{self.project_id}.{dataset_id}"
            dataset = self.bigquery_client.get_dataset(dataset_ref)
            return self._dataset_to_dict(dataset)
        except NotFound:
            raise ValueError(f"Dataset '{dataset_id}' not found")

    def get_table_info(self, dataset_id: str, table_id: str) -> Dict[str, Any]:
        """Get information about a table"""
        try:
            table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
            table = self.bigquery_client.get_table(table_ref)
            return self._table_to_dict(table)
        except NotFound:
            raise ValueError(f"Table '{dataset_id}.{table_id}' not found")

    def delete_dataset(self, dataset_id: str, delete_contents: bool = False) -> bool:
        """Delete a dataset"""
        try:
            dataset_ref = f"{self.project_id}.{dataset_id}"
            self.bigquery_client.delete_dataset(dataset_ref, delete_contents=delete_contents)
            self.status_reporter.success(f"✅ Dataset '{dataset_id}' deleted")
            return True
        except NotFound:
            self.status_reporter.warning(f"⚠️ Dataset '{dataset_id}' not found")
            return False
        except Exception as e:
            self.status_reporter.error(f"❌ Failed to delete dataset '{dataset_id}': {str(e)}")
            raise

    def delete_table(self, dataset_id: str, table_id: str) -> bool:
        """Delete a table"""
        try:
            table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
            self.bigquery_client.delete_table(table_ref)
            self.status_reporter.success(f"✅ Table '{dataset_id}.{table_id}' deleted")
            return True
        except NotFound:
            self.status_reporter.warning(f"⚠️ Table '{dataset_id}.{table_id}' not found")
            return False
        except Exception as e:
            self.status_reporter.error(f"❌ Failed to delete table '{dataset_id}.{table_id}': {str(e)}")
            raise

    def query(self, sql: str, job_config: Optional[bigquery.QueryJobConfig] = None) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results"""
        try:
            self.status_reporter.info("🔍 Executing BigQuery query...")

            query_job = self.bigquery_client.query(sql, job_config=job_config)
            results = query_job.result()

            # Convert to list of dictionaries
            rows = []
            for row in results:
                rows.append(dict(row))

            self.status_reporter.success(f"✅ Query completed - {len(rows)} rows returned")
            return rows

        except Exception as e:
            self.status_reporter.error(f"❌ Query failed: {str(e)}")
            raise

    def load_data_from_gcs(self, dataset_id: str, table_id: str, gcs_uri: str,
                          schema: Optional[List[Dict[str, Any]]] = None,
                          write_disposition: str = "WRITE_APPEND") -> bool:
        """Load data from Google Cloud Storage"""
        try:
            table_ref = f"{self.project_id}.{dataset_id}.{table_id}"

            job_config = bigquery.LoadJobConfig()
            job_config.source_format = bigquery.SourceFormat.CSV
            job_config.skip_leading_rows = 1  # Skip header row
            job_config.autodetect = schema is None
            job_config.write_disposition = write_disposition

            if schema:
                job_config.schema = self._build_schema_from_config(schema)

            load_job = self.bigquery_client.load_table_from_uri(
                gcs_uri, table_ref, job_config=job_config
            )

            load_job.result()  # Wait for job to complete

            self.status_reporter.success(f"✅ Data loaded into '{dataset_id}.{table_id}' from {gcs_uri}")
            return True

        except Exception as e:
            self.status_reporter.error(f"❌ Failed to load data: {str(e)}")
            raise

    def _build_schema_from_config(self, schema_config: List[Dict[str, Any]]) -> List[bigquery.SchemaField]:
        """Build BigQuery schema from configuration"""
        schema = []
        for field in schema_config:
            schema_field = bigquery.SchemaField(
                name=field["name"],
                field_type=field["type"],
                mode=field.get("mode", "NULLABLE"),
                description=field.get("description")
            )
            schema.append(schema_field)
        return schema

    def _get_rails_schema(self, schema_type: str) -> List[bigquery.SchemaField]:
        """Get predefined Rails-like schemas for common use cases"""
        schemas = {
            "web_analytics": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING"),
                bigquery.SchemaField("session_id", "STRING"),
                bigquery.SchemaField("page_url", "STRING"),
                bigquery.SchemaField("page_title", "STRING"),
                bigquery.SchemaField("referrer", "STRING"),
                bigquery.SchemaField("user_agent", "STRING"),
                bigquery.SchemaField("ip_address", "STRING"),
                bigquery.SchemaField("country", "STRING"),
                bigquery.SchemaField("device_type", "STRING"),
                bigquery.SchemaField("browser", "STRING"),
                bigquery.SchemaField("os", "STRING"),
            ],
            "user_events": [
                bigquery.SchemaField("event_timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("event_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("event_params", "JSON"),
                bigquery.SchemaField("session_id", "STRING"),
                bigquery.SchemaField("user_properties", "JSON"),
                bigquery.SchemaField("platform", "STRING"),
                bigquery.SchemaField("app_version", "STRING"),
            ],
            "logs": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("severity", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("message", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("source", "STRING"),
                bigquery.SchemaField("service", "STRING"),
                bigquery.SchemaField("labels", "JSON"),
                bigquery.SchemaField("resource", "JSON"),
                bigquery.SchemaField("trace", "STRING"),
                bigquery.SchemaField("span_id", "STRING"),
            ],
            "ecommerce": [
                bigquery.SchemaField("transaction_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING"),
                bigquery.SchemaField("product_id", "STRING"),
                bigquery.SchemaField("product_name", "STRING"),
                bigquery.SchemaField("category", "STRING"),
                bigquery.SchemaField("quantity", "INTEGER"),
                bigquery.SchemaField("price", "FLOAT"),
                bigquery.SchemaField("currency", "STRING"),
                bigquery.SchemaField("payment_method", "STRING"),
            ]
        }

        return schemas.get(schema_type, [])

    def _dataset_to_dict(self, dataset: bigquery.Dataset) -> Dict[str, Any]:
        """Convert BigQuery dataset to dictionary"""
        return {
            "dataset_id": dataset.dataset_id,
            "project": dataset.project,
            "location": dataset.location,
            "description": dataset.description,
            "friendly_name": dataset.friendly_name,
            "created": dataset.created.isoformat() if dataset.created else None,
            "modified": dataset.modified.isoformat() if dataset.modified else None,
            "labels": dict(dataset.labels) if dataset.labels else {},
            "default_table_expiration_ms": dataset.default_table_expiration_ms,
            "access_entries": len(dataset.access_entries) if dataset.access_entries else 0,
        }

    def _table_to_dict(self, table: bigquery.Table) -> Dict[str, Any]:
        """Convert BigQuery table to dictionary"""
        return {
            "table_id": table.table_id,
            "dataset_id": table.dataset_id,
            "project": table.project,
            "description": table.description,
            "created": table.created.isoformat() if table.created else None,
            "modified": table.modified.isoformat() if table.modified else None,
            "labels": dict(table.labels) if table.labels else {},
            "num_rows": table.num_rows,
            "num_bytes": table.num_bytes,
            "schema_fields": len(table.schema) if table.schema else 0,
            "partitioning": {
                "type": table.time_partitioning.type_.name if hasattr(table.time_partitioning.type_, 'name') else str(table.time_partitioning.type_) if table.time_partitioning else None,
                "field": table.time_partitioning.field if table.time_partitioning else None,
            } if table.time_partitioning else None,
            "clustering_fields": table.clustering_fields if table.clustering_fields else [],
        }

    def get_smart_query_optimization(self, query_type: str = "analytics") -> Dict[str, Any]:
        """Get smart query optimization suggestions for different use cases"""
        optimizations = {
            "analytics": {
                "use_partitioning": True,
                "use_clustering": True,
                "recommended_clustering_fields": ["date", "user_id", "event_name"],
                "partition_field": "date",
                "partition_type": "DAY",
                "require_partition_filter": True,
                "suggested_labels": {"query_type": "analytics", "optimization": "enabled"}
            },
            "reporting": {
                "use_partitioning": True,
                "use_clustering": False,
                "partition_field": "created_date",
                "partition_type": "MONTH",
                "require_partition_filter": False,
                "suggested_labels": {"query_type": "reporting", "optimization": "standard"}
            },
            "streaming": {
                "use_partitioning": True,
                "use_clustering": True,
                "recommended_clustering_fields": ["timestamp", "source"],
                "partition_field": "timestamp",
                "partition_type": "HOUR",
                "require_partition_filter": False,
                "suggested_labels": {"query_type": "streaming", "optimization": "realtime"}
            }
        }

        return optimizations.get(query_type, optimizations["analytics"])

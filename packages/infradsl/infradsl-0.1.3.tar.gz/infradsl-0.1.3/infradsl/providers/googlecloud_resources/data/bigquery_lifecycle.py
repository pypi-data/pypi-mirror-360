"""
GCP BigQuery Lifecycle Mixin

Lifecycle operations for Google Cloud BigQuery.
Handles create, destroy, and preview operations with smart state management.
"""

from typing import Dict, Any, List, Optional, Union
import json


class BigQueryLifecycleMixin:
    """
    Mixin for BigQuery lifecycle operations.
    
    This mixin provides:
    - Create operation with smart state management
    - Destroy operation with safety checks
    - Preview operation for infrastructure planning
    - Query execution and data loading operations
    - State comparison and drift detection
    """
    
    def preview(self) -> Dict[str, Any]:
        """
        Preview what will be created, kept, and removed.
        
        Returns:
            Dict containing preview information and cost estimates
        """
        self._ensure_authenticated()
        
        # Discover existing resources
        existing_datasets = self._discover_existing_datasets()
        current_state = self._fetch_current_cloud_state()
        
        # Categorize resources
        datasets_to_create = []
        datasets_to_keep = []
        datasets_to_remove = []
        
        tables_to_create = []
        tables_to_keep = []
        tables_to_remove = []
        
        # Check if our desired dataset exists
        dataset_exists = current_state.get("exists", False)
        
        if not dataset_exists:
            datasets_to_create.append({
                'dataset_id': self.dataset_id,
                'location': self.dataset_location,
                'description': self.dataset_description,
                'schema_type': self.dataset_schema_type,
                'table_count': len(self.table_configs),
                'labels': self.dataset_labels
            })
        else:
            datasets_to_keep.append({
                'dataset_id': self.dataset_id,
                'location': current_state.get('location'),
                'description': current_state.get('description'),
                'table_count': current_state.get('table_count', 0),
                'labels': current_state.get('labels', {})
            })
            
            # Analyze table changes
            existing_tables = {t['table_id']: t for t in current_state.get('tables', [])}
            desired_table_ids = {table.table_id for table in self.table_configs}
            
            # Find tables to create
            for table_config in self.table_configs:
                if table_config.table_id not in existing_tables:
                    tables_to_create.append({
                        'table_id': table_config.table_id,
                        'schema_type': table_config.schema_type,
                        'table_type': table_config.table_type,
                        'partition_field': table_config.partition_field,
                        'clustering_fields': table_config.clustering_fields,
                        'optimized': bool(table_config.partition_field or table_config.clustering_fields),
                        'labels': table_config.labels
                    })
                else:
                    tables_to_keep.append(existing_tables[table_config.table_id])
            
            # Find tables to remove (exist but not in configuration)
            for table_id, table_info in existing_tables.items():
                if table_id not in desired_table_ids:
                    tables_to_remove.append(table_info)
        
        # Display preview
        self._display_bigquery_preview(datasets_to_create, datasets_to_keep, datasets_to_remove,
                                     tables_to_create, tables_to_keep, tables_to_remove)
        
        # Return structured data
        return {
            'resource_type': 'gcp_bigquery',
            'name': self.dataset_id,
            'current_state': current_state,
            'datasets_to_create': datasets_to_create,
            'datasets_to_keep': datasets_to_keep,
            'datasets_to_remove': datasets_to_remove,
            'tables_to_create': tables_to_create,
            'tables_to_keep': tables_to_keep,
            'tables_to_remove': tables_to_remove,
            'estimated_cost': self._calculate_bigquery_cost(),
            'configuration': self._get_bigquery_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the BigQuery dataset with tables.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration
        self._validate_bigquery_configuration()
        
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_bigquery_actions(current_state)
        
        # Execute actions
        result = self._execute_bigquery_actions(actions, current_state)
        
        # Update state
        self.dataset_exists = True
        self.dataset_created = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the BigQuery dataset and all tables.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying BigQuery dataset: {self.dataset_id}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  Dataset '{self.dataset_id}' does not exist")
                return {"success": True, "message": "Dataset does not exist", "name": self.dataset_id}
            
            # Show what will be destroyed
            self._display_bigquery_destruction_preview(current_state)
            
            # Perform destruction
            try:
                self.bigquery_client.delete_dataset(
                    self.dataset_id,
                    delete_contents=True,  # Delete all tables
                    not_found_ok=True
                )
                print(f"✅ Dataset '{self.dataset_id}' destroyed successfully")
                
                self.dataset_exists = False
                self.dataset_created = False
                
                return {
                    "success": True, 
                    "name": self.dataset_id,
                    "tables_destroyed": current_state.get("table_count", 0)
                }
                
            except Exception as e:
                print(f"❌ Failed to destroy dataset: {str(e)}")
                return {"success": False, "name": self.dataset_id, "error": str(e)}
                
        except Exception as e:
            print(f"❌ Error destroying BigQuery dataset: {str(e)}")
            return {"success": False, "name": self.dataset_id, "error": str(e)}
            
    def query(self, sql: str, dry_run: bool = False) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Execute SQL query with optional dry run validation.
        
        Args:
            sql: SQL query to execute
            dry_run: If True, validates query syntax without executing
            
        Returns:
            Query results or validation information
        """
        self._ensure_authenticated()
        
        try:
            if dry_run:
                from google.cloud import bigquery
                
                job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
                
                print("🔍 Dry run mode - validating query syntax...")
                
                try:
                    # Dry run doesn't return results, just validates
                    query_job = self.bigquery_client.query(sql, job_config=job_config)
                    
                    return {
                        "success": True,
                        "message": "Query syntax is valid",
                        "total_bytes_processed": query_job.total_bytes_processed,
                        "total_bytes_billed": query_job.total_bytes_billed,
                        "estimated_cost": f"${(query_job.total_bytes_billed or 0) / 1e12 * 5:.4f}"  # $5 per TB
                    }
                except Exception as validation_error:
                    return {
                        "success": False,
                        "error": str(validation_error),
                        "message": "Query validation failed"
                    }
            else:
                query_job = self.bigquery_client.query(sql)
                results = query_job.result()
                
                # Convert results to list of dictionaries
                rows = [dict(row) for row in results]
                
                return {
                    "success": True,
                    "rows": rows,
                    "total_rows": query_job.total_rows,
                    "total_bytes_processed": query_job.total_bytes_processed,
                    "total_bytes_billed": query_job.total_bytes_billed,
                    "job_id": query_job.job_id,
                    "estimated_cost": f"${(query_job.total_bytes_billed or 0) / 1e12 * 5:.4f}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Query execution failed"
            }
            
    def load_from_gcs(self, gcs_uri: str, table_name: str,
                     schema: Optional[List[Dict[str, Any]]] = None,
                     write_mode: str = "append") -> Dict[str, Any]:
        """Load data from Google Cloud Storage"""
        self._ensure_authenticated()
        
        write_disposition_map = {
            "append": "WRITE_APPEND",
            "truncate": "WRITE_TRUNCATE",
            "empty": "WRITE_EMPTY"
        }
        
        try:
            from google.cloud import bigquery
            
            # Get table reference
            table_ref = self.bigquery_client.dataset(self.dataset_id).table(table_name)
            
            # Configure load job
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,  # Default to CSV
                skip_leading_rows=1,  # Skip header row
                autodetect=schema is None,  # Auto-detect schema if not provided
                write_disposition=write_disposition_map.get(write_mode, "WRITE_APPEND")
            )
            
            if schema:
                job_config.schema = [
                    bigquery.SchemaField(
                        field["name"],
                        field["type"],
                        mode=field.get("mode", "NULLABLE"),
                        description=field.get("description", "")
                    )
                    for field in schema
                ]
            
            # Start load job
            load_job = self.bigquery_client.load_table_from_uri(
                gcs_uri,
                table_ref,
                job_config=job_config
            )
            
            # Wait for job to complete
            load_job.result()
            
            # Get updated table info
            table = self.bigquery_client.get_table(table_ref)
            
            print(f"✅ Data loaded from {gcs_uri} into {table_name}")
            
            return {
                "success": True,
                "table_name": table_name,
                "rows_loaded": table.num_rows,
                "bytes_loaded": table.num_bytes,
                "job_id": load_job.job_id
            }
            
        except Exception as e:
            print(f"❌ Failed to load data: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
            
    def _validate_bigquery_configuration(self):
        """Validate the BigQuery configuration before creation"""
        errors = []
        warnings = []
        
        # Validate dataset name
        if not self.dataset_id:
            errors.append("Dataset ID is required")
        elif not self._is_valid_dataset_name(self.dataset_id):
            errors.append(f"Invalid dataset name: {self.dataset_id}")
        
        # Validate location
        if not self._is_valid_location(self.dataset_location):
            errors.append(f"Invalid location: {self.dataset_location}")
        
        # Validate table configurations
        table_names = set()
        for table_config in self.table_configs:
            if not table_config.table_id:
                errors.append("Table ID is required for all tables")
            elif not self._is_valid_table_name(table_config.table_id):
                errors.append(f"Invalid table name: {table_config.table_id}")
            
            if table_config.table_id in table_names:
                errors.append(f"Duplicate table name: {table_config.table_id}")
            table_names.add(table_config.table_id)
        
        # Performance warnings
        unoptimized_tables = [
            t for t in self.table_configs 
            if not t.partition_field and not t.clustering_fields
        ]
        if unoptimized_tables:
            warnings.append(f"{len(unoptimized_tables)} tables have no partitioning or clustering")
        
        # Cost warnings
        if self.dataset_location not in ["US", "EU"] and len(self.table_configs) > 10:
            warnings.append("Regional datasets with many tables may have higher costs")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
                
    def _determine_bigquery_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create_dataset": False,
            "update_dataset": False,
            "keep_dataset": False,
            "create_tables": [],
            "update_tables": [],
            "remove_tables": [],
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create_dataset"] = True
            actions["changes"].append("Create new dataset")
            actions["create_tables"] = [t.table_id for t in self.table_configs]
            actions["changes"].extend([f"Create table {t}" for t in actions["create_tables"]])
        else:
            # Compare current state with desired state
            dataset_changes = self._detect_dataset_drift(current_state)
            
            if dataset_changes:
                actions["update_dataset"] = True
                actions["changes"].extend(dataset_changes)
            
            # Analyze table changes
            existing_tables = {t['table_id']: t for t in current_state.get('tables', [])}
            desired_table_ids = {table.table_id for table in self.table_configs}
            
            # Find tables to create
            for table_config in self.table_configs:
                if table_config.table_id not in existing_tables:
                    actions["create_tables"].append(table_config.table_id)
                    actions["changes"].append(f"Create table {table_config.table_id}")
            
            # Find tables to remove
            for table_id in existing_tables:
                if table_id not in desired_table_ids:
                    actions["remove_tables"].append(table_id)
                    actions["changes"].append(f"Remove table {table_id}")
            
            if not actions["changes"]:
                actions["keep_dataset"] = True
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_dataset_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences between current and desired dataset state"""
        changes = []
        
        # Compare description
        current_description = current_state.get("description", "")
        if current_description != self.dataset_description:
            changes.append(f"Description: '{current_description}' → '{self.dataset_description}'")
        
        # Compare friendly name
        current_friendly_name = current_state.get("friendly_name", "")
        if current_friendly_name != (self.dataset_friendly_name or ""):
            changes.append(f"Friendly name: '{current_friendly_name}' → '{self.dataset_friendly_name or ''}'")
        
        # Compare labels
        current_labels = current_state.get("labels", {})
        if current_labels != self.dataset_labels:
            changes.append(f"Labels: {current_labels} → {self.dataset_labels}")
        
        # Note: Location cannot be changed after creation
        
        return changes
        
    def _execute_bigquery_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create_dataset"]:
            return self._create_bigquery_dataset()
        elif actions["update_dataset"] or actions["create_tables"] or actions["remove_tables"]:
            return self._update_bigquery_dataset(current_state, actions)
        else:
            return self._keep_bigquery_dataset(current_state)
            
    def _create_bigquery_dataset(self) -> Dict[str, Any]:
        """Create a new BigQuery dataset"""
        print(f"\n📊 Creating BigQuery dataset: {self.dataset_id}")
        print(f"   📍 Location: {self.dataset_location}")
        print(f"   📋 Description: {self.dataset_description}")
        if self.dataset_schema_type:
            print(f"   🎯 Schema Type: {self.dataset_schema_type}")
        print(f"   📦 Tables: {len(self.table_configs)} configured")
        
        try:
            from google.cloud import bigquery
            
            # Create dataset
            dataset = bigquery.Dataset(f"{self.project_id}.{self.dataset_id}")
            dataset.location = self.dataset_location
            dataset.description = self.dataset_description
            
            if self.dataset_friendly_name:
                dataset.friendly_name = self.dataset_friendly_name
            
            if self.dataset_labels:
                dataset.labels = self.dataset_labels
            
            if self.default_table_expiration_ms:
                dataset.default_table_expiration_ms = self.default_table_expiration_ms
            
            if self.default_partition_expiration_ms:
                dataset.default_partition_expiration_ms = self.default_partition_expiration_ms
            
            # Create the dataset
            created_dataset = self.bigquery_client.create_dataset(dataset, exists_ok=False)
            
            print(f"\n✅ Dataset created successfully!")
            print(f"   📊 Dataset: {self.dataset_id}")
            print(f"   📍 Location: {created_dataset.location}")
            print(f"   🌐 Resource: {created_dataset.self_link}")
            
            # Create tables
            tables_created = []
            for table_config in self.table_configs:
                table_result = self._create_table(table_config)
                if table_result.get("success"):
                    tables_created.append(table_config.table_id)
            
            print(f"   📋 Tables Created: {len(tables_created)}")
            print(f"   💰 Estimated Cost: {self._calculate_bigquery_cost()}")
            
            return {
                "success": True,
                "name": self.dataset_id,
                "location": created_dataset.location,
                "dataset_created": True,
                "tables_created": tables_created,
                "table_count": len(tables_created),
                "estimated_cost": self._calculate_bigquery_cost()
            }
            
        except Exception as e:
            print(f"❌ Failed to create BigQuery dataset: {str(e)}")
            raise
            
    def _update_bigquery_dataset(self, current_state: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing BigQuery dataset"""
        print(f"\n🔄 Updating BigQuery dataset: {self.dataset_id}")
        print(f"   📋 Changes to apply:")
        for change in actions["changes"]:
            print(f"      • {change}")
            
        try:
            results = []
            
            # Remove tables first
            for table_id in actions["remove_tables"]:
                try:
                    self.bigquery_client.delete_table(f"{self.project_id}.{self.dataset_id}.{table_id}")
                    print(f"   🗑️  Removed table: {table_id}")
                    results.append(("remove_table", table_id, True))
                except Exception as e:
                    print(f"   ❌ Failed to remove table {table_id}: {str(e)}")
                    results.append(("remove_table", table_id, False))
            
            # Create new tables
            tables_created = []
            for table_id in actions["create_tables"]:
                table_config = next((t for t in self.table_configs if t.table_id == table_id), None)
                if table_config:
                    table_result = self._create_table(table_config)
                    if table_result.get("success"):
                        tables_created.append(table_id)
                        results.append(("create_table", table_id, True))
                    else:
                        results.append(("create_table", table_id, False))
            
            # Update dataset metadata if needed
            if actions["update_dataset"]:
                try:
                    dataset = self.bigquery_client.get_dataset(self.dataset_id)
                    dataset.description = self.dataset_description
                    if self.dataset_friendly_name:
                        dataset.friendly_name = self.dataset_friendly_name
                    if self.dataset_labels:
                        dataset.labels = self.dataset_labels
                    
                    self.bigquery_client.update_dataset(dataset, ["description", "friendly_name", "labels"])
                    results.append(("update_dataset", True))
                except Exception as e:
                    print(f"   ❌ Failed to update dataset metadata: {str(e)}")
                    results.append(("update_dataset", False))
            
            print(f"\n✅ BigQuery dataset updated successfully!")
            print(f"   📊 Dataset: {self.dataset_id}")
            print(f"   🔄 Changes Applied: {len(actions['changes'])}")
            
            return {
                "success": True,
                "name": self.dataset_id,
                "changes_applied": len(actions["changes"]),
                "results": results,
                "tables_created": tables_created,
                "tables_removed": actions["remove_tables"],
                "updated": True
            }
            
        except Exception as e:
            print(f"❌ Failed to update BigQuery dataset: {str(e)}")
            raise
            
    def _keep_bigquery_dataset(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing BigQuery dataset (no changes needed)"""
        print(f"\n✅ BigQuery dataset '{self.dataset_id}' is up to date")
        print(f"   📊 Dataset: {self.dataset_id}")
        print(f"   📍 Location: {current_state.get('location', 'Unknown')}")
        print(f"   📦 Tables: {current_state.get('table_count', 0)} total")
        print(f"   📋 Description: {current_state.get('description', 'No description')}")
        
        return {
            "success": True,
            "name": self.dataset_id,
            "location": current_state.get("location"),
            "table_count": current_state.get("table_count", 0),
            "description": current_state.get("description"),
            "unchanged": True
        }
        
    def _create_table(self, table_config) -> Dict[str, Any]:
        """Create a single table"""
        try:
            from google.cloud import bigquery
            
            # Build table reference
            table_ref = self.bigquery_client.dataset(self.dataset_id).table(table_config.table_id)
            
            # Create table
            table = bigquery.Table(table_ref)
            
            if table_config.description:
                table.description = table_config.description
            
            if table_config.labels:
                table.labels = table_config.labels
            
            if table_config.expiration_ms:
                table.expires = table_config.expiration_ms
            
            # Set schema
            if table_config.table_schema:
                table.schema = [
                    bigquery.SchemaField(
                        field["name"],
                        field["type"],
                        mode=field.get("mode", "NULLABLE"),
                        description=field.get("description", "")
                    )
                    for field in table_config.table_schema
                ]
            
            # Set partitioning
            if table_config.partition_field:
                if table_config.partition_type == "DAY":
                    table.time_partitioning = bigquery.TimePartitioning(
                        type_=bigquery.TimePartitioningType.DAY,
                        field=table_config.partition_field
                    )
                elif table_config.partition_type == "HOUR":
                    table.time_partitioning = bigquery.TimePartitioning(
                        type_=bigquery.TimePartitioningType.HOUR,
                        field=table_config.partition_field
                    )
                
                if table_config.partition_expiration_days:
                    table.time_partitioning.expiration_ms = table_config.partition_expiration_days * 24 * 60 * 60 * 1000
                
                if table_config.require_partition_filter:
                    table.time_partitioning.require_partition_filter = True
            
            # Set clustering
            if table_config.clustering_fields:
                table.clustering_fields = table_config.clustering_fields
            
            # Create the table
            created_table = self.bigquery_client.create_table(table)
            
            print(f"   📋 Created table: {table_config.table_id}")
            
            return {
                "success": True,
                "table_id": table_config.table_id,
                "table_ref": created_table.reference,
                "created": True
            }
            
        except Exception as e:
            print(f"   ❌ Failed to create table {table_config.table_id}: {str(e)}")
            return {
                "success": False,
                "table_id": table_config.table_id,
                "error": str(e)
            }
            
    def _display_bigquery_preview(self, datasets_to_create, datasets_to_keep, datasets_to_remove,
                                 tables_to_create, tables_to_keep, tables_to_remove):
        """Display preview of actions to be taken"""
        print(f"\n📊 Google Cloud BigQuery Preview")
        print(f"   🎯 Dataset: {self.dataset_id}")
        print(f"   📍 Location: {self.dataset_location}")
        print(f"   🏷️  Schema Type: {self.dataset_schema_type or 'General'}")
        
        if datasets_to_create:
            dataset = datasets_to_create[0]
            print(f"\n╭─ 🆕 WILL CREATE DATASET")
            print(f"├─ 📊 Dataset: {dataset['dataset_id']}")
            print(f"├─ 📍 Location: {dataset['location']}")
            print(f"├─ 📋 Description: {dataset['description']}")
            if dataset['schema_type']:
                print(f"├─ 🎯 Schema Type: {dataset['schema_type']}")
            print(f"├─ 📦 Tables: {dataset['table_count']} configured")
            
            if dataset['labels']:
                print(f"├─ 🏷️  Labels: {len(dataset['labels'])}")
                for key, value in list(dataset['labels'].items())[:3]:
                    print(f"│  • {key}: {value}")
            
            print(f"├─ 🚀 Features:")
            print(f"│  ├─ 📊 Standard SQL engine")
            print(f"│  ├─ 🔍 Petabyte-scale analytics")
            print(f"│  ├─ 🔐 IAM access control")
            print(f"│  └─ 📋 Audit logging")
            print(f"╰─ 💰 Estimated Cost: {self._calculate_bigquery_cost()}")
        
        if tables_to_create:
            print(f"\n╭─ 📋 WILL CREATE TABLES: {len(tables_to_create)}")
            for table in tables_to_create:
                print(f"├─ 🆕 {table['table_id']}")
                if table['schema_type']:
                    print(f"│  ├─ 🎯 Schema: {table['schema_type']}")
                if table['partition_field']:
                    print(f"│  ├─ 🗂️  Partitioned: {table['partition_field']}")
                if table['clustering_fields']:
                    print(f"│  ├─ 🔍 Clustered: {', '.join(table['clustering_fields'])}")
                if table['optimized']:
                    print(f"│  ├─ ⚡ Performance: Optimized")
                print(f"│  └─ 💾 Storage: Compressed columnar")
            print(f"╰─")
        
        if tables_to_keep:
            print(f"\n╭─ ✅ WILL KEEP TABLES: {len(tables_to_keep)}")
            for table in tables_to_keep[:3]:  # Show first 3
                print(f"├─ 📋 {table['table_id']}")
                print(f"│  ├─ 📊 Type: {table.get('table_type', 'TABLE')}")
                print(f"│  ├─ 📈 Rows: {table.get('num_rows', 0):,}")
                print(f"│  └─ 💾 Size: {table.get('num_bytes', 0) / 1024 / 1024:.1f} MB")
            if len(tables_to_keep) > 3:
                print(f"├─ ... and {len(tables_to_keep) - 3} more tables")
            print(f"╰─")
        
        if tables_to_remove:
            print(f"\n╭─ 🗑️  WILL REMOVE TABLES: {len(tables_to_remove)}")
            for table in tables_to_remove:
                print(f"├─ 🔄 {table['table_id']}")
                print(f"│  ├─ 📊 Type: {table.get('table_type', 'TABLE')}")
                print(f"│  ├─ 📈 Rows: {table.get('num_rows', 0):,}")
                print(f"│  └─ ⚠️  Will be deleted")
            print(f"╰─")
            
    def _display_bigquery_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  Dataset: {self.dataset_id}")
        print(f"   📍 Location: {current_state.get('location', 'Unknown')}")
        print(f"   📦 Tables: {current_state.get('table_count', 0)}")
        if current_state.get("tables"):
            print(f"   📋 Table List:")
            for table in current_state["tables"][:5]:  # Show first 5
                print(f"      • {table['table_id']} ({table.get('num_rows', 0):,} rows)")
            if len(current_state["tables"]) > 5:
                print(f"      • ... and {len(current_state['tables']) - 5} more tables")
        print(f"   ⚠️  ALL DATA WILL BE PERMANENTLY DELETED")
        print(f"   ⚠️  THIS ACTION CANNOT BE UNDONE")
        
    def _calculate_bigquery_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_bigquery_cost()
        return f"${base_cost:.2f}/month"
        
    def _get_bigquery_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current BigQuery configuration"""
        return {
            "dataset_id": self.dataset_id,
            "dataset_location": self.dataset_location,
            "dataset_description": self.dataset_description,
            "dataset_schema_type": self.dataset_schema_type,
            "dataset_labels": self.dataset_labels,
            "table_count": len(self.table_configs),
            "tables": [
                {
                    "table_id": table.table_id,
                    "schema_type": table.schema_type,
                    "partition_field": table.partition_field,
                    "clustering_fields": table.clustering_fields,
                    "labels": table.labels
                }
                for table in self.table_configs
            ],
            "optimized_tables": len([t for t in self.table_configs if t.partition_field or t.clustering_fields]),
            "default_table_expiration_ms": self.default_table_expiration_ms,
            "default_partition_expiration_ms": self.default_partition_expiration_ms
        }
        
    def optimize_for(self, priority: str):
        """
        Use Cross-Cloud Magic to optimize for cost/performance/reliability/compliance
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        print(f"🎯 Cross-Cloud Magic: Optimizing BigQuery for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective analytics")
            # Cost optimization
            self.location("US")  # Multi-region for better pricing
            self.default_table_expiration(365)  # 1 year retention
            self.default_partition_expiration(90)  # 90 day partitions
            self.label("optimization", "cost")
            
            # Optimize all tables for cost
            for table_config in self.table_configs:
                if not table_config.partition_field and not table_config.require_partition_filter:
                    table_config.partition_field = "date"
                    table_config.require_partition_filter = True
            print("   💡 Configured for cost-effective storage and query patterns")
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance analytics")
            # Performance optimization
            self.location("us-central1")  # Single region for performance
            self.label("optimization", "performance")
            
            # Optimize all tables for performance
            for table_config in self.table_configs:
                if not table_config.partition_field:
                    table_config.partition_field = "date"
                if not table_config.clustering_fields:
                    # Add common clustering fields based on schema type
                    if table_config.schema_type == "web_analytics":
                        table_config.clustering_fields = ["user_id", "page_url"]
                    elif table_config.schema_type == "user_events":
                        table_config.clustering_fields = ["user_id", "event_name"]
                    elif table_config.schema_type == "logs":
                        table_config.clustering_fields = ["severity", "source"]
            print("   💡 Configured for high-performance queries and analytics")
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable analytics")
            # Reliability optimization
            self.location("US")  # Multi-region for reliability
            self.label("optimization", "reliability")
            self.label("backup", "enabled")
            
            # Configure for reliability
            for table_config in self.table_configs:
                if not table_config.partition_field:
                    table_config.partition_field = "date"
                # Keep more historical data for reliability
                if not table_config.expiration_ms:
                    table_config.expiration_ms = 3 * 365 * 24 * 60 * 60 * 1000  # 3 years
            print("   💡 Configured for high availability and data durability")
                
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant analytics")
            # Compliance optimization
            self.location("us-central1")  # Data residency
            self.label("optimization", "compliance")
            self.label("compliance", "required")
            self.label("audit", "enabled")
            self.label("retention", "7years")
            
            # Configure for compliance
            for table_config in self.table_configs:
                if not table_config.partition_field:
                    table_config.partition_field = "date"
                # Long retention for compliance
                if not table_config.expiration_ms:
                    table_config.expiration_ms = 7 * 365 * 24 * 60 * 60 * 1000  # 7 years
                # Add compliance labels
                if not table_config.labels:
                    table_config.labels = {}
                table_config.labels.update({
                    "compliance": "required",
                    "audit": "enabled"
                })
            print("   💡 Configured for compliance with audit and retention requirements")
            
        return self
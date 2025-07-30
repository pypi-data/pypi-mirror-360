"""
GCP BigQuery Complete Implementation

Complete BigQuery implementation combining core functionality, 
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .bigquery_core import BigQueryCore, TableConfig
from .bigquery_configuration import BigQueryConfigurationMixin
from .bigquery_lifecycle import BigQueryLifecycleMixin


class BigQuery(BigQueryCore, BigQueryConfigurationMixin, BigQueryLifecycleMixin):
    """
    Complete Google Cloud BigQuery implementation.
    
    This class combines:
    - BigQueryCore: Basic dataset and table attributes and authentication
    - BigQueryConfigurationMixin: Chainable configuration methods
    - BigQueryLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent analytics configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Predefined schemas for common use cases (web analytics, events, logs)
    - Performance optimization (partitioning, clustering)
    - Cost optimization patterns
    - Compliance and audit configurations
    - SQL query execution and data loading
    
    Example:
        # Analytics dataset with web tracking
        bq = BigQuery("web_analytics")
        bq.analytics_dataset().location("US")
        bq.web_analytics_table("page_views")
        bq.user_events_table("events")
        bq.create()
        
        # Data warehouse with star schema
        bq = BigQuery("sales_dwh")
        bq.reporting_dataset().production()
        bq.fact_table("sales_facts")
        bq.dimension_table("product_dim")
        bq.create()
        
        # Cross-Cloud Magic optimization
        bq = BigQuery("ml_features")
        bq.machine_learning_dataset()
        bq.table("features", "user_events")
        bq.optimize_for("performance")
        bq.create()
    """
    
    def __init__(self, dataset_name: str):
        """
        Initialize BigQuery with dataset name.
        
        Args:
            dataset_name: Dataset name (must be valid BigQuery dataset name)
        """
        # Initialize all parent classes
        BigQueryCore.__init__(self, dataset_name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of BigQuery instance"""
        status = "configured" if self.table_configs else "empty"
        optimization = "optimized" if any(t.partition_field or t.clustering_fields for t in self.table_configs) else "standard"
        
        return (f"BigQuery(dataset='{self.dataset_id}', "
                f"location='{self.dataset_location}', "
                f"status='{status}', "
                f"tables={len(self.table_configs)}, "
                f"optimization='{optimization}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of BigQuery configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze table optimizations
        partitioned_tables = len([t for t in self.table_configs if t.partition_field])
        clustered_tables = len([t for t in self.table_configs if t.clustering_fields])
        optimized_tables = len([t for t in self.table_configs if t.partition_field or t.clustering_fields])
        
        # Analyze schemas
        schema_types = {}
        for table in self.table_configs:
            schema_type = table.schema_type or "custom"
            schema_types[schema_type] = schema_types.get(schema_type, 0) + 1
        
        summary = {
            "dataset_id": self.dataset_id,
            "dataset_location": self.dataset_location,
            "dataset_description": self.dataset_description,
            "dataset_schema_type": self.dataset_schema_type,
            "dataset_friendly_name": self.dataset_friendly_name,
            
            # Tables
            "table_count": len(self.table_configs),
            "table_schemas": schema_types,
            "partitioned_tables": partitioned_tables,
            "clustered_tables": clustered_tables,
            "optimized_tables": optimized_tables,
            "optimization_percentage": (optimized_tables / len(self.table_configs) * 100) if self.table_configs else 0,
            
            # Configuration
            "labels": self.dataset_labels,
            "label_count": len(self.dataset_labels),
            "default_table_expiration_ms": self.default_table_expiration_ms,
            "default_partition_expiration_ms": self.default_partition_expiration_ms,
            
            # State
            "state": {
                "exists": self.dataset_exists,
                "created": self.dataset_created,
                "resource_name": self.dataset_resource_name,
                "tables_created": self.tables_created
            },
            
            # Cost
            "estimated_monthly_cost": self._calculate_bigquery_cost()
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\n📊 BigQuery Configuration: {self.dataset_id}")
        print(f"   📍 Location: {self.dataset_location}")
        print(f"   📋 Description: {self.dataset_description}")
        if self.dataset_schema_type:
            print(f"   🎯 Schema Type: {self.dataset_schema_type}")
        if self.dataset_friendly_name:
            print(f"   👤 Friendly Name: {self.dataset_friendly_name}")
        
        # Tables
        if self.table_configs:
            print(f"\n📦 Tables ({len(self.table_configs)}):")
            for table in self.table_configs:
                print(f"   📋 {table.table_id}")
                if table.schema_type:
                    print(f"      🎯 Schema: {table.schema_type}")
                if table.partition_field:
                    print(f"      🗂️  Partitioned: {table.partition_field} ({table.partition_type})")
                if table.clustering_fields:
                    print(f"      🔍 Clustered: {', '.join(table.clustering_fields)}")
                if table.require_partition_filter:
                    print(f"      🔒 Requires partition filter")
                if table.labels:
                    print(f"      🏷️  Labels: {len(table.labels)}")
        else:
            print(f"\n📦 Tables: None configured")
        
        # Optimization analysis
        if self.table_configs:
            optimized = len([t for t in self.table_configs if t.partition_field or t.clustering_fields])
            optimization_pct = (optimized / len(self.table_configs)) * 100
            print(f"\n⚡ Performance Optimization:")
            print(f"   📊 Optimized Tables: {optimized}/{len(self.table_configs)} ({optimization_pct:.1f}%)")
            
            partitioned = len([t for t in self.table_configs if t.partition_field])
            if partitioned > 0:
                print(f"   🗂️  Partitioned: {partitioned} tables")
                
            clustered = len([t for t in self.table_configs if t.clustering_fields])
            if clustered > 0:
                print(f"   🔍 Clustered: {clustered} tables")
        
        # Expiration settings
        if self.default_table_expiration_ms or self.default_partition_expiration_ms:
            print(f"\n⏰ Expiration Settings:")
            if self.default_table_expiration_ms:
                days = self.default_table_expiration_ms // (24 * 60 * 60 * 1000)
                print(f"   📋 Default Table Expiration: {days} days")
            if self.default_partition_expiration_ms:
                days = self.default_partition_expiration_ms // (24 * 60 * 60 * 1000)
                print(f"   🗂️  Default Partition Expiration: {days} days")
        
        # Labels
        if self.dataset_labels:
            print(f"\n🏷️  Labels ({len(self.dataset_labels)}):")
            for key, value in list(self.dataset_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.dataset_labels) > 5:
                print(f"   • ... and {len(self.dataset_labels) - 5} more")
        
        # Cost
        print(f"\n💰 Estimated Cost: {self._calculate_bigquery_cost()}")
        
        # State
        if self.dataset_exists:
            print(f"\n📊 State:")
            print(f"   ✅ Exists: {self.dataset_exists}")
            print(f"   🆔 Resource: {self.dataset_resource_name}")
            if self.tables_created:
                print(f"   📋 Tables Created: {len(self.tables_created)}")
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze performance configuration and provide recommendations.
        
        Returns:
            Dict containing performance analysis and recommendations
        """
        analysis = {
            "performance_score": 0,
            "max_score": 100,
            "recommendations": [],
            "optimization_opportunities": [],
            "cost_factors": []
        }
        
        # Dataset location analysis
        if self.dataset_location in ["US", "EU"]:
            analysis["performance_score"] += 20
        elif self.dataset_location in ["us-central1", "europe-west1"]:
            analysis["performance_score"] += 25
        else:
            analysis["performance_score"] += 15
            analysis["recommendations"].append("Consider US or EU multi-regions for better performance")
        
        # Table optimization analysis
        if self.table_configs:
            partitioned_tables = len([t for t in self.table_configs if t.partition_field])
            clustered_tables = len([t for t in self.table_configs if t.clustering_fields])
            optimized_tables = len([t for t in self.table_configs if t.partition_field or t.clustering_fields])
            
            optimization_pct = (optimized_tables / len(self.table_configs)) * 100
            
            if optimization_pct >= 80:
                analysis["performance_score"] += 30
            elif optimization_pct >= 60:
                analysis["performance_score"] += 25
            elif optimization_pct >= 40:
                analysis["performance_score"] += 20
            else:
                analysis["performance_score"] += 10
                analysis["recommendations"].append("Optimize more tables with partitioning and clustering")
            
            # Check for specific optimizations
            if partitioned_tables / len(self.table_configs) >= 0.8:
                analysis["performance_score"] += 20
            else:
                analysis["optimization_opportunities"].append("Add partitioning to more tables")
            
            if clustered_tables / len(self.table_configs) >= 0.6:
                analysis["performance_score"] += 15
            else:
                analysis["optimization_opportunities"].append("Add clustering to more tables")
            
            # Check for partition filters
            partition_filter_tables = len([t for t in self.table_configs if t.require_partition_filter])
            if partition_filter_tables > 0:
                analysis["performance_score"] += 15
            else:
                analysis["optimization_opportunities"].append("Enable partition filter requirements for cost control")
        
        # Schema type analysis
        if self.dataset_schema_type in ["analytics", "streaming", "reporting"]:
            analysis["performance_score"] += 10
        
        return analysis
    
    def analyze_cost(self) -> Dict[str, Any]:
        """
        Analyze cost configuration and provide recommendations.
        
        Returns:
            Dict containing cost analysis and recommendations
        """
        analysis = {
            "cost_score": 0,
            "max_score": 100,
            "recommendations": [],
            "cost_drivers": [],
            "savings_opportunities": []
        }
        
        # Location cost analysis
        if self.dataset_location in ["US", "EU"]:
            analysis["cost_score"] += 25
        else:
            analysis["cost_score"] += 15
            analysis["cost_drivers"].append("Regional dataset may have higher costs than multi-region")
        
        # Expiration settings analysis
        if self.default_table_expiration_ms:
            analysis["cost_score"] += 20
        else:
            analysis["savings_opportunities"].append("Set default table expiration to reduce storage costs")
        
        if self.default_partition_expiration_ms:
            analysis["cost_score"] += 15
        else:
            analysis["savings_opportunities"].append("Set partition expiration for automatic cleanup")
        
        # Optimization analysis
        if self.table_configs:
            partition_filter_tables = len([t for t in self.table_configs if t.require_partition_filter])
            if partition_filter_tables / len(self.table_configs) >= 0.8:
                analysis["cost_score"] += 25
            else:
                analysis["savings_opportunities"].append("Require partition filters to reduce query costs")
            
            partitioned_tables = len([t for t in self.table_configs if t.partition_field])
            if partitioned_tables / len(self.table_configs) >= 0.8:
                analysis["cost_score"] += 15
            else:
                analysis["savings_opportunities"].append("Partition more tables to enable partition pruning")
        
        return analysis
    
    # Connection and integration methods
    def connection_info(self) -> Dict[str, str]:
        """Get connection information for external tools"""
        return {
            "project_id": self.project_id or "PROJECT_ID",
            "dataset_id": self.dataset_id,
            "location": self.dataset_location,
            "jdbc_url": f"jdbc:bigquery://https://www.googleapis.com/bigquery/v2:443;ProjectId={self.project_id or 'PROJECT_ID'};DefaultDataset={self.dataset_id}",
            "odbc_connection": f"DRIVER={{Google BigQuery ODBC Driver}};SERVER=https://www.googleapis.com/bigquery/v2;PROJECT={self.project_id or 'PROJECT_ID'};DATASET={self.dataset_id}"
        }
    
    def python_client_code(self) -> str:
        """Generate Python client code for connecting to this dataset"""
        return f'''# BigQuery Python client code
from google.cloud import bigquery

client = bigquery.Client(project="{self.project_id or 'YOUR_PROJECT_ID'}")
dataset_ref = client.dataset("{self.dataset_id}")

# Example query
query = """
    SELECT *
    FROM `{self.project_id or 'YOUR_PROJECT_ID'}.{self.dataset_id}.your_table`
    LIMIT 10
"""

results = client.query(query).result()
for row in results:
    print(row)
'''
    
    def sql_connection_string(self, tool: str = "generic") -> str:
        """Generate SQL connection strings for different tools"""
        connection_strings = {
            "looker": f"connection: bigquery_{self.dataset_id} {{\n  database: \"{self.project_id or 'PROJECT_ID'}\"\n  schema: \"{self.dataset_id}\"\n}}",
            "tableau": f"bigquery-connector://{self.project_id or 'PROJECT_ID'}/{self.dataset_id}",
            "power_bi": f"https://app.powerbi.com/getdata/services/bigquery?project={self.project_id or 'PROJECT_ID'}&dataset={self.dataset_id}",
            "generic": f"bigquery://{self.project_id or 'PROJECT_ID'}/{self.dataset_id}"
        }
        
        return connection_strings.get(tool, connection_strings["generic"])
    
    # Utility methods for backwards compatibility
    def info(self) -> Dict[str, Any]:
        """Get information about the dataset - backwards compatibility"""
        return self.summary()
    
    def delete(self, force: bool = False) -> bool:
        """Delete the dataset and all tables - backwards compatibility"""
        if not force:
            print("⚠️ This will delete the entire dataset and all tables")
            print("⚠️ Use .delete(force=True) to confirm")
            return False
        
        result = self.destroy()
        return result.get("success", False)


# Convenience function for creating BigQuery instances
def create_bigquery(dataset_name: str) -> BigQuery:
    """
    Create a new BigQuery instance.
    
    Args:
        dataset_name: Dataset name
        
    Returns:
        BigQuery instance
    """
    return BigQuery(dataset_name)


# Export the class for easy importing
__all__ = ['BigQuery', 'create_bigquery', 'TableConfig']
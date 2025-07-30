"""
Google Cloud Spanner Core Implementation

Core attributes and authentication for Google Cloud Spanner.
Provides the foundation for the modular globally distributed database.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class CloudSpannerCore(BaseGcpResource):
    """
    Core class for Google Cloud Spanner functionality.
    
    This class provides:
    - Basic Cloud Spanner attributes and configuration
    - Authentication setup
    - Common utilities for Spanner operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """
        Initialize Cloud Spanner core with instance name.
        
        Args:
            name: Spanner instance name
        """
        super().__init__(name)
        
        # Core Spanner attributes
        self.instance_name = name
        self.instance_description = f"Cloud Spanner instance: {name}"
        self.spanner_type = "spanner_instance"
        
        # Instance configuration
        self.instance_id = None
        self.project_id = None
        self.instance_config = "regional-us-central1"
        self.display_name = None
        self.node_count = 1
        self.processing_units = None  # Alternative to node_count
        
        # Database configuration
        self.databases = []
        self.default_database = None
        
        # Performance configuration
        self.multi_region = False
        self.leader_region = None
        self.read_replicas = []
        
        # Security configuration
        self.deletion_protection = True
        self.encryption_config = None
        self.customer_managed_encryption = False
        
        # Backup configuration
        self.backup_enabled = True
        self.backup_retention_period = "7d"
        self.point_in_time_recovery = True
        
        # Monitoring configuration
        self.monitoring_enabled = True
        self.alerting_enabled = False
        self.query_insights = True
        
        # IAM and access configuration
        self.iam_members = []
        self.database_roles = []
        
        # State tracking
        self.instance_exists = False
        self.instance_created = False
        self.instance_state = None
        self.deployment_status = None
        
        # Labels and metadata
        self.spanner_labels = {}
        self.spanner_annotations = {}
        
        # Cost tracking
        self.estimated_monthly_cost = "$700.00/month"
        
    def _initialize_managers(self):
        """Initialize Spanner specific managers"""
        self.spanner_admin_instance = None
        self.spanner_admin_database = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            from google.cloud import spanner_admin_instance_v1
            from google.cloud import spanner_admin_database_v1
            
            self.spanner_admin_instance = spanner_admin_instance_v1.InstanceAdminClient()
            self.spanner_admin_database = spanner_admin_database_v1.DatabaseAdminClient()
            
            # Set project ID from GCP client if available
            if hasattr(self.gcp_client, 'project'):
                self.project_id = self.gcp_client.project
                
        except Exception as e:
            print(f"⚠️  Cloud Spanner setup note: {str(e)}")
            
    def _validate_instance_config(self, config: str) -> bool:
        """Validate if instance configuration is valid"""
        valid_configs = [
            # Regional configurations
            "regional-us-central1", "regional-us-east1", "regional-us-west1", "regional-us-west2",
            "regional-europe-west1", "regional-europe-west4", "regional-europe-north1",
            "regional-asia-east1", "regional-asia-northeast1", "regional-asia-south1",
            "regional-australia-southeast1", "regional-southamerica-east1",
            
            # Multi-regional configurations
            "nam3", "nam6", "eur3", "eur5", "asia1",
            
            # Special configurations
            "nam-eur-asia1"
        ]
        return config in valid_configs
        
    def _validate_node_count(self, node_count: int) -> bool:
        """Validate node count for instance"""
        return 1 <= node_count <= 10000
        
    def _validate_processing_units(self, processing_units: int) -> bool:
        """Validate processing units for instance"""
        # Processing units must be between 100-100000 and in increments of 100
        return (100 <= processing_units <= 100000 and 
                processing_units % 100 == 0)
                
    def _get_spanner_type_from_config(self) -> str:
        """Determine Spanner type from configuration"""
        # Check by instance configuration
        if "multi" in self.instance_config or "nam" in self.instance_config or "eur" in self.instance_config or "asia" in self.instance_config:
            return "multi_regional"
        elif "regional" in self.instance_config:
            return "regional"
            
        # Check by database count
        if len(self.databases) > 1:
            return "multi_database"
        elif len(self.databases) == 1:
            return "single_database"
            
        # Check by node count
        if self.node_count >= 3:
            return "high_availability"
        else:
            return "development"
            
    def _estimate_spanner_cost(self) -> float:
        """Estimate monthly cost for Cloud Spanner"""
        # Cloud Spanner pricing (simplified)
        
        # Node costs (730 hours per month)
        if self.processing_units:
            # Processing unit pricing
            units = self.processing_units
            if "multi" in self.instance_config:
                cost_per_100_units = 0.90  # $0.90/100 processing units/hour for multi-region
            else:
                cost_per_100_units = 0.30  # $0.30/100 processing units/hour for regional
                
            compute_cost = (units / 100) * cost_per_100_units * 730
        else:
            # Node pricing
            nodes = self.node_count
            if "multi" in self.instance_config:
                cost_per_node = 4.50  # $4.50/node/hour for multi-region
            else:
                cost_per_node = 1.50  # $1.50/node/hour for regional
                
            compute_cost = nodes * cost_per_node * 730
            
        # Storage costs (estimated 100GB per database)
        estimated_storage_gb = len(self.databases or [1]) * 100
        if "multi" in self.instance_config:
            storage_cost_per_gb = 0.50  # $0.50/GB/month for multi-region
        else:
            storage_cost_per_gb = 0.30  # $0.30/GB/month for regional
            
        storage_cost = estimated_storage_gb * storage_cost_per_gb
        
        # Backup costs (estimated 50% of data size)
        backup_storage_gb = estimated_storage_gb * 0.5 if self.backup_enabled else 0
        backup_cost = backup_storage_gb * 0.126  # $0.126/GB/month for backups
        
        # Network egress (estimated 10GB/month)
        egress_gb = 10
        egress_cost = egress_gb * 0.12  # $0.12/GB for egress
        
        total_cost = compute_cost + storage_cost + backup_cost + egress_cost
        
        return total_cost
        
    def _fetch_current_instance_state(self) -> Dict[str, Any]:
        """Fetch current state of Spanner instance"""
        try:
            if not self.spanner_admin_instance or not self.project_id:
                return {
                    "exists": False,
                    "instance_name": self.instance_name,
                    "error": "Spanner admin client not initialized or no project ID"
                }
                
            # Get instance info
            from google.cloud import spanner_admin_instance_v1
            
            try:
                instance_path = f"projects/{self.project_id}/instances/{self.instance_id or self.instance_name}"
                
                request = spanner_admin_instance_v1.GetInstanceRequest(
                    name=instance_path
                )
                
                instance = self.spanner_admin_instance.get_instance(request=request)
                
                return {
                    "exists": True,
                    "instance_name": self.instance_name,
                    "instance_id": instance.name.split("/")[-1],
                    "display_name": instance.display_name,
                    "config": instance.config.split("/")[-1],
                    "node_count": instance.node_count,
                    "processing_units": instance.processing_units,
                    "state": instance.state.name,
                    "create_time": instance.create_time,
                    "update_time": instance.update_time,
                    "labels": dict(instance.labels)
                }
                
            except Exception as e:
                if "not found" in str(e).lower():
                    return {
                        "exists": False,
                        "instance_name": self.instance_name,
                        "project_id": self.project_id,
                        "reason": "Instance not found"
                    }
                else:
                    return {
                        "exists": False,
                        "instance_name": self.instance_name,
                        "error": str(e)
                    }
                    
        except Exception as e:
            return {
                "exists": False,
                "instance_name": self.instance_name,
                "error": str(e)
            }
            
    def _discover_existing_instances(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Spanner instances in the project"""
        existing_instances = {}
        
        try:
            if not self.spanner_admin_instance or not self.project_id:
                return existing_instances
                
            from google.cloud import spanner_admin_instance_v1
            
            # List instances
            request = spanner_admin_instance_v1.ListInstancesRequest(
                parent=f"projects/{self.project_id}"
            )
            
            instances = self.spanner_admin_instance.list_instances(request=request)
            
            for instance in instances:
                instance_id = instance.name.split("/")[-1]
                
                instance_info = {
                    "instance_id": instance_id,
                    "instance_name": instance.display_name or instance_id,
                    "config": instance.config.split("/")[-1],
                    "node_count": instance.node_count,
                    "processing_units": instance.processing_units,
                    "state": instance.state.name,
                    "create_time": str(instance.create_time)[:19] if instance.create_time else "unknown",
                    "update_time": str(instance.update_time)[:19] if instance.update_time else "unknown",
                    "labels": dict(instance.labels),
                    "multi_region": "multi" in instance.config or any(region in instance.config for region in ["nam", "eur", "asia"])
                }
                
                # Get databases for this instance
                try:
                    db_request = spanner_admin_database_v1.ListDatabasesRequest(
                        parent=instance.name
                    )
                    
                    databases = self.spanner_admin_database.list_databases(request=db_request)
                    database_list = []
                    
                    for database in databases:
                        db_info = {
                            "database_id": database.name.split("/")[-1],
                            "create_time": str(database.create_time)[:19] if database.create_time else "unknown",
                            "version_retention_period": database.version_retention_period,
                            "earliest_version_time": str(database.earliest_version_time)[:19] if database.earliest_version_time else "unknown",
                            "default_leader": database.default_leader
                        }
                        database_list.append(db_info)
                        
                    instance_info["databases"] = database_list
                    instance_info["database_count"] = len(database_list)
                    
                except Exception as e:
                    instance_info["databases"] = []
                    instance_info["database_error"] = str(e)
                    
                existing_instances[instance_id] = instance_info
                
        except Exception as e:
            print(f"⚠️  Failed to discover existing instances: {str(e)}")
            
        return existing_instances
        
    def _discover_existing_databases(self, instance_id: str) -> Dict[str, Dict[str, Any]]:
        """Discover existing databases in a Spanner instance"""
        existing_databases = {}
        
        try:
            if not self.spanner_admin_database or not self.project_id:
                return existing_databases
                
            from google.cloud import spanner_admin_database_v1
            
            # List databases
            instance_path = f"projects/{self.project_id}/instances/{instance_id}"
            request = spanner_admin_database_v1.ListDatabasesRequest(
                parent=instance_path
            )
            
            databases = self.spanner_admin_database.list_databases(request=request)
            
            for database in databases:
                database_id = database.name.split("/")[-1]
                
                database_info = {
                    "database_id": database_id,
                    "instance_id": instance_id,
                    "create_time": str(database.create_time)[:19] if database.create_time else "unknown",
                    "version_retention_period": database.version_retention_period,
                    "earliest_version_time": str(database.earliest_version_time)[:19] if database.earliest_version_time else "unknown",
                    "default_leader": database.default_leader,
                    "encryption_config": bool(database.encryption_config)
                }
                
                existing_databases[database_id] = database_info
                
        except Exception as e:
            print(f"⚠️  Failed to discover existing databases: {str(e)}")
            
        return existing_databases
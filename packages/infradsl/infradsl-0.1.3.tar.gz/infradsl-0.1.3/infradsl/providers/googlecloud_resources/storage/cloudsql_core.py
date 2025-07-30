"""
GCP Cloud SQL Core Implementation

Core attributes and authentication for Google Cloud SQL databases.
Provides the foundation for the modular database system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class CloudSQLCore(BaseGcpResource):
    """
    Core class for Google Cloud SQL database functionality.
    
    This class provides:
    - Basic database attributes and configuration
    - Authentication setup
    - Common utilities for database operations
    """
    
    def __init__(self, name: str):
        """Initialize cloud sql core with instance name"""
        super().__init__(name)
        
        # Core database attributes
        self.instance_name = name
        self.database_version = "POSTGRES_15"  # Default version
        self.db_tier = "db-f1-micro"  # Default tier
        self.db_region = "us-central1"  # Default region
        self.db_zone = None
        self.db_database_name = "app_production"  # Default database name
        self.db_username = "app_user"  # Default username
        self.db_password = None  # Auto-generated if not set
        
        # Storage configuration
        self.disk_size_gb = 20  # Default disk size
        self.disk_type = "PD_SSD"  # Default to SSD
        self.disk_autoresize = True
        
        # Availability and backup
        self.availability_type = "ZONAL"  # Default to zonal
        self.backup_enabled = True
        self.backup_start_time = "03:00"
        self.deletion_protection = True  # Secure by default
        
        # Network and security
        self.authorized_networks = []
        self.ssl_mode = "REQUIRE"  # Secure by default
        self.public_ip = False  # Private by default
        
        # Advanced configuration
        self.database_flags = {}
        self.db_labels = {}
        self.insights_enabled = False
        self.maintenance_window_day = 7  # Sunday
        self.maintenance_window_hour = 4  # 4 AM
        
        # Connection and status
        self.connection_name = None
        self.instance_ip = None
        self.connection_info = None
        
        # State tracking
        self.instance_exists = False
        self.instance_created = False
        
    def _initialize_managers(self):
        """Initialize database-specific managers"""
        # Will be set up after authentication
        self.cloudsql_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Import here to avoid circular imports
        from ...googlecloud_managers.database.cloudsql_manager import CloudSQLManager
        self.cloudsql_manager = CloudSQLManager(self.gcp_client)
        
        # Set up connection name
        self.connection_name = f"{self.gcp_client.project_id}:{self.db_region}:{self.instance_name}"
        
    def _is_valid_database_version(self, version: str) -> bool:
        """Check if database version is valid for GCP Cloud SQL"""
        valid_versions = [
            # PostgreSQL versions
            "POSTGRES_11", "POSTGRES_12", "POSTGRES_13", "POSTGRES_14", "POSTGRES_15",
            # MySQL versions
            "MYSQL_5_7", "MYSQL_8_0", "MYSQL_8_0_18", "MYSQL_8_0_26", "MYSQL_8_0_27", "MYSQL_8_0_28", "MYSQL_8_0_31",
            # SQL Server versions
            "SQLSERVER_2017_STANDARD", "SQLSERVER_2017_ENTERPRISE", "SQLSERVER_2017_EXPRESS", "SQLSERVER_2017_WEB",
            "SQLSERVER_2019_STANDARD", "SQLSERVER_2019_ENTERPRISE", "SQLSERVER_2019_EXPRESS", "SQLSERVER_2019_WEB"
        ]
        return version in valid_versions
        
    def _is_valid_tier(self, tier: str) -> bool:
        """Check if machine tier is valid"""
        # Basic validation - real implementation would check current available tiers
        valid_prefixes = ["db-f1-", "db-g1-", "db-n1-", "db-n2-", "db-custom-"]
        return any(tier.startswith(prefix) for prefix in valid_prefixes)
        
    def _is_valid_region(self, region: str) -> bool:
        """Check if region is valid for GCP Cloud SQL"""
        gcp_regions = [
            'us-central1', 'us-east1', 'us-east4', 'us-west1', 'us-west2', 'us-west3', 'us-west4',
            'europe-north1', 'europe-west1', 'europe-west2', 'europe-west3', 'europe-west4', 'europe-west6',
            'asia-east1', 'asia-east2', 'asia-northeast1', 'asia-northeast2', 'asia-south1', 'asia-southeast1',
            'australia-southeast1', 'northamerica-northeast1', 'southamerica-east1'
        ]
        return region in gcp_regions
        
    def _is_valid_disk_type(self, disk_type: str) -> bool:
        """Check if disk type is valid"""
        valid_types = ["PD_SSD", "PD_HDD"]
        return disk_type in valid_types
        
    def _is_valid_availability_type(self, availability_type: str) -> bool:
        """Check if availability type is valid"""
        valid_types = ["ZONAL", "REGIONAL"]
        return availability_type in valid_types
        
    def _is_valid_ssl_mode(self, ssl_mode: str) -> bool:
        """Check if SSL mode is valid"""
        valid_modes = ["ALLOW", "REQUIRE", "VERIFY_CA", "VERIFY_IDENTITY"]
        return ssl_mode in valid_modes
        
    def _get_database_engine(self) -> str:
        """Get the database engine from version string"""
        if "POSTGRES" in self.database_version:
            return "PostgreSQL"
        elif "MYSQL" in self.database_version:
            return "MySQL"
        elif "SQLSERVER" in self.database_version:
            return "SQL Server"
        else:
            return "Unknown"
            
    def _get_engine_version(self) -> str:
        """Get the engine version number"""
        if "POSTGRES" in self.database_version:
            return self.database_version.replace("POSTGRES_", "")
        elif "MYSQL" in self.database_version:
            version = self.database_version.replace("MYSQL_", "")
            # Convert 8_0 to 8.0 format
            if "_" in version and len(version.split("_")) >= 2:
                parts = version.split("_")
                return f"{parts[0]}.{parts[1]}"
            return version
        elif "SQLSERVER" in self.database_version:
            return self.database_version.replace("SQLSERVER_", "").split("_")[0]
        else:
            return self.database_version
            
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the database instance from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get instance info if it exists
            if self.cloudsql_manager:
                instance_info = self.cloudsql_manager.get_instance_info(self.instance_name)
                
                if instance_info.get("exists", False):
                    return {
                        "exists": True,
                        "instance_name": self.instance_name,
                        "database_version": instance_info.get("database_version"),
                        "tier": instance_info.get("tier"),
                        "state": instance_info.get("state"),
                        "region": instance_info.get("region"),
                        "zone": instance_info.get("zone"),
                        "disk_size_gb": instance_info.get("disk_size_gb"),
                        "disk_type": instance_info.get("disk_type"),
                        "availability_type": instance_info.get("availability_type"),
                        "backup_enabled": instance_info.get("backup_enabled", False),
                        "backup_start_time": instance_info.get("backup_start_time"),
                        "ssl_mode": instance_info.get("ssl_mode"),
                        "deletion_protection": instance_info.get("deletion_protection", False),
                        "public_ip": instance_info.get("public_ip"),
                        "private_ip": instance_info.get("private_ip"),
                        "connection_name": instance_info.get("connection_name"),
                        "create_time": instance_info.get("create_time"),
                        "database_flags": instance_info.get("database_flags", {}),
                        "authorized_networks": instance_info.get("authorized_networks", []),
                        "maintenance_window": instance_info.get("maintenance_window"),
                        "insights_enabled": instance_info.get("insights_enabled", False)
                    }
                else:
                    return {
                        "exists": False,
                        "instance_name": self.instance_name
                    }
            else:
                return {
                    "exists": False,
                    "instance_name": self.instance_name,
                    "error": "CloudSQL manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch database state: {str(e)}")
            return {
                "exists": False,
                "instance_name": self.instance_name,
                "error": str(e)
            }
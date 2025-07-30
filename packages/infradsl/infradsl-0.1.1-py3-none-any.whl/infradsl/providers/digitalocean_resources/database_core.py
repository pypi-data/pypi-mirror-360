"""
DigitalOcean Database Core Implementation

Core attributes and authentication for DigitalOcean Managed Databases.
Provides the foundation for the modular database system.
"""

from typing import Dict, Any, List, Optional, Union
from .base_resource import BaseDigitalOceanResource


class DatabaseCore(BaseDigitalOceanResource):
    """
    Core class for DigitalOcean Database functionality.
    
    This class provides:
    - Basic database attributes and configuration
    - Authentication setup
    - Common utilities for database operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """Initialize Database core with database name"""
        super().__init__(name)
        
        # Core database attributes
        self.database_name = name
        self.database_description = f"DigitalOcean Managed Database: {name}"
        
        # Engine configuration
        self.engine = "pg"  # pg, mysql, redis
        self.version = None
        
        # Instance configuration
        self.size = "db-s-1vcpu-1gb"
        self.region = "nyc3"
        self.num_nodes = 1
        self.storage_size_mib = None
        
        # Network configuration
        self.private_network_uuid = None
        self.trusted_sources = []
        self.firewall_rules = []
        
        # Engine-specific configuration
        self.eviction_policy = None  # Redis only
        self.sql_mode = None  # MySQL only
        self.redis_config = {}  # Redis settings
        self.mysql_config = {}  # MySQL settings
        self.postgres_config = {}  # PostgreSQL settings
        
        # Backup and recovery
        self.backup_enabled = True
        self.backup_hour = 0  # UTC hour for daily backups
        self.backup_restore = None
        self.point_in_time_recovery = False
        
        # Maintenance configuration
        self.maintenance_window = {
            "day": "sunday",
            "hour": "02:00"
        }
        
        # Monitoring and alerts
        self.monitoring_enabled = True
        self.alerts_enabled = True
        self.alert_policy = {}
        
        # Labels and metadata
        self.database_tags = []
        self.database_labels = {}
        self.database_annotations = {}
        
        # State tracking
        self.database_exists = False
        self.database_created = False
        self.database_status = None
        self.connection_info = {}
        
        # Cost tracking
        self.estimated_monthly_cost = "$15.00/month"
        
        # Client references
        self.database_manager = None
        
    def _initialize_managers(self):
        """Initialize Database-specific managers"""
        self.database_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            from ..digitalocean_managers.database_manager import DatabaseManager
            self.database_manager = DatabaseManager(self.do_client)
                
        except Exception as e:
            print(f"⚠️  Database manager setup note: {str(e)}")
            
    def _is_valid_engine(self, engine: str) -> bool:
        """Check if database engine is valid"""
        valid_engines = ["pg", "mysql", "redis"]
        return engine in valid_engines
        
    def _is_valid_size(self, size: str) -> bool:
        """Check if database size is valid"""
        valid_sizes = [
            "db-s-1vcpu-1gb", "db-s-1vcpu-2gb", "db-s-1vcpu-3gb",
            "db-s-2vcpu-4gb", "db-s-4vcpu-8gb", "db-s-6vcpu-16gb",
            "db-s-8vcpu-32gb", "db-s-16vcpu-64gb"
        ]
        return size in valid_sizes
        
    def _is_valid_region(self, region: str) -> bool:
        """Check if region is valid for DigitalOcean"""
        valid_regions = [
            "nyc1", "nyc3", "ams2", "ams3", "sfo1", "sfo2", "sfo3",
            "sgp1", "lon1", "fra1", "tor1", "blr1", "syd1"
        ]
        return region in valid_regions
        
    def _validate_database_config(self, config: Dict[str, Any]) -> bool:
        """Validate database configuration"""
        required_fields = ["name", "engine", "size", "region"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate engine
        if not self._is_valid_engine(config["engine"]):
            return False
            
        # Validate size
        if not self._is_valid_size(config["size"]):
            return False
            
        # Validate region
        if not self._is_valid_region(config["region"]):
            return False
            
        # Validate nodes
        num_nodes = config.get("num_nodes", 1)
        if not isinstance(num_nodes, int) or num_nodes < 1 or num_nodes > 3:
            return False
            
        return True
        
    def _get_database_type_from_config(self) -> str:
        """Determine database type from configuration"""
        labels = self.database_labels
        
        # Check for purpose-based types
        purpose = labels.get("purpose", "").lower()
        if purpose:
            if "cache" in purpose:
                return "cache_database"
            elif "analytics" in purpose:
                return "analytics_database"
            elif "session" in purpose:
                return "session_store"
            elif "queue" in purpose:
                return "message_queue"
            elif "search" in purpose:
                return "search_database"
        
        # Check environment
        environment = labels.get("environment", "").lower()
        if environment:
            if environment == "development":
                return "development"
            elif environment == "staging":
                return "staging"
            elif environment == "production":
                return "production"
        
        # Check by engine and size
        if self.engine == "redis":
            if "1vcpu" in self.size:
                return "redis_cache"
            else:
                return "redis_enterprise"
        elif self.engine == "mysql":
            if self.num_nodes > 1:
                return "mysql_cluster"
            else:
                return "mysql_database"
        elif self.engine == "pg":
            if self.num_nodes > 1:
                return "postgres_cluster"
            else:
                return "postgres_database"
        
        return "managed_database"
        
    def _estimate_database_cost(self) -> float:
        """Estimate monthly cost for database usage"""
        # DigitalOcean Managed Database pricing (simplified)
        
        # Base pricing by size
        size_costs = {
            "db-s-1vcpu-1gb": 15.00,
            "db-s-1vcpu-2gb": 25.00,
            "db-s-1vcpu-3gb": 35.00,
            "db-s-2vcpu-4gb": 50.00,
            "db-s-4vcpu-8gb": 100.00,
            "db-s-6vcpu-16gb": 200.00,
            "db-s-8vcpu-32gb": 400.00,
            "db-s-16vcpu-64gb": 800.00
        }
        
        base_cost = size_costs.get(self.size, 15.00)
        
        # Multiply by number of nodes
        total_cost = base_cost * self.num_nodes
        
        # Add backup costs if larger than included storage
        if self.storage_size_mib and self.storage_size_mib > (10 * 1024):  # 10GB included
            extra_gb = (self.storage_size_mib - (10 * 1024)) / 1024
            total_cost += extra_gb * 0.10  # $0.10 per GB
        
        return total_cost
        
    def _fetch_current_database_state(self) -> Dict[str, Any]:
        """Fetch current state of database from DigitalOcean"""
        try:
            if not self.database_manager:
                return {
                    "exists": False,
                    "database_name": self.database_name,
                    "error": "No database manager available"
                }
            
            # Try to get current database info
            try:
                database_info = self.database_manager.get_database_info(self.database_name)
                
                if database_info:
                    current_state = {
                        "exists": True,
                        "database_name": self.database_name,
                        "id": database_info.get("id"),
                        "engine": database_info.get("engine"),
                        "version": database_info.get("version"),
                        "size": database_info.get("size"),
                        "region": database_info.get("region", {}).get("slug"),
                        "num_nodes": database_info.get("num_nodes"),
                        "status": database_info.get("status"),
                        "created_at": database_info.get("created_at"),
                        "connection": database_info.get("connection", {}),
                        "private_connection": database_info.get("private_connection", {}),
                        "console_url": f"https://cloud.digitalocean.com/databases/{database_info.get('id')}"
                    }
                    
                    return current_state
                    
            except Exception:
                # Database doesn't exist
                pass
            
            return {
                "exists": False,
                "database_name": self.database_name
            }
            
        except Exception as e:
            return {
                "exists": False,
                "database_name": self.database_name,
                "error": str(e)
            }
            
    def _discover_existing_databases(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing databases in the account"""
        existing_databases = {}
        
        try:
            if self.database_manager:
                databases = self.database_manager.list_databases()
                
                for database in databases:
                    database_name = database.get("name")
                    if database_name:
                        database_info = {
                            "database_name": database_name,
                            "id": database.get("id"),
                            "engine": database.get("engine"),
                            "version": database.get("version"),
                            "size": database.get("size"),
                            "region": database.get("region", {}).get("slug"),
                            "num_nodes": database.get("num_nodes"),
                            "status": database.get("status"),
                            "created_at": database.get("created_at")[:10] if database.get("created_at") else "unknown",
                            "tags": database.get("tags", []),
                            "private_network_uuid": database.get("private_network_uuid")
                        }
                        
                        existing_databases[database_name] = database_info
                        
        except Exception as e:
            print(f"⚠️  Failed to discover existing databases: {str(e)}")
            
        return existing_databases
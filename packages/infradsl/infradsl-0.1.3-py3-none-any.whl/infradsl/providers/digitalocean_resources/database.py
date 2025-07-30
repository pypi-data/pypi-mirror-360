"""
DigitalOcean Managed Database Resource

Provides Rails-like interface for creating and managing DigitalOcean managed databases
(PostgreSQL, MySQL, Redis).
"""

from typing import Dict, Any, List, Optional
from .base_resource import BaseDigitalOceanResource


class Database(BaseDigitalOceanResource):
    """DigitalOcean Managed Database with Rails-like API"""

    def __init__(self, name: str):
        super().__init__(name)
        self.config = {
            "name": name,
            "engine": "pg",  # Default to PostgreSQL
            "version": None,
            "size": "db-s-1vcpu-1gb",  # Default size
            "region": "nyc3",  # Default region
            "num_nodes": 1,  # Default to single node
            "private_network_uuid": None,
            "tags": [],
            "backup_restore": None,
            "eviction_policy": None,  # For Redis
            "sql_mode": None,  # For MySQL
            "storage_size_mib": None  # For custom storage
        }

    def _initialize_managers(self):
        """Initialize database-specific managers"""
        from ..digitalocean_managers.database_manager import DatabaseManager
        self.database_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        from ..digitalocean_managers.database_manager import DatabaseManager
        self.database_manager = DatabaseManager(self.do_client)

    # Engine configuration methods
    def postgresql(self, version: Optional[str] = None) -> 'Database':
        """Configure as PostgreSQL database"""
        self.config["engine"] = "pg"
        if version:
            self.config["version"] = version
        return self

    def mysql(self, version: Optional[str] = None) -> 'Database':
        """Configure as MySQL database"""
        self.config["engine"] = "mysql"
        if version:
            self.config["version"] = version
        return self

    def redis(self, version: Optional[str] = None) -> 'Database':
        """Configure as Redis database"""
        self.config["engine"] = "redis"
        if version:
            self.config["version"] = version
        return self

    # Size and performance configuration
    def size(self, size: str) -> 'Database':
        """Set database size (e.g., 'db-s-1vcpu-1gb', 'db-s-2vcpu-4gb')"""
        self.config["size"] = size
        return self

    def region(self, region: str) -> 'Database':
        """Set the region (e.g., 'nyc3', 'sfo3')"""
        self.config["region"] = region
        return self

    def nodes(self, num_nodes: int) -> 'Database':
        """Set number of nodes (for high availability)"""
        self.config["num_nodes"] = num_nodes
        return self

    def storage(self, size_gb: int) -> 'Database':
        """Set custom storage size in GB"""
        self.config["storage_size_mib"] = size_gb * 1024
        return self

    # Network configuration
    def private_network(self, vpc_uuid: str) -> 'Database':
        """Place database in a private network/VPC"""
        self.config["private_network_uuid"] = vpc_uuid
        return self

    def tags(self, tags: List[str]) -> 'Database':
        """Add tags to the database"""
        self.config["tags"] = tags
        return self

    # Engine-specific configurations
    def eviction_policy(self, policy: str) -> 'Database':
        """Set Redis eviction policy (allkeys-lru, volatile-lru, etc.)"""
        if self.config["engine"] != "redis":
            raise ValueError("Eviction policy can only be set for Redis databases")
        self.config["eviction_policy"] = policy
        return self

    def sql_mode(self, mode: str) -> 'Database':
        """Set MySQL SQL mode"""
        if self.config["engine"] != "mysql":
            raise ValueError("SQL mode can only be set for MySQL databases")
        self.config["sql_mode"] = mode
        return self

    # Backup configuration
    def restore_from_backup(self, backup_name: str) -> 'Database':
        """Restore database from backup"""
        self.config["backup_restore"] = {
            "type": "backup",
            "name": backup_name
        }
        return self

    # Rails-like convenience methods
    def development(self) -> 'Database':
        """Configure for development environment"""
        return self.size("db-s-1vcpu-1gb").nodes(1)

    def staging(self) -> 'Database':
        """Configure for staging environment"""
        return self.size("db-s-2vcpu-4gb").nodes(1)

    def production(self) -> 'Database':
        """Configure for production environment"""
        return self.size("db-s-4vcpu-8gb").nodes(3)

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created"""
        self._ensure_authenticated()
        return self.database_manager.preview_database(self.config)

    def create(self) -> Dict[str, Any]:
        """Create the managed database"""
        self._ensure_authenticated()
        
        self._print_resource_header("Managed Database", "Creating")
        
        # Print configuration summary
        engine_display = {
            "pg": "PostgreSQL",
            "mysql": "MySQL", 
            "redis": "Redis"
        }.get(self.config["engine"], self.config["engine"])
        
        print(f"📊 Database Engine: {engine_display}")
        print(f"🏷️  Database Name: {self.config['name']}")
        print(f"💾 Size: {self.config['size']}")
        print(f"📍 Region: {self.config['region']}")
        print(f"🔢 Nodes: {self.config['num_nodes']}")
        
        if self.config["private_network_uuid"]:
            print(f"🔒 Private Network: {self.config['private_network_uuid']}")
        
        result = self.database_manager.create_database(self.config)
        
        self._print_resource_footer("create database")
        return result

    def destroy(self) -> Dict[str, Any]:
        """Destroy the managed database"""
        self._ensure_authenticated()
        
        print(f"\n🗑️  Destroying database: {self.name}")
        result = self.database_manager.destroy_database(self.name)
        
        if result.get("success"):
            print(f"✅ Database '{self.name}' destroyed successfully")
        else:
            print(f"❌ Failed to destroy database: {result.get('error', 'Unknown error')}")
        
        return result
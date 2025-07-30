"""
DigitalOcean Database Manager

Handles creation, management, and monitoring of DigitalOcean managed databases.
"""

import time
from typing import Dict, Any, List, Optional
from digitalocean import Database as DODatabase


class DatabaseManager:
    """Manager for DigitalOcean managed databases"""

    def __init__(self, do_client):
        self.do_client = do_client
        self.client = do_client.client

    def preview_database(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview database configuration without creating it"""
        engine_display = {
            "pg": "PostgreSQL",
            "mysql": "MySQL", 
            "redis": "Redis"
        }.get(config["engine"], config["engine"])

        # Check if database already exists
        existing_db = self._find_database_by_name(config["name"])
        
        preview = {
            "action": "UPDATE" if existing_db else "CREATE",
            "name": config["name"],
            "engine": engine_display,
            "version": config.get("version", "Latest"),
            "size": config["size"],
            "region": config["region"],
            "num_nodes": config["num_nodes"],
            "private_network": config.get("private_network_uuid"),
            "tags": config.get("tags", []),
            "existing": bool(existing_db)
        }

        if existing_db:
            preview["current_status"] = existing_db.status
            preview["current_size"] = existing_db.size
            preview["current_nodes"] = existing_db.num_nodes

        # Add engine-specific configurations
        if config["engine"] == "redis" and config.get("eviction_policy"):
            preview["eviction_policy"] = config["eviction_policy"]
        
        if config["engine"] == "mysql" and config.get("sql_mode"):
            preview["sql_mode"] = config["sql_mode"]

        self._print_database_preview(preview)
        return preview

    def create_database(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update managed database"""
        try:
            # Check if database already exists
            existing_db = self._find_database_by_name(config["name"])
            
            if existing_db:
                print(f"🔄 Database '{config['name']}' already exists, checking for updates...")
                return self._handle_existing_database(existing_db, config)
            
            # Create new database
            print(f"🚀 Creating new {config['engine']} database...")
            
            database_params = self._build_database_params(config)
            
            # Create database using DigitalOcean API
            database = DODatabase(
                name=database_params["name"],
                engine=database_params["engine"],
                version=database_params.get("version"),
                region=database_params["region"],
                size=database_params["size"],
                num_nodes=database_params["num_nodes"],
                tags=database_params.get("tags", []),
                private_network_uuid=database_params.get("private_network_uuid"),
                **database_params.get("engine_config", {})
            )
            
            database.token = self.client.api_token
            database.create()
            
            # Wait for database to be ready
            print("⏳ Waiting for database to be ready...")
            ready_database = self._wait_for_database_ready(database.id)
            
            result = {
                "id": ready_database.id,
                "name": ready_database.name,
                "engine": ready_database.engine,
                "version": ready_database.version,
                "status": ready_database.status,
                "host": ready_database.host,
                "port": ready_database.port,
                "user": ready_database.user,
                "password": ready_database.password,
                "database": ready_database.database,
                "uri": ready_database.uri,
                "region": ready_database.region,
                "size": ready_database.size,
                "num_nodes": ready_database.num_nodes,
                "created_at": ready_database.created_at,
                "private_host": getattr(ready_database, 'private_host', None),
                "private_uri": getattr(ready_database, 'private_uri', None),
                "tags": ready_database.tags
            }
            
            self._print_database_result(result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to create database: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "success": False}

    def destroy_database(self, name: str) -> Dict[str, Any]:
        """Destroy managed database"""
        try:
            database = self._find_database_by_name(name)
            
            if not database:
                return {"error": f"Database '{name}' not found", "success": False}
            
            # Delete the database
            database.destroy()
            
            print(f"🗑️  Database '{name}' destruction initiated...")
            
            return {
                "success": True,
                "name": name,
                "id": database.id,
                "message": "Database destruction initiated"
            }
            
        except Exception as e:
            error_msg = f"Failed to destroy database: {str(e)}"
            return {"error": error_msg, "success": False}

    def _find_database_by_name(self, name: str):
        """Find database by name"""
        try:
            databases = self.client.get_all_databases()
            for db in databases:
                if db.name == name:
                    return db
            return None
        except Exception:
            return None

    def _build_database_params(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build database parameters for API call"""
        params = {
            "name": config["name"],
            "engine": config["engine"],
            "region": config["region"],
            "size": config["size"],
            "num_nodes": config["num_nodes"]
        }
        
        # Add optional parameters
        if config.get("version"):
            params["version"] = config["version"]
        
        if config.get("tags"):
            params["tags"] = config["tags"]
        
        if config.get("private_network_uuid"):
            params["private_network_uuid"] = config["private_network_uuid"]
        
        # Add engine-specific configuration
        engine_config = {}
        
        if config["engine"] == "redis":
            if config.get("eviction_policy"):
                engine_config["eviction_policy"] = config["eviction_policy"]
        
        elif config["engine"] == "mysql":
            if config.get("sql_mode"):
                engine_config["sql_mode"] = config["sql_mode"]
        
        if engine_config:
            params["engine_config"] = engine_config
        
        return params

    def _handle_existing_database(self, database, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle existing database - check for necessary updates"""
        updates_needed = []
        
        # Check if size needs updating
        if database.size != config["size"]:
            updates_needed.append(f"Size: {database.size} → {config['size']}")
        
        # Check if node count needs updating
        if database.num_nodes != config["num_nodes"]:
            updates_needed.append(f"Nodes: {database.num_nodes} → {config['num_nodes']}")
        
        if updates_needed:
            print(f"🔄 Updates needed:")
            for update in updates_needed:
                print(f"   • {update}")
            print(f"⚠️  Database resizing requires manual intervention via DigitalOcean console")
        else:
            print(f"✅ Database configuration is up to date")
        
        # Return current database information
        result = {
            "id": database.id,
            "name": database.name,
            "engine": database.engine,
            "version": database.version,
            "status": database.status,
            "host": database.host,
            "port": database.port,
            "user": database.user,
            "password": database.password,
            "database": database.database,
            "uri": database.uri,
            "region": database.region,
            "size": database.size,
            "num_nodes": database.num_nodes,
            "created_at": database.created_at,
            "private_host": getattr(database, 'private_host', None),
            "private_uri": getattr(database, 'private_uri', None),
            "tags": database.tags,
            "was_existing": True,
            "updates_needed": updates_needed
        }
        
        self._print_database_result(result)
        return result

    def _wait_for_database_ready(self, database_id: str, timeout: int = 600) -> DODatabase:
        """Wait for database to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                database = self.client.get_database(database_id)
                
                if database.status == "online":
                    print(f"✅ Database is online and ready!")
                    return database
                
                print(f"⏳ Database status: {database.status} (waiting...)")
                time.sleep(10)
                
            except Exception as e:
                print(f"⚠️  Error checking database status: {e}")
                time.sleep(10)
        
        raise TimeoutError(f"Database did not become ready within {timeout} seconds")

    def _print_database_preview(self, preview: Dict[str, Any]):
        """Print formatted database preview"""
        print(f"\n╭─ 📊 Database Preview: {preview['name']}")
        print(f"├─ 🔧 Action: {preview['action']}")
        print(f"├─ 🗄️  Engine: {preview['engine']} {preview['version']}")
        print(f"├─ 💾 Size: {preview['size']}")
        print(f"├─ 📍 Region: {preview['region']}")
        print(f"├─ 🔢 Nodes: {preview['num_nodes']}")
        
        if preview.get('private_network'):
            print(f"├─ 🔒 Private Network: {preview['private_network']}")
        
        if preview.get('tags'):
            print(f"├─ 🏷️  Tags: {', '.join(preview['tags'])}")
        
        if preview.get('eviction_policy'):
            print(f"├─ 🗑️  Eviction Policy: {preview['eviction_policy']}")
        
        if preview.get('sql_mode'):
            print(f"├─ 🔧 SQL Mode: {preview['sql_mode']}")
        
        if preview['existing']:
            print(f"├─ 📊 Current Status: {preview.get('current_status', 'Unknown')}")
            print(f"├─ 📏 Current Size: {preview.get('current_size', 'Unknown')}")
            print(f"├─ 🔢 Current Nodes: {preview.get('current_nodes', 'Unknown')}")
        
        print(f"╰─ 🎯 Action: {'Update existing database' if preview['existing'] else 'Create new database'}")

    def _print_database_result(self, result: Dict[str, Any]):
        """Print formatted database creation result"""
        print(f"\n╭─ 📊 Database: {result['name']}")
        print(f"├─ 🆔 ID: {result['id']}")
        print(f"├─ 🗄️  Engine: {result['engine']} {result.get('version', '')}")
        print(f"├─ 🟢 Status: {result['status']}")
        print(f"├─ 🌐 Host: {result['host']}")
        print(f"├─ 🔌 Port: {result['port']}")
        print(f"├─ 👤 User: {result['user']}")
        print(f"├─ 🗃️  Database: {result['database']}")
        
        if result.get('private_host'):
            print(f"├─ 🔒 Private Host: {result['private_host']}")
        
        print(f"├─ 🔗 Connection URI: {result['uri'][:50]}...")
        print(f"├─ 📍 Region: {result['region']}")
        print(f"├─ 💾 Size: {result['size']}")
        print(f"├─ 🔢 Nodes: {result['num_nodes']}")
        
        if result.get('tags'):
            print(f"├─ 🏷️  Tags: {', '.join(result['tags'])}")
        
        if result.get('was_existing'):
            print(f"├─ ♻️  Action: Updated existing database")
            if result.get('updates_needed'):
                print(f"├─ ⚠️  Manual Updates Needed: {len(result['updates_needed'])}")
        else:
            print(f"├─ ✨ Action: Created new database")
        
        print(f"╰─ 📅 Created: {result.get('created_at', 'Recently')}")
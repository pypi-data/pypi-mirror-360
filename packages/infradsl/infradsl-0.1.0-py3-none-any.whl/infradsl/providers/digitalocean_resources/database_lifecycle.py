"""
DigitalOcean Database Lifecycle Implementation

Lifecycle operations for DigitalOcean Managed Databases.
Handles creation, updates, destruction, and state management.
"""

from typing import Dict, Any, List, Optional
import time


class DatabaseLifecycleMixin:
    """
    Lifecycle operations for DigitalOcean Database.
    
    This mixin provides:
    - Database creation and deletion
    - Configuration updates and scaling
    - State management and drift detection
    - Backup and restore operations
    - Health checks and monitoring
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview the database configuration without creating it"""
        config = self._get_database_config()
        
        # Estimate costs
        monthly_cost = self._estimate_database_cost()
        
        # Engine display name
        engine_names = {"pg": "PostgreSQL", "mysql": "MySQL", "redis": "Redis"}
        engine_display = engine_names.get(self.engine, self.engine)
        
        # Size details
        size_info = self._parse_size_string(self.size)
        
        preview = {
            "resource_type": "DigitalOcean Managed Database",
            "database_name": self.database_name,
            "description": self.database_description,
            
            # Engine configuration
            "engine": {
                "type": engine_display,
                "version": self.version or "latest",
                "engine_code": self.engine
            },
            
            # Instance configuration
            "instance": {
                "size": self.size,
                "vcpus": size_info["vcpus"],
                "memory_gb": size_info["memory_gb"],
                "nodes": self.num_nodes,
                "region": self.region,
                "storage_gb": self.storage_size_mib // 1024 if self.storage_size_mib else "default"
            },
            
            # Network configuration
            "network": {
                "private_network": self.private_network_uuid is not None,
                "private_network_uuid": self.private_network_uuid,
                "trusted_sources": len(self.trusted_sources),
                "firewall_rules": len(self.firewall_rules)
            },
            
            # Security and backup
            "backup": {
                "enabled": self.backup_enabled,
                "hour": self.backup_hour,
                "point_in_time_recovery": self.point_in_time_recovery
            },
            
            # Monitoring
            "monitoring": {
                "enabled": self.monitoring_enabled,
                "alerts": self.alerts_enabled,
                "alert_policies": len(self.alert_policy)
            },
            
            # Maintenance
            "maintenance": self.maintenance_window,
            
            # Labels and tags
            "metadata": {
                "tags": self.database_tags,
                "labels": self.database_labels,
                "annotations": self.database_annotations
            },
            
            # Cost estimation
            "cost": {
                "estimated_monthly": f"${monthly_cost:.2f}",
                "breakdown": self._get_cost_breakdown()
            },
            
            # Generated configuration
            "config": config
        }
        return preview
    
    def create(self) -> Dict[str, Any]:
        """Create the managed database"""
        self._ensure_authenticated()
        
        print(f"\\n🗄️  Creating DigitalOcean Managed Database: {self.database_name}")
        
        # Validate configuration
        config = self._get_database_config()
        if not self._validate_database_config(config):
            raise ValueError("Invalid database configuration")
        
        # Display configuration summary
        self._display_creation_summary()
        
        try:
            # Check if database already exists
            current_state = self._fetch_current_database_state()
            if current_state.get("exists"):
                print(f"⚠️  Database '{self.database_name}' already exists")
                return {
                    "status": "exists",
                    "database_info": current_state,
                    "message": "Database already exists"
                }
            
            # Create the database
            print(f"🚀 Creating database...")
            
            if self.database_manager:
                result = self.database_manager.create_database(config)
                
                if result.get("success"):
                    self.database_exists = True
                    self.database_created = True
                    self.database_status = "creating"
                    
                    database_info = result.get("database", {})
                    database_id = database_info.get("id")
                    
                    print(f"✅ Database creation initiated")
                    print(f"📊 Database ID: {database_id}")
                    print(f"⏰ Status: Creating (this may take several minutes)")
                    
                    # Wait for database to be ready
                    if database_id:
                        print(f"⏳ Waiting for database to be ready...")
                        final_status = self._wait_for_database_ready(database_id)
                        
                        if final_status == "online":
                            print(f"✅ Database is ready!")
                            
                            # Get connection info
                            updated_info = self.database_manager.get_database_info(self.database_name)
                            if updated_info:
                                self._display_connection_info(updated_info)
                        else:
                            print(f"⚠️  Database creation completed but status is: {final_status}")
                    
                    return {
                        "status": "created",
                        "database_info": database_info,
                        "console_url": f"https://cloud.digitalocean.com/databases/{database_id}"
                    }
                else:
                    error_msg = result.get("error", "Unknown error")
                    print(f"❌ Database creation failed: {error_msg}")
                    return {
                        "status": "failed",
                        "error": error_msg
                    }
            else:
                raise Exception("Database manager not available")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Database creation failed: {error_msg}")
            return {
                "status": "failed",
                "error": error_msg
            }
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy the managed database"""
        self._ensure_authenticated()
        
        print(f"\\n🗑️  Destroying database: {self.database_name}")
        
        try:
            # Check if database exists
            current_state = self._fetch_current_database_state()
            if not current_state.get("exists"):
                print(f"⚠️  Database '{self.database_name}' does not exist")
                return {
                    "status": "not_found",
                    "message": "Database does not exist"
                }
            
            database_id = current_state.get("id")
            
            # Confirm destruction for production databases
            if "production" in self.database_tags or self.database_labels.get("environment") == "production":
                print(f"⚠️  WARNING: This is a production database!")
                print(f"🔒 Data will be permanently deleted")
            
            if self.database_manager:
                print(f"🗑️  Deleting database...")
                result = self.database_manager.destroy_database(self.database_name)
                
                if result.get("success"):
                    self.database_exists = False
                    self.database_status = "deleted"
                    
                    print(f"✅ Database '{self.database_name}' destroyed successfully")
                    return {
                        "status": "destroyed",
                        "database_name": self.database_name
                    }
                else:
                    error_msg = result.get("error", "Unknown error")
                    print(f"❌ Failed to destroy database: {error_msg}")
                    return {
                        "status": "failed",
                        "error": error_msg
                    }
            else:
                raise Exception("Database manager not available")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Database destruction failed: {error_msg}")
            return {
                "status": "failed",
                "error": error_msg
            }
    
    def update(self) -> Dict[str, Any]:
        """Update database configuration (resize, add nodes, etc.)"""
        self._ensure_authenticated()
        
        print(f"\\n🔄 Updating database: {self.database_name}")
        
        try:
            # Check if database exists
            current_state = self._fetch_current_database_state()
            if not current_state.get("exists"):
                print(f"❌ Database '{self.database_name}' does not exist")
                return {
                    "status": "not_found",
                    "message": "Database does not exist"
                }
            
            # Determine what changes need to be made
            changes = self._detect_configuration_changes(current_state)
            
            if not changes:
                print(f"✅ Database configuration is up to date")
                return {
                    "status": "up_to_date",
                    "message": "No changes required"
                }
            
            print(f"📊 Detected changes: {', '.join(changes.keys())}")
            
            if self.database_manager:
                # Apply updates
                result = self.database_manager.update_database(self.database_name, changes)
                
                if result.get("success"):
                    print(f"✅ Database update initiated")
                    
                    # Some updates require waiting
                    if "size" in changes or "num_nodes" in changes:
                        print(f"⏳ Waiting for resize/scaling to complete...")
                        database_id = current_state.get("id")
                        self._wait_for_database_ready(database_id)
                        print(f"✅ Database update completed")
                    
                    return {
                        "status": "updated",
                        "changes": changes,
                        "database_name": self.database_name
                    }
                else:
                    error_msg = result.get("error", "Unknown error")
                    print(f"❌ Database update failed: {error_msg}")
                    return {
                        "status": "failed",
                        "error": error_msg
                    }
            else:
                raise Exception("Database manager not available")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Database update failed: {error_msg}")
            return {
                "status": "failed",
                "error": error_msg
            }
    
    # Helper methods for lifecycle operations
    def _get_database_config(self) -> Dict[str, Any]:
        """Get complete database configuration"""
        config = {
            "name": self.database_name,
            "engine": self.engine,
            "size": self.size,
            "region": self.region,
            "num_nodes": self.num_nodes,
            "tags": self.database_tags
        }
        
        # Optional configurations
        if self.version:
            config["version"] = self.version
        if self.private_network_uuid:
            config["private_network_uuid"] = self.private_network_uuid
        if self.storage_size_mib:
            config["storage_size_mib"] = self.storage_size_mib
        if self.backup_restore:
            config["backup_restore"] = self.backup_restore
        
        # Engine-specific configurations
        if self.engine == "redis" and self.eviction_policy:
            config["eviction_policy"] = self.eviction_policy
        if self.engine == "mysql" and self.sql_mode:
            config["sql_mode"] = self.sql_mode
        
        return config
    
    def _display_creation_summary(self):
        """Display creation summary"""
        engine_names = {"pg": "PostgreSQL", "mysql": "MySQL", "redis": "Redis"}
        engine_display = engine_names.get(self.engine, self.engine)
        
        print(f"📊 Engine: {engine_display}")
        if self.version:
            print(f"🔖 Version: {self.version}")
        print(f"💾 Size: {self.size}")
        print(f"📍 Region: {self.region}")
        print(f"🔢 Nodes: {self.num_nodes}")
        
        if self.private_network_uuid:
            print(f"🔒 Private Network: {self.private_network_uuid}")
        
        if self.database_tags:
            print(f"🏷️  Tags: {', '.join(self.database_tags)}")
        
        cost = self._estimate_database_cost()
        print(f"💰 Estimated Cost: ${cost:.2f}/month")
    
    def _display_connection_info(self, database_info: Dict[str, Any]):
        """Display database connection information"""
        connection = database_info.get("connection", {})
        private_connection = database_info.get("private_connection", {})
        
        print(f"\\n📡 Connection Information:")
        
        if connection:
            print(f"   🌐 Public Connection:")
            print(f"      Host: {connection.get('host', 'N/A')}")
            print(f"      Port: {connection.get('port', 'N/A')}")
            print(f"      Database: {connection.get('database', 'N/A')}")
            print(f"      User: {connection.get('user', 'N/A')}")
            print(f"      SSL: {connection.get('ssl', False)}")
        
        if private_connection:
            print(f"   🔒 Private Connection:")
            print(f"      Host: {private_connection.get('host', 'N/A')}")
            print(f"      Port: {private_connection.get('port', 'N/A')}")
        
        print(f"\\n🌐 Console: https://cloud.digitalocean.com/databases/{database_info.get('id')}")
    
    def _wait_for_database_ready(self, database_id: str, timeout: int = 600) -> str:
        """Wait for database to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if self.database_manager:
                    database_info = self.database_manager.get_database_by_id(database_id)
                    if database_info:
                        status = database_info.get("status", "unknown")
                        
                        if status == "online":
                            return "online"
                        elif status in ["failed", "error"]:
                            return status
                        
                        # Still creating, wait and check again
                        time.sleep(30)
                    else:
                        break
                else:
                    break
                    
            except Exception:
                time.sleep(30)
        
        return "timeout"
    
    def _detect_configuration_changes(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Detect what configuration changes are needed"""
        changes = {}
        
        # Check size changes
        if current_state.get("size") != self.size:
            changes["size"] = self.size
        
        # Check node count changes
        if current_state.get("num_nodes") != self.num_nodes:
            changes["num_nodes"] = self.num_nodes
        
        # Check tag changes
        current_tags = set(current_state.get("tags", []))
        new_tags = set(self.database_tags)
        if current_tags != new_tags:
            changes["tags"] = self.database_tags
        
        return changes
    
    def _parse_size_string(self, size: str) -> Dict[str, Any]:
        """Parse size string to extract vCPUs and memory"""
        # Example: "db-s-2vcpu-4gb" -> {"vcpus": 2, "memory_gb": 4}
        parts = size.split("-")
        
        vcpus = 1
        memory_gb = 1
        
        for part in parts:
            if "vcpu" in part:
                vcpus = int(part.replace("vcpu", ""))
            elif "gb" in part:
                memory_gb = int(part.replace("gb", ""))
        
        return {"vcpus": vcpus, "memory_gb": memory_gb}
    
    def _get_cost_breakdown(self) -> Dict[str, str]:
        """Get detailed cost breakdown"""
        base_cost = self._estimate_database_cost() / self.num_nodes
        total_cost = self._estimate_database_cost()
        
        breakdown = {
            "base_instance": f"${base_cost:.2f} x {self.num_nodes} nodes",
            "total_monthly": f"${total_cost:.2f}"
        }
        
        if self.storage_size_mib and self.storage_size_mib > (10 * 1024):
            extra_gb = (self.storage_size_mib - (10 * 1024)) / 1024
            storage_cost = extra_gb * 0.10
            breakdown["extra_storage"] = f"${storage_cost:.2f} ({extra_gb:.0f}GB)"
        
        return breakdown
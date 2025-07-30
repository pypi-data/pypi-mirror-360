"""
Google Cloud SQL Manager

Rails-like database management with intelligent defaults, security best practices,
and developer-friendly operations. Follows InfraDSL's convention over configuration
philosophy for database infrastructure.
"""

import os
import time
import secrets
import string
from typing import Dict, Any, List, Optional, Union
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from pydantic import BaseModel
from ..gcp_client import GcpClient


class DatabaseConfig(BaseModel):
    """Configuration for Google Cloud SQL database instance"""
    instance_name: str
    database_version: str = "POSTGRES_15"  # Rails-like modern default
    tier: str = "db-f1-micro"  # Cost-effective default
    region: str = "us-central1"
    zone: str = None  # Optional specific zone
    disk_size_gb: int = 10  # Minimum viable size
    disk_type: str = "PD_SSD"  # Fast storage by default
    disk_autoresize: bool = True  # Rails convention: grow as needed
    availability_type: str = "ZONAL"  # Regional for production
    backup_enabled: bool = True  # Security by default
    backup_start_time: str = "03:00"  # 3 AM backup window
    maintenance_window_day: int = 7  # Sunday
    maintenance_window_hour: int = 4  # 4 AM maintenance
    deletion_protection: bool = True  # Safety by default
    insights_enabled: bool = True  # Monitoring by default
    ssl_mode: str = "REQUIRE"  # Security by default
    authorized_networks: List[Dict[str, str]] = []
    database_flags: Dict[str, str] = {}
    labels: Optional[Dict[str, str]] = None

    # Database and user configuration
    database_name: str = "app_production"  # Rails convention
    username: str = "app_user"  # Rails convention
    password: Optional[str] = None  # Auto-generated if not provided


class CloudSQLManager:
    """
    Manages Google Cloud SQL database operations with Rails-like conventions.

    Features:
    - Smart defaults for security and performance
    - Intelligent backup and maintenance scheduling
    - Convention-based database and user management
    - Developer-friendly error messages
    """

    def __init__(self, gcp_client: GcpClient):
        self.gcp_client = gcp_client
        self._sql_client = None
        self._project_id = None

    @property
    def sql_client(self):
        """Get the Cloud SQL client (lazy loading after authentication)"""
        if not self._sql_client:
            self._sql_client = discovery.build(
                'sqladmin', 'v1',
                credentials=self.gcp_client.credentials
            )
        return self._sql_client

    @property
    def project_id(self):
        """Get the project ID (lazy loading after authentication)"""
        if not self._project_id:
            self._project_id = self.gcp_client.project
        return self._project_id

    def create_database_instance(self, config: DatabaseConfig) -> Dict[str, Any]:
        """
        Create a Cloud SQL database instance with Rails-like conventions.

        Args:
            config: Database configuration

        Returns:
            Dict containing database instance information

        Raises:
            Exception: If database creation fails
        """
        if not self.gcp_client.check_authenticated():
            raise ValueError("Authentication not set. Use .authenticate() first.")

        try:
            # Check if instance already exists
            existing_instance = self._get_instance(config.instance_name)
            if existing_instance:
                print(f"🔄 Database instance '{config.instance_name}' already exists")
                return self._instance_to_dict(existing_instance, config)

            print(f"🗄️ Creating Cloud SQL instance: {config.instance_name}")
            print(f"   🔧 Engine: {config.database_version}")
            print(f"   📍 Region: {config.region}")
            print(f"   💾 Tier: {config.tier}")

            # Generate secure password if not provided
            if not config.password:
                config.password = self._generate_secure_password()
                print(f"   🔑 Generated secure password for user: {config.username}")

            # Build database instance configuration
            instance_body = self._build_instance_config(config)

            # Create the instance
            operation = self.sql_client.instances().insert(
                project=self.project_id,
                body=instance_body
            ).execute()
            print(f"✅ Database instance creation initiated: {config.instance_name}")
            print(f"   🔄 Operation: {operation.name}")
            print(f"   ⏳ This may take 5-10 minutes to complete")

            # Wait for the operation to complete
            self._wait_for_operation(operation)

            # Get the created instance
            created_instance = self._get_instance(config.instance_name)
            if not created_instance:
                raise Exception("Instance creation completed but instance not found")

            print(f"✅ Database instance ready: {config.instance_name}")

            # Create database and user
            self._create_database_and_user(config)

            return self._instance_to_dict(created_instance, config)

        except HttpError as e:
            if e.resp.status == 409:
                # Instance name already taken
                raise Exception(
                    f"Database instance name '{config.instance_name}' is already taken. "
                    f"Try: {config.instance_name}-{secrets.token_hex(4)}"
                )
            raise Exception(f"HTTP error: {e}")
        except Exception as e:
            raise Exception(f"Failed to create database instance: {str(e)}")

    def get_instance_info(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """Get database instance information"""
        try:
            instance = self._get_instance(instance_name)
            if not instance:
                return None

            return self._instance_to_dict(instance)
        except Exception as e:
            raise Exception(f"Failed to get instance info: {str(e)}")

    def delete_instance(self, instance_name: str, force: bool = False) -> bool:
        """
        Delete a Cloud SQL database instance.

        Args:
            instance_name: Name of instance to delete
            force: If True, disable deletion protection first

        Returns:
            bool: True if deletion successful
        """
        try:
            instance = self._get_instance(instance_name)
            if not instance:
                print(f"✅ Database instance '{instance_name}' doesn't exist - nothing to delete")
                return True

            print(f"🗑️  Deleting database instance: {instance_name}")

            # Check deletion protection
            if instance.settings.deletion_protection_enabled and not force:
                print(f"⚠️  Instance '{instance_name}' has deletion protection enabled")
                print(f"   Use force=True to disable protection and delete")
                return False

            # Disable deletion protection if force is True
            if force and instance.settings.deletion_protection_enabled:
                print(f"🔓 Disabling deletion protection...")
                self._disable_deletion_protection(instance_name)

            # Delete the instance
            operation = self.sql_client.instances().delete(
                project=self.project_id,
                instance=instance_name
            ).execute()
            print(f"✅ Database instance deletion initiated: {instance_name}")
            print(f"   🔄 Operation: {operation.name}")
            print(f"   ⏳ This may take a few minutes to complete")

            # Wait for the operation to complete
            self._wait_for_operation(operation)

            print(f"✅ Database instance deleted: {instance_name}")
            return True

        except Exception as e:
            print(f"⚠️  Failed to delete instance {instance_name}: {str(e)}")
            return False

    def create_database(self, instance_name: str, database_name: str) -> Dict[str, Any]:
        """Create a database within an instance"""
        try:
            print(f"📊 Creating database: {database_name}")

            database_body = {
                "name": database_name,
                "instance": instance_name,
                "project": self.project_id
            }

            operation = self.sql_client.databases().insert(
                project=self.project_id,
                instance=instance_name,
                body=database_body
            ).execute()

            print(f"✅ Database created: {database_name}")
            return {"database_name": database_name, "instance": instance_name}

        except Exception as e:
            raise Exception(f"Failed to create database: {str(e)}")

    def create_user(self, instance_name: str, username: str, password: str) -> Dict[str, Any]:
        """Create a database user"""
        try:
            print(f"👤 Creating database user: {username}")

            user_body = {
                "name": username,
                "password": password,
                "instance": instance_name,
                "project": self.project_id
            }

            operation = self.sql_client.users().insert(
                project=self.project_id,
                instance=instance_name,
                body=user_body
            ).execute()

            print(f"✅ Database user created: {username}")
            return {"username": username, "instance": instance_name}

        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")

    def get_connection_info(self, instance_name: str, config: DatabaseConfig = None) -> Dict[str, Any]:
        """Get database connection information"""
        try:
            instance = self._get_instance(instance_name)
            if not instance:
                raise Exception(f"Instance '{instance_name}' not found")

            connection_info = {
                "host": instance["ipAddresses"][0]["ipAddress"] if instance.get("ipAddresses") else None,
                "port": 5432 if "POSTGRES" in instance["databaseVersion"] else 3306,
                "instance_name": instance_name,
                "project_id": self.project_id,
                "region": instance["region"],
                "connection_name": f"{self.project_id}:{instance['region']}:{instance_name}"
            }

            if config:
                connection_info.update({
                    "database": config.database_name,
                    "username": config.username,
                    "password": config.password
                })

            return connection_info

        except Exception as e:
            raise Exception(f"Failed to get connection info: {str(e)}")

    def _get_instance(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """Get database instance by name"""
        try:
            return self.sql_client.instances().get(
                project=self.project_id,
                instance=instance_name
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                return None
            return None
        except Exception:
            return None

    def _build_instance_config(self, config: DatabaseConfig) -> Dict[str, Any]:
        """Build database instance configuration"""

        # Settings configuration
        settings = {
            "tier": config.tier,
            "availabilityType": config.availability_type,
            "dataDiskSizeGb": config.disk_size_gb,
            "dataDiskType": config.disk_type,
            "storageAutoResize": config.disk_autoresize,
            "deletionProtectionEnabled": config.deletion_protection,
            "insightsConfig": {
                "queryInsightsEnabled": config.insights_enabled,
                "recordApplicationTags": True,
                "recordClientAddress": True
            },
            "ipConfiguration": {
                "authorizedNetworks": [
                    {"value": net["value"], "name": net.get("name", "")}
                    for net in config.authorized_networks
                ],
                "requireSsl": config.ssl_mode == "REQUIRE"
            },
            "backupConfiguration": {
                "enabled": config.backup_enabled,
                "startTime": config.backup_start_time,
                "location": config.region,
                "pointInTimeRecoveryEnabled": True,
                "transactionLogRetentionDays": 7
            },
            "maintenanceWindow": {
                "day": config.maintenance_window_day,
                "hour": config.maintenance_window_hour,
                "updateTrack": "stable"
            },
            "databaseFlags": [
                {"name": key, "value": value}
                for key, value in config.database_flags.items()
            ]
        }

        # Instance configuration
        instance = {
            "name": config.instance_name,
            "databaseVersion": config.database_version,
            "region": config.region,
            "settings": settings
        }

        if config.zone:
            instance["gceZone"] = config.zone

        if config.labels:
            instance["userLabels"] = config.labels

        return instance

    def _create_database_and_user(self, config: DatabaseConfig):
        """Create database and user after instance is ready"""
        try:
            # Create database
            self.create_database(config.instance_name, config.database_name)

            # Create user
            self.create_user(config.instance_name, config.username, config.password)

        except Exception as e:
            print(f"⚠️  Warning: Failed to create database/user: {e}")

    def _generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(characters) for _ in range(length))

    def _disable_deletion_protection(self, instance_name: str):
        """Disable deletion protection on an instance"""
        try:
            instance = self._get_instance(instance_name)
            if not instance:
                return

            # Update settings to disable deletion protection
            instance["settings"]["deletionProtectionEnabled"] = False

            operation = self.sql_client.instances().patch(
                project=self.project_id,
                instance=instance_name,
                body=instance
            ).execute()
            self._wait_for_operation(operation)

        except Exception as e:
            raise Exception(f"Failed to disable deletion protection: {str(e)}")

    def _wait_for_operation(self, operation, timeout: int = 600):
        """Wait for a Cloud SQL operation to complete"""
        try:
            print(f"⏳ Waiting for operation to complete (timeout: {timeout}s)...")
            start_time = time.time()

            while time.time() - start_time < timeout:
                current_op = self.sql_client.operations().get(
                    project=self.project_id,
                    operation=operation["name"]
                ).execute()

                if current_op["status"] == "DONE":
                    if current_op.get("error"):
                        error_msg = current_op["error"].get("message", "Unknown error")
                        raise Exception(f"Operation failed: {error_msg}")

                    print(f"✅ Operation completed successfully")
                    return current_op

                elif current_op["status"] == "RUNNING":
                    elapsed = int(time.time() - start_time)
                    print(f"   ⏳ Still running... (elapsed: {elapsed}s)")
                    time.sleep(10)

                else:
                    print(f"   📋 Operation status: {current_op['status']}")
                    time.sleep(5)

            raise Exception(f"Operation timed out after {timeout} seconds")

        except Exception as e:
            print(f"   ❌ Operation failed: {e}")
            raise e

    def _instance_to_dict(self, instance: Dict[str, Any], config: DatabaseConfig = None) -> Dict[str, Any]:
        """Convert instance object to dictionary"""
        result = {
            "instance_name": instance["name"],
            "database_version": instance["databaseVersion"],
            "region": instance["region"],
            "state": instance.get("state", "UNKNOWN"),
            "tier": instance.get("settings", {}).get("tier"),
            "disk_size_gb": instance.get("settings", {}).get("dataDiskSizeGb"),
            "creation_time": instance.get("createTime"),
            "ip_addresses": [
                {"ip": ip["ipAddress"], "type": ip["type"]}
                for ip in instance.get("ipAddresses", [])
            ],
            "project_id": self.project_id,
            "connection_name": f"{self.project_id}:{instance['region']}:{instance['name']}"
        }

        if config:
            result.update({
                "database_name": config.database_name,
                "username": config.username,
                "password": config.password if config.password else "[HIDDEN]"
            })

        return result

    def get_smart_database_flags(self, db_type: str = "postgres", use_case: str = "general") -> Dict[str, str]:
        """
        Get smart database flags based on database type and use case.

        Args:
            db_type: Database type ("postgres", "mysql")
            use_case: Use case ("general", "analytics", "web", "api")

        Returns:
            Dict of database flags
        """
        if db_type == "postgres":
            if use_case == "analytics":
                return {
                    "shared_preload_libraries": "pg_stat_statements",
                    "max_connections": "200",
                    "work_mem": "256MB",
                    "maintenance_work_mem": "512MB",
                    "effective_cache_size": "1GB"
                }
            elif use_case == "web":
                return {
                    "shared_preload_libraries": "pg_stat_statements",
                    "max_connections": "100",
                    "shared_buffers": "256MB",
                    "effective_cache_size": "512MB"
                }
            else:  # general
                return {
                    "shared_preload_libraries": "pg_stat_statements",
                    "max_connections": "100"
                }
        elif db_type == "mysql":
            if use_case == "analytics":
                return {
                    "innodb_buffer_pool_size": "1073741824",  # 1GB
                    "max_connections": "200",
                    "query_cache_size": "268435456"  # 256MB
                }
            else:  # general or web
                return {
                    "innodb_buffer_pool_size": "536870912",  # 512MB
                    "max_connections": "100"
                }

        return {}

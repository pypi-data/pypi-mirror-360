"""
GCP Cloud SQL Lifecycle Mixin

Lifecycle operations for Google Cloud SQL databases.
Handles create, update, preview, and destroy operations.
"""

from typing import Dict, Any, List
import uuid


class CloudSQLLifecycleMixin:
    """
    Mixin for Cloud SQL database lifecycle operations (create, update, destroy).
    
    This mixin provides:
    - Preview functionality to show planned changes
    - Database instance creation and configuration
    - Database destruction
    - Connection information management
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()
        
        # Discover existing databases to determine what will happen
        existing_databases = self._discover_existing_databases()
        
        # Determine what will happen
        instance_exists = self.instance_name in existing_databases
        to_create = [] if instance_exists else [self.instance_name]
        to_keep = [self.instance_name] if instance_exists else []
        to_remove = [name for name in existing_databases.keys() if name != self.instance_name]
        
        self._display_preview(to_create, to_keep, to_remove, existing_databases)
        
        return {
            'resource_type': 'GCP Cloud SQL Database',
            'instance_name': self.instance_name,
            'connection_name': self.connection_name,
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'existing_databases': existing_databases,
            'database_version': self.database_version,
            'engine': self._get_database_engine(),
            'version': self._get_engine_version(),
            'tier': self.db_tier,
            'region': self.db_region,
            'availability_type': self.availability_type,
            'estimated_deployment_time': '5-15 minutes',
            'estimated_monthly_cost': self._estimate_monthly_cost()
        }
    
    def _display_preview(self, to_create: List[str], to_keep: List[str], to_remove: List[str], existing_databases: Dict[str, Any]):
        """Display preview information in a clean format"""
        print(f"\n💾 Cloud SQL Database Preview")
        
        # Show databases to create
        if to_create:
            print(f"╭─ 🚀 Database Instances to CREATE: {len(to_create)}")
            for instance in to_create:
                print(f"├─ 🆕 {instance}")
                print(f"│  ├─ 🔧 Engine: {self._get_database_engine()} {self._get_engine_version()}")
                print(f"│  ├─ 💪 Tier: {self.db_tier}")
                print(f"│  ├─ 📍 Region: {self.db_region}")
                print(f"│  ├─ 💿 Storage: {self.disk_size_gb}GB ({self.disk_type})")
                print(f"│  ├─ 🏗️  Availability: {self.availability_type}")
                print(f"│  ├─ 💾 Backups: {'✅ Enabled' if self.backup_enabled else '❌ Disabled'}")
                if self.backup_enabled:
                    print(f"│  │  └─ ⏰ Start Time: {self.backup_start_time}")
                print(f"│  ├─ 🔒 SSL: {self.ssl_mode}")
                print(f"│  ├─ 🛡️  Deletion Protection: {'✅ Enabled' if self.deletion_protection else '❌ Disabled'}")
                print(f"│  ├─ 📊 Initial Database: {self.database_name}")
                print(f"│  ├─ 👤 Username: {self.username}")
                print(f"│  ├─ 🔑 Password: {'Custom' if self.password else 'Auto-generated'}")
                if self.authorized_networks:
                    print(f"│  ├─ 🌐 Authorized Networks: {len(self.authorized_networks)}")
                if self.database_flags:
                    print(f"│  ├─ ⚙️  Database Flags: {len(self.database_flags)} optimizations")
                if self.insights_enabled:
                    print(f"│  ├─ 📈 Query Insights: ✅ Enabled")
                print(f"│  └─ ⏱️  Deployment Time: 5-15 minutes")
            print(f"╰─")
        
        # Show databases to keep
        if to_keep:
            print(f"╭─ 🔄 Database Instances to KEEP: {len(to_keep)}")
            for instance in to_keep:
                db_info = existing_databases.get(instance, {})
                state_icon = "🟢" if db_info.get('state') == 'RUNNABLE' else "🟡" if db_info.get('state') == 'PENDING_CREATE' else "🔴"
                print(f"├─ {state_icon} {instance}")
                print(f"│  ├─ 🔧 Engine: {db_info.get('engine', 'Unknown')} {db_info.get('version', '')}")
                print(f"│  ├─ 💪 Tier: {db_info.get('tier', 'Unknown')}")
                print(f"│  ├─ 📍 Region: {db_info.get('region', 'Unknown')}")
                print(f"│  ├─ 📊 Status: {db_info.get('state', 'Unknown')}")
                if db_info.get('public_ip'):
                    print(f"│  ├─ 🌐 Public IP: {db_info['public_ip']}")
                if db_info.get('private_ip'):
                    print(f"│  ├─ 🔒 Private IP: {db_info['private_ip']}")
                print(f"│  └─ 📅 Created: {db_info.get('creation_time', 'Unknown')}")
            print(f"╰─")
        
        # Show databases to remove
        if to_remove:
            print(f"╭─ 🗑️  Database Instances to REMOVE: {len(to_remove)}")
            for instance in to_remove:
                db_info = existing_databases.get(instance, {})
                print(f"├─ ❌ {instance}")
                print(f"│  ├─ 🔧 Engine: {db_info.get('engine', 'Unknown')} {db_info.get('version', '')}")
                print(f"│  ├─ 💪 Tier: {db_info.get('tier', 'Unknown')}")
                print(f"│  ├─ 📍 Region: {db_info.get('region', 'Unknown')}")
                print(f"│  ├─ 💿 Storage: {db_info.get('disk_size_gb', 0)}GB")
                print(f"│  └─ ⚠️  All databases and data will be permanently deleted")
            print(f"╰─")
        
        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        base_cost, storage_cost, backup_cost, ha_cost = self._calculate_cost_breakdown()
        print(f"   ├─ 💾 Database Instance ({self.db_tier}): ${base_cost:.2f}/month")
        print(f"   ├─ 💿 Storage ({self.disk_size_gb}GB {self.disk_type}): ${storage_cost:.2f}/month")
        if self.backup_enabled:
            print(f"   ├─ 💾 Automated Backups: ${backup_cost:.2f}/month")
        if self.availability_type == 'REGIONAL':
            print(f"   ├─ 🏗️  High Availability: ${ha_cost:.2f}/month")
        print(f"   ├─ 📊 Network Egress: $0.12/GB (first 1GB free)")
        total_cost = base_cost + storage_cost + backup_cost + ha_cost
        print(f"   └─ 📊 Total Estimated: ${total_cost:.2f}/month")
    
    def create(self) -> Dict[str, Any]:
        """Create/update Cloud SQL database instance"""
        self._ensure_authenticated()
        
        if not self.instance_name:
            raise ValueError("Instance name is required")
        
        # Discover existing databases to determine what changes are needed
        existing_databases = self._discover_existing_databases()
        instance_exists = self.instance_name in existing_databases
        to_create = [] if instance_exists else [self.instance_name]
        to_remove = [name for name in existing_databases.keys() if name != self.instance_name]
        
        print(f"\n💾 Creating Cloud SQL Database: {self.instance_name}")
        print(f"   🔧 Engine: {self._get_database_engine()} {self._get_engine_version()}")
        print(f"   📍 Region: {self.db_region}")
        print(f"   💪 Tier: {self.db_tier}")
        print(f"   💿 Storage: {self.disk_size_gb}GB ({self.disk_type})")
        
        try:
            # Remove databases that are no longer needed
            for db_name in to_remove:
                print(f"🗑️  Removing database instance: {db_name}")
                try:
                    # Mock removal for now - in real implementation this would use GCP SDK
                    print(f"✅ Database instance removed successfully: {db_name}")
                except Exception as e:
                    print(f"⚠️  Warning: Failed to remove database {db_name}: {str(e)}")
            
            # Create database configuration
            db_config = {
                'instance_name': self.instance_name,
                'database_version': self.database_version,
                'tier': self.db_tier,
                'region': self.db_region,
                'zone': self.db_zone,
                'disk_size_gb': self.disk_size_gb,
                'disk_type': self.disk_type,
                'disk_autoresize': self.disk_autoresize,
                'availability_type': self.availability_type,
                'backup_enabled': self.backup_enabled,
                'backup_start_time': self.backup_start_time,
                'deletion_protection': self.deletion_protection,
                'authorized_networks': self.authorized_networks,
                'ssl_mode': self.ssl_mode,
                'public_ip': self.public_ip,
                'database_flags': self.database_flags,
                'labels': self.db_labels,
                'insights_enabled': self.insights_enabled,
                'maintenance_window_day': self.maintenance_window_day,
                'maintenance_window_hour': self.maintenance_window_hour,
                'database_name': self.database_name,
                'username': self.username,
                'password': self.password
            }
            
            # Create or update the database instance
            if instance_exists:
                print(f"🔄 Updating existing database instance")
            else:
                print(f"🆕 Creating new database instance")
            
            # Mock creation for now - in real implementation this would use GCP SDK
            instance_id = f"db-{str(uuid.uuid4())[:8]}"
            public_ip = "35.123.45.67" if self.public_ip else None
            private_ip = "10.0.0.100"
            
            result = {
                'instance_name': self.instance_name,
                'instance_id': instance_id,
                'database_version': self.database_version,
                'engine': self._get_database_engine(),
                'version': self._get_engine_version(),
                'tier': self.db_tier,
                'region': self.db_region,
                'zone': self.db_zone,
                'disk_size_gb': self.disk_size_gb,
                'disk_type': self.disk_type,
                'availability_type': self.availability_type,
                'backup_enabled': self.backup_enabled,
                'backup_start_time': self.backup_start_time,
                'deletion_protection': self.deletion_protection,
                'ssl_mode': self.ssl_mode,
                'public_ip': public_ip,
                'private_ip': private_ip,
                'connection_name': self.connection_name,
                'database_name': self.database_name,
                'username': self.username,
                'password': self.password or 'auto-generated-password',
                'database_flags': self.database_flags,
                'labels': self.db_labels,
                'insights_enabled': self.insights_enabled,
                'status': 'RUNNABLE',
                'created': True,
                'updated': instance_exists,
                'changes': {
                    'created': to_create,
                    'removed': to_remove,
                    'updated': [self.instance_name] if instance_exists else []
                }
            }
            
            # Update instance attributes
            self.instance_exists = True
            self.instance_created = True
            self.instance_ip = public_ip or private_ip
            self.connection_info = {
                'host': self.instance_ip,
                'port': 5432 if 'POSTGRES' in self.database_version else 3306,
                'database': self.database_name,
                'username': self.username,
                'password': result['password'],
                'connection_name': self.connection_name
            }
            
            self._display_creation_success(result)
            return result
            
        except Exception as e:
            print(f"❌ Failed to create Cloud SQL database: {str(e)}")
            raise
    
    def _display_creation_success(self, result: Dict[str, Any]):
        """Display creation success information"""
        print(f"✅ Cloud SQL database {'updated' if result['updated'] else 'created'} successfully")
        print(f"   💾 Instance Name: {result['instance_name']}")
        print(f"   🔧 Engine: {result['engine']} {result['version']}")
        print(f"   💪 Tier: {result['tier']}")
        print(f"   📍 Region: {result['region']}")
        print(f"   💿 Storage: {result['disk_size_gb']}GB ({result['disk_type']})")
        print(f"   📊 Status: {result['status']}")
        
        # Connection information
        print(f"\n📡 Connection Information:")
        print(f"   🔗 Connection Name: {result['connection_name']}")
        if result.get('public_ip'):
            print(f"   🌐 Public IP: {result['public_ip']}")
        if result.get('private_ip'):
            print(f"   🔒 Private IP: {result['private_ip']}")
        print(f"   📊 Database: {result['database_name']}")
        print(f"   👤 Username: {result['username']}")
        print(f"   🔑 Password: [HIDDEN - use get_connection_info() to retrieve]")
        
        # Connection examples
        print(f"\n🔌 Connection Examples:")
        print(f"   Cloud SQL Proxy: gcloud sql connect {result['instance_name']}")
        if 'POSTGRES' in result['database_version']:
            print(f"   Direct (if allowed): psql -h {result.get('public_ip', result.get('private_ip'))} -U {result['username']} -d {result['database_name']}")
        else:
            print(f"   Direct (if allowed): mysql -h {result.get('public_ip', result.get('private_ip'))} -u {result['username']} -p {result['database_name']}")
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy the Cloud SQL database instance"""
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying Cloud SQL Database: {self.instance_name}")
        
        if self.deletion_protection:
            print(f"⚠️  Warning: Deletion protection is enabled")
            print(f"   This will be automatically disabled to proceed with destruction")
        
        try:
            # Mock destruction for now - in real implementation this would use GCP SDK
            result = {
                'instance_name': self.instance_name,
                'engine': self._get_database_engine(),
                'region': self.db_region,
                'destroyed': True,
                'note': 'Database instance and all data deleted permanently'
            }
            
            # Reset instance attributes
            self.instance_exists = False
            self.instance_created = False
            self.instance_ip = None
            self.connection_info = None
            
            print(f"✅ Cloud SQL database destroyed successfully")
            print(f"   💾 Instance Name: {result['instance_name']}")
            print(f"   🔧 Engine: {result['engine']}")
            print(f"   📍 Region: {result['region']}")
            print(f"   ⚠️  Note: All databases and data have been permanently deleted")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to destroy Cloud SQL database: {str(e)}")
            raise
    
    def _discover_existing_databases(self) -> Dict[str, Any]:
        """Discover existing Cloud SQL database instances"""
        try:
            existing_databases = {}
            
            # Mock discovery for now - in real implementation this would use GCP SDK
            # This would list all database instances in the project and filter for related ones
            
            # For testing, we'll simulate finding related databases
            if hasattr(self, 'cloudsql_manager') and self.cloudsql_manager:
                # In real implementation, this would call GCP APIs
                pass
                
            return existing_databases
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to discover existing databases: {str(e)}")
            return {}
    
    def _estimate_monthly_cost(self) -> str:
        """Estimate monthly cost based on configuration"""
        base_cost, storage_cost, backup_cost, ha_cost = self._calculate_cost_breakdown()
        total_cost = base_cost + storage_cost + backup_cost + ha_cost
        return f"~${total_cost:.2f}/month"
    
    def _calculate_cost_breakdown(self) -> tuple:
        """Calculate cost breakdown components"""
        # Base instance cost estimation (simplified)
        if 'micro' in self.db_tier:
            base_cost = 7.67
        elif 'small' in self.db_tier or 'standard-1' in self.db_tier:
            base_cost = 25.76
        elif 'standard-2' in self.db_tier:
            base_cost = 51.52
        elif 'standard-4' in self.db_tier:
            base_cost = 103.04
        elif 'standard-8' in self.db_tier:
            base_cost = 206.08
        else:
            base_cost = 25.76  # Default estimate
        
        # Storage cost
        storage_cost_per_gb = 0.17 if self.disk_type == "PD_SSD" else 0.04  # Per GB per month
        storage_cost = self.disk_size_gb * storage_cost_per_gb
        
        # Backup cost
        backup_cost = (self.disk_size_gb * 0.08) if self.backup_enabled else 0
        
        # High availability cost (doubles instance cost)
        ha_cost = base_cost if self.availability_type == 'REGIONAL' else 0
        
        return base_cost, storage_cost, backup_cost, ha_cost
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information"""
        if not self.connection_info:
            # In real implementation, this would fetch from GCP
            default_port = 5432 if 'POSTGRES' in self.database_version else 3306
            self.connection_info = {
                'host': self.instance_ip or 'pending',
                'port': default_port,
                'database': self.database_name,
                'username': self.username,
                'password': self.password or 'auto-generated',
                'connection_name': self.connection_name
            }
        return self.connection_info
    
    def connection_string(self, format: str = "standard") -> str:
        """Generate connection string for applications"""
        conn_info = self.get_connection_info()
        
        if format == "postgres" or format == "postgresql":
            return f"postgresql://{conn_info['username']}:{conn_info['password']}@{conn_info['host']}:{conn_info['port']}/{conn_info['database']}"
        elif format == "mysql":
            return f"mysql://{conn_info['username']}:{conn_info['password']}@{conn_info['host']}:{conn_info['port']}/{conn_info['database']}"
        elif format == "django":
            engine = 'django.db.backends.postgresql' if 'POSTGRES' in self.database_version else 'django.db.backends.mysql'
            return f"""DATABASES = {{
    'default': {{
        'ENGINE': '{engine}',
        'NAME': '{conn_info['database']}',
        'USER': '{conn_info['username']}',
        'PASSWORD': '{conn_info['password']}',
        'HOST': '{conn_info['host']}',
        'PORT': '{conn_info['port']}',
    }}
}}"""
        elif format == "rails":
            adapter = 'postgresql' if 'POSTGRES' in self.database_version else 'mysql2'
            return f"""production:
  adapter: {adapter}
  encoding: unicode
  database: {conn_info['database']}
  username: {conn_info['username']}
  password: {conn_info['password']}
  host: {conn_info['host']}
  port: {conn_info['port']}"""
        else:
            return f"Host: {conn_info['host']}, Port: {conn_info['port']}, Database: {conn_info['database']}, User: {conn_info['username']}"
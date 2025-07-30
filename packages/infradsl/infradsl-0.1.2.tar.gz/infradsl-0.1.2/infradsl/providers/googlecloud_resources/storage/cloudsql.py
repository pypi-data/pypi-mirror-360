import os
from typing import Dict, Any, Optional, List, Union
from ..base_resource import BaseGcpResource
from ..auth_service import GcpAuthenticationService
from ...googlecloud_managers.database.cloudsql_manager import CloudSQLManager, DatabaseConfig
from ...googlecloud_managers.status_reporter import GcpStatusReporter


class CloudSQL(BaseGcpResource):
    """Rails-like Cloud SQL database orchestrator - databases made simple"""

    def __init__(self, instance_name: str):
        self.config = DatabaseConfig(instance_name=instance_name)
        self.status_reporter = GcpStatusReporter()
        self._connection_info = None
        super().__init__(instance_name)

    def _initialize_managers(self):
        """Initialize CloudSQL specific managers"""
        self.cloudsql_manager = None

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.cloudsql_manager = CloudSQLManager(self.gcp_client)

    def _discover_existing_databases(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Cloud SQL database instances"""
        existing_databases = {}
        
        try:
            from googleapiclient import discovery
            from googleapiclient.errors import HttpError
            
            service = discovery.build('sqladmin', 'v1', credentials=self.gcp_client.credentials)
            
            # List all SQL instances in the project
            request = service.instances().list(project=self.gcp_client.project_id)
            response = request.execute()
            
            for instance in response.get('items', []):
                instance_name = instance['name']
                
                try:
                    # Get detailed instance information
                    detailed_request = service.instances().get(
                        project=self.gcp_client.project_id, 
                        instance=instance_name
                    )
                    detailed_instance = detailed_request.execute()
                    
                    # Extract instance configuration
                    settings = detailed_instance.get('settings', {})
                    tier = settings.get('tier', 'unknown')
                    
                    # Determine database engine
                    db_version = detailed_instance.get('databaseVersion', 'UNKNOWN')
                    if 'POSTGRES' in db_version:
                        engine = 'PostgreSQL'
                        version = db_version.replace('POSTGRES_', '')
                    elif 'MYSQL' in db_version:
                        engine = 'MySQL'
                        version = db_version.replace('MYSQL_', '').replace('_', '.')
                    else:
                        engine = 'Unknown'
                        version = db_version
                    
                    # Get storage and availability info
                    disk_size = settings.get('dataDiskSizeGb', 0)
                    disk_type = settings.get('dataDiskType', 'PD_SSD')
                    availability_type = settings.get('availabilityType', 'ZONAL')
                    
                    # Get backup configuration
                    backup_config = settings.get('backupConfiguration', {})
                    backup_enabled = backup_config.get('enabled', False)
                    
                    # Get IP addresses
                    ip_addresses = detailed_instance.get('ipAddresses', [])
                    public_ip = None
                    private_ip = None
                    for ip_info in ip_addresses:
                        if ip_info.get('type') == 'PRIMARY':
                            public_ip = ip_info.get('ipAddress')
                        elif ip_info.get('type') == 'PRIVATE':
                            private_ip = ip_info.get('ipAddress')
                    
                    # Get connection name for proxy
                    connection_name = detailed_instance.get('connectionName', '')
                    
                    # Get pricing tier info
                    pricing_plan = settings.get('pricingPlan', 'PER_USE')
                    
                    # Get database flags
                    db_flags = {}
                    for flag in settings.get('databaseFlags', []):
                        db_flags[flag.get('name')] = flag.get('value')
                    
                    existing_databases[instance_name] = {
                        'instance_name': instance_name,
                        'engine': engine,
                        'version': version,
                        'database_version': db_version,
                        'tier': tier,
                        'region': detailed_instance.get('region', 'unknown'),
                        'zone': detailed_instance.get('gceZone', 'unknown'),
                        'state': detailed_instance.get('state', 'UNKNOWN'),
                        'disk_size_gb': disk_size,
                        'disk_type': disk_type,
                        'availability_type': availability_type,
                        'backup_enabled': backup_enabled,
                        'backup_start_time': backup_config.get('startTime', 'unknown'),
                        'public_ip': public_ip,
                        'private_ip': private_ip,
                        'connection_name': connection_name,
                        'pricing_plan': pricing_plan,
                        'database_flags': db_flags,
                        'flag_count': len(db_flags),
                        'ssl_mode': settings.get('ipConfiguration', {}).get('requireSsl', False),
                        'deletion_protection': detailed_instance.get('settings', {}).get('deletionProtectionEnabled', False),
                        'creation_time': detailed_instance.get('createTime'),
                        'insights_enabled': settings.get('insightsConfig', {}).get('queryInsightsEnabled', False)
                    }
                    
                except HttpError as e:
                    if e.resp.status == 404:
                        continue
                    else:
                        print(f"⚠️  Failed to get details for database {instance_name}: {str(e)}")
                        existing_databases[instance_name] = {
                            'instance_name': instance_name,
                            'error': str(e)
                        }
                        
        except Exception as e:
            print(f"⚠️  Failed to discover existing databases: {str(e)}")
        
        return existing_databases

    def engine(self, database_version: str) -> 'CloudSQL':
        """Set database engine version (e.g., 'POSTGRES_15', 'MYSQL_8_0')"""
        self.config.database_version = database_version
        return self

    def postgres(self, version: str = "15") -> 'CloudSQL':
        """Configure PostgreSQL database (Rails convention)"""
        self.config.database_version = f"POSTGRES_{version}"
        return self

    def mysql(self, version: str = "8.0") -> 'CloudSQL':
        """Configure MySQL database (Rails convention)"""
        version_clean = version.replace(".", "_")
        self.config.database_version = f"MYSQL_{version_clean}"
        return self

    def tier(self, tier: str) -> 'CloudSQL':
        """Set machine tier (e.g., 'db-f1-micro', 'db-n1-standard-1')"""
        self.config.tier = tier
        return self

    def micro(self) -> 'CloudSQL':
        """Use micro tier for development (Rails convention)"""
        self.config.tier = "db-f1-micro"
        return self

    def small(self) -> 'CloudSQL':
        """Use small tier for small workloads (Rails convention)"""
        self.config.tier = "db-n1-standard-1"
        return self

    def standard(self) -> 'CloudSQL':
        """Use standard tier for production (Rails convention)"""
        self.config.tier = "db-n1-standard-2"
        return self

    def large(self) -> 'CloudSQL':
        """Use large tier for high-traffic applications (Rails convention)"""
        self.config.tier = "db-n1-standard-4"
        return self

    def region(self, region: str) -> 'CloudSQL':
        """Set database region (e.g., 'us-central1', 'europe-north1')"""
        self.config.region = region
        return self

    def zone(self, zone: str) -> 'CloudSQL':
        """Set specific zone for zonal instances"""
        self.config.zone = zone
        return self

    def disk_size(self, size_gb: int) -> 'CloudSQL':
        """Set disk size in GB"""
        if size_gb < 10:
            raise ValueError("Minimum disk size is 10 GB")
        self.config.disk_size_gb = size_gb
        return self

    def ssd(self) -> 'CloudSQL':
        """Use SSD storage for better performance (Rails convention)"""
        self.config.disk_type = "PD_SSD"
        return self

    def hdd(self) -> 'CloudSQL':
        """Use HDD storage for cost optimization (Rails convention)"""
        self.config.disk_type = "PD_HDD"
        return self

    def autoresize(self, enabled: bool = True) -> 'CloudSQL':
        """Enable/disable automatic disk resize"""
        self.config.disk_autoresize = enabled
        return self

    def high_availability(self) -> 'CloudSQL':
        """Enable regional high availability (Rails convention)"""
        self.config.availability_type = "REGIONAL"
        return self

    def zonal(self) -> 'CloudSQL':
        """Use zonal configuration for cost savings (Rails convention)"""
        self.config.availability_type = "ZONAL"
        return self

    def backups(self, enabled: bool = True, start_time: str = "03:00") -> 'CloudSQL':
        """Configure automatic backups"""
        self.config.backup_enabled = enabled
        self.config.backup_start_time = start_time
        return self

    def maintenance(self, day: int = 7, hour: int = 4) -> 'CloudSQL':
        """Set maintenance window (day: 1=Monday, 7=Sunday; hour: 0-23)"""
        self.config.maintenance_window_day = day
        self.config.maintenance_window_hour = hour
        return self

    def deletion_protection(self, enabled: bool = True) -> 'CloudSQL':
        """Enable/disable deletion protection"""
        self.config.deletion_protection = enabled
        return self

    def insights(self, enabled: bool = True) -> 'CloudSQL':
        """Enable/disable query insights and monitoring"""
        self.config.insights_enabled = enabled
        return self

    def ssl_required(self, required: bool = True) -> 'CloudSQL':
        """Require SSL connections for security"""
        self.config.ssl_mode = "REQUIRE" if required else "ALLOW"
        return self

    def allow_public_access(self, enabled: bool = False) -> 'CloudSQL':
        """
        Allow public IP access (Rails security: private by default).

        Warning: This exposes your database to the internet.
        Consider using private IP or authorized networks instead.
        """
        if enabled:
            print("⚠️  WARNING: Enabling public IP access exposes database to internet")
            print("   💡 Consider using private IP or authorized networks for security")
        return self

    def authorized_network(self, cidr: str, name: str = None) -> 'CloudSQL':
        """Add authorized network for database access"""
        network = {"value": cidr}
        if name:
            network["name"] = name
        self.config.authorized_networks.append(network)
        return self

    def database_name(self, name: str) -> 'CloudSQL':
        """Set the initial database name (Rails convention: app_production)"""
        self.config.database_name = name
        return self

    def username(self, username: str) -> 'CloudSQL':
        """Set the database username (Rails convention: app_user)"""
        self.config.username = username
        return self

    def password(self, password: str) -> 'CloudSQL':
        """Set the database password (auto-generated if not provided)"""
        self.config.password = password
        return self

    def labels(self, labels: Dict[str, str]) -> 'CloudSQL':
        """Add labels for organization and billing"""
        self.config.labels = labels
        return self

    def flags(self, flags: Dict[str, str]) -> 'CloudSQL':
        """Set custom database flags"""
        self.config.database_flags.update(flags)
        return self

    def optimize_for(self, use_case: str) -> 'CloudSQL':
        """
        Apply optimizations for specific use cases (Rails convention).

        Use cases: 'web', 'api', 'analytics', 'general'
        """
        db_type = "postgres" if "POSTGRES" in self.config.database_version else "mysql"

        if not self.cloudsql_manager:
            # Store for later application
            self._optimize_use_case = use_case
        else:
            flags = self.cloudsql_manager.get_smart_database_flags(db_type, use_case)
            self.config.database_flags.update(flags)
            print(f"🎯 Applied {use_case} optimizations ({len(flags)} flags)")

        return self

    def development_db(self) -> 'CloudSQL':
        """Configure for development environment (Rails convention)"""
        return (self.micro()
                .zonal()
                .ssd()
                .deletion_protection(False)
                .database_name("app_development")
                .optimize_for("web"))

    def production_db(self) -> 'CloudSQL':
        """Configure for production environment (Rails convention)"""
        return (self.standard()
                .high_availability()
                .ssd()
                .autoresize(True)
                .backups(True)
                .deletion_protection(True)
                .database_name("app_production")
                .optimize_for("web"))

    def analytics_db(self) -> 'CloudSQL':
        """Configure for analytics workloads (Rails convention)"""
        return (self.large()
                .ssd()
                .disk_size(100)
                .optimize_for("analytics")
                .database_name("analytics"))

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()

        # Discover existing databases
        existing_databases = self._discover_existing_databases()
        
        # Categorize databases
        dbs_to_create = []
        dbs_to_keep = []
        dbs_to_remove = []
        
        # Check if our desired database exists
        desired_db_name = self.config.instance_name
        db_exists = desired_db_name in existing_databases
        
        if not db_exists:
            dbs_to_create.append({
                'instance_name': desired_db_name,
                'engine': "PostgreSQL" if "POSTGRES" in self.config.database_version else "MySQL",
                'version': self.config.database_version,
                'tier': self.config.tier,
                'region': self.config.region,
                'disk_size_gb': self.config.disk_size_gb,
                'disk_type': self.config.disk_type,
                'availability_type': self.config.availability_type,
                'backup_enabled': self.config.backup_enabled,
                'deletion_protection': self.config.deletion_protection,
                'database_name': self.config.database_name,
                'username': self.config.username,
                'authorized_networks': len(self.config.authorized_networks),
                'database_flags': len(self.config.database_flags),
                'ssl_required': self.config.ssl_mode == "REQUIRE"
            })
        else:
            dbs_to_keep.append(existing_databases[desired_db_name])

        print(f"\n💾 Google Cloud SQL Database Preview")
        
        # Show databases to create
        if dbs_to_create:
            print(f"╭─ 💾 Database Instances to CREATE: {len(dbs_to_create)}")
            for db in dbs_to_create:
                print(f"├─ 🆕 {db['instance_name']}")
                print(f"│  ├─ 🔧 Engine: {db['engine']} ({db['version']})")
                print(f"│  ├─ 💪 Tier: {db['tier']}")
                print(f"│  ├─ 📍 Region: {db['region']}")
                print(f"│  ├─ 💿 Storage: {db['disk_size_gb']}GB ({db['disk_type']})")
                print(f"│  ├─ 🏗️  Availability: {db['availability_type']}")
                print(f"│  ├─ 💾 Backups: {'✅ Enabled' if db['backup_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🔒 SSL Required: {'✅ Yes' if db['ssl_required'] else '❌ No'}")
                print(f"│  ├─ 🛡️  Deletion Protection: {'✅ Enabled' if db['deletion_protection'] else '❌ Disabled'}")
                print(f"│  ├─ 📊 Initial Database: {db['database_name']}")
                print(f"│  ├─ 👤 Username: {db['username']}")
                
                if db['authorized_networks'] > 0:
                    print(f"│  ├─ 🌐 Authorized Networks: {db['authorized_networks']}")
                
                if db['database_flags'] > 0:
                    print(f"│  ├─ ⚙️  Database Flags: {db['database_flags']} optimizations")
                
                # Show connectivity options
                print(f"│  ├─ 🔗 Connectivity:")
                if db['availability_type'] == 'REGIONAL':
                    print(f"│  │  ├─ 🌐 Public IP: Available")
                    print(f"│  │  ├─ 🔒 Private IP: Available") 
                    print(f"│  │  └─ 🔌 Cloud SQL Proxy: Recommended")
                else:
                    print(f"│  │  ├─ 🌐 Public IP: Available")
                    print(f"│  │  └─ 🔌 Cloud SQL Proxy: Available")
                
                print(f"│  └─ ⚡ Performance: Optimized for {self.config.database_name.split('_')[-1] if '_' in self.config.database_name else 'general'} workload")
            print(f"╰─")

        # Show existing databases being kept
        if dbs_to_keep:
            print(f"\n╭─ 💾 Existing Database Instances to KEEP: {len(dbs_to_keep)}")
            for db in dbs_to_keep:
                state_icon = "🟢" if db['state'] == 'RUNNABLE' else "🟡" if db['state'] == 'PENDING_CREATE' else "🔴"
                print(f"├─ {state_icon} {db['instance_name']}")
                print(f"│  ├─ 🔧 Engine: {db['engine']} {db['version']}")
                print(f"│  ├─ 💪 Tier: {db['tier']}")
                print(f"│  ├─ 📍 Location: {db['region']} ({db['zone']})")
                print(f"│  ├─ 💿 Storage: {db['disk_size_gb']}GB ({db['disk_type']})")
                print(f"│  ├─ 🏗️  Availability: {db['availability_type']}")
                print(f"│  ├─ 💾 Backups: {'✅ Enabled' if db['backup_enabled'] else '❌ Disabled'}")
                
                if db['backup_enabled'] and db['backup_start_time'] != 'unknown':
                    print(f"│  │  └─ ⏰ Backup Time: {db['backup_start_time']}")
                
                print(f"│  ├─ 🔒 SSL Required: {'✅ Yes' if db['ssl_mode'] else '❌ No'}")
                print(f"│  ├─ 🛡️  Deletion Protection: {'✅ Enabled' if db['deletion_protection'] else '❌ Disabled'}")
                
                if db['public_ip']:
                    print(f"│  ├─ 🌐 Public IP: {db['public_ip']}")
                if db['private_ip']:
                    print(f"│  ├─ 🔒 Private IP: {db['private_ip']}")
                    
                if db['connection_name']:
                    print(f"│  ├─ 🔗 Connection Name: {db['connection_name']}")
                
                if db['flag_count'] > 0:
                    print(f"│  ├─ ⚙️  Database Flags: {db['flag_count']} custom flags")
                
                print(f"│  ├─ 📊 Query Insights: {'✅ Enabled' if db['insights_enabled'] else '❌ Disabled'}")
                print(f"│  └─ 📅 Created: {db.get('creation_time', 'Unknown')}")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        
        # Default cost values
        base_cost = 25.76
        storage_cost = 0
        
        if dbs_to_create:
            db = dbs_to_create[0]
            
            # Basic tier costs (simplified estimation)
            if 'micro' in db['tier']:
                base_cost = 7.67
            elif 'small' in db['tier'] or 'standard-1' in db['tier']:
                base_cost = 25.76
            elif 'standard-2' in db['tier']:
                base_cost = 51.52
            elif 'standard-4' in db['tier']:
                base_cost = 103.04
            else:
                base_cost = 25.76  # default estimate
            
            storage_cost = db['disk_size_gb'] * 0.17  # $0.17/GB/month for SSD
            
            print(f"   ├─ 💾 Database Instance ({db['tier']}): ${base_cost:.2f}/month")
            print(f"   ├─ 💿 Storage ({db['disk_size_gb']}GB {db['disk_type']}): ${storage_cost:.2f}/month")
            
            if db['backup_enabled']:
                backup_cost = db['disk_size_gb'] * 0.08  # $0.08/GB/month for backups
                print(f"   ├─ 💾 Automated Backups: ${backup_cost:.2f}/month")
            else:
                backup_cost = 0
                
            if db['availability_type'] == 'REGIONAL':
                ha_cost = base_cost * 2  # Regional HA doubles the instance cost
                print(f"   ├─ 🏗️  High Availability: ${ha_cost:.2f}/month")
            else:
                ha_cost = 0
            
            total_cost = base_cost + storage_cost + backup_cost + ha_cost
            print(f"   ├─ 📊 Network Egress: $0.12/GB (first 1GB free)")
            print(f"   └─ 📊 Total Estimated: ${total_cost:.2f}/month")
        else:
            print(f"   ├─ 💾 Database instances: From $7.67/month")
            print(f"   ├─ 💿 SSD Storage: $0.17/GB/month")
            print(f"   ├─ 💾 Automated Backups: $0.08/GB/month")
            print(f"   └─ 🏗️  High Availability: 2x instance cost")

        return {
            'resource_type': 'gcp_cloudsql',
            'name': desired_db_name,
            'dbs_to_create': dbs_to_create,
            'dbs_to_keep': dbs_to_keep,
            'dbs_to_remove': dbs_to_remove,
            'existing_databases': existing_databases,
            'instance_name': desired_db_name,
            'engine': "PostgreSQL" if "POSTGRES" in self.config.database_version else "MySQL",
            'version': self.config.database_version,
            'tier': self.config.tier,
            'estimated_cost': f"${base_cost + storage_cost:.2f}/month" if dbs_to_create else "From $7.67/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create database instance with smart state management"""
        self._ensure_authenticated()

        # Discover existing databases first
        existing_databases = self._discover_existing_databases()
        
        # Determine what changes need to be made
        desired_db_name = self.config.instance_name
        
        # Check for databases to remove (not in current configuration)
        dbs_to_remove = []
        for db_name, db_info in existing_databases.items():
            # In a real implementation, this would have more sophisticated logic
            # to determine which databases should be removed based on configuration
            # For now, we'll focus on creating the desired database
            pass
        
        # Remove databases no longer in configuration
        if dbs_to_remove:
            print(f"\n🗑️  Removing databases no longer in configuration:")
            for db_info in dbs_to_remove:
                print(f"╭─ 🔄 Removing database: {db_info['instance_name']}")
                print(f"├─ 🔧 Engine: {db_info['engine']} {db_info['version']}")
                print(f"├─ 💪 Tier: {db_info['tier']}")
                print(f"├─ 📍 Region: {db_info['region']}")
                print(f"├─ 💿 Storage: {db_info['disk_size_gb']}GB")
                if db_info['backup_enabled']:
                    print(f"├─ 💾 Note: Automatic backups will be retained for recovery")
                print(f"└─ ⚠️  Database instance and all data will be permanently deleted")
                
                # In real implementation:
                # self.cloudsql_manager.delete_database_instance(db_info['instance_name'])

        # Check if our desired database already exists
        db_exists = desired_db_name in existing_databases
        if db_exists:
            existing_db = existing_databases[desired_db_name]
            print(f"\n🔄 Database '{desired_db_name}' already exists")
            print(f"   🔧 Engine: {existing_db['engine']} {existing_db['version']}")
            print(f"   💪 Tier: {existing_db['tier']}")
            print(f"   📊 Status: {existing_db['state']}")
            print(f"   📍 Location: {existing_db['region']}")
            
            if existing_db['public_ip']:
                print(f"   🌐 Public IP: {existing_db['public_ip']}")
            if existing_db['private_ip']:
                print(f"   🔒 Private IP: {existing_db['private_ip']}")
            
            # In a real implementation, we would:
            # 1. Compare existing configuration with desired configuration
            # 2. Update database flags, users, and databases if needed
            # 3. Scale the instance if tier changed
            
            result = {
                'instance_name': existing_db['instance_name'],
                'engine': existing_db['engine'],
                'version': existing_db['version'],
                'tier': existing_db['tier'],
                'state': existing_db['state'],
                'region': existing_db['region'],
                'public_ip': existing_db.get('public_ip'),
                'private_ip': existing_db.get('private_ip'),
                'connection_name': existing_db.get('connection_name'),
                'existing': True
            }
            if len(dbs_to_remove) > 0:
                result['changes'] = True
            return result

        print(f"\n💾 Creating Google Cloud SQL Database: {desired_db_name}")
        print(f"   🔧 Engine: {self.config.database_version}")
        print(f"   📍 Region: {self.config.region}")
        print(f"   💾 Tier: {self.config.tier}")
        print(f"   💿 Storage: {self.config.disk_size_gb}GB ({self.config.disk_type})")
        print(f"   🏗️  Availability: {self.config.availability_type}")
        print(f"   💾 Backups: {'✅ Enabled' if self.config.backup_enabled else '❌ Disabled'}")

        # Apply deferred optimizations
        if hasattr(self, '_optimize_use_case'):
            db_type = "postgres" if "POSTGRES" in self.config.database_version else "mysql"
            flags = self.cloudsql_manager.get_smart_database_flags(db_type, self._optimize_use_case)
            self.config.database_flags.update(flags)
            print(f"   ⚙️  Applied {self._optimize_use_case} optimizations")

        try:
            # Create the database instance
            db_result = self.cloudsql_manager.create_database_instance(self.config)
            
            print(f"\n✅ Database instance created successfully!")
            print(f"   💾 Name: {db_result['instance_name']}")
            print(f"   🔧 Engine: {self.config.database_version}")
            print(f"   💪 Tier: {self.config.tier}")
            print(f"   📍 Region: {self.config.region}")

            # Get connection information
            self._connection_info = self.cloudsql_manager.get_connection_info(
                self.config.instance_name, self.config
            )

            # Display connection info
            print(f"\n📡 Connection Information:")
            print(f"   🔗 Connection Name: {self._connection_info['connection_name']}")
            print(f"   🌐 Host: {self._connection_info.get('host', 'Pending IP assignment...')}")
            print(f"   🔌 Port: {self._connection_info['port']}")
            print(f"   📊 Database: {self._connection_info['database']}")
            print(f"   👤 Username: {self._connection_info['username']}")
            print(f"   🔑 Password: [HIDDEN - stored securely]")
            print(f"   🔌 Cloud SQL Proxy: gcloud sql connect {self.config.instance_name}")
            
            if len(dbs_to_remove) > 0:
                db_result['changes'] = True
                print(f"   🔄 Infrastructure changes applied")

            # Add connection info to result
            db_result.update(self._connection_info)

            return db_result

        except Exception as e:
            print(f"❌ Failed to create database: {str(e)}")
            raise

    def destroy(self) -> Dict[str, Any]:
        """Destroy the database instance"""
        self._ensure_authenticated()

        print(f"\n🗑️  DESTROY OPERATION")
        print("=" * 50)
        print(f"📋 Resources to be destroyed:")
        print(f"   🗄️ Database Instance: {self.config.instance_name}")
        print(f"   🔧 Engine: {self.config.database_version}")
        print(f"   📍 Region: {self.config.region}")
        print(f"   📊 Database: {self.config.database_name}")
        if self.config.deletion_protection:
            print(f"   🛡️ Deletion Protection: ENABLED")
        print("=" * 50)
        print("⚠️  WARNING: This will permanently delete the database and ALL its data!")
        print("💾 Make sure you have recent backups if you need to restore data later.")
        print("=" * 50)

        try:
            # Delete with force=True to handle deletion protection
            success = self.cloudsql_manager.delete_instance(
                self.config.instance_name,
                force=True  # Handle deletion protection automatically
            )

            result = {
                "instance_name": self.config.instance_name,
                "destroyed": success
            }

            if success:
                print(f"✅ Database instance destroyed: {self.config.instance_name}")
            else:
                print(f"⚠️  Failed to destroy database: {self.config.instance_name}")

            return result

        except Exception as e:
            print(f"❌ Failed to destroy database: {str(e)}")
            return {
                "instance_name": self.config.instance_name,
                "destroyed": False,
                "error": str(e)
            }

    # Utility methods for direct operations (Rails-like convenience)
    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information"""
        self._ensure_authenticated()
        return self.cloudsql_manager.get_connection_info(self.config.instance_name, self.config)

    def get_info(self) -> Dict[str, Any]:
        """Get database instance information"""
        self._ensure_authenticated()
        return self.cloudsql_manager.get_instance_info(self.config.instance_name)

    def create_database(self, database_name: str) -> Dict[str, Any]:
        """Create additional database in this instance"""
        self._ensure_authenticated()
        return self.cloudsql_manager.create_database(self.config.instance_name, database_name)

    def create_user(self, username: str, password: str) -> Dict[str, Any]:
        """Create additional user in this instance"""
        self._ensure_authenticated()
        return self.cloudsql_manager.create_user(self.config.instance_name, username, password)

    def connection_string(self, format: str = "postgres") -> str:
        """
        Generate connection string for applications.

        Args:
            format: Connection string format ('postgres', 'mysql', 'django', 'rails')
        """
        if not self._connection_info:
            self._connection_info = self.get_connection_info()

        info = self._connection_info

        if format == "postgres" or format == "postgresql":
            return f"postgresql://{info['username']}:{info['password']}@{info['host']}:{info['port']}/{info['database']}"
        elif format == "mysql":
            return f"mysql://{info['username']}:{info['password']}@{info['host']}:{info['port']}/{info['database']}"
        elif format == "django":
            return f"""DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '{info['database']}',
        'USER': '{info['username']}',
        'PASSWORD': '{info['password']}',
        'HOST': '{info['host']}',
        'PORT': '{info['port']}',
    }}
}}"""
        elif format == "rails":
            return f"""production:
  adapter: postgresql
  encoding: unicode
  database: {info['database']}
  username: {info['username']}
  password: {info['password']}
  host: {info['host']}
  port: {info['port']}"""
        else:
            return f"Host: {info['host']}, Port: {info['port']}, Database: {info['database']}, User: {info['username']}"

    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the database instance from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get instance info if it exists
            if self.cloudsql_manager:
                instance_info = self.cloudsql_manager.get_instance_info(self.config.instance_name)
                
                if instance_info.get("exists", False):
                    return {
                        "exists": True,
                        "instance_name": self.config.instance_name,
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
                        "instance_name": self.config.instance_name
                    }
            else:
                return {
                    "exists": False,
                    "instance_name": self.config.instance_name,
                    "error": "CloudSQL manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch database state: {str(e)}")
            return {
                "exists": False,
                "instance_name": self.config.instance_name,
                "error": str(e)
            }

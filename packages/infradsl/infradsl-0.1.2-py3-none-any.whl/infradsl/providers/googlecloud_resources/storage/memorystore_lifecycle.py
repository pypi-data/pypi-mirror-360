"""
GCP Memorystore Lifecycle Mixin

Lifecycle operations for Google Cloud Memorystore Redis.
Provides create, destroy, and preview operations with smart state management.
"""

import time
from typing import Dict, Any, List, Optional, Union


class MemorystoreLifecycleMixin:
    """
    Mixin for Memorystore lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update Memorystore instances
    - destroy(): Clean up Memorystore instances
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()

        # Discover existing instances
        existing_instances = self._discover_existing_instances()
        
        # Categorize instances
        instances_to_create = []
        instances_to_keep = []
        instances_to_remove = []
        
        # Check if our desired instance exists
        desired_instance_name = self.instance_id
        instance_exists = desired_instance_name in existing_instances
        
        if not instance_exists:
            instances_to_create.append({
                'instance_name': desired_instance_name,
                'instance_id': self.instance_id,
                'memory_size_gb': self.memory_size_gb,
                'tier': self.tier,
                'redis_version': self.redis_version,
                'region': self.region,
                'zone': self.zone,
                'auth_enabled': self.auth_enabled,
                'transit_encryption_mode': self.transit_encryption_mode,
                'persistence_config': self.persistence_config,
                'read_replicas_mode': self.read_replicas_mode,
                'replica_count': self.replica_count,
                'redis_configs': self.redis_configs,
                'redis_config_count': len(self.redis_configs),
                'labels': self.instance_labels,
                'label_count': len(self.instance_labels),
                'authorized_network': self.authorized_network,
                'reserved_ip_range': self.reserved_ip_range,
                'maintenance_policy': self.maintenance_policy,
                'instance_type': self._get_instance_type_from_config(),
                'estimated_cost': self._estimate_memorystore_cost(),
                'has_persistence': self.has_persistence(),
                'has_read_replicas': self.has_read_replicas(),
                'has_encryption': self.has_encryption()
            })
        else:
            instances_to_keep.append(existing_instances[desired_instance_name])

        print(f"\n⚡ Google Cloud Memorystore Redis Preview")
        
        # Show instances to create
        if instances_to_create:
            print(f"╭─ ⚡ Redis Instances to CREATE: {len(instances_to_create)}")
            for instance in instances_to_create:
                print(f"├─ 🆕 {instance['instance_name']}")
                print(f"│  ├─ 🆔 Instance ID: {instance['instance_id']}")
                print(f"│  ├─ 📊 Memory: {instance['memory_size_gb']}GB")
                print(f"│  ├─ 🏗️  Tier: {instance['tier']}")
                print(f"│  ├─ ⚡ Version: {instance['redis_version']}")
                print(f"│  ├─ 📍 Region: {instance['region']}")
                print(f"│  ├─ 🎯 Instance Type: {instance['instance_type'].replace('_', ' ').title()}")
                
                if instance['zone']:
                    print(f"│  ├─ 🌐 Zone: {instance['zone']}")
                
                # Show security configuration
                print(f"│  ├─ 🔒 Security:")
                print(f"│  │  ├─ 🔑 Authentication: {'✅ Enabled' if instance['auth_enabled'] else '❌ Disabled'}")
                print(f"│  │  └─ 🔐 Encryption: {instance['transit_encryption_mode']}")
                
                # Show persistence configuration
                persistence_mode = instance['persistence_config'].get('persistence_mode', 'DISABLED') if instance['persistence_config'] else 'DISABLED'
                print(f"│  ├─ 💾 Persistence: {persistence_mode}")
                
                if persistence_mode != 'DISABLED' and instance['persistence_config']:
                    period = instance['persistence_config'].get('rdb_snapshot_period', 'UNKNOWN')
                    backup_time = instance['persistence_config'].get('rdb_snapshot_start_time', 'Unknown')
                    print(f"│  │  ├─ 📅 Backup Period: {period}")
                    print(f"│  │  └─ ⏰ Backup Time: {backup_time}")
                
                # Show read replicas
                if instance['read_replicas_mode'] == 'READ_REPLICAS_ENABLED':
                    print(f"│  ├─ 📚 Read Replicas: {instance['replica_count']}")
                else:
                    print(f"│  ├─ 📚 Read Replicas: ❌ Disabled")
                
                # Show Redis configurations
                if instance['redis_config_count'] > 0:
                    print(f"│  ├─ ⚙️  Redis Config: {instance['redis_config_count']} parameters")
                    for key, value in list(instance['redis_configs'].items())[:3]:
                        print(f"│  │  ├─ {key}: {value}")
                    if instance['redis_config_count'] > 3:
                        print(f"│  │  └─ ... and {instance['redis_config_count'] - 3} more configs")
                
                # Show network configuration
                print(f"│  ├─ 🌐 Network:")
                if instance['authorized_network']:
                    network_name = instance['authorized_network'].split('/')[-1]
                    print(f"│  │  ├─ 🔗 VPC Network: {network_name}")
                else:
                    print(f"│  │  ├─ 🔗 VPC Network: default")
                
                if instance['reserved_ip_range']:
                    print(f"│  │  └─ 📍 IP Range: {instance['reserved_ip_range']}")
                else:
                    print(f"│  │  └─ 📍 IP Range: Auto-assigned")
                
                # Show maintenance window
                if instance['maintenance_policy']:
                    maintenance = instance['maintenance_policy']
                    if 'weekly_maintenance_window' in maintenance:
                        window = maintenance['weekly_maintenance_window'][0]
                        day = window.get('day', 'UNKNOWN')
                        hour = window.get('start_time', {}).get('hours', 0)
                        print(f"│  ├─ 🔧 Maintenance: {day} at {hour:02d}:00")
                else:
                    print(f"│  ├─ 🔧 Maintenance: Default window")
                
                # Show labels
                if instance['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {instance['label_count']}")
                    for key, value in list(instance['labels'].items())[:3]:
                        print(f"│  │  ├─ {key}: {value}")
                    if instance['label_count'] > 3:
                        print(f"│  │  └─ ... and {instance['label_count'] - 3} more")
                
                # Show connectivity info
                print(f"│  ├─ 🔗 Connectivity:")
                print(f"│  │  ├─ 🌐 Primary endpoint: {instance['instance_name']}.{instance['region']}.c.memorystore.internal:6379")
                if instance['read_replicas_mode'] == 'READ_REPLICAS_ENABLED':
                    print(f"│  │  ├─ 📖 Read endpoint: {instance['instance_name']}-ro.{instance['region']}.c.memorystore.internal:6379")
                print(f"│  │  └─ 🔌 VPC network access only")
                
                # Show performance characteristics
                print(f"│  ├─ 🚀 Performance:")
                print(f"│  │  ├─ ⚡ Sub-millisecond latency")
                print(f"│  │  ├─ 📊 100K+ operations/sec")
                if instance['tier'] == 'STANDARD_HA':
                    print(f"│  │  ├─ 🔄 Automatic failover")
                    print(f"│  │  └─ 📈 99.9% availability SLA")
                else:
                    print(f"│  │  └─ 📈 99.5% availability SLA")
                
                print(f"│  └─ 💰 Estimated Cost: ${instance['estimated_cost']:.2f}/month")
            print(f"╰─")

        # Show existing instances being kept
        if instances_to_keep:
            print(f"\n╭─ ⚡ Existing Redis Instances to KEEP: {len(instances_to_keep)}")
            for instance in instances_to_keep:
                state_icon = "🟢" if instance['state'] == 'READY' else "🟡" if instance['state'] == 'CREATING' else "🔴"
                print(f"├─ {state_icon} {instance['instance_name']}")
                print(f"│  ├─ 📊 Memory: {instance['memory_size_gb']}GB")
                print(f"│  ├─ 🏗️  Tier: {instance['tier']}")
                print(f"│  ├─ ⚡ Version: {instance['redis_version']}")
                print(f"│  ├─ 📍 Location: {instance['location_id']}")
                print(f"│  ├─ 📊 State: {instance['state']}")
                
                if instance['alternative_location_id']:
                    print(f"│  ├─ 🌐 Alternative Zone: {instance['alternative_location_id']}")
                
                print(f"│  ├─ 🔑 Authentication: {'✅ Enabled' if instance['auth_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🔒 Encryption: {instance['transit_encryption_mode']}")
                print(f"│  ├─ 💾 Persistence: {instance['persistence_mode']}")
                
                if instance['read_replicas_mode'] == 'READ_REPLICAS_ENABLED':
                    print(f"│  ├─ 📚 Read Replicas: {instance['replica_count']}")
                
                if instance['redis_config_count'] > 0:
                    print(f"│  ├─ ⚙️  Redis Config: {instance['redis_config_count']} parameters")
                
                # Show endpoints
                if instance['redis_endpoint']:
                    print(f"│  ├─ 🌐 Primary Endpoint: {instance['redis_endpoint']}")
                elif instance['host'] != 'unknown':
                    print(f"│  ├─ 🌐 Primary Endpoint: {instance['host']}:{instance['port']}")
                
                if instance['read_endpoint']:
                    print(f"│  ├─ 📖 Read Endpoint: {instance['read_endpoint']}:{instance['read_endpoint_port']}")
                
                if instance['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {instance['label_count']}")
                
                print(f"│  └─ 📅 Created: {instance.get('create_time', 'Unknown')[:10] if instance.get('create_time') else 'Unknown'}")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 Memorystore Redis Costs:")
        if instances_to_create:
            instance = instances_to_create[0]
            
            # Basic tier costs (simplified estimation)
            memory_gb = instance['memory_size_gb']
            
            if instance['tier'] == 'BASIC':
                # Basic tier: $0.049/GB/hour
                hourly_cost = memory_gb * 0.049
                monthly_cost = hourly_cost * 24 * 30
                tier_note = "Basic (single node)"
            else:
                # Standard HA tier: $0.054/GB/hour
                hourly_cost = memory_gb * 0.054
                monthly_cost = hourly_cost * 24 * 30
                tier_note = "Standard HA (high availability)"
            
            print(f"   ├─ ⚡ Redis Instance ({tier_note}): ${monthly_cost:.2f}/month")
            print(f"   ├─ 📊 Memory ({memory_gb}GB): ${hourly_cost:.3f}/hour")
            
            if instance['read_replicas_mode'] == 'READ_REPLICAS_ENABLED':
                replica_cost = monthly_cost * instance['replica_count']
                print(f"   ├─ 📚 Read Replicas ({instance['replica_count']}x): ${replica_cost:.2f}/month")
                monthly_cost += replica_cost
            
            if instance['has_persistence']:
                print(f"   ├─ 💾 Persistence: Included")
            
            print(f"   ├─ 🌐 Network egress: $0.12/GB (first 1GB free)")
            print(f"   └─ 📊 Total Estimated: ${monthly_cost:.2f}/month")
        else:
            print(f"   ├─ ⚡ Basic tier: $0.049/GB/hour")
            print(f"   ├─ ⚡ Standard HA: $0.054/GB/hour") 
            print(f"   ├─ 📚 Read replicas: Same cost per replica")
            print(f"   ├─ 💾 Persistence: Included")
            print(f"   └─ 🌐 Network egress: $0.12/GB")

        return {
            'resource_type': 'gcp_memorystore',
            'name': desired_instance_name,
            'instances_to_create': instances_to_create,
            'instances_to_keep': instances_to_keep,
            'instances_to_remove': instances_to_remove,
            'existing_instances': existing_instances,
            'instance_id': desired_instance_name,
            'memory_size_gb': self.memory_size_gb,
            'tier': self.tier,
            'redis_version': self.redis_version,
            'estimated_cost': f"${self._estimate_memorystore_cost():.2f}/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create the Memorystore Redis instance"""
        self._ensure_authenticated()
        
        existing_instance = self._find_existing_instance()
        if existing_instance:
            print(f"🔄 Memorystore instance '{self.instance_id}' already exists")
            self._update_connection_details(existing_instance)
            return self._get_instance_info()
        
        print(f"🚀 Creating Memorystore Redis instance: {self.instance_id}")
        return self._create_new_instance()

    def destroy(self) -> Dict[str, Any]:
        """Destroy the Memorystore Redis instance"""
        self._ensure_authenticated()
        print(f"🗑️  Destroying Memorystore Redis instance: {self.instance_id}")

        try:
            # Delete instance
            try:
                request = self.memorystore_client.projects().locations().instances().delete(
                    name=self.instance_name
                )
                operation = request.execute()
                print(f"   🗑️  Initiated deletion: {self.instance_id}")
                
                # Wait for deletion to complete
                self._wait_for_deletion(operation)
                
            except Exception as e:
                print(f"⚠️  Failed to delete instance: {e}")

            print(f"✅ Memorystore Redis instance destroyed!")

            return {'success': True, 'instance_id': self.instance_id, 'status': 'deleted'}

        except Exception as e:
            print(f"❌ Failed to destroy Memorystore instance: {str(e)}")
            return {'success': False, 'error': str(e)}

    def wait_for_creation(self, max_wait: int = 1800) -> bool:
        """
        Wait for Memorystore instance creation to complete.
        
        Args:
            max_wait: Maximum wait time in seconds (default: 30 minutes)
            
        Returns:
            bool: True if creation completed successfully, False otherwise
        """
        try:
            wait_time = 0
            
            print(f"   ⏳ Waiting for instance creation (max {max_wait//60} minutes)...")
            
            while wait_time < max_wait:
                try:
                    request = self.memorystore_client.projects().locations().instances().get(
                        name=self.instance_name
                    )
                    instance = request.execute()
                    
                    state = instance.get('state', 'UNKNOWN')
                    if state == 'READY':
                        self.instance_state = 'READY'
                        self.host = instance.get('host', '')
                        self.port = instance.get('port', 6379)
                        self.redis_endpoint = f"{self.host}:{self.port}"
                        
                        if instance.get('readEndpoint'):
                            self.read_endpoint = f"{instance['readEndpoint']}:{instance.get('readEndpointPort', 6379)}"
                        
                        print(f"✅ Instance created successfully!")
                        print(f"📍 Primary Endpoint: {self.redis_endpoint}")
                        if self.read_endpoint:
                            print(f"📖 Read Endpoint: {self.read_endpoint}")
                        return True
                    elif state in ['CREATING', 'UPDATING']:
                        # Still in progress
                        pass
                    elif state in ['DELETING', 'IMPORT_FAILED', 'FAILOVER_IN_PROGRESS']:
                        print(f"❌ Instance creation failed with state: {state}")
                        return False
                        
                except Exception:
                    # Instance might not exist yet
                    pass
                
                time.sleep(30)  # Check every 30 seconds
                wait_time += 30
                
                # Show progress every 5 minutes
                if wait_time % 300 == 0:
                    print(f"   ⏳ Still waiting... ({wait_time//60} minutes elapsed)")
            
            print(f"⚠️  Instance creation taking longer than expected ({max_wait//60} minutes)")
            return False

        except Exception as e:
            print(f"⚠️  Failed to wait for creation: {e}")
            return False

    def optimize_for(self, optimization_target: str):
        """
        Cross-Cloud Magic: Optimize instance configuration for specific targets.
        
        Args:
            optimization_target: Target to optimize for ('cost', 'performance', 'reliability', 'compliance')
        """
        if optimization_target.lower() == "cost":
            return self._optimize_for_cost()
        elif optimization_target.lower() == "performance":
            return self._optimize_for_performance()
        elif optimization_target.lower() == "reliability":
            return self._optimize_for_reliability()
        elif optimization_target.lower() == "compliance":
            return self._optimize_for_compliance()
        else:
            print(f"⚠️  Unknown optimization target: {optimization_target}")
            return self

    def _optimize_for_cost(self):
        """Optimize configuration for cost efficiency"""
        print("🏗️  Applying Cross-Cloud Magic: Cost Optimization")
        
        # Use basic tier for cost savings if possible
        if self.memory_size_gb <= 4:
            self.tier = 'BASIC'
        
        # Disable read replicas to save cost
        self.read_replicas_mode = 'READ_REPLICAS_DISABLED'
        self.replica_count = 0
        
        # Disable persistence to save backup costs (if appropriate)
        self.persistence_config = {'persistence_mode': 'DISABLED'}
        
        # Add cost optimization labels
        self.instance_labels.update({
            "optimization": "cost",
            "cost_management": "enabled",
            "billing_alert": "enabled"
        })
        
        print("   ├─ 🏗️  Set to basic tier for cost savings")
        print("   ├─ 📚 Disabled read replicas")
        print("   ├─ 💾 Disabled persistence")
        print("   └─ 🏷️  Added cost optimization labels")
        
        return self

    def _optimize_for_performance(self):
        """Optimize configuration for performance"""
        print("🏗️  Applying Cross-Cloud Magic: Performance Optimization")
        
        # Use Standard HA for better performance
        self.tier = 'STANDARD_HA'
        
        # Enable read replicas for read performance
        self.read_replicas_mode = 'READ_REPLICAS_ENABLED'
        self.replica_count = 2
        
        # Optimize Redis configs for performance
        self.redis_configs.update({
            'maxmemory-policy': 'allkeys-lru',
            'timeout': '0',
            'tcp-keepalive': '60'
        })
        
        # Add performance labels
        self.instance_labels.update({
            "optimization": "performance",
            "monitoring": "enhanced",
            "caching": "optimized"
        })
        
        print("   ├─ 🏗️  Set to Standard HA tier")
        print("   ├─ 📚 Enabled read replicas for read performance")
        print("   ├─ ⚙️  Optimized Redis configurations")
        print("   └─ 🏷️  Added performance optimization labels")
        
        return self

    def _optimize_for_reliability(self):
        """Optimize configuration for reliability"""
        print("🏗️  Applying Cross-Cloud Magic: Reliability Optimization")
        
        # Use Standard HA for high availability
        self.tier = 'STANDARD_HA'
        
        # Enable persistence for data durability
        self.persistence_config = {
            'persistence_mode': 'RDB',
            'rdb_snapshot_period': 'TWELVE_HOURS',
            'rdb_snapshot_start_time': '0 2,14 * * *'  # Twice daily
        }
        
        # Enable read replicas for failover
        self.read_replicas_mode = 'READ_REPLICAS_ENABLED'
        self.replica_count = 1
        
        # Set maintenance window
        self.maintenance_policy = {
            'weekly_maintenance_window': [{
                'day': 'SUNDAY',
                'start_time': {'hours': 3, 'minutes': 0}
            }]
        }
        
        # Add reliability labels
        self.instance_labels.update({
            "optimization": "reliability",
            "monitoring": "comprehensive",
            "alerting": "enabled",
            "backup": "enabled"
        })
        
        print("   ├─ 🏗️  Set to Standard HA tier")
        print("   ├─ 💾 Enabled persistence with twice-daily backups")
        print("   ├─ 📚 Enabled read replicas for failover")
        print("   ├─ 🔧 Set maintenance window")
        print("   └─ 🏷️  Added reliability optimization labels")
        
        return self

    def _optimize_for_compliance(self):
        """Optimize configuration for compliance requirements"""
        print("🏗️  Applying Cross-Cloud Magic: Compliance Optimization")
        
        # Enable all security features
        self.auth_enabled = True
        self.transit_encryption_mode = 'SERVER_AUTHENTICATION'
        
        # Enable persistence for audit trails
        self.persistence_config = {
            'persistence_mode': 'RDB',
            'rdb_snapshot_period': 'TWENTY_FOUR_HOURS',
            'rdb_snapshot_start_time': '0 2 * * *'
        }
        
        # Use Standard HA for compliance requirements
        self.tier = 'STANDARD_HA'
        
        # Add compliance labels
        self.instance_labels.update({
            "optimization": "compliance",
            "security": "maximum",
            "audit": "enabled",
            "compliance": "sox_pci",
            "encryption": "required"
        })
        
        print("   ├─ 🔑 Enabled authentication")
        print("   ├─ 🔐 Enabled transit encryption")
        print("   ├─ 💾 Enabled persistence for audit trails")
        print("   ├─ 🏗️  Set to Standard HA tier")
        print("   └─ 🏷️  Added compliance optimization labels")
        
        return self

    def _find_existing_instance(self) -> Optional[Dict[str, Any]]:
        """Find existing instance by name"""
        try:
            request = self.memorystore_client.projects().locations().instances().get(
                name=self.instance_name
            )
            instance = request.execute()
            return instance
        except Exception:
            return None

    def _create_new_instance(self) -> Dict[str, Any]:
        """Create new Memorystore instance"""
        try:
            from googleapiclient import discovery
            
            # Prepare instance configuration
            instance_config = {
                'name': self.instance_name,
                'displayName': self.instance_id,
                'memorySizeGb': self.memory_size_gb,
                'tier': self.tier,
                'redisVersion': self.redis_version,
                'authEnabled': self.auth_enabled,
                'transitEncryptionMode': self.transit_encryption_mode,
                'labels': self.instance_labels
            }
            
            # Add optional configurations
            if self.zone and self.tier == 'BASIC':
                instance_config['locationId'] = self.zone
            
            if self.authorized_network:
                instance_config['authorizedNetwork'] = self.authorized_network
                
            if self.reserved_ip_range:
                instance_config['reservedIpRange'] = self.reserved_ip_range
                
            if self.auth_string:
                instance_config['authString'] = self.auth_string
                
            if self.persistence_config:
                instance_config['persistenceConfig'] = self.persistence_config
                
            if self.maintenance_policy:
                instance_config['maintenancePolicy'] = self.maintenance_policy
                
            if self.redis_configs:
                instance_config['redisConfigs'] = self.redis_configs
                
            if self.read_replicas_mode == 'READ_REPLICAS_ENABLED':
                instance_config['readReplicasMode'] = self.read_replicas_mode
                instance_config['replicaCount'] = self.replica_count
            
            # Create the instance
            request = self.memorystore_client.projects().locations().instances().create(
                parent=f"projects/{self.project_id}/locations/{self.region}",
                instanceId=self.instance_id,
                body=instance_config
            )
            operation = request.execute()
            
            print(f"   📋 Instance creation initiated: {self.instance_id}")
            print(f"   📊 Memory: {self.memory_size_gb}GB")
            print(f"   🏗️  Tier: {self.tier}")
            print(f"   ⚡ Version: {self.redis_version}")
            
            # Wait for creation to complete
            creation_success = self.wait_for_creation()
            
            if creation_success:
                print(f"✅ Memorystore Redis instance '{self.instance_id}' created successfully!")
                
                if self.auth_enabled:
                    print(f"   🔑 AUTH enabled (retrieve auth string from console)")
                
                if self.transit_encryption_mode != 'DISABLED':
                    print(f"   🔒 Transit encryption: {self.transit_encryption_mode}")
            else:
                print(f"⚠️  Instance created but deployment may still be in progress")

            return self._get_instance_info()

        except Exception as e:
            print(f"❌ Failed to create Memorystore instance: {str(e)}")
            raise

    def _wait_for_deletion(self, operation: Dict[str, Any]):
        """Wait for deletion operation to complete"""
        try:
            operation_name = operation.get('name', '')
            if not operation_name:
                return
                
            wait_time = 0
            max_wait = 600  # 10 minutes
            
            print(f"   ⏳ Waiting for deletion to complete...")
            
            while wait_time < max_wait:
                try:
                    request = self.memorystore_client.projects().locations().operations().get(
                        name=operation_name
                    )
                    op = request.execute()
                    
                    if op.get('done', False):
                        if 'error' in op:
                            print(f"❌ Deletion failed: {op['error']}")
                        else:
                            print(f"✅ Deletion completed successfully")
                        return
                        
                except Exception:
                    # Operation might be done and cleaned up
                    break
                
                time.sleep(15)
                wait_time += 15
                
        except Exception as e:
            print(f"⚠️  Could not track deletion progress: {e}")

    def _update_connection_details(self, instance: Dict[str, Any]):
        """Update connection details from existing instance"""
        self.host = instance.get('host', '')
        self.port = instance.get('port', 6379)
        self.redis_endpoint = f"{self.host}:{self.port}" if self.host else None
        
        if instance.get('readEndpoint'):
            self.read_endpoint = f"{instance['readEndpoint']}:{instance.get('readEndpointPort', 6379)}"
        
        self.instance_state = instance.get('state', 'UNKNOWN')

    def _get_instance_info(self) -> Dict[str, Any]:
        """Get instance information"""
        try:
            return {
                'success': True,
                'instance_id': self.instance_id,
                'instance_name': self.instance_name,
                'memory_size_gb': self.memory_size_gb,
                'tier': self.tier,
                'redis_version': self.redis_version,
                'region': self.region,
                'zone': self.zone,
                'primary_endpoint': self.redis_endpoint,
                'read_endpoint': self.read_endpoint,
                'host': self.host,
                'port': self.port,
                'auth_enabled': self.auth_enabled,
                'transit_encryption_mode': self.transit_encryption_mode,
                'state': self.instance_state,
                'has_persistence': self.has_persistence(),
                'has_read_replicas': self.has_read_replicas(),
                'has_encryption': self.has_encryption(),
                'redis_config_count': len(self.redis_configs),
                'label_count': len(self.instance_labels),
                'instance_type': self._get_instance_type_from_config(),
                'estimated_monthly_cost': f"${self._estimate_memorystore_cost():.2f}",
                'connection_string': self.connection_string()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def connection_string(self) -> str:
        """Get Redis connection string"""
        if not self.host:
            return "Instance not yet created"
        
        if self.auth_enabled and self.auth_string:
            return f"redis://:{self.auth_string}@{self.host}:{self.port}"
        else:
            return f"redis://{self.host}:{self.port}"

    def get_status(self) -> Dict[str, Any]:
        """Get instance status and health information"""
        return {
            "instance_id": self.instance_id,
            "state": self.instance_state,
            "tier": self.tier,
            "memory_size_gb": self.memory_size_gb,
            "redis_version": self.redis_version,
            "primary_endpoint": self.redis_endpoint,
            "read_endpoint": self.read_endpoint,
            "connection_string": self.connection_string(),
            "auth_enabled": self.auth_enabled,
            "has_persistence": self.has_persistence(),
            "has_read_replicas": self.has_read_replicas(),
            "has_encryption": self.has_encryption()
        }
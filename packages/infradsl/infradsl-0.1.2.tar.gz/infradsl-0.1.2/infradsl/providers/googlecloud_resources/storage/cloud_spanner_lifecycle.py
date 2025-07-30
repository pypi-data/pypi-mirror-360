"""
Google Cloud Spanner Lifecycle Mixin

Lifecycle operations for Google Cloud Spanner.
Provides create, destroy, and preview operations with smart state management.
"""

import time
from typing import Dict, Any, List, Optional, Union


class CloudSpannerLifecycleMixin:
    """
    Mixin for Google Cloud Spanner lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update Spanner instance and databases
    - destroy(): Clean up Spanner instance and databases
    - Smart state management and cost estimation
    - Cross-Cloud Magic optimization
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        # Check authentication first
        try:
            self._ensure_authenticated()
        except Exception:
            print("⚠️  Authentication required for Cloud Spanner preview")
            
        # Get current instance and database state
        existing_instances = self._discover_existing_instances()
        
        # Categorize what will happen
        instances_to_create = []
        instances_to_keep = []
        instances_to_update = []
        databases_to_create = []
        
        target_instance_id = self.instance_id or self.instance_name
        
        if target_instance_id not in existing_instances:
            # New Spanner instance
            compute_capacity = self.get_compute_capacity()
            
            instances_to_create.append({
                "instance_id": target_instance_id,
                "instance_name": self.instance_name,
                "display_name": self.display_name or self.instance_name,
                "config": self.instance_config,
                "multi_region": self.is_multi_region(),
                "compute_capacity": compute_capacity,
                "node_count": self.node_count,
                "processing_units": self.processing_units,
                "databases": [db["database_id"] for db in self.databases],
                "database_count": len(self.databases),
                "backup_enabled": self.backup_enabled,
                "backup_retention": self.backup_retention_period,
                "monitoring_enabled": self.monitoring_enabled,
                "deletion_protection": self.deletion_protection,
                "labels": self.spanner_labels,
                "estimated_cost": self._estimate_spanner_cost(),
                "estimated_qps": self.get_estimated_qps()
            })
            
            # All databases will be created
            for db_config in self.databases:
                databases_to_create.append({
                    "database_id": db_config["database_id"],
                    "instance_id": target_instance_id,
                    "retention_period": db_config.get("version_retention_period", "1h"),
                    "encryption": bool(db_config.get("encryption_config")),
                    "default_leader": db_config.get("default_leader")
                })
        else:
            # Existing instance
            existing_instance = existing_instances[target_instance_id]
            instances_to_keep.append(existing_instance)
            
            # Check for new databases
            existing_db_ids = {db["database_id"] for db in existing_instance.get("databases", [])}
            for db_config in self.databases:
                if db_config["database_id"] not in existing_db_ids:
                    databases_to_create.append({
                        "database_id": db_config["database_id"],
                        "instance_id": target_instance_id,
                        "retention_period": db_config.get("version_retention_period", "1h"),
                        "encryption": bool(db_config.get("encryption_config")),
                        "default_leader": db_config.get("default_leader")
                    })
                    
        print(f"\\n🗄️  Cloud Spanner Preview")
        
        # Show instances to create
        if instances_to_create:
            print(f"╭─ 🗄️  Spanner Instances to CREATE: {len(instances_to_create)}")
            for instance in instances_to_create:
                print(f"├─ 🆕 {instance['instance_id']}")
                print(f"│  ├─ 📝 Display Name: {instance['display_name']}")
                print(f"│  ├─ 🌍 Configuration: {instance['config']}")
                print(f"│  ├─ 🌐 Multi-Region: {'✅ Yes' if instance['multi_region'] else '❌ No'}")
                
                if instance['node_count']:
                    print(f"│  ├─ 🖥️  Nodes: {instance['node_count']}")
                else:
                    print(f"│  ├─ ⚡ Processing Units: {instance['processing_units']}")
                    
                print(f"│  ├─ 📊 Estimated QPS: {instance['estimated_qps']:,}")
                print(f"│  ├─ 🗄️  Databases: {instance['database_count']}")
                
                if instance['databases']:
                    for db in instance['databases'][:3]:
                        print(f"│  │  ├─ {db}")
                    if len(instance['databases']) > 3:
                        print(f"│  │  └─ ... and {len(instance['databases']) - 3} more")
                        
                print(f"│  ├─ 💾 Backup: {'✅ Enabled' if instance['backup_enabled'] else '❌ Disabled'}")
                if instance['backup_enabled']:
                    print(f"│  │  └─ ⏰ Retention: {instance['backup_retention']}")
                    
                print(f"│  ├─ 📊 Monitoring: {'✅ Enabled' if instance['monitoring_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🔒 Deletion Protection: {'✅ Enabled' if instance['deletion_protection'] else '❌ Disabled'}")
                
                if instance['labels']:
                    print(f"│  ├─ 🏷️  Labels: {len(instance['labels'])}")
                    
                cost = instance['estimated_cost']
                print(f"│  └─ 💰 Estimated Cost: ${cost:,.2f}/month")
            print(f"╰─")
            
        # Show existing instances
        if instances_to_keep:
            print(f"\\n╭─ ✅ Existing Spanner Instances: {len(instances_to_keep)}")
            for instance in instances_to_keep:
                print(f"├─ ✅ {instance['instance_id']}")
                print(f"│  ├─ 📝 Name: {instance['instance_name']}")
                print(f"│  ├─ 🌍 Config: {instance['config']}")
                print(f"│  ├─ 🌐 Multi-Region: {'✅ Yes' if instance['multi_region'] else '❌ No'}")
                
                if instance['node_count']:
                    print(f"│  ├─ 🖥️  Nodes: {instance['node_count']}")
                if instance.get('processing_units'):
                    print(f"│  ├─ ⚡ Processing Units: {instance['processing_units']}")
                    
                print(f"│  ├─ 🟢 State: {instance['state']}")
                print(f"│  ├─ 🗄️  Databases: {instance['database_count']}")
                print(f"│  └─ 📅 Created: {instance['create_time']}")
            print(f"╰─")
            
        # Show databases to create
        if databases_to_create:
            print(f"\\n╭─ 🗄️  Databases to CREATE: {len(databases_to_create)}")
            for db in databases_to_create:
                print(f"├─ 🆕 {db['database_id']}")
                print(f"│  ├─ 🗄️  Instance: {db['instance_id']}")
                print(f"│  ├─ ⏰ Retention: {db['retention_period']}")
                print(f"│  ├─ 🔐 Encryption: {'✅ Custom' if db['encryption'] else '🔒 Google-managed'}")
                if db.get('default_leader'):
                    print(f"│  └─ 👑 Default Leader: {db['default_leader']}")
            print(f"╰─")
            
        # Show Spanner features
        print(f"\\n🗄️  Cloud Spanner Features:")
        print(f"   ├─ 🌍 Global consistency and ACID transactions")
        print(f"   ├─ 📈 Horizontal scaling (up to 10,000+ nodes)")
        print(f"   ├─ 🔄 Automatic multi-region replication")
        print(f"   ├─ 📊 99.999% availability SLA")
        print(f"   ├─ 🚀 Low-latency reads and writes")
        print(f"   ├─ 🛠️  SQL interface with ANSI SQL support")
        print(f"   ├─ 🔄 Automatic failover and recovery")
        print(f"   └─ 📊 Built-in monitoring and insights")
        
        # Cost information
        print(f"\\n💰 Cloud Spanner Pricing:")
        if instances_to_create:
            instance = instances_to_create[0]
            if instance['multi_region']:
                print(f"   ├─ 🖥️  Multi-region nodes: $4.50/node/hour")
                print(f"   ├─ ⚡ Multi-region processing units: $0.90/100 units/hour")
                print(f"   ├─ 💾 Multi-region storage: $0.50/GB/month")
            else:
                print(f"   ├─ 🖥️  Regional nodes: $1.50/node/hour")
                print(f"   ├─ ⚡ Regional processing units: $0.30/100 units/hour")
                print(f"   ├─ 💾 Regional storage: $0.30/GB/month")
                
            print(f"   ├─ 💾 Backup storage: $0.126/GB/month")
            print(f"   ├─ 🌐 Network egress: $0.12/GB")
            print(f"   └─ 📊 Estimated: ${instance['estimated_cost']:,.2f}/month")
        else:
            print(f"   ├─ 🖥️  Nodes: $1.50-$4.50/node/hour")
            print(f"   ├─ ⚡ Processing units: $0.30-$0.90/100 units/hour")
            print(f"   ├─ 💾 Storage: $0.30-$0.50/GB/month")
            print(f"   └─ 💾 Backups: $0.126/GB/month")
            
        return {
            "resource_type": "cloud_spanner",
            "name": self.instance_name,
            "instances_to_create": instances_to_create,
            "instances_to_keep": instances_to_keep,
            "instances_to_update": instances_to_update,
            "databases_to_create": databases_to_create,
            "existing_instances": existing_instances,
            "instance_id": target_instance_id,
            "project_id": self.project_id,
            "estimated_cost": f"${self._estimate_spanner_cost():,.2f}/month"
        }
        
    def create(self) -> Dict[str, Any]:
        """Create Spanner instance and databases"""
        if not self.project_id:
            raise ValueError("Project ID is required. Use .project('your-project-id')")
            
        print(f"🚀 Creating Cloud Spanner: {self.instance_name}")
        
        target_instance_id = self.instance_id or self.instance_name
        
        # Check if instance exists
        instance_state = self._fetch_current_instance_state()
        
        results = {
            "success": True,
            "instance_created": False,
            "databases_created": [],
            "failed": []
        }
        
        if not instance_state.get("exists"):
            # Create instance
            try:
                print(f"   🗄️  Creating Spanner instance: {target_instance_id}")
                print(f"      ├─ Config: {self.instance_config}")
                
                if self.node_count:
                    print(f"      ├─ Nodes: {self.node_count}")
                else:
                    print(f"      ├─ Processing Units: {self.processing_units}")
                    
                instance_result = self._create_spanner_instance()
                
                if instance_result["success"]:
                    print(f"   ✅ Instance created successfully")
                    results["instance_created"] = True
                    
                    # Update state tracking
                    self.instance_exists = True
                    self.instance_created = True
                    self.deployment_status = "deployed"
                else:
                    raise Exception(instance_result.get("error", "Instance creation failed"))
                    
            except Exception as e:
                print(f"   ❌ Instance creation failed: {str(e)}")
                results["failed"].append({
                    "resource": "instance",
                    "name": target_instance_id,
                    "error": str(e)
                })
                results["success"] = False
                return results
        else:
            print(f"   ✅ Instance already exists: {target_instance_id}")
            
        # Create databases
        for db_config in self.databases:
            database_id = db_config["database_id"]
            
            try:
                print(f"   🗄️  Creating database: {database_id}")
                
                db_result = self._create_spanner_database(target_instance_id, db_config)
                
                if db_result["success"]:
                    print(f"   ✅ Database created: {database_id}")
                    results["databases_created"].append(database_id)
                else:
                    raise Exception(db_result.get("error", "Database creation failed"))
                    
            except Exception as e:
                print(f"   ❌ Database creation failed: {database_id} - {str(e)}")
                results["failed"].append({
                    "resource": "database",
                    "name": database_id,
                    "error": str(e)
                })
                
        # Show summary
        print(f"\\n📊 Creation Summary:")
        print(f"   ├─ 🗄️  Instance: {'✅ Created' if results['instance_created'] else '✅ Exists'}")
        print(f"   ├─ 🗄️  Databases: {len(results['databases_created'])} created")
        print(f"   └─ ❌ Failed: {len(results['failed'])}")
        
        if results["success"]:
            cost = self._estimate_spanner_cost()
            print(f"\\n💰 Estimated Cost: ${cost:,.2f}/month")
            print(f"🌐 Console: https://console.cloud.google.com/spanner/instances?project={self.project_id}")
            
        # Final result
        results.update({
            "instance_id": target_instance_id,
            "project_id": self.project_id,
            "config": self.instance_config,
            "databases": results["databases_created"],
            "estimated_cost": f"${self._estimate_spanner_cost():,.2f}/month",
            "console_url": f"https://console.cloud.google.com/spanner/instances?project={self.project_id}"
        })
        
        return results
        
    def destroy(self) -> Dict[str, Any]:
        """Destroy Spanner instance and databases"""
        print(f"🗑️  Destroying Cloud Spanner: {self.instance_name}")
        
        target_instance_id = self.instance_id or self.instance_name
        
        if self.deletion_protection:
            print(f"   ⚠️  Deletion protection is enabled")
            print(f"   🔧 To delete the instance:")
            print(f"      1. Disable deletion protection first")
            print(f"      2. Use .deletion_protection(False)")
            print(f"      3. Then call .destroy() again")
            
            return {
                "success": False,
                "error": "Deletion protection enabled",
                "instance_id": target_instance_id,
                "message": "Disable deletion protection first"
            }
            
        try:
            # Check if instance exists
            instance_state = self._fetch_current_instance_state()
            
            if not instance_state.get("exists"):
                print(f"   ℹ️  Instance doesn't exist: {target_instance_id}")
                return {
                    "success": True,
                    "message": "Instance doesn't exist"
                }
                
            print(f"   🗑️  Deleting Spanner instance: {target_instance_id}")
            print(f"   ⚠️  This will delete ALL databases in the instance")
            
            # Delete instance (this also deletes all databases)
            delete_result = self._delete_spanner_instance()
            
            if delete_result["success"]:
                print(f"   ✅ Instance deleted successfully")
                
                # Update state tracking
                self.instance_exists = False
                self.instance_created = False
                self.deployment_status = "destroyed"
                
                return {
                    "success": True,
                    "instance_id": target_instance_id,
                    "project_id": self.project_id,
                    "message": "Instance and all databases deleted"
                }
            else:
                raise Exception(delete_result.get("error", "Deletion failed"))
                
        except Exception as e:
            print(f"   ❌ Deletion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _create_spanner_instance(self) -> Dict[str, Any]:
        """Create Spanner instance using API"""
        try:
            from google.cloud import spanner_admin_instance_v1
            
            if not self.spanner_admin_instance:
                return {"success": False, "error": "Spanner admin client not initialized"}
                
            # Prepare instance configuration
            instance_id = self.instance_id or self.instance_name
            
            instance = spanner_admin_instance_v1.Instance(
                display_name=self.display_name or self.instance_name,
                config=f"projects/{self.project_id}/instanceConfigs/{self.instance_config}",
                labels=self.spanner_labels
            )
            
            # Set compute capacity
            if self.processing_units:
                instance.processing_units = self.processing_units
            else:
                instance.node_count = self.node_count
                
            # Create instance request
            request = spanner_admin_instance_v1.CreateInstanceRequest(
                parent=f"projects/{self.project_id}",
                instance_id=instance_id,
                instance=instance
            )
            
            # Execute creation
            operation = self.spanner_admin_instance.create_instance(request=request)
            
            print(f"      ⏳ Waiting for instance creation (this may take several minutes)...")
            
            # Wait for operation to complete
            result = operation.result(timeout=900)  # 15 minutes timeout
            
            return {
                "success": True,
                "instance": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def _create_spanner_database(self, instance_id: str, db_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Spanner database using API"""
        try:
            from google.cloud import spanner_admin_database_v1
            
            if not self.spanner_admin_database:
                return {"success": False, "error": "Database admin client not initialized"}
                
            database_id = db_config["database_id"]
            
            # Create database request
            request = spanner_admin_database_v1.CreateDatabaseRequest(
                parent=f"projects/{self.project_id}/instances/{instance_id}",
                create_statement=f"CREATE DATABASE `{database_id}`"
            )
            
            # Execute creation
            operation = self.spanner_admin_database.create_database(request=request)
            
            # Wait for operation to complete
            result = operation.result(timeout=300)  # 5 minutes timeout
            
            return {
                "success": True,
                "database": result
            }
            
        except Exception as e:
            if "already exists" in str(e).lower():
                return {"success": True, "message": "Database already exists"}
            return {
                "success": False,
                "error": str(e)
            }
            
    def _delete_spanner_instance(self) -> Dict[str, Any]:
        """Delete Spanner instance using API"""
        try:
            from google.cloud import spanner_admin_instance_v1
            
            if not self.spanner_admin_instance:
                return {"success": False, "error": "Spanner admin client not initialized"}
                
            instance_id = self.instance_id or self.instance_name
            instance_path = f"projects/{self.project_id}/instances/{instance_id}"
            
            # Delete instance request
            request = spanner_admin_instance_v1.DeleteInstanceRequest(
                name=instance_path
            )
            
            # Execute deletion
            self.spanner_admin_instance.delete_instance(request=request)
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    # Cross-Cloud Magic Integration
    def optimize_for(self, optimization_target: str):
        """
        Cross-Cloud Magic: Optimize Cloud Spanner configuration for specific targets.
        
        Args:
            optimization_target: Target to optimize for ('cost', 'performance', 'security', 'user_experience')
        """
        if optimization_target.lower() == "cost":
            return self._optimize_for_cost()
        elif optimization_target.lower() == "performance":
            return self._optimize_for_performance()
        elif optimization_target.lower() == "security":
            return self._optimize_for_security()
        elif optimization_target.lower() == "user_experience":
            return self._optimize_for_user_experience()
        else:
            print(f"⚠️  Unknown optimization target: {optimization_target}")
            return self
            
    def _optimize_for_cost(self):
        """Optimize configuration for cost efficiency"""
        print("🏗️  Applying Cross-Cloud Magic: Cost Optimization")
        
        # Use minimum processing units and regional config
        self.processing_units(100)
        self.regional()
        
        # Minimal backup retention
        self.backup_retention("1d")
        self.deletion_protection(False)
        
        # Add cost optimization labels
        self.labels({
            "optimization": "cost",
            "capacity": "minimal",
            "region": "single"
        })
        
        print("   ├─ ⚡ Minimum processing units (100)")
        print("   ├─ 🌍 Regional configuration")
        print("   ├─ 💾 Minimal backup retention")
        print("   └─ 🏷️  Added cost optimization labels")
        
        return self
        
    def _optimize_for_performance(self):
        """Optimize configuration for performance"""
        print("🏗️  Applying Cross-Cloud Magic: Performance Optimization")
        
        # Use more nodes and multi-region
        self.large_instance()
        self.multi_region_us()
        
        # Enable all monitoring
        self.monitoring().query_insights().alerting()
        
        # Add performance labels
        self.labels({
            "optimization": "performance",
            "capacity": "high",
            "region": "multi"
        })
        
        print("   ├─ 🖥️  Large instance (5 nodes)")
        print("   ├─ 🌍 Multi-region US configuration")
        print("   ├─ 📊 Full monitoring and insights")
        print("   └─ 🏷️  Added performance optimization labels")
        
        return self
        
    def _optimize_for_security(self):
        """Optimize configuration for security"""
        print("🏗️  Applying Cross-Cloud Magic: Security Optimization")
        
        # Enable all security features
        self.deletion_protection()
        self.backup_retention("90d")
        self.point_in_time_recovery()
        
        # Enable monitoring for security insights
        self.monitoring().alerting()
        
        # Add security labels
        self.labels({
            "optimization": "security",
            "deletion_protection": "enabled",
            "backup_retention": "extended"
        })
        
        print("   ├─ 🔒 Deletion protection enabled")
        print("   ├─ 💾 Extended backup retention")
        print("   ├─ 🔄 Point-in-time recovery")
        print("   ├─ 📊 Security monitoring")
        print("   └─ 🏷️  Added security optimization labels")
        
        return self
        
    def _optimize_for_user_experience(self):
        """Optimize configuration for user experience"""
        print("🏗️  Applying Cross-Cloud Magic: User Experience Optimization")
        
        # Balance performance and cost
        self.medium_instance()
        self.multi_region_us()
        
        # Enable monitoring for UX insights
        self.monitoring().query_insights()
        
        # Add UX labels
        self.labels({
            "optimization": "user_experience",
            "capacity": "balanced",
            "monitoring": "enabled"
        })
        
        print("   ├─ ⚖️  Balanced instance size")
        print("   ├─ 🌍 Multi-region for low latency")
        print("   ├─ 📊 Query insights for optimization")
        print("   └─ 🏷️  Added UX optimization labels")
        
        return self
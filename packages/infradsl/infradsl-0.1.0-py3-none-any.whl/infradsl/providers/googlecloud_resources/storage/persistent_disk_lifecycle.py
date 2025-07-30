"""
Google Cloud Persistent Disk Lifecycle Mixin

Lifecycle operations for Google Cloud Persistent Disk.
Provides create, destroy, and preview operations with smart state management.
"""

import time
from typing import Dict, Any, List, Optional, Union


class PersistentDiskLifecycleMixin:
    """
    Mixin for Google Cloud Persistent Disk lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update persistent disk
    - destroy(): Clean up persistent disk
    - Smart state management and cost estimation
    - Cross-Cloud Magic optimization
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        # Check authentication first
        try:
            self._ensure_authenticated()
        except Exception:
            print("⚠️  Authentication required for Persistent Disk preview")
            
        # Get current disk state
        existing_disks = self._discover_existing_disks()
        
        # Categorize what will happen
        disks_to_create = []
        disks_to_keep = []
        disks_to_update = []
        
        if self.disk_name not in existing_disks:
            # New disk
            performance_specs = self.get_performance_specs()
            
            disk_config = {
                "disk_name": self.disk_name,
                "size_gb": self.size_gb,
                "disk_type": self.pd_type,
                "zone": self.zone,
                "region": self.region,
                "is_regional": bool(self.region),
                "interface": self.interface,
                "mode": self.mode,
                "auto_delete": self.auto_delete,
                "boot": self.boot,
                "multi_writer": self.multi_writer,
                "deletion_protection": self.enable_deletion_protection,
                "source_image": self.source_image,
                "source_image_family": self.source_image_family,
                "source_snapshot": self.source_snapshot,
                "performance_specs": performance_specs,
                "labels": self.disk_labels,
                "estimated_cost": self._estimate_disk_cost()
            }
            disks_to_create.append(disk_config)
        else:
            # Existing disk
            existing_disk = existing_disks[self.disk_name]
            disks_to_keep.append(existing_disk)
            
        print(f"\\n💾 Persistent Disk Preview")
        
        # Show disks to create
        if disks_to_create:
            print(f"╭─ 💾 Persistent Disks to CREATE: {len(disks_to_create)}")
            for disk in disks_to_create:
                print(f"├─ 🆕 {disk['disk_name']}")
                print(f"│  ├─ 📏 Size: {disk['size_gb']:,} GB ({disk['size_gb']/1024:.1f} TB)")
                print(f"│  ├─ 💿 Type: {disk['disk_type']}")
                
                if disk['is_regional']:
                    print(f"│  ├─ 🌍 Region: {disk['region']}")
                    if self.replica_zones:
                        print(f"│  │  └─ 🔄 Replica zones: {', '.join(self.replica_zones)}")
                else:
                    print(f"│  ├─ 📍 Zone: {disk['zone']}")
                    
                # Performance specs
                specs = disk['performance_specs']
                print(f"│  ├─ ⚡ Max Read IOPS: {specs['max_iops_read']:,}")
                print(f"│  ├─ ⚡ Max Write IOPS: {specs['max_iops_write']:,}")
                print(f"│  ├─ 🚀 Max Read Throughput: {specs['max_throughput_read']:,} MB/s")
                print(f"│  ├─ 🚀 Max Write Throughput: {specs['max_throughput_write']:,} MB/s")
                
                # Source configuration
                if disk['source_image']:
                    print(f"│  ├─ 🖼️  Source Image: {disk['source_image']}")
                elif disk['source_image_family']:
                    print(f"│  ├─ 👨‍👩‍👧‍👦 Image Family: {disk['source_image_family']}")
                elif disk['source_snapshot']:
                    print(f"│  ├─ 📸 Source Snapshot: {disk['source_snapshot']}")
                else:
                    print(f"│  ├─ 🆕 Blank Disk: No source")
                    
                # Configuration
                print(f"│  ├─ 🔌 Interface: {disk['interface']}")
                print(f"│  ├─ 📖 Mode: {disk['mode']}")
                print(f"│  ├─ 🥾 Boot Disk: {'✅ Yes' if disk['boot'] else '❌ No'}")
                print(f"│  ├─ 🗑️  Auto Delete: {'✅ Yes' if disk['auto_delete'] else '❌ No'}")
                print(f"│  ├─ 👥 Multi-writer: {'✅ Yes' if disk['multi_writer'] else '❌ No'}")
                print(f"│  ├─ 🔒 Deletion Protection: {'✅ Yes' if disk['deletion_protection'] else '❌ No'}")
                
                if disk['labels']:
                    print(f"│  ├─ 🏷️  Labels: {len(disk['labels'])}")
                    
                cost = disk['estimated_cost']
                print(f"│  └─ 💰 Estimated Cost: ${cost:,.2f}/month")
            print(f"╰─")
            
        # Show existing disks
        if disks_to_keep:
            print(f"\\n╭─ ✅ Existing Persistent Disks: {len(disks_to_keep)}")
            for disk in disks_to_keep:
                print(f"├─ ✅ {disk['disk_name']}")
                print(f"│  ├─ 📏 Size: {disk['size_gb']:,} GB")
                print(f"│  ├─ 💿 Type: {disk['disk_type']}")
                if disk.get('is_regional'):
                    print(f"│  ├─ 🌍 Region: {disk['region']}")
                else:
                    print(f"│  ├─ 📍 Zone: {disk['zone']}")
                print(f"│  ├─ 🟢 Status: {disk['status']}")
                print(f"│  ├─ 👥 Users: {len(disk['users'])} attached instances")
                print(f"│  └─ 📅 Created: {disk['creation_timestamp']}")
            print(f"╰─")
            
        # Show disk capabilities
        print(f"\\n💾 Persistent Disk Features:")
        print(f"   ├─ 🚀 High-performance block storage")
        print(f"   ├─ 🔄 Automatic replication and snapshots")
        print(f"   ├─ 📈 Dynamic resizing without downtime")
        print(f"   ├─ 🛡️  Built-in encryption at rest")
        print(f"   ├─ 👥 Multi-attach support (read-only/multi-writer)")
        print(f"   ├─ 🌍 Regional disks for high availability")
        print(f"   ├─ ⚡ NVMe interface for maximum performance")
        print(f"   └─ 💾 Up to 64TB per disk")
        
        # Performance information
        if disks_to_create:
            disk = disks_to_create[0]
            print(f"\\n⚡ Performance Comparison:")
            print(f"   ├─ 💿 Standard: Lowest cost, good for sequential workloads")
            print(f"   ├─ ⚖️  Balanced: Cost/performance balance, general purpose")
            print(f"   ├─ 🚀 SSD: High random IOPS, low latency")
            print(f"   └─ 🏎️  Extreme: Highest performance, customizable IOPS")
            
        # Cost information
        print(f"\\n💰 Persistent Disk Pricing:")
        print(f"   ├─ 💿 Standard: $0.040/GB/month")
        print(f"   ├─ ⚖️  Balanced: $0.100/GB/month")
        print(f"   ├─ 🚀 SSD: $0.170/GB/month")
        print(f"   ├─ 🏎️  Extreme: $0.650/GB/month")
        print(f"   ├─ 📸 Snapshots: $0.026/GB/month")
        if disks_to_create:
            print(f"   └─ 📊 Estimated: ${disks_to_create[0]['estimated_cost']:,.2f}/month")
        else:
            print(f"   └─ 🌍 Regional disks: 2x cost for high availability")
            
        return {
            "resource_type": "persistent_disk",
            "name": self.disk_name,
            "disks_to_create": disks_to_create,
            "disks_to_keep": disks_to_keep,
            "disks_to_update": disks_to_update,
            "existing_disks": existing_disks,
            "project_id": self.project_id,
            "estimated_cost": f"${self._estimate_disk_cost():,.2f}/month"
        }
        
    def create(self) -> Dict[str, Any]:
        """Create persistent disk"""
        if not self.project_id:
            raise ValueError("Project ID is required. Use .project('your-project-id')")
            
        if not (self.zone or self.region):
            raise ValueError("Zone or region is required. Use .zone() or .region()")
            
        print(f"🚀 Creating Persistent Disk: {self.disk_name}")
        
        # Check if disk exists
        disk_state = self._fetch_current_disk_state()
        
        results = {
            "success": True,
            "disk_created": False,
            "failed": []
        }
        
        if not disk_state.get("exists"):
            # Create disk
            try:
                print(f"   💾 Creating disk: {self.disk_name}")
                print(f"      ├─ Size: {self.size_gb:,} GB ({self.size_gb/1024:.1f} TB)")
                print(f"      ├─ Type: {self.pd_type}")
                
                if self.region:
                    print(f"      ├─ Region: {self.region}")
                    if self.replica_zones:
                        print(f"      │  └─ Replica zones: {', '.join(self.replica_zones)}")
                else:
                    print(f"      ├─ Zone: {self.zone}")
                    
                if self.source_image:
                    print(f"      ├─ Source Image: {self.source_image}")
                elif self.source_image_family:
                    print(f"      ├─ Image Family: {self.source_image_family}")
                elif self.source_snapshot:
                    print(f"      ├─ Source Snapshot: {self.source_snapshot}")
                else:
                    print(f"      ├─ Type: Blank disk")
                    
                disk_result = self._create_persistent_disk()
                
                if disk_result["success"]:
                    print(f"   ✅ Disk created successfully")
                    results["disk_created"] = True
                    
                    # Update state tracking
                    self.disk_exists = True
                    self.disk_created = True
                    self.deployment_status = "deployed"
                else:
                    raise Exception(disk_result.get("error", "Disk creation failed"))
                    
            except Exception as e:
                print(f"   ❌ Disk creation failed: {str(e)}")
                results["failed"].append({
                    "resource": "disk",
                    "name": self.disk_name,
                    "error": str(e)
                })
                results["success"] = False
                return results
        else:
            print(f"   ✅ Disk already exists: {self.disk_name}")
            
        # Show summary
        print(f"\\n📊 Creation Summary:")
        print(f"   ├─ 💾 Disk: {'✅ Created' if results['disk_created'] else '✅ Exists'}")
        print(f"   └─ ❌ Failed: {len(results['failed'])}")
        
        if results["success"]:
            cost = self._estimate_disk_cost()
            performance = self.get_performance_specs()
            
            print(f"\\n⚡ Performance Specs:")
            print(f"   ├─ 📊 Max Read IOPS: {performance['max_iops_read']:,}")
            print(f"   ├─ 📊 Max Write IOPS: {performance['max_iops_write']:,}")
            print(f"   ├─ 🚀 Max Read Throughput: {performance['max_throughput_read']:,} MB/s")
            print(f"   └─ 🚀 Max Write Throughput: {performance['max_throughput_write']:,} MB/s")
            
            print(f"\\n💰 Estimated Cost: ${cost:,.2f}/month")
            print(f"🌐 Console: https://console.cloud.google.com/compute/disks?project={self.project_id}")
            
        # Final result
        results.update({
            "disk_name": self.disk_name,
            "project_id": self.project_id,
            "size_gb": self.size_gb,
            "disk_type": self.pd_type,
            "zone": self.zone,
            "region": self.region,
            "estimated_cost": f"${self._estimate_disk_cost():,.2f}/month",
            "console_url": f"https://console.cloud.google.com/compute/disks?project={self.project_id}"
        })
        
        return results
        
    def destroy(self) -> Dict[str, Any]:
        """Destroy persistent disk"""
        print(f"🗑️  Destroying Persistent Disk: {self.disk_name}")
        
        if self.enable_deletion_protection:
            print(f"   ⚠️  Deletion protection is enabled")
            print(f"   🔧 To delete the disk:")
            print(f"      1. Disable deletion protection first")
            print(f"      2. Use .deletion_protection(False)")
            print(f"      3. Then call .destroy() again")
            
            return {
                "success": False,
                "error": "Deletion protection enabled",
                "disk_name": self.disk_name,
                "message": "Disable deletion protection first"
            }
            
        try:
            # Check if disk exists
            disk_state = self._fetch_current_disk_state()
            
            if not disk_state.get("exists"):
                print(f"   ℹ️  Disk doesn't exist: {self.disk_name}")
                return {
                    "success": True,
                    "message": "Disk doesn't exist"
                }
                
            # Check if disk is attached
            if disk_state.get("users"):
                print(f"   ⚠️  Disk is attached to instances: {', '.join(disk_state['users'])}")
                print(f"   🔧 Detach disk from instances before deletion")
                
                return {
                    "success": False,
                    "error": "Disk is attached",
                    "attached_instances": disk_state["users"],
                    "message": "Detach disk from instances first"
                }
                
            print(f"   🗑️  Deleting disk: {self.disk_name}")
            print(f"   ⚠️  This action cannot be undone")
            
            # Delete disk
            delete_result = self._delete_persistent_disk()
            
            if delete_result["success"]:
                print(f"   ✅ Disk deleted successfully")
                
                # Update state tracking
                self.disk_exists = False
                self.disk_created = False
                self.deployment_status = "destroyed"
                
                return {
                    "success": True,
                    "disk_name": self.disk_name,
                    "project_id": self.project_id,
                    "message": "Disk deleted successfully"
                }
            else:
                raise Exception(delete_result.get("error", "Deletion failed"))
                
        except Exception as e:
            print(f"   ❌ Deletion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _create_persistent_disk(self) -> Dict[str, Any]:
        """Create persistent disk using API"""
        try:
            from google.cloud import compute_v1
            
            if not self.disks_client or not self.project_id:
                return {"success": False, "error": "Disks client not initialized"}
                
            # Prepare disk configuration
            disk = compute_v1.Disk()
            disk.name = self.disk_name
            disk.size_gb = str(self.size_gb)
            disk.type = f"projects/{self.project_id}/zones/{self.zone or 'global'}/diskTypes/{self.pd_type}"
            
            if self.disk_description:
                disk.description = self.disk_description
                
            # Set source
            if self.source_image:
                disk.source_image = self.source_image
            elif self.source_image_family:
                disk.source_image_family = self.source_image_family
            elif self.source_snapshot:
                disk.source_snapshot = self.source_snapshot
            elif self.source_disk:
                disk.source_disk = self.source_disk
                
            # Set labels
            if self.disk_labels:
                disk.labels = self.disk_labels
                
            # Special configurations for pd-extreme
            if self.pd_type == "pd-extreme":
                if self.provisioned_iops:
                    disk.provisioned_iops = self.provisioned_iops
                if self.provisioned_throughput:
                    disk.provisioned_throughput_mb = self.provisioned_throughput
                    
            # Multi-writer
            if self.multi_writer:
                disk.multi_writer = True
                
            # Create request
            if self.region:
                # Regional disk
                regional_disks_client = compute_v1.RegionDisksClient()
                request = compute_v1.InsertRegionDiskRequest(
                    project=self.project_id,
                    region=self.region,
                    disk_resource=disk
                )
                
                operation = regional_disks_client.insert(request=request)
                
                print(f"      ⏳ Creating regional disk (this may take a few minutes)...")
                
                # Wait for operation
                wait_result = self._wait_for_regional_operation(operation, self.region)
                
            else:
                # Zonal disk
                request = compute_v1.InsertDiskRequest(
                    project=self.project_id,
                    zone=self.zone,
                    disk_resource=disk
                )
                
                operation = self.disks_client.insert(request=request)
                
                print(f"      ⏳ Creating zonal disk (this may take a few minutes)...")
                
                # Wait for operation
                wait_result = self._wait_for_zonal_operation(operation, self.zone)
                
            if wait_result["success"]:
                return {"success": True, "disk": disk}
            else:
                return {"success": False, "error": wait_result.get("error", "Operation failed")}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def _delete_persistent_disk(self) -> Dict[str, Any]:
        """Delete persistent disk using API"""
        try:
            from google.cloud import compute_v1
            
            if not self.disks_client or not self.project_id:
                return {"success": False, "error": "Disks client not initialized"}
                
            if self.region:
                # Regional disk
                regional_disks_client = compute_v1.RegionDisksClient()
                request = compute_v1.DeleteRegionDiskRequest(
                    project=self.project_id,
                    region=self.region,
                    disk=self.disk_name
                )
                
                operation = regional_disks_client.delete(request=request)
                wait_result = self._wait_for_regional_operation(operation, self.region)
                
            else:
                # Zonal disk
                request = compute_v1.DeleteDiskRequest(
                    project=self.project_id,
                    zone=self.zone,
                    disk=self.disk_name
                )
                
                operation = self.disks_client.delete(request=request)
                wait_result = self._wait_for_zonal_operation(operation, self.zone)
                
            return wait_result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def _wait_for_zonal_operation(self, operation, zone: str) -> Dict[str, Any]:
        """Wait for zonal operation to complete"""
        try:
            from google.cloud import compute_v1
            
            zone_operations_client = compute_v1.ZoneOperationsClient()
            
            # Wait for operation to complete
            result = zone_operations_client.wait(
                project=self.project_id,
                zone=zone,
                operation=operation.name,
                timeout=300  # 5 minutes
            )
            
            if result.status == compute_v1.Operation.Status.DONE:
                if result.error:
                    return {"success": False, "error": str(result.error)}
                return {"success": True}
            else:
                return {"success": False, "error": "Operation timeout"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _wait_for_regional_operation(self, operation, region: str) -> Dict[str, Any]:
        """Wait for regional operation to complete"""
        try:
            from google.cloud import compute_v1
            
            region_operations_client = compute_v1.RegionOperationsClient()
            
            # Wait for operation to complete
            result = region_operations_client.wait(
                project=self.project_id,
                region=region,
                operation=operation.name,
                timeout=300  # 5 minutes
            )
            
            if result.status == compute_v1.Operation.Status.DONE:
                if result.error:
                    return {"success": False, "error": str(result.error)}
                return {"success": True}
            else:
                return {"success": False, "error": "Operation timeout"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    # Cross-Cloud Magic Integration
    def optimize_for(self, optimization_target: str):
        """
        Cross-Cloud Magic: Optimize Persistent Disk configuration for specific targets.
        
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
        
        # Use standard disk type for lowest cost
        self.standard_disk()
        
        # Enable auto-delete to avoid orphaned disks
        self.auto_delete()
        
        # Disable deletion protection for dev environments
        self.deletion_protection(False)
        
        # Use SCSI interface (lower cost than NVMe)
        self.scsi_interface()
        
        # Add cost optimization labels
        self.labels({
            "optimization": "cost",
            "disk_tier": "standard",
            "auto_cleanup": "enabled"
        })
        
        print("   ├─ 💿 Standard disk type")
        print("   ├─ 🗑️  Auto-delete enabled")
        print("   ├─ 🔓 Deletion protection disabled")
        print("   ├─ 🔌 SCSI interface")
        print("   └─ 🏷️  Added cost optimization labels")
        
        return self
        
    def _optimize_for_performance(self):
        """Optimize configuration for performance"""
        print("🏗️  Applying Cross-Cloud Magic: Performance Optimization")
        
        # Use SSD or extreme disk for performance
        if self.size_gb >= 500:
            self.extreme_disk().high_iops().max_throughput()
        else:
            self.ssd_disk()
            
        # Use NVMe interface for best performance
        self.nvme_interface()
        
        # Disable auto-delete for important data
        self.auto_delete(False)
        self.deletion_protection()
        
        # Add performance labels
        self.labels({
            "optimization": "performance",
            "disk_tier": "high_performance",
            "interface": "nvme"
        })
        
        print("   ├─ 🚀 High-performance disk type")
        print("   ├─ 🔌 NVMe interface")
        print("   ├─ 🔒 Deletion protection enabled")
        print("   └─ 🏷️  Added performance optimization labels")
        
        return self
        
    def _optimize_for_security(self):
        """Optimize configuration for security"""
        print("🏗️  Applying Cross-Cloud Magic: Security Optimization")
        
        # Enable deletion protection
        self.deletion_protection()
        
        # Disable auto-delete to prevent accidental data loss
        self.auto_delete(False)
        
        # Enable confidential compute if available
        self.confidential_compute()
        
        # Add security labels
        self.labels({
            "optimization": "security",
            "deletion_protection": "enabled",
            "confidential": "enabled"
        })
        
        print("   ├─ 🔒 Deletion protection enabled")
        print("   ├─ 🗑️  Auto-delete disabled")
        print("   ├─ 🛡️  Confidential compute enabled")
        print("   └─ 🏷️  Added security optimization labels")
        
        return self
        
    def _optimize_for_user_experience(self):
        """Optimize configuration for user experience"""
        print("🏗️  Applying Cross-Cloud Magic: User Experience Optimization")
        
        # Use balanced disk for good UX balance
        self.balanced_disk()
        
        # Use NVMe for better responsiveness
        self.nvme_interface()
        
        # Enable deletion protection for important data
        self.deletion_protection()
        
        # Disable auto-delete to prevent data loss
        self.auto_delete(False)
        
        # Add UX labels
        self.labels({
            "optimization": "user_experience",
            "disk_tier": "balanced",
            "responsiveness": "optimized"
        })
        
        print("   ├─ ⚖️  Balanced disk type")
        print("   ├─ 🔌 NVMe interface for responsiveness")
        print("   ├─ 🔒 Deletion protection enabled")
        print("   └─ 🏷️  Added UX optimization labels")
        
        return self
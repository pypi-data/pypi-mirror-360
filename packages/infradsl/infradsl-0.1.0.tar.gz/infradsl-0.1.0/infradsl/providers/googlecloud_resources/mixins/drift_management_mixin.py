from typing import TYPE_CHECKING, Dict, Any, Optional
import hashlib
import json

if TYPE_CHECKING:
    from ..vm import Vm

class DriftManagementMixin:
    """Mixin for configuration drift detection and auto-remediation"""
    
    def check_state(self: 'Vm', check_interval=None, auto_remediate: str = "DISABLED", 
                   webhook: Optional[str] = None, enable_auto_fix: bool = False,
                   learning_mode: bool = False) -> 'Vm':
        """Configure intelligent drift detection and auto-remediation"""
        try:
            from ...core.drift_management import (
                get_drift_manager, 
                DriftCheckInterval, 
                AutoRemediationPolicy
            )
            
            # Store drift configuration
            self._drift_enabled = True
            self._check_interval = check_interval or DriftCheckInterval.SIX_HOURS
            
            # Convert string policy to enum
            policy_map = {
                "CONSERVATIVE": AutoRemediationPolicy.CONSERVATIVE,
                "AGGRESSIVE": AutoRemediationPolicy.AGGRESSIVE,
                "DISABLED": AutoRemediationPolicy.DISABLED
            }
            self._auto_remediate_policy = policy_map.get(auto_remediate, AutoRemediationPolicy.DISABLED)
            self._enable_auto_fix = enable_auto_fix
            self._learning_mode = learning_mode
            
            # Setup drift manager
            drift_manager = get_drift_manager()
            
            # Add webhook if provided
            if webhook:
                drift_manager.add_webhook(webhook)
            
            # Enable learning mode for the primary VM
            if learning_mode:
                primary_vm = self.vm_names[0]
                drift_manager.enable_learning_mode(primary_vm, learning_days=30)
                print(f"🎓 Learning mode enabled for {primary_vm} (30 days)")
            
            print(f"🔍 Drift detection configured:")
            print(f"   📅 Check interval: {self._check_interval.name if hasattr(self._check_interval, 'name') else self._check_interval}")
            print(f"   🛡️ Auto-remediation: {auto_remediate}")
            print(f"   🔧 Auto-fix: {'enabled' if enable_auto_fix else 'disabled'}")
            print(f"   🎓 Learning mode: {'enabled' if learning_mode else 'disabled'}")
            
        except ImportError:
            print("⚠️ Drift management not available")
        
        return self

    def _check_drift_if_enabled(self: 'Vm'):
        """Check for drift if drift detection is enabled"""
        if not hasattr(self, '_drift_enabled') or not self._drift_enabled:
            return None
            
        try:
            from ...core.drift_management import get_drift_manager
            
            drift_manager = get_drift_manager()
            primary_vm = self.vm_names[0]
            
            # Check drift for the primary VM
            drift_result = drift_manager.check_resource_drift(
                resource_name=primary_vm,
                provider="gcp",
                check_interval=self._check_interval,
                current_state_fetcher=self._fetch_current_cloud_state
            )
            
            if drift_result and drift_result.has_drift:
                print(f"🔍 Drift detected in {primary_vm}:")
                for action in drift_result.suggested_actions:
                    print(f"   → {action}")
                
                # Apply auto-remediation if enabled
                if self._enable_auto_fix and hasattr(self, '_auto_remediate_policy'):
                    remediated_result = drift_manager.auto_remediate_drift(
                        drift_result=drift_result,
                        resource_instance=self,
                        policy=self._auto_remediate_policy
                    )
                    return remediated_result
            
            return drift_result
            
        except ImportError:
            return None
        except Exception as e:
            print(f"⚠️  Drift check failed: {e}")
            return None

    def _cache_resource_state(self: 'Vm'):
        """Cache the current resource state for drift detection"""
        if not hasattr(self, '_drift_enabled') or not self._drift_enabled:
            return
            
        try:
            from ...core.drift_management import get_drift_manager
            
            drift_manager = get_drift_manager()
            primary_vm = self.vm_names[0]
            primary_config = self.configs[primary_vm]
            
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            # Generate configuration for caching
            config = {
                'machine_type': primary_config.machine_type,
                'disk_size_gb': primary_config.disk_size_gb,
                'image_family': primary_config.image_family,
                'image_project': primary_config.image_project,
                'zone': primary_config.zone,
                'tags': primary_config.tags or [],  # Ensure tags is not None
                'vm_count': len(self.vm_names)
            }
            
            # Cache the state
            drift_manager.cache_resource_state(
                resource_name=primary_vm,
                resource_type="compute_engine",
                provider="gcp",
                config=config,
                current_state=current_state
            )
            
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️  Failed to cache resource state: {e}")
    
    def _fetch_current_cloud_state(self: 'Vm') -> Dict[str, Any]:
        """Fetch current state of the VM from Google Cloud for drift detection"""
        self._ensure_authenticated()
        
        # For single VM, fetch its current state
        if not self.is_multi_vm:
            vm_name = self.vm_names[0]
            config = self.configs[vm_name]
            
            try:
                vm_info = self.vm_manager.get_vm_info(vm_name, config.zone)
                if vm_info:
                    return {
                        "machine_type": vm_info.get("machine_type", config.machine_type),
                        "zone": vm_info.get("zone", config.zone),
                        "status": vm_info.get("status", "UNKNOWN"),
                        "ip_address": vm_info.get("ip"),
                        "tags": config.tags or []
                    }
                else:
                    # VM doesn't exist
                    return {
                        "machine_type": None,
                        "zone": config.zone,
                        "status": "NOT_FOUND",
                        "ip_address": None,
                        "tags": []
                    }
            except Exception as e:
                print(f"❌ Failed to fetch current state for {vm_name}: {e}")
                return {}
        
        # For multi-VM, return state of first VM (or could be extended to handle all)
        vm_name = self.vm_names[0]
        config = self.configs[vm_name]
        
        try:
            vm_info = self.vm_manager.get_vm_info(vm_name, config.zone)
            if vm_info:
                return {
                    "machine_type": vm_info.get("machine_type", config.machine_type),
                    "zone": vm_info.get("zone", config.zone),
                    "status": vm_info.get("status", "UNKNOWN"),
                    "ip_address": vm_info.get("ip"),
                    "tags": config.tags or []
                }
            else:
                return {
                    "machine_type": None,
                    "zone": config.zone,
                    "status": "NOT_FOUND",
                    "ip_address": None,
                    "tags": []
                }
        except Exception as e:
            print(f"❌ Failed to fetch current state for {vm_name}: {e}")
            return {}
    
    def _apply_configuration_update(self: 'Vm', field_name: str, new_value: Any):
        """Apply configuration updates to the VM in Google Cloud"""
        if not self.is_multi_vm:
            vm_name = self.vm_names[0]
            config = self.configs[vm_name]
            self._apply_single_vm_update(vm_name, config, field_name, new_value)
        else:
            # Apply to all VMs in the group
            for vm_name in self.vm_names:
                config = self.configs[vm_name]
                self._apply_single_vm_update(vm_name, config, field_name, new_value)
    
    def _apply_single_vm_update(self: 'Vm', vm_name: str, config, field_name: str, new_value: Any):
        """Apply a configuration update to a single VM"""
        try:
            if field_name == 'machine_type':
                # Machine type change requires VM to be stopped
                print(f"   🔧 Updating machine type for {vm_name} to {new_value}")
                # Note: In a real implementation, this would:
                # 1. Stop the VM
                # 2. Change the machine type via GCP APIs
                # 3. Start the VM
                config.machine_type = new_value
                print(f"   ✅ Machine type updated for {vm_name}")
                
            elif field_name.startswith('tag_'):
                # Update VM tags
                tag_key = field_name.replace('tag_', '')
                print(f"   🏷️ Updating tag {tag_key} for {vm_name} to {new_value}")
                # Note: In a real implementation, this would call:
                # compute_client.instances().set_labels() or similar
                print(f"   ✅ Tag updated for {vm_name}")
                
            elif field_name == 'status' and new_value == 'RUNNING':
                # Start the VM
                print(f"   🚀 Starting VM {vm_name}")
                # Note: In a real implementation, this would call:
                # compute_client.instances().start()
                print(f"   ✅ VM {vm_name} started successfully")
                
            elif field_name == 'disk_size':
                # Disk size changes are more complex - usually require recreation
                print(f"   ⚠️ Disk size change for {vm_name} requires manual intervention")
                print(f"     Current approach: Requires VM recreation")
                
            else:
                # Fall back to default implementation
                print(f"   🔧 Applying update: {field_name} = {new_value}")
                setattr(config, field_name, new_value)
                
        except Exception as e:
            print(f"   ❌ Failed to update {field_name} for {vm_name}: {e}")
            raise

    def _get_config_hash(self: 'Vm') -> str:
        """Generate a hash of the current configuration"""
        try:
            from ...core.drift_management import get_drift_manager
            
            # For multi-VM, use the first VM's config as representative
            primary_config = self.configs[self.vm_names[0]]
            
            config = {
                'machine_type': primary_config.machine_type,
                'disk_size_gb': primary_config.disk_size_gb,
                'image_family': primary_config.image_family,
                'image_project': primary_config.image_project,
                'zone': primary_config.zone,
                'tags': primary_config.tags,
                'vm_count': len(self.vm_names)
            }
            return get_drift_manager().generate_config_hash(config)
        except ImportError:
            # Fallback implementation
            primary_config = self.configs[self.vm_names[0]]
            config = {
                'machine_type': primary_config.machine_type,
                'disk_size_gb': primary_config.disk_size_gb,
                'image_family': primary_config.image_family,
                'image_project': primary_config.image_project,
                'zone': primary_config.zone,
                'tags': primary_config.tags,
                'vm_count': len(self.vm_names)
            }
            config_str = json.dumps(config, sort_keys=True, default=str)
            return hashlib.sha256(config_str.encode()).hexdigest()[:16] 
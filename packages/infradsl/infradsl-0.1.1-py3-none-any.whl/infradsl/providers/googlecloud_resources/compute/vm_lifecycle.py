"""
Google Compute Engine VM Lifecycle Mixin

Lifecycle operations for Google Compute Engine VMs.
Provides create, destroy, and preview operations with smart state management.
"""

import hashlib
import json
from typing import Dict, Any, List, Optional, Union
from ...googlecloud_managers.firewall_manager import FirewallRule


class VmLifecycleMixin:
    """
    Mixin for Google Compute Engine VM lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update VMs
    - destroy(): Clean up VMs and associated resources
    - Smart state management and drift detection
    - Firewall rule management
    - Load balancer integration
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()
        
        # Discover existing VMs
        existing_vms = self._discover_existing_vms()
        
        # Categorize VMs
        vms_to_create = []
        vms_to_keep = []
        vms_to_update = []
        vms_to_remove = []
        
        # Check each configured VM
        for vm_name in self.vm_names:
            if vm_name in existing_vms:
                # VM exists - check if update needed
                existing_state = existing_vms[vm_name]
                config = self.configs[vm_name]
                
                # Check if configuration has changed
                needs_update = False
                update_reasons = []
                
                # Check machine type
                current_machine_type = existing_state.get("machine_type", "")
                if current_machine_type != config.machine_type:
                    needs_update = True
                    update_reasons.append(f"machine type: {current_machine_type} → {config.machine_type}")
                    
                # Check labels
                current_labels = existing_state.get("labels", {})
                desired_labels = config.labels.copy()
                desired_labels.update(self.vm_labels)
                if current_labels != desired_labels:
                    needs_update = True
                    update_reasons.append("labels")
                    
                if needs_update:
                    vms_to_update.append({
                        "name": vm_name,
                        "zone": config.zone,
                        "current_state": existing_state,
                        "update_reasons": update_reasons
                    })
                else:
                    vms_to_keep.append({
                        "name": vm_name,
                        "zone": config.zone,
                        "state": existing_state
                    })
            else:
                # VM doesn't exist - will create
                config = self.configs[vm_name]
                vms_to_create.append({
                    "name": vm_name,
                    "zone": config.zone,
                    "machine_type": config.machine_type,
                    "disk_size": config.disk_size_gb,
                    "image": f"{config.image_project}/{config.image_family}",
                    "network": config.network,
                    "external_ip": config.external_ip,
                    "services": [s.name for s in config.services],
                    "labels": {**config.labels, **self.vm_labels}
                })
                
        # Find VMs that exist but aren't in our configuration (orphaned)
        configured_names = set(self.vm_names)
        for existing_name, existing_state in existing_vms.items():
            if existing_name not in configured_names:
                # Check if it matches our naming pattern
                base_pattern = self._extract_base_pattern(self.vm_names[0])
                if base_pattern and existing_name.startswith(base_pattern):
                    vms_to_remove.append({
                        "name": existing_name,
                        "zone": existing_state.get("zone", "unknown"),
                        "reason": "Not in current configuration"
                    })
                    
        # Display preview
        print(f"\\n🖥️  Compute Engine VM Preview")
        
        # Show VMs to create
        if vms_to_create:
            print(f"╭─ 🖥️  VMs to CREATE: {len(vms_to_create)}")
            for vm in vms_to_create:
                print(f"├─ 🆕 {vm['name']}")
                print(f"│  ├─ 📍 Zone: {vm['zone']}")
                print(f"│  ├─ 🖥️  Type: {vm['machine_type']}")
                print(f"│  ├─ 💾 Disk: {vm['disk_size']}GB")
                print(f"│  ├─ 🖼️  Image: {vm['image']}")
                print(f"│  ├─ 🌐 Network: {vm['network']}")
                print(f"│  ├─ 🌍 External IP: {'✅ Yes' if vm['external_ip'] else '❌ No'}")
                
                if vm['services']:
                    print(f"│  ├─ 📦 Services: {', '.join(vm['services'])}")
                    
                if vm['labels']:
                    print(f"│  ├─ 🏷️  Labels: {len(vm['labels'])}")
                    for key, value in list(vm['labels'].items())[:3]:
                        print(f"│  │  ├─ {key}: {value}")
                    if len(vm['labels']) > 3:
                        print(f"│  │  └─ ... and {len(vm['labels']) - 3} more")
                        
                # Show cost estimate
                config = self.configs[vm['name']]
                machine_costs = {
                    "e2-micro": 6.13, "e2-small": 12.26, "e2-medium": 24.53,
                    "e2-standard-2": 48.92, "e2-standard-4": 97.84,
                    "e2-standard-8": 195.67, "n1-standard-1": 34.68,
                    "n1-standard-2": 69.35, "n1-standard-4": 138.70
                }
                monthly_cost = machine_costs.get(vm['machine_type'], 50.0)
                print(f"│  └─ 💰 Est. Cost: ${monthly_cost:.2f}/month")
            print(f"╰─")
            
        # Show VMs to keep
        if vms_to_keep:
            print(f"\\n╭─ ✅ VMs to KEEP: {len(vms_to_keep)}")
            for vm in vms_to_keep:
                print(f"├─ ✅ {vm['name']}")
                print(f"│  ├─ 📍 Zone: {vm['zone']}")
                print(f"│  ├─ 🟢 Status: {vm['state'].get('status', 'UNKNOWN')}")
                print(f"│  └─ 📅 Created: {vm['state'].get('creation_timestamp', 'unknown')[:10]}")
            print(f"╰─")
            
        # Show VMs to update
        if vms_to_update:
            print(f"\\n╭─ 🔄 VMs to UPDATE: {len(vms_to_update)}")
            for vm in vms_to_update:
                print(f"├─ 🔄 {vm['name']}")
                print(f"│  ├─ 📍 Zone: {vm['zone']}")
                print(f"│  └─ 📝 Updates: {', '.join(vm['update_reasons'])}")
            print(f"╰─")
            
        # Show VMs to remove
        if vms_to_remove:
            print(f"\\n╭─ 🗑️  VMs to REMOVE: {len(vms_to_remove)}")
            for vm in vms_to_remove:
                print(f"├─ 🗑️  {vm['name']}")
                print(f"│  ├─ 📍 Zone: {vm['zone']}")
                print(f"│  └─ 📝 Reason: {vm['reason']}")
            print(f"╰─")
            
        # Firewall rules preview
        if self.firewall_rules:
            print(f"\\n🔥 Firewall Rules:")
            for rule in self.firewall_rules[:5]:
                print(f"   ├─ {rule.name}: {rule.direction} {rule.protocol}:{','.join(map(str, rule.ports))}")
            if len(self.firewall_rules) > 5:
                print(f"   └─ ... and {len(self.firewall_rules) - 5} more rules")
                
        # Cost summary
        total_monthly_cost = self._estimate_vm_cost()
        print(f"\\n💰 Cost Summary:")
        print(f"   ├─ VMs: {len(self.vm_names)}")
        print(f"   ├─ Total vCPUs: {sum(self._extract_cpu_from_machine_type(c.machine_type) for c in self.configs.values())}")
        print(f"   ├─ Total RAM: {sum(self._extract_ram_from_machine_type(c.machine_type) for c in self.configs.values())}GB")
        print(f"   ├─ Total Disk: {sum(c.disk_size_gb for c in self.configs.values())}GB")
        print(f"   └─ Estimated Cost: ${total_monthly_cost:.2f}/month")
        
        return {
            "resource_type": "compute_vm",
            "name": self.name,
            "vms_to_create": vms_to_create,
            "vms_to_keep": vms_to_keep,
            "vms_to_update": vms_to_update,
            "vms_to_remove": vms_to_remove,
            "existing_vms": existing_vms,
            "firewall_rules": len(self.firewall_rules),
            "total_vms": len(self.vm_names),
            "estimated_monthly_cost": f"${total_monthly_cost:.2f}"
        }
        
    def create(self) -> Dict[str, Any]:
        """Create or update VMs"""
        self._ensure_authenticated()
        
        print(f"🚀 Creating Compute Engine VMs")
        
        results = {
            "success": True,
            "created": [],
            "updated": [],
            "failed": [],
            "firewall_rules": []
        }
        
        # Get configuration hash for tracking changes
        config_hash = self._get_config_hash()
        
        # Create each VM
        for vm_name in self.vm_names:
            config = self.configs[vm_name]
            
            try:
                print(f"\\n📦 Processing VM: {vm_name}")
                print(f"   ├─ 📍 Zone: {config.zone}")
                print(f"   ├─ 🖥️  Type: {config.machine_type}")
                print(f"   ├─ 💾 Disk: {config.disk_size_gb}GB")
                
                # Check if VM exists
                existing_state = self._fetch_current_vm_state(vm_name)
                
                if existing_state.get("exists"):
                    print(f"   ├─ ✅ VM already exists")
                    # Update VM if needed
                    # Note: Full VM updates require stop/start, so we'll just update metadata/labels
                    results["updated"].append({
                        "name": vm_name,
                        "zone": config.zone,
                        "status": "exists"
                    })
                else:
                    # Create VM
                    print(f"   ├─ 🔨 Creating VM...")
                    
                    # Prepare VM configuration for manager
                    vm_result = self.vm_manager.create_vm(config)
                    
                    if vm_result:
                        print(f"   ├─ ✅ VM created successfully")
                        results["created"].append({
                            "name": vm_name,
                            "zone": config.zone,
                            "machine_type": config.machine_type,
                            "external_ip": vm_result.get("external_ip")
                        })
                        
                        # Update firewall rules if needed
                        self._smart_update_firewall_rules_for_vm(vm_name, config)
                    else:
                        raise Exception("VM creation failed")
                        
            except Exception as e:
                print(f"   └─ ❌ Failed: {str(e)}")
                results["failed"].append({
                    "name": vm_name,
                    "error": str(e)
                })
                results["success"] = False
                
        # Apply firewall rules
        if self.firewall_rules:
            print(f"\\n🔥 Applying firewall rules...")
            for rule in self.firewall_rules:
                try:
                    self.firewall_manager.create_or_update_rule(rule)
                    print(f"   ✅ Rule '{rule.name}' applied")
                    results["firewall_rules"].append(rule.name)
                except Exception as e:
                    print(f"   ❌ Rule '{rule.name}' failed: {str(e)}")
                    
        # Show summary
        print(f"\\n📊 Creation Summary:")
        print(f"   ├─ ✅ Created: {len(results['created'])}")
        print(f"   ├─ 🔄 Updated: {len(results['updated'])}")
        print(f"   ├─ ❌ Failed: {len(results['failed'])}")
        print(f"   └─ 🔥 Firewall Rules: {len(results['firewall_rules'])}")
        
        # Update state tracking
        self.deployment_status = "deployed" if results["success"] else "failed"
        self.estimated_monthly_cost = f"${self._estimate_vm_cost():.2f}/month"
        
        # Store config hash for drift detection
        if results["success"]:
            for vm_name in self.vm_names:
                self.vm_exists[vm_name] = True
                self.vm_created[vm_name] = True
                
        return results
        
    def destroy(self) -> Dict[str, Any]:
        """Destroy VMs and associated resources"""
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying Compute Engine VMs")
        
        results = {
            "success": True,
            "destroyed": [],
            "failed": [],
            "firewall_rules_removed": []
        }
        
        # Destroy each VM
        for vm_name in self.vm_names:
            config = self.configs[vm_name]
            
            try:
                print(f"\\n🗑️  Processing VM: {vm_name}")
                print(f"   ├─ 📍 Zone: {config.zone}")
                
                # Check if VM exists
                existing_state = self._fetch_current_vm_state(vm_name)
                
                if existing_state.get("exists"):
                    print(f"   ├─ 🔨 Deleting VM...")
                    
                    # Delete VM
                    self.vm_manager.delete_vm(vm_name, config.zone)
                    
                    print(f"   ├─ ✅ VM deleted successfully")
                    results["destroyed"].append({
                        "name": vm_name,
                        "zone": config.zone
                    })
                else:
                    print(f"   ├─ ℹ️  VM doesn't exist, skipping")
                    
            except Exception as e:
                print(f"   └─ ❌ Failed: {str(e)}")
                results["failed"].append({
                    "name": vm_name,
                    "error": str(e)
                })
                results["success"] = False
                
        # Remove firewall rules
        if self.firewall_rules:
            print(f"\\n🔥 Removing firewall rules...")
            for rule in self.firewall_rules:
                try:
                    self.firewall_manager.delete_rule(rule.name)
                    print(f"   ✅ Rule '{rule.name}' removed")
                    results["firewall_rules_removed"].append(rule.name)
                except Exception as e:
                    print(f"   ⚠️  Rule '{rule.name}' removal failed: {str(e)}")
                    
        # Show summary
        print(f"\\n📊 Destruction Summary:")
        print(f"   ├─ ✅ Destroyed: {len(results['destroyed'])}")
        print(f"   ├─ ❌ Failed: {len(results['failed'])}")
        print(f"   └─ 🔥 Rules Removed: {len(results['firewall_rules_removed'])}")
        
        # Update state tracking
        if results["success"]:
            for vm_name in self.vm_names:
                self.vm_exists[vm_name] = False
                self.vm_created[vm_name] = False
            self.deployment_status = "destroyed"
            
        return results
        
    def _get_config_hash(self) -> str:
        """Generate hash of current configuration for drift detection"""
        config_dict = {
            "vms": {}
        }
        
        for vm_name, config in self.configs.items():
            config_dict["vms"][vm_name] = {
                "machine_type": config.machine_type,
                "zone": config.zone,
                "disk_size_gb": config.disk_size_gb,
                "image_family": config.image_family,
                "image_project": config.image_project,
                "network": config.network,
                "subnetwork": config.subnetwork,
                "tags": sorted(config.tags),
                "labels": config.labels,
                "metadata": config.metadata,
                "services": [{"name": s.name, "vars": s.variables} for s in config.services]
            }
            
        config_json = json.dumps(config_dict, sort_keys=True)
        return hashlib.sha256(config_json.encode()).hexdigest()
        
    def _smart_update_firewall_rules_for_vm(self, vm_name: str, config: Any):
        """Intelligently update firewall rules for a VM"""
        # Skip if no special tags
        if not config.tags:
            return
            
        # Create firewall rules based on tags
        if "http-server" in config.tags:
            http_rule = FirewallRule(
                name=f"{vm_name}-allow-http",
                direction="INGRESS",
                priority=1000,
                source_ranges=["0.0.0.0/0"],
                target_tags=["http-server"],
                protocol="tcp",
                ports=[80]
            )
            if http_rule not in self.firewall_rules:
                self.firewall_rules.append(http_rule)
                
        if "https-server" in config.tags:
            https_rule = FirewallRule(
                name=f"{vm_name}-allow-https",
                direction="INGRESS",
                priority=1000,
                source_ranges=["0.0.0.0/0"],
                target_tags=["https-server"],
                protocol="tcp",
                ports=[443]
            )
            if https_rule not in self.firewall_rules:
                self.firewall_rules.append(https_rule)
                
        if "ssh-server" in config.tags:
            ssh_rule = FirewallRule(
                name=f"{vm_name}-allow-ssh",
                direction="INGRESS",
                priority=1000,
                source_ranges=["0.0.0.0/0"],
                target_tags=["ssh-server"],
                protocol="tcp",
                ports=[22]
            )
            if ssh_rule not in self.firewall_rules:
                self.firewall_rules.append(ssh_rule)
                
    def _extract_base_pattern(self, vm_name: str) -> str:
        """Extract base pattern from VM name for finding related VMs"""
        # Remove common suffixes
        suffixes = ["-1", "-2", "-3", "-01", "-02", "-03", "-a", "-b", "-c"]
        for suffix in suffixes:
            if vm_name.endswith(suffix):
                return vm_name[:-len(suffix)]
                
        # Remove number at end
        import re
        match = re.match(r"^(.+?)[-_]?\d+$", vm_name)
        if match:
            return match.group(1)
            
        return vm_name
        
    # Cross-Cloud Magic Integration
    def apply_cross_cloud_recommendations(self, recommendations: Dict[str, Any]):
        """Apply Cross-Cloud Magic recommendations to VM configuration"""
        if not recommendations:
            return
            
        provider_rec = recommendations.get("primary_recommendation", {})
        
        # Apply region recommendation
        if provider_rec.get("region"):
            # Map Cross-Cloud region to GCP zone
            region = provider_rec["region"]
            zone_mapping = {
                "us-east": "us-east1-b",
                "us-west": "us-west1-a",
                "europe": "europe-west1-b",
                "asia": "asia-northeast1-a"
            }
            zone = zone_mapping.get(region, "us-central1-a")
            self.zone(zone)
            
        # Apply instance type recommendation
        if provider_rec.get("instance_type"):
            self.machine_type(provider_rec["instance_type"])
            
        # Apply optimization flags
        optimizations = recommendations.get("optimizations", {})
        if optimizations.get("use_spot_instances"):
            for config in self.configs.values():
                config.preemptible = True
                
        if optimizations.get("enable_auto_scaling"):
            # Note: Auto-scaling would be handled by instance groups
            self.label("auto-scaling", "recommended")
            
        print(f"   ✅ Applied Cross-Cloud Magic recommendations")
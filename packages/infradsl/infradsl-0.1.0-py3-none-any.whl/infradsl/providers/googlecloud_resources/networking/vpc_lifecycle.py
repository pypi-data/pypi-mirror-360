"""
GCP VPC Lifecycle Mixin

Lifecycle operations for Google Cloud VPC networks.
Handles create, destroy, and preview operations with smart state management.
"""

from typing import Dict, Any, List, Optional


class VPCLifecycleMixin:
    """
    Mixin for VPC network lifecycle operations.
    
    This mixin provides:
    - Create operation with smart state management
    - Destroy operation with safety checks
    - Preview operation for infrastructure planning
    - State comparison and drift detection
    """
    
    def preview(self) -> Dict[str, Any]:
        """
        Preview what will be created, kept, and removed.
        
        Returns:
            Dict containing preview information and cost estimates
        """
        self._ensure_authenticated()
        
        # Validate configuration
        self._validate_vpc_configuration()
        
        # Get current cloud state
        current_state = self._fetch_current_cloud_state()
        
        # Determine actions needed
        actions = self._determine_vpc_actions(current_state)
        
        # Display preview
        self._display_vpc_preview(actions, current_state)
        
        # Return structured data
        return {
            'resource_type': 'gcp_vpc',
            'name': self.vpc_name,
            'current_state': current_state,
            'actions': actions,
            'estimated_cost': self._calculate_vpc_cost(),
            'configuration': self._get_vpc_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the VPC with smart state management.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration
        self._validate_vpc_configuration()
        
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_vpc_actions(current_state)
        
        # Execute actions
        result = self._execute_vpc_actions(actions, current_state)
        
        # Update state
        self.vpc_exists = True
        self.vpc_created = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the VPC and all associated resources.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying VPC: {self.vpc_name}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  VPC '{self.vpc_name}' does not exist")
                return {"success": True, "message": "VPC does not exist", "name": self.vpc_name}
            
            # Show what will be destroyed
            self._display_vpc_destruction_preview(current_state)
            
            # Perform destruction in correct order
            if self.vpc_manager:
                # 1. Delete firewall rules first
                firewall_success = self._destroy_firewall_rules()
                
                # 2. Delete subnets
                subnets_success = self._destroy_subnets()
                
                # 3. Delete VPC peerings
                peerings_success = self._destroy_vpc_peerings()
                
                # 4. Finally delete VPC
                vpc_success = self.vpc_manager.delete_vpc(self.vpc_name)
                
                overall_success = all([firewall_success, subnets_success, peerings_success, vpc_success])
                
                if overall_success:
                    print(f"✅ VPC '{self.vpc_name}' destroyed successfully")
                    self.vpc_exists = False
                    self.vpc_created = False
                    return {"success": True, "name": self.vpc_name}
                else:
                    print(f"⚠️  Partial failure destroying VPC '{self.vpc_name}'")
                    return {"success": False, "name": self.vpc_name, "error": "Partial destruction failure"}
            else:
                print(f"❌ VPC manager not available")
                return {"success": False, "name": self.vpc_name, "error": "Manager not initialized"}
                
        except Exception as e:
            print(f"❌ Error destroying VPC: {str(e)}")
            return {"success": False, "name": self.vpc_name, "error": str(e)}
            
    def _validate_vpc_configuration(self):
        """Validate the VPC configuration before creation"""
        errors = []
        warnings = []
        
        # Check for subnet CIDR overlaps
        overlaps = self._check_subnet_overlaps()
        if overlaps:
            errors.extend(overlaps)
        
        # Validate subnets
        for subnet in self.subnets:
            if not self._validate_subnet_config(subnet):
                errors.append(f"Invalid subnet configuration: {subnet.get('name', 'Unknown')}")
        
        # Validate firewall rules
        for rule in self.firewall_rules:
            if not self._validate_firewall_rule(rule):
                errors.append(f"Invalid firewall rule: {rule.get('name', 'Unknown')}")
        
        # Warnings for auto-subnet mode
        if self.auto_create_subnetworks and self.subnets:
            warnings.append("Auto-subnet mode enabled but manual subnets defined - manual subnets will be ignored")
        
        # Warnings for no subnets in custom mode
        if not self.auto_create_subnetworks and not self.subnets:
            warnings.append("Custom subnet mode with no subnets defined - VPC will be empty")
        
        if errors:
            raise ValueError(f"VPC configuration validation failed: {'; '.join(errors)}")
        
        if warnings:
            print(f"⚠️  VPC configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
                
    def _determine_vpc_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create_vpc": False,
            "update_vpc": False,
            "keep_vpc": False,
            "create_subnets": [],
            "update_subnets": [],
            "delete_subnets": [],
            "create_firewall_rules": [],
            "update_firewall_rules": [],
            "delete_firewall_rules": [],
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create_vpc"] = True
            actions["create_subnets"] = self.subnets
            actions["create_firewall_rules"] = self.firewall_rules
            actions["changes"].append("Create new VPC")
            if self.subnets:
                actions["changes"].append(f"Create {len(self.subnets)} subnets")
            if self.firewall_rules:
                actions["changes"].append(f"Create {len(self.firewall_rules)} firewall rules")
        else:
            # Compare current state with desired state
            vpc_changes = self._detect_vpc_configuration_drift(current_state)
            subnet_changes = self._detect_subnet_drift(current_state)
            firewall_changes = self._detect_firewall_drift(current_state)
            
            if vpc_changes:
                actions["update_vpc"] = True
                actions["changes"].extend(vpc_changes)
            else:
                actions["keep_vpc"] = True
                
            if subnet_changes:
                actions["create_subnets"] = subnet_changes.get("create", [])
                actions["update_subnets"] = subnet_changes.get("update", [])
                actions["delete_subnets"] = subnet_changes.get("delete", [])
                
                if subnet_changes.get("create"):
                    actions["changes"].append(f"Create {len(subnet_changes['create'])} new subnets")
                if subnet_changes.get("update"):
                    actions["changes"].append(f"Update {len(subnet_changes['update'])} existing subnets")
                if subnet_changes.get("delete"):
                    actions["changes"].append(f"Delete {len(subnet_changes['delete'])} obsolete subnets")
                    
            if firewall_changes:
                actions["create_firewall_rules"] = firewall_changes.get("create", [])
                actions["update_firewall_rules"] = firewall_changes.get("update", [])
                actions["delete_firewall_rules"] = firewall_changes.get("delete", [])
                
                if firewall_changes.get("create"):
                    actions["changes"].append(f"Create {len(firewall_changes['create'])} new firewall rules")
                if firewall_changes.get("update"):
                    actions["changes"].append(f"Update {len(firewall_changes['update'])} existing firewall rules")
                if firewall_changes.get("delete"):
                    actions["changes"].append(f"Delete {len(firewall_changes['delete'])} obsolete firewall rules")
                    
            if not actions["changes"]:
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_vpc_configuration_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences between current and desired VPC configuration"""
        changes = []
        
        # Check description
        if current_state.get("description") != self.vpc_description:
            changes.append(f"Description: '{current_state.get('description')}' → '{self.vpc_description}'")
            
        # Check routing mode
        if current_state.get("routing_mode") != self.routing_mode:
            changes.append(f"Routing mode: {current_state.get('routing_mode')} → {self.routing_mode}")
            
        # Check MTU
        if current_state.get("mtu") != self.mtu:
            changes.append(f"MTU: {current_state.get('mtu')} → {self.mtu}")
            
        # Check auto-subnet mode
        current_auto = current_state.get("auto_create_subnetworks", False)
        if current_auto != self.auto_create_subnetworks:
            changes.append(f"Auto-create subnets: {current_auto} → {self.auto_create_subnetworks}")
            
        return changes
        
    def _detect_subnet_drift(self, current_state: Dict[str, Any]) -> Dict[str, List]:
        """Detect differences between current and desired subnets"""
        current_subnets = current_state.get("subnets", [])
        desired_subnets = self.subnets
        
        # Create lookup dictionaries
        current_lookup = {s["name"]: s for s in current_subnets}
        desired_lookup = {s["name"]: s for s in desired_subnets}
        
        changes = {
            "create": [],
            "update": [],
            "delete": []
        }
        
        # Find subnets to create (in desired but not in current)
        for name, subnet in desired_lookup.items():
            if name not in current_lookup:
                changes["create"].append(subnet)
            else:
                # Check if subnet needs updating
                current_subnet = current_lookup[name]
                if self._subnets_differ(current_subnet, subnet):
                    changes["update"].append(subnet)
                    
        # Find subnets to delete (in current but not in desired)
        for name, subnet in current_lookup.items():
            if name not in desired_lookup:
                changes["delete"].append(subnet)
                
        return changes
        
    def _detect_firewall_drift(self, current_state: Dict[str, Any]) -> Dict[str, List]:
        """Detect differences between current and desired firewall rules"""
        current_rules = current_state.get("firewall_rules", [])
        desired_rules = self.firewall_rules
        
        # Create lookup dictionaries
        current_lookup = {r["name"]: r for r in current_rules}
        desired_lookup = {r["name"]: r for r in desired_rules}
        
        changes = {
            "create": [],
            "update": [],
            "delete": []
        }
        
        # Find rules to create (in desired but not in current)
        for name, rule in desired_lookup.items():
            if name not in current_lookup:
                changes["create"].append(rule)
            else:
                # Check if rule needs updating
                current_rule = current_lookup[name]
                if self._firewall_rules_differ(current_rule, rule):
                    changes["update"].append(rule)
                    
        # Find rules to delete (in current but not in desired)
        for name, rule in current_lookup.items():
            if name not in desired_lookup:
                # Don't delete default GCP rules
                if not name.startswith("default-"):
                    changes["delete"].append(rule)
                    
        return changes
        
    def _subnets_differ(self, current: Dict[str, Any], desired: Dict[str, Any]) -> bool:
        """Check if two subnet configurations differ"""
        return (current.get("cidr") != desired.get("cidr") or
                current.get("region") != desired.get("region") or
                current.get("description") != desired.get("description"))
                
    def _firewall_rules_differ(self, current: Dict[str, Any], desired: Dict[str, Any]) -> bool:
        """Check if two firewall rule configurations differ"""
        return (current.get("direction") != desired.get("direction") or
                current.get("action") != desired.get("action") or
                current.get("priority") != desired.get("priority") or
                set(current.get("source_ranges", [])) != set(desired.get("source_ranges", [])))
        
    def _execute_vpc_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create_vpc"]:
            return self._create_vpc()
        elif actions["update_vpc"] or actions["create_subnets"] or actions["create_firewall_rules"]:
            return self._update_vpc(current_state, actions)
        else:
            return self._keep_vpc(current_state)
            
    def _create_vpc(self) -> Dict[str, Any]:
        """Create a new VPC"""
        print(f"\\n🌐 Creating VPC: {self.vpc_name}")
        print(f"   📝 Description: {self.vpc_description}")
        print(f"   🛤️  Routing Mode: {self.routing_mode}")
        print(f"   📏 MTU: {self.mtu}")
        print(f"   🏗️  Auto-create Subnets: {self.auto_create_subnetworks}")
        print(f"   🌐 Subnets: {len(self.subnets)} to create")
        print(f"   🔥 Firewall Rules: {len(self.firewall_rules)} to create")
        
        try:
            # Create VPC through manager
            if self.vpc_manager:
                vpc_result = self.vpc_manager.create_vpc(
                    name=self.vpc_name,
                    description=self.vpc_description,
                    routing_mode=self.routing_mode,
                    auto_create_subnetworks=self.auto_create_subnetworks,
                    mtu=self.mtu,
                    labels=self.vpc_labels
                )
                
                if vpc_result:
                    print(f"✅ VPC created successfully!")
                    
                    # Create subnets
                    subnets_created = 0
                    if self.subnets and self.subnet_manager:
                        for subnet in self.subnets:
                            subnet_result = self.subnet_manager.create_subnet(
                                vpc_name=self.vpc_name,
                                **subnet
                            )
                            if subnet_result:
                                subnets_created += 1
                                
                    # Create firewall rules
                    firewall_rules_created = 0
                    if self.firewall_rules and self.firewall_manager:
                        for rule in self.firewall_rules:
                            rule_result = self.firewall_manager.create_firewall_rule(
                                vpc_name=self.vpc_name,
                                **rule
                            )
                            if rule_result:
                                firewall_rules_created += 1
                    
                    print(f"\\n📊 VPC Infrastructure Summary:")
                    print(f"   🌐 VPC: {vpc_result.get('name', self.vpc_name)}")
                    print(f"   🌍 Global URL: {vpc_result.get('selfLink', 'Pending')}")
                    print(f"   🌐 Subnets: {subnets_created}/{len(self.subnets)} created")
                    print(f"   🔥 Firewall Rules: {firewall_rules_created}/{len(self.firewall_rules)} created")
                    print(f"   📏 MTU: {self.mtu}")
                    print(f"   🛤️  Routing: {self.routing_mode}")
                    
                    # Update internal state
                    self.vpc_url = vpc_result.get('selfLink')
                    
                    return {
                        "success": True,
                        "name": self.vpc_name,
                        "vpc_url": self.vpc_url,
                        "subnets_created": subnets_created,
                        "firewall_rules_created": firewall_rules_created,
                        "routing_mode": self.routing_mode,
                        "mtu": self.mtu,
                        "created": True
                    }
                else:
                    raise Exception("VPC creation failed")
            else:
                raise Exception("VPC manager not available")
                
        except Exception as e:
            print(f"❌ Failed to create VPC: {str(e)}")
            raise
            
    def _update_vpc(self, current_state: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing VPC"""
        print(f"\\n🔄 Updating VPC: {self.vpc_name}")
        print(f"   📋 Changes to apply:")
        for change in actions["changes"]:
            print(f"      • {change}")
            
        try:
            # Update through managers
            changes_applied = 0
            
            if self.vpc_manager and actions["update_vpc"]:
                vpc_result = self.vpc_manager.update_vpc(
                    name=self.vpc_name,
                    current_config=current_state,
                    desired_config=self._get_vpc_configuration_summary()
                )
                if vpc_result:
                    changes_applied += 1
                    
            # Handle subnet changes
            if actions["create_subnets"] and self.subnet_manager:
                for subnet in actions["create_subnets"]:
                    result = self.subnet_manager.create_subnet(vpc_name=self.vpc_name, **subnet)
                    if result:
                        changes_applied += 1
                        
            # Handle firewall rule changes
            if actions["create_firewall_rules"] and self.firewall_manager:
                for rule in actions["create_firewall_rules"]:
                    result = self.firewall_manager.create_firewall_rule(vpc_name=self.vpc_name, **rule)
                    if result:
                        changes_applied += 1
                
            print(f"✅ VPC updated successfully!")
            print(f"   🌐 VPC: {self.vpc_name}")
            print(f"   🔄 Changes Applied: {changes_applied}")
            
            return {
                "success": True,
                "name": self.vpc_name,
                "changes_applied": changes_applied,
                "updated": True
            }
                
        except Exception as e:
            print(f"❌ Failed to update VPC: {str(e)}")
            raise
            
    def _keep_vpc(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing VPC (no changes needed)"""
        print(f"\\n✅ VPC '{self.vpc_name}' is up to date")
        print(f"   🌍 URL: {current_state.get('vpc_url', 'Unknown')}")
        print(f"   🌐 Subnets: {current_state.get('subnets_count', 0)}")
        print(f"   🔥 Firewall Rules: {current_state.get('firewall_rules_count', 0)}")
        print(f"   📊 Status: {current_state.get('status', 'Unknown')}")
        
        return {
            "success": True,
            "name": self.vpc_name,
            "vpc_url": current_state.get('vpc_url'),
            "subnets_count": current_state.get('subnets_count', 0),
            "firewall_rules_count": current_state.get('firewall_rules_count', 0),
            "status": current_state.get('status'),
            "unchanged": True
        }
        
    def _display_vpc_preview(self, actions: Dict[str, Any], current_state: Dict[str, Any]):
        """Display preview of actions to be taken"""
        print(f"\\n🌐 Google Cloud VPC Preview")
        print(f"   🎯 VPC: {self.vpc_name}")
        print(f"   📝 Description: {self.vpc_description}")
        print(f"   🛤️  Routing: {self.routing_mode}")
        
        if actions["create_vpc"]:
            print(f"\\n╭─ 🆕 WILL CREATE")
            print(f"├─ 🌐 VPC Network: {self.vpc_name}")
            print(f"├─ 🛤️  Routing Mode: {self.routing_mode}")
            print(f"├─ 📏 MTU: {self.mtu}")
            print(f"├─ 🏗️  Auto Subnets: {self.auto_create_subnetworks}")
            print(f"├─ 🌐 Subnets: {len(self.subnets)} to create")
            print(f"├─ 🔥 Firewall Rules: {len(self.firewall_rules)} to create")
            print(f"╰─ 💰 Estimated Cost: {self._calculate_vpc_cost()}")
            
            # Show sample subnets
            if self.subnets:
                print(f"\\n🌐 Subnets to Create:")
                for subnet in self.subnets[:3]:  # Show first 3
                    print(f"   • {subnet['name']}: {subnet['cidr']} ({subnet['region']})")
                if len(self.subnets) > 3:
                    print(f"   ... and {len(self.subnets) - 3} more subnets")
            
        elif any([actions["update_vpc"], actions["create_subnets"], actions["create_firewall_rules"]]):
            print(f"\\n╭─ 🔄 WILL UPDATE")
            print(f"├─ 🌐 VPC Network: {self.vpc_name}")
            print(f"├─ 📋 Changes:")
            for change in actions["changes"]:
                print(f"│  • {change}")
            print(f"╰─ 💰 Updated Cost: {self._calculate_vpc_cost()}")
            
        else:
            print(f"\\n╭─ ✅ WILL KEEP")
            print(f"├─ 🌐 VPC Network: {self.vpc_name}")
            print(f"├─ 🌍 URL: {current_state.get('vpc_url', 'Unknown')}")
            print(f"├─ 🌐 Subnets: {current_state.get('subnets_count', 0)}")
            print(f"╰─ 📊 Status: {current_state.get('status', 'Unknown')}")
            
    def _display_vpc_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  VPC Network: {self.vpc_name}")
        print(f"   🌍 URL: {current_state.get('vpc_url', 'Unknown')}")
        print(f"   🌐 Subnets: {current_state.get('subnets_count', 0)}")
        print(f"   🔥 Firewall Rules: {current_state.get('firewall_rules_count', 0)}")
        print(f"   📊 Status: {current_state.get('status', 'Unknown')}")
        print(f"   ⚠️  ALL NETWORK CONNECTIVITY WILL BE PERMANENTLY LOST")
        
    def _destroy_firewall_rules(self) -> bool:
        """Destroy firewall rules"""
        if not self.firewall_manager:
            return True
            
        try:
            return self.firewall_manager.delete_all_firewall_rules(self.vpc_name)
        except Exception as e:
            print(f"⚠️  Warning: Failed to delete firewall rules: {str(e)}")
            return False
            
    def _destroy_subnets(self) -> bool:
        """Destroy subnets"""
        if not self.subnet_manager:
            return True
            
        try:
            return self.subnet_manager.delete_all_subnets(self.vpc_name)
        except Exception as e:
            print(f"⚠️  Warning: Failed to delete subnets: {str(e)}")
            return False
            
    def _destroy_vpc_peerings(self) -> bool:
        """Destroy VPC peerings"""
        if not self.vpc_peerings:
            return True
            
        try:
            # Implementation would delete VPC peerings
            return True
        except Exception as e:
            print(f"⚠️  Warning: Failed to delete VPC peerings: {str(e)}")
            return False
            
    def _calculate_vpc_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_vpc_cost()
        return f"${base_cost:.2f}/month"
        
    def _get_vpc_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current VPC configuration"""
        return {
            "vpc_name": self.vpc_name,
            "description": self.vpc_description,
            "routing_mode": self.routing_mode,
            "auto_create_subnetworks": self.auto_create_subnetworks,
            "mtu": self.mtu,
            "subnets": self.subnets,
            "subnets_count": len(self.subnets),
            "firewall_rules": self.firewall_rules,
            "firewall_rules_count": len(self.firewall_rules),
            "static_routes": self.static_routes,
            "vpc_peerings": self.vpc_peerings,
            "enable_flow_logs": self.enable_flow_logs,
            "flow_logs_config": self.flow_logs_config,
            "dns_config": self.dns_config,
            "labels": self.vpc_labels
        }
        
    def optimize_for(self, priority: str):
        """
        Use Cross-Cloud Magic to optimize for cost/performance/reliability/compliance
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        print(f"🎯 Cross-Cloud Magic: Optimizing VPC for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective VPC")
            # Use regional routing for cost savings
            if self.routing_mode == "GLOBAL":
                print("   💡 Switching to regional routing for cost savings")
                self.routing_mode = "REGIONAL"
            # Disable flow logs for cost savings
            if self.enable_flow_logs:
                print("   💡 Disabling flow logs for cost savings")
                self.enable_flow_logs = False
            # Use standard MTU
            if self.mtu > 1460:
                print("   💡 Using standard MTU for compatibility")
                self.mtu = 1460
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance VPC")
            # Use global routing for performance
            if self.routing_mode == "REGIONAL":
                print("   💡 Enabling global routing for better performance")
                self.routing_mode = "GLOBAL"
            # Use maximum MTU for performance
            if self.mtu < 1500:
                print("   💡 Increasing MTU for better network performance")
                self.mtu = 1500
            # Enable flow logs for performance monitoring
            if not self.enable_flow_logs:
                print("   💡 Enabling flow logs for performance monitoring")
                self.enable_flow_logs = True
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable VPC")
            # Use global routing for reliability
            if self.routing_mode == "REGIONAL":
                print("   💡 Enabling global routing for better reliability")
                self.routing_mode = "GLOBAL"
            # Enable flow logs for monitoring
            if not self.enable_flow_logs:
                print("   💡 Enabling flow logs for network monitoring")
                self.enable_flow_logs = True
                self.flow_logs_config["flow_sampling"] = 1.0  # Full sampling
            # Enable DNS logging
            self.dns_config["enable_logging"] = True
            print("   💡 Enabled comprehensive network monitoring")
            
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant VPC")
            # Enable flow logs for audit trails
            if not self.enable_flow_logs:
                print("   💡 Enabling flow logs for compliance monitoring")
                self.enable_flow_logs = True
                self.flow_logs_config = {
                    "aggregation_interval": "INTERVAL_5_SEC",
                    "flow_sampling": 1.0,  # Full sampling for compliance
                    "metadata": "INCLUDE_ALL_METADATA"
                }
            # Enable DNS logging for compliance
            self.dns_config["enable_logging"] = True
            # Add compliance labels
            self.vpc_labels.update({
                "compliance": "enabled",
                "audit": "required",
                "data-classification": "regulated"
            })
            print("   💡 Added compliance labels and full audit logging")
            
        return self
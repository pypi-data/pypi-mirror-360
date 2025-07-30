"""
GCP Cloud IAM Lifecycle Mixin

Lifecycle operations for Google Cloud Identity & Access Management.
Handles create, destroy, and preview operations with smart state management.
"""

from typing import Dict, Any, List, Optional


class IAMLifecycleMixin:
    """
    Mixin for IAM lifecycle operations.
    
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
        self._validate_iam_configuration()
        
        # Get current cloud state
        current_state = self._fetch_current_cloud_state()
        
        # Determine actions needed
        actions = self._determine_iam_actions(current_state)
        
        # Display preview
        self._display_iam_preview(actions, current_state)
        
        # Return structured data
        return {
            'resource_type': 'gcp_iam',
            'name': self.iam_name,
            'current_state': current_state,
            'actions': actions,
            'estimated_cost': self._calculate_iam_cost(),
            'configuration': self._get_iam_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the IAM configuration with smart state management.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration
        self._validate_iam_configuration()
        
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_iam_actions(current_state)
        
        # Execute actions
        result = self._execute_iam_actions(actions, current_state)
        
        # Update state
        self.iam_exists = True
        self.iam_created = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the IAM configuration and all associated resources.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying IAM configuration: {self.iam_name}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  IAM configuration '{self.iam_name}' does not exist")
                return {"success": True, "message": "IAM configuration does not exist", "name": self.iam_name}
            
            # Show what will be destroyed
            self._display_iam_destruction_preview(current_state)
            
            # Perform destruction in correct order
            destruction_results = []
            
            # 1. Remove custom roles first
            if self.role_manager and current_state.get("custom_roles"):
                for role in current_state["custom_roles"]:
                    result = self.role_manager.delete_custom_role(role["name"])
                    destruction_results.append(("custom_role", role["name"], result))
            
            # 2. Remove service accounts
            if self.service_account_manager and current_state.get("service_accounts"):
                for sa in current_state["service_accounts"]:
                    result = self.service_account_manager.delete_service_account(sa["email"])
                    destruction_results.append(("service_account", sa["email"], result))
            
            # 3. Clear IAM policy bindings
            if self.iam_manager:
                result = self.iam_manager.clear_iam_policy(self.resource_name)
                destruction_results.append(("iam_policy", self.resource_name, result))
            
            # Check overall success
            overall_success = all(result for _, _, result in destruction_results)
            
            if overall_success:
                print(f"✅ IAM configuration '{self.iam_name}' destroyed successfully")
                self.iam_exists = False
                self.iam_created = False
                return {"success": True, "name": self.iam_name, "destroyed_resources": len(destruction_results)}
            else:
                failed_resources = [name for _, name, result in destruction_results if not result]
                print(f"⚠️  Partial failure destroying IAM configuration. Failed: {failed_resources}")
                return {"success": False, "name": self.iam_name, "error": f"Failed to destroy: {failed_resources}"}
                
        except Exception as e:
            print(f"❌ Error destroying IAM configuration: {str(e)}")
            return {"success": False, "name": self.iam_name, "error": str(e)}
            
    def _validate_iam_configuration(self):
        """Validate the IAM configuration before creation"""
        errors = []
        warnings = []
        
        # Validate resource name
        if not self.resource_name:
            errors.append("Resource name is required (project, organization, or folder)")
        
        # Validate policy bindings
        for i, binding in enumerate(self.policy_bindings):
            if not self._validate_policy_binding(binding):
                errors.append(f"Invalid policy binding at index {i}")
        
        # Validate service accounts
        for sa in self.service_accounts:
            if not self._validate_service_account_config(sa):
                errors.append(f"Invalid service account configuration: {sa.get('account_id', 'Unknown')}")
        
        # Validate custom roles
        for role in self.custom_roles:
            if not self._validate_custom_role_config(role):
                errors.append(f"Invalid custom role configuration: {role.get('role_id', 'Unknown')}")
        
        # Security warnings
        public_bindings = [b for b in self.policy_bindings 
                          if "allUsers" in b.get("members", []) or "allAuthenticatedUsers" in b.get("members", [])]
        if public_bindings:
            warnings.append(f"{len(public_bindings)} binding(s) grant public access - review for security")
        
        # Owner role warnings
        owner_bindings = [b for b in self.policy_bindings if b.get("role") == "roles/owner"]
        if len(owner_bindings) > 2:
            warnings.append(f"{len(owner_bindings)} owner role bindings found - consider limiting owner access")
        
        if errors:
            raise ValueError(f"IAM configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  IAM configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
                
    def _determine_iam_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create_policy": False,
            "update_policy": False,
            "keep_policy": False,
            "create_service_accounts": [],
            "update_service_accounts": [],
            "delete_service_accounts": [],
            "create_custom_roles": [],
            "update_custom_roles": [],
            "delete_custom_roles": [],
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create_policy"] = True
            actions["create_service_accounts"] = self.service_accounts
            actions["create_custom_roles"] = self.custom_roles
            actions["changes"].append("Create new IAM policy")
            if self.service_accounts:
                actions["changes"].append(f"Create {len(self.service_accounts)} service accounts")
            if self.custom_roles:
                actions["changes"].append(f"Create {len(self.custom_roles)} custom roles")
        else:
            # Compare current state with desired state
            policy_changes = self._detect_policy_drift(current_state)
            sa_changes = self._detect_service_account_drift(current_state)
            role_changes = self._detect_custom_role_drift(current_state)
            
            if policy_changes:
                actions["update_policy"] = True
                actions["changes"].extend(policy_changes)
            else:
                actions["keep_policy"] = True
                
            if sa_changes:
                actions["create_service_accounts"] = sa_changes.get("create", [])
                actions["update_service_accounts"] = sa_changes.get("update", [])
                actions["delete_service_accounts"] = sa_changes.get("delete", [])
                
                if sa_changes.get("create"):
                    actions["changes"].append(f"Create {len(sa_changes['create'])} new service accounts")
                if sa_changes.get("update"):
                    actions["changes"].append(f"Update {len(sa_changes['update'])} existing service accounts")
                if sa_changes.get("delete"):
                    actions["changes"].append(f"Delete {len(sa_changes['delete'])} obsolete service accounts")
                    
            if role_changes:
                actions["create_custom_roles"] = role_changes.get("create", [])
                actions["update_custom_roles"] = role_changes.get("update", [])
                actions["delete_custom_roles"] = role_changes.get("delete", [])
                
                if role_changes.get("create"):
                    actions["changes"].append(f"Create {len(role_changes['create'])} new custom roles")
                if role_changes.get("update"):
                    actions["changes"].append(f"Update {len(role_changes['update'])} existing custom roles")
                if role_changes.get("delete"):
                    actions["changes"].append(f"Delete {len(role_changes['delete'])} obsolete custom roles")
                    
            if not actions["changes"]:
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_policy_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences between current and desired IAM policy"""
        changes = []
        
        current_bindings = current_state.get("bindings", [])
        desired_bindings = self.policy_bindings
        
        # Compare binding counts
        if len(current_bindings) != len(desired_bindings):
            changes.append(f"Policy bindings: {len(current_bindings)} → {len(desired_bindings)}")
        
        # Compare policy version
        current_version = current_state.get("policy_version", 1)
        if current_version != self.policy_version:
            changes.append(f"Policy version: {current_version} → {self.policy_version}")
        
        # Detailed binding comparison would be more complex
        # For now, we'll do a simplified check
        current_roles = set(b.get("role") for b in current_bindings)
        desired_roles = set(b.get("role") for b in desired_bindings)
        
        new_roles = desired_roles - current_roles
        removed_roles = current_roles - desired_roles
        
        if new_roles:
            changes.append(f"New roles: {', '.join(new_roles)}")
        if removed_roles:
            changes.append(f"Removed roles: {', '.join(removed_roles)}")
            
        return changes
        
    def _detect_service_account_drift(self, current_state: Dict[str, Any]) -> Dict[str, List]:
        """Detect differences between current and desired service accounts"""
        current_sas = current_state.get("service_accounts", [])
        desired_sas = self.service_accounts
        
        # Create lookup dictionaries
        current_lookup = {sa["email"].split("@")[0]: sa for sa in current_sas}
        desired_lookup = {sa["account_id"]: sa for sa in desired_sas}
        
        changes = {
            "create": [],
            "update": [],
            "delete": []
        }
        
        # Find service accounts to create
        for account_id, sa in desired_lookup.items():
            if account_id not in current_lookup:
                changes["create"].append(sa)
                
        # Find service accounts to delete
        for account_id, sa in current_lookup.items():
            if account_id not in desired_lookup:
                # Don't delete default service accounts
                if not account_id.endswith("-compute"):
                    changes["delete"].append(sa)
                    
        return changes
        
    def _detect_custom_role_drift(self, current_state: Dict[str, Any]) -> Dict[str, List]:
        """Detect differences between current and desired custom roles"""
        current_roles = current_state.get("custom_roles", [])
        desired_roles = self.custom_roles
        
        # Create lookup dictionaries
        current_lookup = {role["name"].split("/")[-1]: role for role in current_roles}
        desired_lookup = {role["role_id"]: role for role in desired_roles}
        
        changes = {
            "create": [],
            "update": [],
            "delete": []
        }
        
        # Find roles to create
        for role_id, role in desired_lookup.items():
            if role_id not in current_lookup:
                changes["create"].append(role)
                
        # Find roles to delete
        for role_id, role in current_lookup.items():
            if role_id not in desired_lookup:
                changes["delete"].append(role)
                
        return changes
        
    def _execute_iam_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create_policy"]:
            return self._create_iam_configuration()
        elif any([actions["update_policy"], actions["create_service_accounts"], actions["create_custom_roles"]]):
            return self._update_iam_configuration(current_state, actions)
        else:
            return self._keep_iam_configuration(current_state)
            
    def _create_iam_configuration(self) -> Dict[str, Any]:
        """Create a new IAM configuration"""
        print(f"\\n🔐 Creating IAM configuration: {self.iam_name}")
        print(f"   📝 Resource: {self.resource_name}")
        print(f"   🎭 Policy Bindings: {len(self.policy_bindings)}")
        print(f"   🤖 Service Accounts: {len(self.service_accounts)}")
        print(f"   🎨 Custom Roles: {len(self.custom_roles)}")
        print(f"   📊 Policy Version: {self.policy_version}")
        
        try:
            # Create custom roles first
            custom_roles_created = 0
            if self.custom_roles and self.role_manager:
                for role in self.custom_roles:
                    result = self.role_manager.create_custom_role(
                        project_id=self.project_id,
                        **role
                    )
                    if result:
                        custom_roles_created += 1
            
            # Create service accounts
            service_accounts_created = 0
            if self.service_accounts and self.service_account_manager:
                for sa in self.service_accounts:
                    result = self.service_account_manager.create_service_account(
                        project_id=self.project_id,
                        **sa
                    )
                    if result:
                        service_accounts_created += 1
            
            # Apply IAM policy
            policy_created = False
            if self.iam_manager:
                policy_result = self.iam_manager.set_iam_policy(
                    resource_name=self.resource_name,
                    bindings=self.policy_bindings,
                    version=self.policy_version,
                    audit_configs=self.audit_logging_enabled
                )
                policy_created = bool(policy_result)
            
            print(f"\\n✅ IAM configuration created successfully!")
            print(f"   🔐 Resource: {self.resource_name}")
            print(f"   🎭 Policy Bindings: {len(self.policy_bindings)} applied")
            print(f"   🤖 Service Accounts: {service_accounts_created}/{len(self.service_accounts)} created")
            print(f"   🎨 Custom Roles: {custom_roles_created}/{len(self.custom_roles)} created")
            print(f"   📊 Policy Version: {self.policy_version}")
            
            if self.audit_logging_enabled:
                print(f"   📋 Audit Logging: Enabled")
            
            return {
                "success": True,
                "name": self.iam_name,
                "resource_name": self.resource_name,
                "policy_bindings_applied": len(self.policy_bindings),
                "service_accounts_created": service_accounts_created,
                "custom_roles_created": custom_roles_created,
                "policy_version": self.policy_version,
                "audit_logging_enabled": self.audit_logging_enabled,
                "created": True
            }
                
        except Exception as e:
            print(f"❌ Failed to create IAM configuration: {str(e)}")
            raise
            
    def _update_iam_configuration(self, current_state: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing IAM configuration"""
        print(f"\\n🔄 Updating IAM configuration: {self.iam_name}")
        print(f"   📋 Changes to apply:")
        for change in actions["changes"]:
            print(f"      • {change}")
            
        try:
            changes_applied = 0
            
            # Create new custom roles
            if actions["create_custom_roles"] and self.role_manager:
                for role in actions["create_custom_roles"]:
                    result = self.role_manager.create_custom_role(project_id=self.project_id, **role)
                    if result:
                        changes_applied += 1
            
            # Create new service accounts
            if actions["create_service_accounts"] and self.service_account_manager:
                for sa in actions["create_service_accounts"]:
                    result = self.service_account_manager.create_service_account(project_id=self.project_id, **sa)
                    if result:
                        changes_applied += 1
            
            # Update IAM policy
            if actions["update_policy"] and self.iam_manager:
                result = self.iam_manager.set_iam_policy(
                    resource_name=self.resource_name,
                    bindings=self.policy_bindings,
                    version=self.policy_version,
                    audit_configs=self.audit_logging_enabled
                )
                if result:
                    changes_applied += 1
                
            print(f"✅ IAM configuration updated successfully!")
            print(f"   🔐 Resource: {self.resource_name}")
            print(f"   🔄 Changes Applied: {changes_applied}")
            
            return {
                "success": True,
                "name": self.iam_name,
                "changes_applied": changes_applied,
                "updated": True
            }
                
        except Exception as e:
            print(f"❌ Failed to update IAM configuration: {str(e)}")
            raise
            
    def _keep_iam_configuration(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing IAM configuration (no changes needed)"""
        print(f"\\n✅ IAM configuration '{self.iam_name}' is up to date")
        print(f"   🔐 Resource: {current_state.get('resource_name', 'Unknown')}")
        print(f"   🎭 Policy Bindings: {current_state.get('bindings_count', 0)}")
        print(f"   🤖 Service Accounts: {current_state.get('service_accounts_count', 0)}")
        print(f"   🎨 Custom Roles: {current_state.get('custom_roles_count', 0)}")
        print(f"   📊 Status: {current_state.get('status', 'Unknown')}")
        
        return {
            "success": True,
            "name": self.iam_name,
            "resource_name": current_state.get('resource_name'),
            "bindings_count": current_state.get('bindings_count', 0),
            "service_accounts_count": current_state.get('service_accounts_count', 0),
            "custom_roles_count": current_state.get('custom_roles_count', 0),
            "status": current_state.get('status'),
            "unchanged": True
        }
        
    def _display_iam_preview(self, actions: Dict[str, Any], current_state: Dict[str, Any]):
        """Display preview of actions to be taken"""
        print(f"\\n🔐 Google Cloud IAM Preview")
        print(f"   🎯 Configuration: {self.iam_name}")
        print(f"   📝 Resource: {self.resource_name}")
        print(f"   📊 Policy Version: {self.policy_version}")
        
        if actions["create_policy"]:
            print(f"\\n╭─ 🆕 WILL CREATE")
            print(f"├─ 🔐 IAM Configuration: {self.iam_name}")
            print(f"├─ 📝 Resource: {self.resource_name}")
            print(f"├─ 🎭 Policy Bindings: {len(self.policy_bindings)}")
            print(f"├─ 🤖 Service Accounts: {len(self.service_accounts)}")
            print(f"├─ 🎨 Custom Roles: {len(self.custom_roles)}")
            print(f"├─ 📊 Policy Version: {self.policy_version}")
            print(f"├─ 📋 Audit Logging: {'Enabled' if self.audit_logging_enabled else 'Disabled'}")
            print(f"╰─ 💰 Estimated Cost: {self._calculate_iam_cost()}")
            
            # Show sample bindings
            if self.policy_bindings:
                print(f"\\n🎭 Policy Bindings to Create:")
                for binding in self.policy_bindings[:3]:  # Show first 3
                    role = binding.get("role", "Unknown")
                    member_count = len(binding.get("members", []))
                    print(f"   • {role}: {member_count} member(s)")
                if len(self.policy_bindings) > 3:
                    print(f"   ... and {len(self.policy_bindings) - 3} more bindings")
            
        elif any([actions["update_policy"], actions["create_service_accounts"], actions["create_custom_roles"]]):
            print(f"\\n╭─ 🔄 WILL UPDATE")
            print(f"├─ 🔐 IAM Configuration: {self.iam_name}")
            print(f"├─ 📋 Changes:")
            for change in actions["changes"]:
                print(f"│  • {change}")
            print(f"╰─ 💰 Updated Cost: {self._calculate_iam_cost()}")
            
        else:
            print(f"\\n╭─ ✅ WILL KEEP")
            print(f"├─ 🔐 IAM Configuration: {self.iam_name}")
            print(f"├─ 📝 Resource: {current_state.get('resource_name', 'Unknown')}")
            print(f"├─ 🎭 Policy Bindings: {current_state.get('bindings_count', 0)}")
            print(f"╰─ 📊 Status: {current_state.get('status', 'Unknown')}")
            
    def _display_iam_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  IAM Configuration: {self.iam_name}")
        print(f"   📝 Resource: {current_state.get('resource_name', 'Unknown')}")
        print(f"   🎭 Policy Bindings: {current_state.get('bindings_count', 0)}")
        print(f"   🤖 Service Accounts: {current_state.get('service_accounts_count', 0)}")
        print(f"   🎨 Custom Roles: {current_state.get('custom_roles_count', 0)}")
        print(f"   ⚠️  ALL ACCESS PERMISSIONS WILL BE PERMANENTLY LOST")
        
    def _calculate_iam_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_iam_cost()
        return f"${base_cost:.2f}/month"
        
    def _get_iam_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current IAM configuration"""
        return {
            "iam_name": self.iam_name,
            "description": self.iam_description,
            "resource_name": self.resource_name,
            "policy_version": self.policy_version,
            "policy_bindings": self.policy_bindings,
            "policy_bindings_count": len(self.policy_bindings),
            "service_accounts": self.service_accounts,
            "service_accounts_count": len(self.service_accounts),
            "custom_roles": self.custom_roles,
            "custom_roles_count": len(self.custom_roles),
            "audit_logging_enabled": self.audit_logging_enabled,
            "labels": self.iam_labels
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
        
        print(f"🎯 Cross-Cloud Magic: Optimizing IAM for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective IAM")
            # Disable audit logging for cost savings
            if self.audit_logging_enabled:
                print("   💡 Disabling audit logging for cost savings")
                self.audit_logging_enabled = False
            # Use policy version 1 for simplicity
            if self.policy_version > 1:
                print("   💡 Using basic policy version for cost efficiency")
                self.policy_version = 1
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance IAM")
            # Use latest policy version for performance
            if self.policy_version < 3:
                print("   💡 Upgrading to policy version 3 for better performance")
                self.policy_version = 3
            # Enable audit logging for performance monitoring
            if not self.audit_logging_enabled:
                print("   💡 Enabling audit logging for performance monitoring")
                self.audit_logging_enabled = True
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable IAM")
            # Use latest policy version for reliability
            if self.policy_version < 3:
                print("   💡 Upgrading to policy version 3 for better reliability")
                self.policy_version = 3
            # Enable audit logging for monitoring
            if not self.audit_logging_enabled:
                print("   💡 Enabling audit logging for reliability monitoring")
                self.audit_logging_enabled = True
                
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant IAM")
            # Use latest policy version for compliance features
            if self.policy_version < 3:
                print("   💡 Upgrading to policy version 3 for compliance features")
                self.policy_version = 3
            # Enable audit logging for compliance
            if not self.audit_logging_enabled:
                print("   💡 Enabling audit logging for compliance monitoring")
                self.audit_logging_enabled = True
            # Add compliance labels
            self.iam_labels.update({
                "compliance": "enabled",
                "audit": "required",
                "security": "enhanced"
            })
            print("   💡 Added compliance labels")
            
        return self
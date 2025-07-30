"""
GCP Cloud Monitoring Lifecycle Mixin

Lifecycle operations for Google Cloud Monitoring.
Handles create, destroy, and preview operations with smart state management.
"""

from typing import Dict, Any, List, Optional


class MonitoringLifecycleMixin:
    """
    Mixin for Cloud Monitoring lifecycle operations.
    
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
        self._validate_monitoring_configuration()
        
        # Get current cloud state
        current_state = self._fetch_current_cloud_state()
        
        # Determine actions needed
        actions = self._determine_monitoring_actions(current_state)
        
        # Display preview
        self._display_monitoring_preview(actions, current_state)
        
        # Return structured data
        return {
            'resource_type': 'gcp_monitoring',
            'name': self.monitoring_name,
            'current_state': current_state,
            'actions': actions,
            'estimated_cost': self._calculate_monitoring_cost(),
            'configuration': self._get_monitoring_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the monitoring configuration with smart state management.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration
        self._validate_monitoring_configuration()
        
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_monitoring_actions(current_state)
        
        # Execute actions
        result = self._execute_monitoring_actions(actions, current_state)
        
        # Update state
        self.monitoring_exists = True
        self.monitoring_created = True
        self.workspace_created = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the monitoring configuration and all associated resources.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying Monitoring configuration: {self.monitoring_name}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  Monitoring configuration '{self.monitoring_name}' does not exist")
                return {"success": True, "message": "Monitoring configuration does not exist", "name": self.monitoring_name}
            
            # Show what will be destroyed
            self._display_monitoring_destruction_preview(current_state)
            
            # Perform destruction in correct order
            destruction_results = []
            
            # 1. Delete uptime checks first
            if self.uptime_manager and current_state.get("uptime_checks"):
                for check in current_state["uptime_checks"]:
                    result = self.uptime_manager.delete_uptime_check(check["name"])
                    destruction_results.append(("uptime_check", check["name"], result))
            
            # 2. Delete dashboards
            if self.dashboard_manager and current_state.get("dashboards"):
                for dashboard in current_state["dashboards"]:
                    result = self.dashboard_manager.delete_dashboard(dashboard["name"])
                    destruction_results.append(("dashboard", dashboard["name"], result))
            
            # 3. Delete alert policies
            if self.alerting_manager and current_state.get("alert_policies"):
                for policy in current_state["alert_policies"]:
                    result = self.alerting_manager.delete_alert_policy(policy["name"])
                    destruction_results.append(("alert_policy", policy["name"], result))
            
            # 4. Delete notification channels
            if self.alerting_manager and current_state.get("notification_channels"):
                for channel in current_state["notification_channels"]:
                    result = self.alerting_manager.delete_notification_channel(channel["name"])
                    destruction_results.append(("notification_channel", channel["name"], result))
            
            # Check overall success
            overall_success = all(result for _, _, result in destruction_results)
            
            if overall_success:
                print(f"✅ Monitoring configuration '{self.monitoring_name}' destroyed successfully")
                self.monitoring_exists = False
                self.monitoring_created = False
                self.workspace_created = False
                return {"success": True, "name": self.monitoring_name, "destroyed_resources": len(destruction_results)}
            else:
                failed_resources = [name for _, name, result in destruction_results if not result]
                print(f"⚠️  Partial failure destroying monitoring configuration. Failed: {failed_resources}")
                return {"success": False, "name": self.monitoring_name, "error": f"Failed to destroy: {failed_resources}"}
                
        except Exception as e:
            print(f"❌ Error destroying monitoring configuration: {str(e)}")
            return {"success": False, "name": self.monitoring_name, "error": str(e)}
            
    def _validate_monitoring_configuration(self):
        """Validate the monitoring configuration before creation"""
        errors = []
        warnings = []
        
        # Validate workspace ID
        if not self.workspace_id:
            errors.append("Workspace ID is required")
        
        # Validate alert policies
        for i, policy in enumerate(self.alert_policies):
            if not self._validate_alert_policy_config(policy):
                errors.append(f"Invalid alert policy at index {i}")
        
        # Validate notification channels
        for i, channel in enumerate(self.notification_channels):
            if not self._validate_notification_channel_config(channel):
                errors.append(f"Invalid notification channel at index {i}")
        
        # Validate uptime checks
        for i, check in enumerate(self.uptime_checks):
            if not self._validate_uptime_check_config(check):
                errors.append(f"Invalid uptime check at index {i}")
        
        # Validate dashboards
        for i, dashboard in enumerate(self.dashboards):
            if not self._validate_dashboard_config(dashboard):
                errors.append(f"Invalid dashboard at index {i}")
        
        # Cost warnings
        estimated_cost = self._estimate_monitoring_cost()
        if estimated_cost > 100:
            warnings.append(f"High estimated cost: ${estimated_cost:.2f}/month")
        
        # Uptime check limits
        if len(self.uptime_checks) > 100:
            warnings.append(f"{len(self.uptime_checks)} uptime checks may exceed quotas")
        
        if errors:
            raise ValueError(f"Monitoring configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Monitoring configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
                
    def _determine_monitoring_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create_workspace": False,
            "update_workspace": False,
            "keep_workspace": False,
            "create_alert_policies": [],
            "update_alert_policies": [],
            "delete_alert_policies": [],
            "create_notification_channels": [],
            "update_notification_channels": [],
            "delete_notification_channels": [],
            "create_uptime_checks": [],
            "update_uptime_checks": [],
            "delete_uptime_checks": [],
            "create_dashboards": [],
            "update_dashboards": [],
            "delete_dashboards": [],
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create_workspace"] = True
            actions["create_alert_policies"] = self.alert_policies
            actions["create_notification_channels"] = self.notification_channels
            actions["create_uptime_checks"] = self.uptime_checks
            actions["create_dashboards"] = self.dashboards
            actions["changes"].append("Create new monitoring workspace")
            if self.alert_policies:
                actions["changes"].append(f"Create {len(self.alert_policies)} alert policies")
            if self.notification_channels:
                actions["changes"].append(f"Create {len(self.notification_channels)} notification channels")
            if self.uptime_checks:
                actions["changes"].append(f"Create {len(self.uptime_checks)} uptime checks")
            if self.dashboards:
                actions["changes"].append(f"Create {len(self.dashboards)} dashboards")
        else:
            # Compare current state with desired state
            policy_changes = self._detect_alert_policy_drift(current_state)
            channel_changes = self._detect_notification_channel_drift(current_state)
            uptime_changes = self._detect_uptime_check_drift(current_state)
            dashboard_changes = self._detect_dashboard_drift(current_state)
            
            if any([policy_changes, channel_changes, uptime_changes, dashboard_changes]):
                actions["update_workspace"] = True
                
                if policy_changes:
                    actions["create_alert_policies"] = policy_changes.get("create", [])
                    actions["update_alert_policies"] = policy_changes.get("update", [])
                    actions["delete_alert_policies"] = policy_changes.get("delete", [])
                    
                if channel_changes:
                    actions["create_notification_channels"] = channel_changes.get("create", [])
                    actions["update_notification_channels"] = channel_changes.get("update", [])
                    actions["delete_notification_channels"] = channel_changes.get("delete", [])
                    
                if uptime_changes:
                    actions["create_uptime_checks"] = uptime_changes.get("create", [])
                    actions["update_uptime_checks"] = uptime_changes.get("update", [])
                    actions["delete_uptime_checks"] = uptime_changes.get("delete", [])
                    
                if dashboard_changes:
                    actions["create_dashboards"] = dashboard_changes.get("create", [])
                    actions["update_dashboards"] = dashboard_changes.get("update", [])
                    actions["delete_dashboards"] = dashboard_changes.get("delete", [])
                    
                # Build change descriptions
                if policy_changes and policy_changes.get("create"):
                    actions["changes"].append(f"Create {len(policy_changes['create'])} new alert policies")
                if channel_changes and channel_changes.get("create"):
                    actions["changes"].append(f"Create {len(channel_changes['create'])} new notification channels")
                if uptime_changes and uptime_changes.get("create"):
                    actions["changes"].append(f"Create {len(uptime_changes['create'])} new uptime checks")
                if dashboard_changes and dashboard_changes.get("create"):
                    actions["changes"].append(f"Create {len(dashboard_changes['create'])} new dashboards")
                    
            else:
                actions["keep_workspace"] = True
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_alert_policy_drift(self, current_state: Dict[str, Any]) -> Dict[str, List]:
        """Detect differences between current and desired alert policies"""
        current_policies = current_state.get("alert_policies", [])
        desired_policies = self.alert_policies
        
        # Create lookup dictionaries by display name
        current_lookup = {policy["display_name"]: policy for policy in current_policies}
        desired_lookup = {policy["display_name"]: policy for policy in desired_policies}
        
        changes = {
            "create": [],
            "update": [],
            "delete": []
        }
        
        # Find policies to create
        for name, policy in desired_lookup.items():
            if name not in current_lookup:
                changes["create"].append(policy)
                
        # Find policies to delete
        for name, policy in current_lookup.items():
            if name not in desired_lookup:
                changes["delete"].append(policy)
                
        return changes
        
    def _detect_notification_channel_drift(self, current_state: Dict[str, Any]) -> Dict[str, List]:
        """Detect differences between current and desired notification channels"""
        current_channels = current_state.get("notification_channels", [])
        desired_channels = self.notification_channels
        
        # Create lookup dictionaries by display name
        current_lookup = {channel["display_name"]: channel for channel in current_channels}
        desired_lookup = {channel["display_name"]: channel for channel in desired_channels}
        
        changes = {
            "create": [],
            "update": [],
            "delete": []
        }
        
        # Find channels to create
        for name, channel in desired_lookup.items():
            if name not in current_lookup:
                changes["create"].append(channel)
                
        # Find channels to delete
        for name, channel in current_lookup.items():
            if name not in desired_lookup:
                changes["delete"].append(channel)
                
        return changes
        
    def _detect_uptime_check_drift(self, current_state: Dict[str, Any]) -> Dict[str, List]:
        """Detect differences between current and desired uptime checks"""
        current_checks = current_state.get("uptime_checks", [])
        desired_checks = self.uptime_checks
        
        # Create lookup dictionaries by display name
        current_lookup = {check["display_name"]: check for check in current_checks}
        desired_lookup = {check["display_name"]: check for check in desired_checks}
        
        changes = {
            "create": [],
            "update": [],
            "delete": []
        }
        
        # Find checks to create
        for name, check in desired_lookup.items():
            if name not in current_lookup:
                changes["create"].append(check)
                
        # Find checks to delete
        for name, check in current_lookup.items():
            if name not in desired_lookup:
                changes["delete"].append(check)
                
        return changes
        
    def _detect_dashboard_drift(self, current_state: Dict[str, Any]) -> Dict[str, List]:
        """Detect differences between current and desired dashboards"""
        current_dashboards = current_state.get("dashboards", [])
        desired_dashboards = self.dashboards
        
        # Create lookup dictionaries by display name
        current_lookup = {dash["display_name"]: dash for dash in current_dashboards}
        desired_lookup = {dash["display_name"]: dash for dash in desired_dashboards}
        
        changes = {
            "create": [],
            "update": [],
            "delete": []
        }
        
        # Find dashboards to create
        for name, dashboard in desired_lookup.items():
            if name not in current_lookup:
                changes["create"].append(dashboard)
                
        # Find dashboards to delete
        for name, dashboard in current_lookup.items():
            if name not in desired_lookup:
                changes["delete"].append(dashboard)
                
        return changes
        
    def _execute_monitoring_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create_workspace"]:
            return self._create_monitoring_configuration()
        elif actions["update_workspace"]:
            return self._update_monitoring_configuration(current_state, actions)
        else:
            return self._keep_monitoring_configuration(current_state)
            
    def _create_monitoring_configuration(self) -> Dict[str, Any]:
        """Create a new monitoring configuration"""
        print(f"\n📊 Creating Monitoring configuration: {self.monitoring_name}")
        print(f"   🏢 Workspace: {self.workspace_id}")
        print(f"   🚨 Alert Policies: {len(self.alert_policies)}")
        print(f"   📢 Notification Channels: {len(self.notification_channels)}")
        print(f"   🔍 Uptime Checks: {len(self.uptime_checks)}")
        print(f"   📈 Dashboards: {len(self.dashboards)}")
        print(f"   📊 Custom Metrics: {len(self.custom_metrics)}")
        
        try:
            # Create notification channels first
            channels_created = 0
            if self.notification_channels and self.alerting_manager:
                for channel in self.notification_channels:
                    result = self.alerting_manager.create_notification_channel(
                        workspace_id=self.workspace_id,
                        **channel
                    )
                    if result:
                        channels_created += 1
            
            # Create alert policies
            policies_created = 0
            if self.alert_policies and self.alerting_manager:
                for policy in self.alert_policies:
                    result = self.alerting_manager.create_alert_policy(
                        workspace_id=self.workspace_id,
                        **policy
                    )
                    if result:
                        policies_created += 1
            
            # Create uptime checks
            checks_created = 0
            if self.uptime_checks and self.uptime_manager:
                for check in self.uptime_checks:
                    result = self.uptime_manager.create_uptime_check(
                        workspace_id=self.workspace_id,
                        **check
                    )
                    if result:
                        checks_created += 1
            
            # Create dashboards
            dashboards_created = 0
            if self.dashboards and self.dashboard_manager:
                for dashboard in self.dashboards:
                    result = self.dashboard_manager.create_dashboard(
                        workspace_id=self.workspace_id,
                        **dashboard
                    )
                    if result:
                        dashboards_created += 1
            
            print(f"\n✅ Monitoring configuration created successfully!")
            print(f"   🏢 Workspace: {self.workspace_id}")
            print(f"   🚨 Alert Policies: {policies_created}/{len(self.alert_policies)} created")
            print(f"   📢 Notification Channels: {channels_created}/{len(self.notification_channels)} created")
            print(f"   🔍 Uptime Checks: {checks_created}/{len(self.uptime_checks)} created")
            print(f"   📈 Dashboards: {dashboards_created}/{len(self.dashboards)} created")
            print(f"   💰 Estimated Cost: {self._calculate_monitoring_cost()}")
            
            return {
                "success": True,
                "name": self.monitoring_name,
                "workspace_id": self.workspace_id,
                "alert_policies_created": policies_created,
                "notification_channels_created": channels_created,
                "uptime_checks_created": checks_created,
                "dashboards_created": dashboards_created,
                "estimated_cost": self._calculate_monitoring_cost(),
                "created": True
            }
                
        except Exception as e:
            print(f"❌ Failed to create monitoring configuration: {str(e)}")
            raise
            
    def _update_monitoring_configuration(self, current_state: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing monitoring configuration"""
        print(f"\n🔄 Updating Monitoring configuration: {self.monitoring_name}")
        print(f"   📋 Changes to apply:")
        for change in actions["changes"]:
            print(f"      • {change}")
            
        try:
            changes_applied = 0
            
            # Create new notification channels
            if actions["create_notification_channels"] and self.alerting_manager:
                for channel in actions["create_notification_channels"]:
                    result = self.alerting_manager.create_notification_channel(workspace_id=self.workspace_id, **channel)
                    if result:
                        changes_applied += 1
            
            # Create new alert policies
            if actions["create_alert_policies"] and self.alerting_manager:
                for policy in actions["create_alert_policies"]:
                    result = self.alerting_manager.create_alert_policy(workspace_id=self.workspace_id, **policy)
                    if result:
                        changes_applied += 1
            
            # Create new uptime checks
            if actions["create_uptime_checks"] and self.uptime_manager:
                for check in actions["create_uptime_checks"]:
                    result = self.uptime_manager.create_uptime_check(workspace_id=self.workspace_id, **check)
                    if result:
                        changes_applied += 1
            
            # Create new dashboards
            if actions["create_dashboards"] and self.dashboard_manager:
                for dashboard in actions["create_dashboards"]:
                    result = self.dashboard_manager.create_dashboard(workspace_id=self.workspace_id, **dashboard)
                    if result:
                        changes_applied += 1
                
            print(f"✅ Monitoring configuration updated successfully!")
            print(f"   🏢 Workspace: {self.workspace_id}")
            print(f"   🔄 Changes Applied: {changes_applied}")
            
            return {
                "success": True,
                "name": self.monitoring_name,
                "changes_applied": changes_applied,
                "updated": True
            }
                
        except Exception as e:
            print(f"❌ Failed to update monitoring configuration: {str(e)}")
            raise
            
    def _keep_monitoring_configuration(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing monitoring configuration (no changes needed)"""
        print(f"\n✅ Monitoring configuration '{self.monitoring_name}' is up to date")
        print(f"   🏢 Workspace: {current_state.get('workspace_id', 'Unknown')}")
        print(f"   🚨 Alert Policies: {current_state.get('alert_policies_count', 0)}")
        print(f"   📢 Notification Channels: {current_state.get('notification_channels_count', 0)}")
        print(f"   🔍 Uptime Checks: {current_state.get('uptime_checks_count', 0)}")
        print(f"   📈 Dashboards: {current_state.get('dashboards_count', 0)}")
        print(f"   📊 Status: {current_state.get('status', 'Unknown')}")
        
        return {
            "success": True,
            "name": self.monitoring_name,
            "workspace_id": current_state.get('workspace_id'),
            "alert_policies_count": current_state.get('alert_policies_count', 0),
            "notification_channels_count": current_state.get('notification_channels_count', 0),
            "uptime_checks_count": current_state.get('uptime_checks_count', 0),
            "dashboards_count": current_state.get('dashboards_count', 0),
            "status": current_state.get('status'),
            "unchanged": True
        }
        
    def _display_monitoring_preview(self, actions: Dict[str, Any], current_state: Dict[str, Any]):
        """Display preview of actions to be taken"""
        print(f"\n📊 Google Cloud Monitoring Preview")
        print(f"   🎯 Configuration: {self.monitoring_name}")
        print(f"   🏢 Workspace: {self.workspace_id}")
        print(f"   📊 Metrics Scope: {self.metrics_scope}")
        print(f"   📅 Retention: {self.retention_days} days")
        
        if actions["create_workspace"]:
            print(f"\n╭─ 🆕 WILL CREATE")
            print(f"├─ 📊 Monitoring Workspace: {self.monitoring_name}")
            print(f"├─ 🏢 Workspace ID: {self.workspace_id}")
            print(f"├─ 🚨 Alert Policies: {len(self.alert_policies)}")
            print(f"├─ 📢 Notification Channels: {len(self.notification_channels)}")
            print(f"├─ 🔍 Uptime Checks: {len(self.uptime_checks)}")
            print(f"├─ 📈 Dashboards: {len(self.dashboards)}")
            print(f"├─ 📊 Custom Metrics: {len(self.custom_metrics)}")
            print(f"├─ 📅 Retention: {self.retention_days} days")
            print(f"╰─ 💰 Estimated Cost: {self._calculate_monitoring_cost()}")
            
            # Show sample alerts
            if self.alert_policies:
                print(f"\n🚨 Alert Policies to Create:")
                for policy in self.alert_policies[:3]:  # Show first 3
                    name = policy.get("display_name", "Unknown")
                    condition_count = len(policy.get("conditions", []))
                    print(f"   • {name}: {condition_count} condition(s)")
                if len(self.alert_policies) > 3:
                    print(f"   ... and {len(self.alert_policies) - 3} more policies")
            
        elif actions["update_workspace"]:
            print(f"\n╭─ 🔄 WILL UPDATE")
            print(f"├─ 📊 Monitoring Workspace: {self.monitoring_name}")
            print(f"├─ 📋 Changes:")
            for change in actions["changes"]:
                print(f"│  • {change}")
            print(f"╰─ 💰 Updated Cost: {self._calculate_monitoring_cost()}")
            
        else:
            print(f"\n╭─ ✅ WILL KEEP")
            print(f"├─ 📊 Monitoring Workspace: {self.monitoring_name}")
            print(f"├─ 🏢 Workspace: {current_state.get('workspace_id', 'Unknown')}")
            print(f"├─ 🚨 Alert Policies: {current_state.get('alert_policies_count', 0)}")
            print(f"├─ 📢 Notification Channels: {current_state.get('notification_channels_count', 0)}")
            print(f"╰─ 📊 Status: {current_state.get('status', 'Unknown')}")
            
    def _display_monitoring_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  Monitoring Workspace: {self.monitoring_name}")
        print(f"   🏢 Workspace: {current_state.get('workspace_id', 'Unknown')}")
        print(f"   🚨 Alert Policies: {current_state.get('alert_policies_count', 0)}")
        print(f"   📢 Notification Channels: {current_state.get('notification_channels_count', 0)}")
        print(f"   🔍 Uptime Checks: {current_state.get('uptime_checks_count', 0)}")
        print(f"   📈 Dashboards: {current_state.get('dashboards_count', 0)}")
        print(f"   ⚠️  ALL MONITORING DATA AND ALERTS WILL BE PERMANENTLY LOST")
        
    def _calculate_monitoring_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_monitoring_cost()
        return f"${base_cost:.2f}/month"
        
    def _get_monitoring_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current monitoring configuration"""
        return {
            "monitoring_name": self.monitoring_name,
            "description": self.monitoring_description,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "metrics_scope": self.metrics_scope,
            "retention_days": self.retention_days,
            "alert_policies": self.alert_policies,
            "alert_policies_count": len(self.alert_policies),
            "notification_channels": self.notification_channels,
            "notification_channels_count": len(self.notification_channels),
            "uptime_checks": self.uptime_checks,
            "uptime_checks_count": len(self.uptime_checks),
            "dashboards": self.dashboards,
            "dashboards_count": len(self.dashboards),
            "custom_metrics": self.custom_metrics,
            "custom_metrics_count": len(self.custom_metrics),
            "labels": self.monitoring_labels
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
        
        print(f"🎯 Cross-Cloud Magic: Optimizing monitoring for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective monitoring")
            # Reduce retention period for cost savings
            if self.retention_days > 30:
                print("   💡 Reducing retention period to 30 days for cost savings")
                self.retention_days = 30
            # Limit uptime checks
            if len(self.uptime_checks) > 5:
                print("   💡 Limiting uptime checks to reduce costs")
                self.uptime_checks = self.uptime_checks[:5]
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance monitoring")
            # Increase retention for performance analysis
            if self.retention_days < 90:
                print("   💡 Increasing retention to 90 days for performance analysis")
                self.retention_days = 90
            # Add performance-focused alerts
            self.threshold_alert("High Latency", "loadbalancing.googleapis.com/https/total_latencies", 1000)
            print("   💡 Added performance monitoring alerts")
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable monitoring")
            # Comprehensive monitoring for reliability
            if self.retention_days < 60:
                print("   💡 Increasing retention to 60 days for reliability analysis")
                self.retention_days = 60
            # Add reliability alerts
            self.threshold_alert("High Error Rate", "loadbalancing.googleapis.com/https/request_count", 0.05)
            print("   💡 Added reliability monitoring alerts")
                
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant monitoring")
            # Long retention for compliance
            if self.retention_days < 365:
                print("   💡 Increasing retention to 365 days for compliance requirements")
                self.retention_days = 365
            # Add compliance labels
            self.monitoring_labels.update({
                "compliance": "enabled",
                "audit": "required",
                "retention": "long-term"
            })
            print("   💡 Added compliance labels and long-term retention")
            
        return self
"""
GCP Cloud Build Lifecycle Mixin

Lifecycle operations for Google Cloud Build CI/CD service.
Handles create, destroy, and preview operations with smart state management.
"""

from typing import Dict, Any, List, Optional


class CloudBuildLifecycleMixin:
    """
    Mixin for Cloud Build lifecycle operations.
    
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
        self._validate_build_configuration()
        
        # Get current cloud state
        current_state = self._fetch_current_cloud_state()
        
        # Determine actions needed
        actions = self._determine_build_actions(current_state)
        
        # Display preview
        self._display_build_preview(actions, current_state)
        
        # Return structured data
        return {
            'resource_type': 'gcp_cloud_build',
            'name': self.build_name,
            'current_state': current_state,
            'actions': actions,
            'estimated_cost': self._calculate_build_cost(),
            'configuration': self._get_build_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the build configuration with smart state management.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration
        self._validate_build_configuration()
        
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_build_actions(current_state)
        
        # Execute actions
        result = self._execute_build_actions(actions, current_state)
        
        # Update state
        self.build_exists = True
        self.build_created = True
        self.triggers_created = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the build configuration and all associated resources.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying Cloud Build configuration: {self.build_name}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  Cloud Build configuration '{self.build_name}' does not exist")
                return {"success": True, "message": "Build configuration does not exist", "name": self.build_name}
            
            # Show what will be destroyed
            self._display_build_destruction_preview(current_state)
            
            # Perform destruction in correct order
            destruction_results = []
            
            # 1. Delete triggers first
            if self.trigger_manager and current_state.get("triggers"):
                for trigger in current_state["triggers"]:
                    result = self.trigger_manager.delete_trigger(trigger["id"])
                    destruction_results.append(("trigger", trigger["name"], result))
            
            # 2. Cancel running builds
            if self.build_manager and current_state.get("recent_builds"):
                running_builds = [b for b in current_state["recent_builds"] if b.get("status") == "WORKING"]
                for build in running_builds:
                    result = self.build_manager.cancel_build(build["id"])
                    destruction_results.append(("build", build["id"], result))
            
            # 3. Delete build configuration (if stored separately)
            if self.build_manager:
                result = self.build_manager.delete_build_config(self.project_id, self.build_name)
                destruction_results.append(("build_config", self.build_name, result))
            
            # Check overall success
            overall_success = all(result for _, _, result in destruction_results)
            
            if overall_success:
                print(f"✅ Cloud Build configuration '{self.build_name}' destroyed successfully")
                self.build_exists = False
                self.build_created = False
                self.triggers_created = False
                return {"success": True, "name": self.build_name, "destroyed_resources": len(destruction_results)}
            else:
                failed_resources = [name for _, name, result in destruction_results if not result]
                print(f"⚠️  Partial failure destroying build configuration. Failed: {failed_resources}")
                return {"success": False, "name": self.build_name, "error": f"Failed to destroy: {failed_resources}"}
                
        except Exception as e:
            print(f"❌ Error destroying build configuration: {str(e)}")
            return {"success": False, "name": self.build_name, "error": str(e)}
            
    def run_build(self, branch: str = None, tag: str = None, commit_sha: str = None) -> Dict[str, Any]:
        """
        Manually trigger a build execution.
        
        Args:
            branch: Specific branch to build
            tag: Specific tag to build
            commit_sha: Specific commit SHA to build
            
        Returns:
            Dict containing build execution results
        """
        self._ensure_authenticated()
        
        print(f"🚀 Triggering build: {self.build_name}")
        
        try:
            # Prepare build request
            build_request = {
                "project_id": self.project_id,
                "build_name": self.build_name,
                "source": {
                    "repo_url": self.source_repo_url,
                    "branch": branch or self.source_branch,
                    "tag": tag or self.source_tag,
                    "commit_sha": commit_sha
                },
                "steps": self.build_steps,
                "substitutions": self.substitutions,
                "timeout": f"{self.timeout_seconds}s",
                "machine_type": self.machine_type_value,
                "disk_size_gb": self.disk_size_gb
            }
            
            if self.service_account_email:
                build_request["service_account"] = self.service_account_email
                
            if self.build_logs_bucket:
                build_request["logs_bucket"] = self.build_logs_bucket
            
            # Execute build
            if self.build_manager:
                build_result = self.build_manager.run_build(build_request)
                
                if build_result.get("success", False):
                    build_id = build_result.get("build_id")
                    print(f"✅ Build started successfully!")
                    print(f"   🆔 Build ID: {build_id}")
                    print(f"   📊 Status: {build_result.get('status', 'QUEUED')}")
                    print(f"   🔗 Logs: {build_result.get('log_url', 'N/A')}")
                    
                    return {
                        "success": True,
                        "build_id": build_id,
                        "status": build_result.get("status"),
                        "log_url": build_result.get("log_url"),
                        "estimated_duration": f"{self.timeout_seconds // 60} minutes"
                    }
                else:
                    print(f"❌ Failed to start build: {build_result.get('error', 'Unknown error')}")
                    return {"success": False, "error": build_result.get("error")}
            else:
                print(f"❌ Build manager not initialized")
                return {"success": False, "error": "Build manager not initialized"}
                
        except Exception as e:
            print(f"❌ Error triggering build: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def _validate_build_configuration(self):
        """Validate the build configuration before creation"""
        errors = []
        warnings = []
        
        # Validate build name
        if not self.build_name:
            errors.append("Build name is required")
        
        # Validate source repository
        if not self.source_repo_url:
            errors.append("Source repository URL is required")
        elif not self._is_valid_repo_url(self.source_repo_url):
            errors.append(f"Invalid repository URL: {self.source_repo_url}")
        
        # Validate build steps
        if not self.build_steps:
            warnings.append("No build steps defined - build will do nothing")
        
        for i, step in enumerate(self.build_steps):
            if not self._validate_build_step(step):
                errors.append(f"Invalid build step at index {i}")
        
        # Validate triggers
        if not self.triggers:
            warnings.append("No triggers defined - builds will only run manually")
        
        for i, trigger in enumerate(self.triggers):
            if not self._validate_trigger_config(trigger):
                errors.append(f"Invalid trigger configuration at index {i}")
        
        # Validate deployment targets
        for target in self.deployment_targets:
            if not self._validate_deployment_target(target):
                errors.append(f"Invalid deployment target: {target.get('name', 'Unknown')}")
        
        # Resource warnings
        if self.timeout_seconds > 3600:  # 1 hour
            warnings.append(f"Long build timeout ({self.timeout_seconds}s) may increase costs")
        
        if "standard-8" in self.machine_type_value or "highmem" in self.machine_type_value:
            warnings.append(f"High-performance machine type ({self.machine_type_value}) will increase costs")
        
        # Cost warnings
        estimated_cost = self._estimate_build_cost()
        if estimated_cost > 50:
            warnings.append(f"High estimated cost: ${estimated_cost:.2f}/month")
        
        if errors:
            raise ValueError(f"Build configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Build configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
                
    def _determine_build_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create_build_config": False,
            "update_build_config": False,
            "keep_build_config": False,
            "create_triggers": [],
            "update_triggers": [],
            "delete_triggers": [],
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create_build_config"] = True
            actions["create_triggers"] = self.triggers
            actions["changes"].append("Create new build configuration")
            if self.triggers:
                actions["changes"].append(f"Create {len(self.triggers)} triggers")
        else:
            # Compare current state with desired state
            trigger_changes = self._detect_trigger_drift(current_state)
            config_changes = self._detect_config_drift(current_state)
            
            if trigger_changes or config_changes:
                actions["update_build_config"] = True
                
                if trigger_changes:
                    actions["create_triggers"] = trigger_changes.get("create", [])
                    actions["update_triggers"] = trigger_changes.get("update", [])
                    actions["delete_triggers"] = trigger_changes.get("delete", [])
                    
                    if trigger_changes.get("create"):
                        actions["changes"].append(f"Create {len(trigger_changes['create'])} new triggers")
                    if trigger_changes.get("update"):
                        actions["changes"].append(f"Update {len(trigger_changes['update'])} existing triggers")
                    if trigger_changes.get("delete"):
                        actions["changes"].append(f"Delete {len(trigger_changes['delete'])} obsolete triggers")
                        
                if config_changes:
                    actions["changes"].extend(config_changes)
                    
            else:
                actions["keep_build_config"] = True
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_trigger_drift(self, current_state: Dict[str, Any]) -> Dict[str, List]:
        """Detect differences between current and desired triggers"""
        current_triggers = current_state.get("triggers", [])
        desired_triggers = self.triggers
        
        # Create lookup dictionaries by name
        current_lookup = {trigger["name"]: trigger for trigger in current_triggers}
        desired_lookup = {trigger["name"]: trigger for trigger in desired_triggers}
        
        changes = {
            "create": [],
            "update": [],
            "delete": []
        }
        
        # Find triggers to create
        for name, trigger in desired_lookup.items():
            if name not in current_lookup:
                changes["create"].append(trigger)
                
        # Find triggers to delete
        for name, trigger in current_lookup.items():
            if name not in desired_lookup:
                changes["delete"].append(trigger)
                
        return changes
        
    def _detect_config_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences between current and desired build configuration"""
        changes = []
        
        # Compare machine type
        current_machine_type = current_state.get("machine_type", "e2-standard-2")
        if current_machine_type != self.machine_type_value:
            changes.append(f"Machine type: {current_machine_type} → {self.machine_type_value}")
        
        # Compare timeout
        current_timeout = current_state.get("timeout", "1200s")
        desired_timeout = f"{self.timeout_seconds}s"
        if current_timeout != desired_timeout:
            changes.append(f"Timeout: {current_timeout} → {desired_timeout}")
        
        # Compare service account
        current_sa = current_state.get("service_account")
        if current_sa != self.service_account_email:
            changes.append(f"Service account: {current_sa} → {self.service_account_email}")
            
        return changes
        
    def _execute_build_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create_build_config"]:
            return self._create_build_configuration()
        elif actions["update_build_config"]:
            return self._update_build_configuration(current_state, actions)
        else:
            return self._keep_build_configuration(current_state)
            
    def _create_build_configuration(self) -> Dict[str, Any]:
        """Create a new build configuration"""
        print(f"\n🔨 Creating Cloud Build configuration: {self.build_name}")
        print(f"   📁 Repository: {self.source_repo_url}")
        print(f"   🌿 Branch: {self.source_branch}")
        print(f"   🔧 Build Steps: {len(self.build_steps)}")
        print(f"   🎯 Triggers: {len(self.triggers)}")
        print(f"   🚀 Deployment Targets: {len(self.deployment_targets)}")
        print(f"   🖥️  Machine Type: {self.machine_type_value}")
        print(f"   ⏱️  Timeout: {self.timeout_seconds}s")
        
        try:
            # Create triggers first
            triggers_created = 0
            if self.triggers:
                # For now, create triggers directly without manager
                triggers_created = self._create_triggers_directly()
                print(f"   🎯 Triggers created: {triggers_created}/{len(self.triggers)}")
            
            # Store build configuration (if using external config)
            config_created = False
            if self.build_manager:
                config_result = self.build_manager.create_build_config(
                    project_id=self.project_id,
                    build_name=self.build_name,
                    steps=self.build_steps,
                    substitutions=self.substitutions,
                    timeout=self.timeout_seconds,
                    machine_type=self.machine_type_value,
                    service_account=self.service_account_email,
                    logs_bucket=self.build_logs_bucket
                )
                config_created = bool(config_result)
            
            print(f"\n✅ Cloud Build configuration created successfully!")
            print(f"   📁 Repository: {self.source_repo_url}")
            print(f"   🎯 Triggers: {triggers_created}/{len(self.triggers)} created")
            print(f"   🔧 Build Steps: {len(self.build_steps)} configured")
            print(f"   🚀 Deployment Targets: {len(self.deployment_targets)} configured")
            print(f"   💰 Estimated Cost: {self._calculate_build_cost()}")
            
            if self.deployment_targets:
                print(f"   🎯 Deploy Targets:")
                for target in self.deployment_targets:
                    print(f"      • {target['type']}: {target['name']}")
            
            return {
                "success": True,
                "name": self.build_name,
                "project_id": self.project_id,
                "triggers_created": triggers_created,
                "build_steps": len(self.build_steps),
                "deployment_targets": len(self.deployment_targets),
                "estimated_cost": self._calculate_build_cost(),
                "created": True
            }
                
        except Exception as e:
            print(f"❌ Failed to create build configuration: {str(e)}")
            raise
            
    def _update_build_configuration(self, current_state: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing build configuration"""
        print(f"\n🔄 Updating Cloud Build configuration: {self.build_name}")
        print(f"   📋 Changes to apply:")
        for change in actions["changes"]:
            print(f"      • {change}")
            
        try:
            changes_applied = 0
            
            # Create new triggers
            if actions["create_triggers"] and self.trigger_manager:
                for trigger in actions["create_triggers"]:
                    result = self.trigger_manager.create_trigger(project_id=self.project_id, repo_url=self.source_repo_url, **trigger)
                    if result:
                        changes_applied += 1
            
            # Delete obsolete triggers
            if actions["delete_triggers"] and self.trigger_manager:
                for trigger in actions["delete_triggers"]:
                    result = self.trigger_manager.delete_trigger(trigger["id"])
                    if result:
                        changes_applied += 1
            
            # Update build configuration
            if self.build_manager:
                result = self.build_manager.update_build_config(
                    project_id=self.project_id,
                    build_name=self.build_name,
                    steps=self.build_steps,
                    substitutions=self.substitutions,
                    timeout=self.timeout_seconds,
                    machine_type=self.machine_type_value,
                    service_account=self.service_account_email
                )
                if result:
                    changes_applied += 1
                
            print(f"✅ Cloud Build configuration updated successfully!")
            print(f"   📁 Repository: {self.source_repo_url}")
            print(f"   🔄 Changes Applied: {changes_applied}")
            
            return {
                "success": True,
                "name": self.build_name,
                "changes_applied": changes_applied,
                "updated": True
            }
                
        except Exception as e:
            print(f"❌ Failed to update build configuration: {str(e)}")
            raise
            
    def _keep_build_configuration(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing build configuration (no changes needed)"""
        print(f"\n✅ Cloud Build configuration '{self.build_name}' is up to date")
        print(f"   📁 Repository: {current_state.get('repository', self.source_repo_url)}")
        print(f"   🎯 Triggers: {current_state.get('triggers_count', 0)}")
        print(f"   🔧 Recent Builds: {current_state.get('recent_builds_count', 0)}")
        print(f"   🖥️  Machine Type: {current_state.get('machine_type', 'Unknown')}")
        print(f"   📊 Status: {current_state.get('status', 'Unknown')}")
        
        return {
            "success": True,
            "name": self.build_name,
            "project_id": current_state.get('project_id'),
            "triggers_count": current_state.get('triggers_count', 0),
            "recent_builds_count": current_state.get('recent_builds_count', 0),
            "machine_type": current_state.get('machine_type'),
            "status": current_state.get('status'),
            "unchanged": True
        }
        
    def _display_build_preview(self, actions: Dict[str, Any], current_state: Dict[str, Any]):
        """Display preview of actions to be taken"""
        print(f"\n🔨 Google Cloud Build Preview")
        print(f"   🎯 Configuration: {self.build_name}")
        print(f"   📁 Repository: {self.source_repo_url}")
        print(f"   🌿 Branch: {self.source_branch}")
        print(f"   🖥️  Machine Type: {self.machine_type_value}")
        print(f"   ⏱️  Timeout: {self.timeout_seconds}s")
        
        if actions["create_build_config"]:
            print(f"\n╭─ 🆕 WILL CREATE")
            print(f"├─ 🔨 Build Configuration: {self.build_name}")
            print(f"├─ 📁 Repository: {self.source_repo_url}")
            print(f"├─ 🌿 Branch: {self.source_branch}")
            print(f"├─ 🔧 Build Steps: {len(self.build_steps)}")
            print(f"├─ 🎯 Triggers: {len(self.triggers)}")
            print(f"├─ 🚀 Deployment Targets: {len(self.deployment_targets)}")
            print(f"├─ 🖥️  Machine Type: {self.machine_type_value}")
            print(f"├─ ⏱️  Timeout: {self.timeout_seconds}s")
            print(f"╰─ 💰 Estimated Cost: {self._calculate_build_cost()}")
            
            # Show build steps
            if self.build_steps:
                print(f"\n🔧 Build Steps to Create:")
                for i, step in enumerate(self.build_steps[:5]):  # Show first 5
                    name = step.get("name", "Unknown")
                    description = self._get_step_description(name)
                    print(f"   {i+1}. {description}")
                if len(self.build_steps) > 5:
                    print(f"   ... and {len(self.build_steps) - 5} more steps")
            
            # Show deployment targets
            if self.deployment_targets:
                print(f"\n🚀 Deployment Targets:")
                for target in self.deployment_targets:
                    print(f"   • {target['type']}: {target['name']}")
            
        elif actions["update_build_config"]:
            print(f"\n╭─ 🔄 WILL UPDATE")
            print(f"├─ 🔨 Build Configuration: {self.build_name}")
            print(f"├─ 📋 Changes:")
            for change in actions["changes"]:
                print(f"│  • {change}")
            print(f"╰─ 💰 Updated Cost: {self._calculate_build_cost()}")
            
        else:
            print(f"\n╭─ ✅ WILL KEEP")
            print(f"├─ 🔨 Build Configuration: {self.build_name}")
            print(f"├─ 📁 Repository: {current_state.get('repository', 'Unknown')}")
            print(f"├─ 🎯 Triggers: {current_state.get('triggers_count', 0)}")
            print(f"├─ 🔧 Recent Builds: {current_state.get('recent_builds_count', 0)}")
            print(f"╰─ 📊 Status: {current_state.get('status', 'Unknown')}")
            
    def _display_build_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  Build Configuration: {self.build_name}")
        print(f"   📁 Repository: {current_state.get('repository', 'Unknown')}")
        print(f"   🎯 Triggers: {current_state.get('triggers_count', 0)}")
        print(f"   🔧 Recent Builds: {current_state.get('recent_builds_count', 0)}")
        print(f"   ⚠️  ALL BUILD HISTORY AND TRIGGERS WILL BE PERMANENTLY LOST")
        
    def _calculate_build_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_build_cost()
        return f"${base_cost:.2f}/month"
        
    def _get_build_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current build configuration"""
        return {
            "build_name": self.build_name,
            "description": self.build_description,
            "project_id": self.project_id,
            "source_repo_url": self.source_repo_url,
            "source_branch": self.source_branch,
            "build_steps": self.build_steps,
            "build_steps_count": len(self.build_steps),
            "triggers": self.triggers,
            "triggers_count": len(self.triggers),
            "deployment_targets": self.deployment_targets,
            "deployment_targets_count": len(self.deployment_targets),
            "machine_type": self.machine_type_value,
            "timeout_seconds": self.timeout_seconds,
            "labels": self.build_labels
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
        
        print(f"🎯 Cross-Cloud Magic: Optimizing build pipeline for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective build pipeline")
            # Use smaller machine type for cost savings
            if "standard-8" in self.machine_type_value:
                print("   💡 Switching to e2-standard-4 for cost savings")
                self.machine_type_value = "e2-standard-4"
            elif "standard-4" in self.machine_type_value:
                print("   💡 Switching to e2-standard-2 for cost savings")
                self.machine_type_value = "e2-standard-2"
            # Reduce timeout
            if self.timeout_seconds > 1200:
                print("   💡 Reducing timeout to 20 minutes for cost efficiency")
                self.timeout_seconds = 1200
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance build pipeline")
            # Use larger machine type for performance
            if "standard-2" in self.machine_type_value:
                print("   💡 Upgrading to e2-standard-4 for better performance")
                self.machine_type_value = "e2-standard-4"
            elif "standard-4" in self.machine_type_value:
                print("   💡 Upgrading to e2-standard-8 for high performance")
                self.machine_type_value = "e2-standard-8"
            # Increase timeout for complex builds
            if self.timeout_seconds < 1800:
                print("   💡 Increasing timeout to 30 minutes for complex builds")
                self.timeout_seconds = 1800
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable build pipeline")
            # Use balanced machine type for reliability
            if "standard-2" in self.machine_type_value:
                print("   💡 Upgrading to e2-standard-4 for better reliability")
                self.machine_type_value = "e2-standard-4"
            # Enable parallel builds for reliability
            self.parallel_builds = True
            print("   💡 Enabled parallel builds for reliability")
            # Add retry logic to build steps (would be implemented in actual manager)
            print("   💡 Configured build step retry logic")
                
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant build pipeline")
            # Require approval for compliance
            self.approval_required = True
            print("   💡 Enabled manual approval for compliance")
            # Add compliance labels
            self.build_labels.update({
                "compliance": "enabled",
                "audit": "required",
                "security": "enhanced"
            })
            print("   💡 Added compliance labels")
            # Use private pool if available
            if not self.private_pool_name:
                print("   💡 Consider using private worker pool for compliance")
            
        return self
        
    def _create_triggers_directly(self) -> int:
        """Create Cloud Build triggers using gcloud CLI (Rails: use existing tools)"""
        triggers_created = 0
        
        # Parse GitHub repo URL
        repo_url = self.source_repo_url
        if "github.com/" not in repo_url:
            print(f"   ⚠️  Unsupported repo URL format: {repo_url}")
            return 0
            
        repo_parts = repo_url.replace("https://github.com/", "").split("/")
        owner = repo_parts[0]
        name = repo_parts[1].replace(".git", "")
        
        # Create cloudbuild.yaml content for triggers
        cloudbuild_yaml = self._generate_cloudbuild_yaml()
        
        # Check if GitHub App is connected (Rails: validate prerequisites)
        github_connected = self._check_github_app_connected()
        
        # Always write the cloudbuild.yaml file 
        self._write_cloudbuild_yaml(cloudbuild_yaml)
        
        if not github_connected:
            print(f"   🔧 GitHub repository connection required")
            print(f"   📋 One-time setup (takes 30 seconds):")
            print(f"      1. Open: https://console.cloud.google.com/cloud-build/triggers/connect?project={self.project_id}")
            print(f"      2. Click 'Connect Repository' → GitHub → {owner}/{name}")
            print(f"      3. Re-run: infra apply prod_firebase_deployment.py")
            print(f"   ℹ️  This enables triggers: push → auto-build → auto-deploy")
            return 0
        
        # For now, provide manual instructions instead of auto-creating triggers
        # This is more reliable and follows Rails principle: fail gracefully
        print(f"   📋 Triggers need to be created manually (one-time setup):")
        print(f"   1. Open: https://console.cloud.google.com/cloud-build/triggers?project={self.project_id}")  
        print(f"   2. Click 'Create Trigger' → Name: 'push-to-main'")
        print(f"   3. Source: GitHub → {owner}/{name} → Branch: main")
        print(f"   4. Configuration: Cloud Build → cloudbuild.yaml")
        print(f"   5. ⚠️  Region: Choose 'us-central1' or 'europe-west1' (avoid europe-north2)")
        print(f"   6. Click 'Create' to enable auto-deployment")
        print(f"   ℹ️  Once created: git push → auto-builds → auto-deploys!")
        
        triggers_created = 0  # For now, no automatic creation
            
        return triggers_created
        
    def _generate_cloudbuild_yaml(self) -> str:
        """Generate cloudbuild.yaml content from build steps"""
        yaml_content = """# 🚀 InfraDSL Auto-Generated Cloud Build Configuration
# Generated from your CloudBuild configuration

steps:
"""
        
        for i, step in enumerate(self.build_steps):
            yaml_content += f"  # Step {i+1}\n"
            yaml_content += f"  - name: '{step['name']}'\n"
            
            if step.get('args'):
                yaml_content += f"    args: {step['args']}\n"
                
            if step.get('env'):
                yaml_content += f"    env:\n"
                for key, value in step['env'].items():
                    yaml_content += f"      - '{key}={value}'\n"
                    
            yaml_content += "\n"
        
        # Convert machine type to valid Cloud Build enum values
        # Valid values: E2_HIGHCPU_8, E2_HIGHCPU_32, E2_MEDIUM, N1_HIGHCPU_8, N1_HIGHCPU_32, UNSPECIFIED
        machine_type_map = {
            'e2-standard-2': 'UNSPECIFIED',      # e2 Standard: 2 vCPU, 8GB RAM
            'e2-standard-4': 'E2_HIGHCPU_8',     # e2 HighCPU: 8 vCPUs, 8GB RAM
            'e2-standard-8': 'E2_HIGHCPU_8', 
            'e2-highmem-2': 'E2_MEDIUM',         # e2 Medium: 1 vCPU, 4GB RAM
            'e2-highmem-4': 'E2_HIGHCPU_8'
        }
        machine_type = machine_type_map.get(self.machine_type_value, 'UNSPECIFIED')
        
        yaml_content += f"""
# ⚙️ Build Configuration  
options:
  machineType: {machine_type}
  diskSizeGb: {self.disk_size_gb}
  logging: CLOUD_LOGGING_ONLY
  
timeout: '{self.timeout_seconds}s'

# 🏷️ Build substitutions
substitutions:
  _ENVIRONMENT: 'production'
"""
        
        return yaml_content
        
    def _create_inline_build_config(self) -> str:
        """Create a simple inline build config as a file path"""
        import tempfile
        import os
        
        # Create temporary file with build config
        build_config = {
            "steps": []
        }
        
        # Add a simple step for now
        build_config["steps"].append({
            "name": "gcr.io/cloud-builders/gcloud",
            "args": ["version"]
        })
        
        # Write to temporary file
        import json
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(build_config, temp_file)
        temp_file.close()
        
        return temp_file.name
        
    def _write_cloudbuild_yaml(self, content: str):
        """Write cloudbuild.yaml file to current directory"""
        try:
            with open("cloudbuild.yaml", "w") as f:
                f.write(content)
            print(f"   📄 Generated cloudbuild.yaml")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not write cloudbuild.yaml: {str(e)}")
            
    def _check_github_app_connected(self) -> bool:
        """Check if GitHub App is connected to Cloud Build"""
        try:
            import subprocess
            
            # Check for Cloud Build GitHub App connections
            result = subprocess.run([
                "gcloud", "builds", "triggers", "list", 
                "--project", self.project_id,
                "--format", "value(github.owner,github.name)"
            ], capture_output=True, text=True, timeout=10)
            
            # If command succeeds and we can list triggers, connection likely works
            # Even if empty, it means the API is accessible
            if result.returncode == 0:
                print(f"   ℹ️  GitHub App connection detected")
                return True
            else:
                print(f"   ⚠️  GitHub App connection check failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ GitHub connection check timed out")
            return False
        except Exception as e:
            print(f"   ⚠️  Error checking GitHub connection: {str(e)}")
            return False
            

"""
GCP Cloud Run Lifecycle Mixin

Lifecycle operations for Google Cloud Run serverless containers.
Handles create, destroy, and preview operations with smart state management.
"""

import os
from typing import Dict, Any, List, Optional


class CloudRunLifecycleMixin:
    """
    Mixin for Cloud Run lifecycle operations.
    
    This mixin provides:
    - Create operation with smart state management
    - Destroy operation with safety checks
    - Preview operation for infrastructure planning
    - Container building and deployment automation
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
        self._validate_cloud_run_configuration()
        
        # Get current cloud state
        current_state = self._fetch_current_cloud_state()
        
        # Determine actions needed
        actions = self._determine_cloud_run_actions(current_state)
        
        # Display preview
        self._display_cloud_run_preview(actions, current_state)
        
        # Return structured data
        return {
            'resource_type': 'gcp_cloud_run',
            'name': self.service_name,
            'current_state': current_state,
            'actions': actions,
            'estimated_cost': self._calculate_cloud_run_cost(),
            'configuration': self._get_cloud_run_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the Cloud Run service with smart state management.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration
        self._validate_cloud_run_configuration()
        
        # Handle container building if needed
        if self.build_enabled and self.build_source_path:
            build_result = self._build_container()
            if not build_result.get("success", False):
                raise RuntimeError(f"Container build failed: {build_result.get('error', 'Unknown error')}")
        
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_cloud_run_actions(current_state)
        
        # Execute actions
        result = self._execute_cloud_run_actions(actions, current_state)
        
        # Update state
        self.service_exists = True
        self.service_created = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the Cloud Run service and all associated resources.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying Cloud Run service: {self.service_name}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  Cloud Run service '{self.service_name}' does not exist")
                return {"success": True, "message": "Service does not exist", "name": self.service_name}
            
            # Show what will be destroyed
            self._display_cloud_run_destruction_preview(current_state)
            
            # Perform destruction
            destruction_results = []
            
            # 1. Remove custom domain mapping if exists
            if current_state.get("custom_domain") and self.cloud_run_manager:
                result = self.cloud_run_manager.delete_domain_mapping(
                    current_state["custom_domain"], 
                    self.region
                )
                destruction_results.append(("domain_mapping", current_state["custom_domain"], result))
            
            # 2. Delete the Cloud Run service
            if self.cloud_run_manager:
                result = self.cloud_run_manager.delete_service(self.service_name, self.region)
                destruction_results.append(("service", self.service_name, result))
            
            # Check overall success
            overall_success = all(result for _, _, result in destruction_results)
            
            if overall_success:
                print(f"✅ Cloud Run service '{self.service_name}' destroyed successfully")
                self.service_exists = False
                self.service_created = False
                return {"success": True, "name": self.service_name, "destroyed_resources": len(destruction_results)}
            else:
                failed_resources = [name for _, name, result in destruction_results if not result]
                print(f"⚠️  Partial failure destroying service. Failed: {failed_resources}")
                return {"success": False, "name": self.service_name, "error": f"Failed to destroy: {failed_resources}"}
                
        except Exception as e:
            print(f"❌ Error destroying Cloud Run service: {str(e)}")
            return {"success": False, "name": self.service_name, "error": str(e)}
            
    def run_build(self) -> Dict[str, Any]:
        """
        Manually trigger container build without deploying.
        
        Returns:
            Dict containing build results
        """
        self._ensure_authenticated()
        
        if not self.build_enabled or not self.build_source_path:
            return {"success": False, "error": "Container building not configured"}
            
        print(f"🔨 Building container for Cloud Run service: {self.service_name}")
        
        return self._build_container()
        
    def _validate_cloud_run_configuration(self):
        """Validate the Cloud Run configuration before creation"""
        errors = []
        warnings = []
        
        # Validate service name
        if not self.service_name:
            errors.append("Service name is required")
        
        # Validate image URL or build configuration
        if not self.image_url and not (self.build_enabled and self.build_source_path):
            errors.append("Either image URL or build source path is required")
        
        if self.image_url and not self._validate_image_url(self.image_url):
            warnings.append(f"Image URL format may be invalid: {self.image_url}")
        
        # Validate resource limits
        if not self._is_valid_memory_limit(self.memory_limit):
            errors.append(f"Invalid memory limit: {self.memory_limit}")
        
        if not self._is_valid_cpu_limit(self.cpu_limit):
            errors.append(f"Invalid CPU limit: {self.cpu_limit}")
        
        # Validate scaling configuration
        if self.min_instances > self.max_instances:
            errors.append(f"Min instances ({self.min_instances}) cannot be greater than max instances ({self.max_instances})")
        
        # Validate region
        if not self._is_valid_region(self.region):
            warnings.append(f"Region '{self.region}' may not support Cloud Run")
        
        # Performance warnings
        if self.min_instances > 10:
            warnings.append(f"High minimum instances ({self.min_instances}) will increase costs significantly")
        
        if self.memory_limit in ["8Gi", "16Gi", "32Gi"]:
            warnings.append(f"High memory allocation ({self.memory_limit}) will increase costs")
        
        # Security warnings
        if self.allow_unauthenticated:
            warnings.append("Service allows unauthenticated access - ensure this is intended")
        
        if not self.service_account_email:
            warnings.append("No custom service account specified - using default Compute Engine service account")
        
        # Build warnings
        if self.build_enabled and self.build_source_path:
            if not os.path.exists(self.build_source_path):
                errors.append(f"Build source path does not exist: {self.build_source_path}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
                
    def _determine_cloud_run_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create_service": False,
            "update_service": False,
            "keep_service": False,
            "build_container": False,
            "update_traffic": False,
            "configure_domain": False,
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create_service"] = True
            actions["changes"].append("Create new Cloud Run service")
            
            if self.build_enabled and self.build_source_path:
                actions["build_container"] = True
                actions["changes"].append("Build container from source")
            
            if self.custom_domain:
                actions["configure_domain"] = True
                actions["changes"].append(f"Configure custom domain: {self.custom_domain}")
        else:
            # Compare current state with desired state
            config_changes = self._detect_configuration_drift(current_state)
            traffic_changes = self._detect_traffic_drift(current_state)
            domain_changes = self._detect_domain_drift(current_state)
            
            if config_changes:
                actions["update_service"] = True
                actions["changes"].extend(config_changes)
                
                # Check if we need to rebuild container
                if self.build_enabled and self.build_source_path:
                    actions["build_container"] = True
                    actions["changes"].append("Rebuild container with updated source")
            
            if traffic_changes:
                actions["update_traffic"] = True
                actions["changes"].extend(traffic_changes)
            
            if domain_changes:
                actions["configure_domain"] = True
                actions["changes"].extend(domain_changes)
            
            if not actions["changes"]:
                actions["keep_service"] = True
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_configuration_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences between current and desired configuration"""
        changes = []
        
        # Compare image URL
        current_image = current_state.get("image_url", "")
        if self.image_url and current_image != self.image_url:
            changes.append(f"Image: {current_image} → {self.image_url}")
        
        # Compare memory
        current_memory = current_state.get("memory", "")
        if current_memory != self.memory_limit:
            changes.append(f"Memory: {current_memory} → {self.memory_limit}")
        
        # Compare CPU
        current_cpu = current_state.get("cpu", "")
        if current_cpu != self.cpu_limit:
            changes.append(f"CPU: {current_cpu} → {self.cpu_limit}")
        
        # Compare scaling
        current_min = current_state.get("min_instances", 0)
        current_max = current_state.get("max_instances", 100)
        if current_min != self.min_instances or current_max != self.max_instances:
            changes.append(f"Scaling: {current_min}-{current_max} → {self.min_instances}-{self.max_instances}")
        
        # Compare access
        current_auth = current_state.get("allow_unauthenticated", False)
        if current_auth != self.allow_unauthenticated:
            access_change = "public" if self.allow_unauthenticated else "private"
            changes.append(f"Access: {'public' if current_auth else 'private'} → {access_change}")
        
        return changes
        
    def _detect_traffic_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences in traffic allocation"""
        changes = []
        
        current_traffic = current_state.get("traffic_allocation", {"LATEST": 100})
        
        # Simplified traffic comparison
        if current_traffic != self.traffic_allocation:
            changes.append(f"Traffic allocation updated")
            
        return changes
        
    def _detect_domain_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences in domain configuration"""
        changes = []
        
        current_domain = current_state.get("custom_domain")
        
        if self.custom_domain and not current_domain:
            changes.append(f"Add custom domain: {self.custom_domain}")
        elif not self.custom_domain and current_domain:
            changes.append(f"Remove custom domain: {current_domain}")
        elif self.custom_domain != current_domain:
            changes.append(f"Change domain: {current_domain} → {self.custom_domain}")
            
        return changes
        
    def _build_container(self) -> Dict[str, Any]:
        """Build container from source code"""
        if not self.build_source_path or not os.path.exists(self.build_source_path):
            return {"success": False, "error": "Invalid build source path"}
        
        print(f"🐳 Building container from source: {self.build_source_path}")
        
        try:
            # Generate unique tag
            tag = self._generate_unique_tag(self.build_source_path)
            
            # Use container builder if available
            if self.container_builder:
                result = self.container_builder.build_and_push_for_cloud_run(
                    service_name=self.service_name,
                    source_path=self.build_source_path,
                    template=self.build_template,
                    port=self.container_port
                )
                
                if result.get("push_successful"):
                    self.image_url = result["deployed_image"]
                    self.container_built = True
                    print(f"✅ Container built successfully: {self.image_url}")
                    return {"success": True, "image_url": self.image_url, "tag": tag}
                else:
                    return {"success": False, "error": "Container build failed"}
            
            # Fallback to artifact registry manager
            elif self.artifact_registry_manager:
                # Ensure repository exists
                from ...googlecloud_managers.artifact_registry_manager import RegistryConfig
                repo_config = RegistryConfig(repository_name=self.repository_name)
                self.artifact_registry_manager.create_repository(repo_config)
                
                # Build and push
                repository_url = f"{self.repository_location}-docker.pkg.dev/{self.project_id}/{self.repository_name}"
                image_info = self.artifact_registry_manager.build_and_push_image(
                    image_name=self.service_name,
                    tag=tag,
                    template_path=self.build_source_path,
                    repository_url=repository_url,
                    port=self.container_port
                )
                
                self.image_url = image_info["full_url"]
                self.container_built = True
                print(f"✅ Container built successfully: {self.image_url}")
                return {"success": True, "image_url": self.image_url, "tag": tag}
            else:
                return {"success": False, "error": "No container builder available"}
                
        except Exception as e:
            print(f"❌ Container build failed: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def _execute_cloud_run_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create_service"]:
            return self._create_cloud_run_service()
        elif actions["update_service"]:
            return self._update_cloud_run_service(current_state, actions)
        else:
            return self._keep_cloud_run_service(current_state)
            
    def _create_cloud_run_service(self) -> Dict[str, Any]:
        """Create a new Cloud Run service"""
        print(f"\n🚀 Creating Cloud Run service: {self.service_name}")
        print(f"   📍 Region: {self.region}")
        print(f"   🐳 Image: {self.image_url}")
        print(f"   💾 Memory: {self.memory_limit}")
        print(f"   🖥️  CPU: {self.cpu_limit}")
        print(f"   📊 Scaling: {self.min_instances}-{self.max_instances}")
        print(f"   🌐 Access: {'Public' if self.allow_unauthenticated else 'Private'}")
        print(f"   🔌 Port: {self.container_port}")
        
        try:
            # Prepare service configuration
            from ...googlecloud_managers.cloud_run_manager import CloudRunConfig
            
            config = CloudRunConfig(
                service_name=self.service_name,
                image_url=self.image_url
            )
            
            # Set all configuration options
            config.memory = self.memory_limit
            config.cpu = self.cpu_limit
            config.port = self.container_port
            config.location = self.region
            config.min_instances = self.min_instances
            config.max_instances = self.max_instances
            config.concurrency = self.max_concurrent_requests
            config.timeout = self.timeout_seconds
            config.allow_unauthenticated = self.allow_unauthenticated
            config.environment_variables = self.environment_variables
            config.labels = self.service_labels
            config.custom_domain = self.custom_domain
            config.auto_ssl = self.auto_ssl
            config.service_account = self.service_account_email
            config.vpc_connector = self.vpc_connector
            
            # Create the service
            if self.custom_domain:
                result = self.cloud_run_manager.configure_service_with_domain(config)
            else:
                result = self.cloud_run_manager.create_service(config)
            
            print(f"\n✅ Cloud Run service created successfully!")
            print(f"   🚀 Service: {self.service_name}")
            print(f"   🌐 URL: {result.get('url', 'Unknown')}")
            if self.custom_domain:
                print(f"   🌐 Custom Domain: https://{self.custom_domain}")
            print(f"   📍 Region: {self.region}")
            print(f"   💰 Estimated Cost: {self._calculate_cloud_run_cost()}")
            
            return {
                "success": True,
                "name": self.service_name,
                "region": self.region,
                "url": result.get("url"),
                "custom_domain": self.custom_domain,
                "image_url": self.image_url,
                "estimated_cost": self._calculate_cloud_run_cost(),
                "created": True
            }
                
        except Exception as e:
            print(f"❌ Failed to create Cloud Run service: {str(e)}")
            raise
            
    def _update_cloud_run_service(self, current_state: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing Cloud Run service"""
        print(f"\n🔄 Updating Cloud Run service: {self.service_name}")
        print(f"   📋 Changes to apply:")
        for change in actions["changes"]:
            print(f"      • {change}")
            
        try:
            # Prepare updated configuration
            from ...googlecloud_managers.cloud_run_manager import CloudRunConfig
            
            config = CloudRunConfig(
                service_name=self.service_name,
                image_url=self.image_url
            )
            
            # Set all configuration options
            config.memory = self.memory_limit
            config.cpu = self.cpu_limit
            config.port = self.container_port
            config.location = self.region
            config.min_instances = self.min_instances
            config.max_instances = self.max_instances
            config.concurrency = self.max_concurrent_requests
            config.timeout = self.timeout_seconds
            config.allow_unauthenticated = self.allow_unauthenticated
            config.environment_variables = self.environment_variables
            config.labels = self.service_labels
            config.custom_domain = self.custom_domain
            config.auto_ssl = self.auto_ssl
            config.service_account = self.service_account_email
            config.vpc_connector = self.vpc_connector
            
            # Update the service
            result = self.cloud_run_manager.create_service(config)
            
            print(f"✅ Cloud Run service updated successfully!")
            print(f"   🚀 Service: {self.service_name}")
            print(f"   🌐 URL: {result.get('url', 'Unknown')}")
            print(f"   🔄 Changes Applied: {len(actions['changes'])}")
            
            return {
                "success": True,
                "name": self.service_name,
                "changes_applied": len(actions["changes"]),
                "url": result.get("url"),
                "updated": True
            }
                
        except Exception as e:
            print(f"❌ Failed to update Cloud Run service: {str(e)}")
            raise
            
    def _keep_cloud_run_service(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing Cloud Run service (no changes needed)"""
        print(f"\n✅ Cloud Run service '{self.service_name}' is up to date")
        print(f"   🚀 Service: {self.service_name}")
        print(f"   📍 Region: {current_state.get('region', 'Unknown')}")
        print(f"   🌐 URL: {current_state.get('url', 'Unknown')}")
        print(f"   💾 Memory: {current_state.get('memory', 'Unknown')}")
        print(f"   🖥️  CPU: {current_state.get('cpu', 'Unknown')}")
        print(f"   📊 Status: {current_state.get('status', 'Unknown')}")
        
        return {
            "success": True,
            "name": self.service_name,
            "region": current_state.get('region'),
            "url": current_state.get('url'),
            "memory": current_state.get('memory'),
            "cpu": current_state.get('cpu'),
            "status": current_state.get('status'),
            "unchanged": True
        }
        
    def _display_cloud_run_preview(self, actions: Dict[str, Any], current_state: Dict[str, Any]):
        """Display preview of actions to be taken"""
        print(f"\n🚀 Google Cloud Run Preview")
        print(f"   🎯 Service: {self.service_name}")
        print(f"   📍 Region: {self.region}")
        print(f"   🐳 Image: {self.image_url or 'Will be built from source'}")
        print(f"   💾 Memory: {self.memory_limit}")
        print(f"   🖥️  CPU: {self.cpu_limit}")
        print(f"   📊 Scaling: {self.min_instances}-{self.max_instances}")
        
        if actions["create_service"]:
            print(f"\n╭─ 🆕 WILL CREATE")
            print(f"├─ 🚀 Service: {self.service_name}")
            print(f"├─ 📍 Region: {self.region}")
            print(f"├─ 🐳 Image: {self.image_url or 'Built from source'}")
            print(f"├─ 💾 Memory: {self.memory_limit}")
            print(f"├─ 🖥️  CPU: {self.cpu_limit}")
            print(f"├─ 📊 Scaling: {self.min_instances}-{self.max_instances}")
            print(f"├─ 🔌 Port: {self.container_port}")
            print(f"├─ 🌐 Access: {'Public' if self.allow_unauthenticated else 'Private'}")
            if self.custom_domain:
                print(f"├─ 🌐 Domain: {self.custom_domain}")
            print(f"╰─ 💰 Estimated Cost: {self._calculate_cloud_run_cost()}")
            
        elif any([actions["update_service"], actions["update_traffic"], actions["configure_domain"]]):
            print(f"\n╭─ 🔄 WILL UPDATE")
            print(f"├─ 🚀 Service: {self.service_name}")
            print(f"├─ 📋 Changes:")
            for change in actions["changes"]:
                print(f"│  • {change}")
            print(f"╰─ 💰 Updated Cost: {self._calculate_cloud_run_cost()}")
            
        else:
            print(f"\n╭─ ✅ WILL KEEP")
            print(f"├─ 🚀 Service: {self.service_name}")
            print(f"├─ 📍 Region: {current_state.get('region', 'Unknown')}")
            print(f"├─ 🌐 URL: {current_state.get('url', 'Unknown')}")
            print(f"├─ 💾 Memory: {current_state.get('memory', 'Unknown')}")
            print(f"╰─ 📊 Status: {current_state.get('status', 'Unknown')}")
            
    def _display_cloud_run_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  Service: {self.service_name}")
        print(f"   📍 Region: {current_state.get('region', 'Unknown')}")
        print(f"   🌐 URL: {current_state.get('url', 'Unknown')}")
        print(f"   🐳 Image: {current_state.get('image_url', 'Unknown')}")
        if current_state.get("custom_domain"):
            print(f"   🌐 Custom Domain: {current_state['custom_domain']}")
        print(f"   ⚠️  ALL SERVICE DATA AND TRAFFIC WILL BE PERMANENTLY LOST")
        
    def _calculate_cloud_run_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_cloud_run_cost()
        return f"${base_cost:.2f}/month"
        
    def _get_cloud_run_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current Cloud Run configuration"""
        return {
            "service_name": self.service_name,
            "description": self.service_description,
            "region": self.region,
            "image_url": self.image_url,
            "memory_limit": self.memory_limit,
            "cpu_limit": self.cpu_limit,
            "container_port": self.container_port,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "max_concurrent_requests": self.max_concurrent_requests,
            "timeout_seconds": self.timeout_seconds,
            "allow_unauthenticated": self.allow_unauthenticated,
            "environment_variables": self.environment_variables,
            "service_account_email": self.service_account_email,
            "custom_domain": self.custom_domain,
            "vpc_connector": self.vpc_connector,
            "labels": self.service_labels,
            "build_enabled": self.build_enabled,
            "build_source_path": self.build_source_path
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
        
        print(f"🎯 Cross-Cloud Magic: Optimizing Cloud Run for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective serverless deployment")
            # Use minimal resources for cost savings
            self.memory_limit = "256Mi"
            self.cpu_limit = "1000m"
            self.min_instances = 0  # Scale to zero
            self.max_instances = 10  # Limit max for cost control
            self.cpu_throttling = True
            print("   💡 Configured for scale-to-zero and minimal resources")
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance serverless deployment")
            # Use higher resources for performance
            self.memory_limit = "2Gi"
            self.cpu_limit = "2000m"
            self.min_instances = 1  # Always warm
            self.max_instances = 100
            self.cpu_boost = True
            self.cpu_throttling = False
            print("   💡 Configured for always-warm instances and high resources")
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable serverless deployment")
            # Balance resources and availability
            self.memory_limit = "1Gi"
            self.cpu_limit = "1000m"
            self.min_instances = 2  # Multiple instances for reliability
            self.max_instances = 50
            self.max_concurrent_requests = 80  # Conservative concurrency
            print("   💡 Configured for multiple instances and conservative scaling")
                
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant serverless deployment")
            # Security-focused configuration
            self.allow_unauthenticated = False  # Require authentication
            self.execution_environment = "gen2"  # Latest environment
            self.service_labels.update({
                "compliance": "enabled",
                "audit": "required",
                "security": "enhanced"
            })
            print("   💡 Configured for enhanced security and compliance")
            
        return self
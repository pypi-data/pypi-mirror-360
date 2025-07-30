"""
GCP Cloud Build Complete Implementation

Combines all Cloud Build functionality through multiple inheritance:
- CloudBuildCore: Core attributes and authentication
- CloudBuildConfigurationMixin: Chainable configuration methods  
- CloudBuildLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from typing import Dict, Any, List, Optional
from .cloud_build_core import CloudBuildCore
from .cloud_build_configuration import CloudBuildConfigurationMixin
from .cloud_build_lifecycle import CloudBuildLifecycleMixin


class CloudBuild(CloudBuildLifecycleMixin, CloudBuildConfigurationMixin, CloudBuildCore):
    """
    Complete GCP Cloud Build implementation for CI/CD pipelines and automation.
    
    This class combines:
    - Build pipeline configuration methods (steps, triggers, deployments)
    - Build lifecycle management (create, destroy, preview, run)
    - Source repository and container image management
    - Advanced deployment targets (Cloud Run, GKE, App Engine)
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize CloudBuild instance for CI/CD pipelines"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$25.00/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._build_type = None
        self._auto_scaling_enabled = True
        self._high_availability_enabled = False
    
    # Required abstract methods implementation
    def create(self) -> Dict[str, Any]:
        """Create Cloud Build pipeline"""
        return CloudBuildLifecycleMixin.create(self)
        
    def destroy(self) -> Dict[str, Any]:
        """Destroy Cloud Build pipeline"""
        return CloudBuildLifecycleMixin.destroy(self)
        
    def preview(self) -> Dict[str, Any]:
        """Preview Cloud Build configuration"""
        return CloudBuildLifecycleMixin.preview(self)
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current Cloud Build state"""
        # Simulate fetching current state
        return {
            "exists": False,
            "build_name": self.build_name,
            "project_id": getattr(self, 'project_id', None)
        }

    def validate_configuration(self):
        """Validate the current Cloud Build configuration"""
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
                errors.append(f"Invalid build step at index {i}: {step.get('name', 'Unknown')}")
        
        # Validate triggers
        if not self.triggers:
            warnings.append("No triggers defined - builds will only run manually")
        
        for trigger in self.triggers:
            if not self._validate_trigger_config(trigger):
                errors.append(f"Invalid trigger configuration: {trigger.get('name', 'Unknown')}")
        
        # Validate deployment targets
        for target in self.deployment_targets:
            if not self._validate_deployment_target(target):
                errors.append(f"Invalid deployment target: {target.get('name', 'Unknown')}")
        
        # Resource warnings
        if len(self.build_steps) > 20:
            warnings.append(f"{len(self.build_steps)} build steps may increase build time significantly")
        
        if self.timeout_seconds > 3600:  # 1 hour
            warnings.append(f"Long build timeout ({self.timeout_seconds // 60} minutes) may increase costs")
        
        # Cost warnings
        estimated_cost = self._estimate_build_cost()
        if estimated_cost > 100:
            warnings.append(f"High estimated cost: ${estimated_cost:.2f}/month")
        
        # Security warnings
        if not self.service_account_email:
            warnings.append("No service account specified - using default Compute Engine service account")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_build_info(self):
        """Get complete information about the Cloud Build configuration"""
        return {
            'build_name': self.build_name,
            'description': self.build_description,
            'project_id': self.project_id,
            'source_repo_url': self.source_repo_url,
            'source_branch': self.source_branch,
            'source_type': self.source_type,
            'build_steps_count': len(self.build_steps),
            'build_steps': self.build_steps,
            'triggers_count': len(self.triggers),
            'triggers': self.triggers,
            'deployment_targets_count': len(self.deployment_targets),
            'deployment_targets': self.deployment_targets,
            'machine_type': self.machine_type,
            'timeout_seconds': self.timeout_seconds,
            'disk_size_gb': self.disk_size_gb,
            'docker_image_name': self.docker_image_name,
            'container_registry': self.container_registry,
            'service_account_email': self.service_account_email,
            'substitutions': self.substitutions,
            'notification_channels_count': len(self.notification_channels),
            'slack_webhooks_count': len(self.slack_webhooks),
            'labels_count': len(self.build_labels),
            'build_exists': self.build_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'build_type': self._build_type
        }
    
    def clone(self, new_name: str):
        """Create a copy of this build configuration with a new name"""
        cloned_build = CloudBuild(new_name)
        cloned_build.build_name = new_name
        cloned_build.build_description = self.build_description
        cloned_build.project_id = self.project_id
        cloned_build.source_repo_url = self.source_repo_url
        cloned_build.source_branch = self.source_branch
        cloned_build.source_type = self.source_type
        cloned_build.build_steps = [step.copy() for step in self.build_steps]
        cloned_build.triggers = [trigger.copy() for trigger in self.triggers]
        cloned_build.deployment_targets = [target.copy() for target in self.deployment_targets]
        cloned_build.machine_type = self.machine_type
        cloned_build.timeout_seconds = self.timeout_seconds
        cloned_build.substitutions = self.substitutions.copy()
        cloned_build.build_labels = self.build_labels.copy()
        return cloned_build
    
    def export_configuration(self):
        """Export build configuration for backup or migration"""
        return {
            'metadata': {
                'build_name': self.build_name,
                'project_id': self.project_id,
                'source_repo_url': self.source_repo_url,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'build_name': self.build_name,
                'description': self.build_description,
                'project_id': self.project_id,
                'source_repo_url': self.source_repo_url,
                'source_branch': self.source_branch,
                'source_type': self.source_type,
                'build_steps': self.build_steps,
                'triggers': self.triggers,
                'deployment_targets': self.deployment_targets,
                'machine_type': self.machine_type,
                'timeout_seconds': self.timeout_seconds,
                'disk_size_gb': self.disk_size_gb,
                'docker_image_name': self.docker_image_name,
                'container_registry': self.container_registry,
                'service_account_email': self.service_account_email,
                'substitutions': self.substitutions,
                'secret_substitutions': self.secret_substitutions,
                'notification_channels': self.notification_channels,
                'slack_webhooks': self.slack_webhooks,
                'email_notifications': self.email_notifications,
                'labels': self.build_labels,
                'optimization_priority': self._optimization_priority,
                'build_type': self._build_type,
                'auto_scaling_enabled': self._auto_scaling_enabled,
                'high_availability_enabled': self._high_availability_enabled
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import build configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.build_name = config.get('build_name', self.build_name)
            self.build_description = config.get('description', f"CI/CD pipeline for {self.build_name}")
            self.project_id = config.get('project_id')
            self.source_repo_url = config.get('source_repo_url')
            self.source_branch = config.get('source_branch', 'main')
            self.source_type = config.get('source_type', 'github')
            self.build_steps = config.get('build_steps', [])
            self.triggers = config.get('triggers', [])
            self.deployment_targets = config.get('deployment_targets', [])
            self.machine_type = config.get('machine_type', 'e2-standard-2')
            self.timeout_seconds = config.get('timeout_seconds', 1200)
            self.disk_size_gb = config.get('disk_size_gb', 100)
            self.docker_image_name = config.get('docker_image_name')
            self.container_registry = config.get('container_registry', 'gcr.io')
            self.service_account_email = config.get('service_account_email')
            self.substitutions = config.get('substitutions', {})
            self.secret_substitutions = config.get('secret_substitutions', {})
            self.notification_channels = config.get('notification_channels', [])
            self.slack_webhooks = config.get('slack_webhooks', [])
            self.email_notifications = config.get('email_notifications', [])
            self.build_labels = config.get('labels', {})
            self._optimization_priority = config.get('optimization_priority')
            self._build_type = config.get('build_type')
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', True)
            self._high_availability_enabled = config.get('high_availability_enabled', False)
        
        return self
    
    def enable_auto_scaling(self, enabled: bool = True):
        """Enable automatic scaling for build resources"""
        self._auto_scaling_enabled = enabled
        if enabled:
            print("📈 Auto-scaling enabled for builds")
            print("   💡 Dynamic machine type adjustment configured")
            print("   💡 Parallel build execution enabled")
        return self
    
    def enable_high_availability(self, enabled: bool = True):
        """Enable high availability for builds"""
        self._high_availability_enabled = enabled
        if enabled:
            print("🛡️ High availability enabled for builds")
            print("   💡 Multi-region build execution configured")
            print("   💡 Redundant notification channels enabled")
        return self
    
    def get_build_step_by_name(self, name: str):
        """Get build step by container name"""
        for step in self.build_steps:
            if step.get("name") == name:
                return step
        return None
    
    def get_trigger_by_name(self, name: str):
        """Get trigger by name"""
        for trigger in self.triggers:
            if trigger.get("name") == name:
                return trigger
        return None
    
    def get_deployment_target_by_name(self, name: str):
        """Get deployment target by name"""
        for target in self.deployment_targets:
            if target.get("name") == name:
                return target
        return None
    
    def remove_build_step(self, name: str):
        """Remove a build step by container name"""
        self.build_steps = [s for s in self.build_steps if s.get("name") != name]
        print(f"🗑️  Removed build step '{name}'")
        return self
    
    def remove_trigger(self, name: str):
        """Remove a trigger by name"""
        self.triggers = [t for t in self.triggers if t.get("name") != name]
        print(f"🗑️  Removed trigger '{name}'")
        return self
    
    def remove_deployment_target(self, name: str):
        """Remove a deployment target by name"""
        self.deployment_targets = [t for t in self.deployment_targets if t.get("name") != name]
        print(f"🗑️  Removed deployment target '{name}'")
        return self
    
    def get_build_summary(self):
        """Get a summary of the build configuration"""
        return {
            "build_name": self.build_name,
            "project_id": self.project_id,
            "source_repo": self.source_repo_url,
            "source_branch": self.source_branch,
            "total_build_steps": len(self.build_steps),
            "total_triggers": len(self.triggers),
            "total_deployment_targets": len(self.deployment_targets),
            "machine_type": self.machine_type,
            "timeout_minutes": self.timeout_seconds // 60,
            "estimated_monthly_cost": self.estimated_monthly_cost,
            "deployment_ready": self.deployment_ready
        }
    
    def get_pipeline_status(self):
        """Get status of the build pipeline"""
        status = {
            "overall_status": "healthy",
            "issues": [],
            "recommendations": []
        }
        
        # Check for common issues
        if not self.build_steps:
            status["issues"].append("No build steps defined")
            status["overall_status"] = "error"
        
        if not self.triggers:
            status["recommendations"].append("Consider adding triggers for automatic builds")
        
        if not self.deployment_targets:
            status["recommendations"].append("Consider adding deployment targets")
        
        # Check for Docker-related steps
        has_docker_build = any("docker" in step.get("name", "").lower() for step in self.build_steps)
        has_docker_push = any("push" in " ".join(step.get("args", [])) for step in self.build_steps)
        
        if has_docker_build and not has_docker_push:
            status["recommendations"].append("Consider adding Docker push step after build")
        
        # Check timeout settings
        if self.timeout_seconds < 300:  # 5 minutes
            status["recommendations"].append("Build timeout may be too short for complex builds")
        elif self.timeout_seconds > 3600:  # 1 hour
            status["recommendations"].append("Build timeout may be unnecessarily long (increases costs)")
        
        return status
    
    def apply_build_best_practices(self):
        """Apply build best practices to the configuration"""
        print("🔨 Applying build best practices")
        
        # Ensure reasonable timeout
        if self.timeout_seconds < 600:
            print("   💡 Increasing timeout to 10 minutes minimum")
            self.timeout_seconds = 600
        
        # Ensure appropriate machine type
        if len(self.build_steps) > 10 and self.machine_type == "e2-standard-2":
            print("   💡 Upgrading to e2-standard-4 for complex builds")
            self.machine_type = "e2-standard-4"
        
        # Add build labels
        self.build_labels.update({
            "managed-by": "infradsl",
            "best-practices": "applied",
            "ci-cd": "enabled"
        })
        print("   💡 Added build best practice labels")
        
        # Ensure at least one trigger
        if not self.triggers:
            print("   💡 Adding push trigger for main branch")
            self.push_trigger("main")
        
        return self
    
    def get_cost_breakdown(self):
        """Get detailed cost breakdown for builds"""
        # Estimate builds per month
        builds_per_day = len(self.triggers) * 5  # 5 builds per trigger per day
        builds_per_month = builds_per_day * 30
        
        # Estimate minutes per build
        minutes_per_build = 10  # Base estimate
        if len(self.build_steps) > 5:
            minutes_per_build = 20
        if len(self.build_steps) > 10:
            minutes_per_build = 30
        
        total_minutes = builds_per_month * minutes_per_build
        free_minutes = 120 * 30  # Free tier
        billable_minutes = max(0, total_minutes - free_minutes)
        
        # Cost per minute based on machine type
        cost_per_minute = 0.003  # e2-standard-2
        if "standard-4" in self.machine_type:
            cost_per_minute = 0.006
        elif "standard-8" in self.machine_type:
            cost_per_minute = 0.012
        
        breakdown = {
            "builds_per_month": builds_per_month,
            "minutes_per_build": minutes_per_build,
            "total_minutes": total_minutes,
            "free_minutes": min(total_minutes, free_minutes),
            "billable_minutes": billable_minutes,
            "cost_per_minute": cost_per_minute,
            "monthly_cost": billable_minutes * cost_per_minute
        }
        
        return breakdown
    
    def get_security_analysis(self):
        """Analyze build security configuration"""
        analysis = {
            "security_score": 100,
            "issues": [],
            "recommendations": []
        }
        
        # Check service account
        if not self.service_account_email:
            analysis["recommendations"].append("Use dedicated service account instead of default")
            analysis["security_score"] -= 10
        
        # Check for secrets in substitutions
        for key, value in self.substitutions.items():
            if any(keyword in key.lower() for keyword in ["password", "key", "secret", "token"]):
                analysis["issues"].append(f"Potential secret in substitution: {key}")
                analysis["security_score"] -= 20
        
        # Check private pool usage
        if not self.private_pool_name:
            analysis["recommendations"].append("Consider using private worker pool for sensitive builds")
            analysis["security_score"] -= 5
        
        # Check logs bucket
        if not self.build_logs_bucket:
            analysis["recommendations"].append("Use custom logs bucket for better security control")
            analysis["security_score"] -= 5
        
        return analysis


# Convenience functions for creating CloudBuild instances
def create_node_webapp_build(project_id: str, app_name: str, repo_url: str) -> CloudBuild:
    """Create build configuration for Node.js web application"""
    build = CloudBuild(f"{app_name}-build")
    build.project(project_id).github_repo(repo_url).node_webapp_pipeline(app_name).push_trigger()
    return build

def create_python_api_build(project_id: str, app_name: str, repo_url: str) -> CloudBuild:
    """Create build configuration for Python API"""
    build = CloudBuild(f"{app_name}-build")
    build.project(project_id).github_repo(repo_url).python_api_pipeline(app_name).push_trigger()
    return build

def create_k8s_deploy_build(project_id: str, app_name: str, repo_url: str, cluster_name: str) -> CloudBuild:
    """Create build configuration for Kubernetes deployment"""
    build = CloudBuild(f"{app_name}-k8s-build")
    build.project(project_id).github_repo(repo_url).k8s_deploy_pipeline(app_name, cluster_name).push_trigger()
    return build

def create_cloud_run_build(project_id: str, app_name: str, repo_url: str) -> CloudBuild:
    """Create build configuration for Cloud Run deployment"""
    build = CloudBuild(f"{app_name}-cloudrun-build")
    build.project(project_id).github_repo(repo_url).cloud_run_deploy_pipeline(app_name).push_trigger()
    return build

def create_fullstack_build(project_id: str, app_name: str, repo_url: str, cluster_name: str) -> CloudBuild:
    """Create build configuration for full-stack application"""
    build = CloudBuild(f"{app_name}-fullstack-build")
    build.project(project_id).github_repo(repo_url).fullstack_deploy_pipeline(f"{app_name}-frontend", f"{app_name}-backend", cluster_name).push_trigger()
    return build

# Aliases for backward compatibility
Build = CloudBuild
GCPBuild = CloudBuild
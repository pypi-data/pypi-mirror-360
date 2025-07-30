"""
GCP Cloud Build Core Implementation

Core attributes and authentication for Google Cloud Build CI/CD service.
Provides the foundation for the modular build pipeline system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class CloudBuildCore(BaseGcpResource):
    """
    Core class for Google Cloud Build functionality.
    
    This class provides:
    - Basic build configuration attributes
    - Authentication setup
    - Common utilities for CI/CD operations
    - Build triggers and step management foundations
    """
    
    def __init__(self, name: str):
        """Initialize Cloud Build core with build name"""
        super().__init__(name)
        
        # Core build attributes
        self.build_name = name
        self.build_description = f"CI/CD pipeline for {name}"
        self.build_type = "pipeline"  # pipeline, trigger, manual
        self.project_id = None
        
        # Build configuration
        self.build_steps = []
        self.build_images = []
        self.build_artifacts = []
        self.build_environment = {}
        
        # Source configuration
        self.source_repo_url = None
        self.source_branch = "main"
        self.source_tag = None
        self.source_commit_sha = None
        self.source_type = "github"  # github, bitbucket, cloud_source_repos
        
        # Trigger configuration
        self.triggers = []
        self.trigger_type = "push"  # push, pull_request, tag, manual
        self.trigger_branch_pattern = None
        self.trigger_tag_pattern = None
        self.trigger_file_filter = []
        
        # Build environment
        self.machine_type_value = "e2-standard-2"  # e2-standard-2, e2-standard-4, e2-standard-8, etc.
        self.disk_size_gb = 100
        self.timeout_seconds = 1200  # 20 minutes default
        self.log_streaming = "STREAM_DEFAULT"
        
        # Container and registry settings
        self.dockerfile_path = "Dockerfile"
        self.docker_image_name = None
        self.container_registry = "gcr.io"  # gcr.io, us-docker.pkg.dev, etc.
        self.image_tags = ["latest"]
        
        # Deployment targets
        self.deployment_targets = []
        self.cloud_run_services = []
        self.gke_clusters = []
        self.app_engine_services = []
        
        # Build substitutions (variables)
        self.substitutions = {}
        self.secret_substitutions = {}
        
        # Notification settings
        self.notification_channels = []
        self.slack_webhooks = []
        self.email_notifications = []
        
        # Security and permissions
        self.service_account_email = None
        self.build_logs_bucket = None
        self.private_pool_name = None
        
        # Advanced features
        self.build_config_file = "cloudbuild.yaml"
        self.inline_build_config = None
        self.approval_required = False
        self.parallel_builds = True
        
        # Labels and organization
        self.build_labels = {}
        
        # State tracking
        self.build_exists = False
        self.build_created = False
        self.triggers_created = False
        
    def _initialize_managers(self):
        """Initialize Cloud Build-specific managers"""
        # Will be set up after authentication
        self.build_manager = None
        self.trigger_manager = None
        self.artifact_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # TODO: Implement Cloud Build managers
        # For now, use basic setup without managers
        self.build_manager = None
        self.trigger_manager = None
        self.artifact_manager = None
        
        # Set up project context
        if hasattr(self.gcp_client, 'project_id'):
            self.project_id = self.project_id or self.gcp_client.project_id
        
    def _is_valid_repo_url(self, url: str) -> bool:
        """Check if repository URL is valid"""
        valid_patterns = [
            "https://github.com/",
            "https://bitbucket.org/",
            "https://source.developers.google.com/"
        ]
        return any(url.startswith(pattern) for pattern in valid_patterns)
        
    def _is_valid_machine_type(self, machine_type: str) -> bool:
        """Check if machine type is valid"""
        valid_types = [
            "e2-standard-2", "e2-standard-4", "e2-standard-8", "e2-standard-16", "e2-standard-32",
            "e2-highmem-2", "e2-highmem-4", "e2-highmem-8", "e2-highmem-16",
            "e2-highcpu-16", "e2-highcpu-32",
            "n1-standard-1", "n1-standard-2", "n1-standard-4", "n1-standard-8"
        ]
        return machine_type in valid_types
        
    def _is_valid_trigger_type(self, trigger_type: str) -> bool:
        """Check if trigger type is valid"""
        valid_types = ["push", "pull_request", "tag", "manual", "webhook", "pubsub"]
        return trigger_type in valid_types
        
    def _is_valid_source_type(self, source_type: str) -> bool:
        """Check if source type is valid"""
        valid_types = ["github", "bitbucket", "cloud_source_repos", "storage"]
        return source_type in valid_types
        
    def _is_valid_registry_url(self, registry_url: str) -> bool:
        """Check if container registry URL is valid"""
        valid_registries = [
            "gcr.io", "us.gcr.io", "eu.gcr.io", "asia.gcr.io",
            "us-docker.pkg.dev", "europe-docker.pkg.dev", "asia-docker.pkg.dev"
        ]
        return any(registry_url.startswith(registry) for registry in valid_registries)
        
    def _validate_build_step(self, step: Dict[str, Any]) -> bool:
        """Validate build step configuration"""
        required_fields = ["name"]
        
        for field in required_fields:
            if field not in step:
                return False
                
        # Validate step name (should be a container image)
        name = step.get("name", "")
        if not name:
            return False
            
        # Check if it's a valid container image reference
        if "/" not in name and ":" not in name:
            # Assume it's a Cloud Build step like 'gcr.io/cloud-builders/docker'
            pass
            
        return True
        
    def _validate_trigger_config(self, trigger: Dict[str, Any]) -> bool:
        """Validate trigger configuration"""
        required_fields = ["name", "trigger_type"]
        
        for field in required_fields:
            if field not in trigger:
                return False
                
        # Validate trigger type
        if not self._is_valid_trigger_type(trigger["trigger_type"]):
            return False
            
        # Validate source configuration
        if "github" in trigger and trigger["github"]:
            github_config = trigger["github"]
            if "owner" not in github_config or "name" not in github_config:
                return False
                
        return True
        
    def _validate_deployment_target(self, target: Dict[str, Any]) -> bool:
        """Validate deployment target configuration"""
        required_fields = ["type", "name"]
        
        for field in required_fields:
            if field not in target:
                return False
                
        # Validate target type
        valid_types = ["cloud_run", "gke", "app_engine", "compute_engine"]
        if target["type"] not in valid_types:
            return False
            
        return True
        
    def _get_common_build_steps(self) -> List[Dict[str, Any]]:
        """Get list of common Cloud Build steps"""
        return [
            # Docker steps
            {
                "name": "gcr.io/cloud-builders/docker",
                "description": "Build Docker container",
                "args": ["build", "-t", "gcr.io/$PROJECT_ID/${_IMAGE_NAME}:${SHORT_SHA}", "."]
            },
            {
                "name": "gcr.io/cloud-builders/docker", 
                "description": "Push Docker container",
                "args": ["push", "gcr.io/$PROJECT_ID/${_IMAGE_NAME}:${SHORT_SHA}"]
            },
            
            # Cloud Run deployment
            {
                "name": "gcr.io/cloud-builders/gcloud",
                "description": "Deploy to Cloud Run",
                "args": [
                    "run", "deploy", "${_SERVICE_NAME}",
                    "--image", "gcr.io/$PROJECT_ID/${_IMAGE_NAME}:${SHORT_SHA}",
                    "--region", "${_REGION}",
                    "--platform", "managed"
                ]
            },
            
            # GKE deployment
            {
                "name": "gcr.io/cloud-builders/gke-deploy",
                "description": "Deploy to GKE",
                "args": [
                    "run",
                    "--filename=k8s/",
                    "--image=gcr.io/$PROJECT_ID/${_IMAGE_NAME}:${SHORT_SHA}",
                    "--cluster=${_GKE_CLUSTER}",
                    "--location=${_GKE_LOCATION}"
                ]
            },
            
            # Node.js steps
            {
                "name": "node:16",
                "description": "Install Node.js dependencies",
                "entrypoint": "npm",
                "args": ["install"]
            },
            {
                "name": "node:16",
                "description": "Run Node.js tests",
                "entrypoint": "npm",
                "args": ["test"]
            },
            {
                "name": "node:16",
                "description": "Build Node.js application",
                "entrypoint": "npm",
                "args": ["run", "build"]
            },
            
            # Python steps
            {
                "name": "python:3.9",
                "description": "Install Python dependencies",
                "entrypoint": "pip",
                "args": ["install", "-r", "requirements.txt"]
            },
            {
                "name": "python:3.9",
                "description": "Run Python tests",
                "entrypoint": "python",
                "args": ["-m", "pytest"]
            },
            
            # Go steps
            {
                "name": "golang:1.19",
                "description": "Build Go application",
                "entrypoint": "go",
                "args": ["build", "-o", "app", "."]
            },
            {
                "name": "golang:1.19",
                "description": "Run Go tests",
                "entrypoint": "go",
                "args": ["test", "./..."]
            }
        ]
        
    def _get_step_description(self, step_name: str) -> str:
        """Get description for a build step"""
        descriptions = {
            "gcr.io/cloud-builders/docker": "Docker build and push operations",
            "gcr.io/cloud-builders/gcloud": "Google Cloud CLI operations",
            "gcr.io/cloud-builders/gke-deploy": "Deploy to Google Kubernetes Engine",
            "gcr.io/cloud-builders/kubectl": "Kubernetes CLI operations",
            "gcr.io/cloud-builders/git": "Git operations",
            "gcr.io/cloud-builders/npm": "Node.js package management",
            "gcr.io/cloud-builders/yarn": "Yarn package management",
            "node:16": "Node.js 16 runtime environment",
            "python:3.9": "Python 3.9 runtime environment",
            "golang:1.19": "Go 1.19 runtime environment",
            "openjdk:11": "Java 11 runtime environment"
        }
        return descriptions.get(step_name, step_name)
        
    def _estimate_build_cost(self) -> float:
        """Estimate monthly cost for Cloud Build"""
        # Google Cloud Build pricing (simplified)
        
        # Free tier: 120 build-minutes per day
        free_minutes_per_month = 120 * 30  # 3600 minutes
        
        # Estimate builds per month based on triggers
        builds_per_day = len(self.triggers) * 5  # 5 builds per trigger per day (estimated)
        builds_per_month = builds_per_day * 30
        
        # Estimate minutes per build based on complexity
        minutes_per_build = 10  # Default estimate
        if len(self.build_steps) > 5:
            minutes_per_build = 20
        if len(self.build_steps) > 10:
            minutes_per_build = 30
            
        total_minutes_per_month = builds_per_month * minutes_per_build
        
        # Calculate billable minutes (after free tier)
        billable_minutes = max(0, total_minutes_per_month - free_minutes_per_month)
        
        # Pricing based on machine type
        cost_per_minute = 0.003  # $0.003 per build-minute for e2-standard-2
        if "standard-4" in self.machine_type_value:
            cost_per_minute = 0.006
        elif "standard-8" in self.machine_type_value:
            cost_per_minute = 0.012
        elif "highmem" in self.machine_type_value:
            cost_per_minute = 0.008
        elif "highcpu" in self.machine_type_value:
            cost_per_minute = 0.004
            
        monthly_cost = billable_minutes * cost_per_minute
        
        return monthly_cost
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of Cloud Build from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get build configuration info
            if self.build_manager:
                build_info = self.build_manager.get_build_info(
                    project_id=self.project_id,
                    build_name=self.build_name
                )
                
                if build_info.get("exists", False):
                    # Get triggers
                    triggers = []
                    if self.trigger_manager:
                        triggers = self.trigger_manager.list_triggers(self.project_id)
                    
                    # Get recent builds
                    recent_builds = []
                    if self.build_manager:
                        recent_builds = self.build_manager.list_recent_builds(self.project_id)
                    
                    return {
                        "exists": True,
                        "build_name": self.build_name,
                        "project_id": self.project_id,
                        "triggers": triggers,
                        "triggers_count": len(triggers),
                        "recent_builds": recent_builds,
                        "recent_builds_count": len(recent_builds),
                        "machine_type": build_info.get("machine_type", "e2-standard-2"),
                        "timeout": build_info.get("timeout", "1200s"),
                        "service_account": build_info.get("service_account"),
                        "creation_time": build_info.get("creation_time"),
                        "status": build_info.get("status", "UNKNOWN")
                    }
                else:
                    return {
                        "exists": False,
                        "build_name": self.build_name,
                        "project_id": self.project_id
                    }
            else:
                return {
                    "exists": False,
                    "build_name": self.build_name,
                    "project_id": self.project_id,
                    "error": "Build manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch Cloud Build state: {str(e)}")
            return {
                "exists": False,
                "build_name": self.build_name,
                "project_id": self.project_id,
                "error": str(e)
            }
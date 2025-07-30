"""
GCP Cloud Build Configuration Mixin

Chainable configuration methods for Google Cloud Build CI/CD service.
Provides Rails-like method chaining for fluent pipeline configuration.
"""

from typing import Dict, Any, List, Optional


class CloudBuildConfigurationMixin:
    """
    Mixin for Cloud Build configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Build steps and pipeline configuration
    - Source repository and trigger setup
    - Container image building and deployment
    - Notification and approval workflows
    - Environment variables and secrets
    """
    
    def description(self, description_text: str):
        """Set description for the build pipeline"""
        self.build_description = description_text
        return self
        
    def project(self, project_id: str):
        """Set project ID for build operations - Rails convenience"""
        self.project_id = project_id
        return self
        
    def timeout(self, seconds: int):
        """Set build timeout in seconds"""
        if seconds < 60 or seconds > 86400:  # 1 minute to 24 hours
            print(f"⚠️  Warning: Invalid timeout {seconds}s. Valid range: 60-86400 seconds")
        self.timeout_seconds = seconds
        return self
        
    def machine_type(self, machine_type_name: str):
        """Set build machine type"""
        # TODO: Add validation back when _is_valid_machine_type is fixed
        # if not self._is_valid_machine_type(machine_type_name):
        #     print(f"⚠️  Warning: Invalid machine type '{machine_type_name}'")
        self.machine_type_value = machine_type_name
        return self
        
    def disk_size(self, size_gb: int):
        """Set disk size in GB"""
        if size_gb < 100 or size_gb > 2000:
            print(f"⚠️  Warning: Invalid disk size {size_gb}GB. Valid range: 100-2000GB")
        self.disk_size_gb = size_gb
        return self
        
    # Source repository configuration
    def github_repo(self, repo_url: str, branch: str = "main"):
        """Configure GitHub repository as source - Rails convenience"""
        if not repo_url.startswith("https://github.com/"):
            print(f"⚠️  Warning: Invalid GitHub URL format")
        self.source_repo_url = repo_url
        self.source_branch = branch
        self.source_type = "github"
        return self
        
    def bitbucket_repo(self, repo_url: str, branch: str = "main"):
        """Configure Bitbucket repository as source - Rails convenience"""
        if not repo_url.startswith("https://bitbucket.org/"):
            print(f"⚠️  Warning: Invalid Bitbucket URL format")
        self.source_repo_url = repo_url
        self.source_branch = branch
        self.source_type = "bitbucket"
        return self
        
    def cloud_source_repo(self, repo_name: str, branch: str = "main"):
        """Configure Cloud Source Repository - Rails convenience"""
        self.source_repo_url = f"https://source.developers.google.com/p/{self.project_id}/r/{repo_name}"
        self.source_branch = branch
        self.source_type = "cloud_source_repos"
        return self
        
    def branch(self, branch_name: str):
        """Set source branch"""
        self.source_branch = branch_name
        return self
        
    def tag(self, tag_name: str):
        """Set source tag"""
        self.source_tag = tag_name
        return self
        
    # Build trigger configuration
    def push_trigger(self, branch_pattern: str = None):
        """Add push trigger - Rails convenience"""
        trigger = {
            "name": f"{self.build_name}-push-trigger",
            "trigger_type": "push",
            "branch_pattern": branch_pattern or self.source_branch,
            "description": f"Trigger on push to {branch_pattern or self.source_branch}"
        }
        self.triggers.append(trigger)
        return self
        
    def pull_request_trigger(self, branch_pattern: str = "main"):
        """Add pull request trigger - Rails convenience"""
        trigger = {
            "name": f"{self.build_name}-pr-trigger",
            "trigger_type": "pull_request",
            "branch_pattern": branch_pattern,
            "description": f"Trigger on pull request to {branch_pattern}"
        }
        self.triggers.append(trigger)
        return self
        
    def tag_trigger(self, tag_pattern: str = "v*"):
        """Add tag trigger - Rails convenience"""
        trigger = {
            "name": f"{self.build_name}-tag-trigger",
            "trigger_type": "tag",
            "tag_pattern": tag_pattern,
            "description": f"Trigger on tag matching {tag_pattern}"
        }
        self.triggers.append(trigger)
        return self
        
    def manual_trigger(self):
        """Add manual trigger - Rails convenience"""
        trigger = {
            "name": f"{self.build_name}-manual-trigger",
            "trigger_type": "manual",
            "description": "Manual trigger for builds"
        }
        self.triggers.append(trigger)
        return self
        
    def schedule_trigger(self, cron_schedule: str):
        """Add scheduled trigger - Rails convenience"""
        trigger = {
            "name": f"{self.build_name}-schedule-trigger",
            "trigger_type": "schedule",
            "schedule": cron_schedule,
            "description": f"Scheduled trigger: {cron_schedule}"
        }
        self.triggers.append(trigger)
        return self
        
    def file_filter(self, patterns: List[str]):
        """Set file filter patterns for triggers"""
        self.trigger_file_filter = patterns
        return self
        
    # Build steps configuration
    def add_step(self, name: str, args: List[str] = None, entrypoint: str = None, env: Dict[str, str] = None):
        """Add a build step"""
        step = {
            "name": name,
            "args": args or [],
            "env": env or {}
        }
        
        if entrypoint:
            step["entrypoint"] = entrypoint
            
        if self._validate_build_step(step):
            self.build_steps.append(step)
        else:
            print(f"⚠️  Warning: Invalid build step configuration for '{name}'")
            
        return self
    
    def step(self, step_name: str):
        """Start a new build step configuration - Rails convenience"""
        self._current_step = {
            "name": step_name,
            "image": None,
            "script": [],
            "env": {},
            "working_dir": None,
            "depends_on": []
        }
        return self
    
    def image(self, image_name: str):
        """Set Docker image for current step"""
        if hasattr(self, '_current_step') and self._current_step:
            self._current_step["image"] = image_name
        return self
    
    def script(self, commands: List[str]):
        """Set script commands for current step"""
        if hasattr(self, '_current_step') and self._current_step:
            self._current_step["script"] = commands
            # Finalize the step
            self._finalize_current_step()
        return self
    
    def working_dir(self, directory: str):
        """Set working directory for current step"""
        if hasattr(self, '_current_step') and self._current_step:
            self._current_step["working_dir"] = directory
        return self
    
    def env(self, key: str, value: str):
        """Add environment variable to current step"""
        if hasattr(self, '_current_step') and self._current_step:
            self._current_step["env"][key] = value
        return self
    
    def depends_on(self, step_names: List[str]):
        """Set step dependencies"""
        if hasattr(self, '_current_step') and self._current_step:
            self._current_step["depends_on"] = step_names
        return self
    
    def _finalize_current_step(self):
        """Convert current step to Cloud Build format and add to steps"""
        if not hasattr(self, '_current_step') or not self._current_step:
            return
        
        step = self._current_step
        cloud_build_step = {
            "name": step["image"],
            "args": ["bash", "-c", " && ".join(step["script"])],
            "env": [f"{k}={v}" for k, v in step["env"].items()]
        }
        
        if step["working_dir"]:
            cloud_build_step["dir"] = step["working_dir"]
        
        if step["depends_on"]:
            cloud_build_step["waitFor"] = step["depends_on"]
        
        self.build_steps.append(cloud_build_step)
        self._current_step = None
    
    # Trigger configuration
    def trigger_on_push(self):
        """Enable trigger on push to repository"""
        self.trigger_on_push_enabled = True
        return self
    
    def trigger_on_pull_request(self):
        """Enable trigger on pull requests"""
        self.trigger_on_pr_enabled = True
        return self
    
    def branch_filter(self, branches: List[str]):
        """Set branch filter for triggers"""
        self.trigger_branches = branches
        return self
    
    # Notification configuration
    def slack_notifications(self, webhook_url: str):
        """Configure Slack notifications"""
        self.slack_webhook = webhook_url
        self.notifications_enabled = True
        return self
    
    def discord_notifications(self, webhook_url: str):
        """Configure Discord notifications"""
        self.discord_webhook = webhook_url
        self.notifications_enabled = True
        return self
    
    def email_notifications(self, emails: List[str]):
        """Configure email notifications"""
        self.notification_emails = emails
        self.notifications_enabled = True
        return self
    
    # Performance optimizations
    def cache_node_modules(self):
        """Enable node_modules caching"""
        self.cache_paths = getattr(self, 'cache_paths', [])
        self.cache_paths.append("node_modules")
        return self
    
    def cache_yarn(self):
        """Enable Yarn cache"""
        self.cache_paths = getattr(self, 'cache_paths', [])
        self.cache_paths.extend(["node_modules", ".yarn/cache"])
        return self
    
    def parallel_execution(self):
        """Enable parallel step execution where possible"""
        self.parallel_enabled = True
        return self
    
    def fail_fast(self):
        """Enable fail-fast mode"""
        self.fail_fast_enabled = True
        return self
    
    def managed_by_cicd(self):
        """Mark this resource as managed by CI/CD"""
        self.cicd_managed = True
        return self
        
    def docker_build(self, dockerfile: str = "Dockerfile", image_name: str = None, tags: List[str] = None):
        """Add Docker build step - Rails convenience"""
        image_name = image_name or self.build_name
        tags = tags or ["latest"]
        
        # Build step
        self.add_step(
            "gcr.io/cloud-builders/docker",
            ["build", "-t", f"gcr.io/$PROJECT_ID/{image_name}:${SHORT_SHA}", "-f", dockerfile, "."]
        )
        
        # Tag with additional tags
        for tag in tags:
            if tag != "latest":
                self.add_step(
                    "gcr.io/cloud-builders/docker",
                    ["tag", f"gcr.io/$PROJECT_ID/{image_name}:${SHORT_SHA}", f"gcr.io/$PROJECT_ID/{image_name}:{tag}"]
                )
        
        self.docker_image_name = image_name
        self.image_tags = tags
        return self
        
    def docker_push(self, image_name: str = None, tags: List[str] = None):
        """Add Docker push step - Rails convenience"""
        image_name = image_name or self.docker_image_name or self.build_name
        tags = tags or self.image_tags or ["latest"]
        
        # Push with SHA tag
        self.add_step(
            "gcr.io/cloud-builders/docker",
            ["push", f"gcr.io/$PROJECT_ID/{image_name}:${SHORT_SHA}"]
        )
        
        # Push additional tags
        for tag in tags:
            if tag != "latest":
                self.add_step(
                    "gcr.io/cloud-builders/docker",
                    ["push", f"gcr.io/$PROJECT_ID/{image_name}:{tag}"]
                )
        
        return self
        
    def npm_install(self):
        """Add npm install step - Rails convenience"""
        return self.add_step("node:16", ["install"], entrypoint="npm")
        
    def npm_test(self):
        """Add npm test step - Rails convenience"""
        return self.add_step("node:16", ["test"], entrypoint="npm")
        
    def npm_build(self):
        """Add npm build step - Rails convenience"""
        return self.add_step("node:16", ["run", "build"], entrypoint="npm")
        
    def yarn_install(self):
        """Add yarn install step - Rails convenience"""
        return self.add_step("node:16", ["install"], entrypoint="yarn")
        
    def yarn_test(self):
        """Add yarn test step - Rails convenience"""
        return self.add_step("node:16", ["test"], entrypoint="yarn")
        
    def yarn_build(self):
        """Add yarn build step - Rails convenience"""
        return self.add_step("node:16", ["build"], entrypoint="yarn")
        
    def pip_install(self, requirements_file: str = "requirements.txt"):
        """Add pip install step - Rails convenience"""
        return self.add_step("python:3.9", ["install", "-r", requirements_file], entrypoint="pip")
        
    def pytest(self):
        """Add pytest step - Rails convenience"""
        return self.add_step("python:3.9", ["-m", "pytest"], entrypoint="python")
        
    def go_build(self, output: str = "app"):
        """Add Go build step - Rails convenience"""
        return self.add_step("golang:1.19", ["build", "-o", output, "."], entrypoint="go")
        
    def go_test(self):
        """Add Go test step - Rails convenience"""
        return self.add_step("golang:1.19", ["test", "./..."], entrypoint="go")
        
    def maven_build(self):
        """Add Maven build step - Rails convenience"""
        return self.add_step("maven:3.8-openjdk-11", ["clean", "package"], entrypoint="mvn")
        
    def gradle_build(self):
        """Add Gradle build step - Rails convenience"""
        return self.add_step("gradle:7-jdk11", ["build"], entrypoint="gradle")
        
    # Deployment configuration
    def deploy_to_cloud_run(self, service_name: str, region: str = "us-central1", **kwargs):
        """Add Cloud Run deployment step - Rails convenience"""
        image_name = self.docker_image_name or self.build_name
        
        args = [
            "run", "deploy", service_name,
            "--image", f"gcr.io/$PROJECT_ID/{image_name}:${SHORT_SHA}",
            "--region", region,
            "--platform", "managed"
        ]
        
        # Add optional parameters
        if kwargs.get("allow_unauthenticated"):
            args.extend(["--allow-unauthenticated"])
        if kwargs.get("memory"):
            args.extend(["--memory", kwargs["memory"]])
        if kwargs.get("cpu"):
            args.extend(["--cpu", str(kwargs["cpu"])])
        if kwargs.get("concurrency"):
            args.extend(["--concurrency", str(kwargs["concurrency"])])
        if kwargs.get("port"):
            args.extend(["--port", str(kwargs["port"])])
        
        self.add_step("gcr.io/cloud-builders/gcloud", args)
        
        # Track deployment target
        self.deployment_targets.append({
            "type": "cloud_run",
            "name": service_name,
            "region": region,
            "image": f"gcr.io/$PROJECT_ID/{image_name}:${SHORT_SHA}"
        })
        
        return self
        
    def deploy_to_gke(self, cluster_name: str, location: str = "us-central1", namespace: str = "default"):
        """Add GKE deployment step - Rails convenience"""
        image_name = self.docker_image_name or self.build_name
        
        self.add_step("gcr.io/cloud-builders/gke-deploy", [
            "run",
            f"--filename=k8s/",
            f"--image=gcr.io/$PROJECT_ID/{image_name}:${SHORT_SHA}",
            f"--cluster={cluster_name}",
            f"--location={location}",
            f"--namespace={namespace}"
        ])
        
        # Track deployment target
        self.deployment_targets.append({
            "type": "gke",
            "name": cluster_name,
            "location": location,
            "namespace": namespace,
            "image": f"gcr.io/$PROJECT_ID/{image_name}:${SHORT_SHA}"
        })
        
        return self
        
    def deploy_to_app_engine(self, version: str = None):
        """Add App Engine deployment step - Rails convenience"""
        args = ["app", "deploy"]
        if version:
            args.extend(["--version", version])
            
        self.add_step("gcr.io/cloud-builders/gcloud", args)
        
        # Track deployment target
        self.deployment_targets.append({
            "type": "app_engine",
            "version": version
        })
        
        return self
        
    # Environment variables and substitutions
    def env_var(self, key: str, value: str):
        """Add environment variable"""
        self.build_environment[key] = value
        return self
        
    def substitution(self, key: str, value: str):
        """Add build substitution variable"""
        self.substitutions[key] = value
        return self
        
    def secret_substitution(self, key: str, secret_name: str, secret_version: str = "latest"):
        """Add secret substitution from Secret Manager"""
        self.secret_substitutions[key] = {
            "secret_name": secret_name,
            "version": secret_version
        }
        return self
        
    # Container registry configuration
    def container_registry(self, registry_url: str):
        """Set container registry URL"""
        if not self._is_valid_registry_url(registry_url):
            print(f"⚠️  Warning: Invalid container registry URL '{registry_url}'")
        self.container_registry = registry_url
        return self
        
    def artifact_registry(self, region: str = "us-central1", repository: str = None):
        """Use Artifact Registry - Rails convenience"""
        repository = repository or self.build_name
        self.container_registry = f"{region}-docker.pkg.dev/{self.project_id}/{repository}"
        return self
        
    # Notification configuration
    def slack_notification(self, webhook_url: str, channel: str = None):
        """Add Slack notification"""
        self.slack_webhooks.append({
            "webhook_url": webhook_url,
            "channel": channel
        })
        return self
        
    def email_notification(self, email: str):
        """Add email notification"""
        self.email_notifications.append(email)
        return self
        
    def notification_channel(self, channel_name: str):
        """Add notification channel"""
        self.notification_channels.append(channel_name)
        return self
        
    # Security configuration
    def service_account(self, email: str):
        """Set service account for builds"""
        self.service_account_email = email
        return self
        
    def private_pool(self, pool_name: str):
        """Use private worker pool"""
        self.private_pool_name = pool_name
        return self
        
    def logs_bucket(self, bucket_name: str):
        """Set custom logs storage bucket"""
        self.build_logs_bucket = bucket_name
        return self
        
    # Advanced configuration
    def approval_required(self, required: bool = True):
        """Require manual approval for builds"""
        self.approval_required = required
        return self
        
    def parallel_builds(self, enabled: bool = True):
        """Enable parallel build execution"""
        self.parallel_builds = enabled
        return self
        
    def build_config_file(self, file_path: str):
        """Use external build configuration file"""
        self.build_config_file = file_path
        return self
        
    def inline_config(self, config: Dict[str, Any]):
        """Use inline build configuration"""
        self.inline_build_config = config
        return self
        
    # Labels and organization
    def labels(self, labels: Dict[str, str]):
        """Add labels for organization and billing"""
        self.build_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.build_labels[key] = value
        return self
        
    # Rails-like environment configurations
    def development_pipeline(self):
        """Configure for development environment - Rails convention"""
        return (self.timeout(600)  # 10 minutes
                .machine_type("e2-standard-2")
                .label("environment", "development")
                .label("cost-optimization", "enabled"))
                
    def staging_pipeline(self):
        """Configure for staging environment - Rails convention"""
        return (self.timeout(1200)  # 20 minutes
                .machine_type("e2-standard-4")
                .label("environment", "staging")
                .label("testing", "comprehensive"))
                
    def production_pipeline(self):
        """Configure for production environment - Rails convention"""
        return (self.timeout(1800)  # 30 minutes
                .machine_type("e2-standard-8")
                .approval_required(True)
                .label("environment", "production")
                .label("security", "enhanced"))
                
    # Common pipeline patterns
    def node_webapp_pipeline(self, app_name: str, dockerfile: str = "Dockerfile"):
        """Set up Node.js web application pipeline - Rails convenience"""
        return (self.npm_install()
                .npm_test()
                .npm_build()
                .docker_build(dockerfile, app_name)
                .docker_push())
                
    def python_api_pipeline(self, app_name: str, dockerfile: str = "Dockerfile"):
        """Set up Python API pipeline - Rails convenience"""
        return (self.pip_install()
                .pytest()
                .docker_build(dockerfile, app_name)
                .docker_push())
                
    def go_microservice_pipeline(self, app_name: str, dockerfile: str = "Dockerfile"):
        """Set up Go microservice pipeline - Rails convenience"""
        return (self.go_test()
                .go_build()
                .docker_build(dockerfile, app_name)
                .docker_push())
                
    def java_spring_pipeline(self, app_name: str, dockerfile: str = "Dockerfile"):
        """Set up Java Spring pipeline - Rails convenience"""
        return (self.maven_build()
                .docker_build(dockerfile, app_name)
                .docker_push())
                
    def react_frontend_pipeline(self, app_name: str):
        """Set up React frontend pipeline - Rails convenience"""
        return (self.yarn_install()
                .yarn_test()
                .yarn_build()
                .docker_build("Dockerfile", app_name)
                .docker_push())
                
    def k8s_deploy_pipeline(self, app_name: str, cluster_name: str, location: str = "us-central1"):
        """Set up Kubernetes deployment pipeline - Rails convenience"""
        return (self.docker_build("Dockerfile", app_name)
                .docker_push()
                .deploy_to_gke(cluster_name, location))
                
    def cloud_run_deploy_pipeline(self, app_name: str, region: str = "us-central1"):
        """Set up Cloud Run deployment pipeline - Rails convenience"""
        return (self.docker_build("Dockerfile", app_name)
                .docker_push()
                .deploy_to_cloud_run(app_name, region, allow_unauthenticated=True))
                
    def fullstack_deploy_pipeline(self, frontend_name: str, backend_name: str, cluster_name: str):
        """Set up full-stack deployment pipeline - Rails convenience"""
        return (self.yarn_install()
                .yarn_build()
                .docker_build("frontend/Dockerfile", frontend_name)
                .docker_build("backend/Dockerfile", backend_name)
                .docker_push()
                .deploy_to_gke(cluster_name))
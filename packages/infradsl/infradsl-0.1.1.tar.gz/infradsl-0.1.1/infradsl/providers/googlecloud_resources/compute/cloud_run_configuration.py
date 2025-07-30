"""
GCP Cloud Run Configuration Mixin

Chainable configuration methods for Google Cloud Run serverless containers.
Provides Rails-like method chaining for fluent service configuration.
"""

import os
import time
import hashlib
from typing import Dict, Any, List, Optional


class CloudRunConfigurationMixin:
    """
    Mixin for Cloud Run configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Container image and build configuration
    - Resource allocation (CPU, memory, scaling)
    - Network and security settings
    - Environment variables and secrets
    - Traffic management and deployments
    """
    
    def description(self, description: str):
        """Set description for the Cloud Run service"""
        self.service_description = description
        return self
        
    def project(self, project_id: str):
        """Set project ID for Cloud Run operations - Rails convenience"""
        self.project_id = project_id
        return self
        
    def region(self, region: str):
        """Set deployment region"""
        if not self._is_valid_region(region):
            print(f"⚠️  Warning: Invalid region '{region}'. Use us-central1, europe-west1, etc.")
        self.region = region
        return self
        
    def location(self, region: str):
        """Set deployment location - alias for region()"""
        return self.region(region)
        
    # Container configuration
    def image(self, image_url: str):
        """Set container image URL"""
        if not self._validate_image_url(image_url):
            print(f"⚠️  Warning: Invalid image URL format '{image_url}'")
        self.image_url = image_url
        return self
        
    def container(self, image_name: str, source_path: str = None, template: str = "auto", port: int = 8080):
        """Build and deploy container from source - Rails convenience"""
        if source_path:
            self.build_source_path = source_path
            self.build_template = template
            self.build_enabled = True
        
        self.container_port = port
        
        # Set image URL for building
        if self.project_id and self.repository_location:
            registry_url = f"{self.repository_location}-docker.pkg.dev/{self.project_id}/{self.repository_name}"
            self.image_url = f"{registry_url}/{image_name}:latest"
        
        return self
        
    def dockerfile(self, dockerfile_path: str):
        """Set custom Dockerfile path"""
        self.dockerfile_path = dockerfile_path
        return self
        
    def port(self, port: int):
        """Set container port"""
        if not (1 <= port <= 65535):
            print(f"⚠️  Warning: Invalid port {port}. Must be between 1-65535")
        self.container_port = port
        return self
        
    def command(self, command: List[str]):
        """Set container command override"""
        self.container_command = command
        return self
        
    def args(self, args: List[str]):
        """Set container arguments"""
        self.container_args = args
        return self
        
    # Resource allocation
    def memory(self, memory: str):
        """Set memory limit (128Mi, 256Mi, 512Mi, 1Gi, 2Gi, 4Gi, 8Gi)"""
        if not self._is_valid_memory_limit(memory):
            print(f"⚠️  Warning: Invalid memory limit '{memory}'. Use 128Mi, 256Mi, 512Mi, 1Gi, 2Gi, 4Gi, 8Gi")
        self.memory_limit = memory
        return self
        
    def cpu(self, cpu: str):
        """Set CPU limit (1000m = 1 CPU, 2000m = 2 CPUs, or decimal like 1.5)"""
        if not self._is_valid_cpu_limit(cpu):
            print(f"⚠️  Warning: Invalid CPU limit '{cpu}'. Use millicores (1000m) or decimal (1.0)")
        self.cpu_limit = cpu
        return self
        
    def timeout(self, seconds: int):
        """Set request timeout in seconds (max 3600)"""
        if not (1 <= seconds <= 3600):
            print(f"⚠️  Warning: Invalid timeout {seconds}s. Must be between 1-3600 seconds")
        self.timeout_seconds = seconds
        return self
        
    def execution_environment(self, env: str):
        """Set execution environment (gen1, gen2)"""
        if not self._is_valid_execution_environment(env):
            print(f"⚠️  Warning: Invalid execution environment '{env}'. Use 'gen1' or 'gen2'")
        self.execution_environment = env
        return self
        
    # Scaling configuration
    def min_instances(self, count: int):
        """Set minimum number of instances (0 for scale-to-zero)"""
        if not (0 <= count <= 1000):
            print(f"⚠️  Warning: Invalid min instances {count}. Must be between 0-1000")
        self.min_instances = count
        return self
        
    def max_instances(self, count: int):
        """Set maximum number of instances"""
        if not (1 <= count <= 1000):
            print(f"⚠️  Warning: Invalid max instances {count}. Must be between 1-1000")
        self.max_instances = count
        return self
        
    def scaling(self, min_instances: int = 0, max_instances: int = 100):
        """Configure auto-scaling - Rails convenience"""
        return self.min_instances(min_instances).max_instances(max_instances)
        
    def auto_scale(self, min_instances: int = 0, max_instances: int = 100):
        """Configure auto-scaling - alias for scaling()"""
        return self.scaling(min_instances, max_instances)
        
    def concurrency(self, max_requests: int):
        """Set maximum concurrent requests per instance"""
        if not (1 <= max_requests <= 1000):
            print(f"⚠️  Warning: Invalid concurrency {max_requests}. Must be between 1-1000")
        self.max_concurrent_requests = max_requests
        return self
        
    def cpu_throttling(self, enabled: bool = True):
        """Enable or disable CPU throttling when not serving requests"""
        self.cpu_throttling = enabled
        return self
        
    def cpu_boost(self, enabled: bool = True):
        """Enable CPU boost for faster cold starts"""
        self.cpu_boost = enabled
        return self
        
    # Security and access
    def public(self):
        """Allow unauthenticated public access"""
        self.allow_unauthenticated = True
        return self
        
    def private(self):
        """Require authentication for access"""
        self.allow_unauthenticated = False
        return self
        
    def allow_unauthenticated_access(self, allow: bool = True):
        """Set whether to allow unauthenticated access"""
        self.allow_unauthenticated = allow
        return self
        
    def service_account(self, email: str):
        """Set service account for the Cloud Run service"""
        self.service_account_email = email
        return self
        
    def vpc_connector(self, connector_name: str):
        """Connect to VPC using Serverless VPC Access connector"""
        self.vpc_connector = connector_name
        return self
        
    def vpc_egress(self, egress_setting: str):
        """Set VPC egress setting (all-traffic, private-ranges-only)"""
        if not self._is_valid_vpc_egress(egress_setting):
            print(f"⚠️  Warning: Invalid VPC egress '{egress_setting}'. Use 'all-traffic' or 'private-ranges-only'")
        self.vpc_egress = egress_setting
        return self
        
    # Environment variables and secrets
    def environment(self, env_vars: Dict[str, str]):
        """Set environment variables"""
        self.environment_variables.update(env_vars)
        return self
        
    def env(self, key: str, value: str):
        """Set individual environment variable - Rails convenience"""
        self.environment_variables[key] = value
        return self
        
    def secret_env(self, key: str, secret_name: str, secret_version: str = "latest"):
        """Set environment variable from Secret Manager"""
        self.secret_environment_variables[key] = {
            "secret_name": secret_name,
            "version": secret_version
        }
        return self
        
    def secrets(self, secret_mappings: Dict[str, str]):
        """Set multiple secrets from Secret Manager"""
        for env_key, secret_name in secret_mappings.items():
            self.secret_env(env_key, secret_name)
        return self
        
    # Health checks and probes
    def health_check(self, path: str):
        """Set health check endpoint path"""
        self.health_check_path = path
        return self
        
    def startup_probe(self, path: str):
        """Set startup probe endpoint path"""
        self.startup_probe_path = path
        return self
        
    def liveness_probe(self, path: str):
        """Set liveness probe endpoint path"""
        self.liveness_probe_path = path
        return self
        
    # Domain and SSL configuration
    def domain(self, domain_name: str):
        """Configure custom domain with automatic SSL"""
        self.custom_domain = domain_name
        self.auto_ssl = True
        return self
        
    def ssl_certificate(self, certificate_name: str):
        """Use specific SSL certificate instead of automatic"""
        self.ssl_certificate = certificate_name
        self.auto_ssl = False
        return self
        
    def no_ssl(self):
        """Disable automatic SSL certificate"""
        self.auto_ssl = False
        return self
        
    # Traffic management
    def traffic(self, allocations: Dict[str, int]):
        """Set traffic allocation between revisions"""
        total = sum(allocations.values())
        if total != 100:
            print(f"⚠️  Warning: Traffic allocation totals {total}%, should be 100%")
        self.traffic_allocation = allocations
        return self
        
    def revision_suffix(self, suffix: str):
        """Set custom revision suffix"""
        self.revision_suffix = suffix
        return self
        
    def revision_timeout(self, seconds: int):
        """Set revision timeout in seconds"""
        self.revision_timeout = seconds
        return self
        
    # Container registry configuration
    def artifact_registry(self, repository: str = None, location: str = None):
        """Use Artifact Registry for container images"""
        self.registry_type = "artifact_registry"
        if repository:
            self.repository_name = repository
        if location:
            self.repository_location = location
        return self
        
    def gcr_registry(self):
        """Use Google Container Registry (legacy)"""
        self.registry_type = "gcr"
        return self
        
    # Build configuration
    def build_from_source(self, source_path: str, template: str = "auto"):
        """Enable building from source code"""
        self.build_enabled = True
        self.build_source_path = source_path
        self.build_template = template
        return self
        
    def build_substitutions(self, substitutions: Dict[str, str]):
        """Set build substitutions for container building"""
        self.build_substitutions.update(substitutions)
        return self
        
    def no_build(self):
        """Disable automatic container building"""
        self.build_enabled = False
        return self
        
    # Labels and annotations
    def labels(self, labels: Dict[str, str]):
        """Add labels for organization and billing"""
        self.service_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.service_labels[key] = value
        return self
        
    def annotations(self, annotations: Dict[str, str]):
        """Add service annotations"""
        self.service_annotations.update(annotations)
        return self
        
    def annotation(self, key: str, value: str):
        """Add individual annotation - Rails convenience"""
        self.service_annotations[key] = value
        return self
        
    # Rails-like environment configurations
    def development(self):
        """Configure for development environment - Rails convention"""
        return (self.memory("512Mi")
                .cpu("1000m")
                .scaling(0, 5)
                .timeout(300)
                .public()
                .label("environment", "development")
                .label("cost-optimization", "enabled"))
                
    def staging(self):
        """Configure for staging environment - Rails convention"""
        return (self.memory("1Gi")
                .cpu("1000m") 
                .scaling(1, 10)
                .timeout(600)
                .private()
                .label("environment", "staging")
                .label("testing", "enabled"))
                
    def production(self):
        """Configure for production environment - Rails convention"""
        return (self.memory("2Gi")
                .cpu("2000m")
                .scaling(2, 50)
                .timeout(900)
                .private()
                .cpu_boost(True)
                .label("environment", "production")
                .label("security", "enhanced"))
                
    # Common application patterns
    def web_app(self, port: int = 8080):
        """Configure for web application - Rails convenience"""
        return (self.port(port)
                .memory("1Gi")
                .cpu("1000m")
                .scaling(1, 20)
                .concurrency(80)
                .timeout(300)
                .health_check("/health"))
                
    def api_service(self, port: int = 8080):
        """Configure for API service - Rails convenience"""
        return (self.port(port)
                .memory("512Mi")
                .cpu("1000m")
                .scaling(2, 100)
                .concurrency(100)
                .timeout(60)
                .health_check("/health")
                .startup_probe("/ready"))
                
    def microservice(self, port: int = 8080):
        """Configure for microservice - Rails convenience"""
        return (self.port(port)
                .memory("256Mi")
                .cpu("500m")
                .scaling(0, 50)
                .concurrency(100)
                .timeout(30)
                .cpu_throttling(True))
                
    def background_worker(self):
        """Configure for background worker - Rails convenience"""
        return (self.memory("1Gi")
                .cpu("1000m")
                .scaling(1, 10)
                .concurrency(1)
                .timeout(3600)
                .private())
                
    def cron_job(self):
        """Configure for scheduled job - Rails convenience"""
        return (self.memory("512Mi")
                .cpu("1000m")
                .scaling(0, 1)
                .concurrency(1)
                .timeout(1800)
                .private())
                
    def static_site(self):
        """Configure for static site hosting - Rails convenience"""
        return (self.memory("128Mi")
                .cpu("250m")
                .scaling(0, 10)
                .concurrency(100)
                .timeout(60)
                .public())
                
    # Language-specific configurations
    def node_app(self, port: int = 3000):
        """Configure for Node.js application"""
        return (self.port(port)
                .memory("512Mi")
                .cpu("1000m")
                .env("NODE_ENV", "production")
                .web_app(port))
                
    def python_app(self, port: int = 8080):
        """Configure for Python application"""
        return (self.port(port)
                .memory("512Mi")
                .cpu("1000m")
                .env("PYTHONPATH", "/app")
                .web_app(port))
                
    def go_app(self, port: int = 8080):
        """Configure for Go application"""
        return (self.port(port)
                .memory("256Mi")
                .cpu("500m")
                .web_app(port))
                
    def java_app(self, port: int = 8080):
        """Configure for Java application"""
        return (self.port(port)
                .memory("1Gi")
                .cpu("1000m")
                .timeout(600)
                .web_app(port))
                
    def react_app(self, port: int = 3000):
        """Configure for React frontend application"""
        return (self.port(port)
                .memory("256Mi")
                .cpu("500m")
                .static_site()
                .env("NODE_ENV", "production"))
                
    def next_app(self, port: int = 3000):
        """Configure for Next.js application"""
        return (self.port(port)
                .memory("1Gi")
                .cpu("1000m")
                .web_app(port)
                .env("NODE_ENV", "production"))
                
    def django_app(self, port: int = 8000):
        """Configure for Django application"""
        return (self.port(port)
                .memory("1Gi")
                .cpu("1000m")
                .web_app(port)
                .env("DJANGO_SETTINGS_MODULE", "myapp.settings.production"))
                
    def flask_app(self, port: int = 5000):
        """Configure for Flask application"""
        return (self.port(port)
                .memory("512Mi")
                .cpu("1000m")
                .web_app(port)
                .env("FLASK_ENV", "production"))
                
    def fastapi_app(self, port: int = 8000):
        """Configure for FastAPI application"""
        return (self.port(port)
                .memory("512Mi")
                .cpu("1000m")
                .api_service(port)
                .env("ENVIRONMENT", "production"))
                
    # Common deployment patterns
    def blue_green_deployment(self, blue_percent: int = 100, green_percent: int = 0):
        """Configure blue-green deployment"""
        return self.traffic({"blue": blue_percent, "green": green_percent})
        
    def canary_deployment(self, stable_percent: int = 90, canary_percent: int = 10):
        """Configure canary deployment"""
        return self.traffic({"stable": stable_percent, "canary": canary_percent})
        
    def a_b_testing(self, variant_a: int = 50, variant_b: int = 50):
        """Configure A/B testing traffic split"""
        return self.traffic({"variant-a": variant_a, "variant-b": variant_b})
        
    # Utility methods
    def _resolve_template_path(self, template_path: str) -> str:
        """Resolve template path to absolute path"""
        if os.path.isabs(template_path) and os.path.exists(template_path):
            return template_path
            
        # Search common locations
        search_paths = [
            os.path.join(os.getcwd(), template_path),
            os.path.join(os.getcwd(), "..", template_path),
            os.path.join(os.getcwd(), "..", "..", template_path)
        ]
        
        for path in search_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path) and os.path.isdir(abs_path):
                return abs_path
                
        raise FileNotFoundError(f"Template directory '{template_path}' not found")
        
    def _generate_unique_tag(self, source_path: str = None) -> str:
        """Generate unique tag for container images"""
        try:
            if source_path and os.path.exists(source_path):
                content_hash = self._hash_directory_contents(source_path)
                timestamp = str(int(time.time()))
                return f"{content_hash[:8]}-{timestamp[-6:]}"
            else:
                return f"build-{int(time.time())}"
        except Exception:
            return f"build-{int(time.time())}"
            
    def _hash_directory_contents(self, directory: str) -> str:
        """Generate hash of directory contents"""
        hash_md5 = hashlib.md5()
        
        try:
            for root, dirs, files in os.walk(directory):
                for filename in sorted(files):
                    if filename.startswith('.') or filename in ['node_modules', '__pycache__']:
                        continue
                        
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'rb') as f:
                            hash_md5.update(filepath.encode())
                            hash_md5.update(f.read())
                    except (OSError, IOError):
                        continue
                        
            return hash_md5.hexdigest()
        except Exception:
            hash_md5.update(directory.encode())
            return hash_md5.hexdigest()
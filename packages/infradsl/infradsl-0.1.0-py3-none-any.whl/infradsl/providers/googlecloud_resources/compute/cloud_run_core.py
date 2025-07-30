"""
GCP Cloud Run Core Implementation

Core attributes and authentication for Google Cloud Run serverless containers.
Provides the foundation for the modular serverless container system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class CloudRunCore(BaseGcpResource):
    """
    Core class for Google Cloud Run functionality.
    
    This class provides:
    - Basic container service attributes and configuration
    - Authentication setup
    - Common utilities for serverless container operations
    - Container image and deployment management foundations
    """
    
    def __init__(self, name: str):
        """Initialize Cloud Run core with service name"""
        super().__init__(name)
        
        # Core service attributes
        self.service_name = name
        self.service_description = f"Cloud Run service for {name}"
        self.service_type = "serverless"  # serverless, managed
        
        # Container configuration
        self.image_url = None
        self.container_port = 8080
        self.container_command = None
        self.container_args = []
        self.dockerfile_path = "Dockerfile"
        
        # Resource allocation
        self.memory_limit = "512Mi"  # 128Mi, 256Mi, 512Mi, 1Gi, 2Gi, 4Gi, 8Gi
        self.cpu_limit = "1000m"     # 1000m = 1 CPU, 2000m = 2 CPUs
        self.timeout_seconds = 300   # Request timeout
        self.execution_environment = "gen2"  # gen1, gen2
        
        # Scaling configuration
        self.min_instances = 0
        self.max_instances = 100
        self.max_concurrent_requests = 80
        self.cpu_throttling = True
        self.cpu_boost = False
        
        # Location and region settings
        self.region = "us-central1"
        self.platform = "managed"  # managed, gke
        
        # Security and access
        self.allow_unauthenticated = False
        self.service_account_email = None
        self.vpc_connector = None
        self.vpc_egress = "all-traffic"  # all-traffic, private-ranges-only
        
        # Environment variables and secrets
        self.environment_variables = {}
        self.secret_environment_variables = {}
        self.volume_mounts = []
        
        # Traffic and deployment
        self.traffic_allocation = {"LATEST": 100}
        self.revision_suffix = None
        self.revision_timeout = 300
        
        # Domain and SSL
        self.custom_domain = None
        self.ssl_certificate = None
        self.auto_ssl = True
        
        # Container registry settings
        self.registry_type = "artifact_registry"  # artifact_registry, gcr
        self.repository_name = "cloud-run-apps"
        self.repository_location = "us-central1"
        
        # Build configuration (for container building)
        self.build_enabled = True
        self.build_source_path = None
        self.build_template = "auto"
        self.build_substitutions = {}
        
        # Monitoring and health checks
        self.health_check_path = None
        self.startup_probe_path = None
        self.liveness_probe_path = None
        
        # Labels and annotations
        self.service_labels = {}
        self.service_annotations = {}
        
        # State tracking
        self.service_exists = False
        self.service_created = False
        self.container_built = False
        self.domain_mapped = False
        
    def _initialize_managers(self):
        """Initialize Cloud Run-specific managers"""
        # Will be set up after authentication
        self.cloud_run_manager = None
        self.artifact_registry_manager = None
        self.container_builder = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Import here to avoid circular imports
        from ...googlecloud_managers.cloud_run_manager import CloudRunManager
        from ...googlecloud_managers.artifact_registry_manager import ArtifactRegistryManager
        from infradsl.container_engines.builder import ContainerBuilder
        from infradsl.container_engines.exceptions import NoEngineFoundError
        
        self.cloud_run_manager = CloudRunManager(self.gcp_client)
        self.artifact_registry_manager = ArtifactRegistryManager(self.gcp_client)
        
        # Initialize container builder
        try:
            self.container_builder = ContainerBuilder(
                project_id=self.gcp_client.project_id,
                location=self.repository_location
            )
        except (NoEngineFoundError, Exception) as e:
            print(f"⚠️  Container builder initialization failed: {e}")
            self.container_builder = None
        
        # Set up project context
        self.project_id = self.project_id or self.gcp_client.project_id
        
    def _is_valid_memory_limit(self, memory: str) -> bool:
        """Check if memory limit is valid"""
        valid_limits = [
            "128Mi", "256Mi", "512Mi", "1Gi", "2Gi", "4Gi", "8Gi", "16Gi", "32Gi"
        ]
        return memory in valid_limits
        
    def _is_valid_cpu_limit(self, cpu: str) -> bool:
        """Check if CPU limit is valid"""
        # CPU can be specified as millicores (1000m = 1 CPU) or as decimal (1.0)
        if cpu.endswith("m"):
            try:
                millicores = int(cpu[:-1])
                return 1 <= millicores <= 8000  # 1m to 8000m (8 CPUs)
            except ValueError:
                return False
        else:
            try:
                cores = float(cpu)
                return 0.001 <= cores <= 8.0  # 0.001 to 8 CPUs
            except ValueError:
                return False
                
    def _is_valid_region(self, region: str) -> bool:
        """Check if region is valid for Cloud Run"""
        valid_regions = [
            "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west3", "us-west4",
            "europe-north1", "europe-west1", "europe-west2", "europe-west3", "europe-west4", "europe-west6",
            "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2", "asia-northeast3",
            "asia-south1", "asia-southeast1", "asia-southeast2", "australia-southeast1"
        ]
        return region in valid_regions
        
    def _is_valid_execution_environment(self, env: str) -> bool:
        """Check if execution environment is valid"""
        return env in ["gen1", "gen2"]
        
    def _is_valid_vpc_egress(self, egress: str) -> bool:
        """Check if VPC egress setting is valid"""
        return egress in ["all-traffic", "private-ranges-only"]
        
    def _validate_image_url(self, image_url: str) -> bool:
        """Validate container image URL format"""
        if not image_url:
            return False
            
        # Common container registry patterns
        valid_patterns = [
            "gcr.io/", "us.gcr.io/", "eu.gcr.io/", "asia.gcr.io/",
            "docker.pkg.dev/", "us-docker.pkg.dev/", "europe-docker.pkg.dev/", "asia-docker.pkg.dev/",
            "docker.io/", "index.docker.io/", "registry.hub.docker.com/",
            "quay.io/", "ghcr.io/"
        ]
        
        return any(image_url.startswith(pattern) for pattern in valid_patterns)
        
    def _validate_service_config(self, config: Dict[str, Any]) -> bool:
        """Validate Cloud Run service configuration"""
        required_fields = ["service_name"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate memory if specified
        if "memory" in config and not self._is_valid_memory_limit(config["memory"]):
            return False
            
        # Validate CPU if specified
        if "cpu" in config and not self._is_valid_cpu_limit(config["cpu"]):
            return False
            
        # Validate region if specified
        if "region" in config and not self._is_valid_region(config["region"]):
            return False
            
        return True
        
    def _validate_scaling_config(self, config: Dict[str, Any]) -> bool:
        """Validate scaling configuration"""
        min_instances = config.get("min_instances", 0)
        max_instances = config.get("max_instances", 100)
        
        # Validate ranges
        if not (0 <= min_instances <= 1000):
            return False
        if not (1 <= max_instances <= 1000):
            return False
        if min_instances > max_instances:
            return False
            
        # Validate concurrent requests
        concurrency = config.get("max_concurrent_requests", 80)
        if not (1 <= concurrency <= 1000):
            return False
            
        return True
        
    def _get_common_container_images(self) -> List[str]:
        """Get list of common container images for Cloud Run"""
        return [
            # Google official images
            "gcr.io/google-samples/hello-app:1.0",
            "gcr.io/cloudrun/hello",
            "gcr.io/google-samples/microservices-demo/frontend:v0.3.9",
            
            # Language runtime images
            "node:16-alpine",
            "node:18-alpine", 
            "python:3.9-slim",
            "python:3.10-slim",
            "python:3.11-slim",
            "golang:1.19-alpine",
            "golang:1.20-alpine",
            "openjdk:11-jre-slim",
            "openjdk:17-jre-slim",
            
            # Web server images
            "nginx:alpine",
            "httpd:alpine",
            "caddy:alpine",
            
            # Popular application images
            "wordpress:latest",
            "ghost:alpine",
            "drupal:alpine"
        ]
        
    def _get_image_description(self, image: str) -> str:
        """Get description for a container image"""
        descriptions = {
            "gcr.io/cloudrun/hello": "Google Cloud Run hello world sample",
            "node:16-alpine": "Node.js 16 on Alpine Linux",
            "node:18-alpine": "Node.js 18 on Alpine Linux",
            "python:3.9-slim": "Python 3.9 slim image",
            "python:3.10-slim": "Python 3.10 slim image", 
            "python:3.11-slim": "Python 3.11 slim image",
            "golang:1.19-alpine": "Go 1.19 on Alpine Linux",
            "golang:1.20-alpine": "Go 1.20 on Alpine Linux",
            "nginx:alpine": "Nginx web server on Alpine",
            "httpd:alpine": "Apache HTTP Server on Alpine"
        }
        return descriptions.get(image, image)
        
    def _estimate_cloud_run_cost(self) -> float:
        """Estimate monthly cost for Cloud Run service"""
        # Google Cloud Run pricing (simplified)
        
        # CPU pricing: $0.000024 per vCPU-second
        # Memory pricing: $0.0000025 per GiB-second
        # Requests pricing: $0.40 per million requests
        
        # Parse CPU limit
        if self.cpu_limit.endswith("m"):
            cpu_cores = int(self.cpu_limit[:-1]) / 1000
        else:
            cpu_cores = float(self.cpu_limit)
            
        # Parse memory limit
        if self.memory_limit.endswith("Mi"):
            memory_mb = int(self.memory_limit[:-2])
            memory_gb = memory_mb / 1024
        elif self.memory_limit.endswith("Gi"):
            memory_gb = int(self.memory_limit[:-2])
        else:
            memory_gb = 0.5  # Default fallback
            
        # Estimate usage (these are rough estimates)
        requests_per_month = 100000  # 100K requests per month
        avg_request_duration = 0.5   # 500ms average request duration
        cpu_utilization = 0.3        # 30% CPU utilization during requests
        
        # Calculate resource costs
        total_cpu_seconds = requests_per_month * avg_request_duration * cpu_utilization
        total_memory_seconds = requests_per_month * avg_request_duration
        
        cpu_cost = total_cpu_seconds * cpu_cores * 0.000024
        memory_cost = total_memory_seconds * memory_gb * 0.0000025
        request_cost = (requests_per_month / 1000000) * 0.40
        
        # Add minimum instance costs if min_instances > 0
        minimum_instance_cost = 0
        if self.min_instances > 0:
            # Cost for always-on instances
            seconds_per_month = 30 * 24 * 3600  # ~2.6M seconds
            minimum_instance_cost = (
                self.min_instances * seconds_per_month * 
                (cpu_cores * 0.000024 + memory_gb * 0.0000025)
            )
        
        total_cost = cpu_cost + memory_cost + request_cost + minimum_instance_cost
        
        return total_cost
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of Cloud Run service from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get service information
            if self.cloud_run_manager:
                service_info = self.cloud_run_manager.get_service_info(
                    self.service_name, self.region
                )
                
                if service_info:
                    return {
                        "exists": True,
                        "service_name": self.service_name,
                        "region": self.region,
                        "image_url": service_info.get("image", ""),
                        "cpu": service_info.get("cpu", ""),
                        "memory": service_info.get("memory", ""),
                        "port": service_info.get("port", 8080),
                        "min_instances": service_info.get("min_instances", 0),
                        "max_instances": service_info.get("max_instances", 100),
                        "allow_unauthenticated": service_info.get("allow_unauthenticated", False),
                        "environment_variables": service_info.get("environment_variables", {}),
                        "labels": service_info.get("labels", {}),
                        "url": service_info.get("url", ""),
                        "status": service_info.get("status", "unknown"),
                        "last_updated": service_info.get("updated", ""),
                        "revision_id": service_info.get("revision_id", ""),
                        "traffic_allocation": service_info.get("traffic", {}),
                        "custom_domain": service_info.get("custom_domain"),
                        "vpc_connector": service_info.get("vpc_connector"),
                        "service_account": service_info.get("service_account")
                    }
                else:
                    return {
                        "exists": False,
                        "service_name": self.service_name,
                        "region": self.region
                    }
            else:
                return {
                    "exists": False,
                    "service_name": self.service_name,
                    "region": self.region,
                    "error": "Cloud Run manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch Cloud Run state: {str(e)}")
            return {
                "exists": False,
                "service_name": self.service_name,
                "region": self.region,
                "error": str(e)
            }
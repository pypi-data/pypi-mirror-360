import os
import time
import hashlib
from typing import Dict, Any, Optional, List
from ..base_resource import BaseGcpResource
from ..auth_service import GcpAuthenticationService
from ...googlecloud_managers.gcp_client import GcpClient
from ...googlecloud_managers.cloud_run_manager import CloudRunManager, CloudRunConfig
from ...googlecloud_managers.artifact_registry_manager import ArtifactRegistryManager, RegistryConfig
from ...googlecloud_managers.status_reporter import GcpStatusReporter
from ...googlecloud_managers.service_manager import GcpServiceManager
from infradsl.container_engines.builder import ContainerBuilder
from infradsl.container_engines.exceptions import NoEngineFoundError


def resolve_template_path(template_path: str) -> str:
    """
    Resolve template path to absolute path, handling relative paths intelligently.

    This function searches for templates in common locations:
    1. Relative to current working directory
    2. Relative to project root (infradsl directory)
    3. Relative to script location

    Args:
        template_path: Template path (e.g., "templates/nodejs-webapp")

    Returns:
        Absolute path to template directory

    Raises:
        FileNotFoundError: If template directory cannot be found
    """
    # If already absolute and exists, return as-is
    if os.path.isabs(template_path) and os.path.exists(template_path):
        return template_path

    # Search locations in order of preference
    search_paths = [
        # 1. Relative to current working directory
        os.path.join(os.getcwd(), template_path),

        # 2. Relative to project root (look for infradsl directory)
        os.path.join(os.getcwd(), "..", "..", template_path),
        os.path.join(os.getcwd(), "..", template_path),

        # 3. Assume template_path starts with "templates/" and try project root
        os.path.join(os.getcwd(), "..", "..", template_path) if template_path.startswith("templates/") else None,

        # 4. Check if we're in a subdirectory and try going up to find templates
        os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), template_path),
    ]

    # Filter out None values
    search_paths = [path for path in search_paths if path is not None]

    # Try each search path
    for search_path in search_paths:
        abs_path = os.path.abspath(search_path)
        if os.path.exists(abs_path) and os.path.isdir(abs_path):
            return abs_path

    # If not found, raise descriptive error
    raise FileNotFoundError(
        f"Template directory '{template_path}' not found. "
        f"Searched locations: {search_paths[:3]}... "
        f"Current working directory: {os.getcwd()}"
    )


class CloudRun(BaseGcpResource):
    """Rails-like Cloud Run service orchestrator - serverless containers made simple"""

    def __init__(self, name: str):
        self.config = CloudRunConfig(service_name=name, image_url="")
        self._repository_created = False
        self._container_builder = None
        super().__init__(name)

    def _initialize_managers(self):
        """Initialize Cloud Run specific managers"""
        self.cloud_run_manager = None
        self.artifact_registry_manager = None

    def _ensure_authenticated(self):
        """Override to use Cloud Run specific authentication"""
        if not self._auto_authenticated:
            # Use silent mode for subsequent authentication calls to reduce noise
            BaseGcpResource._auth_call_count += 1
            silent = BaseGcpResource._auth_call_count > 1

            GcpAuthenticationService.authenticate_for_cloud_run(self.gcp_client, silent=silent)
            self._post_authentication_setup()
            self._auto_authenticated = True

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.cloud_run_manager = CloudRunManager(self.gcp_client)
        self.artifact_registry_manager = ArtifactRegistryManager(self.gcp_client)
        # Initialize universal container builder
        try:
            self._container_builder = ContainerBuilder(
                project_id=self.gcp_client.project,
                location=self.config.location or "us-central1"
            )
            print(f"🐳 Container builder initialized for Cloud Run")
        except NoEngineFoundError:
            print("⚠️  No container engine found - container builds will not be available")
            self._container_builder = None
        except Exception as e:
            print(f"⚠️  Container builder initialization failed: {e}")
            self._container_builder = None

    def container_engine_status(self) -> Dict[str, Any]:
        """Check container engine status - Rails-like developer convenience"""
        if not self._container_builder:
            return {
                "available": False,
                "error": "No container engine detected",
                "suggestion": "Install Docker Desktop or Podman to enable container builds"
            }

        return self._container_builder.get_build_status()

    def print_container_status(self):
        """Print Rails-like container engine status report"""
        if not self._container_builder:
            print("❌ No container engine available")
            print("💡 Install Docker Desktop or Podman to enable container builds")
            return

        self._container_builder.print_build_status()

    def container(self, image_name: str, template_path: str, port: int = 8080, template: str = "auto") -> 'CloudRun':
        """Deploy container from template with universal container engine (Rails magic!)"""

        # Resolve template path to absolute path
        try:
            resolved_template_path = resolve_template_path(template_path)
            print(f"📁 Resolved template path: {template_path} -> {resolved_template_path}")
        except FileNotFoundError as e:
            print(f"❌ Template path error: {e}")
            raise

        # Check if we're in destroy mode - skip expensive build operations
        if os.getenv('INFRA_MODE') == 'destroy':
            # For destroy operations, we just need to know the service configuration
            # No need to build or push containers
            self._ensure_authenticated()
            repository_url = f"europe-north1-docker.pkg.dev/{self.gcp_client.project}/infradsl-apps"
            self.config.image_url = f"{repository_url}/{image_name}:latest"
            self.config.port = port
            print(f"🗑️  Skipping container build for destroy operation")
            print(f"   📦 Target image: {self.config.image_url}")
            return self

        # Check if we're in preview mode - skip expensive build operations
        if os.getenv('INFRA_MODE') == 'preview':
            # For preview operations, we just need to show the configuration
            # No need to build or push containers
            self._ensure_authenticated()
            repository_url = f"europe-north1-docker.pkg.dev/{self.gcp_client.project}/infradsl-apps"
            self.config.image_url = f"{repository_url}/{image_name}:latest"
            self.config.port = port
            print(f"📋 Preview mode: Container will be built from {resolved_template_path}")
            print(f"   📦 Target image: {self.config.image_url}")
            print(f"   🏗️  Template: {template}")
            print(f"   🔌 Port: {port}")
            return self

        # Normal create/apply mode - build and push with universal container engine
        self._ensure_authenticated()

        # Create repository if needed
        if not self._repository_created:
            repo_config = RegistryConfig(repository_name="infradsl-apps")
            self.artifact_registry_manager.create_repository(repo_config)
            self._repository_created = True

        # Use universal container builder if available
        if self._container_builder:
            print(f"🚀 Building container with universal engine (Rails-like)")
            try:
                # Build and push with the new universal system
                build_result = self._container_builder.build_and_push_for_cloud_run(
                    service_name=self.config.service_name,
                    source_path=resolved_template_path,
                    template=template,
                    port=port
                )

                if build_result.get('push_successful'):
                    self.config.image_url = build_result['deployed_image']
                    self.config.port = port
                    print(f"✅ Universal container build successful!")
                    print(f"   📦 Image: {self.config.image_url}")
                    print(f"   🔌 Port: {port}")
                    print(f"   🏗️  Template: {build_result.get('template', 'auto')}")
                    return self
                else:
                    print(f"⚠️  Universal container build failed, falling back to legacy method")

            except Exception as e:
                print(f"⚠️  Universal container engine failed: {e}")
                print(f"🔄 Falling back to legacy container build method")

        # Fallback to legacy build method
        # Generate unique tag to ensure fresh builds when code changes
        tag = self._generate_unique_tag(resolved_template_path)
        print(f"🏷️  Using dynamic tag: {tag} (ensures fresh build with code changes)")

        # Build and push image
        repository_url = f"europe-north1-docker.pkg.dev/{self.gcp_client.project}/infradsl-apps"
        image_info = self.artifact_registry_manager.build_and_push_image(
            image_name=image_name,
            tag=tag,
            template_path=resolved_template_path,
            repository_url=repository_url,
            port=port
        )

        self.config.image_url = image_info["full_url"]
        self.config.port = port
        return self

    def image(self, image_url: str) -> 'CloudRun':
        """Use existing container image"""
        self.config.image_url = image_url
        return self

    def port(self, port: int) -> 'CloudRun':
        """Set the container port (default: 8080)"""
        self.config.port = port
        return self

    def memory(self, memory: str) -> 'CloudRun':
        """Set memory limit (e.g., '512Mi', '1Gi')"""
        self.config.memory = memory
        return self

    def cpu(self, cpu: str) -> 'CloudRun':
        """Set CPU limit (e.g., '1000m', '2000m')"""
        self.config.cpu = cpu
        return self

    def location(self, location: str) -> 'CloudRun':
        """Set the deployment location"""
        self.config.location = location
        return self

    def auto_scale(self, min_instances: int = 0, max_instances: int = 10) -> 'CloudRun':
        """Configure auto-scaling"""
        self.config.min_instances = min_instances
        self.config.max_instances = max_instances
        return self

    def scaling(self, min_instances: int = 0, max_instances: int = 10) -> 'CloudRun':
        """Configure scaling (alias for auto_scale)"""
        return self.auto_scale(min_instances, max_instances)

    def environment(self, env_vars: Dict[str, str]) -> 'CloudRun':
        """Set environment variables"""
        self.config.environment_variables = env_vars
        return self

    def timeout(self, seconds: int) -> 'CloudRun':
        """Set request timeout in seconds"""
        self.config.timeout = seconds
        return self

    def concurrency(self, concurrency: int) -> 'CloudRun':
        """Set maximum concurrent requests per instance"""
        self.config.concurrency = concurrency
        return self

    def private(self) -> 'CloudRun':
        """Make service private (require authentication)"""
        self.config.allow_unauthenticated = False
        return self

    def public(self) -> 'CloudRun':
        """Make service public (allow unauthenticated access)"""
        self.config.allow_unauthenticated = True
        return self

    def labels(self, labels: Dict[str, str]) -> 'CloudRun':
        """Add labels for organization"""
        self.config.labels = labels
        return self

    def domain(self, domain: str) -> 'CloudRun':
        """Configure custom domain with automatic SSL certificate"""
        self.config.custom_domain = domain
        self.config.auto_ssl = True
        return self

    def ssl_certificate(self, certificate_name: str) -> 'CloudRun':
        """Use a specific SSL certificate instead of automatic"""
        self.config.ssl_certificate = certificate_name
        self.config.auto_ssl = False
        return self

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, updated, or removed"""
        self._ensure_authenticated()

        # Discover existing services to determine what will happen
        existing_services = self._discover_existing_services()
        
        # Determine what will happen
        service_exists = self.config.service_name in existing_services
        to_create = [] if service_exists else [self.config.service_name]
        to_keep = [self.config.service_name] if service_exists else []
        to_remove = [name for name in existing_services.keys() if name != self.config.service_name]

        # Print simple header without formatting
        print(f"🔍 Cloud Run Service Preview")

        # Show infrastructure changes (only actionable changes)
        changes_needed = to_create or to_remove
        
        if changes_needed:
            print(f"📋 Infrastructure Changes:")
            
            if to_create:
                print(f"🆕 SERVICES to CREATE:  {', '.join(to_create)}")
                # Show details about service being created
                print(f"   ╭─ 🚀 {self.config.service_name}")
                print(f"   ├─ 📍 Location: {self.config.location}")
                print(f"   ├─ 🐳 Image: {self.config.image_url or 'Will be built from template'}")
                print(f"   ├─ 💾 Memory: {self.config.memory}")
                print(f"   ├─ 🖥️  CPU: {self.config.cpu}")
                print(f"   ├─ 📊 Auto-scaling: {self.config.min_instances}-{self.config.max_instances}")
                print(f"   ╰─ 🌐 Public: {'Yes' if self.config.allow_unauthenticated else 'No'}")
                print()
                
            if to_remove:
                print(f"🗑️  SERVICES to REMOVE:")
                # Show details about services being removed
                for service_name in to_remove:
                    service_info = existing_services.get(service_name)
                    if service_info:
                        status = service_info.get('status', 'unknown')
                        url = service_info.get('url', 'unknown')
                        status_icon = '🟢' if 'ready' in status.lower() else '🟡'
                        
                        # Pretty format with box drawing
                        print(f"   ╭─ 🚀 {service_name}")
                        print(f"   ├─ 📍 Location: {service_info.get('location', 'unknown')}")
                        print(f"   ├─ 🌐 URL: {url}")
                        print(f"   ╰─ {status_icon} Status: {status}")
                        print()
        else:
            print(f"✨ No changes needed - infrastructure matches configuration")

        # Show unchanged services summary
        if to_keep:
            print(f"📋 Unchanged: {len(to_keep)} service(s) remain the same")

        return {
            "service_name": self.config.service_name,
            "location": self.config.location,
            "to_create": to_create,
            "to_keep": to_keep,
            "to_remove": to_remove,
            "existing_services": existing_services,
            "image": self.config.image_url,
            "memory": self.config.memory,
            "cpu": self.config.cpu,
            "auto_scale": f"{self.config.min_instances}-{self.config.max_instances}",
            "public": self.config.allow_unauthenticated
        }

    def create(self) -> Dict[str, Any]:
        """Create/update Cloud Run service and remove any that are no longer needed"""
        self._ensure_authenticated()

        if not self.config.image_url:
            raise ValueError("No container image specified. Use .container() or .image() first.")

        # Discover existing services to determine what changes are needed
        existing_services = self._discover_existing_services()
        service_exists = self.config.service_name in existing_services
        to_create = [] if service_exists else [self.config.service_name]
        to_remove = [name for name in existing_services.keys() if name != self.config.service_name]

        # Show infrastructure changes
        print(f"\n🔍 Cloud Run Service")

        changes_needed = to_create or to_remove
        if changes_needed:
            print(f"📋 Infrastructure Changes:")
            
            if to_create:
                print(f"🆕 SERVICES to CREATE:  {', '.join(to_create)}")
                
            if to_remove:
                print(f"🗑️  SERVICES to REMOVE:")
                # Show details about services being removed
                for service_name in to_remove:
                    service_info = existing_services.get(service_name)
                    if service_info:
                        status = service_info.get('status', 'unknown')
                        url = service_info.get('url', 'unknown')
                        status_icon = '🟢' if 'ready' in status.lower() else '🟡'
                        
                        # Pretty format with box drawing
                        print(f"   ╭─ 🚀 {service_name}")
                        print(f"   ├─ 📍 Location: {service_info.get('location', 'unknown')}")
                        print(f"   ├─ 🌐 URL: {url}")
                        print(f"   ╰─ {status_icon} Status: {status}")
                        print()
        else:
            print(f"✨ No changes needed - infrastructure matches configuration")

        try:
            # Remove services that are no longer needed
            for service_name in to_remove:
                print(f"🗑️  Removing service: {service_name}")
                success = self.cloud_run_manager.delete_service(service_name, self.config.location)
                if success:
                    print(f"✅ Service removed successfully: {service_name}")

            # Create/update the service that is in the configuration
            if service_exists:
                print(f"🔄 Updating service: {self.config.service_name}")
            else:
                print(f"🆕 Creating service: {self.config.service_name}")

            # Use domain mapping method if custom domain is specified
            if self.config.custom_domain:
                result = self.cloud_run_manager.configure_service_with_domain(self.config)
            else:
                result = self.cloud_run_manager.create_service(self.config)

            print(f"✅ Service ready: {self.config.service_name}")
            print(f"   🌐 URL: {result['url']}")
            if self.config.custom_domain:
                print(f"   🌐 Custom Domain: https://{self.config.custom_domain}")

            # Add change tracking to result
            result["changes"] = {
                "created": to_create,
                "removed": to_remove,
                "updated": [self.config.service_name] if service_exists else []
            }

            return result

        except Exception as e:
            print(f"❌ Failed to manage Cloud Run service: {str(e)}")
            raise

    def _discover_existing_services(self) -> Dict[str, Any]:
        """Discover existing Cloud Run services in the current location"""
        try:
            existing_services = {}
            
            # Get all services in the location
            services = self.cloud_run_manager.list_services(self.config.location)
            
            for service in services:
                service_name = service.get('name', '')
                # Remove the full path prefix to get just the service name
                if '/' in service_name:
                    service_name = service_name.split('/')[-1]
                
                if service_name:
                    existing_services[service_name] = {
                        'name': service_name,
                        'location': self.config.location,
                        'url': service.get('url', ''),
                        'status': service.get('status', 'unknown'),
                        'created': service.get('created', ''),
                        'updated': service.get('updated', '')
                    }
            
            return existing_services
            
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to discover existing Cloud Run services: {str(e)}")
            return {}

    def destroy(self) -> Dict[str, Any]:
        """Destroy the Cloud Run service"""
        self._ensure_authenticated()

        print(f"\n🗑️  DESTROY OPERATION")
        print("=" * 50)
        print(f"📋 Resources to be destroyed:")
        print(f"   🚀 Cloud Run Service: {self.config.service_name}")
        print(f"   📍 Location: {self.config.location}")
        if self.config.image_url:
            print(f"   📦 Container Image: {self.config.image_url}")
        print("=" * 50)
        print("⚠️  WARNING: This will permanently delete the above resources!")
        print("   The container image in the registry will remain.")
        print("=" * 50)

        # First check if the service exists
        existing_service = self.cloud_run_manager.get_service_info(self.config.service_name, self.config.location)

        if not existing_service:
            print(f"ℹ️  Cloud Run service '{self.config.service_name}' doesn't exist - nothing to destroy")
            print(f"   This is normal if the resource was already deleted.")
            return {"success": True, "service_name": self.config.service_name, "status": "not_found"}

        # Service exists, proceed with deletion
        success = self.cloud_run_manager.delete_service(self.config.service_name, self.config.location)

        if success:
            print(f"✅ Cloud Run service destroyed: {self.config.service_name}")
            return {"success": True, "service_name": self.config.service_name, "status": "destroyed"}
        else:
            print(f"⚠️  Failed to destroy Cloud Run service: {self.config.service_name}")
            return {"success": False, "service_name": self.config.service_name, "status": "failed"}

    def _generate_unique_tag(self, template_path: str) -> str:
        """Generate a unique tag based on code content and timestamp"""
        try:
            # Get content hash of template directory
            content_hash = self._hash_directory_contents(template_path)

            # Use timestamp for uniqueness
            timestamp = str(int(time.time()))

            # Combine for unique tag (keep it short for container registries)
            tag = f"{content_hash[:8]}-{timestamp[-6:]}"
            return tag
        except Exception:
            # Fallback to timestamp if hashing fails
            return f"build-{int(time.time())}"

    def _hash_directory_contents(self, directory: str) -> str:
        """Generate hash of directory contents to detect code changes"""
        hash_md5 = hashlib.md5()

        try:
            for root, dirs, files in os.walk(directory):
                # Sort to ensure consistent hashing
                for filename in sorted(files):
                    # Skip hidden files and common ignores
                    if filename.startswith('.') or filename in ['node_modules', '__pycache__']:
                        continue

                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'rb') as f:
                            # Hash file path and content
                            hash_md5.update(filepath.encode())
                            hash_md5.update(f.read())
                    except (OSError, IOError):
                        # Skip files that can't be read
                        continue

            return hash_md5.hexdigest()
        except Exception:
            # If anything fails, use directory path as fallback
            hash_md5.update(directory.encode())
            return hash_md5.hexdigest()

    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the Cloud Run service from Google Cloud
        
        This method is required by the BaseGcpResource for drift detection.
        
        Returns:
            Dictionary representing current Cloud Run service state
        """
        try:
            self._ensure_authenticated()
            
            # Get current service information from Google Cloud
            service_info = self.cloud_run_manager.get_service_info(
                self.config.service_name, 
                self.config.location
            )
            
            if not service_info:
                return {"exists": False, "service_name": self.config.service_name}
            
            # Extract relevant state information for drift detection
            current_state = {
                "exists": True,
                "service_name": self.config.service_name,
                "location": self.config.location,
                "image_url": service_info.get("image", ""),
                "cpu": service_info.get("cpu", ""),
                "memory": service_info.get("memory", ""),
                "port": service_info.get("port", 8080),
                "min_instances": service_info.get("min_instances", 0),
                "max_instances": service_info.get("max_instances", 10),
                "allow_unauthenticated": service_info.get("allow_unauthenticated", False),
                "environment_variables": service_info.get("environment_variables", {}),
                "labels": service_info.get("labels", {}),
                "url": service_info.get("url", ""),
                "status": service_info.get("status", "unknown"),
                "last_updated": service_info.get("updated", ""),
                "revision_id": service_info.get("revision_id", "")
            }
            
            return current_state
            
        except Exception as e:
            # If we can't fetch state, return minimal info for drift detection
            return {
                "exists": False,
                "service_name": self.config.service_name,
                "error": str(e),
                "fetch_failed": True
            }

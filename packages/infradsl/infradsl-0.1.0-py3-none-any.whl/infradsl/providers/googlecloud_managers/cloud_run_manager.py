from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from google.cloud import run_v2
from .gcp_client import GcpClient

class CloudRunConfig(BaseModel):
    service_name: str
    image_url: str
    port: int = 8080
    location: str = "europe-north1"
    memory: str = "512Mi"  # Minimum required by Cloud Run with CPU allocation
    cpu: str = "1000m"
    min_instances: int = 0
    max_instances: int = 10
    timeout: int = 300
    concurrency: int = 80
    environment_variables: Optional[Dict[str, str]] = None
    allow_unauthenticated: bool = False
    labels: Optional[Dict[str, str]] = None
    custom_domain: Optional[str] = None
    ssl_certificate: Optional[str] = None
    auto_ssl: bool = True  # Automatically provision SSL when domain is set

class CloudRunManager:
    """Manages Google Cloud Run operations with Rails-like simplicity"""

    def __init__(self, gcp_client: GcpClient):
        self.gcp_client = gcp_client
        # Don't access client properties immediately - they require authentication
        self._services_client = None
        self._project_id = None

    @property
    def services_client(self):
        """Get the Cloud Run services client (lazy loading after authentication)"""
        if not self._services_client:
            self._services_client = run_v2.ServicesClient(
                credentials=self.gcp_client.credentials
            )
        return self._services_client

    @property
    def project_id(self):
        """Get the project ID (lazy loading after authentication)"""
        if not self._project_id:
            self._project_id = self.gcp_client.project
        return self._project_id

    def create_service(self, config: CloudRunConfig) -> Dict[str, Any]:
        """Create or update a Cloud Run service with intelligent state management (Rails-like)"""
        try:
            # First, check if service already exists (Rails magic!)
            existing_service = self.get_service_info(config.service_name, config.location)

            if existing_service:
                print(f"🔄 Service '{config.service_name}' exists - applying smart updates...")
                return self._smart_update_service(config, existing_service)
            else:
                print(f"🚀 Creating new Cloud Run service: {config.service_name}")
                return self._create_new_service(config)

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Failed to create/update Cloud Run service: {error_msg}")

            # Provide helpful context for common errors
            if "service.name must be empty" in error_msg:
                print(f"   💡 This is a known API issue - service name should not be in service object")
            elif "already exists" in error_msg.lower():
                print(f"   💡 Service already exists - applying smart updates...")
                return self._smart_update_service(config, None)
            elif "permission" in error_msg.lower():
                print(f"   💡 Check Cloud Run permissions for project {self.project_id}")
            elif "reserved env names" in error_msg and "PORT" in error_msg:
                print(f"   💡 PORT environment variable is automatically set by Cloud Run")
            elif "memory" in error_msg.lower() and "512" in error_msg:
                print(f"   💡 Cloud Run requires minimum 512Mi memory with CPU allocation")
            elif "failed to start and listen" in error_msg:
                print(f"   💡 Container startup failed - check these common issues:")
                print(f"      • App must listen on HOST 0.0.0.0 (not localhost)")
                print(f"      • App must listen on PORT from environment variable")
                print(f"      • Container must expose the correct port")
                print(f"      • Health check endpoint (/health) should return 200 OK")
            elif "cannot serve traffic" in error_msg:
                print(f"   💡 Container health check failed:")
                print(f"      • Ensure app starts within timeout (default: 240s)")
                print(f"      • App must respond to HTTP requests on configured port")
                print(f"      • Check container logs for startup errors")

            raise

    def _create_new_service(self, config: CloudRunConfig) -> Dict[str, Any]:
        """Create a new Cloud Run service"""
        print(f"   🐳 Image: {config.image_url}")
        print(f"   📍 Location: {config.location}")
        print(f"   💾 Memory: {config.memory}")
        print(f"   🖥️  CPU: {config.cpu}")
        print(f"   📊 Scaling: {config.min_instances}-{config.max_instances} instances")

        # Build environment variables
        env_vars = []
        if config.environment_variables:
            for key, value in config.environment_variables.items():
                # Skip PORT as it's automatically set by Cloud Run
                if key.upper() != "PORT":
                    env_vars.append(run_v2.EnvVar(name=key, value=value))

        # Build the container spec
        container = run_v2.Container(
            image=config.image_url,
            ports=[run_v2.ContainerPort(container_port=config.port)],
            env=env_vars,
            resources=run_v2.ResourceRequirements(
                limits={
                    "memory": config.memory,
                    "cpu": config.cpu
                }
            )
        )

        # Build the revision template
        template = run_v2.RevisionTemplate(
            scaling=run_v2.RevisionScaling(
                min_instance_count=config.min_instances,
                max_instance_count=config.max_instances
            ),
            timeout=f"{config.timeout}s",
            max_instance_request_concurrency=config.concurrency,
            containers=[container],
            labels=config.labels or {}
        )

        # Build the service spec
        service = run_v2.Service(
            template=template,
            labels=config.labels or {}
        )

        # Create the service
        parent = f"projects/{self.project_id}/locations/{config.location}"
        request = run_v2.CreateServiceRequest(
            parent=parent,
            service=service,
            service_id=config.service_name
        )

        print(f"   ⏳ Creating service (this may take 2-3 minutes)...")

        operation = self.services_client.create_service(request=request)

        # Wait for the operation to complete
        result = operation.result(timeout=300)

        print(f"✅ Cloud Run service created successfully!")
        print(f"   🎯 Service: {config.service_name}")
        print(f"   🌐 URL: {result.uri}")

        # Configure IAM for public access if requested
        if config.allow_unauthenticated:
            print(f"   🔓 Configuring public access...")
            self._allow_unauthenticated_access(config.service_name, config.location)

        return {
            "service_name": config.service_name,
            "url": result.uri,
            "location": config.location,
            "image": config.image_url,
            "status": result.latest_ready_revision,
            "project_id": self.project_id
        }

    def _smart_update_service(self, config: CloudRunConfig, existing_service: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Intelligently update service - only change what's different (Rails magic!)"""
        changes_made = []

        # Update the service configuration
        print(f"   📋 Analyzing configuration changes...")

        # Always update the service with new config (Cloud Run handles no-op updates efficiently)
        print(f"   🔄 Updating service configuration...")
        updated_service = self.update_service(config)
        changes_made.append("service configuration")

        # Handle public/private access changes (The Lego Principle!)
        current_is_public = self._check_if_service_is_public(config.service_name, config.location)
        desired_is_public = config.allow_unauthenticated

        if current_is_public != desired_is_public:
            if desired_is_public:
                print(f"   🔓 Making service public (adding .public() access)...")
                self._allow_unauthenticated_access(config.service_name, config.location)
                changes_made.append("enabled public access")
            else:
                print(f"   🔐 Making service private (removing public access)...")
                self._remove_unauthenticated_access(config.service_name, config.location)
                changes_made.append("disabled public access")
        else:
            if desired_is_public:
                print(f"   ✅ Service already public")
            else:
                print(f"   ✅ Service already private")

        print(f"🎯 Smart update complete! Changes: {', '.join(changes_made) if changes_made else 'no changes needed'}")
        return updated_service

    def _check_if_service_is_public(self, service_name: str, location: str) -> bool:
        """Check if service allows unauthenticated access"""
        try:
            from google.iam.v1 import iam_policy_pb2

            service_resource = f"projects/{self.project_id}/locations/{location}/services/{service_name}"
            request = iam_policy_pb2.GetIamPolicyRequest(resource=service_resource)

            policy = self.services_client.get_iam_policy(request=request)

            # Check if allUsers has run.invoker role
            for binding in policy.bindings:
                if binding.role == "roles/run.invoker" and "allUsers" in binding.members:
                    return True

            return False
        except Exception:
            # If we can't check, assume private (safer default)
            return False

    def _remove_unauthenticated_access(self, service_name: str, location: str):
        """Remove public access from Cloud Run service"""
        try:
            from google.iam.v1 import iam_policy_pb2, policy_pb2

            service_resource = f"projects/{self.project_id}/locations/{location}/services/{service_name}"

            # Get current policy
            get_request = iam_policy_pb2.GetIamPolicyRequest(resource=service_resource)
            current_policy = self.services_client.get_iam_policy(request=get_request)

            # Remove allUsers from run.invoker role
            updated_bindings = []
            for binding in current_policy.bindings:
                if binding.role == "roles/run.invoker":
                    # Remove allUsers from members
                    new_members = [member for member in binding.members if member != "allUsers"]
                    if new_members:  # Only keep binding if there are still members
                        updated_bindings.append(policy_pb2.Binding(
                            role=binding.role,
                            members=new_members
                        ))
                else:
                    updated_bindings.append(binding)

            # Set updated policy
            set_request = iam_policy_pb2.SetIamPolicyRequest(
                resource=service_resource,
                policy=policy_pb2.Policy(bindings=updated_bindings)
            )

            self.services_client.set_iam_policy(request=set_request)
            print(f"   ✅ Removed public access")

        except Exception as e:
            print(f"   ⚠️  Could not remove public access: {str(e)}")

    def _allow_unauthenticated_access(self, service_name: str, location: str):
        """Allow unauthenticated access to the Cloud Run service"""
        try:
            # Try using Cloud Run API directly first
            if self._configure_public_access_via_api(service_name, location):
                print(f"   ✅ Public access configured via API")
                return

            # Fallback to gcloud CLI if available
            import subprocess
            cmd = [
                "gcloud", "run", "services", "add-iam-policy-binding",
                service_name,
                f"--location={location}",
                "--member=allUsers",
                "--role=roles/run.invoker",
                "--quiet"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Public access configured via gcloud")
            else:
                print(f"   ⚠️  gcloud configuration failed: {result.stderr}")
                print(f"   💡 To make service public manually:")
                print(f"      gcloud run services add-iam-policy-binding {service_name} --location={location} --member=allUsers --role=roles/run.invoker")

        except Exception as e:
            print(f"   ⚠️  Could not configure public access: {str(e)}")
            print(f"   💡 To make service public manually:")
            print(f"      gcloud run services add-iam-policy-binding {service_name} --location={location} --member=allUsers --role=roles/run.invoker")

    def _configure_public_access_via_api(self, service_name: str, location: str) -> bool:
        """Configure public access using Cloud Run API directly"""
        try:
            from google.cloud import run_v2
            from google.iam.v1 import policy_pb2
            from google.iam.v1 import iam_policy_pb2

            # Get the service resource name
            service_resource = f"projects/{self.project_id}/locations/{location}/services/{service_name}"

            # Create IAM policy request
            request = iam_policy_pb2.SetIamPolicyRequest(
                resource=service_resource,
                policy=policy_pb2.Policy(
                    bindings=[
                        policy_pb2.Binding(
                            role="roles/run.invoker",
                            members=["allUsers"]
                        )
                    ]
                )
            )

            # Apply the IAM policy
            self.services_client.set_iam_policy(request=request)
            return True

        except Exception as e:
            # API method failed, will fall back to gcloud
            return False

    def update_service(self, config: CloudRunConfig) -> Dict[str, Any]:
        """Update an existing Cloud Run service"""
        try:
            print(f"🔄 Updating Cloud Run service: {config.service_name}")

            # Get the existing service
            service_name = f"projects/{self.project_id}/locations/{config.location}/services/{config.service_name}"
            get_request = run_v2.GetServiceRequest(name=service_name)
            existing_service = self.services_client.get_service(request=get_request)

            # Build updated environment variables
            env_vars = []
            if config.environment_variables:
                for key, value in config.environment_variables.items():
                    # Skip PORT as it's automatically set by Cloud Run
                    if key.upper() != "PORT":
                        env_vars.append(run_v2.EnvVar(name=key, value=value))

            # Update the container spec
            container = run_v2.Container(
                image=config.image_url,
                ports=[run_v2.ContainerPort(container_port=config.port)],
                env=env_vars,
                resources=run_v2.ResourceRequirements(
                    limits={
                        "memory": config.memory,
                        "cpu": config.cpu
                    }
                )
            )

            # Update the revision template
            existing_service.template.scaling.min_instance_count = config.min_instances
            existing_service.template.scaling.max_instance_count = config.max_instances
            existing_service.template.timeout = f"{config.timeout}s"
            existing_service.template.max_instance_request_concurrency = config.concurrency
            existing_service.template.containers = [container]

            # Update the service
            request = run_v2.UpdateServiceRequest(service=existing_service)

            print(f"   ⏳ Updating service...")
            operation = self.services_client.update_service(request=request)
            result = operation.result(timeout=300)

            print(f"✅ Cloud Run service updated successfully!")
            print(f"   🌐 URL: {result.uri}")

            return {
                "service_name": config.service_name,
                "url": result.uri,
                "location": config.location,
                "image": config.image_url,
                "status": result.latest_ready_revision,
                "project_id": self.project_id
            }

        except Exception as e:
            print(f"❌ Failed to update Cloud Run service: {str(e)}")
            raise

    def delete_service(self, service_name: str, location: str = "europe-north1") -> bool:
        """Delete a Cloud Run service"""
        try:
            print(f"🗑️  Deleting Cloud Run service: {service_name}")

            name = f"projects/{self.project_id}/locations/{location}/services/{service_name}"
            request = run_v2.DeleteServiceRequest(name=name)

            operation = self.services_client.delete_service(request=request)
            operation.result(timeout=300)

            print(f"✅ Cloud Run service deleted successfully!")
            return True

        except Exception as e:
            print(f"❌ Failed to delete Cloud Run service: {str(e)}")
            return False

    def get_service_info(self, service_name: str, location: str = "europe-north1") -> Optional[Dict[str, Any]]:
        """Get information about a Cloud Run service"""
        try:
            name = f"projects/{self.project_id}/locations/{location}/services/{service_name}"
            request = run_v2.GetServiceRequest(name=name)
            service = self.services_client.get_service(request=request)

            return {
                "name": service_name,
                "url": service.uri,
                "location": location,
                "status": service.latest_ready_revision,
                "traffic": service.traffic,
                "labels": dict(service.labels) if service.labels else {}
            }

        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                return None
            print(f"❌ Failed to get service info: {str(e)}")
            return None

    def list_services(self, location: str = "europe-north1") -> List[Dict[str, Any]]:
        """List all Cloud Run services in a location"""
        try:
            parent = f"projects/{self.project_id}/locations/{location}"
            request = run_v2.ListServicesRequest(parent=parent)

            services = []
            page_result = self.services_client.list_services(request=request)

            for service in page_result:
                services.append({
                    "name": service.name.split("/")[-1],
                    "url": service.uri,
                    "location": location,
                    "status": service.latest_ready_revision,
                    "labels": dict(service.labels) if service.labels else {}
                })

            return services

        except Exception as e:
            print(f"❌ Failed to list services: {str(e)}")
            return []

    def get_service_logs(self, service_name: str, location: str = "europe-north1",
                        lines: int = 100) -> List[str]:
        """Get recent logs for a Cloud Run service"""
        try:
            import subprocess

            cmd = [
                "gcloud", "logs", "read",
                f"resource.type=cloud_run_revision AND resource.labels.service_name={service_name}",
                f"--location={location}",
                f"--limit={lines}",
                "--format=value(textPayload)"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n') if result.stdout.strip() else []
            else:
                print(f"❌ Failed to get logs: {result.stderr}")
                return []

        except Exception as e:
            print(f"❌ Failed to get logs: {str(e)}")
            return []

    def scale_service(self, service_name: str, min_instances: int, max_instances: int,
                     location: str = "europe-north1") -> bool:
        """Scale a Cloud Run service"""
        try:
            print(f"📊 Scaling service {service_name}: {min_instances}-{max_instances} instances")

            # Get the existing service
            service_name_full = f"projects/{self.project_id}/locations/{location}/services/{service_name}"
            get_request = run_v2.GetServiceRequest(name=service_name_full)
            service = self.services_client.get_service(request=get_request)

            # Update scaling configuration
            service.template.scaling.min_instance_count = min_instances
            service.template.scaling.max_instance_count = max_instances

            # Update the service
            request = run_v2.UpdateServiceRequest(service=service)
            operation = self.services_client.update_service(request=request)
            operation.result(timeout=300)

            print(f"✅ Service scaled successfully!")
            return True

        except Exception as e:
            print(f"❌ Failed to scale service: {str(e)}")
            return False

    def _ensure_gcloud_available(self) -> bool:
        """Ensure gcloud CLI is available, install if needed"""
        import subprocess
        import os
        import shutil
        
        # Check if gcloud is already available
        if shutil.which("gcloud"):
            return True
            
        print("🔧 gcloud CLI not found, installing automatically...")
        
        try:
            # Install gcloud CLI for macOS
            install_cmd = "curl https://sdk.cloud.google.com | bash"
            result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Add to PATH for current session
                gcloud_path = os.path.expanduser("~/google-cloud-sdk/bin")
                if gcloud_path not in os.environ["PATH"]:
                    os.environ["PATH"] = f"{gcloud_path}:{os.environ['PATH']}"
                    
                print("✅ gcloud CLI installed successfully")
                return True
            else:
                print(f"❌ Failed to install gcloud CLI: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error installing gcloud CLI: {e}")
            return False

    def _authenticate_gcloud(self):
        """Authenticate gcloud with the same service account credentials"""
        import subprocess
        import os
        
        try:
            # Look for service account key file
            key_files = ["oopscli.json", "service-account.json", "credentials.json"]
            key_file = None
            
            for filename in key_files:
                if os.path.exists(filename):
                    key_file = filename
                    break
            
            if not key_file:
                print("⚠️  No service account key file found for gcloud authentication")
                return
            
            # Authenticate gcloud
            auth_cmd = [
                "gcloud", "auth", "activate-service-account",
                f"--key-file={key_file}",
                f"--project={self.project_id}"
            ]
            
            result = subprocess.run(auth_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ gcloud authenticated with {key_file}")
            else:
                print(f"⚠️  gcloud authentication failed: {result.stderr}")
                
        except Exception as e:
            print(f"⚠️  Error authenticating gcloud: {e}")

    def create_domain_mapping(self, service_name: str, domain: str, location: str = "europe-north1") -> Dict[str, Any]:
        """Create a custom domain mapping for a Cloud Run service using gcloud CLI"""
        import subprocess
        import json
        
        # Ensure gcloud CLI is available and authenticated
        if not self._ensure_gcloud_available():
            raise Exception("gcloud CLI is required for domain mapping but could not be installed")
        
        # Authenticate gcloud with the same service account
        self._authenticate_gcloud()
        
        try:
            print(f"🌐 Creating domain mapping: {domain} → {service_name}")

            # Use gcloud beta CLI for domain mapping (fully managed Cloud Run)
            cmd = [
                "gcloud", "beta", "run", "domain-mappings", "create",
                f"--service={service_name}",
                f"--domain={domain}",
                f"--region={location}",
                f"--project={self.project_id}",
                "--format=json",
                "--quiet"
            ]

            print(f"   ⏳ Creating domain mapping (this may take 2-3 minutes)...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print(f"✅ Domain mapping created successfully!")
                print(f"   🌐 Domain: {domain}")
                print(f"   🔒 SSL: Automatic (Let's Encrypt)")
                print(f"   ⚡ CDN: Enabled")

                return {
                    "domain": domain,
                    "service_name": service_name,
                    "ssl_certificate": "automatic",
                    "status": "ready"
                }
            else:
                error_msg = result.stderr
                if "already exists" in error_msg.lower():
                    print(f"ℹ️  Domain mapping already exists for {domain}")
                    return {
                        "domain": domain,
                        "service_name": service_name,
                        "ssl_certificate": "automatic",
                        "status": "existing"
                    }
                else:
                    raise Exception(f"gcloud command failed: {error_msg}")

        except subprocess.TimeoutExpired:
            print(f"❌ Domain mapping creation timed out")
            raise Exception("Domain mapping creation timed out")
        except Exception as e:
            print(f"❌ Failed to create domain mapping: {str(e)}")
            print(f"💡 Make sure:")
            print(f"   - Domain {domain} is verified in Google Cloud Console")
            print(f"   - DNS records point to Google Cloud Load Balancer")
            print(f"   - Domain Mapping API is enabled")
            print(f"   - gcloud CLI is installed and authenticated")
            raise

    def delete_domain_mapping(self, domain: str, location: str = "europe-north1") -> bool:
        """Delete a domain mapping using gcloud CLI"""
        import subprocess
        
        try:
            print(f"🗑️  Deleting domain mapping: {domain}")

            cmd = [
                "gcloud", "beta", "run", "domain-mappings", "delete", domain,
                f"--region={location}",
                f"--project={self.project_id}",
                "--quiet"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print(f"✅ Domain mapping deleted successfully!")
                return True
            else:
                print(f"❌ Failed to delete domain mapping: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ Domain mapping deletion timed out")
            return False
        except Exception as e:
            print(f"❌ Failed to delete domain mapping: {str(e)}")
            return False

    def configure_service_with_domain(self, config: CloudRunConfig) -> Dict[str, Any]:
        """Create service and configure custom domain if specified"""
        # First create the service
        result = self.create_service(config)

        # If custom domain is specified, create domain mapping
        if config.custom_domain:
            try:
                domain_result = self.create_domain_mapping(
                    config.service_name,
                    config.custom_domain,
                    config.location
                )
                result.update({
                    "custom_domain": config.custom_domain,
                    "ssl_enabled": True,
                    "domain_mapping": domain_result
                })

                print(f"\n🎉 Service deployed with custom domain!")
                print(f"   🌐 Service URL: {result['url']}")
                print(f"   🌐 Custom Domain: https://{config.custom_domain}")
                print(f"   🔒 SSL Certificate: Automatic")

            except Exception as e:
                print(f"⚠️  Service created but domain mapping failed: {e}")
                print(f"   🌐 Service URL: {result['url']}")
                print(f"   💡 You can configure the domain mapping later")

        return result

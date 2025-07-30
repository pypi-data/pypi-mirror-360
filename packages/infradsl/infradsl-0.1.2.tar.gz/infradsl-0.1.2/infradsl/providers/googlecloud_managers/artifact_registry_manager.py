import os
import json
import subprocess
import tempfile
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from google.cloud import artifactregistry_v1
from .gcp_client import GcpClient

class RegistryConfig(BaseModel):
    repository_name: str
    location: str = "europe-north1"
    format: str = "DOCKER"
    description: Optional[str] = None
    labels: Optional[Dict[str, str]] = None

class ArtifactRegistryManager:
    """Manages Google Cloud Artifact Registry operations with Rails-like simplicity"""

    def __init__(self, gcp_client: GcpClient):
        self.gcp_client = gcp_client
        # Don't access client properties immediately - they require authentication
        self._registry_client = None
        self._project_id = None

    @property
    def registry_client(self):
        """Get the artifact registry client (lazy loading after authentication)"""
        if not self._registry_client:
            self._registry_client = artifactregistry_v1.ArtifactRegistryClient(
                credentials=self.gcp_client.credentials
            )
        return self._registry_client

    @property
    def project_id(self):
        """Get the project ID (lazy loading after authentication)"""
        if not self._project_id:
            self._project_id = self.gcp_client.project
        return self._project_id

    def create_repository(self, config: RegistryConfig) -> Dict[str, Any]:
        """Create an Artifact Registry repository with Rails-like conventions"""
        try:
            print(f"🏗️  Creating Artifact Registry repository: {config.repository_name}")

            # Build the repository resource
            repository = artifactregistry_v1.Repository(
                name=f"projects/{self.project_id}/locations/{config.location}/repositories/{config.repository_name}",
                format_=artifactregistry_v1.Repository.Format.DOCKER,
                description=config.description or f"Docker repository for {config.repository_name}",
                labels=config.labels or {}
            )

            # Create the repository
            parent = f"projects/{self.project_id}/locations/{config.location}"
            request = artifactregistry_v1.CreateRepositoryRequest(
                parent=parent,
                repository_id=config.repository_name,
                repository=repository
            )

            print(f"   📍 Location: {config.location}")
            print(f"   📦 Format: Docker")
            print(f"   ⏳ Creating repository...")

            operation = self.registry_client.create_repository(request=request)
            result = operation.result(timeout=120)

            print(f"✅ Artifact Registry repository created successfully!")
            print(f"   🎯 Repository: {config.repository_name}")
            print(f"   🔗 URL: {config.location}-docker.pkg.dev/{self.project_id}/{config.repository_name}")

            return {
                "repository_name": config.repository_name,
                "location": config.location,
                "url": f"{config.location}-docker.pkg.dev/{self.project_id}/{config.repository_name}",
                "project_id": self.project_id,
                "format": "DOCKER"
            }

        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️  Repository '{config.repository_name}' already exists, continuing...")
                return {
                    "repository_name": config.repository_name,
                    "location": config.location,
                    "url": f"{config.location}-docker.pkg.dev/{self.project_id}/{config.repository_name}",
                    "project_id": self.project_id,
                    "format": "DOCKER"
                }
            else:
                print(f"❌ Failed to create repository: {str(e)}")
                raise

    def build_and_push_image(self, image_name: str, tag: str, template_path: str,
                           repository_url: str, port: int = 8080) -> Dict[str, Any]:
        """Build container image from template and push to Artifact Registry (supports Docker & Podman)"""
        try:
            # Detect available container engine
            container_engine = self._detect_container_engine()
            print(f"🐳 Building and pushing container image with {container_engine}...")
            print(f"   📦 Image: {image_name}:{tag}")
            print(f"   📁 Template: {template_path}")
            print(f"   🏪 Registry: {repository_url}")
            print(f"   🔧 Engine: {container_engine}")

            # Ensure template directory exists
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template directory not found: {template_path}")

            # Check for Dockerfile/Containerfile
            dockerfile_path = self._find_container_file(template_path)
            if not dockerfile_path:
                print(f"   🔧 No Dockerfile/Containerfile found, creating Rails-like default...")
                dockerfile_path = self._create_default_dockerfile(template_path, port)

            # Full image URL
            full_image_url = f"{repository_url}/{image_name}:{tag}"

            # Configure container engine authentication
            print(f"   🔐 Configuring {container_engine} authentication...")
            self._configure_container_auth(container_engine)

            # Build the container image
            print(f"   🔨 Building container image...")
            print(f"   📋 Using: {dockerfile_path}")
            print(f"   📁 Context: {template_path}")
            build_result = self._build_image(container_engine, full_image_url, template_path, dockerfile_path)

            if build_result.returncode != 0:
                print(f"   📋 Build output: {build_result.stdout}")
                print(f"   ❌ Build error: {build_result.stderr}")
                raise Exception(f"{container_engine} build failed: {build_result.stderr}")

            print(f"   ✅ Image built successfully")
            if build_result.stdout:
                print(f"   📋 Build log: {build_result.stdout[-200:]}")  # Last 200 chars

            # Push the image
            print(f"   ⬆️  Pushing image to registry...")
            push_result = self._push_image(container_engine, full_image_url)

            if push_result.returncode != 0:
                raise Exception(f"{container_engine} push failed: {push_result.stderr}")

            print(f"✅ Container image pushed successfully!")
            print(f"   🎯 Image URL: {full_image_url}")
            print(f"   🛠️  Built with: {container_engine}")

            return {
                "image_name": image_name,
                "tag": tag,
                "full_url": full_image_url,
                "repository_url": repository_url,
                "port": port,
                "template_path": template_path,
                "container_engine": container_engine
            }

        except Exception as e:
            print(f"❌ Failed to build and push image: {str(e)}")
            raise

    def _detect_container_engine(self) -> str:
        """Detect available container engine (Docker, Podman, etc.)"""
        engines = [
            ("podman", "Podman"),
            ("docker", "Docker"),
        ]

        for cmd, name in engines:
            try:
                result = subprocess.run([cmd, "--version"],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return name
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                continue

        raise Exception("No container engine found. Please install Docker or Podman.")

    def _find_container_file(self, template_path: str) -> Optional[str]:
        """Find Dockerfile or Containerfile in template directory"""
        container_files = ["Dockerfile", "Containerfile"]
        for filename in container_files:
            filepath = os.path.join(template_path, filename)
            if os.path.exists(filepath):
                return filepath
        return None

    def _configure_container_auth(self, container_engine: str):
        """Configure container engine to authenticate with Google Cloud"""
        try:
            if container_engine.lower() == "docker":
                self._configure_docker_auth()
            elif container_engine.lower() == "podman":
                self._configure_podman_auth()
            else:
                raise Exception(f"Unsupported container engine: {container_engine}")
        except Exception as e:
            print(f"⚠️  {container_engine} authentication may not be configured: {str(e)}")

    def _configure_docker_auth(self):
        """Configure Docker to authenticate with Google Cloud"""
        try:
            # First try: Use service account credentials directly (no gcloud CLI required)
            from google.oauth2 import service_account

            if isinstance(self.gcp_client.credentials, service_account.Credentials):
                # Try to get service account key file path if available
                if hasattr(self.gcp_client.credentials, '_service_account_email'):
                    # Use the credentials file if we can access it
                    if os.path.exists("oopscli.json"):
                        with open("oopscli.json", 'r') as f:
                            credentials_json = f.read()
                    else:
                        # Fallback: construct minimal service account info
                        credentials_json = json.dumps({
                            "type": "service_account",
                            "project_id": self.gcp_client.project,
                            "client_email": getattr(self.gcp_client.credentials, '_service_account_email', 'unknown'),
                        })

                    # Try using docker login with service account key
                    subprocess.run([
                        "docker", "login", "-u", "_json_key",
                        "--password-stdin", "europe-north1-docker.pkg.dev"
                    ], input=credentials_json, text=True, check=True, capture_output=True)
                    print("   ✅ Configured Docker authentication with service account")
                    return

        except Exception as e:
            print(f"⚠️  Service account authentication failed: {e}")

        try:
            # Second try: Use gcloud CLI if available
            subprocess.run([
                "gcloud", "auth", "configure-docker",
                f"europe-north1-docker.pkg.dev", "--quiet"
            ], check=True, capture_output=True)
            print("   ✅ Configured Docker authentication with gcloud")
        except subprocess.CalledProcessError:
            print("⚠️  gcloud authentication not available. This is normal if gcloud CLI is not installed.")
            print("   🔄 Using service account authentication instead")

    def _configure_podman_auth(self):
        """Configure Podman to authenticate with Google Cloud"""
        try:
            # First try: Use service account credentials directly (no gcloud CLI required)
            import base64
            from google.oauth2 import service_account

            if isinstance(self.gcp_client.credentials, service_account.Credentials):
                # Try to get service account key from file
                credentials_json = None
                if os.path.exists("oopscli.json"):
                    with open("oopscli.json", 'r') as f:
                        credentials_json = f.read()
                else:
                    # Fallback: construct minimal service account info
                    service_account_info = {
                        "type": "service_account",
                        "project_id": self.gcp_client.project,
                        "client_email": getattr(self.gcp_client.credentials, '_service_account_email', 'unknown'),
                    }
                    credentials_json = json.dumps(service_account_info)

                if credentials_json:
                    # Method 1: Try using podman login with service account key
                    try:
                        subprocess.run([
                            "podman", "login", "-u", "_json_key",
                            "--password-stdin", "europe-north1-docker.pkg.dev"
                        ], input=credentials_json, text=True, check=True, capture_output=True)
                        print("   ✅ Configured Podman authentication with service account (direct login)")
                        return
                    except subprocess.CalledProcessError:
                        pass

                    # Method 2: Create auth file for Podman
                    encoded_creds = base64.b64encode(f"_json_key:{credentials_json}".encode()).decode()
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        json.dump({
                            "auths": {
                                "europe-north1-docker.pkg.dev": {
                                    "auth": encoded_creds
                                }
                            }
                        }, f)
                        auth_file = f.name

                    # Set auth file for Podman
                    os.environ['REGISTRY_AUTH_FILE'] = auth_file
                    print("   ✅ Configured Podman authentication with service account (auth file)")
                    return

        except Exception as e:
            print(f"⚠️  Service account authentication failed: {e}")

        try:
            # Second try: Use gcloud CLI if available
            token_result = subprocess.run([
                "gcloud", "auth", "print-access-token"
            ], capture_output=True, text=True, check=True)

            access_token = token_result.stdout.strip()

            # Login to registry with Podman
            subprocess.run([
                "podman", "login", "-u", "oauth2accesstoken",
                "--password", access_token,
                "europe-north1-docker.pkg.dev"
            ], check=True, capture_output=True)
            print("   ✅ Configured Podman authentication with gcloud token")

        except subprocess.CalledProcessError as e:
            print(f"⚠️  gcloud authentication not available: {e}")
            print("   💡 This is normal if gcloud CLI is not installed")
            print("   🔄 Falling back to service account authentication")

    def _build_image(self, container_engine: str, image_url: str, template_path: str, dockerfile_path: str):
        """Build container image using specified engine with x86_64 architecture for Cloud Run"""
        if container_engine.lower() == "docker":
            return subprocess.run([
                "docker", "build",
                "--platform", "linux/amd64",
                "-f", dockerfile_path,
                "-t", image_url,
                template_path
            ], capture_output=True, text=True)
        elif container_engine.lower() == "podman":
            return subprocess.run([
                "podman", "build",
                "--platform", "linux/amd64",
                "-f", dockerfile_path,
                "-t", image_url,
                template_path
            ], capture_output=True, text=True)
        else:
            raise Exception(f"Unsupported container engine: {container_engine}")

    def _push_image(self, container_engine: str, image_url: str):
        """Push container image using specified engine"""
        if container_engine.lower() == "docker":
            return subprocess.run([
                "docker", "push", image_url
            ], capture_output=True, text=True)
        elif container_engine.lower() == "podman":
            return subprocess.run([
                "podman", "push", image_url
            ], capture_output=True, text=True)
        else:
            raise Exception(f"Unsupported container engine: {container_engine}")

    def _create_default_dockerfile(self, template_path: str, port: int) -> str:
        """Create a Rails-like default Dockerfile based on detected language"""
        print(f"   🔍 Analyzing template directory: {template_path}")

        # List files for debugging
        try:
            files = os.listdir(template_path)
            print(f"   📁 Found files: {', '.join(files[:10])}{'...' if len(files) > 10 else ''}")
        except Exception as e:
            print(f"   ⚠️  Could not list directory: {e}")

        dockerfile_content = self._detect_and_generate_dockerfile(template_path, port)

        # Try Containerfile first (Podman preference), then Dockerfile
        container_files = ["Containerfile", "Dockerfile"]
        dockerfile_path = None

        for filename in container_files:
            filepath = os.path.join(template_path, filename)
            try:
                with open(filepath, 'w') as f:
                    f.write(dockerfile_content)
                dockerfile_path = filepath
                print(f"   ✅ Generated default {filename} for detected stack")
                print(f"   📄 File size: {len(dockerfile_content)} bytes")
                break
            except Exception as e:
                print(f"   ⚠️  Failed to create {filename}: {e}")
                continue

        if not dockerfile_path:
            # Fallback to Dockerfile
            dockerfile_path = os.path.join(template_path, "Dockerfile")
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            print(f"   ✅ Generated default Dockerfile for detected stack")

        return dockerfile_path

    def _detect_and_generate_dockerfile(self, template_path: str, port: int) -> str:
        """Detect the application stack and generate appropriate Dockerfile"""

        # Check for various language/framework indicators
        try:
            files = os.listdir(template_path)
        except Exception as e:
            print(f"   ⚠️  Could not read directory {template_path}: {e}")
            return self._generate_generic_dockerfile(port)

        print(f"   🔍 Detecting stack from files: {files}")

        # Node.js detection
        if 'package.json' in files:
            print(f"   📦 Detected Node.js project (package.json found)")
            return self._generate_nodejs_dockerfile(template_path, port)

        # Python detection
        if 'requirements.txt' in files or 'app.py' in files or 'main.py' in files:
            print(f"   🐍 Detected Python project")
            return self._generate_python_dockerfile(template_path, port)

        # Go detection
        if 'go.mod' in files or any(f.endswith('.go') for f in files):
            print(f"   🚀 Detected Go project")
            return self._generate_go_dockerfile(template_path, port)

        # Java detection
        if 'pom.xml' in files or 'build.gradle' in files:
            print(f"   ☕ Detected Java project")
            return self._generate_java_dockerfile(template_path, port)

        # Default generic Dockerfile
        print(f"   🔧 No specific stack detected, using generic container")
        return self._generate_generic_dockerfile(port)

    def _generate_nodejs_dockerfile(self, template_path: str, port: int) -> str:
        """Generate Node.js Dockerfile/Containerfile"""
        # Check if package.json exists to determine install strategy
        package_json_exists = os.path.exists(os.path.join(template_path, "package.json"))

        if package_json_exists:
            # Check if package-lock.json exists for npm ci vs npm install
            lock_file_exists = os.path.exists(os.path.join(template_path, "package-lock.json"))
            if lock_file_exists:
                install_cmd = "RUN npm ci --omit=dev"
            else:
                install_cmd = "RUN npm install --omit=dev"
        else:
            install_cmd = "# No package.json found - skipping npm install"

        return f"""# Rails-like Node.js Containerfile (auto-generated, works with Docker & Podman)
FROM --platform=linux/amd64 node:18-alpine

WORKDIR /app

# Install basic tools
RUN apk add --no-cache wget curl

# Copy package files
COPY package*.json ./

# Install dependencies
{install_cmd}

# Copy application code
COPY . .

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \\
    adduser -S nodejs -u 1001 && \\
    chown -R nodejs:nodejs /app

USER nodejs

# Expose port
EXPOSE {port}

# Health check (compatible with both Docker and Podman)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1

# Start the application
CMD ["npm", "start"]
"""

    def _generate_python_dockerfile(self, template_path: str, port: int) -> str:
        """Generate Python Dockerfile/Containerfile"""
        return f"""# Rails-like Python Containerfile (auto-generated, works with Docker & Podman)
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE {port}

# Health check (compatible with both Docker and Podman)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1

# Start the application
CMD ["python", "app.py"]
"""

    def _generate_go_dockerfile(self, template_path: str, port: int) -> str:
        """Generate Go Dockerfile/Containerfile"""
        return f"""# Rails-like Go Containerfile (auto-generated, works with Docker & Podman)
FROM --platform=linux/amd64 golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Final stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates wget curl
WORKDIR /app

# Create non-root user for security
RUN addgroup -g 1001 -S appgroup && \\
    adduser -S appuser -u 1001 -G appgroup

# Copy the binary
COPY --from=builder /app/main .
RUN chown appuser:appgroup main

USER appuser

# Expose port
EXPOSE {port}

# Health check (compatible with both Docker and Podman)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1

# Start the application
CMD ["./main"]
"""

    def _generate_java_dockerfile(self, template_path: str, port: int) -> str:
        """Generate Java Dockerfile/Containerfile"""
        return f"""# Rails-like Java Containerfile (auto-generated, works with Docker & Podman)
FROM --platform=linux/amd64 openjdk:17-jre-slim

WORKDIR /app

# Install wget and curl for health checks
RUN apt-get update && apt-get install -y wget curl && rm -rf /var/lib/apt/lists/*

# Copy the JAR file (assumes Maven/Gradle build)
COPY target/*.jar app.jar 2>/dev/null || COPY build/libs/*.jar app.jar

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
RUN chown appuser:appuser app.jar
USER appuser

# Expose port
EXPOSE {port}

# Health check (compatible with both Docker and Podman)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1

# Start the application
CMD ["java", "-jar", "app.jar"]
"""

    def _generate_generic_dockerfile(self, port: int) -> str:
        """Generate generic Dockerfile/Containerfile"""
        return f"""# Rails-like Generic Containerfile (auto-generated, works with Docker & Podman)
FROM --platform=linux/amd64 ubuntu:22.04

WORKDIR /app

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Make any scripts executable
RUN chmod +x start.sh 2>/dev/null || true

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE {port}

# Health check (compatible with both Docker and Podman)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1

# Start the application
CMD ["./start.sh"]
"""

    def list_images(self, repository_name: str, location: str = "europe-north1") -> List[Dict[str, Any]]:
        """List Docker images in a repository"""
        try:
            parent = f"projects/{self.project_id}/locations/{location}/repositories/{repository_name}"
            request = artifactregistry_v1.ListDockerImagesRequest(parent=parent)

            images = []
            page_result = self.registry_client.list_docker_images(request=request)

            for image in page_result:
                images.append({
                    "name": image.name.split("/")[-1],
                    "uri": image.uri,
                    "tags": list(image.tags),
                    "create_time": image.create_time,
                    "size_bytes": image.size_bytes
                })

            return images

        except Exception as e:
            print(f"❌ Failed to list images: {str(e)}")
            return []

    def delete_repository(self, repository_name: str, location: str = "europe-north1") -> bool:
        """Delete an Artifact Registry repository"""
        try:
            print(f"🗑️  Deleting repository: {repository_name}")

            name = f"projects/{self.project_id}/locations/{location}/repositories/{repository_name}"
            request = artifactregistry_v1.DeleteRepositoryRequest(name=name)

            operation = self.registry_client.delete_repository(request=request)
            operation.result(timeout=120)

            print(f"✅ Repository deleted successfully!")
            return True

        except Exception as e:
            print(f"❌ Failed to delete repository: {str(e)}")
            return False

"""
Universal Container Manager

Provides a Rails-like API for container operations that works seamlessly
across Docker, Podman, and other OCI-compatible engines.

Philosophy:
- Convention over configuration
- Auto-detect best engine
- Cross-platform compatibility
- Intelligent error handling
"""

import os
from typing import Dict, Any, Optional, List
from .detector import ContainerEngineDetector
from .exceptions import (
    NoEngineFoundError,
    TemplateError
)


class UniversalContainerManager:
    """
    Rails-like container manager that abstracts all container engines.

    Provides a consistent API regardless of whether Docker, Podman, or
    other engines are used underneath.
    """

    def __init__(self, preferred_engine: Optional[str] = None):
        """
        Initialize the universal container manager.

        Args:
            preferred_engine: Preferred engine name ('docker', 'podman', etc.)
                             If None, auto-detects best available engine
        """
        self.detector = ContainerEngineDetector()
        self.engine = None
        self.preferred_engine = preferred_engine
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize the best available container engine"""
        try:
            if self.preferred_engine:
                engines = self.detector.detect_engines()
                if self.preferred_engine in engines:
                    engine_info = engines[self.preferred_engine]
                    if engine_info.get('available', False):
                        if self.preferred_engine == 'docker':
                            from .engines import DockerEngine
                            self.engine = DockerEngine(engine_info)
                        elif self.preferred_engine == 'podman':
                            from .engines import PodmanEngine
                            self.engine = PodmanEngine(engine_info)
                        else:
                            # Fallback to auto-detection
                            self.engine = self.detector.get_best_engine()
                    else:
                        print(f"⚠️  Preferred engine '{self.preferred_engine}' found but not available: {engine_info.get('reason', 'Unknown issue')}")
                        print(f"🔄 Auto-detecting alternative engine...")
                        self.engine = self.detector.get_best_engine()
                else:
                    print(f"⚠️  Preferred engine '{self.preferred_engine}' not found")
                    print(f"🔄 Auto-detecting available engine...")
                    self.engine = self.detector.get_best_engine()
            else:
                self.engine = self.detector.get_best_engine()

            print(f"🐳 Using container engine: {self.engine.name}")
            
            # Show helpful info about the selected engine
            if hasattr(self.engine, 'version'):
                print(f"   📦 Version: {self.engine.version}")
            if self.engine.is_rootless():
                print(f"   🔒 Running in rootless mode (enhanced security)")

        except NoEngineFoundError:
            print("❌ No container engine found!")
            print("💡 To use container features, install one of:")
            print("   • Docker Desktop: https://docker.com/desktop")
            print("   • Podman: https://podman.io/getting-started/installation")
            raise

    def build(self, image_name: str, context_path: str, **kwargs) -> bool:
        """
        Build a container image - Rails-like convenience method.

        Args:
            image_name: Name/tag for the built image
            context_path: Path to build context (directory with Dockerfile)
            **kwargs: Additional build options
                - dockerfile: Custom Dockerfile name
                - target_platform: Target platform (e.g., 'linux/amd64')
                - build_args: Dict of build arguments
                - no_cache: Disable build cache

        Returns:
            bool: True if build successful

        Raises:
            ContainerBuildError: If build fails
        """
        if not self.engine:
            raise NoEngineFoundError()

        return self.engine.build(image_name, context_path, **kwargs)

    def build_and_push(
        self,
        image_name: str,
        context_path: str,
        registry_url: str,
        **kwargs
    ) -> bool:
        """
        Build and push in one operation - Rails-like convenience.

        Args:
            image_name: Name/tag for the image
            context_path: Path to build context
            registry_url: Registry URL to push to
            **kwargs: Additional build options

        Returns:
            bool: True if both build and push successful
        """
        if not self.engine:
            raise NoEngineFoundError()

        # Build the image
        success = self.build(image_name, context_path, **kwargs)
        if not success:
            return False

        # Tag for registry if needed
        if registry_url and not image_name.startswith(registry_url):
            registry_image = f"{registry_url}/{image_name}"
            self.engine.tag(image_name, registry_image)
            image_name = registry_image

        # Push to registry
        return self.push(image_name, registry_url)

    def push(self, image_name: str, registry_url: Optional[str] = None) -> bool:
        """
        Push image to registry.

        Args:
            image_name: Image name/tag to push
            registry_url: Registry URL (optional if image already has registry prefix)

        Returns:
            bool: True if push successful
        """
        if not self.engine:
            raise NoEngineFoundError()

        return self.engine.push(image_name, registry_url)

    def pull(self, image_name: str) -> bool:
        """Pull image from registry"""
        if not self.engine:
            raise NoEngineFoundError()

        return self.engine.pull(image_name)

    def tag(self, source_image: str, target_image: str) -> bool:
        """Tag an image with a new name"""
        if not self.engine:
            raise NoEngineFoundError()

        return self.engine.tag(source_image, target_image)

    def remove_image(self, image_name: str) -> bool:
        """Remove an image"""
        if not self.engine:
            raise NoEngineFoundError()

        return self.engine.remove_image(image_name)

    def list_images(self) -> List[Dict[str, Any]]:
        """List available images"""
        if not self.engine:
            raise NoEngineFoundError()

        return self.engine.list_images()

    def build_with_template(
        self,
        image_name: str,
        template_name: str,
        context_path: str,
        variables: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        """
        Build using a template - Rails-like convention over configuration.

        This method will:
        1. Auto-detect the application type if template_name is 'auto'
        2. Generate appropriate Dockerfile/Containerfile
        3. Build the image

        Args:
            image_name: Name for the built image
            template_name: Template to use ('nodejs', 'python', 'go', 'auto')
            context_path: Path to application code
            variables: Template variables
            **kwargs: Additional build options

        Returns:
            bool: True if successful
        """
        if not self.engine:
            raise NoEngineFoundError()

        # Auto-detect template if requested
        if template_name == 'auto':
            template_name = self._detect_application_type(context_path)
            print(f"🔍 Auto-detected application type: {template_name}")

        # Generate container file from template
        container_file = self._generate_container_file(template_name, context_path, variables or {})

        # Check for existing container files
        dockerfile_name = 'Containerfile' if 'podman' in self.engine.name else 'Dockerfile'
        dockerfile_path = os.path.join(context_path, dockerfile_name)
        
        # Also check for the other common name (Dockerfile vs Containerfile)
        alt_dockerfile_name = 'Dockerfile' if 'podman' in self.engine.name else 'Containerfile'
        alt_dockerfile_path = os.path.join(context_path, alt_dockerfile_name)

        # Use existing Dockerfile if present
        if os.path.exists(dockerfile_path):
            print(f"📋 Using existing {dockerfile_name}")
            return self.build(image_name, context_path, dockerfile=dockerfile_name, **kwargs)
        elif os.path.exists(alt_dockerfile_path):
            print(f"📋 Using existing {alt_dockerfile_name}")
            return self.build(image_name, context_path, dockerfile=alt_dockerfile_name, **kwargs)
        
        # Only generate if no Dockerfile exists
        try:
            with open(dockerfile_path, 'w') as f:
                f.write(container_file)
            print(f"📝 Generated {dockerfile_name} using {template_name} template (no existing Dockerfile found)")

            # Build with the generated file
            return self.build(image_name, context_path, dockerfile=dockerfile_name, **kwargs)

        except Exception as e:
            # Clean up generated file if build failed
            if os.path.exists(dockerfile_path):
                os.remove(dockerfile_path)
                print(f"🗑️  Removed generated {dockerfile_name} due to build failure")
            raise TemplateError(template_name, str(e))

    def _detect_application_type(self, context_path: str) -> str:
        """
        Auto-detect application type based on files in context.

        Rails philosophy: Convention over configuration
        """
        # Check for common application files
        files = os.listdir(context_path)

        # Node.js detection
        if 'package.json' in files:
            return 'nodejs'

        # Python detection
        if any(f in files for f in ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile']):
            return 'python'

        # Go detection
        if 'go.mod' in files or any(f.endswith('.go') for f in files):
            return 'go'

        # Java detection
        if any(f in files for f in ['pom.xml', 'build.gradle', 'build.gradle.kts']):
            return 'java'

        # PHP detection
        if 'composer.json' in files or any(f.endswith('.php') for f in files):
            return 'php'

        # Ruby detection
        if 'Gemfile' in files or any(f.endswith('.rb') for f in files):
            return 'ruby'

        # Default to generic linux
        print("⚠️  Could not auto-detect application type, using generic template")
        return 'generic'

    def _generate_container_file(
        self,
        template_name: str,
        context_path: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Generate Dockerfile/Containerfile content from template.

        This is a simplified version - in a full implementation,
        this would use a proper template system.
        """
        # Default variables
        default_vars = {
            'port': '8080',
            'user': 'app',
            'workdir': '/app'
        }
        default_vars.update(variables)

        if template_name == 'nodejs':
            return self._generate_nodejs_container_file(default_vars)
        elif template_name == 'python':
            return self._generate_python_container_file(default_vars)
        elif template_name == 'go':
            return self._generate_go_container_file(default_vars)
        elif template_name == 'java':
            return self._generate_java_container_file(default_vars)
        else:
            return self._generate_generic_container_file(default_vars)

    def _generate_nodejs_container_file(self, variables: Dict[str, Any]) -> str:
        """Generate Node.js optimized container file"""
        return f"""# Generated by InfraDSL - Node.js optimized container
FROM node:18-alpine

# Create app user for security
RUN addgroup -g 1001 -S {variables['user']} && \\
    adduser -S {variables['user']} -u 1001

# Set working directory
WORKDIR {variables['workdir']}

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies (handle missing package-lock.json gracefully)
RUN if [ -f package-lock.json ]; then \
        npm ci --only=production; \
    else \
        npm install --only=production; \
    fi && npm cache clean --force

# Copy application code
COPY . .

# Change ownership to app user
RUN chown -R {variables['user']}:{variables['user']} {variables['workdir']}

# Switch to non-root user
USER {variables['user']}

# Expose port
EXPOSE {variables['port']}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{variables['port']}/health || exit 1

# Start application
CMD ["npm", "start"]
"""

    def _generate_python_container_file(self, variables: Dict[str, Any]) -> str:
        """Generate Python optimized container file"""
        return f"""# Generated by InfraDSL - Python optimized container
FROM python:3.11-slim

# Create app user for security
RUN groupadd -r {variables['user']} && useradd -r -g {variables['user']} {variables['user']}

# Set working directory
WORKDIR {variables['workdir']}

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to app user
RUN chown -R {variables['user']}:{variables['user']} {variables['workdir']}

# Switch to non-root user
USER {variables['user']}

# Expose port
EXPOSE {variables['port']}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{variables['port']}/health || exit 1

# Start application
CMD ["python", "app.py"]
"""

    def _generate_go_container_file(self, variables: Dict[str, Any]) -> str:
        """Generate Go optimized container file"""
        return f"""# Generated by InfraDSL - Go optimized container
# Multi-stage build for minimal image size
FROM golang:1.21-alpine AS builder

WORKDIR /build

# Copy go mod files first for better caching
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

# Final stage - minimal runtime image
FROM alpine:latest

# Install ca-certificates for HTTPS
RUN apk --no-cache add ca-certificates curl

# Create app user for security
RUN addgroup -g 1001 -S {variables['user']} && \\
    adduser -S {variables['user']} -u 1001

WORKDIR {variables['workdir']}

# Copy binary from builder
COPY --from=builder /build/app .

# Change ownership
RUN chown {variables['user']}:{variables['user']} app

# Switch to non-root user
USER {variables['user']}

# Expose port
EXPOSE {variables['port']}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{variables['port']}/health || exit 1

# Start application
CMD ["./app"]
"""

    def _generate_java_container_file(self, variables: Dict[str, Any]) -> str:
        """Generate Java optimized container file"""
        return f"""# Generated by InfraDSL - Java optimized container
FROM openjdk:17-jre-slim

# Create app user for security
RUN groupadd -r {variables['user']} && useradd -r -g {variables['user']} {variables['user']}

# Set working directory
WORKDIR {variables['workdir']}

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy application jar
COPY target/*.jar app.jar

# Change ownership
RUN chown {variables['user']}:{variables['user']} app.jar

# Switch to non-root user
USER {variables['user']}

# Expose port
EXPOSE {variables['port']}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{variables['port']}/actuator/health || exit 1

# Start application
CMD ["java", "-jar", "app.jar"]
"""

    def _generate_generic_container_file(self, variables: Dict[str, Any]) -> str:
        """Generate generic container file"""
        return f"""# Generated by InfraDSL - Generic container
FROM alpine:latest

# Install basic tools
RUN apk --no-cache add curl

# Create app user for security
RUN addgroup -g 1001 -S {variables['user']} && \\
    adduser -S {variables['user']} -u 1001

# Set working directory
WORKDIR {variables['workdir']}

# Copy application files
COPY . .

# Change ownership
RUN chown -R {variables['user']}:{variables['user']} {variables['workdir']}

# Switch to non-root user
USER {variables['user']}

# Expose port
EXPOSE {variables['port']}

# Default command
CMD ["sh"]
"""

    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the current engine"""
        if not self.engine:
            return {"error": "No engine available"}

        return {
            "name": self.engine.name,
            "version": self.engine.version,
            "available": self.engine.available,
            "features": self.engine.features,
            "platform": self.engine.platform,
            "supports_multi_platform": self.engine.supports_multi_platform(),
            "is_rootless": self.engine.is_rootless()
        }

    def print_status(self):
        """Print Rails-like status report"""
        print("🐳 Universal Container Manager Status")
        print("=" * 40)

        if not self.engine:
            print("❌ No container engine available")
            return

        info = self.get_engine_info()
        print(f"✅ Engine: {info['name']} v{info['version']}")
        print(f"📱 Platform: {info['platform']}")

        features = info['features']
        if features.get('multi_platform'):
            print("✅ Multi-platform builds: Supported")
        if features.get('rootless'):
            print("✅ Rootless mode: Available")
        if features.get('cache'):
            print("✅ Build cache: Enabled")

        print("=" * 40)

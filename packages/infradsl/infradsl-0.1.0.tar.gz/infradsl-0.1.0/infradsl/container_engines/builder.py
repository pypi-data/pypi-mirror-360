"""
Container Builder for Cloud Run Integration

High-level builder that integrates universal container engine support
with Google Cloud Run deployment. Provides Rails-like conventions
for building and deploying containerized applications.
"""

import os
import platform
from typing import Dict, Any, Optional, List
from .manager import UniversalContainerManager
from .exceptions import ContainerBuildError, ContainerPushError


class ContainerBuilder:
    """
    High-level container builder for Cloud Run integration.

    Provides Rails-like conventions:
    - Auto-detect application type
    - Generate optimal containers
    - Cross-architecture builds
    - Smart caching
    """

    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.container_manager = UniversalContainerManager()
        self.current_arch = platform.machine().lower()
        self.target_arch = "amd64"  # Cloud Run default

    def build_for_cloud_run(
        self,
        service_name: str,
        source_path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build container optimized for Google Cloud Run.

        Args:
            service_name: Cloud Run service name
            source_path: Path to application source code
            **kwargs: Additional options
                - template: Container template ('auto', 'nodejs', 'python', etc.)
                - port: Application port (default: 8080)
                - environment: Environment variables
                - build_args: Container build arguments

        Returns:
            Dict containing build information
        """
        template = kwargs.get('template', 'auto')
        port = kwargs.get('port', 8080)
        environment = kwargs.get('environment', {})
        build_args = kwargs.get('build_args', {})

        # Generate Cloud Run optimized image name
        image_name = self._generate_image_name(service_name)
        registry_url = f"europe-north1-docker.pkg.dev/{self.project_id}/infradsl-apps"

        print(f"🚀 Building container for Cloud Run service: {service_name}")
        print(f"   📁 Source: {source_path}")
        print(f"   🏗️  Template: {template}")
        print(f"   🔗 Registry: {registry_url}")

        # Prepare build variables for Cloud Run
        variables = {
            'port': str(port),
            'user': 'cloudrun',
            'workdir': '/app',
            'service_name': service_name,
            'project_id': self.project_id
        }
        variables.update(kwargs.get('template_vars', {}))

        # Add Cloud Run specific build args
        cloud_run_build_args = {
            'PORT': str(port),
            'PROJECT_ID': self.project_id,
            'SERVICE_NAME': service_name,
            **build_args
        }

        try:
            # Build with template
            success = self.container_manager.build_with_template(
                image_name=image_name,
                template_name=template,
                context_path=source_path,
                variables=variables,
                target_platform=self._get_target_platform(),
                build_args=cloud_run_build_args,
                **self._get_cloud_run_build_options()
            )

            if not success:
                raise ContainerBuildError("build", 1, "Container build failed")

            # Tag for Google Artifact Registry
            registry_image = f"{registry_url}/{image_name}"
            self.container_manager.tag(image_name, registry_image)

            print(f"✅ Container built successfully: {registry_image}")

            return {
                'image_name': image_name,
                'registry_image': registry_image,
                'registry_url': registry_url,
                'port': port,
                'environment': environment,
                'template': template,
                'build_successful': True
            }

        except Exception as e:
            print(f"❌ Container build failed: {str(e)}")
            raise ContainerBuildError("build", 1, str(e))

    def build_and_push_for_cloud_run(
        self,
        service_name: str,
        source_path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build and push container for Cloud Run in one operation.

        Args:
            service_name: Cloud Run service name
            source_path: Path to application source code
            **kwargs: Additional build options

        Returns:
            Dict containing build and push information
        """
        # Build the container
        build_result = self.build_for_cloud_run(service_name, source_path, **kwargs)

        if not build_result['build_successful']:
            return build_result

        # Push to Google Artifact Registry
        try:
            registry_image = build_result['registry_image']

            print("📤 Pushing to Google Artifact Registry...")
            success = self.container_manager.push(registry_image)

            if not success:
                raise ContainerPushError(
                    build_result['registry_url'],
                    build_result['image_name'],
                    "Push operation failed"
                )

            print(f"✅ Push successful: {registry_image}")

            build_result.update({
                'push_successful': True,
                'deployed_image': registry_image
            })

            return build_result

        except Exception as e:
            print(f"❌ Container push failed: {str(e)}")
            build_result['push_successful'] = False
            build_result['push_error'] = str(e)
            return build_result

    def _generate_image_name(self, service_name: str) -> str:
        """Generate standardized image name for Cloud Run"""
        # Clean service name for container naming
        clean_name = service_name.lower().replace('_', '-')
        return f"{clean_name}:latest"

    def _get_target_platform(self) -> Optional[str]:
        """Get target platform for Cloud Run (handles cross-arch builds)"""
        if self.current_arch in ['arm64', 'aarch64'] and self.target_arch == 'amd64':
            # Cross-architecture build from ARM64 to AMD64
            if self.container_manager.engine and self.container_manager.engine.supports_multi_platform():
                print("🔄 Cross-architecture build: ARM64 → x86_64")
                return "linux/amd64"

        return None  # Use default platform

    def _get_cloud_run_build_options(self) -> Dict[str, Any]:
        """Get Cloud Run specific build options"""
        return {
            'no_cache': False,  # Enable caching for faster builds
            'quiet': False      # Show build output for debugging
        }

    def generate_cloud_run_dockerfile(
        self,
        template: str,
        source_path: str,
        service_name: str,
        port: int = 8080,
        **kwargs
    ) -> str:
        """
        Generate Cloud Run optimized Dockerfile.

        Args:
            template: Template type ('nodejs', 'python', 'go', etc.)
            source_path: Path to application source
            service_name: Cloud Run service name
            port: Application port
            **kwargs: Additional template variables

        Returns:
            str: Generated Dockerfile content
        """
        variables = {
            'port': str(port),
            'user': 'cloudrun',
            'workdir': '/app',
            'service_name': service_name,
            'project_id': self.project_id,
            **kwargs
        }

        return self.container_manager._generate_container_file(
            template, source_path, variables
        )

    def get_supported_templates(self) -> List[str]:
        """Get list of supported container templates"""
        return [
            'auto',      # Auto-detect based on source code
            'nodejs',    # Node.js applications
            'python',    # Python applications
            'go',        # Go applications
            'java',      # Java applications
            'php',       # PHP applications
            'ruby',      # Ruby applications
            'generic'    # Generic Alpine-based container
        ]

    def detect_application_type(self, source_path: str) -> str:
        """
        Detect application type from source code.

        Args:
            source_path: Path to application source

        Returns:
            str: Detected application type
        """
        return self.container_manager._detect_application_type(source_path)

    def validate_source_path(self, source_path: str) -> Dict[str, Any]:
        """
        Validate source path for container build.

        Args:
            source_path: Path to validate

        Returns:
            Dict with validation results
        """
        if not os.path.exists(source_path):
            return {
                'valid': False,
                'error': f"Source path does not exist: {source_path}"
            }

        if not os.path.isdir(source_path):
            return {
                'valid': False,
                'error': f"Source path is not a directory: {source_path}"
            }

        # Check for common application files
        files = os.listdir(source_path)
        app_files = [
            'package.json', 'requirements.txt', 'go.mod', 'pom.xml',
            'composer.json', 'Gemfile', 'app.py', 'main.go', 'index.js'
        ]

        has_app_files = any(f in files for f in app_files)
        detected_type = self.detect_application_type(source_path)

        return {
            'valid': True,
            'detected_type': detected_type,
            'has_application_files': has_app_files,
            'files_found': [f for f in app_files if f in files],
            'suggestion': self._get_build_suggestion(detected_type, has_app_files)
        }

    def _get_build_suggestion(self, detected_type: str, has_app_files: bool) -> str:
        """Get suggestion for container build"""
        if not has_app_files:
            return "No application files detected. Consider using template='generic' or add application files."

        if detected_type == 'generic':
            return "Could not auto-detect application type. Specify template explicitly."

        return f"Detected {detected_type} application. Use template='{detected_type}' or template='auto'."

    def clean_build_cache(self) -> bool:
            """Clean container build cache"""
            try:
                if self.container_manager.engine and 'docker' in self.container_manager.engine.name:
                    import subprocess
                    result = subprocess.run(
                        ['docker', 'system', 'prune', '-f'],
                        capture_output=True,
                        text=True
                    )
                    return result.returncode == 0
                elif self.container_manager.engine and 'podman' in self.container_manager.engine.name:
                    import subprocess
                    result = subprocess.run(
                        ['podman', 'system', 'prune', '-f'],
                        capture_output=True,
                        text=True
                    )
                    return result.returncode == 0
            except Exception:
                return False

            return False

    def get_build_status(self) -> Dict[str, Any]:
        """Get current build environment status"""
        engine_info = self.container_manager.get_engine_info()

        return {
            'container_engine': engine_info,
            'project_id': self.project_id,
            'location': self.location,
            'current_architecture': self.current_arch,
            'target_architecture': self.target_arch,
            'cross_arch_build_needed': self.current_arch != self.target_arch,
            'supported_templates': self.get_supported_templates()
        }

    def print_build_status(self):
        """Print Rails-like build status report"""
        status = self.get_build_status()

        print("🔨 Container Builder Status")
        print("=" * 40)
        print(f"🏗️  Engine: {status['container_engine']['name']}")
        print(f"📱 Platform: {status['current_architecture']} → {status['target_architecture']}")
        print(f"🌍 Project: {self.project_id}")
        print(f"📍 Location: {self.location}")

        if status['cross_arch_build_needed']:
            if status['container_engine']['supports_multi_platform']:
                print("✅ Cross-architecture builds: Supported")
            else:
                print("⚠️  Cross-architecture builds: Limited support")

        print(f"📋 Templates: {', '.join(status['supported_templates'])}")
        print("=" * 40)
